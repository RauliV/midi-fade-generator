"""
🎭 MIDI Light Controller - SAFE VERSION

Yksinkertainen ja turvallinen versio joka ei kaada Blenderiä.
Keskittyy olennaisiin toimintoihin.
"""

bl_info = {
    "name": "MIDI Light Controller (Safe)",
    "author": "Rauli Virtanen", 
    "version": (1, 1, 0),
    "blender": (3, 0, 0),
    "location": "3D Viewport > N-Panel > MIDI Lights",
    "description": "MIDI-valoohjauksen integraatio (turvallinen versio)",
    "category": "Lighting",
}

import bpy
from bpy.types import Panel, Operator

# ==========================================
# OPERATORS (Toiminnot)
# ==========================================

class MIDI_OT_clear_animation_safe(Operator):
    """Tyhjennä animaatiot turvallisesti"""
    bl_idname = "midi.clear_animation_safe"
    bl_label = "Clear Animation"
    bl_description = "Poista vanhat keyframet"
    
    def execute(self, context):
        try:
            cleared_count = 0
            
            # Tyhjennä vain light-objektien animaatiot
            for obj in bpy.data.objects:
                if obj.type == 'LIGHT' and obj.data:
                    obj.data.energy = 1.0  # Minimaalinen energia
                    
                    if obj.data.animation_data:
                        obj.data.animation_data_clear()
                    cleared_count += 1
            
            # Aseta frame 1
            bpy.context.scene.frame_set(1)
            bpy.context.view_layer.update()
            
            self.report({'INFO'}, f"Tyhjennetty {cleared_count} valon animaatiot")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Virhe: {str(e)}")
            return {'CANCELLED'}

class MIDI_OT_restore_lights_safe(Operator):
    """Palauta valot näkyviksi"""
    bl_idname = "midi.restore_lights_safe"
    bl_label = "Restore Lights"
    bl_description = "Palautta valot valkoisiksi ja näkyviksi"
    
    def execute(self, context):
        try:
            restored_count = 0
            
            for obj in bpy.data.objects:
                if obj.type == 'LIGHT' and obj.data:
                    obj.data.energy = 50.0
                    obj.data.color = (1.0, 1.0, 1.0)
                    restored_count += 1
            
            # Aseta viewport Material Preview
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.shading.type = 'MATERIAL'
                            break
            
            bpy.context.view_layer.update()
            
            self.report({'INFO'}, f"Palautettu {restored_count} valoa")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Virhe: {str(e)}")
            return {'CANCELLED'}

class MIDI_OT_scan_lights_safe(Operator):
    """Skannaa valot turvallisesti"""
    bl_idname = "midi.scan_lights_safe"
    bl_label = "Scan Lights"
    bl_description = "Skannaa nykyiset valot"
    
    def execute(self, context):
        try:
            all_lights = []
            
            for obj in bpy.data.objects:
                if obj.type == 'LIGHT':
                    all_lights.append(obj.name)
            
            if not all_lights:
                self.report({'WARNING'}, "Ei löytynyt valoja!")
                return {'CANCELLED'}
            
            # Tulosta console
            print("\n" + "="*40)
            print("🔍 LIGHTS SCAN")
            print("="*40)
            
            for i, name in enumerate(sorted(all_lights), 1):
                obj = bpy.data.objects.get(name)
                if obj:
                    energy = obj.data.energy
                    print(f"{i:2d}. {name} - {energy:.1f}W")
            
            print("="*40)
            
            self.report({'INFO'}, f"Skannattu {len(all_lights)} valoa - katso Console")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Virhe: {str(e)}")
            return {'CANCELLED'}

class MIDI_OT_create_test_lights_safe(Operator):
    """Luo testivaloja"""
    bl_idname = "midi.create_test_lights_safe"
    bl_label = "Test Lights"
    bl_description = "Luo värikkäitä testivaloja"
    
    def execute(self, context):
        try:
            # Poista vanhat testivalot
            for obj in list(bpy.data.objects):
                if obj.name.startswith("TestLight_"):
                    bpy.data.objects.remove(obj, do_unlink=True)
            
            # Luo uudet testivalot
            colors = [
                ("Red", (1.0, 0.0, 0.0)),
                ("Green", (0.0, 1.0, 0.0)), 
                ("Blue", (0.0, 0.0, 1.0)),
                ("White", (1.0, 1.0, 1.0))
            ]
            
            for i, (name, color) in enumerate(colors):
                bpy.ops.object.light_add(type='SPOT', location=(i*3, 0, 3))
                light = bpy.context.object
                light.name = f"TestLight_{name}"
                light.data.color = color
                light.data.energy = 50.0
            
            # Material Preview mode
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.shading.type = 'MATERIAL'
                            break
            
            bpy.context.view_layer.update()
            
            self.report({'INFO'}, f"Luotu {len(colors)} testivaloa")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Virhe: {str(e)}")
            return {'CANCELLED'}

# ==========================================
# PANELS (Käyttöliittymä)
# ==========================================

class MIDI_PT_safe_panel(Panel):
    """Turvallinen pääpaneeli"""
    bl_label = "MIDI Lights (Safe)"
    bl_idname = "MIDI_PT_safe_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MIDI Safe'
    
    def draw(self, context):
        layout = self.layout
        
        # Varoitus
        box = layout.box()
        box.label(text="🛡️ Safe Mode", icon='INFO')
        box.label(text="Yksinkertainen versio")
        
        layout.separator()
        
        # Toiminnot
        box = layout.box()
        box.label(text="Toiminnot:", icon='TOOL_SETTINGS')
        
        box.operator("midi.clear_animation_safe", icon='X')
        box.operator("midi.restore_lights_safe", icon='LIGHT_SUN')
        box.operator("midi.scan_lights_safe", icon='VIEWZOOM')
        box.operator("midi.create_test_lights_safe", icon='LIGHT')
        
        layout.separator()
        
        # Ohjeet
        box = layout.box()
        box.label(text="Ohjeet:", icon='QUESTION')
        box.label(text="1. Restore Lights = palauta näkyviksi")
        box.label(text="2. Scan Lights = listaa valot")
        box.label(text="3. Clear Animation = tyhjennä")
        box.label(text="4. Test Lights = luo värivaloja")

# ==========================================
# REGISTRATION
# ==========================================

classes = (
    MIDI_OT_clear_animation_safe,
    MIDI_OT_restore_lights_safe,
    MIDI_OT_scan_lights_safe,
    MIDI_OT_create_test_lights_safe,
    MIDI_PT_safe_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    print("🛡️ MIDI Light Controller (Safe) rekisteröity!")

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("🛡️ MIDI Light Controller (Safe) poistettu!")

if __name__ == "__main__":
    register()