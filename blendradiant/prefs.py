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
