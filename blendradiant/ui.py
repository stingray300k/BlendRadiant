# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.props import EnumProperty


# this is JUST to have a text field (= StringProperty prop) that can
# be filled in using a long searchable list! ridiculous, blender

entity_classnames = [] # ensure Python keeps refs, cf warning in EnumProperty docs
def get_entity_classnames(self, context):
    global entity_classnames
    entity_classnames = [
        ("worldspawn", "worldspawn", ""),
        ("info_player_deathmatch", "info_player_deathmatch", ""),
    ]
    return entity_classnames

class SearchEntityClassnamesOperator(bpy.types.Operator):
    bl_idname = "object.search_entity_classnames"
    bl_label = "Search Entity Classnames"
    bl_property = "entity_classname"

    entity_classname: EnumProperty(
        name="Entity Classname",
        items=get_entity_classnames,
    )

    def execute(self, context):
        bpy.context.active_object.blendradiant.entity_classname = self.entity_classname
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}


# actual main properties panel

class BlendRadiantObjectPropertiesPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_blendradiant"
    bl_label = "BlendRadiant"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        if obj.type == "MESH":
            layout.prop(obj.blendradiant, "mesh_as")
            if obj.blendradiant.mesh_as == "ROOM_BRUSHES":
                layout.prop(obj.blendradiant, "room_brush_thickness")
        elif obj.type == "LIGHT":
            layout.prop(obj.blendradiant, "light_as")

        row = layout.row()
        row.prop(obj.blendradiant, "entity_classname")
        row.operator("object.search_entity_classnames", text="", icon="VIEWZOOM")

