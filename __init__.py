bl_info = {
    "name": "N-Body Simulation",
    "description": "A Simple N-Body-Simulation Tool",
    "author": "Mantelmann",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "3D View > Create",
    "category": "Animation",
    "wiki": "https://github.com/Mantelmann/N_Bodies_Blender"
}


import bpy
import math

from bpy.props import (StringProperty,
                       IntProperty,
                       FloatProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )

#Wrapper Function
def prepareWrappers(self, context):
    
    nbcollection = bpy.data.collections[get_collection(self, context)]

    for num, currentObject in enumerate(context.selected_objects):
        
        #Create Wrapper Empty
        bpy.ops.object.empty_add(type='SPHERE', location=list(currentObject.location))
        wrapperEmpty = context.active_object
        context.active_object.name = 'WrapperEmpty' + str(num)
        
        #Scale Wrapper appropriately
        wrapperRadius = (((currentObject.dimensions.x/2)+(currentObject.dimensions.y/2)+(currentObject.dimensions.z/2))**3)**(1/3)
        wrapperEmpty.scale = wrapperEmpty.scale * (wrapperRadius)/math.sqrt(3)
        bpy.ops.object.transform_apply(location = False, scale = True, rotation = False)

        currentObject.parent = wrapperEmpty
        currentObject.location = [0,0,0]
        
        #Create Custom Property
        wrapperEmpty["Mass"] = wrapperRadius
        wrapperEmpty["Fixpoint"] = False

        #Create Curve
        bpy.ops.curve.primitive_nurbs_path_add(location=[0,0,0])
        curve = context.active_object
        context.active_object.name = 'VelocityVector' + str(num)
        #Cut down Curve
        for vertex in [2,4]:
            curve.data.splines[0].points[vertex].select = False
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.dissolve_verts()
        bpy.ops.object.mode_set(mode='OBJECT')

        #Add Arrow at Curve Head
        bpy.ops.object.empty_add(type='SINGLE_ARROW', location = [2,0,0])
        arrow = context.active_object
        context.active_object.name = 'VelocityArrow' + str(num)

        #Make Arrow Track to Empty
        arrow.constraints.new(type='TRACK_TO')
        print(arrow.constraints)
        arrow.constraints[0].target = wrapperEmpty
        arrow.constraints[0].up_axis = 'UP_X'
        arrow.constraints[0].track_axis = 'TRACK_NEGATIVE_Z'
        arrow.select_set(False)


        #Select curve, Create Hook Modifier, Hook Index 1 to Arrow
        curve.modifiers.new("Hook To Arrow", type='HOOK')
        curve.modifiers['Hook To Arrow'].vertex_indices_set([1])
        curve.modifiers['Hook To Arrow'].object = arrow

        arrow.parent = wrapperEmpty
        curve.parent = wrapperEmpty
        arrow.location = [0,0,0]
        
        #move relevant objects into nbCollection
        for tempobject in [wrapperEmpty, curve, arrow]:
            for old_coll in tempobject.users_collection:
                old_coll.objects.unlink(tempobject)
            nbcollection.objects.link(tempobject)

#Collection Creator
def get_collection(self, context):
    name = context.scene.n_body_sim.collection_Name
    
    if name == "":
        raise Exception("Please Name your collection")
    
    if name in bpy.data.collections:
        print("already exists")
        return name
    else:
        new_collection = bpy.data.collections.new(name)
        context.scene.collection.children.link(new_collection)
        print("new collection")
        return name

def get_vectors(self, context, wrappers):

    relevant_wrappers = []
    relevant_velarrows = []

    #Go through every object in the collection
    for wrapper in wrappers:
        
        found_arrow = None
        
        #Check if Object really is a Wrapper
        if wrapper.name[0:12] == "WrapperEmpty":
        
            relevant_wrappers.append(wrapper)
            print("Registered " + wrapper.name)
        
            for children in wrapper.children:
                if children.name == "VelocityArrow" + wrapper.name[12:]:
                    found_arrow = children
                    break
            if found_arrow == None:
                raise Exception("Missing Velocity Arrow. Please check whether every wrapper has a velocity Arrow and generate a new one if needed.")
            else:
                relevant_velarrows.append(found_arrow)

    return relevant_wrappers, relevant_velarrows

# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class nbProperties(PropertyGroup):

    gravity_Constant: bpy.props.FloatProperty(
        name = "Gravity Constant",
        description = "Change the Gravity Constant",
        default = 6.674, 
        soft_min = 0.0,
        soft_max = 10.0
    ) 

    velocity_Factor: bpy.props.FloatProperty(
        name = "Velocity Factor",
        description = "Multiplier for Velocity",
        default = 1.0, 
        min = 0.001,
        max = 10.0
    )
    
    frame_start: bpy.props.IntProperty(
        name = "Start Frame",
        description = "Which Frame shall the Simulation Start",
        default = 0, 
        min = 0
    )
    
    frame_end: bpy.props.IntProperty(
        name = "End Frame",
        description = "Which Frame shall the Simulation End",
        default = 250, 
        min = 1,
    )

    keyframe_Stepsize: bpy.props.IntProperty(
        name = "Keyframe Stepsize",
        description = "Every nth Keyframe will be set",
        default = 1, 
        min = 1,
        soft_max = 20
    )
    
    collection_Name: bpy.props.StringProperty(
        name = "Collection",
        description = "Collection to store N-Body Objects in",
        #get = get_collection(),
        default = "N_Bodies",
    )


# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class WM_OT_prepare_wrappers(Operator):
    bl_label = "Prepare Wrapper Objects"
    bl_description = "Generate Wrappers for every selected Object and put them into the Collection"
    bl_info = "Give Every Selected Object Wrapper Empties"
    bl_idname = "wm.prepare_wrappers"

    def execute(self, context):
        scene = context.scene
        nb_sim = scene.n_body_sim

        # print the values to the console
        prepareWrappers(self,context)
        print("Prepared Wrappers")

        return {'FINISHED'}


   
class WM_OT_remove_wrappers(Operator):
    bl_label = "Remove Wrapper Objects"
    bl_description = "Remove every selecteed Wrapper"
    bl_info = "Remove every selected Wrapper Object"
    bl_idname = "wm.remove_wrappers"
    
    def execute(self, context):
        scene = context.scene
        nb_sim = scene.n_body_sim
        
        to_delete = []
        
        for wrapper in context.selected_objects:
            
            #Check if selected object truly is Wrapper
            if wrapper.name[0:12] == "WrapperEmpty":
                #Go through children and delete Velocity Vector and Arrow
                for children in wrapper.children:
                    matrixcopy = children.matrix_world.copy()
                    children.parent = None
                    children.matrix_world = matrixcopy
                    if children.name == "VelocityArrow" + wrapper.name[12:] or children.name == "VelocityVector" + wrapper.name[12:]:
                       to_delete.append(children)
            else:
                wrapper.select_set(False)
        
        to_delete = to_delete + context.selected_objects
        
        for obj in to_delete:
            obj.select_set(True)
        bpy.ops.object.delete()
            
                                           


        
        return {'FINISHED'}
    
class WM_OT_remove_keyframes(Operator):
    bl_label = "Clear Keyframes"
    bl_description = "Remove the Keyframes from all Wrappers in the Collection"
    bl_info = "Clear every Keyframe of the Wrapper Objects"
    bl_idname = "wm.remove_keyframes"
    
    
    def execute(self, context):
        scene = context.scene
        nb_sim = scene.n_body_sim
        wrappers = bpy.data.collections[get_collection(self, context)].objects
        
        relevant_wrappers, relevant_velarrows = get_vectors(self, context, wrappers)
        
        print(relevant_wrappers, relevant_velarrows)
        
        for obj in relevant_wrappers:
            obj.animation_data_clear()
        
        for obj in relevant_velarrows:
            obj.animation_data_clear()
        
        return {'FINISHED'}
    
        
class WM_OT_calculate_keyframes(Operator):
    bl_label = "Calculate!"
    bl_description = "Bake Keyframes for al Wrappers in the Collection"
    bl_info = "Calculate Keyframes for every wrapperObject in the selected colelction"
    bl_idname = "wm.calculate_keyframes"

    def execute(self, context):
        scene = context.scene
        nb_sim = scene.n_body_sim
        wrappers = bpy.data.collections[get_collection(self, context)].objects

        relevant_wrappers, relevant_velarrows = get_vectors(self, context, wrappers)
        
        print(relevant_wrappers)
        print(relevant_velarrows)
        
        #Go through all Frames
        for frame in range(nb_sim.frame_start, nb_sim.frame_end+1):
            
            #Go through every Object
            for obj, vel in zip(relevant_wrappers, relevant_velarrows):
                
                #Set Keyframes
                if frame % nb_sim.keyframe_Stepsize == 0:
                    obj.keyframe_insert(data_path="location", frame=frame)
                    vel.keyframe_insert(data_path="location", frame=frame)
                
                #Calculate gravity for every other object
                for other_object in relevant_wrappers:
                    
                    if obj == other_object:
                        pass
                    else:    
                        sep_x = obj.location.x - other_object.location.x
                        sep_y = obj.location.y - other_object.location.y
                        sep_z = obj.location.z - other_object.location.z
                        
                        radius = sep_x**2 + sep_y**2 + sep_z**2
                        
                        force = nb_sim.gravity_Constant * obj['Mass'] * other_object['Mass'] / radius
                        
                        vel.location.x -= force * sep_x
                        vel.location.y -= force * sep_y
                        vel.location.z -= force * sep_z
                        
                        
                if obj['Fixpoint'] == False:
                    #Apply Velocity
                    obj.location.x += nb_sim.velocity_Factor * vel.location.x / obj['Mass']
                    obj.location.y += nb_sim.velocity_Factor * vel.location.y / obj['Mass']
                    obj.location.z += nb_sim.velocity_Factor * vel.location.z / obj['Mass']
                            

        return {'FINISHED'}


# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class OBJECT_PT_CustomPanel(Panel):
    bl_label = "N-Body Simulation"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Create"
    bl_context = "objectmode"

    @classmethod
    def poll(self,context):
        return True

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        nb_sim = scene.n_body_sim
        layout.prop(nb_sim, "gravity_Constant")
        #layout.prop(nb_sim, "velocity_Factor")
        layout.separator()
        layout.prop(nb_sim, "collection_Name")
        layout.separator()
        layout.prop(nb_sim, "keyframe_Stepsize")
        layout.prop(nb_sim, "frame_start")
        layout.prop(nb_sim, "frame_end")
        layout.separator()
        layout.operator("wm.prepare_wrappers")
        layout.operator("wm.remove_wrappers")
        layout.separator()
        layout.operator("wm.calculate_keyframes")
        layout.operator("wm.remove_keyframes")
        layout.separator()

# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    nbProperties,
    WM_OT_prepare_wrappers,
    WM_OT_calculate_keyframes,
    WM_OT_remove_wrappers,
    WM_OT_remove_keyframes,
    OBJECT_PT_CustomPanel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.n_body_sim = PointerProperty(type=nbProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.n_body_sim
    

if __name__ == "__main__":
    register()
