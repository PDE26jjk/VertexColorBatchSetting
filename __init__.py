bl_info = {
    "name": "VertexColorBatchSetting",
    "category": "Object",
    "location": "View3D > Sidebar > Edit",
    "description": "Set Vertex Color on selected element",
    "author": "PDE26jjk",
    "version": (1, 0, 1),
    "blender": (3, 4, 0),
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": ""
}

import bpy
import mathutils
import bpy.utils.previews
from bpy.types import Panel, Operator
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, IntProperty, StringProperty, CollectionProperty, FloatProperty, EnumProperty, PointerProperty
from random import uniform
import bmesh

def color_to_faces(color):
    context = bpy.context
    mesh = context.edit_object.data

    bm = bmesh.from_edit_mesh(mesh)
    color_layer = bm.loops.layers.color.active
    if not color_layer:
        color_layer = bm.loops.layers.color.new('Col')
    selfaces = [f for f in bm.faces if f.select]
    for face in selfaces:
        for loop in face.loops:
            loop[color_layer] = color
    bmesh.update_edit_mesh(mesh)

def color_to_vertices(color):
    mesh = bpy.context.edit_object.data
    bm = bmesh.from_edit_mesh(mesh)
    color_layer = bm.loops.layers.color.active
    if not color_layer:
        color_layer = bm.loops.layers.color.new('Col')
    selverts = [v for v in bm.verts if v.select]
    for vert in selverts:
        for loop in vert.link_loops:
            loop[color_layer] = color
    bmesh.update_edit_mesh(mesh)
    return

def get_color_from_faces():
    context = bpy.context
    mesh = context.edit_object.data
    bm = bmesh.from_edit_mesh(mesh)
    color_layer = bm.loops.layers.color.active
    if not color_layer:
        color_layer = bm.loops.layers.color.new('Col')
    selfaces = [f for f in bm.faces if f.select]
    colorSum = mathutils.Vector((0,0,0,0))
    if len(selfaces) == 0: return colorSum
    i = 0
    for face in selfaces:
        for loop in face.loops:
            colorSum+=loop[color_layer]
            i+=1
            
    bmesh.update_edit_mesh(mesh)
    return colorSum / i
    
def get_color_from_vertices():
    mesh = bpy.context.edit_object.data
    bm = bmesh.from_edit_mesh(mesh)
    color_layer = bm.loops.layers.color.active
    if not color_layer:
        color_layer = bm.loops.layers.color.new('Col')
    selverts = [v for v in bm.verts if v.select]
    i = 0
    colorSum = mathutils.Vector((0,0,0,0))
    for vert in selverts:
        for loop in vert.link_loops:
            colorSum+=loop[color_layer]
            i+=1
    # bmesh.update_edit_mesh(mesh)
    
    # bm.free()
    return colorSum / i


previews = {}
def getColorPreview(color):
    name = 'ColorIcon'
    for i in range(3):
        c = color[i]
        if isinstance(c,float):
            c = int(255 * c)
        name+='_'+str(c)
    pcoll = previews["main"]
    colorWithA = [color[0],color[1],color[2],1]
    if not pcoll.get(name):
        size = (32,32)
        icon = pcoll.new(name) # name has to be unique!
        icon.icon_size = size
        icon.is_icon_custom = True
        icon.icon_pixels_float = [*colorWithA] * size[0] * size[1]
    #print(*color,name)
    return pcoll[name]

