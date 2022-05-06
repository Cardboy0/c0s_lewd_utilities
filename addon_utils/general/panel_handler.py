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


class SpecialPanelPropTypes():
    """Similar to the "SpecialPropTypes" class of the propertygroup_handler module, only that the methods here are used to show proper
    panel stuff for those special properties. 
    """

    @classmethod
    def get_vertex_group_panel_prop(clss, layout: bpy.types.UILayout, data, property_name, obj: bpy.types.Object, text=None) -> None:
        """
        Calls the proper layout attribute to use for viewing a vertex group property that's basically just a String Property.

        This means you get menu where you can select a vertex group from your object in a dropdown menu.\\
        The same as with all other vertex group properties you already have in default Blender.

        Parameters
        ----------
        layout : bpy.types.UILayout
            Layout in the "draw(self, context)" method of your panel class.\\
            This can be "self.layout", but also "self.layout.column()" or similar 
        data : any
            The same data argument you use in a normal layout.props() method call
        property_name : str
            Name of the property
        obj : bpy.types.Object
            Object the vertex group belongs to.
        text : str OR None
            The same text argument you use in a normal layout.props() method call\\
            If None, no "text" argument will be passed

        Returns
        -------
        None

        """
        additional_args = dict()
        if text != None:
            additional_args["text"] = text

        layout.prop_search(
            data=data,
            property=property_name,
            search_data=obj,
            search_property="vertex_groups",
            **additional_args)

    @classmethod
    def get_bone_panel_prop(clss, layout: bpy.types.UILayout, data, property_name, armature: bpy.types.Armature, text=None) -> None:
        """
        Calls the proper layout attribute to use for viewing a bone property that's basically just a String Property.

        This means you get a menu where you can select a bone from your provided armature in a dropdown menu.\\

        Parameters
        ----------
        layout : bpy.types.UILayout
            Layout in the "draw(self, context)" method of your panel class.\\
            This can be "self.layout", but also "self.layout.column()" or similar 
        data : any
            The same data argument you use in a normal layout.props() method call
        property_name : str
            Name of the property
        obj : bpy.types.Armature
            Armature the vertex group belongs to.\\
            NOT the object that holds the armature (so, use object.data instead of object)
        text : str OR None
            The same text argument you use in a normal layout.props() method call\\
            If None, no "text" argument will be passed

        Returns
        -------
        None

        """
        additional_args = dict()
        if text != None:
            additional_args["text"] = text

        layout.prop_search(
            data=data,
            property=property_name,
            search_data=armature,
            search_property="bones",
            **additional_args)

    @classmethod
    def get_warning_label(clss, layout: bpy.types.UILayout, *text) -> None:
        """Displays a warning message in the panel together with an appropriate icon.

        Parameters
        ----------
        layout : bpy.types.UILayout
            Layout in the "draw(self, context)" method of your panel class.\\
            This can be "self.layout", but also "self.layout.column()" or similar 
        *text : str
            Lines of text to show in the warning.\\
            The asterisk at the front means you can give multiple text arguments instead of just one.\\
            That's required sometimes because '\\n' to get a new line will not work.


        Example
        -------
        SpecialPanelPropTypes.get_warning_label( self.layout, 
                                                "Me: Hey buddy, how are you today?", 
                                                "Dog: Terrible, the nightmares don't end"
                                                )
        """ 
        box = layout.box()
        box.label(text="WARNING", icon='ERROR')
        for single_text in text:
            box.label(text=single_text, icon='NONE')


class PollMethods():
    """Provides poll methods for panels.

    More info: https://docs.blender.org/api/current/bpy.types.Panel.html#bpy.types.Panel.poll
    """
    @classmethod
    def is_object_with_mesh(clss, obj):
        """Simple poll method that checks if the active object has a mesh (and not something else, like a light or camera.)

        Also checks that the object itself isn't None.
        """
        if obj == None:
            return False
        if type(obj.data) == bpy.types.Mesh:
            return True
        else:
            return False

