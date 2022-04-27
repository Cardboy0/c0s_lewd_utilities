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

from c0s_lewd_utilities.addon_utils.animation import animation_to_shapekeys
from c0s_lewd_utilities.addon_utils.context_related.area_type_changer import AreaTypeChanger
from c0s_lewd_utilities.addon_utils.general.propertygroup_handler import get_props_from_string
from c0s_lewd_utilities.addon_utils.general.operator_handler import PollMethods as OpPollMethods
from c0s_lewd_utilities.addon_utils.general.panel_handler import PollMethods as PanelPollMethods
from c0s_lewd_utilities.toolbox_1_0_0 import create_real_mesh, select_objects


_data_path = "c0_lewd_utilities.animation.shapekey_convert"


class OBJECT_OT_animate_with_shapekeys(bpy.types.Operator):
    bl_idname = "object.animate_with_shapekeys"
    bl_label = "Converts the animation of an object to keyframed shapekeys and adds them to a new or another already existing object."
    bl_description = "Converts the animation of an object to keyframed shapekeys and adds them to a new or another already existing object"
    bl_info = {"UNDO"}

    def execute(self, context):
        obj = context.active_object
        props = get_props_from_string(object=obj, datapath=_data_path)
        frame_first = props.frame_start
        frame_last = props.frame_end
        only_current_frame = props.only_current_frame
        apply_transforms = props.apply_transforms
        obj_target = props.target_obj

        area_orig = AreaTypeChanger.change_area_to_good_type(context)
        # some functions below have problems working if context.area.type is "PROPERTIES", and this will be the case with this operator.


        # materials and vertex groups get copied once at the beginning by default
        if only_current_frame == True:
            mesh_new = create_real_mesh.create_real_mesh_copy(
                context=context,
                obj=obj,
                frame="CURRENT",
                apply_transforms=apply_transforms,
                keep_vertex_groups=True,
                keep_materials=True)
            obj_new = create_real_mesh.create_new_obj_for_mesh(context=context, name=obj.name + "_shape_applied", mesh=mesh_new)

        else:
            sk_converter = animation_to_shapekeys.AnimationToShapekeyConverter(
                main_context=context,
                obj_orig=obj,
                apply_transforms=apply_transforms,
                keep_vertex_groups=True,
                keep_materials=True)
            obj_new = sk_converter.set_obj_new(obj_new=obj_target, frame=frame_first)
            if obj_target != None:
                # means we use an already existing object and should check if it's actually valid
                if sk_converter.is_given_obj_new_valid() == False:
                    AreaTypeChanger.reset_area(area_orig)
                    self.report({'ERROR'}, "target object does not have the same topology of your main object (if every modifier had been applied).")
                    print(self.as_keywords())
                    return {'CANCELLED'}

            sk_converter.go_over_multiple_frames_at_once(frame_start=frame_first, frame_end=frame_last)

        select_objects.select_objects(context=context, object_list=[obj_new], deselect_others=True)

        AreaTypeChanger.reset_area(area_orig)
        return {'FINISHED'}

    @classmethod
    def poll(clss, context):
        obj = context.active_object
        return OpPollMethods.is_object_with_mesh(obj=obj)


class OBJECT_PT_animate_with_shapekeys(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_label = "Apply Animation To Shapekeys"
    bl_options = {'DEFAULT_CLOSED'}
    # bl_parent_id = "OBJECT_PT_c0_general_utilities_main"

    def draw(self, context):
        layout = self.layout
        # TODO: find better description method
        # layout.label(text='Creates an "applied" version of your object.', translate=False, icon='INFO')
        # layout.label(text='Animation happens through shapekeys', translate=False)
        layout.use_property_split = True

        obj = context.active_object
        props = get_props_from_string(object=obj, datapath=_data_path)
        frame_first = props.frame_start
        frame_last = props.frame_end
        only_current_frame = props.only_current_frame
        apply_transforms = props.apply_transforms
        obj_target = props.target_obj

        layout.prop(
            data=props,
            property="only_current_frame",
            text="Only Convert Current Frame"
        )

        # Frames and target object
        column_frames = layout.column()
        column_frames.prop(
            data=props,
            property="frame_start",
            text="Starting Frame")
        column_frames.prop(
            data=props,
            property="frame_end",
            text="End Frame")
        column_frames.active = (only_current_frame == False)
        obj_target_selector = layout.column()
        obj_target_selector.prop(
            data=props,
            property="target_obj",
            text="Add Shapekeys to..."
        )
        obj_target_selector.active = (only_current_frame == False)

        # transforms
        column_apply_transforms = layout.column()
        column_apply_transforms.prop(
            data=props,
            property="apply_transforms",
            text="Apply Transforms")

        layout.operator(
            operator=OBJECT_OT_animate_with_shapekeys.bl_idname,
            text="Convert!"
        )

    @classmethod
    def poll(clss, context):
        obj = context.active_object
        return PanelPollMethods.is_object_with_mesh(obj=obj)
