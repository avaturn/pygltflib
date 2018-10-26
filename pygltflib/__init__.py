"""
Copyright (c) 2018 Luke Miller

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

from dataclasses import dataclass, field, asdict
from dataclasses_json import dataclass_json
from dataclasses_json.core import _CollectionEncoder, _decode_dataclass
from datetime import date, datetime

import json
import numpy as np
import os, os.path
from typing import List, TextIO
from typing import Callable, Optional, Tuple, TypeVar, Union


try:
    import git
except ImportError:
    git = None

if git:
    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    __version__ = sha
else:
    __version__ = "0.1"

A = TypeVar('A')


LINEAR = "LINEAR"
STEP = "STEP"
CALMULLROMSPLINE = "CALMULLROMSPLINE"
CUBICSPLINE = "CUBICSPLINE"

SCALAR = "SCALAR"
VEC2 = "VEC2"
VEC3 = "VEC3"
VEC4 = "VEC4"
MAT2 = "MAT2"
MAT3 = "MAT3"
MAT4 = "MAT4"

POSITION = "POSITION"
NORMAL = "NORMAL"
TANGENT = "TANGENT"
TEXCOORD_0 = "TEXCOORD_0"
TEXCOORD_1 = "TEXCOORD_1"
COLOR_0 = "COLOR_0"
JOINTS_0 = "JOINTS_0"
WEIGHTS_0 = "WEIGHTS_0"


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


@dataclass_json
@dataclass
class Asset:
    version: str = "2.0"
    generator: str = f"pygltflib@v{__version__}"


@dataclass_json
@dataclass
class Scene:
    name: str = ""
    nodes: List[int] = field(default_factory=list)


@dataclass_json
@dataclass
class Node:
    pass


@dataclass_json
@dataclass
class Attributes:
    NORMAL: int = None
    POSITON: int = None
    TANGENT: int = None
    TEXCOORD_0: int = None


@dataclass_json
@dataclass
class Primitive:
    attributes: Attributes = Attributes()
    indices: int = None
    material: int = None
    mode: int = None


@dataclass_json
@dataclass
class Mesh:
    name: str = None
    primitives: List[Primitive] = field(default_factory=list)


@dataclass_json
@dataclass
class Accessor:
    bufferView: int = None
    byteOffset: int = None
    componentType: int = None
    count: int = None
    type: str = None
    max: List[float] = field(default_factory=list)
    min: List[float] = field(default_factory=list)


@dataclass_json
@dataclass
class BufferView:
    buffer: int = None
    byteOffset: int = None
    byteLength: int = None
    target: int = None


@dataclass_json
@dataclass
class Buffer:
    uri: str = ""
    byteLength: int = None


@dataclass_json
@dataclass
class Camera:
    pass


@dataclass_json
@dataclass
class Material:
    name: str = ""


@dataclass_json
@dataclass
class Sample:
    pass


@dataclass_json
@dataclass
class Node:
    #mesh: int = None
    pass
 #   name: str = None
#    rotation: List[float] = field(default_factory=list)


@dataclass_json
@dataclass
class Texture:
    sampler: int = None
    source: int = None



@dataclass
class GLTF2:
    asset: Asset = Asset()
    scenes: List[Scene] = field(default_factory=list)
    buffers: List[Buffer] = field(default_factory=list)
    bufferViews: List[BufferView] = field(default_factory=list)
    accessors: List[Accessor] = field(default_factory=list)
    materials: List[Material] = field(default_factory=list)
    meshes: List[Mesh] = field(default_factory=list)
    nodes: List[Node] = field(default_factory=list)
    samplers: List[Sample] = field(default_factory=list)
    textures: List[Texture] = field(default_factory=list)
    scene: int = None

    # to_json and from_json from dataclasses_json
    # courtesy https://github.com/lidatong/dataclasses-json
    def to_json(self,
                *,
                skipkeys: bool = False,
                ensure_ascii: bool = True,
                check_circular: bool = True,
                allow_nan: bool = True,
                indent: Optional[Union[int, str]] = None,
                separators: Tuple[str, str] = None,
                default: Callable = None,
                sort_keys: bool = False,
                **kw) -> str:

        data = asdict(self)

        def del_none(d):
            """
            Delete keys with the value ``None`` in a dictionary, recursively.

            This alters the input so you may wish to ``copy`` the dict first.

            Courtest Chris Morgan:
            https://stackoverflow.com/questions/4255400/exclude-empty-null-values-from-json-serialization
            """
            # For Python 3, write `list(d.items())`; `d.items()` won’t work
            # For Python 2, write `d.items()`; `d.iteritems()` won’t work
            for key, value in list(d.items()):
                if value is None or (hasattr(value, '__iter__') and len(value) == 0):
                    del d[key]
                elif isinstance(value, dict):
                    del_none(value)
            return d  # For convenience
        data = del_none(data)
        if len(self.scenes) == 0:
            del data["scene"]

        return json.dumps(data,
                          cls=_CollectionEncoder,
                          skipkeys=skipkeys,
                          ensure_ascii=ensure_ascii,
                          check_circular=check_circular,
                          allow_nan=allow_nan,
                          indent=indent,
                          separators=separators,
                          default=default,
                          sort_keys=sort_keys,
                          **kw)

    @classmethod
    def from_json(cls: A,
                  s: str,
                  *,
                  encoding=None,
                  parse_float=None,
                  parse_int=None,
                  parse_constant=None,
                  infer_missing=False,
                  **kw) -> A:
        init_kwargs = json.loads(s,
                                 encoding=encoding,
                                 parse_float=parse_float,
                                 parse_int=parse_int,
                                 parse_constant=parse_constant,
                                 **kw)
        return _decode_dataclass(cls, init_kwargs, infer_missing)

    def gltf_to_json(self) -> str:
        return self.to_json()  # default=json_serial, allow_nan=False, skipkeys=True)

    def save(self, fname):
        with open(fname, "w") as f:
            f.write(self, self.gltf_to_json())
        return True

    def load(self, fname):
        if not os.path.exists(fname):
            print("ERROR: File not found", fname)
            return None
        with open(fname, "r") as f:
            obj = GLTF2.from_json(f.read(), infer_missing=True)
        return obj


def main():
    # print(GLTF2().gltf_to_json())
    gltf = GLTF2().load("glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf")
    #import doctest
    #doctest.testfile("../README.md")

if __name__ == "__main__":
    main()