#!/usr/bin/env python3
import json
from collections import OrderedDict

def remove_duplicates(json_file):
    """Poistaa duplikaatti-esitykset JSON-tiedostosta, säilyttäen uusimman version."""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Löydettiin {len(data)} esitystä yhteensä")
    
    # Käytä OrderedDict säilyttämään järjestyksen, mutta poista duplikaatit
    unique_presets = OrderedDict()
    
    for preset in data:
        name = preset['name']
        saved_at = preset.get('saved_at', '')
        
        if name in unique_presets:
            # Vertaa tallennusaikoja ja säilytä uudempi
            current_time = unique_presets[name].get('saved_at', '')
            if saved_at > current_time:
                print(f"Korvataan vanhempi '{name}' uudemmalla versiolla")
                unique_presets[name] = preset
            else:
                print(f"Säilytetään vanhempi '{name}', uudempi hylätään")
        else:
            unique_presets[name] = preset
            print(f"Lisätään uusi esitys: '{name}'")
    
    # Muutetaan takaisin listaksi
    cleaned_data = list(unique_presets.values())
    
    print(f"\nTulos: {len(cleaned_data)} uniikkia esitystä (poistettu {len(data) - len(cleaned_data)} duplikaattia)")
    
    # Luo varmuuskopio
    backup_file = json_file + '.backup'
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Varmuuskopio luotu: {backup_file}")
    
    # Tallenna puhdistettu versio
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    print(f"Puhdistettu tiedosto tallennettu: {json_file}")

if __name__ == "__main__":
    remove_duplicates('/Users/raulivirtanen/Documents/valot/esitykset.json')