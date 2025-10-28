#!/usr/bin/env python3
"""
🌫️ Smoke Machine Demo for Blender

Quick demo showing how smoke machines work with MIDI channels 41-45.
Run this in Blender's Text Editor to see smoke effects in action.
"""

import bpy

def create_demo_smoke_scene():
    """Luo demo-scene savukoneilla"""
    
    # Tyhjennä scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    print("🌫️ Luodaan Smoke Machine Demo Scene")
    
    # Luo savukoneet eri paikoihin
    smoke_machines = [
        ("Smoke_Front_Left", (-3, 2, 0)),
        ("Smoke_Front_Right", (3, 2, 0)), 
        ("Smoke_Back_Left", (-3, -2, 0)),
        ("Smoke_Back_Right", (3, -2, 0)),
        ("Smoke_Center_Stage", (0, 0, 0))
    ]
    
    for name, location in smoke_machines:
        # Luo cube
        bpy.ops.mesh.primitive_cube_add(location=location)
        smoke_obj = bpy.context.active_object
        smoke_obj.name = name
        
        # Lisää smoke effect
        bpy.ops.object.quick_effects_smoke_flow()
        
        # Säädä alkuasetukset
        modifier = smoke_obj.modifiers.get("Fluid")
        if modifier:
            modifier.fluid_settings.density = 0.5  # Alkudensity
            modifier.fluid_settings.temperature = 1.0
            
        print(f"✅ Luotu: {name} kohdassa {location}")
    
    # Luo domain (pakollinen smoke-simulaatiolle)
    bpy.ops.mesh.primitive_cube_add(scale=(5, 5, 3), location=(0, 0, 1))
    domain_obj = bpy.context.active_object
    domain_obj.name = "Smoke_Domain"
    
    # Lisää domain
    bpy.ops.object.quick_effects_smoke_domain()
    
    # Säädä domain-asetuksia
    modifier = domain_obj.modifiers.get("Fluid")
    if modifier:
        modifier.fluid_settings.domain.resolution_max = 64
        modifier.fluid_settings.domain.alpha = 0.8
        
    print("✅ Luotu Smoke Domain")
    
    # Aseta frame range
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 120
    
    # Luo animaatiotesti
    create_smoke_animation_test()
    
    print("🎉 Demo valmis! Paina SPACE toistaaksesi animaation!")

def create_smoke_animation_test():
    """Luo testanimaatio savukoneille"""
    
    smoke_names = [
        "Smoke_Front_Left",
        "Smoke_Front_Right", 
        "Smoke_Back_Left",
        "Smoke_Back_Right",
        "Smoke_Center_Stage"
    ]
    
    for i, name in enumerate(smoke_names):
        smoke_obj = bpy.data.objects.get(name)
        if not smoke_obj:
            continue
            
        modifier = smoke_obj.modifiers.get("Fluid")
        if not modifier:
            continue
        
        # Animoi density: 0 → 1.5 → 0
        start_frame = 1 + i * 20  # Porrastus
        peak_frame = start_frame + 30
        end_frame = start_frame + 60
        
        # Keyframet
        modifier.fluid_settings.density = 0.0
        modifier.fluid_settings.keyframe_insert(data_path="density", frame=start_frame)
        
        modifier.fluid_settings.density = 1.5
        modifier.fluid_settings.keyframe_insert(data_path="density", frame=peak_frame)
        
        modifier.fluid_settings.density = 0.0
        modifier.fluid_settings.keyframe_insert(data_path="density", frame=end_frame)
        
        print(f"🎬 Animoitu: {name} (frames {start_frame}-{end_frame})")

def quick_smoke_test():
    """Nopea testi yhdelle savukoneelle"""
    
    # Luo yksi savukone
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    smoke_obj = bpy.context.active_object
    smoke_obj.name = "Test_Smoke"
    
    # Lisää smoke
    bpy.ops.object.quick_effects_smoke_flow()
    
    # Säädä density
    modifier = smoke_obj.modifiers.get("Fluid")
    if modifier:
        modifier.fluid_settings.density = 1.0
        print("🌫️ Test smoke luotu! Density = 1.0")
        
        # Jos haluat animoida:
        # modifier.fluid_settings.keyframe_insert(data_path="density", frame=1)
    
    return smoke_obj

if __name__ == "__main__":
    # Valitse kumpi haluat:
    
    # 1. Täysi demo
    create_demo_smoke_scene()
    
    # 2. Tai vain nopea testi:
    # quick_smoke_test()
    
    print("\n🌫️ Smoke Machine Demo")
    print("=" * 30)
    print("✅ Savukoneet luotu!")
    print("🎬 Paina SPACE toistaaksesi")
    print("🎛️ Density = savun määrä (0-2.0)")
    print("📺 3D Viewport → Shading → Material Preview/Rendered")
    print("")
    print("🎵 MIDI-integraatio:")
    print("   Kanava 41 = Smoke_Front_Left")
    print("   Kanava 42 = Smoke_Front_Right") 
    print("   Kanava 43 = Smoke_Back_Left")
    print("   Kanava 44 = Smoke_Back_Right")
    print("   Kanava 45 = Smoke_Center_Stage")