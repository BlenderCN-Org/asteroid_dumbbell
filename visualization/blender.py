"""Testing out Blender Python API

First you'll need to build Blender using the script in utilities/build_blender.sh

Then you can try and API instructions at https://docs.blender.org/api/2.78b/info_quickstart.html

Hopefully this works
"""
import os
import bpy
import numpy as np

scene = bpy.context.scene

output_path = 'visualization/blender'

# set scene render options
scene.render.resolution_percentage = 100
# scene.render.filepath = 'visualization/blender/'
scene.render.engine = 'BLENDER_RENDER'

# import OBJ model
bpy.ops.import_scene.obj(filepath='data/itokawa_low.obj')

# add a ground plane
add_plane = bpy.ops.mesh.primitive_plane_add
add_cube = bpy.ops.mesh.primitive_cube_add
cube = bpy.data.objects['Cube']
camera = bpy.data.objects['Camera']
lamp = bpy.data.objects['Lamp']
itokawa = bpy.data.objects['itokawa_low']
layers = [False] * 32
layers[0] = True

# delete the cube
radians = np.arange(0, 2*np.pi, 1*np.pi/180)

itokawa.location.z = 2

# camera.location.y = -2
# camera.location.z = 2
# camera.rotation_euler.x = -90
# camera.rotation_euler.y = 0
# camera.rotation_euler.z = 0

lamp.location.x = 0
lamp.location.y = 0 
lamp.location.z = 5
for rad in radians:
    cube.location.x = np.sin(rad)
    itokawa.rotation_euler.z = rad * 180 / np.pi
    # camera.location.x = np.sin(rad)
    scene.render.filepath = os.path.join(output_path, 'cube_' + str(rad) + '.png')
    bpy.ops.render.render(write_still=True)

for object in bpy.data.objects:
    print(object.name + " is at location " + str(object.location))


# bpy.ops.import_scene.obj('../data/itokawa_low.obj')
# bpy.ops.render.render(write_still=True)
