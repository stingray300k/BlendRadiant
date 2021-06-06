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

import xml.etree.ElementTree as ET
from pathlib import Path

# internal use only
def _get_entity_classes_etree(context):
    prefs = context.preferences.addons[__package__].preferences
    # parse gamepack's entities.ent XML file
    # TODO cache this somehow to avoid re-reading file on each redraw
    if not prefs.radiant_path and not prefs.default_game:
        return []
    entities_path = Path(prefs.radiant_path, "gamepacks",
        prefs.default_game+".game", "data", "entities.ent")
    if not entities_path.exists():
        # TODO display in blender itself
        print(f"entities definition file {entities_path} not found")
    tree = ET.parse(entities_path)
    classes = tree.getroot()
    return classes


entity_classnames = [] # ensure Python keeps refs, cf warning in EnumProperty docs
def get_entity_classnames(self, context):
    global entity_classnames
    entity_classnames[:] = []
    classes = _get_entity_classes_etree(context=context)
    for entity_class in classes:
        name = entity_class.get("name")
        if not name:
            continue
        entity_classnames.append((name, name, ""))
    return entity_classnames


entity_keys = []
def get_entity_keys_for_current(self, context):
    global entity_keys
    entity_keys[:] = []
    classname = context.active_object.blendradiant.entity_classname
    if not classname:
        return []
    classes = _get_entity_classes_etree(context=context)
    active_class = classes.find(f"./*[@name='{classname}']") # TODO quote?
    if not active_class:
        return []
    for key in active_class:
        keyname = key.get("key")
        if not keyname:
            continue
        entity_keys.append((keyname, keyname, ""))
    return entity_keys
