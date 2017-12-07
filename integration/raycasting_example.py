"""Script to do some raycasting with the simulated lidar
"""

from point_cloud import wavefront, lidar, raycaster
import numpy as np
from visualization import graphics

filename = './data/shape_model/ITOKAWA/itokawa_high.obj'
polydata = wavefront.read_obj_to_polydata(filename)

caster = raycaster.RayCaster(polydata)
sensor = lidar.Lidar(view_axis=np.array([-1, 0, 0]))

# need to translate the sensor and give it a pointing direction
pos = np.array([1, 0, 0])
dist = 1 # distance for each raycast

# find the inersections
targets = pos + sensor.lidar_arr * dist
intersections = caster.castarray(pos, targets)

# plot
fig = graphics.mayavi_figure()
graphics.mayavi_addPoly(fig, polydata)

graphics.mayavi_addPoint(fig, pos, radius=0.05)

# draw lines from pos to all targets
for pt in targets:
    graphics.mayavi_addLine(fig, pos, pt, color=(1, 0, 0))

# draw a point at all intersections
for ints in intersections:
    graphics.mayavi_addPoint(fig, ints, radius=0.01, color=(0, 1, 0))
