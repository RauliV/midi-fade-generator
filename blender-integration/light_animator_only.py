"""
Kevyt MIDI-animaattori olemassa oleville valoille
Ei luo uusia valoja eikä muuta setuppia - vain animoi olemassa olevia!
"""

import mido
import bpy
import os

# RGBW-ryhmien nuottialueet (sinun määrityksesi)
rgbw_map = {
    range(82, 86): "RGBW 13-16",
    range(86, 90): "RGBW 17-20", 
    range(94, 98): "RGBW 25-28",
    range(98, 102): "RGBW 29-32",
    range(102, 106): "RGBW 33-36",
    range(106, 110): "RGBW 37-40",
}

# RGBW-kanavat
rgbw_channels = set()
for note_range in rgbw_map:
    for note in note_range:
        channel = note - 69
        rgbw_channels.add(channel)

def clear_light_keyframes_only():
    """Tyhjentää VAIN keyframet - ei koske valojen perusasetuksia"""
    print("🧹 Tyhjennetään vanhat keyframet (setup säilyy)...")
    cleared_count = 0
    
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            # Tyhjennä vain animaatiot, ei perusasetuksia
            if obj.animation_data:
                obj.animation_data_clear()
            if obj.data.animation_data:
                obj.data.animation_data_clear()
            cleared_count += 1
    
    print(f"✅ {cleared_count} valon keyframet poistettu - setup säilyi")

def get_rgbw_group(note):
    """Palauttaa RGBW-ryhmän nimen ja väri-indeksin"""
    for note_range, group_name in rgbw_map.items():
        if note in note_range:
            return group_name, note - min(note_range)  # RGBW-indeksi 0–3
    return None, None

def insert_rgbw_keyframe(obj, rgbw_values, frame):
    """Asettaa RGBW-keyframen paremmalla värisekoituksella"""
    r, g, b, w = rgbw_values
    
    # Parannettu värimixaus: white nostaa kaikkia värikanavia
    color = [
        min(1.0, r + w * 0.3),  # White lisää lämpöä punaiseen
        min(1.0, g + w * 0.3),  # White kirkastaa vihreää
        min(1.0, b + w * 0.3)   # White lämmittää sinistä
    ]
    
    # Intensiteetti: maksimi kanavista + white-boost
    base_intensity = max(r, g, b, w)
    white_boost = w * 0.2  # White antaa lisäintensiteettiä
    intensity = min(1.0, base_intensity + white_boost) * 300
    
    # Aseta arvot
    obj.data.color = color
    obj.data.energy = intensity
    
    # Tallenna keyframet
    obj.data.keyframe_insert(data_path="color", frame=frame)
    obj.data.keyframe_insert(data_path="energy", frame=frame)
    
    print(f"🌈 {obj.name} @ {frame}: RGBW({r:.2f},{g:.2f},{b:.2f},{w:.2f}) → {intensity:.1f}W")

def insert_white_keyframe(obj, velocity, frame):
    """Asettaa valkoisen valon keyframen (säilyttää värin)"""
    intensity = velocity / 127.0 * 300
    
    # Säilytä valon alkuperäinen väri, muuta vain intensiteettiä
    current_color = list(obj.data.color)  # Säilytä nykyinen väri
    
    obj.data.color = current_color  # Pidä sama väri
    obj.data.energy = intensity
    
    obj.data.keyframe_insert(data_path="energy", frame=frame)
    # Lisää väri-keyframe vain jos väri muuttui
    if any(c != 1.0 for c in current_color):
        obj.data.keyframe_insert(data_path="color", frame=frame)
    
    print(f"💡 {obj.name} @ {frame}: velocity={velocity} → {intensity:.1f}W (väri säilyi)")

