"""
🎭 MIDI Light Controller - Blender Add-on

Integraatio MIDI-valoohjauksen ja Blenderin välillä.
Mahdollistaa valoesitysten suunnittelun Blenderissä ja tuonti/vienti MIDI-generaattorin kanssa.

Installation:
1. Save this file as midi_light_controller.py
2. Blender → Edit → Preferences → Add-ons → Install...
3. Select this file and enable "MIDI Light Controller"
4. Find panel in 3D Viewport → N-panel → MIDI Lights tab

Version: 1.0
Author: Rauli Virtanen
Category: Lighting
"""

bl_info = {
    "name": "MIDI Light Controller",
    "author": "Rauli Virtanen",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "3D Viewport > N-Panel > MIDI Lights",
    "description": "Integraatio MIDI-valoohjauksen ja Blenderin välillä",
    "category": "Lighting",
    "doc_url": "https://github.com/RauliV/midi-fade-generator",
    "tracker_url": "https://github.com/RauliV/midi-fade-generator/issues",
}

import bpy
import bmesh
import os
import sys
import json
import subprocess
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, IntProperty, FloatProperty, BoolProperty, EnumProperty

# Lisää mido polkuun jos ei löydy
try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False

# ==========================================
# RGBW COLOR MIXING GLOBALS
# ==========================================

# Globaali RGBW-tila add-onille
addon_rgbw_channel_states = {}

def get_rgbw_channels(light_name):
    """Palauttaa RGBW-valon kanavanumerot tai None jos ei ole RGBW"""
    import re
    match = re.search(r'RGBW\s+(\d+)-(\d+)', light_name)
    if match:
        start_channel = int(match.group(1))
        end_channel = int(match.group(2))
        if end_channel - start_channel == 3:  # Tarkista että on 4 kanavaa
            return {
                'r': start_channel,
                'g': start_channel + 1, 
                'b': start_channel + 2,
                'w': start_channel + 3
            }
    return None

def update_rgbw_color(light_obj, channel, velocity):
    """Päivittää RGBW-valon väri perustuen kaikkiin aktiivisiin kanaviin"""
    global addon_rgbw_channel_states
    
    light_name = light_obj.name
    rgbw_channels = get_rgbw_channels(light_name)
    
    if not rgbw_channels:
        return False  # Ei ole RGBW-valo
    
    # Alusta valon tila jos ei ole vielä
    if light_name not in addon_rgbw_channel_states:
        addon_rgbw_channel_states[light_name] = {'r': 0, 'g': 0, 'b': 0, 'w': 0}
    
    # Päivitä kanavan arvo
    state = addon_rgbw_channel_states[light_name]
    for color, ch in rgbw_channels.items():
        if ch == channel:
            state[color] = velocity
            print(f"🎨 Add-on: {light_name}: {color.upper()} kanava {ch} = {velocity}")
            break
    
    # Laske sekoitettu väri
    r_intensity = state['r'] / 127.0
    g_intensity = state['g'] / 127.0  
    b_intensity = state['b'] / 127.0
    w_intensity = state['w'] / 127.0
    
    # Valkoinen kanava lisää kaikkia värejä
    final_r = min(1.0, r_intensity + w_intensity * 0.8)
    final_g = min(1.0, g_intensity + w_intensity * 0.8) 
    final_b = min(1.0, b_intensity + w_intensity * 0.8)
    
    # Aseta väri Blenderiin
    light_obj.data.color = (final_r, final_g, final_b)
    
    # Laske kokonaisteho
    max_channel = max(state['r'], state['g'], state['b'])
    total_intensity = max(max_channel, state['w'])
    
    print(f"💡 Add-on: {light_name}: RGB({final_r:.2f}, {final_g:.2f}, {final_b:.2f}) intensity={total_intensity}")
    return total_intensity

# ==========================================
# PROPERTY GROUPS (Asetukset)
# ==========================================