class VertexColorTool_PT_Panel(Panel):
    bl_label = "Vertex Color Batch Setting"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Edit'
    bl_context = "mesh_edit"

    def draw(self, context):
        layout = self.layout
        prop = getProp(context)
        
        # layout.operator("vct.init", text="init")
        layout.template_ID(prop,'palette',new="palette.new")
        palette = prop.palette
        
        if not palette : return
        #print(palette.colors.active)
        #grid = layout.grid_flow(row_major=True)
        col = layout.column(align=True)
        row = col.row(align=True)
        num_cols = max(1,(context.region.width) // 32)
        for idx, item in enumerate(palette.colors):
            icon_id = getColorPreview(item.color).icon_id
            row.operator("vct.select_color", icon_value=icon_id,text='',emboss=False).index = idx

            if (idx+1) % num_cols == 0:
                row = col.row(align=True)
        col = layout.column(align=True)
        col.prop(prop, "color", text="Color")
        col.prop(prop, "alpha", text="Alpha",slider=True)
        # layout.template_palette(prop, "palette",color=True)
        # if active_item:
        #     row = layout.row()
        
        r, g, b, a = *prop.color,prop.alpha
        col.label(text=f"Color Value: {r:.3f} {g:.3f} {b:.3f} {a:.3f}") 
        # row = layout.row()
        
        #row.prop(context.scene, "mytool_color", text="Vexter Color")
        col = layout.column()
        row = col.row()
        row.operator("vct.set_vertex_color", text="Set Vertex Color")
        row.operator("vct.get_vertex_color", text="Get Vertex Color")
        
        col.separator(factor=0.5)
        col.prop(prop, "gamma_correction", text="Gamma correction")

    
class SelectColorOperator(Operator):
    bl_idname = "vct.select_color"
    bl_label = "select color"
    bl_description = "Select color from palette"
    bl_options = {'UNDO'}
    
    colorValue: bpy.props.FloatVectorProperty()
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        prop = getProp(context)
        index = self.index
        palette = prop.palette
        if index and index >= 0 and index <= len(palette.colors):
            prop.color = palette.colors[index].color
            print(palette.colors[index].color)
        return {'FINISHED'}
    
class SetColorOperator(Operator):
    bl_idname = "vct.set_vertex_color"
    bl_label = "_"
    bl_options = {'UNDO'}

    def execute(self, context):
        prop = getProp(context)
        clr = (*prop.color,prop.alpha)
        if prop.gamma_correction:
            clr = (prop.color[0]**2.2,prop.color[1]**2.2,prop.color[2]**2.2,prop.alpha)
        if bpy.context.scene.tool_settings.mesh_select_mode[2]:
            color_to_faces(clr)
        else:
            color_to_vertices(clr)
        return {'FINISHED'}

class GetColorOperator(Operator):
    bl_idname = "vct.get_vertex_color"
    bl_label = "get vertex color"
    bl_description = "get average vertex color at points"
    bl_options = {'UNDO'}

    def execute(self, context):
        prop = getProp(context)
        if bpy.context.scene.tool_settings.mesh_select_mode[2]:
            color = get_color_from_faces()
        else: 
            color = get_color_from_vertices()
        if prop.gamma_correction:
            factor = 1/2.2
            prop.color = (color[0]**factor,color[1]**factor,color[2]**factor)
        else:
            prop.color = color.xyz
        prop.alpha = color.w
        return {'FINISHED'}

class VertexColorToolProp(PropertyGroup):
    palette: bpy.props.PointerProperty(type=bpy.types.Palette)
    color: bpy.props.FloatVectorProperty(
                                        subtype = "COLOR",
                                        size=3,
                                        min=0.0, max=1.0)
    alpha: bpy.props.FloatProperty(min= 0,max=1)
    gamma_correction: bpy.props.BoolProperty(name= "gamma correction",
                                            default=False,
                                            description="apply gamma correction when set and get color."
                                            )
    
def getProp(context = bpy.context):
    return context.scene.vertexColorTool_prop


classList = [
    VertexColorTool_PT_Panel,
    SetColorOperator,
    VertexColorToolProp,
    SelectColorOperator,
    GetColorOperator
]

def register():
    # register the classes
    for c in classList:
        bpy.utils.register_class(c)
    pcoll = bpy.utils.previews.new()
    pcoll.icon_gallery = ()
    previews["main"] = pcoll
    bpy.types.Scene.vertexColorTool_prop = PointerProperty(type=VertexColorToolProp)
    

def unregister():
    for c in classList:
        bpy.utils.unregister_class(c)
    
    for pcoll in previews.values():
        bpy.utils.previews.remove(pcoll)
    previews.clear()
    del bpy.types.Scene.vertexColorTool_prop

if __name__ == "__main__":
    register()
