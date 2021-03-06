# ##### BEGIN GPL LICENSE BLOCK #####
#
# Part of the "toolbox" repository
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
import time
import importlib
import sys
import pathlib

# enable relative imports in case someone wants to open this file directly:
if __name__ == '__main__':  # makes sure this only happens when you run the script from inside Blender

    # INCREASE THIS VALUE IF YOU WANT TO ACCESS MODULES IN PARENT FOLDERS (for using something like "from ... import someModule")
    number_of_parents = 1  # default = 1

    original_path = pathlib.Path(bpy.data.filepath)
    parent_path = original_path.parent

    for i in range(number_of_parents):
        parent_path = parent_path.parent

    # remember, paths only work if they're strings
    str_parent_path = str(parent_path.resolve())
    # print(str_parent_path)
    if not str_parent_path in sys.path:
        sys.path.append(str_parent_path)

    # building the correct __package__ name
    relative_path = original_path.parent.relative_to(parent_path)
    with_dots = '.'.join(relative_path.parts)
    # print(with_dots)
    __package__ = with_dots

from . import (coordinates_stuff as _coordinates_stuff,
               create_real_mesh as _create_real_mesh,
               select_objects as _select_objects)
for modu in (_create_real_mesh, _coordinates_stuff, _select_objects):
    importlib.reload(modu)

#########################################################################################
###############                                                  ########################
###############Functions you may want to use for testing purposes########################
###############                                                  ########################
#########################################################################################

# DISCLAIMER:
# These functions are only for "throwaway" testing.
# After using some of these, your Blender Project will likely become clogged up with random objects, scenes, other Stuff.
# Things might just get deleted or changed
# Maybe even some bugs happen that will leave the Project unusable.
# THIS MEANS: DO NOT USE THESE ON ANY PROJECT YOU DON'T PLAN ON THROWING AWAY ANYWAY ( ctrl+z should still work though ).

# Additionally:
# Unlike the other scripts in this repository, some of the functions in this particular file are badly coded, for instance heavily relying on bpy.ops - something the internet will tell you is a bad thing.
# That's because this file is only supposed to be used for simple testing, and a few other reasons


