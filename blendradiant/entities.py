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


entity_classnames = [] # ensure Python keeps refs, cf warning in EnumProperty docs
def get_entity_classnames(self, context):
    global entity_classnames
    prefs = context.preferences.addons[__package__].preferences
    entity_classnames = []
    # parse gamepack's entities.ent XML file
    if not prefs.radiant_path and not prefs.default_game:
        return []
    entities_path = Path(prefs.radiant_path, "gamepacks",
        prefs.default_game+".game", "data", "entities.ent")
    if not entities_path.exists():
        # TODO display in blender itself
        print(f"entities definition file {entities_path} not found")
    tree = ET.parse(entities_path)
    classes = tree.getroot()
    for entity_class in classes:
        name = entity_class.get("name")
        if not name:
            continue
        entity_classnames.append((name, name, ""))
    return entity_classnames
