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

    class ObjectImposterCreator(bpy.types.PropertyGroup):
        pass

    ##############################################
    ############Workspace properties##############
    ##############################################
    class WorkspaceMainProps(bpy.types.PropertyGroup):
        pass


prop_dict_object = {
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
        },
        "imposter_creator": {
            "_CLASS": PropertyGroups.ObjectImposterCreator,
            "mimic_transforms": bpy.props.BoolProperty(default=True, description="Mimic the transformations (location, rotation, scale) of your original object as well?")
        }
    }
}

prop_dict_workspace = {
    "prints_enabled": bpy.props.BoolProperty(default=False, description="Show some progress of operators in the Blender console.\nOnly affects certain operators"),
}


def register():
    register_unregister_propertygroups_recursive(main_prop_group=PropertyGroups.WorkspaceMainProps,
                                                 prop_dict=prop_dict_workspace,
                                                 register=True)
    register_unregister_propertygroups_recursive(main_prop_group=PropertyGroups.ObjectMainProps,
                                                 prop_dict=prop_dict_object,
                                                 register=True)
    bpy.types.WorkSpace.c0_lewd_utilities = bpy.props.PointerProperty(type=PropertyGroups.WorkspaceMainProps)
    bpy.types.Object.c0_lewd_utilities = bpy.props.PointerProperty(type=PropertyGroups.ObjectMainProps)


def unregister():
    del bpy.types.Object.c0_lewd_utilities
    del bpy.types.WorkSpace.c0_lewd_utilities
    register_unregister_propertygroups_recursive(main_prop_group=PropertyGroups.ObjectMainProps,
                                                 prop_dict=prop_dict_object,
                                                 register=False)
    register_unregister_propertygroups_recursive(main_prop_group=PropertyGroups.WorkspaceMainProps,
                                                 prop_dict=prop_dict_workspace,
                                                 register=False)