class MIDILightProperties(PropertyGroup):
    """Lisäosan asetukset"""
    
    # MIDI-tuonti asetukset
    midi_file_path: StringProperty(
        name="MIDI File",
        description="Polku MIDI-tiedostoon",
        default="/Users/raulivirtanen/Documents/valot/generated_midi/testikohde_fade_in.mid",
        subtype='FILE_PATH'
    )
    
    fps: IntProperty(
        name="FPS",
        description="Blenderin framerate",
        default=24,
        min=1,
        max=120
    )
    
    max_wattage: FloatProperty(
        name="Max Wattage",
        description="Maksimiteho watteina",
        default=300.0,
        min=1.0,
        max=1000.0
    )
    
    use_rgbw_groups: BoolProperty(
        name="RGBW Groups",
        description="Käytä RGBW-ryhmiä (4 kanavaa per ryhmä)",
        default=True
    )
    
    # JSON-vienti asetukset
    json_output_path: StringProperty(
        name="Output JSON",
        description="JSON-vientitiedoston polku",
        default="/Users/raulivirtanen/Documents/valot/BlenderExport.json",
        subtype='FILE_PATH'
    )
    
    scene_name: StringProperty(
        name="Scene Name",
        description="Kohtauksen nimi",
        default="BlenderScene"
    )
    
    fade_in_duration: FloatProperty(
        name="Fade In (s)",
        description="Fade-in aika sekunteina",
        default=2.0,
        min=0.1,
        max=30.0
    )
    
    fade_out_duration: FloatProperty(
        name="Fade Out (s)",
        description="Fade-out aika sekunteina", 
        default=3.0,
        min=0.1,
        max=30.0
    )
    
    fade_steps: IntProperty(
        name="Steps",
        description="MIDI-portaiden määrä",
        default=20,
        min=5,
        max=100
    )
    
    # Savukone-asetukset
    enable_smoke_machines: BoolProperty(
        name="Enable Smoke Machines",
        description="Aktivoi savukoneiden tuki (kanavat 41-45)",
        default=False
    )
    
    smoke_density_multiplier: FloatProperty(
        name="Smoke Density",
        description="Savun tiheyden kerroin",
        default=1.0,
        min=0.1,
        max=5.0
    )

# ==========================================
# OPERATORS (Toiminnot)
# ==========================================

class MIDI_OT_install_mido(Operator):
    """Asenna mido-kirjasto"""
    bl_idname = "midi.install_mido"
    bl_label = "Install mido"
    bl_description = "Asenna mido-kirjasto MIDI-tiedostojen lukemista varten"
    
    def execute(self, context):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "mido"])
            self.report({'INFO'}, "mido asennettu onnistuneesti!")
            global MIDO_AVAILABLE
            MIDO_AVAILABLE = True
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Virhe mido:n asennuksessa: {e}")
            return {'CANCELLED'}

class MIDI_OT_clear_animation(Operator):
    """Tyhjennä vanhat animaatiot"""
    bl_idname = "midi.clear_animation"
    bl_label = "Clear Animation"
    bl_description = "Poista kaikki vanhat keyframet ja animaatiot"
    
    def execute(self, context):
        global addon_rgbw_channel_states
        
        try:
            # Tyhjennä RGBW-tila
            addon_rgbw_channel_states = {}
            print("🧹 Add-on: RGBW-tila tyhjennetty")
            
            # Mene frame 1:een
            bpy.context.scene.frame_set(1)
            
            cleared_lights = 0
            
            # Tyhjennä kaikki objektien animaatiot
            for obj in bpy.data.objects:
                if obj.type == 'LIGHT' and obj.data:
                    # Aseta minimaalinen energia ja valkoinen väri
                    obj.data.energy = 1.0
                    obj.data.color = (1.0, 1.0, 1.0)  # Valkoinen
                    cleared_lights += 1
                    
                # Poista animaatiodata
                if obj.animation_data:
                    obj.animation_data_clear()
                    
                if hasattr(obj, 'data') and obj.data and hasattr(obj.data, 'animation_data'):
                    if obj.data.animation_data:
                        obj.data.animation_data_clear()
            
            # Tyhjennä scenen animaatiot
            if bpy.context.scene.animation_data:
                bpy.context.scene.animation_data_clear()
            
            # Poista actionit
            for action in bpy.data.actions:
                bpy.data.actions.remove(action)
            
            # Aseta frame-range uusiksi
            bpy.context.scene.frame_start = 1
            bpy.context.scene.frame_end = 250
            bpy.context.scene.frame_set(1)
            
            # Päivitä näkymät
            bpy.context.view_layer.update()
            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()
            
            self.report({'INFO'}, f"Animaatiot tyhjennetty! {cleared_lights} valoa käsitelty.")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Virhe animaatioiden tyhjennuksessä: {e}")
            return {'CANCELLED'}

