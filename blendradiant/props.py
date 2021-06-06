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

from bpy.props import StringProperty, FloatProperty, EnumProperty
from bpy.types import PropertyGroup


# XXX I guess these could be staticmethods in the property class below, if
# Blender doesn't go nuts over this

def on_update_mesh_as(self, context):
    obj = context.object
    if self.mesh_as == "ROOM_BRUSHES":
        if "BlendRadiantSolidifyPreview" not in obj.modifiers.keys():
            preview_mod = obj.modifiers.new(name="BlendRadiantSolidifyPreview",
                type="SOLIDIFY")
            preview_mod.offset = 1.0
        preview_mod.thickness = self.room_brush_thickness
    else:
        if "BlendRadiantSolidifyPreview" in obj.modifiers:
            preview_mod = obj.modifiers["BlendRadiantSolidifyPreview"]
            obj.modifiers.remove(preview_mod)


def on_update_room_brush_thickness(self, context):
    obj = context.object
    preview_mod = obj.modifiers["BlendRadiantSolidifyPreview"]
    preview_mod.thickness = self.room_brush_thickness


class BlendRadiantObjectProperties(PropertyGroup):
    mesh_as: EnumProperty(
        name="Mesh as",
        description="What to represent this mesh as in .map output",
        items=[
                ('NONE', "Nothing", ""),
                ('CONVEX_BRUSH', "Convex Brush", ""),
                ('ROOM_BRUSHES', "Room Brush(es)", ""),
                ('MODEL', "Model", ""),
            ],
        update=on_update_mesh_as
        )
    light_as: EnumProperty(
        name="Light as",
        description="What to represent this light as in .map output",
        items=[
                ('NONE', "Nothing", ""),
                ('LIGHT', "Light", ""),
            ]
        )
    room_brush_thickness: FloatProperty(
        name="Thickness",
        description="Thickness of Room Brush walls",
        default=0.1,
        update=on_update_room_brush_thickness,
    )
    entity_classname: StringProperty(
        name="Entity Classname",
    )

