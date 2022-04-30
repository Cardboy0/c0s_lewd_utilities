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
from c0s_lewd_utilities.toolbox_1_0_0 import create_real_mesh, shapekeys, everything_key_frames
from c0s_lewd_utilities.addon_utils.context_related.area_type_changer import AreaTypeChanger


class AnimationToShapekeyConverter():

    __obj_orig: bpy.types.Object
    __obj_new: bpy.types.Object
    __mesh_new: bpy.types.Mesh
    __apply_transforms: bool
    __keep_vertex_groups: bool
    __keep_materials: bool
    main_context: bpy.types.Context

    def __init__(self, main_context, obj_orig, apply_transforms=True, keep_vertex_groups=True, keep_materials=True):
        """Converts the animation of an object to keyframed shapekeys (one shapekey for each frame).\\
        Almost anything that affects the geometry will be converted, this includes altered mesh topology from modifiers (such as subdivision surface mods),
        shapekeys, transforms (can be disabled), etc.

        The original object will be left alone, a new one will be created instead that has the shapekeys and the new topology, or an already existing
        object can be chosen as well.

        Parameters
        ----------
        main_context : bpy.types.Context
            Your current context
        obj_orig : bpy.types.Object
            Object that has the animation to be converted
        apply_transforms : bool
            When converting the animation, convert the transforms as well
        keep_vertex_groups : bool
            Include the original vertex groups and their values on the new object (not used if the new object is given by the user)
        keep_materials : bool
            Include the original materials and their values on the new object (not used if the new object is given by the user)\\
            Not properly tested.
        """
        self.main_context = main_context
        self.__obj_orig = obj_orig
        self.__apply_transforms = apply_transforms
        self.__keep_vertex_groups = keep_vertex_groups
        self.__keep_materials = keep_materials

    # TODO (future): enable using multiple objects to get one combined object

    def set_obj_new(self, obj_new=None, frame="CURRENT") -> bpy.types.Object:
        """Sets the new object to use. If you want to add the shapekeys to an already existing object,
        you can specify that object instead and no new one will be created.

        Parameters
        ----------
        obj_new : None or bpy.types.Object
            If None, a new object will be created that gets the shapekeys.\\
            If object, no new object will be created and the shapekeys will be added to the specified object instead.
            The specified object must have the same topology as the original object looks like in the viewport
            (i.e. same amount of vertices as if you had every modifier of the original object applied, not every modifier disabled)
        frame : int or "CURRENT"
            Only used if obj_new=None. The new object will have the shape of the original object at that frame.

        Returns
        -------
        bpy.types.Object
            New object or just the one you gave.
        """
        if obj_new == None:
            # create_real_mesh requires correct area type to be active
            area_orig = AreaTypeChanger.change_area_to_good_type(context=self.main_context)
            self.__mesh_new = create_real_mesh.create_real_mesh_copy(
                context=self.main_context,
                obj=self.__obj_orig,
                frame=frame,
                apply_transforms=self.__apply_transforms,
                keep_vertex_groups=self.__keep_vertex_groups,
                keep_materials=self.__keep_materials
            )
            self.__obj_new = create_real_mesh.create_new_obj_for_mesh(
                context=self.main_context,
                name=self.__obj_orig.name + " with keyframed shapekeys",
                mesh=self.__mesh_new
            )
            AreaTypeChanger.reset_area(area_orig)
        else:
            self.__obj_new = obj_new
            self.__mesh_new = obj_new.data

        # create a base shapekey if not already present
        if hasattr(self.__mesh_new.shape_keys, "reference_key") == False:
            shapekey_base = self.__obj_new.shape_key_add(name="Basis")

        return self.__obj_new

    def is_given_obj_new_valid(self):
        """
        Checks if obj_new provided by set_obj_new() earlier is actually valid.
        This just checks for the same amount of vertices if obj_orig had everything applied.

        Returns
        -------
        bool
            Is valid or not?
        """
        # create_real_mesh requires correct area type to be active
        area_orig = AreaTypeChanger.change_area_to_good_type(context=self.main_context)
        mesh_obj_orig_applied = create_real_mesh.create_real_mesh_copy(
            context=self.main_context,
            obj=self.__obj_orig,
            frame="CURRENT",
            apply_transforms=False,
            keep_vertex_groups=False,
            keep_materials=False
        )
        if len(mesh_obj_orig_applied.vertices) != len(self.__mesh_new.vertices):
            is_valid = False
        else:
            is_valid = True
        AreaTypeChanger.reset_area(area_orig)
        bpy.data.meshes.remove(mesh=mesh_obj_orig_applied)
        return is_valid

    def _get_mesh_current_shape(self, frame) -> bpy.types.Mesh:
        """Gets the shape of the original object at a certain frame, but as if everything (such as modifiers) had been applied.

        Used by add_frame_as_shapekey()

        Parameters
        ----------
        frame : int
            The shape of the original object at that frame will be used.

        Returns
        -------
        bpy.types.Mesh
            Created mesh
        """
        return create_real_mesh.create_real_mesh_copy(
            context=self.main_context,
            obj=self.__obj_orig,
            frame=frame,
            apply_transforms=self.__apply_transforms,
            keep_vertex_groups=False,  # we only care about the vertex locations of the mesh
            keep_materials=False)

    def _create_key_frames_for_single_frame(self, frame, fcurve) -> None:
        """Keyframes a shapekey to be active only at the specified frame and no other.

        Used by add_frame_as_shapekey()

        Parameters
        ----------
        frame : int
            Single frame at which the shapekey is supposed to be active
        fcurve : bpy.types.FCurve
            Created FCurve of the shapekey.
        """
        everything_key_frames.create_key_frames_fast(fcurve=fcurve, values=[frame - 1, 0, frame, 1, frame + 1, 0])

    def add_frame_as_shapekey(self, frame="CURRENT", print_frame=False) -> bpy.types.ShapeKey:
        """Adds the shape of the original object at the specified frame to the new object.

        Uses AreaTypeChanger, meaning it might speed things up if you use it once before a loop to prevent frequent area changes.

        Parameters
        ----------
        frame : int or "CURRENT"
            Frame from which to take the shape from.
        print_frame : bool
            Print the current frame to the console?

        Returns
        -------
        bpy.types.ShapeKey
            New, created shapekey
        """
        area_orig = AreaTypeChanger.change_area_to_good_type(context=self.main_context)
        if frame == "CURRENT":
            frame = self.main_context.scene.frame_current
        if print_frame == True:
            print("Current frame: ", frame)
        mesh_current_shape = self._get_mesh_current_shape(frame=frame)
        shapekey_new = shapekeys.create_shapekey(
            obj=self.__obj_new,
            reference=mesh_current_shape)
        shapekey_new.name = "frame_" + str(frame)
        datapath_to_sk = shapekey_new.path_from_id()
        action = everything_key_frames.get_or_create_action(something=self.__mesh_new.shape_keys)
        fcurve = action.fcurves.new(datapath_to_sk + ".value")
        self._create_key_frames_for_single_frame(frame=frame, fcurve=fcurve)
        bpy.data.meshes.remove(mesh_current_shape)
        AreaTypeChanger.reset_area(area_orig)
        return shapekey_new

    def go_over_multiple_frames_at_once(self, frame_start, frame_end, print_frames=False):
        """Calls add_frame_as_shapekey() in a loop over the specified frame range.

        Parameters
        ----------
        frame_start : int
            First frame of the animation
        frame_end : int
            Last frame of the animation
        print_frames : bool
            Print the current frames to the console?
        """
        area_orig = AreaTypeChanger.change_area_to_good_type(context=self.main_context)
        if print_frames == True:
            print("\n\nStarting conversion of animation to shapekeys for object '"+ str(self.__obj_orig.name)+"'")
        for f in range(frame_start, frame_end + 1):
            self.add_frame_as_shapekey(frame=f, print_frame=print_frames)
        if print_frames == True:
            print("Conversion finished.")
        AreaTypeChanger.reset_area(area_orig)
