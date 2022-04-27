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
from c0s_lewd_utilities.addon_utils.general.propertygroup_handler import register_unregister_propertygroups_recursive, PollMethods, UpdateMethods


class PropertyGroups():

    ###########################################
    ############Object properties##############
    ###########################################
    class ObjectMainProps(bpy.types.PropertyGroup):
        pass

    class ObjectAnimationMain(bpy.types.PropertyGroup):
        pass

    class ObjectAnimationToShapekeys(bpy.types.PropertyGroup):
        pass


class Cardboy0ObjectMiscAnimateWithShapekeys(bpy.types.PropertyGroup):
    frame_start: bpy.props.IntProperty(default=1, description="The starting frame of your animation")
    frame_end: bpy.props.IntProperty(default=100, description="The last frame of your animation")
    apply_transforms: bpy.props.BoolProperty(default=1, description="Result will look like any type of transformation of the original object was applied.\nThis includes delta transforms and constraints")
    keep_vertex_groups: bpy.props.BoolProperty(default=1, description="Do you want the new object to keep any vertex groups of the original?")
    keep_materials: bpy.props.BoolProperty(default=1, description="Do you want your new object to keep its original materials? I know almost nothing about materials to be honest")
    only_current_frame: bpy.props.BoolProperty(default=0, description="Instead of converting a whole animation that spans over several frames, creates an 'applied' version of your object with the current shape")


prop_dict = {
    "animation": {
        "_CLASS": PropertyGroups.ObjectAnimationMain,
        "shapekey_convert": {
            "_CLASS": PropertyGroups.ObjectAnimationToShapekeys,
            "frame_start": bpy.props.IntProperty(default=1, description="The starting frame of your animation"),
            "frame_end": bpy.props.IntProperty(default=100, description="The last frame of your animation"),
            "apply_transforms": bpy.props.BoolProperty(default=1, description="Result will look like rotation, scale and location of the original object was applied.\nThis includes delta transforms and constraints"),
            "only_current_frame": bpy.props.BoolProperty(default=0, description="Instead of converting a whole animation that spans over several frames, creates an 'applied' version of your object with the current shape as the base shape"),
            (s := "target_obj"): bpy.props.PointerProperty(type=bpy.types.Object,
                                                           poll=PollMethods.object_data_is_one_of({bpy.types.Mesh}),
                                                           update=UpdateMethods.just_use_poll_method(attr_name=s),
                                                           description="If left empty, a new object for the shapekeys will be created automatically.\nIf you choose a target object, that already existing object will get the shapekeys instead")
        }
    }
}


def register():
    register_unregister_propertygroups_recursive(main_prop_group=PropertyGroups.ObjectMainProps,
                                                 prop_dict=prop_dict,
                                                 register=True)
    bpy.types.Object.c0_lewd_utilities = bpy.props.PointerProperty(type=PropertyGroups.ObjectMainProps)


def unregister():
    del bpy.types.Object.c0_lewd_utilities
    register_unregister_propertygroups_recursive(main_prop_group=PropertyGroups.ObjectMainProps,
                                                 prop_dict=prop_dict,
                                                 register=False)
