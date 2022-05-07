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
from c0s_lewd_utilities.toolbox_1_0_0.advanced.node_helper import GeometryNodesModifierHandler
from c0s_lewd_utilities.toolbox_1_0_0 import create_real_mesh, modifiers
from c0s_lewd_utilities.addon_utils.context_related.area_type_changer import AreaTypeChanger


class MimicDeforms():
    mod_geo_node: bpy.types.NodesModifier
    __geo_handler: GeometryNodesModifierHandler
    __obj: bpy.types.Object
    node_position: bpy.types.GeometryNodeInputPosition
    node_transfer_attr: bpy.types.GeometryNodeAttributeTransfer
    node_set_position: bpy.types.GeometryNodeSetPosition
    node_object_info: bpy.types.GeometryNodeObjectInfo
    __vertex_group: bpy.types.VertexGroup
    socket_vg_mask: bpy.types.NodeSocketBool

    def __init__(self, context, obj, vertex_group=None):
        """Ever had two objects with the same topology (vertices) but different deformations, and wanted one object to mimic the deformation of the other object?\\
        With this class, you can do that!

        Based on a Geometry Node modifier. The required node group layout is shown in mimic_deforms_nodegroup_layout.jpg, which should be in the same folder as this class.

        Parameters
        ----------
        context: bpy.types.Context
            Current context (such as bpy.context)
        obj : bpy.types.Object
            The object that wants to mimic some deformations.
        vertex_group : None OR bpy.types.VertexGroup
            Vertex group to act as a mask for the deformations.\\
            If None, no mask will be used.
        """
        self.__obj = obj
        self.mod_geo_node = obj.modifiers.new(type='NODES', name='Geometry Node Modififer')
        modifiers.move_modifer_to_position_in_stack(context=context, modifier=self.mod_geo_node, position=-1)
        self.__geo_handler = GeometryNodesModifierHandler(self.mod_geo_node)
        self.__vertex_group = vertex_group

    def fill(self, target_obj):
        """Fill the node group of the geometry node modifier with, well, nodes.

        Parameters
        ----------
        target_obj : bpy.types.Object
            Object to mimic the deformations off.
        """
        gh = self.__geo_handler
        node_set_position = gh.add_node('GeometryNodeSetPosition')
        node_object_info = gh.add_node('GeometryNodeObjectInfo')
        node_position = gh.add_node('GeometryNodeInputPosition')
        node_transfer_attr = gh.add_node('GeometryNodeAttributeTransfer')

        node_object_info.inputs['Object'].default_value = target_obj

        node_transfer_attr.data_type = 'FLOAT_COLOR'
        node_transfer_attr.mapping = 'INDEX'
        node_transfer_attr.domain = 'POINT'

        if self.__vertex_group != None:
            gh.add_input('NodeSocketBool', 'Mask')
            self.socket_vg_mask = gh.main_input_node.outputs['Mask']
            identifier = self.socket_vg_mask.identifier
            self.mod_geo_node[identifier + "_use_attribute"] = True
            self.mod_geo_node[identifier + "_attribute_name"] = self.__vertex_group.name
        else:
            self.socket_vg_mask = None

        gh.main_input_node.location = (-340, 0)
        gh.main_output_node.location = (260, 0)
        node_set_position.location = (-40, 20)
        node_transfer_attr.location = (-240, -160)
        node_object_info.location = (-520, -120)
        node_position.location = (-520, -340)

        self.node_set_position = node_set_position
        self.node_object_info = node_object_info
        self.node_position = node_position
        self.node_transfer_attr = node_transfer_attr

        self.__connect()
        gh.deselect_all_nodes()

    def __connect(self):
        """Properly connects the nodes.
        """
        gh = self.__geo_handler
        gh.connect_nodes(self.node_object_info.outputs["Geometry"], self.node_transfer_attr.inputs["Target"])
        input_attr = gh.get_input_socket_by_identifier(node=self.node_transfer_attr, socket_identifier='Attribute_002')
        gh.connect_nodes(self.node_position.outputs["Position"], input_attr)
        output_attr = gh.get_output_socket_by_identifier(node=self.node_transfer_attr, socket_identifier='Attribute_002')
        gh.connect_nodes(output_attr, self.node_set_position.inputs["Position"])
        if self.__vertex_group != None:
            gh.connect_nodes(self.socket_vg_mask, self.node_set_position.inputs["Selection"])
        gh.connect_nodes(gh.main_input_node.outputs["Geometry"], self.node_set_position.inputs["Geometry"])
        gh.connect_nodes(self.node_set_position.outputs["Geometry"], gh.main_output_node.inputs["Geometry"])

    @classmethod
    def is_valid(clss, context, obj_orig, obj_target):
        """Checks if two objects are eligible to be used for this class.

        Currently just checks if both objects actually have meshes and if they show the same number of vertices in viewport.

        Parameters
        ----------
        context : bpy.types.Context
            bpy.context or similar
        obj_orig : bpy.types.Object
            Object that's supposed to later mimic the deformations
        obj_target : bpy.types.Object
            Object where to later take the deformations from

        Returns
        -------
        bool
        """
        if type(obj_orig.data) != bpy.types.Mesh or type(obj_target.data) != bpy.types.Mesh:
            return False

        area_orig = AreaTypeChanger.change_area_to_good_type(context=context)
        mesh_orig_applied = create_real_mesh.create_real_mesh_copy(
            context=context,
            obj=obj_orig,
            frame="CURRENT",
            apply_transforms=False,
            keep_vertex_groups=False,
            keep_materials=False)

        mesh_target_applied = create_real_mesh.create_real_mesh_copy(
            context=context,
            obj=obj_target,
            frame="CURRENT",
            apply_transforms=False,
            keep_vertex_groups=False,
            keep_materials=False)
        AreaTypeChanger.reset_area(area_orig)

        if len(mesh_orig_applied.vertices) != len(mesh_target_applied.vertices):
            return False

        return True
