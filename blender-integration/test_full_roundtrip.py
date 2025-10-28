#!/usr/bin/env python3
"""
🔄 Full Round-trip RGBW Test
Testaa että MIDI → Blender → MIDI kierto toimii oikein

1. MIDI kanavat → Blender RGB väri
2. Blender RGB väri → MIDI kanavat
3. Vertaa että sama mitä alkuun meni
"""

import re

# MIDI → Blender (sama logiikka kuin tuonnissa)
def channels_to_rgb(rgbw_channels):
    """Muuntaa RGBW-kanavat RGB-väriksi (import-logiikka)"""
    r_intensity = rgbw_channels.get('r', 0) / 127.0
    g_intensity = rgbw_channels.get('g', 0) / 127.0  
    b_intensity = rgbw_channels.get('b', 0) / 127.0
    w_intensity = rgbw_channels.get('w', 0) / 127.0
    
    # Valkoinen kanava lisää kaikkia värejä
    final_r = min(1.0, r_intensity + w_intensity * 0.8)
    final_g = min(1.0, g_intensity + w_intensity * 0.8) 
    final_b = min(1.0, b_intensity + w_intensity * 0.8)
    
    return (final_r, final_g, final_b)

# Blender → MIDI (sama logiikka kuin viennissä)
def rgb_to_channels(rgb_color, intensity=1.0):
    """Muuntaa RGB-värin RGBW-kanaviksi (export-logiikka)"""
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

def test_round_trip():
    """Testaa täysi MIDI → Blender → MIDI kierros"""
    print("🔄 Full Round-trip RGBW Test")
    print("=" * 50)
    
    test_cases = [
        # Alkuperäiset MIDI-kanavat (sinun ongelmatapaus)
        {'r': 0, 'g': 0, 'b': 90, 'w': 0},      # Puhdas sininen
        {'r': 0, 'g': 0, 'b': 90, 'w': 40},     # Sininen + valkoinen
        {'r': 127, 'g': 0, 'b': 127, 'w': 0},   # Violetti
        {'r': 127, 'g': 127, 'b': 127, 'w': 0}, # RGB valkoinen
        {'r': 0, 'g': 0, 'b': 0, 'w': 80},      # Puhdas valkoinen
        {'r': 64, 'g': 127, 'b': 32, 'w': 16},  # Sekaväri
    ]
    
    for i, original_channels in enumerate(test_cases, 1):
        print(f"\n📍 TESTI {i}: {original_channels}")
        
        # Vaihe 1: MIDI → Blender (import)
        blender_rgb = channels_to_rgb(original_channels)
        print(f"   MIDI → Blender: RGB({blender_rgb[0]:.3f}, {blender_rgb[1]:.3f}, {blender_rgb[2]:.3f})")
        
        # Vaihe 2: Blender → MIDI (export)
        exported_channels = rgb_to_channels(blender_rgb, intensity=1.0)
        print(f"   Blender → MIDI: {exported_channels}")
        
        # Vaihe 3: Vertailu
        print("   📊 Vertailu:")
        all_good = True
        for channel in ['r', 'g', 'b', 'w']:
            orig = original_channels[channel]
            exported = exported_channels[channel]
            diff = abs(orig - exported)
            status = "✅" if diff <= 2 else "❌"  # 2 MIDI-askel toleranssi
            if diff > 2:
                all_good = False
            print(f"      {channel.upper()}: {orig} → {exported} (diff: {diff}) {status}")
        
        overall = "✅ PERFECT!" if all_good else "⚠️  SMALL DRIFT"
        print(f"   🎯 Tulos: {overall}")

def test_specific_case():
    """Testaa sinun tarkkaa ongelmatapausta"""
    print("\n" + "="*50)
    print("🎯 SINUN TARKKKA TAPAUS:")
    print("Kanava 35 (sininen) pitää näkyä sinisenä, ei valkoisena!")
    print("="*50)
    
    # Alkuperäinen MIDI-data joka aiheutti ongelman
    problematic_midi = {'r': 0, 'g': 0, 'b': 90, 'w': 0}  # Vain sinistä
    
    print(f"🎵 Alkuperäinen MIDI: {problematic_midi}")
    
    # Tuo Blenderiin
    blender_color = channels_to_rgb(problematic_midi)
    print(f"💡 Blenderissä näkyy: RGB({blender_color[0]:.3f}, {blender_color[1]:.3f}, {blender_color[2]:.3f})")
    
    # Värin tulkinta
    r, g, b = blender_color
    if r < 0.1 and g < 0.1 and b > 0.5:
        print("✅ ONNISTUI! Näkyy sinisenä eikä valkoisena!")
    elif r > 0.5 and g > 0.5 and b > 0.5:
        print("❌ EPÄONNISTUI! Näkyy valkoisena!")
    else:
        print(f"🤔 Epäselvä väri... R={r:.3f} G={g:.3f} B={b:.3f}")
    
    # Vie takaisin
    exported_back = rgb_to_channels(blender_color)
    print(f"📤 Vie takaisin: {exported_back}")
    
    # Tarkista että sininen kanava säilyy
    if exported_back['b'] > 50 and exported_back['r'] < 10 and exported_back['g'] < 10:
        print("✅ ROUND-TRIP OK! Sininen kanava säilyi!")
    else:
        print("❌ ROUND-TRIP FAIL! Sininen kanava hävisi!")

if __name__ == "__main__":
    test_round_trip()
    test_specific_case()