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
from operator import attrgetter


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
                # del value["_CLASS"] # deleting leads to problems when you try to unregister or reload the add-on
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
                # del value["_CLASS"]
                register_unregister_propertygroups_recursive(main_prop_group=sub_prop_group, prop_dict=value, register=False)


def get_props_from_string(object, datapath):
    """Returns the property from a python object.
    This could be a normal Blender object in your scene, but also the scene itself, the context, whatever.

    Parameters
    ----------
    object : any
        Anything that isn't None
    datapath : str
        Names of attributes seperated by dots, so how you would usually get the property of an object.

    Returns
    -------
    any

    Examples
    --------
    objects_in_scene_collection = get_props_from_string(object=C.scene, datapath="collection.objects")\\
    This is equal to:\\
    objects_in_scene_collection = C.scene.collection.objects
    """
    getter = attrgetter(datapath)
    return getter(object)


class PollMethods():
    """Some PropertyGroup attributes accept poll methods, for instance PointerProperties:\\
    class MyProps(bpy.types.PropertyGroup):
        target_obj: bpy.props.PointerProperty(type=bpy.types.Object, poll=A_POLL_METHOD)

    Such a poll method might check that the object has a mesh and isn't for example a light object.\\
    When you show those properties in panels and get selection menus, only objects that fullfill the 
    poll method requirements will be shown (again, no light objects for example).\\
    It does NOT however prevent someone from manually assigning a light object to the property from within the console.
    That's what "update" method arguments are probably for.

    Programming note: 
    - All poll methods start with a "self" parameter. That has nothing to do with them being in a class,
    it is required to exist by the rules for poll methods.
    - All poll methods also have an "object" parameter. That is NOT an actual Blender object (like a cube), but an object of the type of your PointerProperty.
        For example, if you use bpy.props.PointerProperty(type=bpy.types.Scene, poll=A_POLL_METHOD), the "object" argument of the poll method will actually be a scene.
    """

    @classmethod
    def object_data_is_one_of(clss, types={}, allow_self=False):
        """Not a poll method itself, but can be called to give you a poll method.

        The returned poll method will check if obj.data is any of the specified types.

        Parameters
        ----------
        types : set, list or tuple
            Allowed types
        allow_self : bool
            Allow or disallow to use the own object.

        Returns
        -------
        function
            Created poll method (as usual, it will accept a "self" and "obj" argument)

        Examples
        --------
        Get a poll method to check if an object is a Volume or an Empty:\\
        poll_method = PollMethods.object_data_is_one_of(types={bpy.types.Volume, type(None)})\\
        .# the type of empty data is the type of None, because empties have no data\\
        class MyProps(bpy.types.PropertyGroup):
            volume_or_empty_obj: bpy.props.PointerProperty(type=bpy.types.Object, poll=poll_method)

        """

        def poll_function(self, object) -> bool:
            if object == None:
                return True
            main_obj = self.id_data
            # self is the property group
            # and for some reason id_data will give you the object even if the property group actually is part of another propertygroup and only indirectly part of an object
            if allow_self == False and main_obj == object:
                return False
            else:
                if type(object.data) in types:
                    return True
                else:
                    return False
        return poll_function


class UpdateMethods():
    """Many PropertyGroup attributes accept "update" methods, for instance PointerProperties:\\
    class MyProps(bpy.types.PropertyGroup):
        target_scene: bpy.props.PointerProperty(type=bpy.types.Scene, update=AN_UPDATE_METHOD)

    These methods get called when a new value is assigned to the property. 

    Programming notes: 
    - All update methods start with a "self" parameter. That has nothing to do with them being in a class,
    it is required to exist by the rules for poll methods.
    - All update methods also have a "context" parameter. That's of the same type as bpy.context
    """

    @classmethod
    def just_use_poll_method(clss, attr_name):
        """
        Not an update method by itself, but can be called to give you one.\\
        Only works for bpy.props.PointerProperty properties, and only if they also have a "poll" method defined.

        Uses the poll method of itself on the new value and if it fails, resets the value to None instead.

        Parameters
        ----------
        attr_name : str
            Name of the attribute in the PropertyGroup

        Returns
        -------
        function
            Created update method (as usual, it will accept a "self" and "context" argument)

        Examples
        --------
        class MyProps(bpy.types.PropertyGroup):
            target_scene: bpy.props.PointerProperty(\\
                                                    type=bpy.types.Scene,\\
                                                    poll=SOME_POLL_METHOD,\\
                                                    update=UpdateMethods.just_use_poll_method(attr_name="target_scene")\\
                                                    )
        """

        def update_function(self, context) -> None:
            attr_value = getattr(self, attr_name)
            if clss._use_poll_method(self=self, attr_name=attr_name, attr_value=attr_value) == False:
                print(attr_name + " poll method failed when trying to update.")
                setattr(self, attr_name, None)
            return None

        return update_function

    @classmethod
    def _get_poll_method(clss, property_group, attr_name):
        pointer_property = property_group.__annotations__[attr_name]
        poll_method = pointer_property.keywords['poll']
        return poll_method

    @classmethod
    def _use_poll_method(clss, self, attr_name, attr_value):
        poll_method = clss._get_poll_method(property_group=type(self), attr_name=attr_name)
        return poll_method(self, attr_value)
