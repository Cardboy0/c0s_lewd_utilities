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


class AreaTypeChanger():
    """
    Provides methods to deal with the area type of the current window.

    This is important because, depending on the current area type, stuff
    in Blender can behave differently or just straight up not work.

    If your add-on for example adds a panel with an operator button to the object properties panels,
    context.area.type will be "PROPERTIES" for the code inside that operator,
    instead of "CONSOLE" or "TEXT_EDITOR" (like it is usually when you run your code manually in the console or text editor).
    """

    good_types = {"CONSOLE",
                  "VIEW_3D",
                  "TEXT_EDITOR"}

    @classmethod
    def change_area_to_good_type(clss, context) -> tuple:
        """Change the current context area type to a type that's considered "good", i.e. less likely to give you bugs.

        Change only takes place if the current type isn't already one of the good types.

        Parameters
        ----------
        context : bpy.types.Context
            Your context.

        Returns
        -------
        tuple
            A tuple that you can use for the reset_area() method to reset the area properties to its original ones.
        """
        area_type_orig = context.area.type
        if (area_type_orig in clss.good_types) == False:
            context.area.type = "CONSOLE"
        return (context, area_type_orig)

    @classmethod
    def reset_area(clss, area_change_result: tuple):
        """Resets the area properties back to how they were when you ran a change_area_to_good_type() method.

        Change only takes place if the current properties aren't already equal to the old ones.

        Parameters
        ----------
        area_change_result : tuple
            The result you got from a change_area_to_good_type() method you ran earlier.
        """
        context = area_change_result[0]
        area_type_orig = area_change_result[1]
        if context.area.type != area_type_orig:
            context.area.type = area_type_orig
