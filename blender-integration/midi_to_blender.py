"""
MIDI to Blender Light Animation Importer

Lukee MIDI-tiedoston ja luo Blender-valoanimaaation.
Jokainen MIDI-kanava ohjaa yhtä valoa Scene Setter -logiikalla.

Käyttö Blenderissä:
1. Avaa Text Editor
2. Lataa tämä skripti
3. Muokkaa MIDI_FILE_PATH polkua
4. Aja skripti

Vaatimukset:
- Blender 3.0+
- mido-kirjasto (pip install mido)
"""

import bpy
import bmesh
import os
import sys

# Lisää mido polkuun jos ei löydy
try:
    import mido
except ImportError:
    print("Asennetaan mido-kirjasto...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mido"])
    import mido

# ASETUKSET - Muokkaa näitä tarpeen mukaan
MIDI_FILE_PATH = "/Users/raulivirtanen/Documents/Kalareissu_fade_in.mid"
FPS = 24  # Blenderin framerate
MAX_WATTAGE = 300  # Maksimi teho watteina
RGBW_GROUPS = True  # True = käytä RGBW-ryhmiä, False = yksittäiset spotit

def clear_animation():
    """Tyhjennä kaikki animaatiot ja keyframet"""
    global rgbw_channel_states
    
    # Tyhjennä RGBW-tila
    rgbw_channel_states = {}
    
    for obj in bpy.context.scene.objects:
        if obj.type == 'LIGHT':
            obj.animation_data_clear()
            # Nollaa energiat ja värit
            obj.data.energy = 1.0
            obj.data.color = (1.0, 1.0, 1.0)  # Valkoinen
    
    print("🧹 Animaatiot ja RGBW-tila tyhjennetty")

def create_light(name, location=(0, 0, 2)):
    """Luo uuden valon"""
    bpy.ops.object.light_add(type='SPOT', location=location)
    light_obj = bpy.context.object
    light_obj.name = name
    light_obj.data.name = f"{name}_Data"
    light_obj.data.energy = 10.0  # Aloita näkyvällä energialla
    light_obj.data.spot_size = 1.2  # 70 astetta
    return light_obj

def get_or_create_light(channel):
    """Hakee valon VAIN Lights collectionista - ei luo uusia!"""
    
    print(f"🔍 Etsitään valoa kanavalle {channel} Lights collectionista")
    
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
    
    if not collection_lights:
        print("❌ Ei valoja Lights collectionissa!")
        return None
    
    # ENSIKSI: Etsi RGBW x-y muotoa ("RGBW 33-36")
    for light_obj in collection_lights:
        light_name = light_obj.name
        if light_name.startswith('RGBW '):
            import re
            range_match = re.search(r'RGBW (\d+)-(\d+)', light_name)
            if range_match:
                start_ch = int(range_match.group(1))
                end_ch = int(range_match.group(2))
                if start_ch <= channel <= end_ch:
                    print(f"🎯 RGBW range: {light_name} sisältää kanavan {channel}")
                    return light_obj
    
    # TOISEKSI: Etsi Spot-valoja ("Spot.012")
    for light_obj in collection_lights:
        light_name = light_obj.name
        if 'Spot' in light_name:
            import re
            numbers = re.findall(r'\d+', light_name)
            for num_str in numbers:
                if int(num_str) == channel:
                    print(f"🎯 Spot match: {light_name} = kanava {channel}")
                    return light_obj
    
    # KOLMANNEKSI: Etsi mitä tahansa numeroa
    for light_obj in collection_lights:
        light_name = light_obj.name
        import re
        numbers = re.findall(r'\d+', light_name)
        for num_str in numbers:
            if int(num_str) == channel:
                print(f"🎯 Numero match: {light_name} = kanava {channel}")
                return light_obj
    
    # NELJÄNNEKSI: Ota järjestyksessä
    if channel <= len(collection_lights):
        def smart_sort_key(light_obj):
            import re
            numbers = re.findall(r'\d+', light_obj.name)
            return int(numbers[0]) if numbers else 999
        
        sorted_lights = sorted(collection_lights, key=smart_sort_key)
        target_light = sorted_lights[channel - 1]
        print(f"🎯 Järjestys: {target_light.name} = kanava {channel}")
        return target_light
    
    # VIIMEISEKSI: Fallback ensimmäiseen valoon
    if collection_lights:
        fallback = collection_lights[0]
        print(f"⚠️  Fallback: {fallback.name} kanavalle {channel}")
        return fallback
    
    print(f"❌ Ei löytynyt mitään valoa kanavalle {channel}")
    return None

def velocity_to_energy(velocity):
    """Muuntaa MIDI velocity energiaksi - realistinen Scene Setter skaala"""
    if velocity == 0:
        return 1.0  # Minimaalinen energia jotta väri näkyy
    
    # Perusskaalaus
    base_energy = 5.0 + (velocity / 127.0) * (MAX_WATTAGE - 5.0)
    
    # Pikkuspotit ovat todella kirkkaita Scene Setterissä
    # Velocity 60 pikkuspotit = liian kirkkaat kasvoille
    # Velocity 127 RGBW:t = heikot verrattuna pikkuspotteihin
    
    # Simuloidaan tätä: matalat velocity-arvot = todennäköisesti pikkuspotit
    if 40 <= velocity <= 80:  # Pikkuspotti-alue
        return base_energy * 2.5  # 2.5x kirkkaita
    else:
        return base_energy  # RGBW:t normaalilla skaalalla

