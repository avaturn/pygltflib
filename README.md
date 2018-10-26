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
>>> import pdb; pdb.set_trace()
>>> gltf
>>> gltf.scene
0

>>> gltf.scenes
[Scene(name='', nodes=[0])]

>>> gltf.scenes[0].nodes[0]
0

>>> gltf.meshes[0].primitives[0].attributes
    Attributes(NORMAL=4, POSITON=None, TANGENT=5, TEXCOORD_0=6)

>>> gltf = GLTF2().save(filename)

```

## Running the tests

### unittests
python -m tests


### doctests
python -m doctest -v README.md
