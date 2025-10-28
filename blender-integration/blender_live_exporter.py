"""
🎭 BLENDER → MULTIPLAY LIVE EXPORTER

KÄYTTÖOHJEET:
1. Aseta valot Blenderissä haluamaasi tilaan (energia + värit)
2. Kopioi tämä skripti Blenderin Text Editoriin  
3. Paina Run Script
4. Saat valmiin JSON-tiedoston joka voit siirtää midimaker5.py:lle

RGBW-ryhmäsi:
- RGBW 13-16: kanavat 13, 14, 15, 16  
- RGBW 17-20: kanavat 17, 18, 19, 20
- RGBW 25-28: kanavat 25, 26, 27, 28
- jne...

Yksittäiset valot: nimeä numeroilla (esim. "21" = kanava 21)
"""

import bpy
import json
import os
from mathutils import Vector

# 🎛️ ASETUKSET (muokkaa tarpeen mukaan)
OUTPUT_FILE = "/Users/raulivirtanen/Documents/valot/BlenderLive_Setup.json"
SCENE_NAME = "BlenderLive"
DEFAULT_FADE_IN = 2.0    # Fade-in aika sekunteina
DEFAULT_FADE_OUT = 3.0   # Fade-out aika sekunteina
DEFAULT_STEPS = 20       # MIDI-portaiden määrä
MAX_WATTAGE = 300        # Maksimi energia Blenderissä

# 🌈 RGBW-mappings (sinun Scene Setter -järjestelmäsi)
RGBW_GROUPS = {
    "RGBW 13-16": [13, 14, 15, 16],   # R, G, B, W
    "RGBW 17-20": [17, 18, 19, 20],
    "RGBW 25-28": [25, 26, 27, 28], 
    "RGBW 29-32": [29, 30, 31, 32],
    "RGBW 33-36": [33, 34, 35, 36],
    "RGBW 37-40": [37, 38, 39, 40],
}

def energy_to_velocity(energy, max_energy=MAX_WATTAGE):
    """Muuntaa Blenderin energian MIDI velocity-arvoksi (0-127)"""
    if energy <= 0:
        return 0
    velocity = int((energy / max_energy) * 127)
    return min(127, max(1, velocity))  # Vähintään 1 jos energia > 0

def get_channels_from_name(light_name):
    """Päättelee kanavat valon nimestä"""
    
    # 1. RGBW-ryhmät
    if light_name in RGBW_GROUPS:
        return RGBW_GROUPS[light_name]
    
    # 2. Yksittäiset kanavat numeroina
    try:
        channel = int(light_name.strip())
        if 1 <= channel <= 40:
            return [channel]
    except ValueError:
        pass
    
    # 3. Etsi numeroita nimestä ("Light.021" → 21)
    import re
    numbers = re.findall(r'\d+', light_name)
    if numbers:
        try:
            channel = int(numbers[-1])  # Viimeinen numero
            if 1 <= channel <= 40:
                return [channel]
        except ValueError:
            pass
    
    print(f"⚠️  Ei tunnistettu kanavaa: '{light_name}'")
    return []

def analyze_rgbw_color(color, energy):
    """
    Jakaa RGB-värin + energian → RGBW-kanaviin
    Käyttää heuristiikkaa white-kanavan arvaamiseen
    """
    r, g, b = color[:3]
    
    # Arvaa white-taso (konservatiivinen: pienin RGB-arvo * kerroin)
    white_component = min(r, g, b) * 0.6
    
    # "Puhdas" RGB (vähennetään white)
    pure_r = max(0.0, r - white_component)
    pure_g = max(0.0, g - white_component) 
    pure_b = max(0.0, b - white_component)
    
    # Skaalaa energian mukaan
    energy_factor = min(1.0, energy / MAX_WATTAGE)
    
    return [
        pure_r * energy_factor,       # R-kanava
        pure_g * energy_factor,       # G-kanava
        pure_b * energy_factor,       # B-kanava  
        white_component * energy_factor  # W-kanava
    ]

