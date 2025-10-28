#!/usr/bin/env python3
"""
🎨 Simple RGBW MIDI to Blender
Yksinkertainen versio RGBW-värinsekoituksella

Käyttö Blenderissä:
1. Exec(open("/path/to/this/file").read())
2. tai import ja käytä funktioita
"""

import mido
import bpy
import re
import os

# Globaali RGBW-tila
simple_rgbw_channel_states = {}

def get_rgbw_channels(light_name):
    """Palauttaa RGBW-valon kanavanumerot tai None"""
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

def update_rgbw_color(light_obj, channel, velocity):
    """RGBW-värinsekoitus"""
    global simple_rgbw_channel_states
    
    light_name = light_obj.name
    rgbw_channels = get_rgbw_channels(light_name)
    
    if not rgbw_channels:
        return False
    
    if light_name not in simple_rgbw_channel_states:
        simple_rgbw_channel_states[light_name] = {'r': 0, 'g': 0, 'b': 0, 'w': 0}
    
    state = simple_rgbw_channel_states[light_name]
    for color, ch in rgbw_channels.items():
        if ch == channel:
            state[color] = velocity
            print(f"🎨 Simple: {light_name}: {color.upper()} ch{ch} = {velocity}")
            break
    
    # Värinsekoitus
    r_intensity = state['r'] / 127.0
    g_intensity = state['g'] / 127.0  
    b_intensity = state['b'] / 127.0
    w_intensity = state['w'] / 127.0
    
    # Valkoinen lisää kaikkia
    final_r = min(1.0, r_intensity + w_intensity * 0.8)
    final_g = min(1.0, g_intensity + w_intensity * 0.8) 
    final_b = min(1.0, b_intensity + w_intensity * 0.8)
    
    light_obj.data.color = (final_r, final_g, final_b)
    
    max_channel = max(state['r'], state['g'], state['b'])
    total_intensity = max(max_channel, state['w'])
    
    print(f"💡 Simple: {light_name}: RGB({final_r:.2f},{final_g:.2f},{final_b:.2f}) i={total_intensity}")
    return total_intensity

def get_or_create_light(channel):
    """Hakee valon Lights collectionista"""
    print(f"🔍 Simple: Etsitään valo kanavalle {channel}")
    
    # Etsi Lights collection
    lights_collection = None
    for collection in bpy.data.collections:
        if 'Light' in collection.name or 'light' in collection.name.lower():
            lights_collection = collection
            break
    
    if not lights_collection:
        print("❌ Ei Lights collectionia!")
        return None
    
    # Hae valot
    collection_lights = [obj for obj in lights_collection.objects if obj.type == 'LIGHT']
    
    # RGBW-haku
    for light_obj in collection_lights:
        light_name = light_obj.name
        if light_name.startswith('RGBW '):
            match = re.search(r'RGBW (\d+)-(\d+)', light_name)
            if match:
                start_ch = int(match.group(1))
                end_ch = int(match.group(2))
                if start_ch <= channel <= end_ch:
                    print(f"🎯 Simple: RGBW {light_name} sisältää ch{channel}")
                    return light_obj
    
    # Spot-haku
    for light_obj in collection_lights:
        light_name = light_obj.name
        if 'Spot' in light_name:
            numbers = re.findall(r'\d+', light_name)
            for num_str in numbers:
                if int(num_str) == channel:
                    print(f"🎯 Simple: Spot {light_name} = ch{channel}")
                    return light_obj
    
    print(f"❌ Simple: Ei löytynyt valoa ch{channel}")
    return None

def clear_all():
    """Tyhjennä kaikki"""
    global simple_rgbw_channel_states
    simple_rgbw_channel_states = {}
    
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            if obj.animation_data:
                obj.animation_data_clear()
            if obj.data.animation_data:
                obj.data.animation_data_clear()
            obj.data.energy = 1.0
            obj.data.color = (1.0, 1.0, 1.0)
    
    print("🧹 Simple: Kaikki tyhjennetty")

def velocity_to_energy(velocity):
    """Velocity -> energia"""
    if velocity == 0:
        return 1.0
    return 5.0 + (velocity / 127.0) * 295.0

def import_midi_simple(midi_path):
    """Yksinkertainen MIDI-tuonti RGBW-värinsekoituksella"""
    
    if not os.path.exists(midi_path):
        print(f"❌ Ei löydy: {midi_path}")
        return False
    
    print(f"🎵 Simple: Ladataan {midi_path}")
    
    try:
        midi_file = mido.MidiFile(midi_path)
    except Exception as e:
        print(f"❌ MIDI-virhe: {e}")
        return False
    
    clear_all()
    bpy.context.scene.render.fps = 24
    
    processed = 0
    track_time = 0
    
    print(f"🎬 Simple: FPS=24, ticks_per_beat={midi_file.ticks_per_beat}")
    
    for track_num, track in enumerate(midi_file.tracks):
        print(f"📊 Track {track_num}: {len(track)} viestejä")
        track_time = 0
        
        for msg in track:
            track_time += msg.time
            
            if hasattr(msg, 'type') and msg.type == 'note_on':
                channel = msg.note - 69
                
                if channel < 1 or channel > 40:
                    continue
                
                velocity = msg.velocity
                frame = int((track_time / midi_file.ticks_per_beat) * 24 * 0.5)
                
                light_obj = get_or_create_light(channel)
                if not light_obj:
                    continue
                
                # RGBW vai normaali?
                rgbw_intensity = update_rgbw_color(light_obj, channel, velocity)
                if rgbw_intensity is not False:
                    # RGBW-valo
                    energy = velocity_to_energy(rgbw_intensity)
                    light_obj.data.energy = energy
                    light_obj.data.keyframe_insert(data_path="color", frame=frame)
                    light_obj.data.keyframe_insert(data_path="energy", frame=frame)
                else:
                    # Normaali valo
                    energy = velocity_to_energy(velocity)
                    light_obj.data.energy = energy
                    light_obj.data.keyframe_insert(data_path="energy", frame=frame)
                
                processed += 1
                print(f"💡 Simple: Frame {frame}: ch{channel} vel{velocity}")
    
    max_frame = max(1, int(track_time / midi_file.ticks_per_beat * 24 * 0.5))
    bpy.context.scene.frame_end = max_frame
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    
    print(f"✅ Simple: Valmis! {processed} tapahtumaa, {max_frame} framea")
    return True

# Jos ajetaan suoraan Blenderissä
if __name__ == "__main__":
    # Testaa oletuspolulla
    test_midi = "/Users/raulivirtanen/Documents/valot/generated_midi/testikohde_fade_in.mid"
    import_midi_simple(test_midi)