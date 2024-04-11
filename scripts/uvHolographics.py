def printLogo():
    log('===========================================================================')
    log('               __  __      __                             __    _          ')
    log('  __  ___   __/ / / /___  / /___  ____ __________ _____  / /_  (_)_________')
    log(' / / / / | / / /_/ / __ \/ / __ \/ __ `/ ___/ __ `/ __ \/ __ \/ / ___/ ___/')
    log('/ /_/ /| |/ / __  / /_/ / / /_/ / /_/ / /  / /_/ / /_/ / / / / / /__(__  ) ')
    log('\__,_/ |___/_/ /_/\____/_/\____/\__, /_/   \__,_/ .___/_/ /_/_/\___/____/  ')
    log('                               /____/          /_/                         ')
    log('===========================================================================')

bl_info = {
    "name": "uvHolographics",
    "description": "",
    "author": "Raphael Vorias",
    "version": (0, 0, 8),
    "blender": (2, 80, 3),
    "location": "3D View > Tools",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}

# https://gist.github.com/p2or/2947b1aa89141caae182526a8fc2bc5a

import bpy

from bpy.props import (StringProperty,
                       CollectionProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )
from bpy.utils import (previews)

import numpy as np
from random import uniform, randint, choice
import random
import os

DEBUG = True
PATH_UVHOLOGRAPHICS_LOGO = 'logo.png'
TEXTURE_RESOLUTION = 4 # this will be multiplied by 1024
MAIN_OBJECT_NAME = 'Target'
TARGET_COLLECTION = 'annotation'

# global variable to store icons in
custom_icons = None

# ------------------------------------------------------------------------
#    Helper Functions
# ------------------------------------------------------------------------

def log(s):
    '''print a debug message'''
    
    if DEBUG:
        print(s)
        
        
def create_image(name, k=1):
    '''creates defect textures'''
    
    if name not in bpy.data.images:
        bpy.ops.image.new(name=name, width=k*1024, height=k*1024, color=(0.0,0.0,0.0,0.0))
        
    else:
        log('-  create_image() : textures exists')
             
                            
def create_view_layers(context):
    '''todo: checks naming of view layers'''
    
    context.scene.view_layers[0].name = 'real'
    if 'Ground Truth' not in context.scene.view_layers:
        context.scene.view_layers.new(name='ground_truth')


def create_mode_switcher_node_group():
    # https://blender.stackexchange.com/questions/5387/how-to-handle-creating-a-node-group-in-a-script
    # create a group
    
    if 'mode_switcher' not in bpy.data.node_groups:
        test_group = bpy.data.node_groups.new('mode_switcher', 'ShaderNodeTree')
        
        # create group inputs
        group_inputs = test_group.nodes.new('NodeGroupInput')
        group_inputs.location = (-350,0)
        test_group.inputs.new('NodeSocketShader','Real')
        test_group.inputs.new('NodeSocketColor','Ground Truth')

        # create group outputs
        group_outputs = test_group.nodes.new('NodeGroupOutput')
        group_outputs.location = (300,0)
        test_group.outputs.new('NodeSocketShader','Switch')

        # create three math nodes in a group
        node_mix = test_group.nodes.new('ShaderNodeMixShader')
        node_mix.location = (100,0)
        # adding mode driver
        # don't remove this, difficult to find
        modeDriver = bpy.data.node_groups['mode_switcher'].driver_add('nodes["Mix Shader"].inputs[0].default_value')
        modeDriver.driver.expression = 'mode'
        modeVariable = modeDriver.driver.variables.new()
        modeVariable.name = 'mode'
        modeVariable.type = 'SINGLE_PROP'
        modeVariable.targets[0].id_type = 'SCENE'
        modeVariable.targets[0].id = bpy.data.scenes['Scene']
        modeVariable.targets[0].data_path = 'uv_holographics.mode'

        # link inputs
        test_group.links.new(group_inputs.outputs['Real'], node_mix.inputs[1])
        test_group.links.new(group_inputs.outputs['Ground Truth'], node_mix.inputs[2])

        #link output
        test_group.links.new(node_mix.outputs[0], group_outputs.inputs['Switch'])
    else:
        log('-  create_mode_switcher_node_group() : node group already exists')