def scan_blender_lights():
    """Skannaa kaikki Blenderin valot ja palauttaa kanavadatan"""
    
    print("🔍 Skannoidaan Blenderin valoja...")
    
    channels = {}
    processed = 0
    rgbw_count = 0
    single_count = 0
    
    for obj in bpy.data.objects:
        if obj.type != 'LIGHT':
            continue
            
        light_data = obj.data
        energy = light_data.energy
        
        # Ohita sammuneet valot
        if energy <= 0.001:
            continue
            
        light_name = obj.name
        color = list(light_data.color)  # RGB-tupla
        
        # Hae kanavat
        channel_list = get_channels_from_name(light_name)
        if not channel_list:
            continue
            
        if len(channel_list) == 4:
            # 🌈 RGBW-ryhmä
            rgbw_values = analyze_rgbw_color(color, energy)
            
            for i, channel in enumerate(channel_list):
                # Laske MIDI velocity tälle kanavalle
                channel_energy = rgbw_values[i] * MAX_WATTAGE
                velocity = energy_to_velocity(channel_energy)
                
                if velocity > 0:
                    channels[str(channel)] = velocity
            
            print(f"🌈 {light_name}: {energy:.1f}W, RGB{color[:3]} → RGBW {[f'{v:.2f}' for v in rgbw_values]}")
            rgbw_count += 1
            
        elif len(channel_list) == 1:
            # 💡 Yksittäinen kanava
            channel = channel_list[0]
            velocity = energy_to_velocity(energy)
            channels[str(channel)] = velocity
            
            print(f"💡 {light_name}: {energy:.1f}W → kanava {channel} (velocity {velocity})")
            single_count += 1
        
        processed += 1
    
    print(f"📊 Löydettiin {processed} valoa: {rgbw_count} RGBW-ryhmää + {single_count} yksittäistä")
    print(f"🎛️  Päällä olevat kanavat: {sorted([int(k) for k in channels.keys()])}")
    
    return channels

def create_scene_json(channels_data, scene_name=SCENE_NAME):
    """Luo JSON-kohtauksen nykyisistä valoista"""
    
    scene = {
        "name": scene_name,
        "channels": channels_data,
        "fade_in_duration": DEFAULT_FADE_IN,
        "fade_out_duration": DEFAULT_FADE_OUT, 
        "steps": DEFAULT_STEPS
    }
    
    return [scene]  # Palautetaan listana (scenes-array)

def save_json_file(scenes_data, output_path=OUTPUT_FILE):
    """Tallentaa JSON-tiedoston"""
    
    try:
        # Varmista hakemisto
        directory = os.path.dirname(output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Tallenna JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(scenes_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 JSON tallennettu: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Virhe tallennuksessa: {e}")
        return False

def print_multiplay_instructions(json_path):
    """Tulosta ohjeet Multiplay-käyttöön"""
    
    print("\n🎮 MULTIPLAY-OHJEET:")
    print("=" * 40)
    print(f"1. Käy kansiossa: {os.path.dirname(json_path)}")
    print(f"2. Aja: python3 midimaker5.py {os.path.basename(json_path)}")
    print(f"3. Saat kaksi MIDI-tiedostoa:")
    print(f"   - {SCENE_NAME}_fade_in.mid") 
    print(f"   - {SCENE_NAME}_fade_out.mid")
    print(f"4. Siirrä .mid-tiedostot Windows Multiplayhin")
    print(f"5. Yhdistä Scene Setter USB-porttiin")
    print(f"6. Toista MIDI → valot syttyvät! 🌈")

# 🚀 PÄÄOHJELMA
def export_current_setup():
    """Päävie-funktio"""
    
    print("🎭 BLENDER LIVE SETUP EXPORTER")
    print("=" * 50)
    
    # Skannaa nykyiset valot
    channels_data = scan_blender_lights()
    
    if not channels_data:
        print("❌ Ei löytynyt päällä olevia valoja!")
        print("💡 Vinkki: Aseta valojen Energy > 0 Blenderissä")
        return False
    
    # Luo JSON-data
    scenes_data = create_scene_json(channels_data)
    
    # Tallenna
    success = save_json_file(scenes_data)
    
    if success:
        print("\n✅ EXPORT ONNISTUI!")
        print_multiplay_instructions(OUTPUT_FILE)
        return True
    else:
        print("\n❌ Export epäonnistui")
        return False

# 🎬 AJA TÄMÄ
if __name__ == "__main__":
    export_current_setup()