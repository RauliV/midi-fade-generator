#!/usr/bin/env python3
"""
🎨 RGBW Color Mixing Test

Testaa RGBW-värinsekoituslogiikkaa ilman Blenderiä.
Simuloi miten värit sekoittuvat kun eri kanavat aktivoidaan.
"""

import re

# Simuloitu RGBW-tilat
rgbw_channel_states = {}

def get_rgbw_channels(light_name):
    """Palauttaa RGBW-valon kanavanumerot tai None jos ei ole RGBW"""
    match = re.search(r'RGBW\s+(\d+)-(\d+)', light_name)
    if match:
        start_channel = int(match.group(1))
        end_channel = int(match.group(2))
        if end_channel - start_channel == 3:  # Tarkista että on 4 kanavaa
            return {
                'r': start_channel,
                'g': start_channel + 1, 
                'b': start_channel + 2,
                'w': start_channel + 3
            }
    return None

def update_rgbw_color(light_name, channel, velocity):
    """Päivittää RGBW-valon väri perustuen kaikkiin aktiivisiin kanaviin"""
    rgbw_channels = get_rgbw_channels(light_name)
    
    if not rgbw_channels:
        return False  # Ei ole RGBW-valo
    
    # Alusta valon tila jos ei ole vielä
    if light_name not in rgbw_channel_states:
        rgbw_channel_states[light_name] = {'r': 0, 'g': 0, 'b': 0, 'w': 0}
    
    # Päivitä kanavan arvo
    state = rgbw_channel_states[light_name]
    for color, ch in rgbw_channels.items():
        if ch == channel:
            state[color] = velocity
            print(f"🎨 {light_name}: {color.upper()} kanava {ch} = {velocity}")
            break
    
    # Laske sekoitettu väri
    r_intensity = state['r'] / 127.0
    g_intensity = state['g'] / 127.0  
    b_intensity = state['b'] / 127.0
    w_intensity = state['w'] / 127.0
    
    # Valkoinen kanava lisää kaikkia värejä
    final_r = min(1.0, r_intensity + w_intensity * 0.8)
    final_g = min(1.0, g_intensity + w_intensity * 0.8) 
    final_b = min(1.0, b_intensity + w_intensity * 0.8)
    
    # Laske kokonaisteho (käytetään suurinta kanavaa + valkoinen)
    max_channel = max(state['r'], state['g'], state['b'])
    total_intensity = max(max_channel, state['w'])
    
    print(f"💡 {light_name}: RGB({final_r:.2f}, {final_g:.2f}, {final_b:.2f}) teho={total_intensity}")
    print(f"   Kanavat: R={state['r']} G={state['g']} B={state['b']} W={state['w']}")
    print()
    
    return {
        'color': (final_r, final_g, final_b),
        'intensity': total_intensity,
        'channels': state.copy()
    }

def test_scenarios():
    """Testaa erilaisia RGBW-skenaarioita"""
    print("🧪 RGBW Color Mixing Test")
    print("=" * 40)
    
    light_name = "RGBW 33-36"
    
    print(f"Testataan valoa: {light_name}")
    channels = get_rgbw_channels(light_name)
    print(f"Kanavat: {channels}")
    print()
    
    # Skenaario 1: Vain punainen
    print("📍 SKENAARIO 1: Vain punainen (kanava 33)")
    update_rgbw_color(light_name, 33, 127)
    
    # Skenaario 2: Lisätään sininen
    print("📍 SKENAARIO 2: Punainen + sininen")
    update_rgbw_color(light_name, 35, 127)  # Sininen
    
    # Skenaario 3: Lisätään vihreä
    print("📍 SKENAARIO 3: Punainen + sininen + vihreä")
    update_rgbw_color(light_name, 34, 127)  # Vihreä
    
    # Skenaario 4: Lisätään valkoinen
    print("📍 SKENAARIO 4: RGB + valkoinen")
    update_rgbw_color(light_name, 36, 64)   # Valkoinen 50%
    
    # Skenaario 5: Vain valkoinen
    print("📍 SKENAARIO 5: Vain valkoinen")
    rgbw_channel_states[light_name] = {'r': 0, 'g': 0, 'b': 0, 'w': 0}
    update_rgbw_color(light_name, 36, 127)  # Valkoinen 100%
    
    # Skenaario 6: Sininen + valkoinen (käyttäjän ongelma)
    print("📍 SKENAARIO 6: Sininen + valkoinen (käyttäjän tapaus)")
    rgbw_channel_states[light_name] = {'r': 0, 'g': 0, 'b': 0, 'w': 0}
    update_rgbw_color(light_name, 35, 90)   # Sininen
    update_rgbw_color(light_name, 36, 40)   # Valkoinen

if __name__ == "__main__":
    test_scenarios()