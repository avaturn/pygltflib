# pygltflib

Python library for reading, writing and handling GLTF files. Python3.7+

## Requirements
* Python 3.7
* numpy

## Install
pip install pygltflib 

or

python3.7 -m pip install pygltflib

## Usage
Note: These examples use the official [sample models](https://github.com/KhronosGroup/glTF-Sample-Models) provided by Kronos at:

https://github.com/KhronosGroup/glTF-Sample-Models

```python3.7
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
Attributes(NORMAL=4, POSITON=None, TANGENT=5, TEXCOORD_0=6)

>>> filename2 = "test.gltf"
>>> gltf = GLTF2().save(filename2)

```

```python
from pygltflib import GLTF2
filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
gltf = GLTF2().load(filename)
gltf.nodes[0].name = "AnimatedCubeHelloWorld"
filename2 = "test.gltf"
gltf = GLTF2().save(filename2)

```

## Running the tests

### Status of gltf-validator on sample models loaded and then saved using this library

| Model | Validator Status |
| ------| ------- |
| 2CylinderEngine | Untested | 
| AlphaBlendModeTest | Untested | 
| AnimatedCube | Passing (4 infos) | 
| AnimatedMorphCube | Untested | 
| AnimatedMorphSphere | Untested | 
| AnimatedTriangle | Untested | 
| Avocado | Untested | 
| BarramundiFish | Untested | 
| BoomBox | Untested | 
| BoomBoxWithAxes | Untested | 
| Box | Untested | 
| BoxAnimated | Untested | 
| BoxInterleaved | Untested | 
| BoxTextured | Untested | 
| BoxTexturedNonPowerOfTwo | Untested | 
| BoxVertexColors | Untested | 
| BrainStem | Untested | 
| Buggy | Untested | 
| Cameras | Untested | 
| CesiumMan | Untested | 
| CesiumMilkTruck | Untested | 
| Corset | Untested | 
| Cube | Untested | 
| DamagedHelmet | Untested | 
| Duck | Untested | 
| FlightHelmet | Untested | 
| GearboxAssy | Untested | 
| Lantern | Untested | 
| MetalRoughSpheres | Untested | 
| Monster | Untested | 
| MultiUVTest | Untested | 
| NormalTangentMirrorTest | Untested | 
| NormalTangentTest | Untested | 
| OrientationTest | Untested | 
| ReciprocatingSaw | Untested | 
| RiggedFigure | Untested | 
| RiggedSimple | Untested | 
| SciFiHelmet | Untested | 
| SimpleMeshes | Untested | 
| SimpleMorph | Untested | 
| SimpleSparseAccessor | Untested | 
| SpecGlossVsMetalRough | Untested | 
| Sponza | Untested | 
| Suzanne | Untested | 
| TextureCoordinateTest | Untested | 
| TextureSettingsTest | Untested | 
| TextureTransformTest | Untested |
| Triangle | Untested | 
| TriangleWithoutIndices | Untested | 
| TwoSidedPlane | Untested | 
| VC | Untested | 
| VertexColorTest | Untested | 
| WaterBottle | Untested | 





### unittests
python -m tests


### doctests
python -m doctest -v README.md