class TestHelper():

    __context: bpy.types.Context
    __old_area_type: str

    def __init__(self, context):
        self.__context = context

    def create_subdiv_obj(self, subdivisions=0, type="PLANE"):
        """Creates a primitive mesh object, optionally with subdvisions applied.

        Parameters
        ----------
        subdivisions : int
            Amount of times you want the mesh to be suvdivided.
        type : one of {"PLANE","CUBE","UV_SPHERE","ICO_SPHERE","CYLINDER","CONE","TORUS","MONKEY"}
            The type of primitive Mesh you want to have created

        Returns
        -------
        bpy.types.Object
            Created object
        """
        self.switch_area()
        def raise_err():
            raise Exception(str(type) + " not a valid value.")
        possible_ops = {
            "PLANE": bpy.ops.mesh.primitive_plane_add,
            "CUBE": bpy.ops.mesh.primitive_cube_add,
            "UV_SPHERE": bpy.ops.mesh.primitive_uv_sphere_add,
            "ICO_SPHERE": bpy.ops.mesh.primitive_ico_sphere_add,
            "CYLINDER": bpy.ops.mesh.primitive_cylinder_add,
            "CONE": bpy.ops.mesh.primitive_cone_add,
            "TORUS": bpy.ops.mesh.primitive_torus_add,
            "MONKEY": bpy.ops.mesh.primitive_monkey_add,

        }
        possible_ops.get(type, raise_err)()
        obj = self.__context.active_object
        #mesh = obj.data
        bpy.ops.object.mode_set(mode='EDIT')
        for subdivs in range(subdivisions):
            bpy.ops.mesh.subdivide()
        bpy.ops.object.mode_set(mode='OBJECT')
        self.reset_area()
        return obj


    class ArmatureCreator():
        obj_armature: bpy.types.Object
        obj_monkey: bpy.types.Object
        bone_1: bpy.types.Bone
        bone_2: bpy.types.Bone
        bone_3: bpy.types.Bone


        def __init__(self) -> None:
            """Creates a simple armature object with three bones total.
            The bones are not connected, but they all influence the new monkey
            """
            # https://blender.stackexchange.com/questions/51684/python-create-custom-armature-without-ops
            def create_bone(armature, factor):
                bpy.ops.object.mode_set(mode='EDIT')
                bone = armature.edit_bones.new(name="bone")  # edit_bones only works in edit mode
                #bad stuff happens when you try to use that variable after switching back to object mode
                name = bone.name
                bone.head = (1, factor * 1, factor * 1)
                bone.tail = (factor * 2, factor * 2, factor * 2) 
                bpy.ops.object.mode_set(mode='OBJECT')
                return armature.bones.get(name)
            bpy.ops.mesh.primitive_monkey_add()
            monkey = self.__context.active_object
            monkey.scale.z = 3
            bpy.ops.object.armature_add()
            obj_armature = self.__context.active_object
            self.bone_1 = obj_armature.data.bones[0]  # one already exists by default
            self.bone_2 = create_bone(armature=obj_armature.data, factor=1)
            self.bone_3 = create_bone(armature=obj_armature.data, factor=-1)
            _select_objects.select_objects(context=self.__context, object_list=[monkey, obj_armature], deselect_others=True, active=obj_armature)
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            self.obj_monkey = monkey
            self.obj_armature = obj_armature


        def move_bones(self):
            """Moves and rotates the bones to do what armatures usually do.
            """
            posebones = self.obj_armature.pose.bones
            # bpy.ops.object.mode_set(mode='EDIT')
            for bone in [self.bone_1, self.bone_2, self.bone_3]:
                posebones[bone.name].rotation_mode = "XYZ" # for some reason that was quaternion by default for me
            posebones[self.bone_1.name].location = (-1,-0.5,0)
            posebones[self.bone_1.name].rotation_euler = (0.5,0.3,0.2)
            posebones[self.bone_2.name].location = (1.2,0.9,10)
            posebones[self.bone_2.name].rotation_euler=(9,9,9)
            posebones[self.bone_3.name].location = (100,80,99)
            posebones[self.bone_3.name].rotation_euler = (4,-4,0.01)
            # bpy.ops.object.mode_set(mode='OBJECT')

    def mess_around(self,switch_scenes=True, scenes_to_avoid=[]):
        """If you generally just want to f*ck up your project to see if your functions still work when settings change.
        Currently includes:
        - Creating a new object (gets deleted again)
        - Switches to Edit Mode at least once (returns to Object Mode at the end)
        - deselecting all objects
        - changing frames
        - (optional) switching to another scene

        Parameters
        ----------
        switch_scenes : bool
            If True, your active scene will be switched. If no other scenes exist yet, a new one will be created. Note that to change scenes you can use "C.window.scene = yourScene"
        scenes_to_avoid : bpy.types.Scene or list of scenes
            Only matters is switch_scenes is set to True. These scenes will not be switched too. Always includes the current scene.

        """
        self.switch_area()
        bpy.ops.mesh.primitive_cube_add()
        new_obj = self.__context.active_object
        for selected_objs in self.__context.selected_objects.copy():
            if selected_objs != new_obj:
                selected_objs.select_set(False)
        new_obj.select_set(True)
        self.__context.view_layer.objects.active = new_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='OBJECT')
        self.__context.scene.frame_set(self.__context.scene.frame_current + 8)
        self.__context.scene.frame_set(self.__context.scene.frame_current - 4)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='OBJECT')
        self.__context.view_layer.objects.active = new_obj
        bpy.ops.object.delete(use_global=False)
        # after deleting no object will be selected or active, so no mode can be set and will give us an error
        if switch_scenes == True:
            if type(scenes_to_avoid) != list:
                scenes_to_avoid = [scenes_to_avoid]
            current_scene = self.__context.scene
            scenes_to_avoid += [current_scene]
            scenes_to_avoid = set(scenes_to_avoid)  # removing duplicate scenes
            if len(bpy.data.scenes) == 1 or len(bpy.data.scenes) <= len(scenes_to_avoid):
                bpy.ops.scene.new(type='NEW')
            created = False
            for scene in bpy.data.scenes:
                if (scene in scenes_to_avoid) == False:
                    self.__context.window.scene = scene
                    created = True
                    break
            if created == False:
                raise Exception(
                    "Something went wrong when trying to change scenes.")
            bpy.ops.mesh.primitive_cube_add()
            bpy.ops.object.delete(use_global=False)
        self.reset_area()

    def are_objs_the_same(self, obj1, obj2, frame="CURRENT", apply_transforms_obj1=True, apply_transforms_obj2=True,
                          mute=True):
        """Checks if two objects, after everything (such as modifiers) has been applied, are the same (at a single frame) by comparing each vertex coordinate.

        Parameters
        ----------
        obj1 : bpy.types.Object
            First object
        obj2 : bpy.types.Object
            The object that's supposed to be compared agains the first object
        frame : str or int
            The frame for which you want to compare the two objects, by default "CURRENT"
        apply_transforms_obj1 : bool
            Whether you want to apply any transformations or keep them for comparing, by default True
        apply_transforms_obj2 : bool
            Whether you want to apply any transformations or keep them for comparing, by default True
        mute : bool
            Dont print an errormessage with some detail when objs are not the same?
        """
        self.switch_area()
        def error_message(messageStart="Comparison failed for", messageEnd=""):
            if mute == False:
                print(messageStart + " objects " + obj1.name +
                    " and " + obj2.name + " " + messageEnd)

        obj1_mesh_copy = _create_real_mesh.create_real_mesh_copy(
            context=self.__context, obj=obj1, frame=frame, apply_transforms=apply_transforms_obj1)
        obj2_mesh_copy = _create_real_mesh.create_real_mesh_copy(
            context=self.__context, obj=obj2, frame=frame, apply_transforms=apply_transforms_obj2)
        verts_obj1 = _coordinates_stuff.get_vertex_coordinates(mesh=obj1_mesh_copy)
        verts_obj2 = _coordinates_stuff.get_vertex_coordinates(mesh=obj2_mesh_copy)

        # don't need them anymore for what's left
        bpy.data.meshes.remove(obj1_mesh_copy)
        bpy.data.meshes.remove(obj2_mesh_copy)

        if len(verts_obj1) != len(verts_obj2):
            error_message(messageEnd="(Different amount of vertices)")
            self.reset_area()
            return False
        for vertIndex in range(len(verts_obj1)):
            v1 = verts_obj1[vertIndex]
            v2 = verts_obj2[vertIndex]
            if _coordinates_stuff.is_vector_close(vector1=v1, vector2=v2, ndigits=3) == False:
                error_message(messageEnd="(Different vertices found:\nIndex=" +
                            str(vertIndex) + "\nvert1 = " + str(v1) + "\nvert2 = " + str(v2))
                self.reset_area()
                return False
        self.reset_area()
        return True

    def switch_area(self):
        self.__old_area_type = self.__context.area.type
        self.__context.area.type = "CONSOLE"

    def reset_area(self):
        self.__context.area.type = self.__old_area_type


