"""
🔍 Blender Lights Scanner

Skannaa Blenderin 'Lights' collectionin valot ja näyttää niiden nimet.
Auttaa ymmärtämään nykyisen setup:n ja korjaamaan MIDI-integraation.

Käyttö Blenderissä:
1. Avaa Text Editor
2. Kopioi tämä skripti
3. Aja skripti
4. Katso Console-tulosteet
"""

import bpy

def scan_lights_collection():
    """Skannaa 'Lights' collectionin sisällön"""
    
    print("🔍 BLENDER LIGHTS SCANNER")
    print("=" * 50)
    
    # Etsi 'Lights' collection
    lights_collection = None
    for collection in bpy.data.collections:
        if 'Light' in collection.name or 'light' in collection.name.lower():
            lights_collection = collection
            print(f"📁 Löydettiin collection: '{collection.name}'")
            break
    
    if not lights_collection:
        print("❌ Ei löytynyt 'Lights' collectionia!")
        print("📁 Käytettävissä olevat collectionit:")
        for collection in bpy.data.collections:
            print(f"   - {collection.name}")
        return False
    
    # Skannaa collectionin valot
    print(f"\n💡 Valot collectionissa '{lights_collection.name}':")
    print("-" * 40)
    
    light_count = 0
    for obj in lights_collection.objects:
        if obj.type == 'LIGHT':
            energy = obj.data.energy
            color = obj.data.color
            light_type = obj.data.type
            
            print(f"💡 {obj.name}")
            print(f"   Type: {light_type}")
            print(f"   Energy: {energy:.1f}W")
            print(f"   Color: R{color[0]:.2f} G{color[1]:.2f} B{color[2]:.2f}")
            print(f"   Location: X{obj.location[0]:.1f} Y{obj.location[1]:.1f} Z{obj.location[2]:.1f}")
            print()
            
            light_count += 1
    
    print(f"📊 Yhteensä {light_count} valoa collectionissa")
    
    return True

def analyze_light_names():
    """Analysoi valojen nimien rakennetta"""
    
    print("\n🔤 NIMIEN ANALYYSI")
    print("-" * 30)
    
    all_lights = []
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            all_lights.append(obj.name)
    
    if not all_lights:
        print("❌ Ei löytynyt yhtään valoa!")
        return
    
    print(f"📝 Kaikki valojen nimet ({len(all_lights)} kpl):")
    for i, name in enumerate(sorted(all_lights), 1):
        print(f"   {i:2d}. {name}")
    
    # Etsi kuvioita
    print("\n🔍 Tunnistetut kuviot:")
    
    # RGBW-ryhmät
    rgbw_groups = {}
    for name in all_lights:
        if 'RGBW' in name.upper():
            parts = name.split('_') if '_' in name else name.split(' ')
            if len(parts) >= 2:
                group = '_'.join(parts[:-1])  # Kaikki paitsi viimeinen osa
                if group not in rgbw_groups:
                    rgbw_groups[group] = []
                rgbw_groups[group].append(name)
    
    if rgbw_groups:
        print("🌈 RGBW-ryhmät:")
        for group, lights in rgbw_groups.items():
            print(f"   {group}: {lights}")
    
    # Numeroidut valot
    numbered = []
    import re
    for name in all_lights:
        numbers = re.findall(r'\d+', name)
        if numbers:
            numbered.append((name, numbers[-1]))  # Viimeinen numero
    
    if numbered:
        print("🔢 Numeroidut valot:")
        for name, number in sorted(numbered, key=lambda x: int(x[1])):
            print(f"   {name} → numero {number}")

