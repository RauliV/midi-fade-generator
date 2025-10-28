"""
🎯 Automatic Channel Mapper for Blender Lights

Skannaa Blenderin valot ja luo automaattisesti channel-mappingin
joka vastaa Scene Setter -laitteistoa.

Käyttö:
1. Nimeä valot numeroilla (1, 2, 3...) tai käytä numeroita nimissä
2. Aja tämä skripti Blenderissä
3. Saat valmiin mappingin jota voit käyttää MIDI-skripteissä

Esimerkkejä valojen nimistä:
- "1" → Kanava 1
- "Light_5" → Kanava 5  
- "RGBW_13_Red" → Kanava 13
- "Spot_27" → Kanava 27
"""

import bpy
import json
import os

def create_channel_mapping():
    """Luo automaattinen channel-mappaus nykyisistä valoista"""
    
    print("🎯 AUTOMATIC CHANNEL MAPPER")
    print("=" * 50)
    
    # Skannaa kaikki valot
    all_lights = []
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            all_lights.append(obj.name)
    
    if not all_lights:
        print("❌ Ei löytynyt valoja!")
        return None
    
    print(f"📊 Löydettiin {len(all_lights)} valoa")
    
    # Älykäs järjestys numerojärjestyksen mukaan
    def extract_channel_number(light_name):
        import re
        numbers = re.findall(r'\d+', light_name)
        if numbers:
            # Käytä ensimmäistä numeroa
            return int(numbers[0])
        # Jos ei numeroita, käytä aakkosjärjestystä
        return 999 + hash(light_name) % 1000
    
    # Luo mappaus
    channel_mapping = {}
    reverse_mapping = {}
    used_channels = set()
    
    print("\n🔍 Tunnistetaan eksplisiittiset kanavat...")
    
    # Ensiksi tunnista selkeät kanavat (numero alussa/nimessä)
    for light_name in all_lights:
        import re
        numbers = re.findall(r'\d+', light_name)
        if numbers:
            potential_channel = int(numbers[0])
            if 1 <= potential_channel <= 40 and potential_channel not in used_channels:
                channel_mapping[potential_channel] = light_name
                reverse_mapping[light_name] = potential_channel
                used_channels.add(potential_channel)
                print(f"  ✅ {light_name} → Kanava {potential_channel}")
    
    print(f"\n📍 Tunnistettiin {len(channel_mapping)} eksplisiittistä kanavaa")
    
    # Järjestä loput valot älykkäästi
    smart_sorted = sorted(all_lights, key=extract_channel_number)
    
    print("\n📋 Täytetään loput kanavat järjestyksessä...")
    
    # Täytä loput kanavat
    next_channel = 1
    for light_name in smart_sorted:
        if light_name not in reverse_mapping:
            # Etsi seuraava vapaa kanava
            while next_channel in used_channels and next_channel <= 40:
                next_channel += 1
            
            if next_channel <= 40:
                channel_mapping[next_channel] = light_name
                reverse_mapping[light_name] = next_channel
                used_channels.add(next_channel)
                print(f"  📍 {light_name} → Kanava {next_channel}")
                next_channel += 1
    
    # Näytä lopputulos
    print(f"\n✅ Mappaus valmis! {len(channel_mapping)} valoa mapped")
    
    # Ylimääräiset valot
    unmapped = [name for name in all_lights if name not in reverse_mapping]
    if unmapped:
        print(f"\n⚠️  {len(unmapped)} valoa ei mahtunut (Scene Setter max 40):")
        for name in unmapped:
            print(f"  - {name}")
    
    return channel_mapping, reverse_mapping

