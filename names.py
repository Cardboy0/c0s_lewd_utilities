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


# Collection of often used string values.
# By assigning them to variables here once and then using those variables instead of manually typing the names again and again everywhere,
# we save us time and problems when we want to rename a name.

addon_name = "C0s Lewd Utilities"  # name of the module. The bl_info dictionary in __init__.py is supposed to have the same name,
# but cannot actually access the variable for reasons.

prints_enabled_name = "prints_enabled"

def is_print_enabled(context):
    """Is the option to print things into Blender console for the user enabled?"""
    return context.workspace.c0_lewd_utilities.prints_enabled
