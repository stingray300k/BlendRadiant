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

