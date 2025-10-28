"""
Parannettu versio MIDI-tuonnista RGBW-värinsekoituksella
Osaa käsitellä RGBW-valoja älykkäästi ja sekoittaa värejä realistisesti
"""

import mido
import bpy
import os
import re

# RGBW-värinsekoituksen globaali tila
enhanced_rgbw_channel_states = {}

def get_rgbw_channels(light_name):
    """Palauttaa RGBW-valon kanavanumerot tai None jos ei ole RGBW"""
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
    global enhanced_rgbw_channel_states
    
    light_name = light_obj.name
    rgbw_channels = get_rgbw_channels(light_name)
    
    if not rgbw_channels:
        return False  # Ei ole RGBW-valo
    
    # Alusta valon tila jos ei ole vielä
    if light_name not in enhanced_rgbw_channel_states:
        enhanced_rgbw_channel_states[light_name] = {'r': 0, 'g': 0, 'b': 0, 'w': 0}
    
    # Päivitä kanavan arvo
    state = enhanced_rgbw_channel_states[light_name]
    for color, ch in rgbw_channels.items():
        if ch == channel:
            state[color] = velocity
            print(f"🎨 Enhanced: {light_name}: {color.upper()} kanava {ch} = {velocity}")
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
    
    print(f"💡 Enhanced: {light_name}: RGB({final_r:.2f}, {final_g:.2f}, {final_b:.2f}) intensity={total_intensity}")
    return total_intensity

def clear_light_keyframes():
    """Tyhjentää kaikki valojen animaatiot ja RGBW-tilan"""
    global enhanced_rgbw_channel_states
    
    # Tyhjennä RGBW-tila
    enhanced_rgbw_channel_states = {}
    print("🧹 Enhanced: RGBW-tila tyhjennetty")
    
    print("🧹 Tyhjennetään vanhat keyframet...")
    cleared_count = 0
    
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            # Tyhjennä objektin animaatio
            if obj.animation_data:
                obj.animation_data_clear()
            
            # Tyhjennä datan animaatio  
            if obj.data.animation_data:
                obj.data.animation_data_clear()
            
            # Nollaa arvot
            obj.data.energy = 1.0  # Minimaalinen, ei nolla
            obj.data.color = (1.0, 1.0, 1.0)  # Valkoinen
            cleared_count += 1
    
    print(f"✅ {cleared_count} valon animaatiot poistettu.")

def create_missing_lights():
    """DEPRECATED - Ei luo enää uusia valoja! Käyttää Lights collectionin valoja."""
    
    print("⚠️  create_missing_lights() on vanhentunut!")
    print("🔍 Käytetään vain Lights collectionin olemassa olevia valoja")
    
    # Etsi Lights collection
    lights_collection = None
    for collection in bpy.data.collections:
        if 'Light' in collection.name or 'light' in collection.name.lower():
            lights_collection = collection
            print(f"📁 Löydettiin collection: {collection.name}")
            break
    
    if not lights_collection:
        print("❌ Ei löytynyt Lights collectionia!")
        return
    
    # Listaa olemassa olevat valot
    existing_lights = []
    for obj in lights_collection.objects:
        if obj.type == 'LIGHT':
            existing_lights.append(obj.name)
    
    print(f"💡 Lights collectionin valot ({len(existing_lights)} kpl):")
    for light_name in sorted(existing_lights):
        print(f"  - {light_name}")
    
    print("✅ Käytetään näitä valoja - ei luoda uusia!")

def get_rgbw_group(note):
    """Palauttaa RGBW-ryhmän nimen ja väri-indeksin"""
    for note_range, group_name in rgbw_map.items():
        if note in note_range:
            return group_name, note - min(note_range)  # RGBW-indeksi 0–3
    return None, None

def insert_rgbw_keyframe(obj, rgbw_values, frame):
    """Asettaa RGBW-keyframen värisekoituksella"""
    r, g, b, w = rgbw_values
    
    # Värimixaus: lisää white kaikkiin väreihin
    color = [
        min(1.0, r + w * 0.3),  # White lisää punaista
        min(1.0, g + w * 0.3),  # White lisää vihreää  
        min(1.0, b + w * 0.3)   # White lisää sinistä
    ]
    
    # Intensiteetti: maksimi kaikista kanavista
    intensity = max(r, g, b, w) * 300
    
    # Aseta arvot
    obj.data.color = color
    obj.data.energy = intensity
    
    # Tallenna keyframet
    obj.data.keyframe_insert(data_path="color", frame=frame)
    obj.data.keyframe_insert(data_path="energy", frame=frame)
    
    print(f"[RGBW] {obj.name} @ frame {frame}: RGBW=({r:.2f},{g:.2f},{b:.2f},{w:.2f}) → color={color}, energy={intensity:.1f}W")

