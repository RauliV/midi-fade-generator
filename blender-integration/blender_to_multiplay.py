"""
Blender Live Setup → MIDI Exporter

Tallentaa Blenderin nykyisen valosetuppin suoraan MIDI-tiedostoiksi
jotka voi siirtää Multiplay Windows-ohjelmaan Scene Setter -ohjausta varten.

Käyttö:
1. Aseta valot Blenderissä haluamaasi tilaan
2. Aja tämä skripti
3. Saat valmiin MIDI-tiedoston Multiplayhin!
"""

import bpy
import json
import os
import sys
import subprocess
from pathlib import Path

# ASETUKSET
OUTPUT_DIR = "/Users/raulivirtanen/Documents/MIDI-Export"
SCENE_NAME = "BlenderLive"
DEFAULT_FADE_IN = 2.0
DEFAULT_FADE_OUT = 3.0
DEFAULT_STEPS = 20
MAX_WATTAGE = 300

# RGBW-mappings (sinun järjestelmäsi)
rgbw_map = {
    range(82, 86): "RGBW 13-16",
    range(86, 90): "RGBW 17-20", 
    range(94, 98): "RGBW 25-28",
    range(98, 102): "RGBW 29-32",
    range(102, 106): "RGBW 33-36",
    range(106, 110): "RGBW 37-40",
}

# Käänteinen mapping: nimi → kanavat
name_to_channels = {}
for note_range, group_name in rgbw_map.items():
    channels = [note - 69 for note in note_range]  # Muunna MIDI-nuoteista kanaviksi
    name_to_channels[group_name] = channels

def energy_to_velocity(energy):
    """Muuntaa Blenderin energian (W) MIDI velocity-arvoksi (0-127)"""
    if energy <= 0:
        return 0
    velocity = int((energy / MAX_WATTAGE) * 127)
    return min(127, max(0, velocity))

def get_channel_from_light_name(light_name):
    """Päättelee kanavan numeron valon nimestä"""
    
    # RGBW-ryhmät: "RGBW 13-16" → kanavat 13, 14, 15, 16
    if light_name in name_to_channels:
        return name_to_channels[light_name]  # Palauttaa listan kanavia
    
    # Yksittäiset kanavat: "21" → kanava 21
    try:
        channel = int(light_name)
        if 1 <= channel <= 40:
            return [channel]  # Palauttaa listan yhden kanavan kanssa
    except ValueError:
        pass
    
    print(f"⚠️  Ei voitu päätellä kanavaa valolle: {light_name}")
    return []

def analyze_rgbw_color(color, energy):
    """
    Analysoi RGBW-valon väri ja energia → jakaa R, G, B, W kanaviin
    Tämä on heuristiikka joka yrittää päätellä alkuperäiset RGBW-arvot
    """
    r, g, b = color[:3]  # RGB-komponentit
    
    # Arvaa white-komponentti (minimi kaikista väreistä)
    white_level = min(r, g, b) * 0.7  # Konservatiivinen arvaus
    
    # Vähennä white muista väreistä
    pure_r = max(0, r - white_level)
    pure_g = max(0, g - white_level)
    pure_b = max(0, b - white_level)
    
    # Skaalaa energian mukaan
    energy_factor = energy / MAX_WATTAGE
    
    return [
        pure_r * energy_factor,      # R-kanava
        pure_g * energy_factor,      # G-kanava  
        pure_b * energy_factor,      # B-kanava
        white_level * energy_factor  # W-kanava
    ]

def scan_current_blender_setup():
    """Skannaa Blenderin nykyiset valoasetukset"""
    
    print("🔍 Skannoidaan Blenderin nykyinen valosetup...")
    
    channels_data = {}
    processed_lights = 0
    rgbw_groups = 0
    
    for obj in bpy.data.objects:
        if obj.type != 'LIGHT' or obj.data.energy <= 0:
            continue  # Ohita sammuneet valot
        
        light_name = obj.name
        energy = obj.data.energy
        color = list(obj.data.color)
        
        # Hae kanavat tämän valon nimestä
        channels = get_channel_from_light_name(light_name)
        
        if not channels:
            continue
        
        if len(channels) == 4:
            # RGBW-ryhmä
            rgbw_values = analyze_rgbw_color(color, energy)
            
            for i, channel in enumerate(channels):
                velocity = energy_to_velocity(rgbw_values[i] * MAX_WATTAGE)
                if velocity > 0:
                    channels_data[str(channel)] = velocity
            
            rgbw_groups += 1
            print(f"🌈 {light_name}: {energy:.1f}W, väri{color} → RGBW({rgbw_values[0]:.2f},{rgbw_values[1]:.2f},{rgbw_values[2]:.2f},{rgbw_values[3]:.2f})")
            
        elif len(channels) == 1:
            # Yksittäinen kanava
            channel = channels[0]
            velocity = energy_to_velocity(energy)
            channels_data[str(channel)] = velocity
            
            print(f"💡 {light_name}: {energy:.1f}W → kanava {channel} = velocity {velocity}")
        
        processed_lights += 1
    
    print(f"📊 Skannattu {processed_lights} valoa ({rgbw_groups} RGBW-ryhmää)")
    return channels_data

