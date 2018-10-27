# pygltflib

Python library for reading, writing and handling GLTF files. Python3.6+

## Requirements
* Python 3.6
* dataclasses
* dataclasses-json
* numpy


## About
This is an unofficial library that tracks the [official file format](https://github.com/KhronosGroup/glTF/blob/master/specification/2.0/README.md) for GLTF2. 

The library was initially built to load and save simple meshes but support for the entire spec, including materials 
and animations is pretty good. 
Check the table below for an idea of which sample models validate.

Questions? Contributions? Bug reports? Open an issue on the [gitlab page for the project](https://gitlab.com/dodgyville/pygltflib).


Roadmap:
* Add helper functions for creating meshes
* Support for binary GLTF

## Install

### PIP

pip install pygltflib 

or

python -m pip install pygltflib


### Source

git clone https://gitlab.com/dodgyville/pygltflib

## Usage
Note: These examples use the official [sample models](https://github.com/KhronosGroup/glTF-Sample-Models) provided by Kronos at:

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

### Loading and saving

```python3
>>> from pygltflib import GLTF2
>>> filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
>>> gltf = GLTF2().load(filename)
>>> gltf
>>> gltf.scene
0

>>> gltf.scenes
[Scene(name='', nodes=[0])]

>>> gltf.nodes[0]
Node(mesh=0, name='AnimatedCube', rotation=[0.0, -1.0, 0.0, 0.0])

>>> gltf.nodes[0].name
'AnimatedCube'

>>> gltf.meshes[0].primitives[0].attributes
Attributes(NORMAL=4, POSITION=None, TANGENT=5, TEXCOORD_0=6)

>>> filename2 = "test.gltf"
>>> gltf = GLTF2().save(filename2)

```


## Running the tests

### Status of gltf-validator
Using sample models loaded and then saved using this library, here are validator reports (blank is untested). 


| Model | Validator Status |
| ------| ------- |
| 2CylinderEngine | passes | 
| AlphaBlendModeTest | passes | 
| AnimatedCube | passes | 
| AnimatedMorphCube | passes | 
| AnimatedMorphSphere | passes | 
| AnimatedTriangle | passes | 
| Avocado | passes | 
| BarramundiFish | passes | 
| BoomBox | passes | 
| BoomBoxWithAxes | passes | 
| Box | passes | 
| BoxAnimated | passes | 
| BoxInterleaved | passes | 
| BoxTextured | passes | 
| BoxTexturedNonPowerOfTwo | passes | 
| BoxVertexColors | passes | 
| BrainStem | passes | 
| Buggy | passes | 
| Cameras | passes | 
| CesiumMan | passes | 
| CesiumMilkTruck | passes | 
| Corset | passes | 
| Cube | passes | 
| DamagedHelmet | passes | 
| Duck | passes | 
| FlightHelmet | passes | 
| GearboxAssy | passes | 
| Lantern | passes | 
| MetalRoughSpheres | passes | 
| Monster | passes | 
| MultiUVTest | passes | 
| NormalTangentMirrorTest | passes | 
| NormalTangentTest | passes | 
| OrientationTest | passes | 
| ReciprocatingSaw | passes | 
| RiggedFigure | passes | 
| RiggedSimple | passes | 
| SciFiHelmet | passes | 
| SimpleMeshes | passes | 
| SimpleMorph | passes | 
| SimpleSparseAccessor | passes | 
| SpecGlossVsMetalRough | passes | 
| Sponza | passes | 
| Suzanne | passes | 
| TextureCoordinateTest | passes | 
| TextureSettingsTest | passes | 
| TextureTransformTest | passes |
| Triangle | passes | 
| TriangleWithoutIndices | passes | 
| TwoSidedPlane | passes | 
| VC | passes | 
| VertexColorTest | passes | 
| WaterBottle | passes | 





### unittests
python -m tests

