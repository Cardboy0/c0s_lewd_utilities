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

from math import radians
import bpy


class ObjAxisHandler():
    __obj_orig: bpy.types.Object
    __obj_axis_parent: bpy.types.Object
    __bone_parent: bpy.types.Bone
    obj_axis: bpy.types.Object
    constr_location: bpy.types.CopyLocationConstraint
    constr_rotation: bpy.types.CopyRotationConstraint

    def __init__(self, main_object):
        """
        Creates and modifies a new empty (object), displayed as a single arrow in viewport.
        The new object ("obj_axis") is intended to be used as a rotation reference, e.g. the user will be able to rotate this object to automatically change the rotation of another object.

        Parameters
        ----------
        main_object : bpy.types.Object
            The main, "boss" object of your project.
        """
        self.__obj_orig = main_object

        self.obj_axis = bpy.data.objects.new(name="Axis obj", object_data=None)  # is an "Empty"
        self.obj_axis.empty_display_type = "SINGLE_ARROW"
        self.obj_axis.rotation_mode = "XYZ" #make sure there are no weird default settings active that e.g. set it to quaternion
        for collection in main_object.users_collection:
            # link in same collections as main object
            collection.objects.link(self.obj_axis)

    @classmethod
    def rotate_by_90_degrees(clss, obj, axis="X", negative=False):
        """Rotates the object by 90 degrees in any of the three directions

        Assumes that the object uses XYZ Euler rotation.

        Parameters
        ----------
        obj : bpy.types.Object
            Axis object, but can be any object.
        axis : str
            "X" "Y" or "Z"
        negative : bool
            If True, moving will be done in opposite direction
        """
        axis_to_index = {'x': 0, 'y': 1, 'z': 2}
        index = axis_to_index[axis.lower()]

        if negative != False:
            ninety_degrees = radians(90)
        else:
            ninety_degrees = radians(-90)

        obj.rotation_euler[index] += ninety_degrees
        obj.rotation_euler[index] = obj.rotation_euler[index] % radians(360)
        # making sure the degrees are never above 360

    def do_bootleg_parenting(self, obj_axis_parent: bpy.types.Object = None, bone: bpy.types.Bone = None):
        """Adds location and rotation constraints to kind of simulate being parented to something.

        Real parenting can't be done due to reasons.

        By default, the original object is used as the parent.\\
        If obj_axis_parent is provided, its location and rotations will be used.\\
        If obj_axis_parent is an Armature AND a bone of that armature is provided, the location and rotations of the bone will be used.

        Parameters
        ----------
        obj_axis_parent : None or bpy.types.Object (NOT bpy.types.Armature)
            An object to be used as a location/rotation parent to the axis obj.
        bone : None or bpy.types.Bone
            A bone to "parent" to instead. Requires obj_axis_parent to have an Armature.
        """

        self.__bone_parent = bone
        self.__obj_axis_parent = obj_axis_parent

        constr_location = self.obj_axis.constraints.new('COPY_LOCATION')
        constr_rotation = self.obj_axis.constraints.new('COPY_ROTATION')
        constr_rotation.mix_mode = 'ADD'

        if obj_axis_parent == None:
            constr_location.target = self.__obj_orig
            constr_rotation.target = self.__obj_orig
        elif bone == None:
            constr_location.target = obj_axis_parent
            constr_rotation.target = obj_axis_parent
        else:
            for constraint in (constr_location, constr_rotation):
                constraint.target = obj_axis_parent
                constraint.subtarget = bone.name

        self.constr_location = constr_location
        self.constr_rotation = constr_rotation
