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
from c0s_lewd_utilities.addon_utils.context_related.area_type_changer import AreaTypeChanger
from c0s_lewd_utilities.addon_utils.general.propertygroup_handler import get_props_from_string
from c0s_lewd_utilities.addon_utils.general.operator_handler import PollMethods as OpPollMethods, SpecialOperatorPropTypes
from c0s_lewd_utilities.addon_utils.general.panel_handler import PollMethods as PanelPollMethods, SpecialPanelPropTypes
from c0s_lewd_utilities.toolbox_1_0_0 import select_objects
from c0s_lewd_utilities.names import is_print_enabled
from .code.main import Main as SetupHelperMain
from .code.create_obj_axis import ObjAxisHandler

_data_path = "c0_lewd_utilities.shrinkwrap_setup"


class OBJECT_OT_setup_shrinkwrap_mods(bpy.types.Operator):
    bl_idname = "object.setup_shrinkwrap_mods"
    bl_label = ("Create an imposter object of your current one and add a bunch of stuff to it so that it can shrinkwrap certain areas to a target object." +
                "\nImposter object will also have some custom properties")
    bl_description = bl_label
    bl_info = {"UNDO"}

    def execute(self, context):
        obj_orig = context.active_object
        props = get_props_from_string(object=obj_orig, datapath=_data_path)
        obj_target = props.target_obj
        obj_axis_parent = props.axis_parent
        bone_axis_parent_name = props.bone_parent

        vg_target = SpecialOperatorPropTypes.get_vertex_group(obj=obj_orig, vg_name=props.target_vg)
        if vg_target == None:
            self.report({'ERROR'}, "You must use a vertex group!")
            return {'CANCELLED'}
        if vg_target == False:
            self.report({'ERROR'}, "No vertex group with the name '" + props.target_vg + "' could be found!")
            return {'CANCELLED'}

        if obj_axis_parent != None and type(obj_axis_parent.data) == bpy.types.Armature:
            bone_axis_parent = SpecialOperatorPropTypes.get_bone(obj_armature=obj_axis_parent, bone_name=bone_axis_parent_name)
            if bone_axis_parent == False:
                self.report({'ERROR'}, "No bone with the name '" + props.target_vg + "' could be found!")
                return {'CANCELLED'}
        else:
            bone_axis_parent = None

        if SetupHelperMain.is_valid(obj_orig=obj_orig, obj_target=obj_target) == False:
            self.report({'ERROR'}, "'" + obj_orig.name + "' and '" + obj_target.name + "' must both have a mesh!")
            return {'CANCELLED'}

        setup_helper = SetupHelperMain()
        setup_helper.run(
            context=context,
            obj_main=obj_orig,
            vg_target=vg_target,
            obj_target=obj_target,
            axis_parent=obj_axis_parent,
            axis_parent_bone=bone_axis_parent)

        area_orig = AreaTypeChanger.change_area_to_good_type(context=context)
        select_objects.select_objects(context=context, object_list=[setup_helper.obj_imposter, setup_helper.obj_axis], deselect_others=True)
        AreaTypeChanger.reset_area(area_orig)

        return {'FINISHED'}

    @classmethod
    def poll(self, context):
        obj_orig = context.active_object
        props = get_props_from_string(object=obj_orig, datapath=_data_path)
        obj_target = props.target_obj
        vg_name = props.target_vg

        return (obj_orig != None and type(obj_orig.data) == bpy.types.Mesh
                and obj_target != None and type(obj_target.data) == bpy.types.Mesh
                and vg_name != "")


class OBJECT_OT_rotate_axis_obj(bpy.types.Operator):
    bl_idname = "object.rotate_axis_obj"
    bl_label = "Is intended for the created axis object from the shrinkwrap setup, but can be used on any object.\nRotates the object by 90 degrees in one of the three directions"
    bl_description = bl_label
    bl_info = {"UNDO"}
    # note: this operator only supports XYZ Euler Rotation, because that's the type of rotation the axis object will have.

    direction: bpy.props.EnumProperty(items=[('x', 'X', '', 0),
                                             ('y', 'Y', '', 1),
                                             ('z', 'Z', '', 2)])

    def execute(self, context):
        obj = context.active_object

        direction = self.direction
        if direction in {"x", "y", "z"}:
            ObjAxisHandler.rotate_by_90_degrees(obj=obj, axis=direction)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Only accepts x,y or z as directions")
            return {'CANCELLED'}


class OBJECT_PT_setup_shrinkwrap_mods(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_label = "Setup Shrinkwrap"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        obj_orig = context.active_object

        # depending on whether we have a mesh object or an Empty object selected, the panel will look different.
        # The only reason a special panel for Empties exists is because the created axis object is an Empty and includes three buttons to rotate it.

        if obj_orig != None and type(obj_orig.data) == bpy.types.Mesh:
            # Object has a Mesh
            props = get_props_from_string(object=obj_orig, datapath=_data_path)
            obj_axis_parent = props.axis_parent

            column_main = layout.column()
            column_main.prop(data=props, property="target_obj", text="Target object")
            SpecialPanelPropTypes.get_vertex_group_panel_prop(layout=column_main,
                                                              data=props,
                                                              property_name="target_vg",
                                                              obj=obj_orig,
                                                              text="Vertex Mask")

            column_axis_parents = layout.column()
            column_axis_parents.prop(data=props, property="axis_parent", text="Axis Parent")

            if obj_axis_parent != None and type(obj_axis_parent.data) == bpy.types.Armature:
                SpecialPanelPropTypes.get_bone_panel_prop(layout=column_axis_parents,
                                                          data=props,
                                                          property_name="bone_parent",
                                                          armature=obj_axis_parent.data,
                                                          text="Axis Parent Bone")

            layout.operator(
                operator=OBJECT_OT_setup_shrinkwrap_mods.bl_idname,
                text="Setup Shrinkwrap Stuff"
            )

        elif obj_orig != None and obj_orig.data == None:
            layout.label(text="Rotate 90 degrees")
            # Object is an "Empty"
            layout.operator_enum(operator=OBJECT_OT_rotate_axis_obj.bl_idname,
                                 property="direction")

    @classmethod
    def poll(self, context):
        obj = context.active_object

        return (PanelPollMethods.is_object_with_mesh(obj=obj)
                or (obj != None and obj.data == None)  # allows empties as well, for when the created axis empty gets selected
                )
