import bpy
from bpy.props import StringProperty, EnumProperty
from pathlib import Path

available_gamepacks = []
def get_available_gamepacks(self, context):
  # once again, make sure Python holds on to references
  global available_gamepacks
  # /
  l = []
  prefs = context.preferences.addons[__package__].preferences
  if prefs.radiant_path:
    gamepacks_path = Path(prefs.radiant_path)/"gamepacks"
    if gamepacks_path.exists():
      for gamepack_path in gamepacks_path.iterdir():
        if gamepack_path.name.endswith(".game"):
          gamepack_name = gamepack_path.name[:-5]
          l.append((gamepack_name, gamepack_name, ''))
  available_gamepacks[:] = l
  return available_gamepacks


class BlendRadiantAddonPreferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    radiant_path: StringProperty(
        name="Path of (Gtk/Net)Radiant installation",
        subtype='FILE_PATH',
    )
    default_game: EnumProperty(
        name="Default game (gamepack)",
        items=get_available_gamepacks,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "radiant_path")
        layout.prop(self, "default_game")
