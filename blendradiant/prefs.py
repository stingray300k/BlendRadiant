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
from collections import UserList

class CachedAvailableGamepacks(UserList):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loaded_for_radiant_path = None

    def ensure_loaded(self, context):
        prefs = context.preferences.addons[__package__].preferences
        radiant_path = prefs.radiant_path
        if self.loaded_for_radiant_path is None \
        or self.loaded_for_radiant_path != radiant_path:
            self.load_according_to_prefs(context=context)

    def load_according_to_prefs(self, context):
        prefs = context.preferences.addons[__package__].preferences
        l = []
        if prefs.radiant_path:
            l = self.load_from_radiant_path(prefs.radiant_path)
        self.data[:] = l

    def load_from_radiant_path(self, radiant_path):
        l = []
        gamepacks_path = Path(radiant_path)/"gamepacks"
        if gamepacks_path.exists():
            for gamepack_path in gamepacks_path.iterdir():
                if gamepack_path.name.endswith(".game"):
                  gamepack_name = gamepack_path.name[:-5]
                  l.append((gamepack_name, gamepack_name, ''))
        self.data[:] = l
        self.loaded_for_radiant_path = radiant_path
        return l


available_gamepacks = CachedAvailableGamepacks()
def get_available_gamepacks(self, context):
    # once again, make sure Python holds on to references
    # (I tried at least using a method instead of a function for this but
    # Blender won't have it, insists on function)
    global available_gamepacks
    available_gamepacks.ensure_loaded(context=context)
    return available_gamepacks


class BlendRadiantAddonPreferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    radiant_path: StringProperty(
        name="Path of (Gtk/Net)Radiant installation",
        subtype='FILE_PATH',
    )
    # TODO having this as an enum is actually wrong because they're saved as
    # ints, so whenever the directory changes it will mess up its meaning...
    # somehow only use enum for UI but save as str
    default_game: EnumProperty(
        name="Default game (gamepack)",
        items=get_available_gamepacks,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "radiant_path")
        layout.prop(self, "default_game")
