#!/usr/bin/env python3
"""
🌫️ Smoke Machine Integration for MIDI Light Controller

Adds smoke machine support to existing RGBW system.
Maps MIDI channels to Blender volume/particle effects.
"""

import bpy
import re

# Savukoneiden kanavamapping
SMOKE_MACHINE_CHANNELS = {
    41: "Smoke_Front_Left",
    42: "Smoke_Front_Right", 
    43: "Smoke_Back_Left",
    44: "Smoke_Back_Right",
    45: "Smoke_Center_Stage"
}

def create_smoke_machine(name, location=(0, 0, 0)):
    """Luo savukoneen Blenderiin"""
    
    # Luo cube joka toimii emitterinä
    bpy.ops.mesh.primitive_cube_add(location=location)
    smoke_obj = bpy.context.active_object
    smoke_obj.name = name
    
    # Lisää Smoke simulation
    bpy.ops.object.quick_effects_smoke_flow()
    
    # Säädä asetukset
    modifier = smoke_obj.modifiers.get("Fluid")
    if modifier:
        # Flow settings
        modifier.fluid_settings.flow_type = 'SMOKE'
        modifier.fluid_settings.density = 0.0  # Alkuun ei savua
        modifier.fluid_settings.temperature = 1.0
        
    print(f"🌫️ Luotu savukone: {name} kohdassa {location}")
    return smoke_obj

def update_smoke_density(smoke_obj, velocity):
    """Päivittää savukoneen tiheyden MIDI velocity:n mukaan"""
    
    modifier = smoke_obj.modifiers.get("Fluid")
    if not modifier:
        return False
    
    # Muunna MIDI velocity (0-127) → density (0-2.0)
    density = (velocity / 127.0) * 2.0
    modifier.fluid_settings.density = density
    
    print(f"🌫️ {smoke_obj.name}: velocity {velocity} → density {density:.2f}")
    return True

def get_or_create_smoke_machine(channel):
    """Hakee tai luo savukoneen kanavalle"""
    
    if channel not in SMOKE_MACHINE_CHANNELS:
        return None
    
    smoke_name = SMOKE_MACHINE_CHANNELS[channel]
    
    # Etsi olemassa oleva
    smoke_obj = bpy.data.objects.get(smoke_name)
    if smoke_obj:
        print(f"🔍 Löydettiin savukone: {smoke_name}")
        return smoke_obj
    
    # Luo uusi savukone
    # Sijoita älykkäästi
    positions = {
        41: (-3, 2, 0),   # Front Left
        42: (3, 2, 0),    # Front Right  
        43: (-3, -2, 0),  # Back Left
        44: (3, -2, 0),   # Back Right
        45: (0, 0, 0)     # Center Stage
    }
    
    location = positions.get(channel, (0, 0, 0))
    smoke_obj = create_smoke_machine(smoke_name, location)
    
    return smoke_obj

def import_smoke_effects_from_midi(midi_path):
    """Tuo savukone-efektit MIDI-tiedostosta"""
    
    import mido
    
    print(f"🌫️ Tuodaan savuefektit: {midi_path}")
    
    try:
        midi_file = mido.MidiFile(midi_path)
    except Exception as e:
        print(f"❌ MIDI-virhe: {e}")
        return False
    
    # Käsittele MIDI-tapahtumat
    for track_num, track in enumerate(midi_file.tracks):
        track_time = 0
        
        for msg in track:
            track_time += msg.time
            
            if hasattr(msg, 'type') and msg.type == 'note_on':
                channel = msg.note - 69  # MIDI note → kanava
                
                # Tarkista onko savukone-kanava
                if channel in SMOKE_MACHINE_CHANNELS:
                    velocity = msg.velocity
                    frame = int((track_time / midi_file.ticks_per_beat) * 24 * 0.5)
                    
                    # Hae tai luo savukone
                    smoke_obj = get_or_create_smoke_machine(channel)
                    if smoke_obj:
                        # Päivitä density
                        update_smoke_density(smoke_obj, velocity)
                        
                        # Aseta keyframe
                        modifier = smoke_obj.modifiers.get("Fluid")
                        if modifier:
                            modifier.fluid_settings.keyframe_insert(
                                data_path="density", frame=frame
                            )
                        
                        print(f"🌫️ Frame {frame}: {SMOKE_MACHINE_CHANNELS[channel]} = {velocity}")
    
    print("✅ Savuefektit tuotu!")
    return True

def test_smoke_integration():
    """Testaa savukone-integraatioa"""
    print("🌫️ Smoke Machine Integration Test")
    print("=" * 40)
    
    # Testaa eri intensiteettejä
    test_cases = [
        (41, 0, "Ei savua"),
        (41, 64, "Kevyt savu"), 
        (41, 127, "Täysi savu"),
        (45, 90, "Center stage savu")
    ]
    
    for channel, velocity, description in test_cases:
        print(f"\n📍 {description}")
        smoke_obj = get_or_create_smoke_machine(channel)
        if smoke_obj:
            update_smoke_density(smoke_obj, velocity)

if __name__ == "__main__":
    # Testaa jos ajetaan Blenderissä
    test_smoke_integration()