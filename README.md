# pygltflib

This is a library for reading, writing and handling GLTF files. It works for Python3.6 and above.

It supports the entire specification, including materials and animations. Main features are:
* GLB and GLTF support
* Buffer data conversion
* Extensions
* All attributes are type-hinted

# Table of Contents

* [Quickstart](#quickstart)
  * [Install](#install)
  * [How do I...](#how-do-i)
    * [Create an empty GLTF2 object?](#create-an-empty-gltf2-object)
    * [Add a scene?](#add-a-scene)
    * [Load a file?](#load-a-file)
    * [Load a binary GLB file?](#load-a-binary-glb-file)
    * [Load a binary file with an unusual extension?](#load-a-binary-file-with-an-unusual-extension)
    * [Access the first node (the objects comprising the scene) of a scene?](#access-the-first-node-the-objects-comprising-the-scene-of-a-scene)
    * [Create a mesh?](#create-a-mesh)
    * [Convert buffers to GLB binary buffers?](#convert-buffers-to-glb-binary-buffers)
    * [Convert buffer to data uri (embedded) buffer?](#convert-buffer-to-data-uri-embedded-buffer)
    * [Convert buffers to binary file (external) buffers?](#convert-buffers-to-binary-file-external-buffers)
    * [Convert a glb to a gltf file?](#convert-a-glb-to-a-gltf-file)
    * [Access an extension?](#access-an-extension)
    * [Add a custom attribute to Attributes?](#add-a-custom-attribute-to-attributes)
    * [Remove a bufferView?](#remove-a-bufferview)
    * [Validate a gltf object?](#validate-a-gltf-object)
    * [Convert texture images inside a GLTF file to their own PNG files?](#convert-texture-images-inside-a-gltf-file-to-their-own-png-files)
    * [Convert texture images from a GLTF file to their own PNG files using custom file names?](#convert-texture-images-from-a-gltf-file-to-their-own-png-files-using-custom-file-names)
    * [Specify a path to my images when converting to files?](#specify-a-path-to-my-images-when-converting-to-files)
    * [Export images from the GLTF file to any location (ie outside the GLTF file)?](#export-images-from-the-GLTF-file-to-any-location-ie-outside-the-GLTF-file)
    * [Import PNG files as textures into a GLTF?](#import-png-files-as-textures-into-a-gltf)
* [About](#about)
  * [Roadmap](#roadmap)
  * [Contributors](#contributors)
  * [Thanks](#thanks)1
  * [Changelog](#changelog)
  * [Installing](#installing)
  * [Source](#source)
* [More Detailed Usage](#more-detailed-usage)
  * [A simple mesh](#a-simple-mesh)
  * [Reading vertex data from a primitive and/or getting bounding sphere](#reading-vertex-data-from-a-primitive-andor-getting-bounding-sphere)
  * [Create a mesh, convert to bytes, convert back to mesh](#create-a-mesh-convert-to-bytes-convert-back-to-mesh)
  * [Loading and saving](#loading-and-saving)
  * [Converting files](#converting-files)
  * [Converting buffers](#converting-buffers)
  * [Converting texture images](#converting-texture-images)
  * [Extensions](#extensions)
* [Running the tests](#running-the-tests)

## Quickstart

### Install

```
pip install pygltflib
```


### How do I...


#### Create an empty GLTF2 object?

```python
from pygltflib import GLTF2

gltf = GLTF2()
```

#### Add a scene?

```python
from pygltflib import GLTF2, Scene

gltf = GLTF2()
scene = Scene()
gltf.scenes.append(scene)  # scene available at gltf.scenes[0]
```

#### Load a file?

```python
filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
gltf = GLTF2().load(filename)
```

#### Load a binary GLB file?

```python
glb_filename = "glTF-Sample-Models/2.0/Box/glTF-Binary/Box.glb"
glb = GLTF2().load(glb_filename)  # load method auto detects based on extension
```

#### Load a binary file with an unusual extension?

```python
glb = GLTF2().load_binary("BinaryGLTF.glk")   # load_json and load_binary helper methods
```


#### Access the first node (the objects comprising the scene) of a scene?

```python
gltf = GLTF2().load("glTF-Sample-Models/2.0/Box/glTF/Box.gltf")
current_scene = gltf.scenes[gltf.scene]
node_index = current_scene.nodes[0]  # scene.nodes is the indices, not the objects 
box = gltf.nodes[node_index]
box.matrix  # will output vertices for the box object
```


#### Create a mesh?
Consult the longer examples in the second half of this document
  * [A simple mesh](#a-simple-mesh)
  * [Reading vertex data from a primitive and/or getting bounding sphere](#reading-vertex-data-from-a-primitive-andor-getting-bounding-sphere)
  * [Create a mesh, convert to bytes, convert back to mesh](#create-a-mesh-convert-to-bytes-convert-back-to-mesh)


#### Convert buffers to glb binary buffers?

```python
from pygltflib import GLTF2, BufferFormat

gltf = GLTF2().load("glTF-Sample-Models/2.0/Box/glTF/Box.gltf")
gltf.convert_buffers(BufferFormat.BINARYBLOB)   # convert buffers to GLB blob
```

#### Convert buffer to data uri (embedded) buffer?
```python
gltf.convert_buffers(BufferFormat.DATAURI)  # convert buffer URIs to data.
```

#### Convert buffers to binary file (external) buffers?
```python
gltf.convert_buffers(BufferFormat.BINFILE)   # convert buffers to files
gltf.save("test.gltf")  # all the buffers are saved in 0.bin, 1.bin, 2.bin.
```


#### Convert a glb to a gltf file?
```python
from pygltflib.utils import glb2gltf, gltf2glb

# convert glb to gltf
glb2gltf("glTF-Sample-Models/2.0/Box/glTF-Binary/Box.glb")
```

#### Access an extension?
```python
# on a primitve
gltf.meshes[0].primitives[0].extensions['KHR_draco_mesh_compression']

# on a material
gltf.materials[0].extensions['ADOBE_materials_thin_transparency']

```

#### Add a custom attribute to Attributes?
```python
# Application-specific semantics must start with an underscore, e.g., _TEMPERATURE.
a = Attributes()
a._MYCUSTOMATTRIBUTE = 123

gltf.meshes[0].primitives[0].attributes._MYOTHERATTRIBUTE = 456
```

#### Remove a bufferView?
```python
gltf.remove_bufferView(0)  # this will update all accessors, images and sparse accessors to remove the first bufferView
```

#### Validate a gltf object?
```python
from pygltflib import GLTF2
from pygltflib.validator import validate, summary
filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
gltf = GLTF2().load(filename)
validate(gltf)  # will throw an error depending on the problem
summary(gltf)  # will pretty print human readable summary of errors
# NOTE: Currently this experimental validator only validates a few rules about GLTF2 objects
```

#### Convert texture images inside a GLTF file to their own PNG files?
```python
from pygltflib import GLTF2
from pygltflib.utils import ImageFormat
filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
gltf = GLTF2().load(filename)
gltf.convert_images(ImageFormat.FILE)
gltf.images[0].uri  # will now be 0.png and the texture image will be saved in 0.png
```

#### Convert texture images from a GLTF file to their own PNG files using custom file names?
```python
from pygltflib import GLTF2
from pygltflib.utils import ImageFormat
filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
gltf = GLTF2().load(filename)
gltf.images[0].name = "cube.png"  # will save the data uri to this file (regardless of data format)
gltf.convert_images(ImageFormat.FILE)
gltf.images[0].uri  # will now be cube.png and the texture image will be saved in cube.png
```

#### Specify a path to my images when converting to files?
By default pygltflib will load images from the same location as the GLTF file.

It will also try and save image files to the that location when converting image buffers or data uris.

You can override the load/save location using the 'path' argument to `convert_images`
```python
from pygltflib import GLTF2
from pygltflib.utils import ImageFormat
filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
gltf = GLTF2().load(filename)
gltf.images[0].name = "cube.png"  # will save the data uri to this file (regardless of data format)
gltf.convert_images(ImageFormat.FILE, path='/destination/') 
gltf.images[0].uri  # will now be cube.png and the texture image will be saved in /destination/cube.png
```

#### Export images from the GLTF file to any location (ie outside the GLTF file)?
```python
from pygltflib import GLTF2
from pygltflib.utils import ImageFormat
filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
gltf = GLTF2().load(filename)
gltf.export_image(0, "output/cube.png", override=True)  # There is now an image file at output/cube.png
```


#### Import PNG files as textures into a GLTF?
```python
from pygltflib import GLTF2
from pygltflib.utils import ImageFormat, Image
gltf = GLTF2()
image = Image()
image.uri = "myfile.png"
gltf.images.append(image)
gltf.convert_images(ImageFormat.DATAURI)
gltf.images[0].uri  # will now be something like "data:image/png;base64,iVBORw0KGg..."
gltf.images[0].name  # will be myfile.png
```


### More Detailed Usage Below

## About
This is an unofficial library that tracks the [official file format](https://github.com/KhronosGroup/glTF/blob/master/specification/2.0/README.md) for GLTF2. 

The library was initially built to load and save simple meshes but support for the entire spec, including materials 
and animations is pretty good. Supports both json (.gltf) and binary (.glb) file formats, although .glb support 
is missing some features at the moment. 

It requires python 3.6 and above because it uses dataclasses and all attributes are type hinted. And f-strings, plenty of f-strings.

Check the table below for an idea of which sample models validate.

Questions? Contributions? Bug reports? Open an issue on the [gitlab page for the project](https://gitlab.com/dodgyville/pygltflib).
We are very interested in hearing your use cases for `pygltflib` to help drive the roadmap.

### Roadmap
* Add helper functions for creating meshes
* Test coverage
* Enforce single underscore on custom Attribute attributes 
* Investigate creating classes from extensions
* Automated validation and visual inspection

### Contributors
* Luke Miller
* Sebastian Höffner
* Arthur van Hoff
* Arifullah Jan
* Daniel Haehn
* Jon Time
* Laurie O
* Peter Suter
* Frédéric Devernay
* Julian Stirling
* Johannes Deml
* Margarida Silva 
* Patiphan Wongklaew
* Alexander Druz
* Adriano Martins
* Dzmitry Stabrouski
* irtimir

#### Thanks
`pyltflib` made for 'The Beat: A Glam Noir Game' supported by Film Victoria. 

### Changelog
* 1.14.5
  * unquote filepath in compliance with standard (irtimir)

* 1.14.4
  * Add `GLTF.export_image` method to export images from an GLTF2 file to any location (Khac Hoa Le)
  * remove extraneous print message when loading extensions (Michael Daw)

* 1.14.3
  * add ability to save data directly in the uri field to `save_to_bytes` (Israel)
  * fix issue where attributes field is shared between two instances of Primitive (Konstantin Sinitsyn)

See [CHANGELOG.md] (https://gitlab.com/dodgyville/pygltflib/-/blob/master/CHANGELOG.md) for older versions

## Installing
```
pip install pygltflib
```
or
```
py -m pip install pygltflib
```


## Source

```
git clone https://gitlab.com/dodgyville/pygltflib
```


## More Detailed Usage
Note: These examples use the official [sample models](https://github.com/KhronosGroup/glTF-Sample-Models) provided by Khronos at:

https://github.com/KhronosGroup/glTF-Sample-Models

### A simple mesh
```python
from pygltflib import *

# create gltf objects for a scene with a primitive triangle with indexed geometry
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
buffer.uri = "data:application/octet-stream;base64,AAABAAIAAAAAAAAAAAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAACAPwAAAAA="
buffer.byteLength = 44

bufferView1.buffer = 0
bufferView1.byteOffset = 0
bufferView1.byteLength = 6
bufferView1.target = ELEMENT_ARRAY_BUFFER

bufferView2.buffer = 0
bufferView2.byteOffset = 8
bufferView2.byteLength = 36
bufferView2.target = ARRAY_BUFFER

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

primitive.attributes.POSITION = 1
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
gltf.save("triangle.gltf")
```


### Reading vertex data from a primitive and/or getting bounding sphere
```python
import pathlib
import struct

import miniball
import numpy
from pygltflib import GLTF2

# load an example gltf file from the khronos collection
fname = pathlib.Path("glTF-Sample-Models/2.0/Box/glTF-Embedded/Box.gltf")
gltf = GLTF2().load(fname)

# get the first mesh in the current scene (in this example there is only one scene and one mesh)
mesh = gltf.meshes[gltf.scenes[gltf.scene].nodes[0]]

# get the vertices for each primitive in the mesh (in this example there is only one)
for primitive in mesh.primitives:

    # get the binary data for this mesh primitive from the buffer
    accessor = gltf.accessors[primitive.attributes.POSITION]
    bufferView = gltf.bufferViews[accessor.bufferView]
    buffer = gltf.buffers[bufferView.buffer]
    data = gltf.decode_data_uri(buffer.uri)

    # pull each vertex from the binary buffer and convert it into a tuple of python floats
    vertices = []
    for i in range(accessor.count):
        index = bufferView.byteOffset + accessor.byteOffset + i*12  # the location in the buffer of this vertex
        d = data[index:index+12]  # the vertex data
        v = struct.unpack("<fff", d)   # convert from base64 to three floats
        vertices.append(v)
        print(i, v)

# convert a numpy array for some manipulation
S = numpy.array(vertices)

# use a third party library to perform Ritter's algorithm for finding smallest bounding sphere
C, radius_squared = miniball.get_bounding_ball(S)

# output the results
print(f"center of bounding sphere: {C}\nradius squared of bounding sphere: {radius_squared}")
```


### Create a mesh, convert to bytes, convert back to mesh
The geometry is derived from [glTF 2.0 Box Sample](https://github.com/KhronosGroup/glTF-Sample-Models/tree/master/2.0/Box), but point normals were removed and points were reused where it was possible in order to reduce the size of the example. Be aware that some parts are hard-coded (types and shapes for en- and decoding of arrays, no bytes padding).
```python
import numpy as np
import pygltflib
```
Define mesh using `numpy`:
```python
points = np.array(
    [
        [-0.5, -0.5, 0.5],
        [0.5, -0.5, 0.5],
        [-0.5, 0.5, 0.5],
        [0.5, 0.5, 0.5],
        [0.5, -0.5, -0.5],
        [-0.5, -0.5, -0.5],
        [0.5, 0.5, -0.5],
        [-0.5, 0.5, -0.5],
    ],
    dtype="float32",
)
triangles = np.array(
    [
        [0, 1, 2],
        [3, 2, 1],
        [1, 0, 4],
        [5, 4, 0],
        [3, 1, 6],
        [4, 6, 1],
        [2, 3, 7],
        [6, 7, 3],
        [0, 2, 5],
        [7, 5, 2],
        [5, 7, 4],
        [6, 4, 7],
    ],
    dtype="uint8",
)
```
Create glb-style `GLTF2` with single scene, single node and single mesh from arrays of points and triangles:
```python
triangles_binary_blob = triangles.flatten().tobytes()
points_binary_blob = points.tobytes()
gltf = pygltflib.GLTF2(
    scene=0,
    scenes=[pygltflib.Scene(nodes=[0])],
    nodes=[pygltflib.Node(mesh=0)],
    meshes=[
        pygltflib.Mesh(
            primitives=[
                pygltflib.Primitive(
                    attributes=pygltflib.Attributes(POSITION=1), indices=0
                )
            ]
        )
    ],
    accessors=[
        pygltflib.Accessor(
            bufferView=0,
            componentType=pygltflib.UNSIGNED_BYTE,
            count=triangles.size,
            type=pygltflib.SCALAR,
            max=[int(triangles.max())],
            min=[int(triangles.min())],
        ),
        pygltflib.Accessor(
            bufferView=1,
            componentType=pygltflib.FLOAT,
            count=len(points),
            type=pygltflib.VEC3,
            max=points.max(axis=0).tolist(),
            min=points.min(axis=0).tolist(),
        ),
    ],
    bufferViews=[
        pygltflib.BufferView(
            buffer=0,
            byteLength=len(triangles_binary_blob),
            target=pygltflib.ELEMENT_ARRAY_BUFFER,
        ),
        pygltflib.BufferView(
            buffer=0,
            byteOffset=len(triangles_binary_blob),
            byteLength=len(points_binary_blob),
            target=pygltflib.ARRAY_BUFFER,
        ),
    ],
    buffers=[
        pygltflib.Buffer(
            byteLength=len(triangles_binary_blob) + len(points_binary_blob)
        )
    ],
)
gltf.set_binary_blob(triangles_binary_blob + points_binary_blob)
```
Write `GLTF2` to bytes:
```python
glb = b"".join(gltf.save_to_bytes())  # save_to_bytes returns an array of the components of a glb
```
Load `GLTF2` from bytes:
```python
gltf = pygltflib.GLTF2.load_from_bytes(glb)
```
Decode `numpy` arrays from `GLTF2`:
```python
binary_blob = gltf.binary_blob()

triangles_accessor = gltf.accessors[gltf.meshes[0].primitives[0].indices]
triangles_buffer_view = gltf.bufferViews[triangles_accessor.bufferView]
triangles = np.frombuffer(
    binary_blob[
        triangles_buffer_view.byteOffset
        + triangles_accessor.byteOffset : triangles_buffer_view.byteOffset
        + triangles_buffer_view.byteLength
    ],
    dtype="uint8",
    count=triangles_accessor.count,
).reshape((-1, 3))

points_accessor = gltf.accessors[gltf.meshes[0].primitives[0].attributes.POSITION]
points_buffer_view = gltf.bufferViews[points_accessor.bufferView]
points = np.frombuffer(
    binary_blob[
        points_buffer_view.byteOffset
        + points_accessor.byteOffset : points_buffer_view.byteOffset
        + points_buffer_view.byteLength
    ],
    dtype="float32",
    count=points_accessor.count * 3,
).reshape((-1, 3))
```
**P.S.**: If you'd like to use "compiled" version of mesh writing:
```python
gltf = pygltflib.GLTF2(
    scene=0,
    scenes=[pygltflib.Scene(nodes=[0])],
    nodes=[pygltflib.Node(mesh=0)],
    meshes=[
        pygltflib.Mesh(
            primitives=[
                pygltflib.Primitive(
                    attributes=pygltflib.Attributes(POSITION=1), indices=0
                )
            ]
        )
    ],
    accessors=[
        pygltflib.Accessor(
            bufferView=0,
            componentType=pygltflib.UNSIGNED_BYTE,
            count=36,
            type=pygltflib.SCALAR,
            max=[7],
            min=[0],
        ),
        pygltflib.Accessor(
            bufferView=1,
            componentType=pygltflib.FLOAT,
            count=8,
            type=pygltflib.VEC3,
            max=[0.5, 0.5, 0.5],
            min=[-0.5, -0.5, -0.5],
        ),
    ],
    bufferViews=[
        pygltflib.BufferView(
            buffer=0, byteLength=36, target=pygltflib.ELEMENT_ARRAY_BUFFER
        ),
        pygltflib.BufferView(
            buffer=0, byteOffset=36, byteLength=96, target=pygltflib.ARRAY_BUFFER
        ),
    ],
    buffers=[pygltflib.Buffer(byteLength=132)],
)
gltf.set_binary_blob(
    b"\x00\x01\x02\x03\x02\x01\x01\x00\x04\x05\x04\x00\x03\x01\x06\x04\x06\x01"
    b"\x02\x03\x07\x06\x07\x03\x00\x02\x05\x07\x05\x02\x05\x07\x04\x06\x04\x07"
    b"\x00\x00\x00\xbf\x00\x00\x00\xbf\x00\x00\x00?\x00\x00\x00?\x00\x00\x00"
    b"\xbf\x00\x00\x00?\x00\x00\x00\xbf\x00\x00\x00?\x00\x00\x00?\x00\x00\x00?"
    b"\x00\x00\x00?\x00\x00\x00?\x00\x00\x00?\x00\x00\x00\xbf\x00\x00\x00\xbf"
    b"\x00\x00\x00\xbf\x00\x00\x00\xbf\x00\x00\x00\xbf\x00\x00\x00?\x00\x00"
    b"\x00?\x00\x00\x00\xbf\x00\x00\x00\xbf\x00\x00\x00?\x00\x00\x00\xbf"
)
```

### Loading and saving

`pygltflib` can load json-based .GLTF files and binary .GLB files, based on the file extension. 

#### GLTF files

```python
>>> from pygltflib import GLTF2
>>> filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
>>> gltf = GLTF2().load(filename)
>>> gltf.scene
0

>>> gltf.scenes
[Scene(name='', nodes=[0])]

>>> gltf.nodes[0]
Node(mesh=0, skin=None, rotation=[0.0, -1.0, 0.0, 0.0], translation=[], scale=[], children=[], matrix=[], camera=None, name='AnimatedCube')
>>> gltf.nodes[0].name
'AnimatedCube'

>>> gltf.meshes[0].primitives[0].attributes
Attributes(NORMAL=4, POSITION=None, TANGENT=5, TEXCOORD_0=6)

>>> filename2 = "test.gltf"
>>> gltf.save(filename2)
```

#### GLB files 

```python
>>> from pygltflib import GLTF2
>>> glb_filename = "glTF-Sample-Models/2.0/Box/glTF-Binary/Box.glb"
>>> glb = GLTF2().load(glb_filename)
>>> glb.scene
0

>>> glb.scenes
[Scene(name='', nodes=[0])]

>>> glb.nodes[0]
Node(mesh=None, skin=None, rotation=[], translation=[], scale=[], children=[1], matrix=[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0], camera=None, name=None)

>>> glb.meshes[0].primitives[0].attributes
Attributes(POSITION=2, NORMAL=1, TANGENT=None, TEXCOORD_0=None, TEXCOORD_1=None, COLOR_0=None, JOINTS_0=None, WEIGHTS_0=None)

>>> glb.save("test.glb")

>>> glb.binary_blob()  # read the binary blob used by the buffer in a glb
<a bunch of binary data>
```

### Converting files

#### First method

```python
>>> from pygltflib import GLTF2

>>> # convert glb to gltf
>>> glb = GLTF2().load("glTF-Sample-Models/2.0/Box/glTF-Binary/Box.glb")
>>> glb.save("test.gltf")

>>> # convert gltf to glb
>>> gltf = GLTF2().load("glTF-Sample-Models/2.0/Box/glTF/Box.gltf")
>>> gltf.save("test.glb")
```

#### Second method using utils

```python
>>> from pygltflib import GLTF2
>>> from pygltflib.utils import glb2gltf, gltf2glb

>>> # convert glb to gltf
>>> glb2gltf("glTF-Sample-Models/2.0/Box/glTF-Binary/Box.glb")

>>> # convert gltf to glb
>>> gltf2glb("glTF-Sample-Models/2.0/Box/glTF/Box.gltf", "test.glb", override=True)

```

### Converting buffers 
The data for a buffer in a GLTF2 files can be stored in the buffer object's URI string 
or in a binary file pointed to by the buffer objects' URI string or as a binary blob
inside a GLB file.

While saving and loading GLTF2 files is mostly handled transparently by the library, 
there may be some situations where you want a specific type of buffer storage.

For example, if you have a GLTF file that stores all the associated data in .bin files
but you want to create a single file, you need to convert the buffers from binary files
to data uris or glb binary data.

There is a convenience method named `convert_buffers` that can help.

```python
>>> from pygltflib import GLTF2, BufferFormat

>>> gltf = GLTF2().load("glTF-Sample-Models/2.0/Box/glTF/Box.gltf")
>>> gltf.convert_buffers(BufferFormat.DATAURI)  # convert buffer URIs to data.
>>> gltf.save_binary("test.glb")  # try and save, will get warning.
Warning: Unable to save data uri to glb format.

>>> gltf.convert_buffers(BufferFormat.BINARYBLOB)   # convert buffers to GLB blob
>>> gltf.save_binary("test.glb")

>>> gltf.convert_buffers(BufferFormat.BINFILE)   # convert buffers to files
>>> gltf.save("test.gltf")  # all the buffers are saved in 0.bin, 1.bin, 2.bin.
```

### Converting texture images
The image data for textures in GLTF2 files can be stored in the image objects URI string
or in an image file pointed to by the image objects' URI string or as part of the buffer.

While saving and loading GLTF2 files is mostly handled transparently by the library,
there may be some situations where you want a specific type of image storage.

For example, if you have a GLB file that stores all its image files in .PNG files 
but you want to create a single GLTF file, you need to convert the images from files
to data uris.

Currently converting images to and from the buffer is not supported. Only image
files and data uris are supported.

There is a convenience method named `convert_images` that can help.  

```python

>>> # embed an image file to your GLTF.

>>> from pygltflib.utils import ImageFormat, Image
>>> gltf = GLTF2()
>>> image = Image()
>>> image.uri = "myfile.png"
>>> gltf.images.append(image)

>>> gltf.convert_images(ImageFormat.DATAURI)  # image file will be imported into the GLTF
>>> gltf.images[0].uri  # will now be something like "data:image/png;base64,iVBORw0KGg..."
>>> gltf.images[0].name  # will be myfile.png


>>> # create an image file from GLTF data uris

>>> from pathlib import Path
>>> from pygltflib.utils import ImageFormat, Image
>>> gltf = GLTF2()
>>> image = Image()
>>> image.uri = "data:image/png;base64,iVBORw0KGg..."
>>> image.name = "myfile.png"  # optional file name, if not provided, the image files will be called "0.png", "1.png"
>>> gltf.images.append(image)

>>> gltf.convert_images(ImageFormat.FILE)  # image file will be imported into the GLTF
>>> gltf.images[0].uri  # will be myfile.png
"myfile.png"

>>> Path("myfile.png").exists()
True
```


### Extensions
The GLTF2 spec allows for extensions to added to any component of a GLTF file.

As of writing (August 2019) there are [about a dozen extensions from Khronos and other vendors](https://github.com/KhronosGroup/glTF/tree/master/extensions/2.0/)


In pygltflib, extensions are loaded as ordinary `dict` objects and so should be accessed like regular key,value pairs.

For example `extensions["KHR_draco_mesh_compression"]["bufferView"]` instead of `extensions["KHR_draco_mesh_compression"].bufferView`.

This allows future extensions to be automatically supported by pygltflib.

*Extras* should work the same way.


## Running the tests

### Status of gltf-validator
Using sample models loaded and then saved using this library, here are validator reports (blank is untested). 
If available, The result of a visual inspection is in brackets next to the validator result. 


#### Validator Status
| Model | gltf to gltf | gltf to glb | glb to gltf | glb to glb | 
| ------| ------- | ------- | ------- | ------ |
| 2CylinderEngine | passes | passes | passes | passes
| AlphaBlendModeTest | passes | passes | passes | passes
| AnimatedCube | passes | passes | no glb available | no glb available|
| AnimatedMorphCube | passes |  passes | passes | passes
| AnimatedMorphSphere | passes |  passes | passes | passes
| AnimatedTriangle | passes |  passes | no glb available | no glb available|
| Avocado | passes |  passes | passes | passes
| BarramundiFish | passes | passes | passes | passes
| BoomBox | passes | passes | passes | passes
| BoomBoxWithAxes | passes | passes | no glb available | no glb available|
| Box | passes | passes | passes | passes
| BoxAnimated | passes | passes | passes
| BoxInterleaved | passes | passes | | passes
| BoxTextured | passes | passes
| BoxTexturedNonPowerOfTwo | passes | passes
| BoxVertexColors | passes | passes 
| BrainStem | passes | passes | passes
| Buggy | passes | passes | passes
| Cameras | passes | passes | no glb available | no glb available|
| CesiumMan | passes | passes
| CesiumMilkTruck | passes | passes
| Corset | passes | passes | passes | passes |
| Cube | passes | passes | no glb available | no glb available|
| DamagedHelmet | passes | passes | passes | passes
| Duck | passes | passes | passes | passes
| FlightHelmet | passes | passes | no glb available | no glb available|
| GearboxAssy | passes | passes
| Lantern | passes | passes |
| MetalRoughSpheres | passes | passes | 
| Monster | passes | passes
| MultiUVTest | passes | passes
| NormalTangentMirrorTest | passes | passes | 
| NormalTangentTest | passes | passes | | passes
| OrientationTest | passes | passes |
| ReciprocatingSaw | passes | passes |
| RiggedFigure | passes |  passes |
| RiggedSimple | passes |  passes |
| SciFiHelmet | passes |  passes | no glb available | no glb available|
| SimpleMeshes | passes | passes | no glb available | no glb available|
| SimpleMorph | passes | passes | no glb available | no glb available|
| SimpleSparseAccessor | passes | passes | no glb available | no glb available 
| SpecGlossVsMetalRough | passes | passes | passes | passes
| Sponza | passes | passes | no glb available | no glb available|
| Suzanne | passes | passes | no glb available | no glb available|
| TextureCoordinateTest | passes | passes | passes | passes
| TextureSettingsTest | passes | passes | passes | passes
| TextureTransformTest | passes | passes | no glb available | no glb available| 
| Triangle | passes | passes | no glb available | no glb available|
| TriangleWithoutIndices | passes | passes | no glb available | no glb available|
| TwoSidedPlane | passes | passes | no glb available | no glb available|
| VC | passes | *fails* | passes | passes
| VertexColorTest | passes | passes | passes  | passes
| WaterBottle | passes | passes | passes | passes


### utils.validator status
What does pygltflib.utils.validator test?
NOTE: At the moment the validator raises an exception when an rule is broken. If you have ideas of the best way to 
return information on validation warnings/errors please open a ticket on our gitlab.

| Rule | validator tests | exception raised
| ------| ------- | ----- 
| accessor.componentType must be valid |  yes | InvalidAcccessorComponentTypeException
| accessor min and max arrays must be valid length | yes | InvalidArrayLengthException
| accessor min and max arrays must be same length | yes | MismatchedArrayLengthException
| mesh.primitive.mode must be valid | yes | InvalidMeshPrimitiveMode 
| accessor.sparse.indices.componentType must be valid |  yes | InvalidAccessorSparseIndicesComponentTypeException
| bufferView byteOffset and byteStrides must be valid | yes | InvalidValueError
| bufferView targets must be valid | yes | InvalidBufferViewTarget
| all other tests | no  



### unittests
```
git clone https://github.com/KhronosGroup/glTF-Sample-Models
pytest test_pygltflib.py
```

