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
from c0s_lewd_utilities.toolbox_1_0_0 import vertex_groups, modifiers
from c0s_lewd_utilities.toolbox_1_0_0.advanced.drivers import DriverHelper
from c0s_lewd_utilities.toolbox_1_0_0.advanced.custom_properties import CustomPropertyHandler



class ShrinkwrapAndDisplaceHandler():
    """
    Because nothing in Blender can ever be easy, for us to use the shrinkwrap modifier (that sounds cool in theory) requires a bunch of other mods.
    This class does some of those things with its methods, assuming others have already done before.
    Use the setup_everything() method to do everything at once.

    It's recommended to do this with the result of the GeometryLinker() class
    """

    __displace_default_strength = 10

    __obj_imposter: bpy.types.Object
    __obj_orig: bpy.types.Object
    __obj_target: bpy.types.Object
    __vg_target: bpy.types.VertexGroup
    __vg_target_uniform_one: bpy.types.VertexGroup
    __vg_target_uniform_zero: bpy.types.VertexGroup
    __orig_amount_of_mods: int
    mod_vw_mix_target_copy_1: bpy.types.VertexWeightMixModifier
    mod_vw_mix_target_copy_0: bpy.types.VertexWeightMixModifier
    mod_vw_mix_target_uni_1: bpy.types.VertexWeightMixModifier
    mod_vw_mix_target_uni_0: bpy.types.VertexWeightMixModifier
    
    mod_displace_first: bpy.types.DisplaceModifier
    mod_displace_reverse: bpy.types.DisplaceModifier
    mod_vw_proximity: bpy.types.VertexWeightProximityModifier
    mod_shrinkwrap: bpy.types.ShrinkwrapModifier
    __main_context: bpy.types.Context
    drivers: list

    def __init__(self, main_context, obj_mimic_orig, obj_target, obj_orig):
        """A shrinkwrap modifier alone isn't enough, certain other things need to be done as well. This class does those things with its methods.
        Use the setup_everything() method to do everything at once.

        It's recommended to do this with the result of the GeometryLinker() class

        Parameters
        ----------
        main_context : bpy.types.Context
            The context that will be used for everything where a context is required.
            You can change it later with the change_context() method.
        obj_mimic_orig : bpy.types.Object
            The object that mimics the geometry of the original object
        obj_target : bpy.types.Object
            The object that will be shrinkwrapped to
        obj_orig : bpy.types.Object
            The object where to take vertex group data from
        """
        self.__orig_amount_of_mods = len(obj_mimic_orig.modifiers)
        self.__obj_imposter = obj_mimic_orig
        self.__obj_target = obj_target
        self.__obj_orig = obj_orig
        self.__main_context = main_context

    def change_context(self, new_context):
        """Changes the context this instance uses for methods were contexts are required

        Parameters
        ----------
        new_context : bpy.types.Context
        """
        self.__main_context = new_context

    def mimic_vg_data(self, target_vg, placeholder_vg_1, placeholder_vg_2):
        """Sets weights of the given placeholder vertex groups via modifiers.
        One will have all vertices of the target_vg reset to 1, the other to 0 (in both cases excluding unassigned vertices)

        Parameters
        ----------
        target_vg : bpy.types.VertexGroup
            The vertex group of the original object that's supposed to be affected by the shrinkwrapping.
        placeholder_vg_1 : bpy.types.VertexGroup
            Any usable vertex group on obj_mimic
        placeholder_vg_2 : bpy.types.VertexGroup
            Any usable vertex group on obj_mimic
        """
        self.__order_mods()
        self.__vg_target = target_vg
        if self.__has_vg_target_been_linked() == False:
            raise Exception("The required target vertex group hasn't been linked to obj_new yet! Use " + self.mimic_vg_data.__name__ + " first!")

        self.__vg_target_uniform_one = placeholder_vg_1
        self.__vg_target_uniform_zero = placeholder_vg_2
        self.mod_vw_mix_target_copy_1 = self.__mimic_vertex_group(vg_to_target=self.__vg_target.name, vg_placeholder=placeholder_vg_1.name)
        self.mod_vw_mix_target_copy_0 = self.__mimic_vertex_group(vg_to_target=self.__vg_target_uniform_one.name, vg_placeholder=placeholder_vg_2.name)

        self.mod_vw_mix_target_uni_1 = vertex_groups.VGroupsWithModifiers.vertex_weight_uniform(obj=self.__obj_imposter, vg_name=self.__vg_target_uniform_one.name, only_assigned=True, weight=1)
        self.mod_vw_mix_target_uni_0 = vertex_groups.VGroupsWithModifiers.vertex_weight_uniform(obj=self.__obj_imposter, vg_name=self.__vg_target_uniform_zero.name, only_assigned=True, weight=0)

        self.__order_mods()

    def add_first_displace_mod(self):
        """Adds the first displace modifier. Basically, we first need to move everything into a certain direction and then use the shrinkwrap modifier.
        """
        if self.__has_vg_target_been_linked() == False:
            raise Exception("The required target vertex group hasn't been linked to obj_new yet! Use " + self.mimic_vg_data.__name__ + " first!")
        self.mod_displace_first = self.__obj_imposter.modifiers.new("Displace for shrinkwrap", "DISPLACE")
        self.mod_displace_first.direction = "Z"

        self.mod_displace_first.strength = self.__displace_default_strength
        self.__order_mods()

    def add_shrinkwrap_mod(self):
        """Adds the shrinkwrap modifier. This b*tch can only project along a local axis (X, Y or Z), which is why I had to write the GeometryLinker() class to make changing of local axis
        possible without the object actually appearing to rotate.
        """
        if getattr(self, "mod_displace_first", None) == None:
            raise Exception("The required displace mod hasn't been added to obj_new yet! Use " + self.add_first_displace_mod.__name__ + " first!")
        self.mod_shrinkwrap = self.__obj_imposter.modifiers.new("Shrinkwrap", "SHRINKWRAP")

        self.mod_shrinkwrap.wrap_method = 'PROJECT'
        self.mod_shrinkwrap.use_positive_direction = False
        self.mod_shrinkwrap.use_negative_direction = True
        self.mod_shrinkwrap.use_project_z = True
        self.mod_shrinkwrap.project_limit = self.mod_displace_first.strength * self.mod_displace_first.mid_level
        self.mod_shrinkwrap.vertex_group = self.__vg_target_uniform_one.name
        self.mod_shrinkwrap.target = self.__obj_target
        self.__order_mods()

    def add_vw_proximity_mod(self):
        """Adds a vertex weight proximity modifier. To make sure the reverse displace modifier doesn't move *every* vertex back into place, 
        it needs to know which vertices have been shrinkwrapped. For that, this modifier exists. 
        """
        if self.__has_vg_target_been_linked() == False:
            raise Exception("The required target vertex group hasn't been linked to obj_new yet! Use " + self.mimic_vg_data.__name__ + " first!")

        self.mod_vw_proximity = self.__obj_imposter.modifiers.new("Vertex Weight Proximity", "VERTEX_WEIGHT_PROXIMITY")

        self.mod_vw_proximity.vertex_group = self.__vg_target_uniform_zero.name
        self.mod_vw_proximity.proximity_mode = 'GEOMETRY'
        self.mod_vw_proximity.proximity_geometry = {'VERTEX'}
        self.mod_vw_proximity.min_dist = 0
        self.mod_vw_proximity.max_dist = 0.00001
        # shown as 'Median Step', seems to be the best option to really have all other vertices unaffected
        self.mod_vw_proximity.falloff_type = 'STEP'
        self.mod_vw_proximity.target = self.__obj_orig
        self.__order_mods()

    def add_second_displace_mod(self):
        """Adds a second displace modifier, after the shrinkwrap modifier. It basically resets what the first diplace modifier did.
        """
        if self.__has_vg_target_been_linked() == False:
            raise Exception("The required target vertex group hasn't been linked to obj_new yet! Use " + self.mimic_vg_data.__name__ + " first!")

        self.mod_displace_reverse = self.__obj_imposter.modifiers.new("Displace reverse", "DISPLACE")
        self.mod_displace_reverse.direction = "Z"
        self.mod_displace_reverse.strength = -self.__displace_default_strength  # negative!
        self.__order_mods()

    def add_third_displace_mod(self):
        """The first displace modifier displaces in one direction, the second displace mod back into the opposite direction,
        and then the third modifier once again displaces into the original direction. But this time it only displaces vertices that were affected by the shrinkwrapping.
        """
        if self.__has_vg_target_been_linked() == False:
            raise Exception("The required target vertex group hasn't been linked to obj_new yet! Use " + self.mimic_vg_data.__name__ + " first!")

        self.mod_displace_fix = self.__obj_imposter.modifiers.new("Displace fix", "DISPLACE")

        self.mod_displace_fix.direction = "Z"
        self.mod_displace_fix.vertex_group = self.__vg_target_uniform_zero.name
        self.mod_displace_fix.strength = self.__displace_default_strength

    def __has_vg_target_been_linked(self):
        """Checks if a vg_target has already been provided/linked with the data transfer modifier.

        Returns
        -------
        True or False
        """
        try:
            self.__vg_target
            return self.__obj_imposter.vertex_groups.find(self.__vg_target.name) != -1
        except:
            return False

    def __order_mods(self):
        """The created modifiers need to be in a certain order to work properly. This method makes sure that order is present.
        """
        all_mods_in_order = (
            getattr(self, "mod_vw_mix_target_copy_1", None),
            getattr(self, "mod_vw_mix_target_copy_0", None),
            getattr(self, "mod_vw_mix_target_uni_1", None),
            getattr(self, "mod_vw_mix_target_uni_0", None),
            # getattr(self, "mod_vw_edit_target_uni_1", None),
            # getattr(self, "mod_vw_mix_two", None),
            # getattr(self, "mod_vw_mix_target_uni_0", None),
            # getattr(self, "mod_vw_edit_target_uni_0", None),
            getattr(self, "mod_displace_first", None),
            getattr(self, "mod_shrinkwrap", None),
            getattr(self, "mod_displace_reverse", None),
            getattr(self, "mod_vw_proximity", None),
            getattr(self, "mod_displace_fix", None),
        )
        index_current = self.__orig_amount_of_mods
        for mod in (all_mods_in_order):
            if mod != None:
                modifiers.move_modifer_to_position_in_stack(
                    context=self.__main_context, modifier=mod, position=index_current)
                index_current += 1

    def __mimic_vertex_group(self, vg_to_target: str, vg_placeholder: str):
        """ Basically replaces the values of a vertex group with those of another one.

        Parameters
        ----------
        vg_to_duplicate : str
            The name of the vertex group you want to get a duplicate for.
        vg_placeholder : str
            VG that gets its values replaced

        Returns
        -------
        bpy.types.VertexWeightMixModifier
            Created Vertex Weight Mix Modififer
        """
        obj = self.__obj_imposter
        mod_vw_mix = obj.modifiers.new(name='Replace ' + vg_placeholder + " with " + vg_to_target, type='VERTEX_WEIGHT_MIX')

        mod_vw_mix.vertex_group_a = vg_placeholder
        mod_vw_mix.vertex_group_b = vg_to_target
        # 'B' for 'VGroup B', if instead 'ALL' then all vertices will be assigned, just some with a weight of 0 without you noticing
        mod_vw_mix.mix_set = 'B'
        mod_vw_mix.mix_mode = 'SET'  # What you see as 'Replace'
        return mod_vw_mix

    def add_drivers_and_custom_properties(self):
        """Creates custom properties and uses them for drivers of certain values, including:
        - Strength value of all displace modifiers
        - Visibility of all displace and shrinkwrap modifiers
        """
        self.__add_custom_property_displace_values()
        self.__add_custom_property_displace_visibility()

    def __add_custom_property_displace_values(self):
        """Have fun deciphering this code, sucker """

        dhelper_displ_strength_first = DriverHelper(self.mod_displace_first, "strength")
        dhelper_displ_strength_reverse = DriverHelper(self.mod_displace_reverse, "strength")
        dhelper_displ_strength_fix = DriverHelper(self.mod_displace_fix, "strength")

        c_prop_displ_strength = CustomPropertyHandler.SimpleFloat(blend_obj=self.__obj_imposter, name="Displace strength", description="Strength of displace modifiers",
                                                                  default=self.__displace_default_strength, min=0, max=20, soft_max=10)
        c_prop_displ_offset = CustomPropertyHandler.SimpleFloat(blend_obj=self.__obj_imposter, name="Offset", description="Offset",
                                                                default=0, min=-10, max=10, soft_min=-4, soft_max=4)

        var = dhelper_displ_strength_first.add_variable_linked_to_property(prop_owner=c_prop_displ_strength.get_blend_obj(),
                                                                           property_name=c_prop_displ_strength.get_name(),
                                                                           is_custom_property=True)
        dhelper_displ_strength_first.driver.expression = var.name

        var = dhelper_displ_strength_reverse.add_variable_linked_to_property(prop_owner=c_prop_displ_strength.get_blend_obj(),
                                                                             property_name=c_prop_displ_strength.get_name(),
                                                                             is_custom_property=True)
        dhelper_displ_strength_reverse.driver.expression = var.name
        dhelper_displ_strength_reverse.driver.expression = "-(" + dhelper_displ_strength_reverse.driver.expression + ")"

        var_displace_strength = dhelper_displ_strength_fix.add_variable_linked_to_property(prop_owner=c_prop_displ_strength.get_blend_obj(),
                                                                                           property_name=c_prop_displ_strength.get_name(),
                                                                                           is_custom_property=True)
        var_displace_offset = dhelper_displ_strength_fix.add_variable_linked_to_property(prop_owner=c_prop_displ_offset.get_blend_obj(),
                                                                                         property_name=c_prop_displ_offset.get_name(),
                                                                                         is_custom_property=True)
        dhelper_displ_strength_fix.driver.expression = var_displace_strength.name + ' + ' + var_displace_offset.name

        # shrinkwrap modifier requires a driver for mod.project_limit too, as it is supposed to be "displace_strength * mod_displace_first.mid_level"
        dhelper_shrinkwrap_projectlimit = DriverHelper(self.mod_shrinkwrap, "project_limit")
        var_displace_strength = dhelper_shrinkwrap_projectlimit.add_variable_linked_to_property(prop_owner=c_prop_displ_strength.get_blend_obj(),
                                                                                                property_name=c_prop_displ_strength.get_name(),
                                                                                                is_custom_property=True)

        property_path = self.mod_displace_first.path_from_id() + '.' + 'mid_level'
        var_displace_midlevel = dhelper_shrinkwrap_projectlimit.add_variable_linked_to_property(prop_owner=self.__obj_imposter,
                                                                                                property_name=property_path,
                                                                                                is_custom_property=False)

        dhelper_shrinkwrap_projectlimit.driver.expression = var_displace_strength.name + " * " + var_displace_midlevel.name

    def __add_custom_property_displace_visibility(self):
        dhelpers_viewport = []
        dhelpers_render = []
        for mod in [self.mod_displace_first, self.mod_displace_reverse, self.mod_displace_fix, self.mod_shrinkwrap]:
            dhelpers_viewport += [DriverHelper(mod, "show_viewport")]
            dhelpers_render += [DriverHelper(mod, "show_render")]
        cust_prop_viewport = CustomPropertyHandler.SimpleBool(blend_obj=self.__obj_imposter, name="show viewport", description="Show all deforming modifiers in viewport", default=1)
        cust_prop_render = CustomPropertyHandler.SimpleBool(blend_obj=self.__obj_imposter, name="show render", description="Show all deforming modifiers in render", default=1)
        for dhelper_view in dhelpers_viewport:
            var = dhelper_view.add_variable_linked_to_property(prop_owner=cust_prop_viewport.get_blend_obj(),
                                                               property_name=cust_prop_viewport.get_name(),
                                                               is_custom_property=True)
            dhelper_view.driver.expression = var.name

        for dhelper_render in dhelpers_render:
            var = dhelper_render.add_variable_linked_to_property(prop_owner=cust_prop_render.get_blend_obj(),
                                                                 property_name=cust_prop_render.get_name(),
                                                                 is_custom_property=True)
            dhelper_render.driver.expression = var.name

    def setup_everything(self, vg_target, placeholder_vg1, placeholder_vg2):
        """Calls every method that needs to be done.


        Parameters
        ----------
        vg_target : bpy.types.VertexGroup
            The vertex group containing the vertices of the original object that are supposed to be affected by the shrinkwrapping.
        placeholder_vg1 : bpy.types.VertexGroup
            Any usable vertex group on obj_mimic
        placeholder_vg2 : bpy.types.VertexGroup
            Any usable vertex group on obj_mimic
        """
        self.mimic_vg_data(target_vg=vg_target, placeholder_vg_1=placeholder_vg1, placeholder_vg_2=placeholder_vg2)
        self.add_first_displace_mod()
        self.add_shrinkwrap_mod()
        self.add_second_displace_mod()
        self.add_vw_proximity_mod()
        self.add_third_displace_mod()
        self.__order_mods()
        self.add_drivers_and_custom_properties()
