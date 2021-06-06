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
from .entities import get_entity_classnames, get_entity_keys_for_current


# this is JUST to have a text field (= StringProperty prop) that can
# be filled in using a long searchable list! ridiculous, blender

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

# key-value list for entities
class UI_UL_Entity_Key_Value(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        slot = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(slot, "key", text="", emboss=False)
            layout.prop(slot, "value", text="", emboss=False)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class NewEntityKeyValuePairOperator(bpy.types.Operator):
    bl_idname = "object.new_entity_key_value_pair"
    bl_label = "Add New Entity Key-Value Pair"

    def execute(self, context):
        pair = context.active_object.blendradiant.entity_key_value_pairs.add()
        i = len(context.active_object.blendradiant.entity_key_value_pairs)-1
        context.active_object.blendradiant.entity_key_value_pairs_active_index = i
        pair.key = "KEY"
        pair.value = "VALUE"
        bpy.ops.object.search_entity_key("INVOKE_DEFAULT")
        return {'FINISHED'}

class SearchEntityKeyOperator(bpy.types.Operator):
    bl_idname = "object.search_entity_key"
    bl_label = "Search Entity Key"
    bl_property = "entity_key"

    entity_key: EnumProperty(
        name="Entity Key",
        items=get_entity_keys_for_current,
    )

    def execute(self, context):
        i = bpy.context.active_object.blendradiant.entity_key_value_pairs_active_index
        bpy.context.active_object.blendradiant.entity_key_value_pairs[i].key = self.entity_key
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}


class DeleteEntityKeyValuePairOperator(bpy.types.Operator):
    bl_idname = "object.delete_entity_key_value_pair"
    bl_label = "Delete Active Entity Key-Value Pair"

    def execute(self, context):
        i = context.active_object.blendradiant.entity_key_value_pairs_active_index
        context.active_object.blendradiant.entity_key_value_pairs.remove(i)
        if i > 0:
            context.active_object.blendradiant.entity_key_value_pairs_active_index -= 1
        return {'FINISHED'}

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

        if obj.blendradiant.entity_classname:
            row = layout.row()
            row.template_list("UI_UL_Entity_Key_Value", "",
                obj.blendradiant, "entity_key_value_pairs", obj.blendradiant,
                "entity_key_value_pairs_active_index")
            column = row.column()
            column.operator("object.new_entity_key_value_pair", text="",
                icon="ADD")
            column.operator("object.delete_entity_key_value_pair", text="",
                icon="REMOVE")
