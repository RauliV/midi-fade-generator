"""
Blender to JSON Scene Exporter

Vie nykyisen Blender-valosetuppisi JSON-muotoon, joka on yhteensopiva
MIDI-generaattorin kanssa.

Käyttö Blenderissä:
1. Aseta valot haluamaasi tilaan
2. Avaa Text Editor
3. Lataa tämä skripti  
4. Muokkaa OUTPUT_PATH polkua
5. Aja skripti

Tulos: JSON-tiedosto joka voidaan ladata MIDI-generaattoriin
"""

import bpy
import json
import os
import mathutils

# ASETUKSET - Muokkaa näitä
OUTPUT_PATH = "/Users/raulivirtanen/Documents/MIDI-Fade-Generator/exported_scene.json"
SCENE_NAME = "Blender_Export"
DEFAULT_FADE_IN = 2.0  # sekuntia
DEFAULT_FADE_OUT = 3.0  # sekuntia
DEFAULT_STEPS = 20
MAX_WATTAGE = 300

def energy_to_velocity(energy):
    """Muuntaa Blenderin energian MIDI velocity-arvoksi"""
    if energy <= 0:
        return 0
    
    # Skaalaa energia velocity-arvoksi (0-127)
    velocity = int((energy / MAX_WATTAGE) * 127)
    return min(127, max(0, velocity))

def get_rgbw_channels_from_name(light_name):
    """Palauttaa RGBW-valon kanavanumerot tai None"""
    import re
    match = re.search(r'RGBW\s+(\d+)-(\d+)', light_name)
    if match:
        start_channel = int(match.group(1))
        end_channel = int(match.group(2))
        if end_channel - start_channel == 3:
            return {
                'r': start_channel,
                'g': start_channel + 1, 
                'b': start_channel + 2,
                'w': start_channel + 3
            }
    return None

def decompose_rgbw_color(rgb_color, intensity=1.0):
    """Purkaa RGB-värin takaisin RGBW-komponentteihin"""
    r, g, b = rgb_color
    
    # Laske valkoisen komponentti (pienin RGB-arvo)
    white_component = min(r, g, b)
    
    # Poista valkoinen puhtaista väreistä
    pure_r = max(0.0, r - white_component)
    pure_g = max(0.0, g - white_component)
    pure_b = max(0.0, b - white_component)
    
    # Skaalaa intensiteetillä ja muunna MIDI-arvoiksi (0-127)
    r_midi = int(pure_r * intensity * 127)
    g_midi = int(pure_g * intensity * 127)
    b_midi = int(pure_b * intensity * 127)
    w_midi = int(white_component * intensity * 127)
    
    return {
        'r': min(127, max(0, r_midi)),
        'g': min(127, max(0, g_midi)),
        'b': min(127, max(0, b_midi)),
        'w': min(127, max(0, w_midi))
    }

def export_rgbw_light_to_channels(light_name, rgb_color, energy):
    """Vie RGBW-valon Blenderistä MIDI-kanaviin"""
    # Tarkista onko RGBW-valo
    channels = get_rgbw_channels_from_name(light_name)
    if not channels:
        return None
    
    # Laske intensiteetti energiasta
    intensity = min(1.0, energy / MAX_WATTAGE)
    
    # Pura väri RGBW-komponentteihin
    rgbw = decompose_rgbw_color(rgb_color, intensity)
    
    # Luo kanava-velocity mapping
    result = {}
    if rgbw['r'] > 0:
        result[channels['r']] = rgbw['r']
    if rgbw['g'] > 0:
        result[channels['g']] = rgbw['g']
    if rgbw['b'] > 0:
        result[channels['b']] = rgbw['b'] 
    if rgbw['w'] > 0:
        result[channels['w']] = rgbw['w']
    
    print(f"🔄 RGBW Export: {light_name} RGB{rgb_color} @ {energy}W")
    print(f"   → Kanavat: {result}")
    
    return result

def get_channel_from_light_name(light_name):
    """Päättelee kanavan valon nimestä"""
    
    # RGBW-ryhmät: "RGBW_5_Red" -> kanava 17 (ryhmä 5, R-kanava)
    if light_name.startswith("RGBW_"):
        try:
            parts = light_name.split("_")
            group_num = int(parts[1])
            color = parts[2]
            
            color_offset = {
                'Red': 0, 'Green': 1, 'Blue': 2, 'White': 3
            }.get(color, 0)
            
            channel = (group_num - 1) * 4 + color_offset + 1
            return channel
            
        except (IndexError, ValueError):
            pass
    
    # Yksittäiset spotit: "Spot_12" -> kanava 12
    if light_name.startswith("Spot_"):
        try:
            channel = int(light_name.split("_")[1])
            return channel
        except (IndexError, ValueError):
            pass
    
    # Numeronimi: "21" -> kanava 21
    try:
        channel = int(light_name)
        return channel
    except ValueError:
        pass
    
    print(f"⚠️  Ei voitu päätellä kanavaa valolle: {light_name}")
    return None

