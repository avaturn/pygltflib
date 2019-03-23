"""
utils.py : A collection of functions for manipulating GLTF2 objects.


Copyright (c) 2018, 2019 Luke Miller

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from . import *
import warnings


# some higher level helper functions

def add_node(gltf, node):
    warnings.warn("pygltf.utils.add_node is a provisional function and may not exist in future versions.")
    if gltf.scene is not None:
        gltf.scenes[gltf.scene].nodes.append(len(gltf.nodes))
    gltf.nodes.append(node)
    return gltf


def add_default_camera(gltf):
    warnings.warn("pygltf.utils.add_default_camera is a provisional function and may not exist in future versions.")
    n = Node()
    n.rotation = [0.0, 0.0, 0.0, 1]
    n.translation = [-1.0, 0.0, 0.0]
    n.name = "Camera"
    n.camera = len(gltf.cameras)

    gltf.add_node(n)
    c = Camera()
    c.type = PERSPECTIVE
    c.perspective = Perspective()
    c.perspective.aspectRatio = 1.5
    c.perspective.yfov = 0.6
    c.perspective.zfar = 1000
    c.perspective.znear = 0.001
    gltf.cameras.append(c)
    return gltf


def add_default_scene(gltf):
    warnings.warn("pygltf.utils.add_default_scene is a provisional function and may not exist in future versions.")
    s = Scene()
    s.name = "Scene"
    gltf.scene = 0
    gltf.scenes.append(s)
    return gltf
