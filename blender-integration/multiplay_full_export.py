#!/usr/bin/env python3
"""
🎭 Multiplay Full Show Export

Vie Blender-setup täydelliseksi näytelmäohjaukseksi:
- MIDI-tiedostot valoille (Scene Setter)  
- HTTP-skriptit savukoneille (ESP32)
- Multiplay Cue List JSON

Tukee sinun ammattilaisjärjestelmää:
- Multiplay päämittaus
- Scene Setter MIDI-valot
- ESP32 WiFi savukoneet
"""

import bpy
import json
import os
from datetime import datetime

# ESP32 Savukone API (Primary control via Multiplay)
ESP32_BASE_URL = "http://192.168.1.100"  # ESP32 IP oikeassa WiFi-verkossa

# Robotti-kaukolaukaisin (Backup/Manual only)  
ROBOT_BACKUP_NOTE = "Robotti toimii IR/Radio backupina - ei WiFi-yhteyttä Multiplayn kanssa"

# Savukoneiden + silmien mapping  
SMOKE_MACHINE_MAP = {
    41: {"name": "Smoke_Front_Left", "endpoint": "/set-eye-state", "eye_state": "smoke"},
    42: {"name": "Smoke_Front_Right", "endpoint": "/set-eye-state", "eye_state": "smoke"}, 
    43: {"name": "Smoke_Back_Left", "endpoint": "/set-eye-state", "eye_state": "smoke"},
    44: {"name": "Smoke_Back_Right", "endpoint": "/set-eye-state", "eye_state": "smoke"},
    45: {"name": "Smoke_Center_Stage", "endpoint": "/set-eye-state", "eye_state": "smoke"}
}

# Robotti-silmien animaatiot MIDI-kanavien mukaan
EYE_ANIMATION_MAP = {
    46: {"name": "Robot_Eyes_Center", "eye_state": "center"},
    47: {"name": "Robot_Eyes_Left", "eye_state": "left"},
    48: {"name": "Robot_Eyes_Right", "eye_state": "right"},
    49: {"name": "Robot_Eyes_Up", "eye_state": "up"}, 
    50: {"name": "Robot_Eyes_Down", "eye_state": "down"},
    51: {"name": "Robot_Eyes_Blink", "eye_state": "blink"},
    52: {"name": "Robot_Eyes_Roll", "eye_state": "roll"}
}

def scan_blender_lights():
    """Skannaa Blender-valot MIDI-exportia varten"""
    lights_data = {}
    smoke_data = {}
    
    for obj in bpy.data.objects:
        if obj.type != 'LIGHT' or obj.data.energy <= 1.001:
            continue
            
        light_name = obj.name
        energy = obj.data.energy
        color = list(obj.data.color)
        
        # Tarkista onko savukone (simulaatio)
        for channel, smoke_info in SMOKE_MACHINE_MAP.items():
            if smoke_info["name"] in light_name:
                # Savukone löydetty - muunna energy HTTP-komennoksi
                intensity = min(100, int((energy / 300.0) * 100))  # 0-100%
                smoke_data[channel] = {
                    "name": smoke_info["name"],
                    "endpoint": smoke_info["endpoint"], 
                    "eye_state": smoke_info["eye_state"],
                    "intensity": intensity,
                    "duration": 5  # Oletus 5s pulssi
                }
                print(f"🌫️ Smoke: {light_name} → {smoke_info['eye_state']} intensity {intensity}%")
                continue
                
        # Tarkista onko robotti-silmien animaatio
        for channel, eye_info in EYE_ANIMATION_MAP.items():
            if eye_info["name"] in light_name:
                # Robotti-silmä-animaatio löydetty
                smoke_data[channel] = {
                    "name": eye_info["name"],
                    "endpoint": "/set-eye-state",
                    "eye_state": eye_info["eye_state"], 
                    "intensity": int((energy / 300.0) * 100),
                    "duration": 2  # Lyhyempi animaatio
                }
                print(f"👁️ Robot Eyes: {light_name} → {eye_info['eye_state']}")
                continue
        
        # Tavallinen valo - RGBW tai single
        channel_list = get_channels_from_name(light_name)
        if not channel_list:
            continue
            
        if len(channel_list) == 4:
            # RGBW-ryhmä
            rgbw_values = analyze_rgbw_color(color, energy)
            
            for i, channel in enumerate(channel_list):
                velocity = rgbw_values[i]
                if velocity > 0:
                    lights_data[str(channel)] = velocity
                    
        else:
            # Yksittäinen valo
            channel = channel_list[0]
            velocity = energy_to_velocity(energy)
            if velocity > 0:
                lights_data[str(channel)] = velocity
    
    return lights_data, smoke_data

def get_channels_from_name(light_name):
    """Päättelee kanavat valon nimestä"""
    import re
    
    # RGBW-ryhmät: "RGBW 13-16"
    rgbw_match = re.search(r'RGBW\s+(\d+)-(\d+)', light_name)
    if rgbw_match:
        start = int(rgbw_match.group(1))
        end = int(rgbw_match.group(2))
        if end - start == 3:
            return [start, start+1, start+2, start+3]
    
    # Yksittäiset: "21" tai "Spot.021"
    numbers = re.findall(r'\d+', light_name)
    if numbers:
        return [int(numbers[0])]
    
    return []

