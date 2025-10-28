#!/usr/bin/env python3
"""
Automatisoi koko JSON → MIDI → Blender workflow
Ei vaadi Blenderiä - käyttää MIDI-generaattorin Python-backendia suoraan.

Käyttö:
python3 workflow_automation.py example_scenes.json
"""

import json
import sys
import os
import subprocess
from pathlib import Path

# Lisää MIDI-generaattorin backend polkuun
SCRIPT_DIR = Path(__file__).parent
BACKEND_PATH = SCRIPT_DIR.parent / "valot_python_backend.py"
OUTPUT_DIR = SCRIPT_DIR / "generated_midi"

def generate_midi_from_json(json_file, output_dir=None):
    """Luo MIDI-tiedostot JSON-kohtauksista"""
    
    if output_dir is None:
        output_dir = OUTPUT_DIR
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    if not BACKEND_PATH.exists():
        print(f"❌ Python-backend ei löydy: {BACKEND_PATH}")
        return False
    
    print(f"🎵 Luodaan MIDI-tiedostoja: {json_file}")
    print(f"📁 Output: {output_dir}")
    
    # Lue JSON-kohtaukset
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            scenes = json.load(f)
    except Exception as e:
        print(f"❌ Virhe JSON-tiedoston lukemisessa: {e}")
        return False
    
    # Luo data Python-backendille
    backend_data = {
        "scenes": scenes,
        "outputDir": str(output_dir.absolute())
    }
    
    # Aja Python-backend
    try:
        process = subprocess.run(
            [sys.executable, str(BACKEND_PATH)],
            input=json.dumps(backend_data),
            text=True,
            capture_output=True
        )
        
        if process.returncode == 0:
            result = json.loads(process.stdout)
            if result.get('success'):
                print("✅ MIDI-tiedostot luotu onnistuneesti!")
                print(f"📊 Kohtauksia: {len(result['results'])}")
                
                for scene_result in result['results']:
                    scene_name = scene_result['scene']
                    fade_in = scene_result['fade_in_file']
                    fade_out = scene_result['fade_out_file']
                    print(f"  🎭 {scene_name}: {fade_in}, {fade_out}")
                
                return True
            else:
                print(f"❌ Backend virhe: {result.get('error', 'Tuntematon virhe')}")
        else:
            print(f"❌ Prosessi epäonnistui: {process.stderr}")
            
    except Exception as e:
        print(f"❌ Virhe backend-prosessissa: {e}")
    
    return False

def list_generated_files(output_dir=None):
    """Listaa luodut MIDI-tiedostot"""
    
    if output_dir is None:
        output_dir = OUTPUT_DIR
    
    output_dir = Path(output_dir)
    
    if not output_dir.exists():
        print(f"📁 Output-hakemistoa ei ole: {output_dir}")
        return
    
    midi_files = list(output_dir.glob("*.mid"))
    
    if not midi_files:
        print("📁 Ei MIDI-tiedostoja löytynyt")
        return
    
    print(f"\n🎵 Luodut MIDI-tiedostot ({len(midi_files)} kpl):")
    
    # Ryhmittele fade-in/out parit
    scenes = {}
    for midi_file in midi_files:
        name = midi_file.stem
        if name.endswith('_fade_in'):
            scene_name = name[:-8]  # Poista '_fade_in'
            if scene_name not in scenes:
                scenes[scene_name] = {}
            scenes[scene_name]['fade_in'] = midi_file
        elif name.endswith('_fade_out'):
            scene_name = name[:-9]  # Poista '_fade_out'
            if scene_name not in scenes:
                scenes[scene_name] = {}
            scenes[scene_name]['fade_out'] = midi_file
    
    for scene_name, files in scenes.items():
        print(f"\n  🎭 {scene_name}:")
        if 'fade_in' in files:
            print(f"    📈 {files['fade_in'].name}")
        if 'fade_out' in files:
            print(f"    📉 {files['fade_out'].name}")

def show_blender_instructions(output_dir=None):
    """Näytä ohjeet Blender-käyttöön"""
    
    if output_dir is None:
        output_dir = OUTPUT_DIR
    
    print(f"\n🎬 Blender-ohjeet:")
    print(f"1. Avaa Blender")
    print(f"2. Text Editor → Open → {SCRIPT_DIR}/midi_to_blender.py")
    print(f"3. Muokkaa MIDI_FILE_PATH:")
    print(f"   MIDI_FILE_PATH = \"{output_dir}/[tiedostonimi].mid\"")
    print(f"4. Run Script")
    print(f"5. ▶️  Play animation!")
    print(f"\n💡 Vinkki: Kokeile ensin fade_in-tiedostoja")

def main():
    """Pääohjelma"""
    
    if len(sys.argv) != 2:
        print("Käyttö: python3 workflow_automation.py <json_file>")
        print("Esim: python3 workflow_automation.py example_scenes.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    if not os.path.exists(json_file):
        print(f"❌ JSON-tiedostoa ei löydy: {json_file}")
        sys.exit(1)
    
    print("🚀 MIDI-Blender Workflow Automation")
    print("=" * 40)
    
    # Luo MIDI-tiedostot
    success = generate_midi_from_json(json_file)
    
    if success:
        # Listaa tulokset
        list_generated_files()
        
        # Näytä Blender-ohjeet
        show_blender_instructions()
        
        print(f"\n🎉 Workflow valmis!")
        print(f"📂 MIDI-tiedostot: {OUTPUT_DIR}")
        print(f"🎬 Blender-skriptit: {SCRIPT_DIR}")
    else:
        print(f"\n💥 Workflow epäonnistui!")
        sys.exit(1)

if __name__ == "__main__":
    main()