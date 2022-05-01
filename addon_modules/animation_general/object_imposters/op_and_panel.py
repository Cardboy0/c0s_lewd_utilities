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

from c0s_lewd_utilities.addon_utils.animation.imposter_creator import ImposterCreator
from c0s_lewd_utilities.addon_utils.context_related.area_type_changer import AreaTypeChanger
from c0s_lewd_utilities.addon_utils.general.propertygroup_handler import get_props_from_string
from c0s_lewd_utilities.addon_utils.general.operator_handler import PollMethods as OpPollMethods
from c0s_lewd_utilities.addon_utils.general.panel_handler import PollMethods as PanelPollMethods
from c0s_lewd_utilities.toolbox_1_0_0 import select_objects

_data_path = "c0_lewd_utilities.animation.imposter_creator"

class OBJECT_OT_create_imposter(bpy.types.Operator):
    bl_idname = "object.create_imposter_object"
    bl_label = "Creates a new object that will always display the current geometry of your original object, even if that geometry changes."
    bl_description = bl_label
    bl_info = {"UNDO"}

    def execute(self, context):
        obj_orig = context.active_object
        props = get_props_from_string(object=obj_orig, datapath=_data_path)
        mimic_transforms_enabled = props.mimic_transforms
        imposter_creator = ImposterCreator(obj=obj_orig)
        imposter_creator.add_constraints(hidden=(mimic_transforms_enabled == False))
        imposter_creator.transfer_other_data(vertex_groups=True, uv_maps=True, vertex_colors=True, material_slots=True)
        orig_area = AreaTypeChanger.change_area_to_good_type(context=context)
        select_objects.select_objects(context=context, object_list=[imposter_creator.obj_new])
        AreaTypeChanger.reset_area(orig_area)
        return {'FINISHED'}
        

    @classmethod
    def poll(clss, context):
        obj = context.active_object
        return OpPollMethods.is_object_with_mesh(obj=obj)



class OBJECT_PT_create_imposter(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_label = "Imposter Object Creator"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        obj_orig = context.active_object
        props = get_props_from_string(object=obj_orig, datapath=_data_path)
        mimic_transforms_enabled = props.mimic_transforms

        layout.prop(
            data=props,
            property="mimic_transforms",
            text="Also mimic object transforms?"
        )
        layout.operator(
            operator=OBJECT_OT_create_imposter.bl_idname,
            text="Create Imposter"
        )

    @classmethod
    def poll(self, context):
        obj = context.active_object
        return PanelPollMethods.is_object_with_mesh(obj=obj)