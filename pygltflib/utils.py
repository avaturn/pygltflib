"""
pygltflib.utils.py : A collection of functions for manipulating GLTF2 objects.


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

import pathlib
import warnings

from . import *


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


def add_primitive(_gltf):
    warnings.warn("pygltf.utils.add_primitive is a provisional function and may not exist in future versions.")

    # create gltf objects for a scene with a primitive triangle with indexed geometery
    gltf = GLTF2()
    scene = Scene()
    mesh = Mesh()
    primitive = Primitive()
    node = Node()
    buffer = Buffer()
    bufferView1 = BufferView()
    bufferView2 = BufferView()
    accessor1 = Accessor()
    accessor2 = Accessor()

    # add data
    primitive.attributes.POSITION = 1

    buffer.uri = "data:application/octet-stream;base64,AAABAAIAAAAAAAAAAAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAACAPwAAAAA="
    buffer.byteLength = 44

    bufferView1.buffer = 0
    bufferView1.byteOffset = 0
    bufferView1.byteLength = 6
    bufferView1.target = 34963

    bufferView2.buffer = 0
    bufferView2.byteOffset = 8
    bufferView2.byteLength = 36
    bufferView2.target = 34962

    accessor1.bufferView = 0
    accessor1.byteOffset = 0
    accessor1.componentType = UNSIGNED_SHORT
    accessor1.count = 3
    accessor1.type = SCALAR
    accessor1.max = [2]
    accessor1.min = [0]

    accessor2.bufferView = 1
    accessor2.byteOffset = 0
    accessor2.componentType = FLOAT
    accessor2.count = 3
    accessor2.type = VEC3
    accessor2.max = [1.0, 1.0, 0.0]
    accessor2.min = [0.0, 0.0, 0.0]

    node.mesh = 0
    scene.nodes = [0]

    # assemble into a gltf structure
    gltf.scenes.append(scene)
    gltf.meshes.append(mesh)
    gltf.meshes[0].primitives.append(primitive)
    gltf.nodes.append(node)
    gltf.buffers.append(buffer)
    gltf.bufferViews.append(bufferView1)
    gltf.bufferViews.append(bufferView2)
    gltf.accessors.append(accessor1)
    gltf.accessors.append(accessor2)

    # save to file
    gltf.save("primitive.gltf")



def gltf2glb(source, destination=None, override=False):
    """
    Save a .gltf file as its .glb equivalent.

    Args:
        source (str): Path to existing .gltf file.
        destination Optional(str): Filename to write to (default is to use existing filename as base)
        override: Override existing file.

    """
    path = Path(source)
    if not destination:
        destination = path.with_suffix(".glb")
    else:
        destination = Path(destination)
    if destination.is_file() and override is False:
        raise FileExistsError
    else:
        GLTF2().load(str(path))._save_binary(str(destination))
    return True


def glb2gltf(source, destination=None, override=False):
    """
    Save a .glb file as its .gltf equivalent.

    Args:
        source (str): Path to existing .glb file.
        destination Optional(str): Filename to write to (default is to use existing filename as base)
        override: Override existing file.

    """
    path = Path(source)
    if not destination:
        destination = path.with_suffix(".gltf")
    else:
        destination = Path(destination)
    if destination.is_file() and override is False:
        raise FileExistsError
    else:
        GLTF2().load(str(path))._save_json(str(destination))
    return True
