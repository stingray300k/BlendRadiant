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


class MakeRoomOperator(bpy.types.Operator):
    '''(Gtk/Net)Radiant-like "Make Room"'''
    bl_idname = "mesh.make_room"
    bl_label = "Make Room"
    bl_options = {"REGISTER", "UNDO"}

    thickness: bpy.props.FloatProperty(name="Wall Thickness", default=0.2)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None \
        and context.active_object.type == "MESH" \
        and bpy.context.mode == "OBJECT"

    def execute(self, context):
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.edge_split(type="EDGE")
        bpy.ops.mesh.separate(type="LOOSE")
        bpy.ops.object.mode_set(mode='OBJECT')
        for obj in context.selected_objects:
            bpy.context.view_layer.objects.active = obj
            solidify_mod = context.active_object.modifiers.new(name="BlendRadiantSolidify", type="SOLIDIFY")
            solidify_mod.thickness = self.thickness
            solidify_mod.offset = 1.0
            bpy.ops.object.modifier_apply(modifier="BlendRadiantSolidify")
        return {'FINISHED'}

