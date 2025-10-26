#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import os
from midiutil import MIDIFile

def create_fade_midi(filename, notes, velocities, duration, is_fade_in, steps=20):
    """
    Luo fade-in tai fade-out MIDI-tiedoston
    """
    mf = MIDIFile(1)
    track = 0
    channel = 0
    time = 0
    mf.addTempo(track, time, 120)  # 120 BPM

    total_beats = duration * 2  # 120 BPM = 2 beats/second
    duration_per_step_beats = total_beats / steps
    
    if is_fade_in:
        # Fade-in: 1 -> target velocity
        for step in range(1, steps + 1):
            factor = step / steps
            for note, target_vel in zip(notes, velocities):
                vel = max(1, int(target_vel * factor))  # Vähintään 1, ei 0
                mf.addNote(track, channel, note, time, duration_per_step_beats, vel)
            time += duration_per_step_beats
        
        # Hold target velocity lyhyesti
        hold_beats = 0.4
        for note, target_vel in zip(notes, velocities):
            mf.addNote(track, channel, note, time, hold_beats, target_vel)
        time += hold_beats
        
        # Note off
        for note in notes:
            mf.addNote(track, channel, note, time, 0.1, 0)
    else:
        # Fade-out: target -> 0
        for step in range(steps + 1):
            factor = 1 - (step / steps)
            for note, target_vel in zip(notes, velocities):
                vel = int(target_vel * factor)
                mf.addNote(track, channel, note, time, duration_per_step_beats, vel)
            time += duration_per_step_beats
        
        # Varmista note off
        for note in notes:
            mf.addNote(track, channel, note, time, 0.1, 0)

    # Kirjoita tiedosto
    with open(filename, "wb") as output_file:
        mf.writeFile(output_file)
    
    return filename  # Palauta alkuperäinen polku sellaisenaan

def main():
    """
    Pääfunktio joka lukee JSON-datan stdin:stä ja luo MIDI-tiedostot
    """
    try:
                # Lue data stdin:stä
        data = json.load(sys.stdin)
        
        # Määritä output-hakemisto
        output_dir = data.get('outputDir', '.')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        results = []
        
        for scene in data['scenes']:
            scene_name = scene['name']
            channels = scene['channels']  # {channel: velocity}
            fade_in_duration = scene['fade_in_duration']
            fade_out_duration = scene['fade_out_duration'] 
            steps = scene.get('steps', 20)
            
            # Muunna kanavat MIDI-nuoteiksi: nuotti = 69 + kanava
            notes = [69 + int(channel) for channel in channels.keys()]
            velocities = list(channels.values())
            
            # Luo tiedostonimet output-hakemistoon
            fade_in_filename = f"{scene_name}_fade_in.mid"
            fade_out_filename = f"{scene_name}_fade_out.mid"
            fade_in_filepath = os.path.join(output_dir, fade_in_filename)
            fade_out_filepath = os.path.join(output_dir, fade_out_filename)
            
            # Luo MIDI-tiedostot
            fade_in_path = create_fade_midi(fade_in_filepath, notes, velocities, 
                                          fade_in_duration, True, steps)
            fade_out_path = create_fade_midi(fade_out_filepath, notes, velocities,
                                           fade_out_duration, False, steps)
            
            results.append({
                'scene': scene_name,
                'fade_in_file': fade_in_filename,
                'fade_out_file': fade_out_filename,
                'fade_in_path': fade_in_path,
                'fade_out_path': fade_out_path,
                'channels_count': len(channels),
                'steps': steps
            })
        
        # Palauta tulokset JSON-muodossa
        print(json.dumps({
            'success': True,
            'results': results
        }, indent=2))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e)
        }), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()