# ##### BEGIN GPL LICENSE BLOCK #####
#
# Part of the "c0s_lewd_utilities" add-on
# Copyright (C) 2022  Cardboy0 (https://twitter.com/cardboy0)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from c0s_lewd_utilities import names
from c0s_lewd_utilities import property_groups
from c0s_lewd_utilities import operators
from c0s_lewd_utilities import panels

bl_info = {
    # "name": names.addon_name,   # Apparently trying to use a variable from another module here will give you an error. For whatever reason.
    "name": "C0s Lewd Utilities",
    "author": "Cardboy0",
    "version": (0, 0),  # TODO: refresh version!
    "blender": (3, 0, 0),
    # "location": "SpaceBar Search -> Add-on Preferences Example",
    "description": "Utilities for lewd and non-lewd related stuff",
    # "warning": "",
    "doc_url": "",  # TODO add link to doc
    # TODO: add link to source somehow?
    # "tracker_url": "bug tracker", # TODO add bugtracker?
    "category": 'Animation',
    "support": 'TESTING'}


def register():
    # When registering things, order is important.
    property_groups.register()
    operators.register()
    panels.register()


def unregister():
    # reversed order of the register function
    panels.unregister()
    operators.unregister()
    property_groups.unregister()


if __name__ == "__main__":
    register()
