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
from c0s_lewd_utilities.toolbox_1_0_0.advanced.node_helper import GeometryNodesModifierHandler
from c0s_lewd_utilities.addon_utils.animation.imposter_creator import ImposterCreator


class GeometryLinker():
    """Creates a new object that will dynamically copy the animation and shape of a reference object. The reference objects itself will be left completely untouched.
    The whole process requires creation of certain modifiers and constraints via multiple methods, which is why you can call
    the setup_everything() method to do everything at once.

    An important property of the created object will be that it virtually doesn't react to changes in rotation.
    obj_axis transfers its rotation to the object, but no matter what way you rotate it, the object itself will not seem to rotate.

    This is done so that the local axis of the new object can be changed with the obj_axis without actually changing the geometry, because certain
    modifiers can only work with local axis.
    """
    __obj_main: bpy.types.Object
    __main_context: bpy.types.Context
    __obj_axis: bpy.types.Object  # empty that will transfer its rotation to obj_new
    imposter_creator: ImposterCreator
    obj_imposter: bpy.types.Object  # new object
    obj_static: bpy.types.Object  # object that's supposed to not move or rotate in any way. Acts as the hooking target.
    mod_geom_node: bpy.types.NodesModifier
    mod_vw_mix_to_1: bpy.types.VertexWeightMixModifier
    mod_vw_mix_to_0: bpy.types.VertexWeightMixModifier
    mod_hook: bpy.types.HookModifier
    # a vertex group that will contain every vertex with a weight of 1
    vg_all_one: bpy.types.VertexGroup
    # a vertex group that will contain every vertex with a weight of 0
    vg_all_zero: bpy.types.VertexGroup
    constraint_copy_rot: bpy.types.CopyRotationConstraint

    def __init__(self, context, obj_main):
        """
        Parameters
        ----------
        context : bpy.types.Context
            The context that will be used for everything where a context is required.\\
            You can change it with the change_context() method.
        obj_main : bpy.types.Object
            The object whose geometry to show.
        """
        self.__obj_main = obj_main

        imposter_creator = ImposterCreator(obj_main)
        self.imposter_creator = imposter_creator
        self.obj_imposter = imposter_creator.obj_new
        imposter_creator.transfer_other_data()

        self.vg_all_one = imposter_creator.get_new_vertex_group()  # All weights 1
        self.vg_all_zero = imposter_creator.get_new_vertex_group()  # All weights 0

        self.reset_context(new_context=context)

        self.fix_geo_mod_node_group()

        # 1. Create obj_new, a new object that mimics the animation of obj_orig in any possible way.
        #          Because we use a geometry node modifier to copy the mesh data, the obj_new should always look like the original,
        #          even when changes are made to it
        # 2. Create said geometry node to copy the geometry of obj_orig
        # 3. Add a hook modifier. Assign every vertex of obj_new to it.
        #          We later add a constraint that changes the rotation of the object. But we only want that to happen without the geometry
        #          actually rotating in viewport as well. For that, the hook modifier works.
        #          Problems:
        #               - The vertices are hooked the moment a target object is chosen for the modifier.
        #                   Resetting that "soft bind" requires you to remove the target object and choose it again.
        #               - To hook all vertices, we need to provide a vertex group that contains every vertices with a weight of 1.
        # 4. Add an empty - the "obj_axis" that the use can later use to rotate the direction of the bulge.
        #          obj_new gets its rotation with a new copy restraint.
        #

    def reset_context(self, new_context):
        """Changes the context this instance uses for methods were contexts are required

        Parameters
        ----------
        new_context : bpy.types.Context
        """
        self.__main_context = new_context

    def fix_geo_mod_node_group(self):
        """The default node group of the geometry nodes modifier needs to be filled with the stuff we need.
        """
        mod_geom_node = self.imposter_creator.mod_geom_node
        self.mod_geom_node = mod_geom_node

        node_helper = GeometryNodesModifierHandler(source=mod_geom_node, reset=False)

        node_use_obj_transforms = node_helper.add_node(node_type='GeometryNodeTransform')
        node_copy_obj_data = self.imposter_creator.node_copy_obj_data

        node_helper.connect_nodes(node_copy_obj_data.outputs["Location"], node_use_obj_transforms.inputs["Translation"])
        node_helper.connect_nodes(node_copy_obj_data.outputs["Rotation"], node_use_obj_transforms.inputs["Rotation"])
        node_helper.connect_nodes(node_copy_obj_data.outputs["Scale"], node_use_obj_transforms.inputs["Scale"])
        node_helper.connect_nodes(node_copy_obj_data.outputs["Geometry"], node_use_obj_transforms.inputs["Geometry"])

        node_helper.connect_nodes(node_use_obj_transforms.outputs["Geometry"], node_helper.main_output_node.inputs["Geometry"])

        node_helper.deselect_all_nodes()

        node_helper.main_input_node.location = (-350, 0)
        node_use_obj_transforms.location = (-110, -250)
        node_copy_obj_data.location = (-370, -360)
        node_helper.main_output_node.location = (470, -330)

    def add_vg_uniforming_mods(self):
        """Adds vertex weight mix modifiers to fill vg_all_one and vg_all_zero
        """
        self.mod_vw_mix_to_1 = vertex_groups.VGroupsWithModifiers.vertex_weight_uniform(obj=self.obj_imposter, vg_name=self.vg_all_one.name, weight=1)
        self.mod_vw_mix_to_0 = vertex_groups.VGroupsWithModifiers.vertex_weight_uniform(obj=self.obj_imposter, vg_name=self.vg_all_zero.name, weight=0)
        self.__order_mods()

    def add_hook_mod(self):
        """The hook modifiers is the reason why the object will not seem to rotate, translate or scale when you're changing its transforms.
        Note that while the modifiers doesn't have a "bind" button, that same thing basically happens when a target object is given to the hook modifier.
        If you want to "reset" the bind, you have to unassign any target object and then assign it again. Use the reset_hook_mod() method for convenience.
        """
        if getattr(self, "mod_hook", None) != None:
            raise Exception("A hook modifier was already added!")
        self.__create_obj_static()
        self.mod_hook = self.obj_imposter.modifiers.new("Hook", "HOOK")
        self.mod_hook.vertex_group = self.vg_all_one.name
        self.reset_hook_mod()
        self.__order_mods()

    def reset_hook_mod(self):
        """Makes the hook modifier basically "rebind" (although a bind button doesn't actually exist)
        """
        self.mod_hook.object = None
        self.mod_hook.object = self.obj_static

    def __create_obj_static(self):
        """Creates a object that acts as the target for the hook modifier of our new object.
        It must never change its transformations, which is why constraints are added to prevent the user from doing that.
        """
        self.obj_static = bpy.data.objects.new(name="do not move me (" + self.obj_imposter.name + ")", object_data=None)
        # self.obj_static.use_fake_user = True
        limit_location = self.obj_static.constraints.new('LIMIT_LOCATION')
        limit_rotation = self.obj_static.constraints.new('LIMIT_ROTATION')
        limit_scale = self.obj_static.constraints.new('LIMIT_SCALE')
        for xyz in ('x', 'y', 'z'):
            setattr(limit_location, "use_min_" + xyz, True)
            setattr(limit_location, "use_max_" + xyz, True)
            setattr(limit_rotation, "use_limit_" + xyz, True)

            setattr(limit_scale, "use_min_" + xyz, True)
            setattr(limit_scale, "use_max_" + xyz, True)
            # scale is at 0 by default, which obviously should be avoided unless you want your object to just disappear
            setattr(limit_scale, "min_" + xyz, 1)
            setattr(limit_scale, "max_" + xyz, 1)
        for constraint in (limit_location, limit_rotation, limit_scale):
            constraint.use_transform_limit = True
        for collection in self.obj_imposter.users_collection:
            # Putting the new object in the same collection as the imposter object
            collection.objects.link(self.obj_static)

    def use_obj_axis(self, obj_axis):
        """Uses the provided object as a "rotation parent".This allows the user to influence the local axis of our main object by rotating the axis object instead,
        and because of the hook modifier, rotations will virtually not change anything.
        The whole reason why this setup exists is because the shrinkwrap modifier that gets added later can only project along one of the local axis of an object,
        so our object axis can be used to dynamically change those local axis values.

        Parameters
        ----------
        obj_axis : bpy.types.Object
            Object to use as the "rotation parent"
        """
        self.__obj_axis = obj_axis
        self.__order_mods()
        self.constraint_copy_rot = self.obj_imposter.constraints.new(type='COPY_ROTATION')
        self.constraint_copy_rot.target = obj_axis
        self.constraint_copy_rot.name = "Copy Rotation of " + obj_axis.name
        if getattr(self, "mod_hook", None) != None:
            self.reset_hook_mod()

    def setup_everything(self, obj_axis):
        """Calls every method that needs to be done.

        Parameters
        ----------
        obj_axis : bpy.types.Object
            Object to use as the "rotation parent" for our new main object.
        """
        self.use_obj_axis(obj_axis=obj_axis)
        self.add_vg_uniforming_mods()
        self.add_hook_mod()
        self.__order_mods()

    def __order_mods(self):
        """The created modifiers need to be in a certain order to work properly. This method makes sure that order is present.
        """
        all_mods_in_order = (
            getattr(self, "mod_geom_node", None),
            getattr(self, "mod_vw_mix_to_1", None),
            getattr(self, "mod_vw_mix_to_0", None),
            getattr(self, "mod_hook", None),
        )
        index_current = 0
        for mod in (all_mods_in_order):
            if mod != None:
                modifiers.move_modifer_to_position_in_stack(context=self.__main_context, modifier=mod, position=index_current)
                index_current += 1
