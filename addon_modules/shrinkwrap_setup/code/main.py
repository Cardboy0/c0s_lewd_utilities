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
from .geometry_linker import GeometryLinker
from .displace_setup import ShrinkwrapAndDisplaceHandler
from .create_obj_axis import ObjAxisHandler


class Main():

    #TODO: (future) add vg invert option

    obj_imposter: bpy.types.Object
    obj_axis: bpy.types.Object
    obj_static: bpy.types.Object
    __abbr: str

    def run(self, context, obj_main, vg_target, obj_target, axis_parent=None, axis_parent_bone=None):
        """ Runs basically everything required to set up the whole shrinkwrap stuff.

        With "shrinkwrap stuff" I mean using a combination of a bunch of modifiers, objects and constraints
        together with a shrinkwrap modifier to be able to properly use it, and with more options.

        For way more information, checkout the readme.md that should exist in the same folder as this file.

        Parameters
        ----------
        context : bpy.context
            The context that will be used for everything where a context is required.
        obj_main : bpy.types.Object
            The main object.
        vg_target : bpy.types.VertexGroup
            Only vertices assigned to this vertex group will be affected by the shrinkwrap stuff.\\
            Weights don't matter, because I have my limits.
        obj_target : bpy.types.Object
            Object that acts as the source of shrinkwrap deformation
        axis_parent : bpy.types.Object or None
            Object to be used as the rotation parent of the created axis object
        axis_parent_bone : bpy.types.Bone or None
            Bone to be used as the rotation parent. Only used if axis_parent.data is an armature.
        """
        abbr = "SPS."  # abbreviation to use for added mods and other stuff
        self.__abbr = abbr

        obj_axis_handler = ObjAxisHandler(main_object=obj_main)

        geo_linker = GeometryLinker(context=context, obj_main=obj_main)
        geo_linker.setup_everything(obj_axis=obj_axis_handler.obj_axis)

        obj_new = geo_linker.obj_imposter
        obj_static = geo_linker.obj_static
        obj_static.hide_set(True)

        displace_stuffer = ShrinkwrapAndDisplaceHandler(main_context=context, obj_mimic_orig=obj_new, obj_target=obj_target, obj_orig=obj_main)
        displace_stuffer.setup_everything(vg_target=vg_target,
                                          placeholder_vg2=geo_linker.imposter_creator.get_new_vertex_group(),
                                          placeholder_vg1=geo_linker.imposter_creator.get_new_vertex_group())

        obj_axis_handler.do_bootleg_parenting(obj_axis_parent=axis_parent, bone=axis_parent_bone)
        # only add the parenting constraints to obj_axis at the end to prevent bad bindings (e.g. with the hook modifier)

        self.obj_imposter = obj_new
        self.obj_axis = obj_axis_handler.obj_axis
        self.obj_static = obj_static

        self.__add_abbreviations()
        self.__unextend_almost_everything()

    @classmethod
    def is_valid(clss, obj_orig, obj_target):
        """Checks if two objects are eligible to be used for this class.

        Currently just checks if both objects actually have meshes.

        Parameters
        ----------
        obj_orig : bpy.types.Object
            Object that's supposed to deform from shrinkwrap stuff.
        obj_target : bpy.types.Object
            Object that's supposed to act as the source of shrinkwrap deformations.

        Returns
        -------
        bool
        """
        if type(obj_orig.data) != bpy.types.Mesh or type(obj_target.data) != bpy.types.Mesh:
            return False

        return True

    def __add_abbreviations(self):
        for obj in [self.obj_imposter, self.obj_axis, self.obj_static]:
            for thing in ([obj] + list(obj.modifiers) + list(obj.constraints)):
                if thing.name.startswith(self.__abbr) == False:
                    thing.name = self.__abbr + thing.name

    def __unextend_almost_everything(self):
        for obj in [self.obj_imposter, self.obj_axis, self.obj_static]:
            for thing in (list(obj.modifiers) + list(obj.constraints)):
                thing.show_expanded = False
        for con in self.obj_axis.constraints:
            con.show_expanded = True  # Exception, we want the user to know about these ones

    # TODO (future) add smoothing default mods
