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
import importlib
from c0s_lewd_utilities.toolbox_1_0_0 import modifiers, vertex_groups
from c0s_lewd_utilities.toolbox_1_0_0.advanced import node_helper


class ImposterCreator():
    __obj_orig: bpy.types.Object
    obj_new: bpy.types.Object
    node_helper: node_helper.GeometryNodesModifierHandler
    node_copy_obj_data: bpy.types.GeometryNodeObjectInfo
    mod_geom_node: bpy.types.NodesModifier
    # mod_data_transfer: bpy.types.DataTransferModifier
    constr_rotation: bpy.types.CopyRotationConstraint
    constr_location: bpy.types.CopyLocationConstraint
    constr_scale: bpy.types.CopyScaleConstraint

    __created_imposter_vgs: list
    __used_imposter_vgs: list
    __unused_imposter_vgs: list
    _vg_name = "imposter_vg"

    def __init__(self, obj):
        """Creates an "imposter" object. That object will seem to always look the same as the original object, even when changes are done to the original.
        This includes stuff such as modifiers, shape keys, etc.

        Transformations are copied with constraints, but those can also be set to be hidden by default.

        The whole thing is done by using a geometry node modifier.

        Parameters
        ----------
        obj : bpy.types.Object
            Object to create an imposter for.
        """
        self.__obj_orig = obj
        self.__create_obj_new()
        self.mod_geom_node = ImposterCreator.add_geo_mod(self.obj_new, obj_target=self.__obj_orig)
        self.node_helper = node_helper.GeometryNodesModifierHandler(self.mod_geom_node, reset=False)
        self.constr_rotation = None
        self.constr_location = None
        self.constr_scale = None
        # self.mod_data_transfer = None
        self.__created_imposter_vgs = []
        self.__used_imposter_vgs = []
        self.__unused_imposter_vgs = []

    def __create_obj_new(self):
        mesh_empty = bpy.data.meshes.new(name="empty mesh")
        self.obj_new = bpy.data.objects.new(
            name=self.__obj_orig.name + " Imposter", object_data=mesh_empty)
        for collection in self.__obj_orig.users_collection:  # link to the same scenes and collections
            collection.objects.link(self.obj_new)

    @classmethod
    def add_geo_mod(self, obj, obj_target) -> bpy.types.NodesModifier:
        """Adds a geometry node modifier to the obj that "copies" the geometry data of the obj_target.

        This method is called automatically by __init__, only call it yourself when you have a special reason to.

        Parameters
        ----------
        obj : bpy.types.Object
            Object that's supposed to look like obj_target (or rather, have its geometry added to its own)
        obj_target : bpy.types.Object
            Object with the geometry to mimic.

        Returns
        -------
        bpy.types.NodesModifier
            Created Geometry Node modifier
        """
        mod_geom_node = obj.modifiers.new(name="Imposter of " + obj_target.name, type="NODES")
        gh = node_helper.GeometryNodesModifierHandler(mod_geom_node, reset=True)
        node_copy_obj_data = gh.add_node('GeometryNodeObjectInfo')
        node_copy_obj_data.inputs['Object'].default_value = obj_target
        self.node_copy_obj_data = node_copy_obj_data

        # Important: The commented code that you see below is how it was originally done.
        # It uses a "Join Geometry" node to join the empty mesh of our object with the mesh of the target object.
        # That had a purpose, because since the empty mesh is the "original" mesh of our current object, any vertex groups we define ourselves (are not part of the target mesh)
        # are tied to that mesh. If we don't include it via joining, we lose the ability to manipulate those "original" vertex groups with modifiers, and sometimes
        # we do need some extra vertex groups to use.
        #
        # Currently, joining isn't done anymore, and instead the mesh (geometry data) of the target object is used directly.
        # This has (at least) two reasons:
        # - Even though our empty mesh was, well, empty, the join node still heavily influenced performance.
        # - UV maps didn't work properly with that setup.

        # node_join_geometry = gh.add_node('GeometryNodeJoinGeometry')
        # # important note on the join-geometry node:
        # # The owner of the geometry node modifier must be the top input, otherwise you can't use or modifier its vertex groups later.
        # gh.connect_nodes(node_copy_obj_data.outputs['Geometry'], node_join_geometry.inputs["Geometry"])
        # gh.connect_nodes(gh.main_input_node.outputs["Geometry"], node_join_geometry.inputs["Geometry"])
        # gh.connect_nodes(node_join_geometry.outputs["Geometry"], gh.main_output_node.inputs["Geometry"])

        gh.connect_nodes(node_copy_obj_data.outputs["Geometry"], gh.main_output_node.inputs["Geometry"])

        gh.main_input_node.location = (-200, -140)
        node_copy_obj_data.location = (-200, -320)
        # node_join_geometry.location = (100, -240)
        gh.main_output_node.location = (340, -240)
        
        gh.deselect_all_nodes()

        mod_geom_node.show_expanded = False

        return mod_geom_node

    def add_constraints(self, hidden=False):
        """Adds constraints to the new object that mimic the location, rotation and scale of the original object.

        Can be hidden.

        Parameters
        ----------
        hidden : bool
            Are the constraints supposed to be hidden?
        """
        self.constr_location = self.obj_new.constraints.new('COPY_LOCATION')
        self.constr_rotation = self.obj_new.constraints.new('COPY_ROTATION')
        self.constr_scale = self.obj_new.constraints.new('COPY_SCALE')
        for constraint in (self.constr_location, self.constr_rotation, self.constr_scale):
            constraint.target = self.__obj_orig
            constraint.show_expanded = False
            if hidden == True:
                constraint.enabled = False


    def transfer_other_data(self, vertex_groups=True, uv_maps=True, vertex_colors=True, material_slots=True):
        """Aside from the imposter object looking like the original object, you might also want it to mimic some of its other data,
        like vertex groups, uv_maps, etc.

        Use this method for that.

        Parameters
        ----------
        vertex_groups : bool
            Transfer vertex groups?
        uv_maps : bool
            Transfer uv maps?
        vertex_colors : bool
            Transfer vertex color groups?
        material_slots : bool
            Transfer material slots? (Materials already get transferred by default)
        """
        # Note: For most data types, the data already exists on the imposter object, as they seem to be part of the geometry.
        # That means, that if you want to use the "feet" vertex group of the original object on the new object, you just have to add a new vertex group
        # with the same name. It will automatically be filled with the values of the original vertex group.

        # So basically, vertex groups and many other data types will "automatically" transfer as long as ones with their names exist on the new object

        # mod_data_transfer = self.obj_new.modifiers.new(name='Transfer vertex groups from ' + self.__obj_orig.name, type='DATA_TRANSFER')
        # self.mod_data_transfer = mod_data_transfer
        # mod_data_transfer.object = self.__obj_orig
        obj_orig = self.__obj_orig
        obj_new = self.obj_new
        mesh_new = obj_new.data
        
        if vertex_groups == True:
            # mod_data_transfer.use_vert_data = True
            # mod_data_transfer.data_types_verts = {'VGROUP_WEIGHTS'}
            # mod_data_transfer.vert_mapping = 'TOPOLOGY'
            # mod_data_transfer.layers_vgroup_select_src = 'ALL'
            # mod_data_transfer.layers_vgroup_select_dst = 'NAME'
            # modifiers.ButtonPresser.data_transfer_button(mod_data_transfer)
            for vg in obj_orig.vertex_groups:
                obj_new.vertex_groups.new(name=vg.name)

        if uv_maps == True:
            for uv_map in obj_orig.data.uv_layers:
                mesh_new.uv_layers.new(name=uv_map.name)

        if vertex_colors == True:
            for v_colors in obj_orig.data.vertex_colors:
                mesh_new.vertex_colors.new(name=v_colors.name)

        if material_slots == True:
            orig_mats = self.__obj_orig.data.materials
            new_mats = self.obj_new.data.materials
            for material in orig_mats:
                new_mats.append(material)
            # while the material slots seem to be part of objects (object.material_slots), they appear automatically based on object.data.materials

    def _check_for_existing_vgs(self):
        """Checks if vertex groups to be used for imposter objects had already been added to the original object before
        and refreshes attributes of this instance accordingly"""
        vgs = self.__obj_orig.vertex_groups
        for name, vg in dict(vgs).items():
            if self._vg_name.startswith(name) and (vg in self.__created_imposter_vgs) == False:
                self.__created_imposter_vgs += [vg]
                self.__unused_imposter_vgs += [vg]

    def get_new_vertex_group(self) -> bpy.types.VertexGroup:
        """Gives you a vertex group that you can work with on the new object, like e.g. modify it with modifiers.\\
        Just simply adding a vertex group does not work: the vertex group will only exist on paper and you can select it in modifiers,
        but they will act as if you actually selected nothing at all. I don't mean "oh, you selected an empty vertex group" but
        "what vertex group? lol", and you also can't edit it with vertex weight modifiers in any way.

        The cause of this is how the geometry node modifier is set up, and the currently used solution is creating (or finding an already created) 
        vertex group on the original object, since those CAN be used.

        It's not ideal, but also not that bad.

        Returns
        -------
        bpy.types.VertexGroup
            A vertex group on the object new you can use.
        """
        self._check_for_existing_vgs()
        if len(self.__unused_imposter_vgs) == 0:
            vg_new = vertex_groups.create_vertex_group(obj=self.__obj_orig, vg_name=self._vg_name)
            self.__created_imposter_vgs += [vg_new]
            self.__used_imposter_vgs += [vg_new]
        else:
            vg_new = self.__unused_imposter_vgs.pop(0)
            self.__used_imposter_vgs += [vg_new]
        vertex_groups.create_vertex_group(obj=self.obj_new, vg_name=vg_new.name)
        return vg_new
