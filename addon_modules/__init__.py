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

list_of_operators=set()
list_of_panels=set()

from .animation_general.animation_to_mesh_and_shapekeys.op_and_panel import OBJECT_OT_animate_with_shapekeys, OBJECT_PT_animate_with_shapekeys
list_of_operators.add(OBJECT_OT_animate_with_shapekeys)
list_of_panels.add(OBJECT_PT_animate_with_shapekeys)