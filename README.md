# pygltflib

Python library for reading, writing and handling GLTF files. Python3.6+

## Requirements
* Python 3.6+
* dataclasses
* dataclasses-json
* pytest (optional)

It requires python 3.6 and above because it uses dataclasses and all attributes are type hinted. And f-strings, plenty of f-strings.

## About
This is an unofficial library that tracks the [official file format](https://github.com/KhronosGroup/glTF/blob/master/specification/2.0/README.md) for GLTF2. 

The library was initially built to load and save simple meshes but support for the entire spec, including materials 
and animations is pretty good. Supports both json (.gltf) and binary (.glb) file formats, although .glb support 
is missing some features at the moment. 

Check the table below for an idea of which sample models validate.

Questions? Contributions? Bug reports? Open an issue on the [gitlab page for the project](https://gitlab.com/dodgyville/pygltflib).
We are very interested in hearing your use cases for `pygltflib` to help drive the roadmap.

###### Roadmap:
* Add helper functions for creating meshes
* Full support for binary GLTF (.glb) files
* Reject file overwrites unless overwrite flag set
* Give options on storing binary buffers (embedded vs external)


###### Contributors:
* Luke Miller
* Sebastian Höffner
* Arthur van Hoff


###### Changelog:
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

### PIP

###### Method 1
`pip install pygltflib` 

###### Method 2
`python -m pip install pygltflib`

###### Method 3
`py -3 -m pip install pygltflib`


### Source

`git clone https://gitlab.com/dodgyville/pygltflib`

## Usage
Note: These examples use the official [sample models](https://github.com/KhronosGroup/glTF-Sample-Models) provided by Khronos at:

https://github.com/KhronosGroup/glTF-Sample-Models

### Creating
```python3
>>> from pygltflib import GLTF2, Scene
>>> gltf = GLTF2()
>>> gltf.scene # no scene set by default
>>> len(gltf.scenes)
0

>>> scene = Scene()
>>> gltf.scenes.append(scene)
>>> len(gltf.scenes)
1

```
##### A simple mesh
```python3
    from pygltflib import *
    
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
>>> from pygltflib.utils import glb2gltf, gltf2glb
>>> # convert glb to gltf
>>> glb2gltf("glTF-Sample-Models/2.0/Box/glTF-Binary/Box.glb")

>>> # convert gltf to glb
>>> gltf2glb("glTF-Sample-Models/2.0/Box/glTF/Box.gltf", "test.glb", override=True)


```

## Running the tests

### Status of gltf-validator
Using sample models loaded and then saved using this library, here are validator reports (blank is untested). 


#### Validator Status
| Model | gltf to gltf | gltf to glb | glb to gltf | glb to glb | 
| ------| ------- | ------- | ------- | ------ |
| 2CylinderEngine | passes | passes | passes | 
| AlphaBlendModeTest | passes | passes | passes |
| AnimatedCube | passes | passes | no glb available | no glb available|
| AnimatedMorphCube | passes |  passes | passes |
| AnimatedMorphSphere | passes |  passes | passes | passes
| AnimatedTriangle | passes |  passes | no glb available | no glb available|
| Avocado | passes |  passes | passes | passes
| BarramundiFish | passes | passes | passes
| BoomBox | passes | passes | passes
| BoomBoxWithAxes | passes | passes | no glb available | no glb available|
| Box | passes | passes
| BoxAnimated | passes | passes
| BoxInterleaved | passes | passes | | passes
| BoxTextured | passes | passes
| BoxTexturedNonPowerOfTwo | passes | passes
| BoxVertexColors | passes | passes 
| BrainStem | passes | passes | passes
| Buggy | passes | passes | passes
| Cameras | passes | passes | no glb available | no glb available|
| CesiumMan | passes | passes
| CesiumMilkTruck | passes | passes
| Corset | passes | passes |
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
| TextureCoordinateTest | passes | passes | 
| TextureSettingsTest | passes | passes |
| TextureTransformTest | passes | passes | 
| Triangle | passes | passes | no glb available | no glb available|
| TriangleWithoutIndices | passes | passes | no glb available | no glb available|
| TwoSidedPlane | passes | passes | no glb available | no glb available|
| VC | passes | *fails* | passes | passes
| VertexColorTest | passes | passes | passes  | passes
| WaterBottle | passes | passes | passes | passes


### unittests
`pytest tests.py`
    
### Thanks
`pygltflib` made for 'The Beat: A Glam Noir Game' supported by Film Victoria. 