def create_json_scene(channels_data, scene_name=None):
    """Luo JSON-kohtauksen nykyisistä asetuksista"""
    
    if scene_name is None:
        scene_name = SCENE_NAME
    
    scene_data = {
        "name": scene_name,
        "channels": channels_data,
        "fade_in_duration": DEFAULT_FADE_IN,
        "fade_out_duration": DEFAULT_FADE_OUT,
        "steps": DEFAULT_STEPS
    }
    
    return [scene_data]  # Palautetaan listana (scenes-array)

def save_json_and_generate_midi(scenes_data, output_dir):
    """Tallentaa JSON:n ja generoi MIDI-tiedostot"""
    
    # Varmista output-hakemisto
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Tallenna JSON
    json_file = output_path / f"{SCENE_NAME}.json"
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(scenes_data, f, indent=2, ensure_ascii=False)
        print(f"💾 JSON tallennettu: {json_file}")
    except Exception as e:
        print(f"❌ Virhe JSON-tallennuksessa: {e}")
        return False
    
    # Etsi Python-backend
    script_dir = Path(__file__).parent
    backend_candidates = [
        script_dir.parent / "valot_python_backend.py",
        script_dir.parent / "midi-fade-generator-electron" / "valot_python_backend.py",
        script_dir.parent / "midi-fade-generator" / "valot_python_backend.py"
    ]
    
    backend_path = None
    for candidate in backend_candidates:
        if candidate.exists():
            backend_path = candidate
            break
    
    if not backend_path:
        print("❌ Python-backend ei löytynyt. JSON tallennettu, mutta MIDI:ä ei voitu luoda.")
        print(f"📁 JSON-tiedosto: {json_file}")
        return True
    
    print(f"🐍 Käytetään backend: {backend_path}")
    
    # Luo data backendille
    backend_data = {
        "scenes": scenes_data,
        "outputDir": str(output_path.absolute())
    }
    
    # Aja Python-backend
    try:
        print("🎵 Luodaan MIDI-tiedostoja...")
        
        process = subprocess.run(
            [sys.executable, str(backend_path)],
            input=json.dumps(backend_data),
            text=True,
            capture_output=True,
            cwd=str(backend_path.parent)
        )
        
        if process.returncode == 0:
            result = json.loads(process.stdout)
            if result.get('success'):
                print("✅ MIDI-tiedostot luotu onnistuneesti!")
                
                for scene_result in result['results']:
                    fade_in = scene_result['fade_in_file']
                    fade_out = scene_result['fade_out_file']
                    print(f"  🎵 {fade_in}")
                    print(f"  🎵 {fade_out}")
                
                return True
            else:
                print(f"❌ Backend-virhe: {result.get('error', 'Tuntematon virhe')}")
        else:
            print(f"❌ Backend epäonnistui:")
            print(f"STDERR: {process.stderr}")
            
    except Exception as e:
        print(f"❌ Virhe MIDI-generoinnissa: {e}")
    
    return False

def export_blender_setup_to_multiplay():
    """Pääfunktio: vie Blender-setup Multiplay-valmiiksi"""
    
    print("🎭 BLENDER → MULTIPLAY EXPORTER")
    print("=" * 50)
    
    # Skannaa nykyiset valot
    channels_data = scan_current_blender_setup()
    
    if not channels_data:
        print("❌ Ei löytynyt päällä olevia valoja!")
        print("💡 Vinkki: Aseta valojen energy > 0 Blenderissä")
        return False
    
    print(f"📊 Löydettiin {len(channels_data)} kanavaa päällä")
    print(f"🎛️  Kanavat: {', '.join(sorted(channels_data.keys(), key=int))}")
    
    # Luo JSON-kohtaus
    scenes_data = create_json_scene(channels_data)
    
    # Tallenna ja generoi MIDI
    success = save_json_and_generate_midi(scenes_data, OUTPUT_DIR)
    
    if success:
        print("\n🎉 EXPORT VALMIS!")
        print(f"📁 Tiedostot: {OUTPUT_DIR}")
        print("🎮 Multiplay-ohjeet:")
        print(f"  1. Kopioi {OUTPUT_DIR}/{SCENE_NAME}_fade_in.mid Windowsiin")
        print(f"  2. Lataa se Multiplayhin")
        print(f"  3. Yhdistä Scene Setter")
        print(f"  4. Toista MIDI-tiedosto → valot syttyvät! 🌈")
        return True
    else:
        print("\n💥 Export epäonnistui osittain")
        return False

def quick_preview_channels():
    """Näytä mitä kanavia on päällä (esikatseluun)"""
    print("👀 PIKAKATSAUS - Päällä olevat kanavat:")
    
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and obj.data.energy > 0:
            channels = get_channel_from_light_name(obj.name)
            energy = obj.data.energy
            
            if channels:
                ch_str = ', '.join(map(str, channels))
                print(f"  💡 {obj.name}: {energy:.1f}W → kanavat {ch_str}")

# 🚀 KÄYTTÖ
if __name__ == "__main__":
    # Esikatselun
    quick_preview_channels()
    print()
    
    # Vie Multiplayhin
    success = export_blender_setup_to_multiplay()
    
    if success:
        print("\n✨ Nyt voit siirtää MIDI-tiedoston Multiplayhin ja nauttia valoshow'sta!")
    else:
        print("\n🔧 Tarkista asetukset ja yritä uudelleen")