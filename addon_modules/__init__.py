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


class OBJECT_PT_animation_misc(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_label = "Misc. Animation Utilities"
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        pass


list_of_operators = list()
list_of_panels = list()

list_of_panels.append(OBJECT_PT_animation_misc)

from .animation_general.animation_to_mesh_and_shapekeys.op_and_panel import OBJECT_OT_animate_with_shapekeys, OBJECT_PT_animate_with_shapekeys
list_of_operators.append(OBJECT_OT_animate_with_shapekeys)
list_of_panels.append(OBJECT_PT_animate_with_shapekeys)
OBJECT_PT_animate_with_shapekeys.bl_parent_id = OBJECT_PT_animation_misc.__name__

from .animation_general.object_imposters.op_and_panel import OBJECT_OT_create_imposter, OBJECT_PT_create_imposter
list_of_operators.append(OBJECT_OT_create_imposter)
list_of_panels.append(OBJECT_PT_create_imposter)
OBJECT_PT_create_imposter.bl_parent_id = OBJECT_PT_animation_misc.__name__

from .animation_general.mimic_deforms.op_and_panel import OBJECT_OT_mimic_deforms, OBJECT_PT_mimic_deforms
list_of_operators.append(OBJECT_OT_mimic_deforms)
list_of_panels.append(OBJECT_PT_mimic_deforms)
OBJECT_PT_mimic_deforms.bl_parent_id = OBJECT_PT_animation_misc.__name__

from .shrinkwrap_setup.op_and_panel import OBJECT_OT_setup_shrinkwrap_mods, OBJECT_OT_rotate_axis_obj,OBJECT_PT_setup_shrinkwrap_mods
list_of_operators.append(OBJECT_OT_setup_shrinkwrap_mods)
list_of_operators.append(OBJECT_OT_rotate_axis_obj)
list_of_panels.append(OBJECT_PT_setup_shrinkwrap_mods)