def scan_current_lights():
    """Skannaa kaikki valot nykyisestä scenestä - RGBW-tuki"""
    
    lights_data = {}
    processed_lights = 0
    
    for obj in bpy.data.objects:
        if obj.type != 'LIGHT':
            continue
        
        # Tarkista onko RGBW-valo
        rgbw_channels = export_rgbw_light_to_channels(
            obj.name, 
            obj.data.color, 
            obj.data.energy
        )
        
        if rgbw_channels:
            # RGBW-valo: vie kaikki kanavat
            for channel, velocity in rgbw_channels.items():
                if velocity > 0:
                    lights_data[str(channel)] = velocity
                    processed_lights += 1
            print(f"🎨 RGBW: {obj.name} → {len(rgbw_channels)} kanavaa")
        else:
            # Tavallinen valo: yksittäinen kanava
            channel = get_channel_from_light_name(obj.name)
            if channel is None or channel < 1 or channel > 40:
                print(f"🚫 Ohitetaan valo: {obj.name} (virheellinen kanava)")
                continue
            
            energy = obj.data.energy
            velocity = energy_to_velocity(energy)
            
            if velocity > 0:
                lights_data[str(channel)] = velocity
                processed_lights += 1
                print(f"💡 Normal: {obj.name} → kanava {channel}: {energy:.1f}W = velocity {velocity}")
    
    print(f"📊 Löydettiin {processed_lights} päällä olevaa kanavaa")
    return lights_data

def export_scene_to_json(output_path, scene_name=None):
    """Vie nykyinen valosetup JSON-tiedostoon"""
    
    if scene_name is None:
        scene_name = SCENE_NAME
    
    print(f"📤 Viedään scene: {scene_name}")
    
    # Skannaa valot
    channels = scan_current_lights()
    
    if not channels:
        print("❌ Ei löytynyt päällä olevia valoja!")
        return False
    
    # Luo JSON-rakenne
    scene_data = {
        "name": scene_name,
        "channels": channels,
        "fade_in_duration": DEFAULT_FADE_IN,
        "fade_out_duration": DEFAULT_FADE_OUT,
        "steps": DEFAULT_STEPS
    }
    
    # Varmista että output-hakemisto on olemassa
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Kirjoita JSON-tiedosto
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([scene_data], f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON-tiedosto tallennettu: {output_path}")
        print(f"📊 Kanavia: {len(channels)}")
        print(f"🎛️  Kanavat: {', '.join(sorted(channels.keys(), key=int))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Virhe tiedoston tallentamisessa: {e}")
        return False

def export_multiple_frames_to_json(output_path, frame_range=None):
    """Vie useita frameja JSON-tiedostoon (animaatio -> kohtauksia)"""
    
    if frame_range is None:
        start_frame = bpy.context.scene.frame_start
        end_frame = bpy.context.scene.frame_end
    else:
        start_frame, end_frame = frame_range
    
    scenes_data = []
    current_frame = bpy.context.scene.frame_current
    
    print(f"🎬 Viedään framet {start_frame}-{end_frame}")
    
    for frame in range(start_frame, end_frame + 1, 5):  # Joka 5. frame
        bpy.context.scene.frame_set(frame)
        
        channels = scan_current_lights()
        if channels:  # Tallenna vain jos valoja on päällä
            scene_data = {
                "name": f"Frame_{frame}",
                "channels": channels,
                "fade_in_duration": DEFAULT_FADE_IN,
                "fade_out_duration": DEFAULT_FADE_OUT,
                "steps": DEFAULT_STEPS
            }
            scenes_data.append(scene_data)
    
    # Palauta alkuperäinen frame
    bpy.context.scene.frame_set(current_frame)
    
    if not scenes_data:
        print("❌ Ei löytynyt kohtauksia vietäväksi!")
        return False
    
    # Tallenna JSON
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(scenes_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {len(scenes_data)} kohtausta viety tiedostoon: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Virhe: {e}")
        return False

# Aja vienti jos skripti ajetaan
if __name__ == "__main__":
    result = export_scene_to_json(OUTPUT_PATH)
    if result:
        print("🎉 Scene viety onnistuneesti JSON-muotoon!")
        print(f"📁 Tiedosto: {OUTPUT_PATH}")
        print("💡 Voit nyt ladata tämän MIDI-generaattoriin!")
    else:
        print("💥 Viennissä tapahtui virhe!")