def insert_white_keyframe(obj, velocity, frame):
    """Asettaa valkoisen valon keyframen"""
    intensity = velocity / 127.0 * 300
    
    obj.data.color = [1.0, 1.0, 1.0]
    obj.data.energy = intensity
    
    obj.data.keyframe_insert(data_path="color", frame=frame)
    obj.data.keyframe_insert(data_path="energy", frame=frame)
    
    print(f"[WHITE] {obj.name} @ frame {frame}: velocity={velocity} → energy={intensity:.1f}W")

def parse_midi_and_keyframe(midi_path, fps=24):
    """Pääfunktio: parsii MIDI:n ja luo keyframe-animaation"""
    
    if not os.path.exists(midi_path):
        print(f"❌ MIDI-tiedostoa ei löydy: {midi_path}")
        return False
    
    print(f"🎼 MIDI → keyframe-animaatio: {os.path.basename(midi_path)}")
    print(f"📁 Polku: {midi_path}")
    
    try:
        mid = mido.MidiFile(midi_path)
    except Exception as e:
        print(f"❌ Virhe MIDI-tiedoston lukemisessa: {e}")
        return False
    
    # Valmistele Blender
    clear_light_keyframes()
    create_missing_lights()
    
    # Aseta FPS
    bpy.context.scene.render.fps = fps
    
    # RGBW-ryhmien tila (muistaa kunkin ryhmän RGBW-arvot)
    rgbw_state = {group: [0.0, 0.0, 0.0, 0.0] for group in rgbw_map.values()}
    
    time_accum = 0.0
    processed_events = 0
    max_frame = 0
    
    print(f"🎵 Käsitellään MIDI-tapahtumia (fps={fps})...")
    
    # Käy läpi kaikki MIDI-viestit
    for msg in mid:
        time_accum += msg.time
        
        if msg.type == 'note_on' and msg.velocity > 0 and 70 <= msg.note <= 109:
            frame = round(time_accum * fps)
            max_frame = max(max_frame, frame)
            
            # Tarkista onko RGBW-ryhmässä
            group, index = get_rgbw_group(msg.note)
            
            if group is not None and 0 <= index < 4:
                # RGBW-kanava
                rgbw_state[group][index] = msg.velocity / 127.0
                
                obj = bpy.data.objects.get(group)
                if obj and obj.type == 'LIGHT':
                    insert_rgbw_keyframe(obj, rgbw_state[group], frame)
                    processed_events += 1
                else:
                    print(f"⚠️  RGBW-ryhmä {group} ei löydy")
            
            else:
                # Yksittäinen valkoinen kanava
                channel = msg.note - 69
                
                if channel in rgbw_channels:
                    # Tämä kanava kuuluu RGBW-ryhmään, ohita
                    continue
                
                obj = bpy.data.objects.get(str(channel))
                if obj and obj.type == 'LIGHT':
                    insert_white_keyframe(obj, msg.velocity, frame)
                    processed_events += 1
                else:
                    print(f"⚠️  Kanava {channel} ei löydy")
    
    # Aseta animaation pituus
    if max_frame > 0:
        bpy.context.scene.frame_end = max_frame
        print(f"🎬 Animaation pituus: {max_frame} framea ({max_frame/fps:.1f}s)")
    
    print(f"✅ Keyframe-animaatio valmis!")
    print(f"📊 Käsiteltiin {processed_events} tapahtumaa")
    print(f"🎭 RGBW-ryhmät: {len(rgbw_state)}")
    
    return True

def quick_test_animation():
    """Pikatesti: toista animaatio automaattisesti"""
    bpy.context.scene.frame_current = 1
    print("🎬 Toista animaatio nähdäksesi valot!")
    print("   Paina SPACE tai klikkaa ▶️ Play")

# 🎯 KÄYTTÖ - Muokkaa tätä polkua:
MIDI_FILE = "/Users/raulivirtanen/Documents/Kalareissu_fade_in.mid"

if __name__ == "__main__":
    success = parse_midi_and_keyframe(MIDI_FILE)
    if success:
        quick_test_animation()
        print("🎉 Skripti valmis! Nauti valoshow'sta! 🌈")