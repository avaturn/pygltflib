# pygltflib

This is a library for reading, writing and handling GLTF files. It works for Python3.6 and above.

It supports the entire specification, including materials and animations. Main features are:
* GLB and GLTF support
* Buffer data conversion
* Extensions
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


#### Access the first node (the objects comprising the scene) of a scene?

```python3
gltf = GLTF2().load("glTF-Sample-Models/2.0/Box/glTF/Box.gltf")
current_scene = gltf.scenes[gltf.scene]
node_index = current_scene.nodes[0]  # scene.nodes is the indices, not the objects 
box = gltf.nodes[nodex_index]
box.matrix  # will output vertices for the box object
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

#### Access an extension?
```python3
# on a primitve
gltf.meshes[0].primitives[0].extensions['KHR_draco_mesh_compression']

# on a material
gltf.materials[0].extensions['ADOBE_materials_thin_transparency']

```

#### Add a custom attribute to Attributes?
```python3
# Application-specific semantics must start with an underscore, e.g., _TEMPERATURE.
a = Attributes()
a._MYCUSTOMATTRIBUTE = 123

gltf.meshes[0].primitives[0].attributes._MYOTHERATTRIBUTE = 456
```

#### Remove a bufferView?
```python3
gltf.remove_bufferView(0)  # this will update all accessors, images and sparse accessors to remove the first bufferView
```

#### Validate a gltf object?
```python3
from pygltflib import GLTF2
from pygltflib.validator import validate, summary
filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
gltf = GLTF2().load(filename)
validate(gltf)  # will throw an error depending on the problem
summary(gltf)  # will pretty print human readable summary of errors
# NOTE: Currently this experimental validator only validates a few rules about GLTF2 objects
```

#### Export texture images from a GLTF file to their own PNG files
```python3
from pygltflib import GLTF2
from pygltflib.utils import ImageFormat
filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
gltf = GLTF2().load(filename)
gltf.convert_images(ImageFormat.FILE)
gltf.images[0].uri  # will now be 0.png and the texture image will be saved in 0.png
```

#### Export texture images from a GLTF file to their own PNG files using custom file names
```python3
from pygltflib import GLTF2
from pygltflib.utils import ImageFormat
filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
gltf = GLTF2().load(filename)
gltf.images[0].name = "cube.png"  # will save the data uri to this file (regardless of data format)
gltf.convert_images(ImageFormat.FILE)
gltf.images[0].uri  # will now be cube.png and the texture image will be saved in cube.png
```

#### Import PNG files as textures into a GLTF.
```python3
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
* Enforce single underscore on custom Attribute attributes 
* Investigate creating classes from extensions
* Automated validation and visual inspection

#### Contributors
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

#### Thanks
`pygltflib` made for 'The Beat: A Glam Noir Game' supported by Film Victoria. 

#### Changelog
* 1.13.5
    * fix Matrix, Translation, Scale, and Rotation to default to None
    * change `utils.validator` by moving to `validator.validate`
    * add `validator.summary` to provide human readable output of validator
    * add some more unit tests

* 1.13.4
    * add warning to `remove_bufferView` if leaving dangling references to removed bufferView
    * add tests for `remove_bufferView`
    * add node access and remove_bufferView examples to README
    * add validation for animation channels
    * change `metallicRoughnessTexture` to use `TextureInfo`
    * change requirements to not install dataclasses in python 3.7 and above
    * fix `remove_bufferView` when sparse accessor is None
    * fix spelling of `InvalidAccessorSparseIndicesComponentTypeException`

* 1.13.3
    * add support to `GLTF.convert_images` to convert from buffers to image files. NOTE: Does not update buffer yet.
    * add support to `GLTF.convert_images` to convert from buffers to data uris. NOTE: Does not update buffer yet.
    * add accessor sparse indices bufferview check to validator 
    * fix test suite to write tmp files to tmp directory instead of install directory
    * remove support for old versions of dataclasses-json
    * renamed CUBICSPLINE, LINEAR and STEP to ANIM_LINEAR, ANIM_STEP, ANIM_CUBICSPLINE to fix clash with webGL constants 
    * change bin file conversion to only lose binary blob on successful file export

* 1.13.2 
    * add deprecated to pip setup

* 1.13.1
    * add `GLTF.convert_images` method for converting texture image data from data uris to files and vice versa
    * add 'name' attribute to `Image`
    * add more unittests
    * change `Primitive` so that `Attributes` is created on init 

* 1.13.0
    * NOTE: There are a few small deprecations in this version to tighten up the library that will be removed in version 2.0.0
    * deprecate class `SparseAccessor` in favour of `AccessorSparseIndices` and `AccessorSparseValues` (please update your code)
    * deprecate class `MaterialTexture` in favour of `TextureInfo` to better match GLTF2 specification (please update your code)
    * deprecate `AlphaMode` ENUM in favour of constants (eg replace `AlphaMode.OPAQUE` with `OPAQUE` (please update your code)
    * fix support for `material.occlusionTextureInfo`  
    * fix support for `material.normalTextureInfo`
    * fix sampler support in `Animation` class by adding `AnimationSampler`
    * add default values for Accessor, AnimationSampler, BufferView, Material, PbrMetallicRoughness, Primitive, Sampler
    * add Optional to attributes for better type hinting
    * add initial `utils.validator` to validate GLTF2 object accessor and bufferViews
    
* 1.12.0
    * fix bug with binfile path handling
    
* 1.11.10
    * convert load methods from staticmethod to classmethods

* 1.11.9
    * change GLTF.load to a staticmethod
    * add AlphaMode enum type

* 1.11.8
    * add missing top level extensions
    
* 1.11.7
    * add missing `normalized` flag to Accessor

* 1.11.6
    * add support for extensions
    * add support for extras
    * add support for custom attributes on Attributes
    * set Primitive.attributes to `None` by default (use `primitive.attributes = Attributes()`)
    * remove warning about byteStride as that is not the responsibility of this library
    * add lots of tests

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

There is a convenience method named `convert_buffers` that can help.

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

#### Converting texture images
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

```python3

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


#### Extensions
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

