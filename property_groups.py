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
from c0s_lewd_utilities.addon_utils.general import propertygroup_handler


class PropertyGroups():

    ###########################################
    ############Object properties##############
    ###########################################
    class ObjectMainProps(bpy.types.PropertyGroup):
        pass


prop_dict = {
}


def register():
    propertygroup_handler.register_unregister_propertygroups_recursive(main_prop_group=PropertyGroups.ObjectMainProps,
                                                                       prop_dict=prop_dict,
                                                                       register=True)
    bpy.types.Object.c0_lewd_utilities = bpy.props.PointerProperty(type=PropertyGroups.ObjectMainProps)


def unregister():
    del bpy.types.Object.c0_lewd_utilities
    propertygroup_handler.register_unregister_propertygroups_recursive(main_prop_group=PropertyGroups.ObjectMainProps,
                                                                       prop_dict=prop_dict,
                                                                       register=False)
