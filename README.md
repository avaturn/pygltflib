# pygltflib

Python library for reading, writing and handling GLTF files. Python3.6+

## Requirements
* Python 3.6
* dataclasses
* dataclasses-json
* numpy


## About
The library tracks the [official file format](https://github.com/KhronosGroup/glTF/blob/master/specification/2.0/README.md) for GLTF2. 

The library was initially built to load and save simple meshes, support for materials and animations is experimental. 
Check the table below for an idea of which sample models validate.



Roadmap:
* Finishing building out schemas 
* Validate sample models
* Add helper functions

## Install
pip install pygltflib 

or

python -m pip install pygltflib

## Usage
Note: These examples use the official [sample models](https://github.com/KhronosGroup/glTF-Sample-Models) provided by Kronos at:

https://github.com/KhronosGroup/glTF-Sample-Models

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
| AnimatedMorphCube |  | 
| AnimatedMorphSphere |  | 
| AnimatedTriangle |  | 
| Avocado | passes | 
| BarramundiFish | passes | 
| BoomBox |  | 
| BoomBoxWithAxes |  | 
| Box | passes | 
| BoxAnimated | passes | 
| BoxInterleaved | passes | 
| BoxTextured |  | 
| BoxTexturedNonPowerOfTwo |  | 
| BoxVertexColors |  | 
| BrainStem |  | 
| Buggy |  | 
| Cameras |  | 
| CesiumMan | passes | 
| CesiumMilkTruck | passes | 
| Corset |  | 
| Cube | passes | 
| DamagedHelmet |  | 
| Duck |  | 
| FlightHelmet |  | 
| GearboxAssy |  | 
| Lantern |  | 
| MetalRoughSpheres |  | 
| Monster | passes | 
| MultiUVTest |  | 
| NormalTangentMirrorTest |  | 
| NormalTangentTest |  | 
| OrientationTest |  | 
| ReciprocatingSaw |  | 
| RiggedFigure |  | 
| RiggedSimple |  | 
| SciFiHelmet |  | 
| SimpleMeshes | passes | 
| SimpleMorph |  | 
| SimpleSparseAccessor |  | 
| SpecGlossVsMetalRough |  | 
| Sponza |  | 
| Suzanne |  | 
| TextureCoordinateTest |  | 
| TextureSettingsTest |  | 
| TextureTransformTest |  |
| Triangle | passes | 
| TriangleWithoutIndices |  | 
| TwoSidedPlane | passes | 
| VC |  | 
| VertexColorTest |  | 
| WaterBottle |  | 





### unittests
python -m tests

