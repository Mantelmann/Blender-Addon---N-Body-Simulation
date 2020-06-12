import N_Body_Blender
import bpy

print("Test")
bl_info = {
    "name": "N-Body Simulation",
    "description": "A Simple N-Body-Simulation Tool",
    "author": "Mantelmann",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "3D View > Create",
    "category": "Animation",
    "internet": "https://github.com/Mantelmann/Blender-Addon---N-Body-Simulation"
}

classes = (
    N_Body_Blender.nbProperties,
    N_Body_Blender.WM_OT_prepare_wrappers,
    N_Body_Blender.WM_OT_calculate_keyframes,
    N_Body_Blender.WM_OT_remove_wrappers,
    N_Body_Blender.WM_OT_remove_keyframes,
    N_Body_Blender.OBJECT_PT_CustomPanel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.n_body_sim = PointerProperty(type=N_Body_Blender.nbProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.n_body_sim
