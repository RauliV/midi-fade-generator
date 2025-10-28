#!/usr/bin/env python3
"""
🔄 Reverse RGBW Color Mapping
Blender RGB(r,g,b) → MIDI RGBW kanavat

Testaa toimiiko värinpurku oikein:
Blender violetti RGB(1.0, 0.0, 1.0) → R=127, G=0, B=127, W=0
"""

import re

def decompose_rgbw_color(rgb_color, intensity=1.0):
    """
    Purkaa RGB-värin takaisin RGBW-komponentteihin
    
    Args:
        rgb_color: (r, g, b) tuple, arvot 0.0-1.0
        intensity: kokonaisteho 0.0-1.0
    
    Returns:
        dict: {'r': 0-127, 'g': 0-127, 'b': 0-127, 'w': 0-127}
    """
    r, g, b = rgb_color
    
    # Laske valkoisen komponentti (pienin RGB-arvo)
    white_component = min(r, g, b)
    
    # Poista valkoinen puhtaista väreistä
    pure_r = max(0.0, r - white_component)
    pure_g = max(0.0, g - white_component)
    pure_b = max(0.0, b - white_component)
    
    # Skaalaa intensiteetillä ja muunna MIDI-arvoiksi (0-127)
    r_midi = int(pure_r * intensity * 127)
    g_midi = int(pure_g * intensity * 127)
    b_midi = int(pure_b * intensity * 127)
    w_midi = int(white_component * intensity * 127)
    
    return {
        'r': min(127, max(0, r_midi)),
        'g': min(127, max(0, g_midi)),
        'b': min(127, max(0, b_midi)),
        'w': min(127, max(0, w_midi))
    }

def get_rgbw_channels_from_name(light_name):
    """Palauttaa RGBW-valon kanavanumerot"""
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

def export_rgbw_light_to_channels(light_name, rgb_color, energy):
    """
    Vie RGBW-valon Blenderistä MIDI-kanaviin
    
    Args:
        light_name: esim. "RGBW 33-36"
        rgb_color: (r, g, b) tuple
        energy: valon energia (0-300W tyypillisesti)
    
    Returns:
        dict: {channel_num: velocity, ...}
    """
    # Tarkista onko RGBW-valo
    channels = get_rgbw_channels_from_name(light_name)
    if not channels:
        return None
    
    # Laske intensiteetti energiasta
    max_energy = 300.0  # Scene Setter maksimi
    intensity = min(1.0, energy / max_energy)
    
    # Pura väri RGBW-komponentteihin
    rgbw = decompose_rgbw_color(rgb_color, intensity)
    
    # Luo kanava-velocity mapping
    result = {}
    if rgbw['r'] > 0:
        result[channels['r']] = rgbw['r']
    if rgbw['g'] > 0:
        result[channels['g']] = rgbw['g']
    if rgbw['b'] > 0:
        result[channels['b']] = rgbw['b'] 
    if rgbw['w'] > 0:
        result[channels['w']] = rgbw['w']
    
    print(f"🔄 {light_name}: RGB{rgb_color} @ {energy}W")
    print(f"   → Kanavat: {result}")
    print(f"   → RGBW: R={rgbw['r']} G={rgbw['g']} B={rgbw['b']} W={rgbw['w']}")
    
    return result

def test_reverse_mapping():
    """Testaa käänteistä RGBW-mappingia"""
    print("🔄 Reverse RGBW Mapping Test")
    print("=" * 40)
    
    test_cases = [
        # (nimi, RGB-väri, energia, odotus)
        ("RGBW 33-36", (1.0, 0.0, 0.0), 150, "Puhdas punainen"),
        ("RGBW 33-36", (0.0, 1.0, 0.0), 150, "Puhdas vihreä"),
        ("RGBW 33-36", (0.0, 0.0, 1.0), 150, "Puhdas sininen"),
        ("RGBW 33-36", (1.0, 1.0, 1.0), 150, "Valkoinen (kaikki)"),
        ("RGBW 33-36", (1.0, 0.0, 1.0), 150, "Violetti (R+B)"),
        ("RGBW 33-36", (0.5, 0.5, 1.0), 150, "Vaaleansininen"),
        ("RGBW 33-36", (0.8, 0.8, 0.8), 150, "Harmaa (valkoinen dim)"),
    ]
    
    for light_name, rgb_color, energy, description in test_cases:
        print(f"\n📍 {description}")
        result = export_rgbw_light_to_channels(light_name, rgb_color, energy)
        
        # Tarkista toimiiko käänteinen operaatio
        if result:
            # Simuloi tuontia takaisin
            print(f"   💡 Tuonnissa näkyisi: ", end="")
            for ch, vel in result.items():
                channel_color = {33: 'R', 34: 'G', 35: 'B', 36: 'W'}
                print(f"{channel_color.get(ch, ch)}={vel} ", end="")
            print()

if __name__ == "__main__":
    test_reverse_mapping()