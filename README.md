# pygltflib

This is a library for reading, writing and handling GLTF files. It works for Python3.6 and above.

It supports the entire specification, including materials and animations. Main features are:
* GLB and GLTF support
* Buffer data conversion
* All attributes are type-hinted


## Quickstart

```
pip install pygltflib
```

### How do I...


#### Create an empty GLTF2 object?

```python3
from pygltflib import GLTF2

gltf = GLTF2()
```

#### Add a scene?

```python3
from pygltflib import GLTF2, Scene

gltf = GLTF2()
scene = Scene()
gltf.scenes.append(scene)  # scene available at gltf.scenes[0]
```


#### Load a file?

```python3
filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
gltf = GLTF2().load(filename)
```

#### Load a binary glb file?

```python3
glb_filename = "glTF-Sample-Models/2.0/Box/glTF-Binary/Box.glb"
glb = GLTF2().load(glb_filename)  # load method auto detects based on extension
```

#### Load a binary file with an unusual extension?

```python3
glb = GLTF2().load_binary("BinaryGLTF.glk")   # load_json and load_binary helper methods
```

#### Convert buffers to glb binary buffers?

```python3
from pygltflib import GLTF2, BufferFormat

gltf = GLTF2().load("glTF-Sample-Models/2.0/Box/glTF/Box.gltf")
gltf.convert_buffers(BufferFormat.BINARYBLOB)   # convert buffers to GLB blob
```

#### Convert buffer to data uri (embedded) buffer?
```python3
gltf.convert_buffers(BufferFormat.DATAURI)  # convert buffer URIs to data.
```

#### Convert buffers to binary file (external) buffers?
```python3
gltf.convert_buffers(BufferFormat.BINFILE)   # convert buffers to files
gltf.save("test.gltf")  # all the buffers are saved in 0.bin, 1.bin, 2.bin.
```


#### Convert a glb to a gltf file?
```python3
from pygltflib.utils import glb2gltf, gltf2glb

# convert glb to gltf
glb2gltf("glTF-Sample-Models/2.0/Box/glTF-Binary/Box.glb")
```


## About
This is an unofficial library that tracks the [official file format](https://github.com/KhronosGroup/glTF/blob/master/specification/2.0/README.md) for GLTF2. 

The library was initially built to load and save simple meshes but support for the entire spec, including materials 
and animations is pretty good. Supports both json (.gltf) and binary (.glb) file formats, although .glb support 
is missing some features at the moment. 

It requires python 3.6 and above because it uses dataclasses and all attributes are type hinted. And f-strings, plenty of f-strings.

Check the table below for an idea of which sample models validate.

Questions? Contributions? Bug reports? Open an issue on the [gitlab page for the project](https://gitlab.com/dodgyville/pygltflib).
We are very interested in hearing your use cases for `pygltflib` to help drive the roadmap.

#### Roadmap
* Add helper functions for creating meshes
* Test coverage
* Automated validation and visual inspection

#### Contributors
* Luke Miller
* Sebastian Höffner
* Arthur van Hoff
* Arifullah Jan
* Daniel Haehn

#### Thanks
`pygltflib` made for 'The Beat: A Glam Noir Game' supported by Film Victoria. 

#### Changelog
* 1.11.5
    * reorder `identify_uri` to avoid using lengthy byte strings as file names
    * assign parent path when saving so bin files save to same path

* 1.11.4
    * remove padding
    * improve dataclasses-json backwards compatibility

* 1.11.3
    * fix import issue with setup.py

* 1.11.2
    * fix issue with long data uris saving in glb
    * fix compatibility issue with different versions of dataclasses-json
    
* 1.11.1
    * update documentation
    * improve packaging

* 1.11
    * add access to internal glb binary data via `GLTF.binary_blob()`
    * add `convert_buffers` method to switch buffer formats between data uri, binary files and binary blobs
* 1.10
    * handle empty buffers on save
    * warn about unsupported data uri bufferViews
    * allow transparent textures (with alpha channel)
* 1.9
    * use factories to create Attributes and Asset objects
* 1.8
    * allow images to point to bufferViews
* 1.7
    * preserve order of bufferViews when saving to glb
    * pad binary chunks within embedded data correctly
* 1.6
    * provide better support for binary (.glb) files (bug fixes)
    * promote `load_json`, `load_binary`, `save_json` and `save_binary` from internal methods 
* 1.5
    * align embedded data correctly
    * add `glb2gltf` and `gltf2glb` util functions to `pygltflib.utils` for easy file conversion
* 1.4 
    * add basic support for saving to binary GLTF (.glb) files
    * move undocumented non-core methods to `pygltfib.utils`
* 1.3 
    * add basic support for reading binary GLTF (.glb) files
* 1.2 
    * provide better json support
    * remove numpy requirement
    * suppress infer warning
    * add basic default methods
* 1.0 
    * initial release


## Install
```
pip install pygltflib
```


## Source

```
git clone https://gitlab.com/dodgyville/pygltflib
```


## More Detailed Usage
Note: These examples use the official [sample models](https://github.com/KhronosGroup/glTF-Sample-Models) provided by Khronos at:

https://github.com/KhronosGroup/glTF-Sample-Models



##### A simple mesh
```python3
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


### Loading and saving

`pygltflib` can load json-based .GLTF files and binary .GLB files, based on the file extension. 

#### GLTF files

```python3
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

```python3
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

#### Converting files

##### First method

```python3
>>> from pygltflib import GLTF2

>>> # convert glb to gltf
>>> glb = GLTF2().load("glTF-Sample-Models/2.0/Box/glTF-Binary/Box.glb")
>>> glb.save("test.gltf")

>>> # convert gltf to glb
>>> gltf = GLTF2().load("glTF-Sample-Models/2.0/Box/glTF/Box.gltf")
>>> gltf.save("test.glb")
```

##### Second method using utils

```python3
>>> from pygltflib import GLTF2
>>> from pygltflib.utils import glb2gltf, gltf2glb

>>> # convert glb to gltf
>>> glb2gltf("glTF-Sample-Models/2.0/Box/glTF-Binary/Box.glb")

>>> # convert gltf to glb
>>> gltf2glb("glTF-Sample-Models/2.0/Box/glTF/Box.gltf", "test.glb", override=True)

```

#### Converting buffers 
The data for a buffer in a GLTF2 files can be stored in the buffer object's URI string 
or in a binary file pointed to by the buffer objects' URI string or as a binary blob
inside a GLB file.

While saving and loading GLTF2 files is mostly handled transparently by the library, 
there may be some situations where you want a specific type of buffer storage.

For example, if you have a GLTF file that stores all the associated data in .bin files
but you want to create a single file, you need to convert the buffers from binary files
to data uris or glb binary data.

There is a convenience method named `conver_buffers` that can help.

```python3
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


### unittests
```
pytest tests.py
```

