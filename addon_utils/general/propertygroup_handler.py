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


def register_unregister_propertygroups_recursive(main_prop_group, prop_dict, register=True):
    """Registers or unregisters multiple, intertwined propertygroups and their properties.
    Because you provide the properties with the prop_dict argument, the property group classes
    can actually be left empty.

    Parameters
    ----------
    main_prop_group : bpy.types.PropertyGroup
        The main property group the dictionary is meant for.
    prop_dict : dict
        A (potentially big) dictionary containing the bpy.props of your main propertygroup.

        {"frame_start": bpy.props.IntProperty(default=1)}\\
        is equivalent to the normal\\
        class YourPropGroup(bpy.types.PropertyGroup):
            frame_start: bpy.props.IntProperty(default=1)

        If you want to register another property group as a sub group, use another dictionary.\\
        This dictionary has the usual layout (properties of the subgroup), but must also have a "_CLASS" key with the property group class as its value.

    register : bool
        Register or unregister. When unregistering, unimportant items of prop_dict are simply ignored.

    Examples
    --------
    class GuyProps(bpy.types.PropertyGroup):
        pass\\
    class JobProps(bpy.types.PropertyGroup):
        pass\\
    class PainterProps(bpy.types.PropertyGroup):
        pass

    prop_dict = {
        "has_a_job": bpy.props.BoolProperty(default=0),
        "job_props": {      #sub property group
            "_CLASS": JobProps,
            "jobname": bpy.props.StringProperty(default="Painter")
            "painter_props": { #sub property group
                "_CLASS": PainterProps,
                ...
            },
            ...
        }

    register_unregister_propertygroups_recursive(GuyProps, prop_dict, register=True)\\
    bpy.types.Object.guy_props = bpy.props.PointerProperty(type=GuyProps)


    You could now do the following things:

    C.object.guy_props.has_a_job = False\\
    C.object.guy_props.job_props.jobname = "Writer"\\
    C.object.guy_props.job_props.painter_props.something = whatever

    Note: Writing bpy.types.Object.guy_props.has_a_job will not work.

    """
    if register == True:
        # In property groups, you define the properties with colons instead of equal signs.
        # When you do that, you actually add a key (the name of the variable) and a value (the thing after the colon)
        # to the __annotations__ property of the class.
        if hasattr(main_prop_group, "__annotations__") == False:
            main_prop_group.__annotations__ = dict()
        for (key, value) in prop_dict.items():
            if type(value) != dict:
                main_prop_group.__annotations__[key] = value
            else:
                sub_prop_group = value["_CLASS"]
                del value["_CLASS"]
                register_unregister_propertygroups_recursive(main_prop_group=sub_prop_group, prop_dict=value, register=True)
                main_prop_group.__annotations__[key] = bpy.props.PointerProperty(type=sub_prop_group)
                # subgroups need to be added as a PointerProperty and also registered before the parent property group.
        bpy.utils.register_class(main_prop_group)
    else:
        # unregister, in reversed order (main prop groups first, then subgroups)
        bpy.utils.unregister_class(main_prop_group)
        for (key, value) in prop_dict.items():
            if type(value) == dict:
                sub_prop_group = value["_CLASS"]
                del value["_CLASS"]
                register_unregister_propertygroups_recursive(main_prop_group=sub_prop_group, prop_dict=value, register=False)
