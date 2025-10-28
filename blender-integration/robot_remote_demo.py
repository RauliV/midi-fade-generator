#!/usr/bin/env python3
"""
🤖 Robotti-kaukolaukaisin Blender Demo

Demonstroi kuinka Blender simuloi robotti-kaukolaukaisinta:
- Silmä-animaatiot OLED-näytölle
- Savukone-laukaisu napin kautta  
- Multiplay-integraatio
"""

import bpy
import bmesh
from mathutils import Vector
import json

def create_robot_remote_setup():
    """Luo robotti-kaukolaukaisin Blender-setuppi"""
    
    # Poista olemassa olevat objektit
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # 1. Robotti-pää (silmien simulaatio)
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 2))
    robot_head = bpy.context.active_object
    robot_head.name = "Robot_Head"
    robot_head.scale = (0.8, 0.6, 0.4)
    
    # 2. Robotti-vartalo
    bpy.ops.mesh.primitive_cylinder_add(location=(0, 0, 0.5))
    robot_body = bpy.context.active_object  
    robot_body.name = "Robot_Body"
    robot_body.scale = (0.5, 0.5, 1.0)
    
    # 3. Nappi (piilossa pään alla)
    bpy.ops.mesh.primitive_cylinder_add(location=(0, 0, 1.6))
    button = bpy.context.active_object
    button.name = "Robot_Button"
    button.scale = (0.1, 0.1, 0.05)
    
    # 4. OLED-näyttö simulaatio (silmille)
    bpy.ops.mesh.primitive_plane_add(location=(0, -0.4, 2))
    oled_display = bpy.context.active_object
    oled_display.name = "OLED_Display"
    oled_display.scale = (0.3, 0.1, 1)
    oled_display.rotation_euler = (1.57, 0, 0)  # 90° X-akselilla
    
    print("🤖 Robotti-kaukolaukaisin luotu!")

def create_robot_eye_lights():
    """Luo valot jotka simuloivat robotti-silmiä"""
    
    eye_animations = [
        {"name": "Robot_Eyes_Center", "location": (0, -0.5, 2), "channel": 46},
        {"name": "Robot_Eyes_Left", "location": (-0.15, -0.5, 2), "channel": 47},
        {"name": "Robot_Eyes_Right", "location": (0.15, -0.5, 2), "channel": 48},
        {"name": "Robot_Eyes_Up", "location": (0, -0.5, 2.1), "channel": 49},
        {"name": "Robot_Eyes_Down", "location": (0, -0.5, 1.9), "channel": 50},
        {"name": "Robot_Eyes_Blink", "location": (0, -0.45, 2), "channel": 51},
        {"name": "Robot_Eyes_Roll", "location": (0, -0.4, 2), "channel": 52}
    ]
    
    for eye_anim in eye_animations:
        # Luo valo
        bpy.ops.object.light_add(type='POINT', location=eye_anim["location"])
        light = bpy.context.active_object
        light.name = eye_anim["name"]
        
        # Aseta väri ja energia
        light.data.energy = 50  # Matala energia = ei aktiivinen
        light.data.color = (0.8, 0.9, 1.0)  # Sinertävä valkoinen
        light.data.shadow_soft_size = 0.1
        
        print(f"👁️ Luotu: {eye_anim['name']} (kanava {eye_anim['channel']})")

def create_smoke_machine_lights():
    """Luo valot jotka simuloivat savukoneita"""
    
    smoke_machines = [
        {"name": "Smoke_Front_Left", "location": (-3, 3, 0.5), "channel": 41},
        {"name": "Smoke_Front_Right", "location": (3, 3, 0.5), "channel": 42},
        {"name": "Smoke_Back_Left", "location": (-3, -3, 0.5), "channel": 43},
        {"name": "Smoke_Back_Right", "location": (3, -3, 0.5), "channel": 44},
        {"name": "Smoke_Center_Stage", "location": (0, 0, 0.5), "channel": 45}
    ]
    
    for smoke in smoke_machines:
        # Luo valo
        bpy.ops.object.light_add(type='AREA', location=smoke["location"])
        light = bpy.context.active_object
        light.name = smoke["name"]
        
        # Aseta väri ja energia savukoneelle
        light.data.energy = 100  # Kohtalainen energia = valmiustila
        light.data.color = (0.9, 0.9, 0.9)  # Harmaa = savu
        light.data.size = 1.0
        light.data.shape = 'SQUARE'
        
        print(f"🌫️ Luotu: {smoke['name']} (kanava {smoke['channel']})")

def create_demo_animation():
    """Luo demo-animaatio robotti-näytelmälle"""
    
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 200
    
    # Animoi robotti-silmiä
    robot_eyes = [obj for obj in bpy.data.objects if "Robot_Eyes" in obj.name]
    
    for i, eye_light in enumerate(robot_eyes):
        if eye_light.type != 'LIGHT':
            continue
            
        # Aseta keyframet
        frame_start = 20 + i * 25
        frame_end = frame_start + 10
        
        # Alku: energia 50
        scene.frame_set(frame_start)
        eye_light.data.energy = 50
        eye_light.data.keyframe_insert(data_path="energy")
        
        # Huippu: energia 300 (aktiivinen)
        scene.frame_set(frame_start + 5)
        eye_light.data.energy = 300
        eye_light.data.keyframe_insert(data_path="energy")
        
        # Loppu: takaisin 50
        scene.frame_set(frame_end)
        eye_light.data.energy = 50
        eye_light.data.keyframe_insert(data_path="energy")
        
        print(f"👁️ Animoitu: {eye_light.name} frameissa {frame_start}-{frame_end}")
    
    # Animoi savukoneita
    smoke_lights = [obj for obj in bpy.data.objects if "Smoke_" in obj.name]
    
    for i, smoke_light in enumerate(smoke_lights):
        if smoke_light.type != 'LIGHT':
            continue
            
        frame_trigger = 100 + i * 15
        
        # Savukone laukaisu
        scene.frame_set(frame_trigger)
        smoke_light.data.energy = 100
        smoke_light.data.keyframe_insert(data_path="energy")
        
        scene.frame_set(frame_trigger + 1)
        smoke_light.data.energy = 300  # Savu päälle!
        smoke_light.data.keyframe_insert(data_path="energy")
        
        scene.frame_set(frame_trigger + 20)
        smoke_light.data.energy = 100  # Savu pois
        smoke_light.data.keyframe_insert(data_path="energy")
        
        print(f"🌫️ Animoitu: {smoke_light.name} framessa {frame_trigger}")

def export_robot_demo():
    """Vie robotti-demo Multiplay-yhteensopivaksi"""
    
    from . import multiplay_full_export
    
    # Skannaa nykyinen setup
    lights_data, smoke_data = multiplay_full_export.scan_blender_lights()
    
    # Luo Multiplay cue list
    cue_list = multiplay_full_export.create_multiplay_cue_list(lights_data, smoke_data)
    
    # Tallenna
    output_path = bpy.path.abspath("//robot_demo_cues.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cue_list, f, indent=2, ensure_ascii=False)
    
    print(f"🎭 Robotti-demo viety: {output_path}")

# Suorita demo
if __name__ == "__main__":
    print("🤖 Luodaan robotti-kaukolaukaisin demo...")
    create_robot_remote_setup()
    create_robot_eye_lights()
    create_smoke_machine_lights()
    create_demo_animation()
    export_robot_demo()
    print("✅ Robotti-demo valmis!")