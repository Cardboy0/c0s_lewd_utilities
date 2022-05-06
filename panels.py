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

# All panels of the add-on, including the main ones, i.e. those which will contain all other add-on panels.

import bpy
from c0s_lewd_utilities import names

all_object_child_panels = list()


class OBJECT_PT_c0_lewd_utilities_main(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_order = 100  # custom properties panel SHOULD be last with a value of 1000, but this is acting weird
    bl_context = "object"
    bl_label = names.addon_name
    # bl_options = {'DEFAULT_CLOSED'}

    # Note: to have this panel be used as a parent for other panels, those must have bl_parent_id = thisClass.__name__

    def draw(self, context):
        # self.layout.col()
        layout = self.layout
        layout.use_property_split = True

        layout.prop(
            data=context.workspace.c0_lewd_utilities,
            property=names.prints_enabled_name,
            text="Enable print statements in console"
        )


from c0s_lewd_utilities.addon_modules import list_of_panels
all_object_child_panels.extend(list_of_panels)


def register():
    bpy.utils.register_class(OBJECT_PT_c0_lewd_utilities_main)
    for object_panel in all_object_child_panels:
        if hasattr(object_panel, "bl_parent_id") == False:
            # every panel that does not have a parent panel of its own will get the main object panel as its parent.
            object_panel.bl_parent_id = OBJECT_PT_c0_lewd_utilities_main.__name__
        bpy.utils.register_class(object_panel)


def unregister():
    # unregister child panels first, then the main ones.
    for object_panel in all_object_child_panels:
        bpy.utils.unregister_class(object_panel)
    bpy.utils.unregister_class(OBJECT_PT_c0_lewd_utilities_main)