def create_scene_mode_switcher_node_group():
    if 'acolor_mode_switcher' not in bpy.data.node_groups:
        test_group = bpy.data.node_groups.new('color_mode_switcher', 'ShaderNodeTree')
        
        group_inputs = test_group.nodes.new('NodeGroupInput')
        group_inputs.location = (-350,0)
        test_group.inputs.new('NodeSocketColor', 'Color1')
        test_group.inputs.new('NodeSocketColor', 'Color2')
        
        group_outputs = test_group.nodes.new('NodeGroupOutput')
        group_outputs.location = (300,0)
        test_group.outputs.new('NodeSocketColor', 'Mixed Color')
        
        node_mix_rgb = test_group.nodes.new('ShaderNodeMixRGB')
        node_mix_rgb.location = (100,0)
        node_mix_rgb.name = "Mix"  # Explicitly name the node for reference

        # Assuming 'scene_mode' is a custom property on the scene,
        # ensure it exists:
        if not 'scene_mode' in bpy.data.scenes['Scene']:
            bpy.data.scenes['Scene']['scene_mode'] = 0.5  # Default value

        modeDriver = test_group.driver_add(f'nodes["{node_mix_rgb.name}"].inputs[0].default_value')
        modeDriver.driver.expression = 'scene_mode'
        modeVariable = modeDriver.driver.variables.new()
        modeVariable.name = 'scene_mode'  # Changed for clarity
        modeVariable.targets[0].id_type = 'SCENE'
        modeVariable.targets[0].id = bpy.data.scenes['Scene']
        modeVariable.targets[0].data_path = 'uv_holographics.scene_mode'
        
        test_group.links.new(group_inputs.outputs['Color1'], node_mix_rgb.inputs[1])
        test_group.links.new(group_inputs.outputs['Color2'], node_mix_rgb.inputs[2])
        test_group.links.new(node_mix_rgb.outputs[0], group_outputs.inputs['Mixed Color'])
    else:
        print('- create_scene_mode_switcher_node_group() : node group already exists')

def change_texture(context):
    """
    Replaces the file path of an existing image with a new one.
    If the new image is not already loaded, it will be loaded.
    """
    new_image_path = "//Grietas/defect0.png"
    old_image_name = "defect0.001" 
    
    # Try to get the new image if it's already loaded
    new_image = bpy.data.images.get(os.path.basename(new_image_path))
    
    # If not found, load the new image
    if not new_image:
        try:
            new_image = bpy.data.images.load(new_image_path)
        except RuntimeError as e:
            print(f"Failed to load image from '{new_image_path}': {e}")
            return

    # Find the old image by name
    old_image = bpy.data.images.get(old_image_name)
    
    # If the old image is found, replace its filepath and reload
    if old_image:
        old_image.filepath = new_image.filepath
        old_image.reload()
        print(f"Replaced and reloaded image '{old_image_name}' with '{new_image_path}'.")
    else:
        print(f"Image '{old_image_name}' not found.")


   
        
def add_camera_focus(context, cameraName, target):
    camera = context.scene.objects[cameraName]
    
    if 'Track To' not in camera.constraints:
        tracker = camera.constraints.new(type='TRACK_TO')
        tracker.target = target
        tracker.track_axis = 'TRACK_NEGATIVE_Z'
        tracker.up_axis = 'UP_Y'
    else:
        log('-  add_camera_focus() : camera constraint already exists')
        
        
def randomize_lights(context):
    '''Randomizes properties of lights in the scene or adds a new light if none exists.'''
    lights = [obj for obj in context.scene.objects if obj.type == 'LIGHT']
    
    if not lights:  # If no lights, create one
        bpy.ops.object.light_add(type='POINT', radius=10)
        light = context.active_object
        lights = [light]
    
    for light in lights:
        # Randomize location
        light.location = (uniform(-10, 10), uniform(-10, 10), uniform(5, 20))
        # Randomize color
        light.data.color = (uniform(0.5, 1), uniform(0.5, 1), uniform(0.5, 1))
        # Randomize energy with a bias for darker or lighter scenes
        energy_levels = [uniform(10, 50), uniform(500, 1000)]  # Lower values for darker, higher for brighter
        light.data.energy = choice(energy_levels)  
  
