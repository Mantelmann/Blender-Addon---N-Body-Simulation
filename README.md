# Blender Addon - N-Body Simulation

This very small addon is for Blender 2.83 and allows the user to calculate a N-Body simulation. Looks nice, is free.

# So, how does this addon work?

The addon menu panel is in the N-Panel, under Create.

First of all, state a collection Name in which relevant Empties will be placed. The collection doesn't need to actually exist, but there shouldn't be any other objects in it to avoid unfortunate errors.

Once you have stated the collection name, select every object you want to include in the N-Body-Simulation, and click the "Prepare Wrapper Objects" button. This will generate empties and velocity vectors for every selected object.
The generated velocity vectors can be found at the origins of their object. You can freely point and move them to input a starting velocity for the object.

Once you have configured every velocity vector to your liking, simply click "Calculate!" and let the computer take over. For every frame in the given frame range, keyframes will be generated.

If you click "Clear Keyframes", every keyframe of every wrapper in the given collection will be cleared of keyframes.

If you click "Remove Wrapper Objects", the selected wrapper object and its velocity vector will be deleted.
