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
    """Provides poll methods for operators.

    More info: https://docs.blender.org/api/current/bpy.types.Operator.html#bpy.types.Operator.poll
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


class SpecialOperatorPropTypes():
    """Similar to the "SpecialPropTypes" class of the propertygroup_handler module, 
    only that the methods here are used to check or get the values from inside an operator.
    """

    @classmethod
    def get_vertex_group(clss, obj, vg_name):
        """Gets the vertex group of an object from its name.

        Warning: You should not use this method in the poll method of an operator.\\
        It would have a negative impact on performance.

        Parameters
        ----------
        obj : bpy.types.Object
            Object that has the vertex group
        vg_name : str
            Name of the alleged vertex group

        Returns
        -------
        None, False or bpy.types.VertexGroup
            None if the name is empty (vg_name="")\\
            False if the name isn't empty, but no vertex group with that name exists on the object\\
            VertexGroup object if the vertex group was found on the object.
        """
        if vg_name == "":
            return None
        else: 
            return obj.vertex_groups.get(vg_name, False)

    @classmethod
    def get_bone(clss, obj_armature, bone_name):
        """Gets the bone of an object from its name.

        Warning: You should not use this method in the poll method of an operator.\\
        It would have a negative impact on performance.

        Parameters
        ----------
        obj_armature : bpy.types.Object
            Object with an armature. \\
            This means that type(obj_armature.data) == bpy.types.Armature
        bone_name : str
            Name of the alleged bone

        Returns
        -------
        None, False or bpy.types.Bone
            None if the name is empty (bone_name="")\\
            False if the name isn't empty, but no bone with that name exists on the armature\\
            Bone object if the vertex group was found on the object.
        """
        if bone_name == "":
            return None
        else:
            # the "real" armature instance is at object.data (in this case)
            return obj_armature.data.bones.get(bone_name, False)
            # Because many objects can use the same armature data, having a bone object cannot be used to differentiate between them.
            # However, things in Blender that use Bones (e.g. a Copy Rotation Constraint) often require you to specify the object parent AND the bone,
            # which counters that problem.