class MIDI_OT_import_midi(Operator):
    """Tuo MIDI-tiedosto Blenderiin"""
    bl_idname = "midi.import_midi"
    bl_label = "Import MIDI"
    bl_description = "Tuo MIDI-tiedosto valoanimaatioksi"
    
    def execute(self, context):
        if not MIDO_AVAILABLE:
            self.report({'ERROR'}, "mido-kirjasto puuttuu! Asenna se ensin.")
            return {'CANCELLED'}
        
        props = context.scene.midi_light_props
        midi_path = props.midi_file_path
        
        if not os.path.exists(midi_path):
            self.report({'ERROR'}, f"MIDI-tiedostoa ei löydy: {midi_path}")
            return {'CANCELLED'}
        
        try:
            # Tuo MIDI
            result = self.import_midi_to_blender(context, midi_path, props)
            
            if result:
                self.report({'INFO'}, "MIDI tuotu onnistuneesti!")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "MIDI-tuonnissa tapahtui virhe")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Virhe MIDI-tuonnissa: {e}")
            return {'CANCELLED'}
    
    def import_midi_to_blender(self, context, midi_path, props):
        """MIDI-tuonti logiikka"""
        import mido
        
        print(f"🎵 Ladataan MIDI: {midi_path}")
        
        try:
            midi_file = mido.MidiFile(midi_path)
        except Exception as e:
            print(f"❌ Virhe MIDI-lukemisessa: {e}")
            return False
        
        # Tyhjennä vanhat animaatiot
        bpy.ops.midi.clear_animation()
        
        # Aseta FPS
        bpy.context.scene.render.fps = props.fps
        
        processed_events = 0
        
        for track_num, track in enumerate(midi_file.tracks):
            track_time = 0
            
            for msg in track:
                track_time += msg.time
                
                if hasattr(msg, 'type') and msg.type == 'note_on':
                    channel = msg.note - 69
                    
                    # Laajempi kanava-alue: 1-45 (savukoneet 41-45)
                    if channel < 1 or channel > 45:
                        continue
                    
                    velocity = msg.velocity
                    frame = int((track_time / midi_file.ticks_per_beat) * props.fps * 0.5)
                    
                    # Tarkista onko savukone-kanava (41-45)
                    if channel >= 41 and channel <= 45 and props.enable_smoke_machines:
                        # Käsittele savukone
                        self.handle_smoke_machine(channel, velocity, frame, props)
                        processed_events += 1
                        continue
                    
                    # Normaali valokanava (1-40)
                    if channel > 40:
                        continue
                    
                    # Hae tai luo valo
                    light_obj = self.get_or_create_light(channel, props)
                    if not light_obj:
                        continue
                    
                    # Tarkista onko RGBW-valo
                    rgbw_intensity = update_rgbw_color(light_obj, channel, velocity)
                    if rgbw_intensity is not False:
                        # RGBW-värinsekoitus käsitelty, laske energia RGBW-intensiteetistä
                        energy = self.velocity_to_energy(rgbw_intensity, props.max_wattage)
                        light_obj.data.energy = energy
                        # Aseta keyframet väreille ja energialle
                        light_obj.data.keyframe_insert(data_path="color", frame=frame)
                        light_obj.data.keyframe_insert(data_path="energy", frame=frame)
                    else:
                        # Tavallinen valo - pelkkä energia
                        energy = self.velocity_to_energy(velocity, props.max_wattage)
                        light_obj.data.energy = energy
                        light_obj.data.keyframe_insert(data_path="energy", frame=frame)
                    
                    processed_events += 1
        
        # Aseta animaation pituus
        if processed_events > 0:
            max_frame = max(1, int(track_time / midi_file.ticks_per_beat * props.fps * 0.5))
            bpy.context.scene.frame_end = max_frame
            
            # Pakota päivitys
            bpy.context.scene.frame_set(1)
            bpy.context.view_layer.update()
            
            print(f"✅ Tuonti valmis! {processed_events} tapahtumaa, {max_frame} framea")
        
        return True
    
    def get_or_create_light(self, channel, props):
        """Hakee tai luo valon - VAIN Lights collectionista"""
        
        print(f"🔍 Etsitään valoa kanavalle {channel} VAIN Lights collectionista")
        
        # Etsi Lights collection
        lights_collection = None
        for collection in bpy.data.collections:
            if 'Light' in collection.name or 'light' in collection.name.lower():
                lights_collection = collection
                print(f"📁 Käytetään collectionia: {collection.name}")
                break
        
        if not lights_collection:
            print("❌ Ei löytynyt Lights collectionia!")
            return None
        
        # Hae VAIN Lights collectionin valot
        collection_lights = []
        for obj in lights_collection.objects:
            if obj.type == 'LIGHT':
                collection_lights.append(obj)
                print(f"💡 Löydettiin: {obj.name}")
        
        if not collection_lights:
            print("❌ Ei valoja Lights collectionissa!")
            return None
        
        # ENSIKSI: Etsi täsmälleen sinun RGBW-ryhmistä
        # "RGBW 33-36", "RGBW 37-40" jne.
        for light_obj in collection_lights:
            light_name = light_obj.name
            
            # Tarkista RGBW x-y muoto
            if light_name.startswith('RGBW '):
                import re
                range_match = re.search(r'RGBW (\d+)-(\d+)', light_name)
                if range_match:
                    start_ch = int(range_match.group(1))
                    end_ch = int(range_match.group(2))
                    if start_ch <= channel <= end_ch:
                        print(f"🎯 RGBW range match: {light_name} sisältää kanavan {channel}")
                        return light_obj
        
        # TOISEKSI: Etsi Spot-valoja
        # "Spot.012", "Spot.014" jne.
        for light_obj in collection_lights:
            light_name = light_obj.name
            
            if 'Spot' in light_name:
                import re
                spot_numbers = re.findall(r'\d+', light_name)
                for num_str in spot_numbers:
                    if int(num_str) == channel:
                        print(f"🎯 Spot match: {light_name} = kanava {channel}")
                        return light_obj
        
        # KOLMANNEKSI: Etsi mitä tahansa numeroa joka vastaa kanavaa
        for light_obj in collection_lights:
            light_name = light_obj.name
            
            import re
            numbers = re.findall(r'\d+', light_name)
            for num_str in numbers:
                if int(num_str) == channel:
                    print(f"🎯 Numero match: {light_name} = kanava {channel}")
                    return light_obj
        
        # NELJÄNNEKSI: Ota järjestyksessä (channel 1 = ensimmäinen valo jne.)
        if channel <= len(collection_lights):
            # Järjestä valot älykkäästi
            def smart_sort_key(light_obj):
                light_name = light_obj.name
                import re
                numbers = re.findall(r'\d+', light_name)
                if numbers:
                    return int(numbers[0])  # Ensimmäinen numero
                return 999
            
            sorted_lights = sorted(collection_lights, key=smart_sort_key)
            target_light = sorted_lights[channel - 1]  # 0-indexed
            print(f"🎯 Järjestys match: {target_light.name} = kanava {channel} (#{channel} listassa)")
            return target_light
        
        # VIIMEISEKSI: Ei löytynyt mitään sopivaa
        print(f"❌ Ei löytynyt sopivaa valoa kanavalle {channel}")
        print(f"📋 Lights collectionin valot: {[obj.name for obj in collection_lights]}")
        
        # ÄLKÄÄ LUOKO UUTTA VALOA! Palauta None sen sijaan
        print(f"🚫 EI LUODA UUTTA VALOA - käytetään ensimmäistä löytyvää")
        
        # Fallback: palauta ensimmäinen valo jos ei löydy muuta
        if collection_lights:
            fallback_light = collection_lights[0]
            print(f"⚠️  Fallback: käytetään {fallback_light.name} kanavalle {channel}")
            return fallback_light
        
        return None
        
        return light_obj
    
    def velocity_to_energy(self, velocity, max_wattage):
        """Muuntaa velocity energiaksi - realistinen Scene Setter -skaala"""
        if velocity == 0:
            return 1.0
        
        # Realistinen skaala Scene Setter -laitteistoa varten:
        # - Pikkuspotit ovat todella kirkkaita (vel 60 = liian kirkas)
        # - RGBW:t ovat heikompia (tarvitsevat vel 127 ollakseen näkyviä)
        
        # Perusskaalaus 5-300W välille
        base_energy = 5.0 + (velocity / 127.0) * (max_wattage - 5.0)
        
        # Spot-boost: pikkuspotit ovat todellisuudessa 2-3x kirkkaita
        # Tämä simuloi sitä että ne ovat "liian kirkkaita" jo matalilla velocity-arvoilla
        spot_multiplier = 2.5  # Pikkuspotit 2.5x kirkkaita
        
        return base_energy * spot_multiplier if self.is_small_spot_channel(velocity) else base_energy
    
    def is_small_spot_channel(self, velocity):
        """Tarkista onko tämä pikkuspot (kanavat 21-24 yleensä)"""
        # Tämä on heuristiikka - voit säätää tarpeen mukaan
        # Pikkuspotit ovat yleensä matalampi velocity mutta silti kirkkaita
        return 40 <= velocity <= 80  # Keskivahvat velocity-arvot = todennäköisesti pikkuspotit

    def handle_smoke_machine(self, channel, velocity, frame, props):
        """Käsittelee savukone-kanavat (41-45)"""
        
        # Savukoneiden nimet
        smoke_names = {
            41: "Smoke_Front_Left",
            42: "Smoke_Front_Right", 
            43: "Smoke_Back_Left",
            44: "Smoke_Back_Right",
            45: "Smoke_Center_Stage"
        }
        
        smoke_name = smoke_names.get(channel, f"Smoke_{channel}")
        
        # Etsi olemassa oleva savukone
        smoke_obj = bpy.data.objects.get(smoke_name)
        
        if not smoke_obj:
            # Luo uusi savukone
            positions = {
                41: (-3, 2, 0),   # Front Left
                42: (3, 2, 0),    # Front Right  
                43: (-3, -2, 0),  # Back Left
                44: (3, -2, 0),   # Back Right
                45: (0, 0, 0)     # Center Stage
            }
            
            location = positions.get(channel, (0, 0, 0))
            
            # Luo cube savukoneelle
            bpy.ops.mesh.primitive_cube_add(location=location)
            smoke_obj = bpy.context.active_object
            smoke_obj.name = smoke_name
            
            # Lisää Quick Smoke effect
            bpy.ops.object.quick_effects_smoke_flow()
            
            print(f"🌫️ Luotu savukone: {smoke_name} kohdassa {location}")
        
        # Päivitä savun tiheys
        modifier = smoke_obj.modifiers.get("Fluid")
        if modifier and hasattr(modifier, 'fluid_settings'):
            # Muunna MIDI velocity (0-127) → density (0-2.0)
            density = (velocity / 127.0) * 2.0 * props.smoke_density_multiplier
            modifier.fluid_settings.density = density
            
            # Aseta keyframe
            modifier.fluid_settings.keyframe_insert(data_path="density", frame=frame)
            
            print(f"🌫️ Frame {frame}: {smoke_name} velocity {velocity} → density {density:.2f}")
        
        return True