def analyze_rgbw_color(color, energy):
    """Analysoi RGB-väri RGBW-komponentteihin"""
    r, g, b = color[:3]
    
    # Laske valkoinen komponentti
    white_component = min(r, g, b)
    
    # Poista valkoinen puhtaista väreistä  
    pure_r = max(0.0, r - white_component)
    pure_g = max(0.0, g - white_component)
    pure_b = max(0.0, b - white_component)
    
    # Muunna energiasta intensiteetti
    intensity = min(1.0, energy / 300.0)
    
    # Laske MIDI-velocityt
    r_vel = int(pure_r * intensity * 127)
    g_vel = int(pure_g * intensity * 127)
    b_vel = int(pure_b * intensity * 127)
    w_vel = int(white_component * intensity * 127)
    
    return [r_vel, g_vel, b_vel, w_vel]

def energy_to_velocity(energy):
    """Muuntaa energia velocity:ksi"""
    return min(127, int((energy / 300.0) * 127))

def create_multiplay_cue_list(lights_data, smoke_data, scene_name="Blender_Scene"):
    """Luo Multiplay Cue List JSON"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    cue_list = {
        "version": "1.0",
        "name": f"{scene_name}_{timestamp}",
        "description": "Generated from Blender with RGBW lights + ESP32 smoke machines",
        "cues": []
    }
    
    cue_number = 1.0
    
    # Cue 1: Fade In Lights
    if lights_data:
        lights_cue = {
            "number": cue_number,
            "name": "Lights Fade In",
            "type": "midi",
            "action": "play_file",
            "file": f"{scene_name}_fade_in.mid",
            "device": "Scene_Setter_USB",
            "wait": 0.0,
            "notes": f"MIDI channels: {', '.join(lights_data.keys())}"
        }
        cue_list["cues"].append(lights_cue)
        cue_number += 0.5
    
    # Cue 2: Smoke Machines
    if smoke_data:
        for channel, smoke_info in smoke_data.items():
            smoke_cue = {
                "number": cue_number,
                "name": f"Smoke: {smoke_info['name']}",
                "type": "http_post", 
                "url": f"{ESP32_BASE_URL}{smoke_info['endpoint']}/pulse",
                "payload": {
                    "intensity": smoke_info["intensity"],
                    "duration": smoke_info["duration"]
                },
                "wait": 0.1,
                "notes": f"ESP32 Smoke Machine {channel}"
            }
            cue_list["cues"].append(smoke_cue)
            cue_number += 0.1
    
    # Cue 3: Wait for show duration
    wait_cue = {
        "number": cue_number + 1.0,
        "name": "Show Running",
        "type": "wait",
        "duration": 30.0,  # 30s oletus
        "notes": "Adjust duration based on scene length"
    }
    cue_list["cues"].append(wait_cue)
    
    # Cue 4: Fade Out All
    fadeout_cue = {
        "number": cue_number + 2.0,
        "name": "Fade Out All",
        "type": "parallel",
        "actions": [
            {
                "type": "midi",
                "file": f"{scene_name}_fade_out.mid",
                "device": "Scene_Setter_USB"
            },
            {
                "type": "http_post",
                "url": f"{ESP32_BASE_URL}/smoke/all_off",
                "payload": {}
            }
        ],
        "notes": "Simultaneous fadeout of lights and smoke"
    }
    cue_list["cues"].append(fadeout_cue)
    
    return cue_list

def export_full_show(scene_name="Blender_Scene"):
    """Pääfunktio: Vie täysi näytelmäsetup"""
    
    print(f"🎭 Viedään täysi show: {scene_name}")
    print("=" * 50)
    
    # Skannaa Blender
    lights_data, smoke_data = scan_blender_lights()
    
    print(f"💡 Löydettiin {len(lights_data)} valokanavaa")
    print(f"🌫️ Löydettiin {len(smoke_data)} savukonetta")
    
    if not lights_data and not smoke_data:
        print("❌ Ei löytynyt valoja tai savukoneita!")
        return False
    
    # Luo output-kansio
    output_dir = f"/Users/raulivirtanen/Documents/valot/multiplay_export"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Vie MIDI (valot)
    if lights_data:
        midi_json = {
            "scene_name": scene_name,
            "channels": lights_data,
            "fade_in_duration": 2.0,
            "fade_out_duration": 3.0, 
            "steps": 20
        }
        
        midi_file = f"{output_dir}/{scene_name}_lights_{timestamp}.json"
        with open(midi_file, 'w') as f:
            json.dump(midi_json, f, indent=2)
        
        print(f"💾 MIDI JSON: {midi_file}")
    
    # 2. Vie HTTP-skriptit (savukoneet)
    if smoke_data:
        http_scripts = {
            "esp32_base_url": ESP32_BASE_URL,
            "smoke_machines": smoke_data,
            "generated": timestamp
        }
        
        http_file = f"{output_dir}/{scene_name}_smoke_{timestamp}.json"
        with open(http_file, 'w') as f:
            json.dump(http_scripts, f, indent=2)
        
        print(f"💾 HTTP JSON: {http_file}")
    
    # 3. Vie Multiplay Cue List
    cue_list = create_multiplay_cue_list(lights_data, smoke_data, scene_name)
    
    cue_file = f"{output_dir}/{scene_name}_multiplay_{timestamp}.json"
    with open(cue_file, 'w') as f:
        json.dump(cue_list, f, indent=2)
    
    print(f"💾 Multiplay Cues: {cue_file}")
    
    # 4. Tulosta ohje
    print("\n🎬 MULTIPLAY SETUP:")
    print("=" * 30)
    print("1. Generate MIDI files:")
    print(f"   python3 midimaker5.py {midi_file}")
    print("2. Upload .mid files to Multiplay")  
    print("3. Import cue list JSON to Multiplay")
    print("4. Configure ESP32 IP address")
    print("5. Test HTTP endpoints manually")
    print("6. Run show! 🎉")
    
    return True

if __name__ == "__main__":
    # Aja export
    export_full_show("Act1_Scene2")  # Muokkaa scene-nimeä