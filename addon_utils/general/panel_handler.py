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

class PollMethods():
    """Provides poll methods for panels.

    More info: https://docs.blender.org/api/current/bpy.types.Panel.html#bpy.types.Panel.poll
    """
    @classmethod
    def is_object_with_mesh(clss, obj):
        """Simple poll method that checks if the active object has a mesh (and not something else, like a light or camera.)

        Also checks that the object itself isn't None.
        """
        if obj==None:
            return False
        if type(obj.data) == bpy.types.Mesh:
            return True
        else:
            return False