def adjust_hdri_lighting(context):
    '''Adjusts HDRI lighting strength and rotation for varied lighting effects.'''
    # Check if there is an environment texture
    if context.scene.world and context.scene.world.node_tree:
        world_nodes = context.scene.world.node_tree.nodes
        env_texture_node = next((node for node in world_nodes if node.type == 'TEX_ENVIRONMENT'), None)
        
        if env_texture_node:
            # Find the Background node connected to the World Output
            background_node = next((node for node in world_nodes if node.type == 'BACKGROUND'), None)
            
            if background_node:
                # Adjust the HDRI strength to make the lighting darker or lighter
                background_node.inputs['Strength'].default_value = uniform(0.1, 2)  # Adjust this range as needed
                
                # Optional: Rotate the HDRI for different lighting directions
                # Find the mapping node connected to the environment texture
                mapping_node = next((node for node in world_nodes if node.type == 'MAPPING'), None)
                if mapping_node:
                    # Randomly adjust Z rotation for varied lighting directions
                    mapping_node.inputs['Rotation'].default_value[2] = uniform(0, 6.28319)  # 0 to 2*pi radians
                
                print("HDRI lighting adjusted.")
            else:
                print("No background node found.")
        else:
            print("No environment texture node found.")
    else:
        print("World or node tree not found.")
 
def alternate_camera_parameters(context):
    '''Randomly alternates camera focal length and switches between perspective/orthographic modes.'''
    # Ensure there is an active camera object in the scene
    if context.scene.camera and context.scene.camera.data.type == 'CAMERA':
        cam_data = context.scene.camera.data
        
        # Randomly adjust the focal length within a range, for example, between 24mm and 85mm
        cam_data.lens = uniform(24, 85)
        
        # Example of switching between 'PERSP' (perspective) and 'ORTHO' (orthographic) modes
        # This can be commented out or adjusted as per requirements
        if cam_data.lens_unit == 'MILLIMETERS':  # If currently in perspective mode
            cam_data.lens_unit = 'FOV'  # Switch to orthographic by changing the lens unit to FOV
        else:
            cam_data.lens_unit = 'MILLIMETERS'  # Otherwise, switch back to perspective
        
        print(f"Camera focal length adjusted to {cam_data.lens}mm.")
        print(f"Camera mode switched to {'Orthographic' if cam_data.lens_unit == 'FOV' else 'Perspective'}.")
    else:
        print("Active camera not found or not a camera object.")     
            
def toggle_mode(context):
    '''helper function for background switching'''
    
    scene = context.scene
    uvh = scene.uv_holographics
            
    if uvh.mode == 0:
        log("switching to GT")
#        context.window.view_layer = scene.view_layers['ground_truth']
        uvh.mode = 1
        scene.render.filter_size = 0
        scene.view_settings.view_transform = 'Standard'
    else:
        log("switching to realistic")
#        context.window.view_layer = scene.view_layers['real']
        uvh.mode = 0
        scene.render.filter_size = 1.5
        scene.view_settings.view_transform = 'Filmic'
                
    # hack to update driver dependencies
    bpy.data.node_groups["mode_switcher"].animation_data.drivers[0].driver.expression = 'mode'
    
    
            
def render_layer(context,layer,id):
    '''
    Renders a specific layer, useful for compositing view.
    This function is mode agnostic.
    '''
    
    scene = context.scene
    uvh = scene.uv_holographics
#    context.window.view_layer = scene.view_layers[layer]
    
    scene.render.filepath = f'{uvh.output_dir}{layer}/{id:04d}.png'
    bpy.ops.render.render(write_still=True,layer=layer)
    
def run_variation(context):
    '''
    manipulates objects to create variations
    todo: scenarios
    todo: read from XML file
    '''
    
    # assume one camera
    camera = context.scene.objects['Camera']
    uvh = context.scene.uv_holographics
    
    uvh.scene_mode = random.randint(0, 1)

        
    # hack to update driver dependencies
    bpy.data.node_groups["color_mode_switcher"].animation_data.drivers[0].driver.expression = 'scene_mode'
    
    # we assume a perimeter to sample our camera locations from
    r = uvh.camera_dist_mean + uniform(-uvh.camera_dist_var,uvh.camera_dist_var)
    theta = np.pi/2 + uniform(-np.pi/4,np.pi/8)
    phi = uniform(0,2*np.pi)
    
    # create parameter
    randX = r*np.sin(theta)*np.cos(phi)
    randY = r*np.sin(theta)*np.sin(phi)
    randZ = r*np.cos(theta)
    
    camera.location = (randX, randY, randZ)
    
    # object variations
    
    # Randomize lights
    adjust_hdri_lighting(context)
    
    alternate_camera_parameters(context)
    change_texture(context)
    