def animate_existing_lights(midi_path, fps=24):
    """Animoi olemassa olevia valoja - EI luo uusia eikä muuta setuppia"""
    
    if not os.path.exists(midi_path):
        print(f"❌ MIDI-tiedostoa ei löydy: {midi_path}")
        return False
    
    print(f"🎼 Animoidaan olemassa olevia valoja: {os.path.basename(midi_path)}")
    
    try:
        mid = mido.MidiFile(midi_path)
    except Exception as e:
        print(f"❌ Virhe MIDI-lukemisessa: {e}")
        return False
    
    # Tyhjennä vain keyframet
    clear_light_keyframes_only()
    
    # Aseta FPS (jos halutaan)
    if bpy.context.scene.render.fps != fps:
        bpy.context.scene.render.fps = fps
        print(f"🎬 FPS asetettu: {fps}")
    
    # RGBW-ryhmien tila
    rgbw_state = {group: [0.0, 0.0, 0.0, 0.0] for group in rgbw_map.values()}
    
    time_accum = 0.0
    processed_events = 0
    missing_lights = set()
    max_frame = 0
    
    print(f"🎵 Käsitellään MIDI-tapahtumia...")
    
    # Käy läpi MIDI-viestit
    for msg in mid:
        time_accum += msg.time
        
        if msg.type == 'note_on' and msg.velocity > 0 and 70 <= msg.note <= 109:
            frame = round(time_accum * fps)
            max_frame = max(max_frame, frame)
            
            # Tarkista RGBW-ryhmä
            group, index = get_rgbw_group(msg.note)
            
            if group is not None and 0 <= index < 4:
                # RGBW-kanava
                rgbw_state[group][index] = msg.velocity / 127.0
                
                obj = bpy.data.objects.get(group)
                if obj and obj.type == 'LIGHT':
                    insert_rgbw_keyframe(obj, rgbw_state[group], frame)
                    processed_events += 1
                else:
                    missing_lights.add(group)
            
            else:
                # Yksittäinen kanava
                channel = msg.note - 69
                
                if channel in rgbw_channels:
                    continue  # Tämä kuuluu RGBW-ryhmään
                
                obj = bpy.data.objects.get(str(channel))
                if obj and obj.type == 'LIGHT':
                    insert_white_keyframe(obj, msg.velocity, frame)
                    processed_events += 1
                else:
                    missing_lights.add(str(channel))
    
    # Aseta animaation pituus
    if max_frame > 0:
        bpy.context.scene.frame_end = max_frame
        print(f"🎬 Animaation pituus: {max_frame} framea ({max_frame/fps:.1f}s)")
    
    # Raportoi tulokset
    print(f"✅ Animaatio valmis!")
    print(f"📊 Käsiteltiin {processed_events} tapahtumaa")
    
    if missing_lights:
        print(f"⚠️  Seuraavia valoja ei löytynyt: {', '.join(sorted(missing_lights))}")
        print("   Tarkista valojen nimet Blenderissä")
    
    return True

def analyze_current_setup():
    """Analysoi nykyiset valot (auttaa debuggaamisessa)"""
    print("🔍 Analysoidaan nykyiset valot:")
    
    rgbw_found = []
    channel_found = []
    other_lights = []
    
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            name = obj.name
            if name in rgbw_map.values():
                rgbw_found.append(name)
            elif name.isdigit() and 1 <= int(name) <= 40:
                channel_found.append(name)
            else:
                other_lights.append(name)
    
    print(f"🌈 RGBW-ryhmät ({len(rgbw_found)}): {', '.join(sorted(rgbw_found))}")
    print(f"💡 Kanavat ({len(channel_found)}): {', '.join(sorted(channel_found, key=int))}")
    if other_lights:
        print(f"❓ Muut valot ({len(other_lights)}): {', '.join(other_lights)}")
    
    print(f"📊 Yhteensä {len(rgbw_found) + len(channel_found) + len(other_lights)} valoa löytyi")

# 🎯 KÄYTTÖ - Muokkaa tätä polkua:
MIDI_FILE = "/Users/raulivirtanen/Documents/Kalareissu_fade_in.mid"

if __name__ == "__main__":
    print("🎭 MIDI Light Animator - Vain animaatio, ei setupin muutoksia!")
    print("=" * 60)
    
    # Analysoi nykyinen setup
    analyze_current_setup()
    print()
    
    # Animoi valot
    success = animate_existing_lights(MIDI_FILE)
    
    if success:
        print("🎉 Animaatio valmis! Paina SPACE toistaaksesi! 🌈")
        print("💡 Vinkki: Aseta timeline alkuun (frame 1) ennen toistoa")
    else:
        print("💥 Animoinnissa tapahtui virhe!")