class MIDI_OT_export_json(Operator):
    """Vie Blender-setup JSON:na"""
    bl_idname = "midi.export_json"
    bl_label = "Export JSON"
    bl_description = "Vie nykyinen valosetup JSON-muotoon"
    
    def execute(self, context):
        props = context.scene.midi_light_props
        
        try:
            channels_data = self.scan_blender_lights(context)
            
            if not channels_data:
                self.report({'WARNING'}, "Ei löytynyt päällä olevia valoja!")
                return {'CANCELLED'}
            
            # Luo JSON-data
            scene_data = {
                "name": props.scene_name,
                "channels": channels_data,
                "fade_in_duration": props.fade_in_duration,
                "fade_out_duration": props.fade_out_duration,
                "steps": props.fade_steps
            }
            
            scenes_data = [scene_data]
            
            # Tallenna
            output_path = props.json_output_path
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(scenes_data, f, indent=2, ensure_ascii=False)
            
            self.report({'INFO'}, f"JSON viety: {output_path}")
            print(f"💾 JSON tallennettu: {output_path}")
            print(f"🎛️  Kanavat: {', '.join(sorted(channels_data.keys(), key=int))}")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Virhe JSON-viennissä: {e}")
            return {'CANCELLED'}
    
    def scan_blender_lights(self, context):
        """Skannaa Blenderin valot"""
        props = context.scene.midi_light_props
        channels = {}
        
        # RGBW-mappings
        RGBW_GROUPS = {
            "RGBW 13-16": [13, 14, 15, 16],
            "RGBW 17-20": [17, 18, 19, 20],
            "RGBW 25-28": [25, 26, 27, 28],
            "RGBW 29-32": [29, 30, 31, 32],
            "RGBW 33-36": [33, 34, 35, 36],
            "RGBW 37-40": [37, 38, 39, 40],
        }
        
        for obj in bpy.data.objects:
            if obj.type != 'LIGHT' or obj.data.energy <= 1.001:
                continue
            
            light_name = obj.name
            energy = obj.data.energy
            color = list(obj.data.color)
            
            # Hae kanavat
            channel_list = self.get_channels_from_name(light_name, RGBW_GROUPS)
            if not channel_list:
                continue
            
            if len(channel_list) == 4:
                # RGBW-ryhmä
                rgbw_values = self.analyze_rgbw_color(color, energy, props.max_wattage)
                
                for i, channel in enumerate(channel_list):
                    channel_energy = rgbw_values[i] * props.max_wattage
                    velocity = self.energy_to_velocity(channel_energy, props.max_wattage)
                    
                    if velocity > 0:
                        channels[str(channel)] = velocity
                        
            elif len(channel_list) == 1:
                # Yksittäinen kanava
                channel = channel_list[0]
                velocity = self.energy_to_velocity(energy, props.max_wattage)
                channels[str(channel)] = velocity
        
        return channels
    
    def get_channels_from_name(self, light_name, rgbw_groups):
        """Päättelee kanavat nimestä"""
        if light_name in rgbw_groups:
            return rgbw_groups[light_name]
        
        try:
            channel = int(light_name.strip())
            if 1 <= channel <= 40:
                return [channel]
        except ValueError:
            pass
        
        import re
        numbers = re.findall(r'\d+', light_name)
        if numbers:
            try:
                channel = int(numbers[-1])
                if 1 <= channel <= 40:
                    return [channel]
            except ValueError:
                pass
        
        return []
    
    def analyze_rgbw_color(self, color, energy, max_wattage):
        """Jakaa RGB-värin RGBW-kanaviin"""
        r, g, b = color[:3]
        
        white_component = min(r, g, b) * 0.6
        pure_r = max(0.0, r - white_component)
        pure_g = max(0.0, g - white_component)
        pure_b = max(0.0, b - white_component)
        
        energy_factor = min(1.0, energy / max_wattage)
        
        return [
            pure_r * energy_factor,
            pure_g * energy_factor,
            pure_b * energy_factor,
            white_component * energy_factor
        ]
    
    def energy_to_velocity(self, energy, max_wattage):
        """Muuntaa energian velocity-arvoksi"""
        if energy <= 1.001:
            return 0
        velocity = int((energy / max_wattage) * 127)
        return min(127, max(1, velocity))

