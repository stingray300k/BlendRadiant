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
from .export import ExportQuakeMap, menu_func_export
from .ui import BlendRadiantObjectPropertiesPanel, \
  SearchEntityClassnamesOperator
from .mesh import MakeRoomOperator
from .props import BlendRadiantObjectProperties
from .prefs import BlendRadiantAddonPreferences

bl_info = {
    "name": "BlendRadiant",
    "author": "chedap, stingray300k",
    "version": (2021, 6, 4),
    "blender": (2, 91, 0),
    "location": "File > Export",
    "description": "Export scene as (Gtk/Net)Radiant Quake map",
    "category": "Import-Export",
}

def register():
    bpy.utils.register_class(ExportQuakeMap)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.utils.register_class(BlendRadiantObjectProperties)
    bpy.types.Object.blendradiant = bpy.props.PointerProperty(type=BlendRadiantObjectProperties)
    bpy.utils.register_class(SearchEntityClassnamesOperator)
    bpy.utils.register_class(BlendRadiantObjectPropertiesPanel)
    bpy.utils.register_class(MakeRoomOperator)
    bpy.utils.register_class(BlendRadiantAddonPreferences)

def unregister():
    bpy.utils.unregister_class(ExportQuakeMap)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.utils.unregister_class(BlendRadiantObjectProperties)
    del bpy.types.Object.blendradiant
    bpy.utils.unregister_class(SearchEntityClassnamesOperator)
    bpy.utils.unregister_class(BlendRadiantObjectPropertiesPanel)
    bpy.utils.unregister_class(MakeRoomOperator)
    bpy.utils.unregister_class(BlendRadiantAddonPreferences)

if __name__ == "__main__":
    register()