def insert_mode_switcher_node(context,material):
    '''Inserts a mode_switcher group node in the materials that are in target_collection'''
    
    log(f"checking for {material.name}")
    for l in material.node_tree.links:
        if l.to_socket.name == "Surface":
            if l.from_socket.name == "Switch":
                log("-  mode_switcher already inserted")
            else:
                log("found end link, operating ..")
                open_node_pre = l.from_node
                open_node_post = l.to_node
                material.node_tree.links.remove(l)
                group = material.node_tree.nodes.new(type="ShaderNodeGroup",)
                group.node_tree = bpy.data.node_groups["mode_switcher"]
                material.node_tree.links.new(open_node_pre.outputs[0], group.inputs[0])
                material.node_tree.links.new(group.outputs[0], open_node_post.inputs[0])
            log("[[done]]")
                
# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class MyProperties(PropertyGroup):
    separate_background: BoolProperty(
        name="Separate background class",
        description="Extra class for background",
        default = True
        )

    n_defects: IntProperty(
        name ="Defect classes",
        description="Number of defect classes",
        default = 1,
        min = 1,
        max = 10
        )
        
    n_samples: IntProperty(
        name ="Number of samples",
        description="Number of samples to generate",
        default = 1,
        min = 1,
        max = 100000
        )
        
    target_object: PointerProperty(
        type =bpy.types.Object
        )
        
    target_collection: PointerProperty(
        type =bpy.types.Collection
        )

    output_dir: StringProperty(
        name = "Output folder",
        description="Choose a directory:",
        default="../output/",
        maxlen=1024,
        subtype='DIR_PATH'
        )
        
    mode: IntProperty(
        name ="Visualization mode",
        description="Realistic/Ground truth",
        default = 0,
        min = 0,
        max = 1
        )
        
    scene_mode: IntProperty(
        name ="Scene Visualization mode",
        description="Color Mode for the Scene",
        default = 0,
        min = 0,
        max = 1
    )
        
    generate_real_only: BoolProperty(
        name="Generate real only",
        description="",
        default = False
        )
    
    # Camera
    #-------------------------------
    min_camera_angle: FloatProperty(
        name = "Min camera angle",
        default = 0.,
        min = 0.,
        max = 1.,
        )
    max_camera_angle: FloatProperty(
        name = "Max camera angle",
        default = 1.,
        min = 0.,
        max = 1.,
        )
    camera_dist_mean: FloatProperty(
        name = "Camera dist mean",
        default = 5.,
        min = 0.,
        max = 10.,
        )
    camera_dist_var: FloatProperty(
        name = "Camera dist var",
        default = 1.,
        min = 0.,
        max = 4.,
        )
     #-------------------------------

# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------
          
class WM_OT_GenerateComponents(Operator):
    '''Generate blank texture maps and view layers'''
    
    bl_label = "Generate components"
    bl_idname = "wm.gen_components"
    
    def execute(self, context):
        scene = context.scene
        uvh = scene.uv_holographics
        
        log('-  generating components')
        # create blank textures
        for i in range(uvh.n_defects):
            create_image(name=f"defect{i}",k=2)
            
        create_view_layers(context)
        create_mode_switcher_node_group()
        create_scene_mode_switcher_node_group()
        add_camera_focus(context,'Camera',uvh.target_object) # updates viewport
        log('[[done]]')
        
        return {'FINISHED'}
                

class WM_OT_UpdateMaterials(Operator):
    '''Updates existing material nodes of objects in target_collection'''
    
    bl_label = "Update Materials"
    bl_idname = "wm.update_materials"
    
    def execute(self, context):
        
        for o in context.scene.uv_holographics.target_collection.objects:        
            for m in o.data.materials:
                insert_mode_switcher_node(context,m)
        
        return {'FINISHED'}
      
      
class WM_OT_ToggleMaterials(Operator):
    '''Toggle between realistic view and ground truth'''
    
    bl_label = "Toggle Real/GT"
    bl_idname = "wm.toggle_real_gt"
    
    def execute(self, context):
        toggle_mode(context)
        
        return {'FINISHED'}
    
    