class MIDI_OT_create_test_lights(Operator):
    """Luo testivaloja värinäkyvyyden tarkistamiseen"""
    bl_idname = "midi.create_test_lights"
    bl_label = "Create Test Lights"
    bl_description = "Luo värikkäitä testivaloja viewport-asetusten tarkistamiseen"
    
    def execute(self, context):
        try:
            # Poista vanhat testivalot
            for obj in list(bpy.data.objects):
                if obj.name.startswith("ColorTest_"):
                    bpy.data.objects.remove(obj, do_unlink=True)
            
            # Luo testivaloja
            colors = [
                ("Red", (1.0, 0.0, 0.0)),
                ("Green", (0.0, 1.0, 0.0)),
                ("Blue", (0.0, 0.0, 1.0)),
                ("White", (1.0, 1.0, 1.0)),
                ("Yellow", (1.0, 1.0, 0.0)),
                ("Magenta", (1.0, 0.0, 1.0)),
                ("Cyan", (0.0, 1.0, 1.0)),
                ("Orange", (1.0, 0.5, 0.0))
            ]
            
            for i, (name, color) in enumerate(colors):
                x = (i % 4) * 3
                y = (i // 4) * 3
                location = (x, y, 3)
                
                bpy.ops.object.light_add(type='SPOT', location=location)
                light_obj = bpy.context.object
                light_obj.name = f"ColorTest_{name}"
                light_obj.data.name = f"ColorTest_{name}_Data"
                light_obj.data.color = color
                light_obj.data.energy = 50.0
                light_obj.data.spot_size = 1.0
            
            # Aseta viewport Material Preview -tilaan
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.shading.type = 'MATERIAL'
                            area.tag_redraw()
                            break
            
            bpy.context.view_layer.update()
            
            self.report({'INFO'}, f"Luotu {len(colors)} testivaloa!")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Virhe testivalojen luonnissa: {e}")
            return {'CANCELLED'}

class MIDI_OT_restore_lights(Operator):
    """Palauttaa kaikki valot näkyviksi valkoisella valolla"""
    bl_idname = "midi.restore_lights"
    bl_label = "Restore Lights"
    bl_description = "Palauttaa kaikki valot näkyviksi valkoisella valolla (50W)"
    
    def execute(self, context):
        try:
            restored_count = 0
            
            for obj in bpy.data.objects:
                if obj.type == 'LIGHT' and obj.data:
                    # Aseta hyvä näkyvä energia
                    obj.data.energy = 50.0
                    
                    # Aseta valkoinen väri
                    obj.data.color = (1.0, 1.0, 1.0)
                    
                    restored_count += 1
            
            # Aseta viewport Material Preview -tilaan
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.shading.type = 'MATERIAL'
                            area.tag_redraw()
                            break
            
            bpy.context.view_layer.update()
            
            if restored_count > 0:
                self.report({'INFO'}, f"{restored_count} valoa palautettu näkyviksi!")
            else:
                self.report({'WARNING'}, "Ei löytynyt valoja palautettavaksi!")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Virhe valojen palauttamisessa: {e}")
            return {'CANCELLED'}

class MIDI_OT_scan_existing_lights(Operator):
    """Skannaa olemassa olevat valot ja analysoi nimet"""
    bl_idname = "midi.scan_existing_lights"
    bl_label = "Scan Existing Lights"
    bl_description = "Skannaa olemassa olevat valot ja ehdottaa MIDI-mappingia"
    
    def execute(self, context):
        try:
            # Skannaa kaikki valot
            all_lights = []
            lights_collection = None
            
            # Etsi Lights collection
            for collection in bpy.data.collections:
                if 'Light' in collection.name or 'light' in collection.name.lower():
                    lights_collection = collection
                    break
            
            if lights_collection:
                print(f"📁 Löydettiin collection: '{lights_collection.name}'")
                for obj in lights_collection.objects:
                    if obj.type == 'LIGHT':
                        all_lights.append(obj.name)
            else:
                # Skannaa kaikki valot
                for obj in bpy.data.objects:
                    if obj.type == 'LIGHT':
                        all_lights.append(obj.name)
            
            if not all_lights:
                self.report({'WARNING'}, "Ei löytynyt valoja!")
                return {'CANCELLED'}
            
            # Tulosta console:een
            print("\n" + "="*50)
            print("🔍 BLENDER LIGHTS SCANNER")
            print("="*50)
            print(f"📊 Löydettiin {len(all_lights)} valoa:")
            
            for i, name in enumerate(sorted(all_lights), 1):
                obj = bpy.data.objects.get(name)
                if obj and obj.type == 'LIGHT':
                    energy = obj.data.energy
                    color = obj.data.color
                    print(f"  {i:2d}. {name} - {energy:.1f}W - RGB({color[0]:.2f},{color[1]:.2f},{color[2]:.2f})")
            
            # Ehdota mappingia älykästä järjestystä käyttäen
            def extract_channel_number(light_name):
                import re
                numbers = re.findall(r'\d+', light_name)
                if numbers:
                    return int(numbers[0])
                return 999 + hash(light_name) % 1000
            
            smart_sorted = sorted(all_lights, key=extract_channel_number)
            
            print("\n💡 EHDOTETTU MIDI-MAPPAUS (älykäs järjestys):")
            print("-" * 40)
            
            channel_mapping = {}
            used_channels = set()
            
            # Tunnista eksplisiittiset kanavat ensin
            for light_name in all_lights:
                import re
                numbers = re.findall(r'\d+', light_name)
                if numbers:
                    potential_channel = int(numbers[0])
                    if 1 <= potential_channel <= 40 and potential_channel not in used_channels:
                        channel_mapping[potential_channel] = light_name
                        used_channels.add(potential_channel)
                        print(f"  Kanava {potential_channel:2d} ← {light_name} 🎯 (tunnistettu)")
            
            # Täytä loput järjestyksessä
            next_channel = 1
            for light_name in smart_sorted:
                if light_name not in channel_mapping.values():
                    while next_channel in used_channels and next_channel <= 40:
                        next_channel += 1
                    if next_channel <= 40:
                        channel_mapping[next_channel] = light_name
                        used_channels.add(next_channel)
                        print(f"  Kanava {next_channel:2d} ← {light_name}")
                        next_channel += 1
            
            if len(all_lights) > 40:
                print(f"\n⚠️  {len(all_lights)} valoa > 40 kanavaa (Scene Setter max)")
            
            print("\n📋 Skannaus valmis! Katso Console-tulosteet.")
            print("="*50)
            
            self.report({'INFO'}, f"Skannattu {len(all_lights)} valoa - katso Console!")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Virhe skannauksessa: {e}")
            return {'CANCELLED'}

# ==========================================
# PANELS (Käyttöliittymä)
# ==========================================

class MIDI_PT_main_panel(Panel):
    """Pääpaneeli"""
    bl_label = "MIDI Light Controller"
    bl_idname = "MIDI_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MIDI Lights'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.midi_light_props
        
        # Status
        box = layout.box()
        box.label(text="Status:", icon='INFO')
        if MIDO_AVAILABLE:
            box.label(text="✅ mido-kirjasto asennettu", icon='CHECKMARK')
        else:
            box.label(text="❌ mido-kirjasto puuttuu", icon='ERROR')
            box.operator("midi.install_mido", icon='IMPORT')
        
        layout.separator()
        
        # Yleiset toiminnot
        box = layout.box()
        box.label(text="Toiminnot:", icon='TOOL_SETTINGS')
        
        row = box.row(align=True)
        row.operator("midi.clear_animation", icon='X')
        row.operator("midi.restore_lights", icon='LIGHT_SUN')
        
        row = box.row(align=True)
        row.operator("midi.create_test_lights", icon='LIGHT')
        row.operator("midi.scan_existing_lights", icon='VIEWZOOM')

class MIDI_PT_import_panel(Panel):
    """MIDI-tuonti paneeli"""
    bl_label = "MIDI Import"
    bl_idname = "MIDI_PT_import_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MIDI Lights'
    bl_parent_id = "MIDI_PT_main_panel"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.midi_light_props
        
        # MIDI-tiedosto
        layout.prop(props, "midi_file_path")
        
        # Asetukset
        col = layout.column()
        col.prop(props, "fps")
        col.prop(props, "max_wattage")
        col.prop(props, "use_rgbw_groups")
        
        # Savukone-asetukset
        col.separator()
        col.prop(props, "enable_smoke_machines")
        if props.enable_smoke_machines:
            sub_col = col.column()
            sub_col.prop(props, "smoke_density_multiplier")
            sub_col.label(text="Channels 41-45 = Smoke Machines", icon='OUTLINER_OB_VOLUME')
        
        layout.separator()
        
        # Tuonti-nappi
        layout.operator("midi.import_midi", icon='IMPORT', text="Import MIDI Animation")

class MIDI_PT_export_panel(Panel):
    """JSON-vienti paneeli"""
    bl_label = "JSON Export"
    bl_idname = "MIDI_PT_export_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MIDI Lights'
    bl_parent_id = "MIDI_PT_main_panel"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.midi_light_props
        
        # Vientiasetukset
        layout.prop(props, "json_output_path")
        layout.prop(props, "scene_name")
        
        col = layout.column()
        col.prop(props, "fade_in_duration")
        col.prop(props, "fade_out_duration")
        col.prop(props, "fade_steps")
        
        layout.separator()
        
        # Vienti-nappi
        layout.operator("midi.export_json", icon='EXPORT', text="Export Blender Setup")

# ==========================================
# REGISTRATION
# ==========================================

classes = (
    MIDILightProperties,
    MIDI_OT_install_mido,
    MIDI_OT_clear_animation,
    MIDI_OT_import_midi,
    MIDI_OT_export_json,
    MIDI_OT_create_test_lights,
    MIDI_OT_restore_lights,
    MIDI_OT_scan_existing_lights,
    MIDI_PT_main_panel,
    MIDI_PT_import_panel,
    MIDI_PT_export_panel,
)

def register():
    """Rekisteröi lisäosa"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.midi_light_props = bpy.props.PointerProperty(type=MIDILightProperties)
    
    print("🎭 MIDI Light Controller lisäosa rekisteröity!")

def unregister():
    """Poista lisäosa"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.midi_light_props
    
    print("🎭 MIDI Light Controller lisäosa poistettu!")

if __name__ == "__main__":
    register()