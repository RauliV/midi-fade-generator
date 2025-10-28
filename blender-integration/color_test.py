"""
🌈 Blender Color Test Script

Luo testivaloja joissa näkyy kaikki värit selkeästi.
Käytä tätä testaamaan että värit näkyvät Blenderissä!
"""

import bpy

def create_color_test_lights():
    """Luo testivaloja eri väreillä"""
    
    print("🌈 Luodaan väritestivaloja...")
    
    # Poista vanhat testivalot
    for obj in list(bpy.data.objects):
        if obj.name.startswith("ColorTest_"):
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # RGBW-testivalot
    colors = [
        ("Red", (1.0, 0.0, 0.0)),
        ("Green", (0.0, 1.0, 0.0)), 
        ("Blue", (0.0, 0.0, 1.0)),
        ("White", (1.0, 1.0, 1.0)),
        ("Yellow", (1.0, 1.0, 0.0)),
        ("Magenta", (1.0, 0.0, 1.0)),
        ("Cyan", (0.0, 1.0, 1.0)),
        ("Orange", (1.0, 0.5, 0.0))
    ]
    
    for i, (name, color) in enumerate(colors):
        # Luo valo
        x = (i % 4) * 3  # 4 valoa per rivi
        y = (i // 4) * 3
        location = (x, y, 3)
        
        bpy.ops.object.light_add(type='SPOT', location=location)
        light_obj = bpy.context.object
        light_obj.name = f"ColorTest_{name}"
        light_obj.data.name = f"ColorTest_{name}_Data"
        
        # Aseta väri ja energia
        light_obj.data.color = color
        light_obj.data.energy = 50.0  # Hyvä näkyvyys
        light_obj.data.spot_size = 1.0  # 57 astetta
        
        print(f"💡 {name}: {color} @ {light_obj.data.energy}W")
    
    # Varmista että näkymä päivittyy
    bpy.context.view_layer.update()
    
    print("✅ Väritestivalot luotu!")
    print("👀 Jos et näe värejä, tarkista:")
    print("   - Viewport Shading = Material Preview tai Rendered")
    print("   - Valojen energia > 0")
    print("   - Kamera-asento")

def quick_viewport_setup():
    """Asettaa viewportin oikein värien näkemiseen"""
    
    # Etsi 3D Viewport
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    # Aseta Material Preview mode
                    space.shading.type = 'MATERIAL'
                    print("📷 Viewport asetettu Material Preview -tilaan")
                    area.tag_redraw()
                    break

# Aja testit
if __name__ == "__main__":
    print("🌈 BLENDER COLOR TEST")
    print("=" * 30)
    
    create_color_test_lights()
    quick_viewport_setup()
    
    print("\n🎨 Testivalot luotu!")
    print("👁️  Jos värit näkyvät, MIDI-tuonti toimii nyt paremmin!")
    print("🔴 Jos värit ovat mustia, ongelma on viewport-asetuksissa")