# shrinkwrapper

Ever used the [shrinkwrap modifier](https://docs.blender.org/manual/en/latest/modeling/modifiers/deform/shrinkwrap.html) before?

Its **Project** Wrap Method is cool in theory, but there are a lot of limitations and problems you will walk into sooner or later if you want to do more advanced stuff.  

For example, you will see that you can only do the projecting along the local X,Y or Z axis, using your own direction isn't possible.  
At other times, the projections will suddenly look wrong at different coordinates without you knowing the reason why, or being able to find a fix.

That's why I set up scripts that add **a lot** of modifiers to make it work as best as possible.

## Basic Usage
In general, to run the script you will only need an object of your choice, a vertex group to act as a vertex mask, and another object as the shrinkwrap target.

Then, in [main.py](main.py), create a new `Main()` Object and `run()` it. It will set up everything.

Additionally, you can also provide a parent object for the newly created axis object (see description further below).


## Results:
After everything has run, you will end up with three new objects:

1. **obj_static:**   
    A simple and hidden "Empty" object whose whole job it is to literally just stay at location (0,0,0) and receive no transformations whatsoever. It's required by the hook modifier of the imposter object.    
    To make it idiot-proof, it has constraints that prevent transformations.  
2. **obj_axis:**    
    Another Empty object, displayed in viewport as an arrow. The direction of this object directly influences the direction of the shrinkwrap.  
    Depending on if additional objects had been provided at the start, it can be parented (via constraints) to other objects to make using it easier.
3. **obj_imposter:**    
    The main result, an imposter object of the original object that displays the shrinkwrap stuff.    
    - "Imposter" means that this object will always look like the original object, even if you change the geometry of the original object. That's accomplished by using a geometry node modifier.
    - The imposter object has a few custom properties which are linked to some of the modifier data via Drivers. These can be changed by the user to change multiple certain values of the modifiers at once, like the displace strength or visibility of some modifiers.  
    To access these custom properties, the imposter object must be selected and you need to open the side panel in the 3D view panel (press the'n' key for that). The 'Intern' tab has a section at the bottom called 'properties'.
    - The reason why an imposter object is used to show the shrinkwrap stuff instead of just dealing with the original object is because a lot of changes need to be done to make proper shrinkwrapping possible. The user probably doesn't want a bunch of new modifiers and constraints on his original object that could f*ck everything else up, in addition to it just being less likely to cause bugs.   
    - For the list of mods and constraints, and what they do, look below.

## Mods, Constraints and Vertex Groups of the imposter object
As said before, the imposter object has a bunch of new modifiers and constraints added to make proper shrinkwrapping possible. I will try to explain what they do.   

Some notes:
- The order of the modifiers is crucial.
- Modifiers that exist for the purpose of manipulating vertex groups will not be included in the modifier list, although I will still mention them.

### **Required vertex groups**:
The only vertex group we originally get from the original object is the *vg_target*, included by the geometry node modifier. This vg acts as a mask, meaning it decides over which vertices will be affected by shrinkwrapping and which ones will not. The weights of the vertices don't matter.

However, to make the modifiers work we need additional vertex groups. Due to how the geometry node modifier is set up, the script will need to create a new, empty vertex group on the *original* object for each of the vgs listed below.
- vg with *every* vertex assigned with a weight of 1.0
- vg with *every* vertex assigned with a weight of 0.0
- vg with only vertices of the vg_target, assigned with a weight of 1.0
- vg with only vertices of the vg_target, assigned with a weight of 0.0

These vertex groups will be "filled" with the correct data by using *Vertex Weight Edit* and *Vertex Weight Mix* modifiers (on the imposter object, not original object).


### **Modifier List**:
1. *Geometry Nodes* modifier:
    - Makes the imposter object look like the original one, and also transfers data like vertex groups, materials etc.
2. *Hook* modifier:
    - Hooks the object into place, using a vertex group that has all vertices with a weight of 1, and the *obj_static* as its target.
    - The purpose of this is so that you can change the rotation of the imposter object without actually it being visually affected by it. The rotation is important for the shrinkwrap modifier.
3. *Displace* modifier:
    - Moves the whole object several meters into the direction provided by obj_axis.
    - The purpose of this is to basically always have the object be above the object that acts as the shrinkwrap target.
4. *Shrinkwrap* modifier:
    - Shrinkwraps the imposter object geometry on the target object in the direction provided by obj_axis, basically the opposite direction of the first displace modifier.
    - This affects only vertices in vg_target.
5. *Displace* modifier:
    - Moves the whole object in the opposite direction of the first displace modifier. This means that any vertex that wasn't affected by the shrinkwrap modifier is back in its original place.
6. *Vertex Weight Proximity* modifier:
    - This one assigns every vertex that is NOT back in its original place (aka has been shrinkwrapped) a weight of 1.
7. *Displace* modifier:
    - The final modifier, using the vertex group data of the vw proximity mod above to fix the position of the vertices affected by shrinkwrap, as they currently are on the wrong side of the object.

### **Constraints**
The imposter object only has a single *Copy Rotation* constraint, which copies the rotation of obj_axis. Because a hook modifier is used, the rotation changes don't actually seem to affect the imposter object visually.    

