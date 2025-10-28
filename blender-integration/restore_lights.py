"""
💡 Quick Light Restore - Palauta valot näkyviksi

Jos valot ovat mustia/näkymättömiä, aja tämä skripti
Blenderin Text Editorissa. Asettaa kaikki valot näkyviksi
valkoisella valolla.

Käyttö:
1. Kopioi tämä skripti Blenderin Text Editoriin
2. Paina Run Script
3. Kaikki valot syttyvät valkoisina ja näkyvät!
"""

import bpy

def restore_all_lights():
    """Palauttaa kaikki valot näkyviksi valkoisella valolla"""
    
    print("💡 Palautetaan kaikki valot näkyviksi...")
    
    restored_count = 0
    
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and obj.data:
            # Aseta hyvä näkyvä energia
            obj.data.energy = 50.0
            
            # Aseta valkoinen väri (jotta kaikki värit näkyvät)
            obj.data.color = (1.0, 1.0, 1.0)  # Valkoinen
            
            # Varmista että valo on päällä
            if hasattr(obj.data, 'use_shadow'):
                obj.data.use_shadow = True
            
            restored_count += 1
            print(f"  ✅ {obj.name}: 50W, valkoinen")
    
    # Aseta viewport Material Preview -tilaan
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    print("  📷 Viewport: Material Preview")
                    area.tag_redraw()
                    break
    
    # Päivitä näkymä
    bpy.context.view_layer.update()
    
    print(f"✅ {restored_count} valoa palautettu näkyviksi!")
    
    if restored_count == 0:
        print("❌ Ei löytynyt yhtään valoa!")
        print("💡 Vinkki: Luo valoja ensin tai tuo MIDI-tiedosto")
    
    return restored_count

def set_good_viewport():
    """Asettaa viewport-asetukset valojen näkemiseen"""
    
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    # Material Preview on paras valojen näkemiseen
                    space.shading.type = 'MATERIAL'
                    
                    # Varmista että valaistus on päällä
                    if hasattr(space.shading, 'use_scene_lights'):
                        space.shading.use_scene_lights = True
                    if hasattr(space.shading, 'use_scene_world'):
                        space.shading.use_scene_world = True
                    
                    area.tag_redraw()
                    print("📷 Viewport optimoitu valojen näkemiseen")
                    break

def quick_scene_setup():
    """Perustaa nopean scenen valojen testaamiseen"""
    
    # Lisää peruskamera jos ei ole
    if not any(obj.type == 'CAMERA' for obj in bpy.data.objects):
        bpy.ops.object.camera_add(location=(7, -7, 5))
        camera = bpy.context.object
        camera.rotation_euler = (1.1, 0, 0.785)  # Katso alaspäin ja keskelle
        print("📷 Lisätty kamera")
    
    # Varmista että scene on aktiivinen
    bpy.context.scene.frame_set(1)
    
    print("🎬 Scene valmis valojen testaamiseen")

# Aja palauttaminen
if __name__ == "__main__":
    print("💡 LIGHT RESTORE - Palauta valot näkyviksi")
    print("=" * 50)
    
    # Palauta valot
    count = restore_all_lights()
    
    # Optimoi viewport
    set_good_viewport()
    
    # Perustaa scene
    quick_scene_setup()
    
    print("\n🎉 VALMIS!")
    
    if count > 0:
        print("👀 Nyt pitäisi näkyä valkoisia valoja!")
        print("🌈 Jos näet valoja, voit tuoda MIDI-animaation")
        print("🎨 Voit nyt muuttaa valojen värejä manuaalisesti")
    else:
        print("❌ Ei löytynyt valoja palautettavaksi")
        print("💡 Luo ensin valoja tai tuo MIDI-tiedosto")
    
    print("\n🔧 Jos valot ovat edelleen mustia:")
    print("   1. Tarkista Viewport Shading (Material Preview)")
    print("   2. Tarkista valojen Energy > 0")
    print("   3. Tarkista kamera-asento")