# RGBW-värinsekoituksen globaali tila
rgbw_channel_states = {}  # {light_name: {r: velocity, g: velocity, b: velocity, w: velocity}}

def get_rgbw_channels(light_name):
    """Palauttaa RGBW-valon kanavanumerot tai None jos ei ole RGBW"""
    # Etsi RGBW-numeroita nimestä (esim. "RGBW 33-36")
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
    light_name = light_obj.name
    rgbw_channels = get_rgbw_channels(light_name)
    
    if not rgbw_channels:
        return False  # Ei ole RGBW-valo
    
    # Alusta valon tila jos ei ole vielä
    if light_name not in rgbw_channel_states:
        rgbw_channel_states[light_name] = {'r': 0, 'g': 0, 'b': 0, 'w': 0}
    
    # Päivitä kanavan arvo
    state = rgbw_channel_states[light_name]
    for color, ch in rgbw_channels.items():
        if ch == channel:
            state[color] = velocity
            print(f"🎨 {light_name}: {color.upper()} kanava {ch} = {velocity}")
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
    
    # Laske kokonaisteho (käytetään suurinta kanavaa + valkoinen)
    max_channel = max(state['r'], state['g'], state['b'])
    total_intensity = max(max_channel, state['w'])
    energy = velocity_to_energy(total_intensity)
    light_obj.data.energy = energy
    
    print(f"💡 {light_name}: RGB({final_r:.2f}, {final_g:.2f}, {final_b:.2f}) energia={energy:.1f}W")
    return True

def import_midi_to_blender(midi_path):
    """Pääfunktio: tuo MIDI-tiedosto Blenderiin"""
    
    if not os.path.exists(midi_path):
        print(f"❌ MIDI-tiedostoa ei löydy: {midi_path}")
        return False
    
    print(f"🎵 Ladataan MIDI: {midi_path}")
    
    try:
        midi_file = mido.MidiFile(midi_path)
    except Exception as e:
        print(f"❌ Virhe MIDI-tiedoston lukemisessa: {e}")
        return False
    
    # Tyhjennä vanhat animaatiot
    clear_animation()
    
    # Aseta Blenderin FPS
    bpy.context.scene.render.fps = FPS
    
    print(f"🎬 FPS: {FPS}, Ticks per beat: {midi_file.ticks_per_beat}")
    
    # Käsittele MIDI-tapahtumat
    current_time = 0
    processed_events = 0
    
    for track_num, track in enumerate(midi_file.tracks):
        print(f"📊 Käsitellään track {track_num}: {len(track)} viestiä")
        
        track_time = 0
        
        for msg in track:
            track_time += msg.time
            
            if hasattr(msg, 'type') and msg.type == 'note_on':
                # Muunna MIDI-nuotti kanavaksi (nuotti 70 = kanava 1)
                channel = msg.note - 69
                
                if channel < 1 or channel > 40:
                    continue  # Scene Setter tukee kanavia 1-40
                
                velocity = msg.velocity
                
                # Muunna aika frameiksi
                frame = int((track_time / midi_file.ticks_per_beat) * FPS * 0.5)  # 120 BPM oletus
                
                # Hae tai luo valo
                light_obj = get_or_create_light(channel)
                if not light_obj:
                    continue
                
                # Tarkista onko RGBW-valo
                if update_rgbw_color(light_obj, channel, velocity):
                    # RGBW-värinsekoitus käsitelty, aseta keyframet väreille ja energialle
                    light_obj.data.keyframe_insert(data_path="color", frame=frame)
                    light_obj.data.keyframe_insert(data_path="energy", frame=frame)
                else:
                    # Tavallinen valo - pelkkä energia
                    energy = velocity_to_energy(velocity)
                    light_obj.data.energy = energy
                    light_obj.data.keyframe_insert(data_path="energy", frame=frame)
                
                processed_events += 1
                
                print(f"💡 Frame {frame}: Kanava {channel} ({light_obj.name}) (velocity {velocity})")
    
    # Aseta animaation pituus
    max_frame = max(1, int(track_time / midi_file.ticks_per_beat * FPS * 0.5))
    bpy.context.scene.frame_end = max_frame
    
    # Pakota koko Blenderin päivitys
    bpy.context.scene.frame_set(1)  # Hyppii frame 1:een
    bpy.context.view_layer.update()  # Päivitä näkymä
    
    # Päivitä myös timeline
    for area in bpy.context.screen.areas:
        if area.type == 'TIMELINE':
            area.tag_redraw()
        elif area.type == 'VIEW_3D':
            area.tag_redraw()
    
    print(f"✅ Tuonti valmis!")
    print(f"📈 Käsiteltiin {processed_events} note_on tapahtumaa")
    print(f"🎬 Animaation pituus: {max_frame} framea ({max_frame/FPS:.1f}s)")
    print(f"🔄 Paina SPACE välilyönti Blenderissä toistaaksesi animaation!")
    
    return True

# Aja tuonti jos skripti ajetaan
if __name__ == "__main__":
    result = import_midi_to_blender(MIDI_FILE_PATH)
    if result:
        print("🎉 MIDI-animaatio luotu onnistuneesti!")
    else:
        print("💥 Tuonnissa tapahtui virhe!")