def suggest_mapping():
    """Ehdottaa kanavamappingia nykyisten valojen perusteella"""
    
    print("\n💡 EHDOTETTU MIDI-MAPPAUS")
    print("-" * 40)
    
    all_lights = []
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            all_lights.append(obj.name)
    
    if not all_lights:
        return
    
    # Älykäs järjestys: yritä tunnistaa kanavien numerot nimistä
    def extract_channel_number(light_name):
        import re
        # Etsi kaikki numerot nimestä
        numbers = re.findall(r'\d+', light_name)
        if numbers:
            # Jos löytyy numeroita, käytä ensimmäistä
            return int(numbers[0])
        # Jos ei numeroita, käytä aakkosjärjestystä
        return 999 + hash(light_name) % 1000
    
    # Järjestä valojen nimet älykkäästi
    smart_sorted = sorted(all_lights, key=extract_channel_number)
    
    print("🎛️  Scene Setter kanavat 1-40 (älykäs järjestys):")
    print()
    
    channel_mapping = {}
    used_channels = set()
    
    # Ensiksi yritä tunnistaa eksplisiittiset kanavat
    for light_name in all_lights:
        import re
        numbers = re.findall(r'\d+', light_name)
        if numbers:
            potential_channel = int(numbers[0])
            if 1 <= potential_channel <= 40 and potential_channel not in used_channels:
                channel_mapping[potential_channel] = light_name
                used_channels.add(potential_channel)
                midi_note = potential_channel + 69
                print(f"   Kanava {potential_channel:2d} (MIDI {midi_note}) ← {light_name} 🎯 (tunnistettu)")
    
    # Sitten täytä loput kanavat järjestyksessä
    next_channel = 1
    for light_name in smart_sorted:
        if light_name not in channel_mapping.values():
            # Etsi seuraava vapaa kanava
            while next_channel in used_channels and next_channel <= 40:
                next_channel += 1
            
            if next_channel <= 40:
                channel_mapping[next_channel] = light_name
                used_channels.add(next_channel)
                midi_note = next_channel + 69
                print(f"   Kanava {next_channel:2d} (MIDI {midi_note}) ← {light_name}")
                next_channel += 1
    
    # Näytä ylimääräiset valot
    unmapped_lights = [name for name in all_lights if name not in channel_mapping.values()]
    if unmapped_lights:
        print(f"\n⚠️  Ylimääräiset valot (yli 40 kanavaa):")
        for light_name in unmapped_lights:
            print(f"   - {light_name}")
    
    return channel_mapping

def generate_mapping_code():
    """Generoi Python-koodia nykyiselle setupille"""
    
    print("\n🐍 GENEROITU MAPPAUS-KOODI")
    print("-" * 40)
    
    all_lights = []
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            all_lights.append(obj.name)
    
    if not all_lights:
        return
    
    # Käytä samaa älykästä järjestystä kuin suggest_mapping()
    def extract_channel_number(light_name):
        import re
        numbers = re.findall(r'\d+', light_name)
        if numbers:
            return int(numbers[0])
        return 999 + hash(light_name) % 1000
    
    smart_sorted = sorted(all_lights, key=extract_channel_number)
    
    # Luo mappaus
    channel_mapping = {}
    used_channels = set()
    
    # Tunnista eksplisiittiset kanavat
    for light_name in all_lights:
        import re
        numbers = re.findall(r'\d+', light_name)
        if numbers:
            potential_channel = int(numbers[0])
            if 1 <= potential_channel <= 40 and potential_channel not in used_channels:
                channel_mapping[potential_channel] = light_name
                used_channels.add(potential_channel)
    
    # Täytä loput
    next_channel = 1
    for light_name in smart_sorted:
        if light_name not in channel_mapping.values():
            while next_channel in used_channels and next_channel <= 40:
                next_channel += 1
            if next_channel <= 40:
                channel_mapping[next_channel] = light_name
                next_channel += 1
    
    print("# Kopioi tämä MIDI-skripteihin:")
    print()
    print("LIGHT_MAPPING = {")
    
    for channel in sorted(channel_mapping.keys()):
        light_name = channel_mapping[channel]
        print(f"    {channel}: '{light_name}',")
    
    print("}")
    print()
    print("# Käyttö get_or_create_light funktiossa:")
    print("def get_light_name_from_channel(channel):")
    print("    return LIGHT_MAPPING.get(channel, f'Unknown_Channel_{channel}')")
    print()
    print("# Käänteinen haku (valo → kanava):")
    print("CHANNEL_FROM_LIGHT = {")
    for channel, light_name in channel_mapping.items():
        print(f"    '{light_name}': {channel},")
    print("}")
    
    return channel_mapping

# Aja skannaus
if __name__ == "__main__":
    success = scan_lights_collection()
    
    if success:
        analyze_light_names()
        suggest_mapping()
        generate_mapping_code()
    
    print("\n✅ Skannaus valmis!")
    print("📋 Kopioi tulosteet ja lähetä ne - korjataan MIDI-integraatio!")