class WM_OT_SampleVariation(Operator):
    '''Runs a sample variation'''
    
    bl_label = "Sample variation"
    bl_idname = "wm.sample_variation"
    
    def execute(self, context):
        run_variation(context)
        
        return {'FINISHED'}
            
            
class WM_OT_StartScenarios(Operator):
    '''Vary camera positions'''
    
    bl_label = "Generate"
    bl_idname = "wm.start_scenarios"
    
    def execute(self, context):
        scene = context.scene
        uvh = scene.uv_holographics
        
        # make sure to start in realistic mode
        if uvh.mode != 0:
            toggle_mode(context)
        
        for i in range(uvh.n_samples):
            run_variation(context)              
            render_layer(context, 'real', i+1)
            if not uvh.generate_real_only:
                toggle_mode(context)
                render_layer(context, 'ground_truth', i+1)
                toggle_mode(context)
            
        # switch back to real scene
#        context.window.view_layer = scene.view_layers['real']
        log('[[done]]')
        
        return {'FINISHED'}


# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class OBJECT_PT_CustomPanel(Panel):
    bl_label = "uvHolographics"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Annotation"
    bl_context = "objectmode"
    
    @classmethod
    def poll(self,context):
        return context.object is not None
    
    
    def draw_header(self,context):
        global custom_icons
        self.layout.label(text="",icon_value=custom_icons["custom_icon"].icon_id)


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        uvh = scene.uv_holographics
        
        layout.label(text='Setup')
        box = layout.box()
        box.prop(uvh, "separate_background")  
        box.prop(uvh, "n_defects")
        box.prop(uvh, "target_object")
        box.operator("wm.gen_components")
        box.prop(uvh, "target_collection")
        box.operator("wm.update_materials")
        
        layout.label(text='Camera parameters')
        box = layout.box()
        box.prop(uvh,"min_camera_angle", slider=True)
        box.prop(uvh,"max_camera_angle", slider=True)
        box.prop(uvh,"camera_dist_mean", slider=True)
        box.prop(uvh,"camera_dist_var", slider=True)
        
        layout.label(text='Operations')
        box = layout.box()
        box.operator("wm.toggle_real_gt")
        box.operator("wm.sample_variation")
        
        layout.label(text='Generation')
        box = layout.box()
        box.prop(uvh, "generate_real_only")
        box.prop(uvh, "n_samples")
        box.prop(uvh, "output_dir")
        box.operator("wm.start_scenarios")
        box.separator()

#class OBJECT_PT_LabelColorSubPanel(Panel):
#    bl_label = "Class definitions"
#    bl_idname = "OBJECT_PT_label_color_sub_panel"
#    bl_parent_id = "OBJECT_PT_custom_panel"
#    bl_space_type = "VIEW_3D"   
#    bl_region_type = "UI"
#    bl_category = "Annotation"
#    bl_context = "objectmode"
#    
#    @classmethod
#    def poll(self,context):
#        return context.object is not None
#    
#    def draw(self, context):pass
#    def draw_header(self, context):
#        layout = self.layout
#        scene = context.scene
#        uvh = scene.uv_holographics

# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    MyProperties,
    WM_OT_GenerateComponents,
    WM_OT_UpdateMaterials,
    WM_OT_ToggleMaterials,
    WM_OT_SampleVariation,
    WM_OT_StartScenarios,
    OBJECT_PT_CustomPanel
)


def register():
    from bpy.utils import register_class
    
    global custom_icons
    
    printLogo()
    
    for cls in classes:
        register_class(cls)
        
    # https://blender.stackexchange.com/questions/32335/how-to-implement-custom-icons-for-my-script-addon
    custom_icons = bpy.utils.previews.new()
    script_path = bpy.context.space_data.text.filepath
    icons_dir = os.path.join(os.path.dirname(script_path), "icons")
    custom_icons.load("custom_icon", os.path.join(icons_dir, "logo.png"), 'IMAGE')
        
    bpy.types.Scene.uv_holographics = PointerProperty(type=MyProperties)


def unregister():
    from bpy.utils import unregister_class
    
    global custom_icons
    
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.uv_holographics
    
    bpy.utils.previews.remove(custom_icons)

if __name__ == "__main__":
    register()
#    unregister()