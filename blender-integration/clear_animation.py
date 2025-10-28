"""
🔄 Blender Animation Refresher

Jos näet edelleen vanhaa animaatiota, aja tämä skripti:
1. Poistaa KAIKKI vanhat keyframet
2. Nollaa kaikki valojen energiat
3. Pakottaa Blenderin päivittämään näkymän

Käytä tätä ennen uuden MIDI:n tuomista!
"""

import bpy

def force_clear_all_animations():
    """Pakottaa kaiken animaatiodata tyhjentämisen"""
    
    print("🧹 PAKKO-TYHJENNYS - Poistetaan KAIKKI animaatiot...")
    
    # Mene frame 1:een
    bpy.context.scene.frame_set(1)
    
    # Tyhjennä kaikki objektien animaatiot
    for obj in bpy.data.objects:
        # Aseta minimaalinen energia valoille (ei nollaa!)
        if obj.type == 'LIGHT' and obj.data:
            obj.data.energy = 1.0  # Pieni määrä jotta värit näkyvät
            
        # Poista animaatiodata
        if obj.animation_data:
            obj.animation_data_clear()
            
        if hasattr(obj, 'data') and obj.data and hasattr(obj.data, 'animation_data'):
            if obj.data.animation_data:
                obj.data.animation_data_clear()
    
    # Tyhjennä scenen animaatiot
    if bpy.context.scene.animation_data:
        bpy.context.scene.animation_data_clear()
    
    # Tyhjennä mahdolliset actionit
    for action in bpy.data.actions:
        bpy.data.actions.remove(action)
    
    # Pakota frame-range uusiksi
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 250
    bpy.context.scene.frame_set(1)
    
    # Päivitä kaikki näkymät
    bpy.context.view_layer.update()
    
    # Pakota kaikkien alueiden päivitys
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()
    
    print("✅ Kaikki animaatiot PAKOTETTU tyhjäksi!")
    print("💡 Nyt voit tuoda uuden MIDI:n turvallisesti")

def reset_lights_to_zero():
    """Asettaa kaikki valot minimiin (mutta pitää värit näkyvissä)"""
    
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and obj.data:
            obj.data.energy = 1.0  # Minimaalinen energia näkyvyyden säilyttämiseksi
            print(f"� Minimoitu: {obj.name} (energia 1.0W)")
    
    print("✅ Kaikki valot minimoitu mutta värit säilytetty")

# Aja tyhjennys
if __name__ == "__main__":
    print("🔄 BLENDER ANIMATION FORCE REFRESH")
    print("=" * 40)
    
    force_clear_all_animations()
    reset_lights_to_zero()
    
    print("\n🎉 VALMIS!")
    print("👉 Nyt voit ajaa midi_to_blender.py uudelleen")
    print("👉 Tai tuoda uuden MIDI-tiedoston")