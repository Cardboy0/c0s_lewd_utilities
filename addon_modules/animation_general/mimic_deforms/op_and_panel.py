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

from c0s_lewd_utilities.addon_utils.animation import mimic_deforms
from c0s_lewd_utilities.addon_utils.general.propertygroup_handler import get_props_from_string
from c0s_lewd_utilities.addon_utils.general.operator_handler import PollMethods as OpPollMethods
from c0s_lewd_utilities.addon_utils.general.panel_handler import PollMethods as PanelPollMethods, SpecialPanelPropTypes
from c0s_lewd_utilities.toolbox_1_0_0 import select_objects
from c0s_lewd_utilities.names import is_print_enabled


_data_path = "c0_lewd_utilities.animation.mimic_deforms"


class OBJECT_OT_mimic_deforms(bpy.types.Operator):
    bl_idname = "object.mimic_deforms"
    bl_label = "Adds a geometry node modifier to mimic the deformations of an object with the same topology"
    bl_description = bl_label
    bl_info = {"UNDO"}

    def execute(self, context):
        obj_orig = context.active_object
        props = get_props_from_string(object=obj_orig, datapath=_data_path)
        obj_target = props.target_obj
        name_vg_mask = props.vg_mask
        if name_vg_mask == "":
            vg_mask = None
        else:
            vg_mask = obj_orig.vertex_groups.get(name_vg_mask, False)

        if vg_mask==False:
            self.report({'ERROR'}, "No vertex group with the name '"+name_vg_mask+"' could be found!")
            return {'CANCELLED'}
        elif mimic_deforms.MimicDeforms.is_valid(context=context, obj_orig=obj_orig, obj_target=obj_target):
            helper = mimic_deforms.MimicDeforms(context=context, obj=obj_orig,vertex_group=vg_mask)
            helper.fill(target_obj=obj_target)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Your object and '"+obj_target.name+"' show different amounts of vertices in viewport!")
            return {'CANCELLED'}

    @classmethod
    def poll(clss, context):
        obj = context.active_object
        props = get_props_from_string(object=obj, datapath=_data_path)
        return OpPollMethods.is_object_with_mesh(obj=obj) and props.target_obj != None


class OBJECT_PT_mimic_deforms(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_label = "Mimic Animation"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        obj_orig = context.active_object
        props = get_props_from_string(object=obj_orig, datapath=_data_path)

        layout.prop(
            data=props,
            property="target_obj",
            text="Target Object"
        )
        
        SpecialPanelPropTypes.get_vertex_group_panel_prop(
            layout=layout,
            data=props,
            property_name="vg_mask",
            obj=obj_orig,
            text="Vertex Mask"
        )        

        layout.operator(
            operator=OBJECT_OT_mimic_deforms.bl_idname,
            text="Add Mimic Modifier!"
        )

    @classmethod
    def poll(self, context):
        obj = context.active_object
        return PanelPollMethods.is_object_with_mesh(obj=obj)