class Timing:

    @staticmethod
    def print_time(time_to_print, round_digits=2, text=""):
        """Prints the supplied value as time in seconds to the console.

        Parameters
        ----------
        time_to_print : float
            Time in seconds
        round_digits : int
            The digit you want the print statement to be rounded to.
            Regardless of choice, it will always include the first digit that isn't zero.
        text : str
            Any text you want to have printed at the first, e.g. "my cake required" -> "my cake required: 300.0 seconds"
        """
        if text != "":
            text += ":\t"

        # Get the position of the first digit that isnt 0
        first_digit_not_zero = 0
        time_to_test = time_to_print
        while int(time_to_test) == 0:
            first_digit_not_zero += 1
            time_to_test = time_to_test * 10
        if first_digit_not_zero > round_digits:
            round_digits = first_digit_not_zero

        print(text + str(round(time_to_print, round_digits)) + " seconds")

    @classmethod
    def measure_time_needed_to_run(cls, function, print_time=True, print_digits=2):
        """Returns the time a function needed to run. Optionally prints the result into the console.

        Parameters
        ----------
        function : function
            The function to test. NOTE THAT NO PARAMETERS CAN BE USED, so you might have to create a "temporary" function.
        print_time : bool
            Whether you want to have the result be printed to the console.
        print_digits : int
            If printTime==True, decides about the amount of digits that will be printed (e.g. 3 digits -> "functionX needed 0.128 seconds").
            Regardless, it will always include the first digit that isn't zero.

        Returns
        -------
        float
            The required time in seconds (not rounded).
        """
        t = -time.time()
        function()
        t += time.time()
        if print_time == True:
            cls.print_time(time_to_print=t, round_digits=print_digits,
                           text=function.__name__)
        return t



