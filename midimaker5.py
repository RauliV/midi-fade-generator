

from midiutil import MIDIFile

# Loputon loopi kohtausten kyselylle
while True:
    scene_name = input("Syötä kohtauksen nimi (tai 'exit' lopettaaksesi, tai tiedostonimi.txt/.rtf): ").strip()
    
    if scene_name.lower() == 'exit':
        print("Ohjelma lopetettu.")
        break
    
    is_file = scene_name.endswith('.txt') or scene_name.endswith('.rtf')
    if is_file:
        try:
            with open(scene_name, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            print(f"Lukemassa tiedostoa {scene_name}...")
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):  # Ohita tyhjät rivit ja kommentit
                    continue
                parts = line.split(';')
                if len(parts) < 2:
                    print(f"Rivi {line_num}: Virheellinen muoto. Ohitetaan.")
                    continue
                parsed_scene_name = parts[0].strip()
                channels_str = parts[1].strip() if len(parts) > 1 else ''
                fade_in_input = parts[2].strip() if len(parts) > 2 else ''
                fade_out_input = parts[3].strip() if len(parts) > 3 else ''
                
                # Parsitaan kanavat ja arvot
                channels_dict = {}
                pairs = channels_str.split(',')
                for pair in pairs:
                    pair = pair.strip()
                    if ':' in pair:
                        channel, value = pair.split(':')
                        channels_dict[int(channel.strip())] = int(value.strip())
                    else:
                        channels_dict[int(pair)] = 127  # Oletus 127 jos arvo puuttuu
                
                fade_in_duration = float(fade_in_input) if fade_in_input else 1.0
                fade_out_duration = float(fade_out_input) if fade_out_input else 1.0
                
                # Laske MIDI-nuotit: nuotti = 70 + (kanava - 1) = 69 + kanava
                notes = [69 + channel for channel in channels_dict.keys()]
                velocities = list(channels_dict.values())
                
   
                def create_fade_mid(file_name, notes, velocities, duration, fade_in=True):
                    mf = MIDIFile(1)
                    track = 0
                    channel = 0
                    time = 0
                    mf.addTempo(track, time, 120)  # Tempo 120 BPM (0.5 s/beat) tarkempaan kontrolliin

                    steps = 20  # Vähemmän steppejä, pidempi kesto/step (esim. 1 s = 50 ms/step)
                    total_beats = duration * 2  # Säädä beat:eja keston mukaan (120 BPM = 2 beats/s)
                    duration_per_step = total_beats / steps

                    print(f"Fade { 'in' if fade_in else 'out' }: {steps} steppiä, {duration_per_step} beats/step ({duration_per_step * 0.5} s/step)")

                    if fade_in:
                        # Aloita velocity 1:stä (ei 0), range(1, steps + 1)
                        for step in range(1, steps + 1):
                            for note, target_vel in zip(notes, velocities):
                                vel = int(target_vel * (step / steps))  # 1 -> target
                                mf.addNote(track, channel, note, time, duration_per_step, vel)
                                print(f"Step {step}: vel={vel} for note {note}")
                            time += duration_per_step
                        # Loppuun hold target-velocityllä (0.2 s)
                        hold_beats = 0.4  # 0.2 s @ 120 BPM
                        for note, target_vel in zip(notes, velocities):
                            mf.addNote(track, channel, note, time, hold_beats, target_vel)
                        time += hold_beats
                    else:
                        # Fade_out: target -> 0
                        for step in range(steps + 1):
                            for note, target_vel in zip(notes, velocities):
                                vel = int(target_vel * (1 - (step / steps)))  # target -> 0
                                mf.addNote(track, channel, note, time, duration_per_step, vel)
                                print(f"Step {step}: vel={vel} for note {note}")
                            time += duration_per_step
                        # Loppuun Note Off jokaiselle (velocity 0)
                        for note in notes:
                            mf.addNote(track, channel, note, time, 0.1, 0)

                    with open(file_name, "wb") as output_file:
                        mf.writeFile(output_file)
                    print(f"{file_name} luotu onnistuneesti!")

                # Luo tiedostot
                fade_in_file = f"{parsed_scene_name}_fade_in.mid"
                fade_out_file = f"{parsed_scene_name}_fade_out.mid"
 
                create_fade_mid(fade_in_file, notes, velocities, fade_in_duration, fade_in=True)
                create_fade_mid(fade_out_file, notes, velocities, fade_out_duration, fade_in=False)
                print(f"Kohtaus '{parsed_scene_name}' käsitelty.")
        except FileNotFoundError:
            print(f"Tiedostoa '{scene_name}' ei löytynyt. Ohitetaan.")
            continue
        except Exception as e:
            print(f"Virhe tiedoston lukemisessa: {e}. Ohitetaan.")
            continue
        continue  # Jatka looppia seuraavalle syötteelle
    else:
        channels_str = input("Syötä kanavat ja arvot (esim. '1:127, 2:64' tai '1, 2:64' jossa puuttuva arvo = 127): ")
        fade_in_input = input("Syötä fade-in kesto sekunneissa (enter = 1 s): ").strip()
        fade_out_input = input("Syötä fade-out kesto sekunneissa (enter = 1 s): ").strip()

        # Parsitaan kanavat ja arvot
        channels_dict = {}
        pairs = channels_str.split(',')
        for pair in pairs:
            pair = pair.strip()
            if ':' in pair:
                channel, value = pair.split(':')
                channels_dict[int(channel.strip())] = int(value.strip())
            else:
                channels_dict[int(pair)] = 127  # Oletus 127 jos arvo puuttuu
        
        fade_in_duration = float(fade_in_input) if fade_in_input else 1.0
        fade_out_duration = float(fade_out_input) if fade_out_input else 1.0
        
        # Laske MIDI-nuotit: nuotti = 70 + (kanava - 1) = 69 + kanava
        notes = [69 + channel for channel in channels_dict.keys()]
        velocities = list(channels_dict.values())
   
       
        def create_fade_mid(file_name, notes, velocities, duration, fade_in=True):
            mf = MIDIFile(1)
            track = 0
            channel = 0
            time = 0
            mf.addTempo(track, time, 120)  # Tempo 120 BPM (0.5 s/beat) tarkempaan kontrolliin

            steps = 20  # Vähemmän steppejä, pidempi kesto/step (esim. 1 s = 50 ms/step)
            total_beats = duration * 2  # Säädä beat:eja keston mukaan (120 BPM = 2 beats/s)
            duration_per_step = total_beats / steps

            print(f"Fade { 'in' if fade_in else 'out' }: {steps} steppiä, {duration_per_step} beats/step ({duration_per_step * 0.5} s/step)")

            if fade_in:
                # Aloita velocity 1:stä (ei 0), range(1, steps + 1)
                for step in range(1, steps + 1):
                    for note, target_vel in zip(notes, velocities):
                        vel = int(target_vel * (step / steps))  # 1 -> target
                        mf.addNote(track, channel, note, time, duration_per_step, vel)
                        print(f"Step {step}: vel={vel} for note {note}")
                    time += duration_per_step
                # Loppuun hold target-velocityllä (0.2 s)
                hold_beats = 0.4  # 0.2 s @ 120 BPM
                for note, target_vel in zip(notes, velocities):
                    mf.addNote(track, channel, note, time, hold_beats, target_vel)
                time += hold_beats
            else:
                # Fade_out: target -> 0
                for step in range(steps + 1):
                    for note, target_vel in zip(notes, velocities):
                        vel = int(target_vel * (1 - (step / steps)))  # target -> 0
                        mf.addNote(track, channel, note, time, duration_per_step, vel)
                        print(f"Step {step}: vel={vel} for note {note}")
                    time += duration_per_step
                # Loppuun Note Off jokaiselle (velocity 0)
                for note in notes:
                    mf.addNote(track, channel, note, time, 0.1, 0)

            with open(file_name, "wb") as output_file:
                mf.writeFile(output_file)
            print(f"{file_name} luotu onnistuneesti!")

    # Luo tiedostot
        fade_in_file = f"{scene_name}_fade_in.mid"
        fade_out_file = f"{scene_name}_fade_out.mid"
        
        create_fade_mid(fade_in_file, notes, velocities, fade_in_duration, fade_in=True)
        create_fade_mid(fade_out_file, notes, velocities, fade_out_duration, fade_in=False)