def save_mapping_to_file(channel_mapping, reverse_mapping):
    """Tallentaa mappingin JSON-tiedostoon"""
    
    output_path = "/Users/raulivirtanen/Documents/valot/light_channel_mapping.json"
    
    mapping_data = {
        "description": "Automaattisesti generoitu Blender → Scene Setter channel mappaus",
        "generated_from_blender": True,
        "total_channels": len(channel_mapping),
        "scene_setter_max": 40,
        "channel_to_light": channel_mapping,
        "light_to_channel": reverse_mapping,
        "midi_notes": {
            str(channel): channel + 69 for channel in channel_mapping.keys()
        }
    }
    
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mapping_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Mappaus tallennettu: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Virhe tallennuksessa: {e}")
        return None

def generate_python_code(channel_mapping):
    """Generoi Python-koodia MIDI-skripteihin"""
    
    print("\n🐍 PYTHON-KOODI MIDI-SKRIPTEIHIN:")
    print("=" * 50)
    
    print("# Kopioi tämä midi_to_blender.py:n alkuun:")
    print()
    print("# Automaattisesti generoitu channel mappaus")
    print("BLENDER_LIGHT_MAPPING = {")
    for channel in sorted(channel_mapping.keys()):
        light_name = channel_mapping[channel]
        print(f"    {channel}: '{light_name}',")
    print("}")
    print()
    
    print("# Päivitetty get_or_create_light funktio:")
    print("def get_or_create_light(channel, props):")
    print("    # Käytä mappingia jos löytyy")
    print("    if channel in BLENDER_LIGHT_MAPPING:")
    print("        light_name = BLENDER_LIGHT_MAPPING[channel]")
    print("        ")
    print("        # Etsi olemassa oleva valo")
    print("        for obj in bpy.data.objects:")
    print("            if obj.name == light_name and obj.type == 'LIGHT':")
    print("                return obj")
    print("        ")
    print("        # Jos ei löydy, luo uusi samalla nimellä")
    print("        x = (channel % 8) * 2")
    print("        y = (channel // 8) * 2") 
    print("        location = (x, y, 3)")
    print("        ")
    print("        bpy.ops.object.light_add(type='SPOT', location=location)")
    print("        light_obj = bpy.context.object")
    print("        light_obj.name = light_name")
    print("        light_obj.data.name = f'{light_name}_Data'")
    print("        light_obj.data.energy = 10.0")
    print("        return light_obj")
    print("    ")
    print("    # Fallback alkuperäiseen logiikkaan...")
    print("    # (alkuperäinen RGBW/single light logiikka)")
    print()

def test_mapping(channel_mapping):
    """Testaa mappingin toimivuutta"""
    
    print("\n🧪 MAPPAUKSEN TESTAUS:")
    print("=" * 30)
    
    test_channels = [1, 5, 10, 15, 20, 25, 30, 35, 40]
    
    for channel in test_channels:
        if channel in channel_mapping:
            light_name = channel_mapping[channel]
            midi_note = channel + 69
            
            # Tarkista että valo löytyy Blenderistä
            obj = bpy.data.objects.get(light_name)
            if obj and obj.type == 'LIGHT':
                energy = obj.data.energy
                print(f"✅ Kanava {channel:2d} (MIDI {midi_note}) → {light_name} ({energy:.1f}W)")
            else:
                print(f"⚠️  Kanava {channel:2d} (MIDI {midi_note}) → {light_name} (EI LÖYDY)")
        else:
            print(f"❌ Kanava {channel:2d} - ei mappingia")

# Aja mappaus
if __name__ == "__main__":
    mapping_result = create_channel_mapping()
    
    if mapping_result:
        channel_mapping, reverse_mapping = mapping_result
        
        # Tallenna tiedostoon
        save_mapping_to_file(channel_mapping, reverse_mapping)
        
        # Generoi Python-koodi
        generate_python_code(channel_mapping)
        
        # Testaa mappingia
        test_mapping(channel_mapping)
        
        print("\n🎉 MAPPAUS VALMIS!")
        print("📋 Kopioi Python-koodi MIDI-skripteihin")
        print("💾 JSON-mappaus tallennettu tiedostoon")
        print("🧪 Testaus suoritettu")
    else:
        print("\n❌ Mappauksen luonti epäonnistui")
    
    print("\n" + "="*50)