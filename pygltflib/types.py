"""
pygltflib : A Python library for reading, writing and handling GLTF files.


Copyright (c) 2018,2021 Luke Miller

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
import copy
import json

import warnings
from dataclasses import _is_dataclass_instance, dataclass, field, fields
from datetime import date, datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union
from urllib.parse import unquote

from dataclasses_json import dataclass_json as dataclass_json
from dataclasses_json.core import _decode_dataclass
from dataclasses_json.core import _ExtendedEncoder as JsonEncoder

__version__ = "1.15.3"

"""
About the GLTF2 file format:

glTF uses a right-handed coordinate system, that is, the cross product of +X and +Y yields +Z. glTF defines +Y as up.
The front of a glTF asset faces +Z.
The units for all linear distances are meters.
All angles are in radians.
Positive rotation is counterclockwise.
"""

A = TypeVar("A")

ANIM_LINEAR = "LINEAR"
ANIM_STEP = "STEP"
ANIM_CALMULLROMSPLINE = "CALMULLROMSPLINE"
ANIM_CUBICSPLINE = "CUBICSPLINE"

SCALAR = "SCALAR"
VEC2 = "VEC2"
VEC3 = "VEC3"
VEC4 = "VEC4"
MAT2 = "MAT2"
MAT3 = "MAT3"
MAT4 = "MAT4"

BYTE = 5120
UNSIGNED_BYTE = 5121
SHORT = 5122
UNSIGNED_SHORT = 5123
UNSIGNED_INT = 5125
FLOAT = 5126

COMPONENT_TYPES = [BYTE, UNSIGNED_BYTE, SHORT, UNSIGNED_SHORT, UNSIGNED_INT, FLOAT]
ACCESSOR_SPARSE_INDICES_COMPONENT_TYPES = [UNSIGNED_BYTE, UNSIGNED_SHORT, UNSIGNED_INT]

# MESH PRIMITIVE MODES
POINTS = 0
LINES = 1
LINE_LOOP = 2
LINE_STRIP = 3
TRIANGLES = 4
TRIANGLE_STRIP = 5
TRIANGLE_FAN = 6

MESH_PRIMITIVE_MODES = [
    POINTS,
    LINES,
    LINE_LOOP,
    LINE_STRIP,
    TRIANGLES,
    TRIANGLE_STRIP,
    TRIANGLE_FAN,
]

# The bufferView target that the GPU buffer should be bound to.
ARRAY_BUFFER = 34962  # eg vertex data
ELEMENT_ARRAY_BUFFER = 34963  # eg index data

BUFFERVIEW_TARGETS = [ARRAY_BUFFER, ELEMENT_ARRAY_BUFFER]

TRANSLATION = "translation"
ROTATION = "rotation"
SCALE = "scale"
WEIGHTS = "weights"

ANIMATION_CHANNEL_TARGET_PATHS = [TRANSLATION, ROTATION, SCALE, WEIGHTS]

POSITION = "POSITION"
NORMAL = "NORMAL"
TANGENT = "TANGENT"
TEXCOORD_0 = "TEXCOORD_0"
TEXCOORD_1 = "TEXCOORD_1"
COLOR_0 = "COLOR_0"
JOINTS_0 = "JOINTS_0"
WEIGHTS_0 = "WEIGHTS_0"

CLAMP_TO_EDGE = 33071
MIRRORED_REPEAT = 33648
REPEAT = 10497

WRAPPING_MODES = [CLAMP_TO_EDGE, MIRRORED_REPEAT, REPEAT]

IMAGEJPEG = "image/jpeg"
IMAGEPNG = "image/png"

IMAGE_MIMETYPES = [IMAGEJPEG, IMAGEPNG]

NEAREST = 9728
LINEAR = 9729
NEAREST_MIPMAP_NEAREST = 9984
LINEAR_MIPMAP_NEAREST = 9985
NEAREST_MIPMAP_LINEAR = 9986
LINEAR_MIPMAP_LINEAR = 9987

MAGNIFICATION_FILTERS = [NEAREST, LINEAR]
MINIFICATION_FILTERS = [
    NEAREST,
    LINEAR,
    NEAREST_MIPMAP_NEAREST,
    LINEAR_MIPMAP_NEAREST,
    NEAREST_MIPMAP_LINEAR,
    LINEAR_MIPMAP_LINEAR,
]

PERSPECTIVE = "perspective"
ORTHOGRAPHIC = "orthographic"

CAMERA_TYPES = [PERSPECTIVE, ORTHOGRAPHIC]

BLEND = "BLEND"
MASK = "MASK"
OPAQUE = "OPAQUE"

MATERIAL_ALPHAMODES = [OPAQUE, MASK, BLEND]

JSON = "JSON"
BIN = "BIN\x00"
MAGIC = b"glTF"
GLTF_VERSION = 2  # version this library exports
GLTF_MIN_VERSION = 2  # minimum version this library can load
GLTF_MAX_VERSION = 2  # maximum supported version this library can load

DATA_URI_HEADER = "data:application/octet-stream;base64,"


class BufferFormat(Enum):
    DATAURI = "data uri"
    BINARYBLOB = "binary blob"
    BINFILE = "bin file"


class ImageFormat(Enum):
    DATAURI = "data uri"
    FILE = "image file"
    BUFFERVIEW = "buffer view"


# backwards and forwards compat dataclasses-json and dataclasses
class LetterCase(Enum):
    CAMEL = "camelCase"
    KEBAB = "kebab-case"
    SNAKE = "snake_case"


def delete_empty_keys(dictionary):
    """
    Delete keys with the value ``None`` in a dictionary, recursively.

    This alters the input so you may wish to ``copy`` the dict first.

    Courtesy Chris Morgan and modified from:
    https://stackoverflow.com/questions/4255400/exclude-empty-null-values-from-json-serialization
    """
    for key, value in list(dictionary.items()):
        if value is None or (hasattr(value, "__iter__") and len(value) == 0):
            del dictionary[key]
        elif isinstance(value, dict) and key != "extensions":
            # delete empty dicts except when the dictionary is an extension inside "extensions".
            # The extension exemption is because we use dicts for extensions instead of dataclass objects
            delete_empty_keys(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    delete_empty_keys(item)
    return dictionary  # For convenience


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def gltf_asdict(obj, *, dict_factory=dict):
    # convert a dataclass object to a dict
    if not _is_dataclass_instance(obj):
        raise TypeError("asdict() should be called on dataclass instances")
    return _asdict_inner(obj, dict_factory)


def _asdict_inner(obj, dict_factory):
    # return the same result as dataclass _asdict_inner except for Attributes, which can have custom specifiers.
    if type(obj) == Attributes:
        return copy.deepcopy(obj.__dict__)
    if _is_dataclass_instance(obj):
        result = []
        for f in fields(obj):
            value = _asdict_inner(getattr(obj, f.name), dict_factory)
            result.append((f.name, value))
        return dict_factory(result)
    elif isinstance(obj, tuple) and hasattr(obj, "_fields"):
        return type(obj)(*[_asdict_inner(v, dict_factory) for v in obj])
    elif isinstance(obj, (list, tuple)):

        return type(obj)(_asdict_inner(v, dict_factory) for v in obj)
    elif isinstance(obj, dict):
        return type(obj)(
            (_asdict_inner(k, dict_factory), _asdict_inner(v, dict_factory))
            for k, v in obj.items()
        )
    else:
        return copy.deepcopy(obj)


@dataclass_json
@dataclass
class Property:
    extensions: Optional[Dict[str, Any]] = field(default_factory=dict)
    extras: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass_json
@dataclass
class Asset(Property):
    generator: Optional[str] = f"pygltflib@v{__version__}"
    copyright: Optional[str] = None
    version: str = "2.0"  # required
    minVersion: Optional[str] = None


# Attributes is a special case so we provide our own json handling
class Attributes:
    def __init__(
        self,
        POSITION=None,
        NORMAL=None,
        TANGENT=None,
        TEXCOORD_0=None,
        TEXCOORD_1=None,
        COLOR_0: int = None,
        JOINTS_0: int = None,
        WEIGHTS_0=None,
        *args,
        **kwargs,
    ):
        self.POSITION = POSITION
        self.NORMAL = NORMAL
        self.TANGENT = TANGENT
        self.TEXCOORD_0 = TEXCOORD_0
        self.TEXCOORD_1 = TEXCOORD_1
        self.COLOR_0 = COLOR_0
        self.JOINTS_0 = JOINTS_0
        self.WEIGHTS_0 = WEIGHTS_0
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return (
            self.__class__.__qualname__
            + "("
            + ", ".join([f"{f}={v}" for f, v in self.__dict__.items()])
            + ")"
        )

    def to_json(self, *args, **kwargs):
        # Attributes objects can have custom attrs, so use our own json conversion methods.
        data = copy.deepcopy(self.__dict__)
        return json.dumps(data)

    @staticmethod
    def from_json():
        warnings.warn(
            "To allow custom attributes on Attributes, we don't use dataclasses-json on this class."
            "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues"
        )


@dataclass_json
@dataclass
class Primitive(Property):
    attributes: Attributes = field(default_factory=Attributes)  # required
    indices: Optional[int] = None
    mode: Optional[int] = TRIANGLES
    material: Optional[int] = None
    targets: Optional[List[Attributes]] = field(default_factory=list)


@dataclass_json
@dataclass
class Mesh(Property):
    primitives: List[Primitive] = field(default_factory=list)  # required
    weights: Optional[List[float]] = field(default_factory=list)
    name: Optional[str] = None


@dataclass_json
@dataclass
class AccessorSparseIndices(Property):
    bufferView: int = None  # required
    byteOffset: Optional[int] = 0
    componentType: int = None  # required


@dataclass_json
@dataclass
class AccessorSparseValues(Property):
    bufferView: int = None  # required
    byteOffset: Optional[int] = 0


@dataclass_json
@dataclass
class Sparse(Property):
    count: int = None  # required
    indices: AccessorSparseIndices = None  # required
    values: AccessorSparseValues = None  # required


@dataclass_json
@dataclass
class Accessor(Property):
    bufferView: Optional[int] = None
    byteOffset: Optional[int] = 0
    componentType: int = None  # required
    normalized: Optional[bool] = False
    count: int = None  # required
    type: str = None  # required
    sparse: Optional[Sparse] = None
    max: Optional[List[float]] = field(default_factory=list)
    min: Optional[List[float]] = field(default_factory=list)
    name: Optional[str] = None


@dataclass_json
@dataclass
class BufferView(Property):
    buffer: int = None
    byteOffset: Optional[int] = 0
    byteLength: int = None
    byteStride: Optional[int] = None
    target: Optional[int] = None
    name: Optional[str] = None


@dataclass_json
@dataclass
class Buffer(Property):
    uri: Optional[str] = None
    byteLength: int = None


@dataclass_json
@dataclass
class Perspective(Property):
    aspectRatio: Optional[float] = None
    yfov: float = None  # required
    zfar: Optional[float] = None
    znear: float = None  # required


@dataclass_json
@dataclass
class Orthographic(Property):
    xmag: float = None  # required
    ymag: float = None  # required
    zfar: float = None  # required
    znear: float = None  # required


@dataclass_json
@dataclass
class Camera(Property):
    perspective: Optional[Perspective] = None
    orthographic: Optional[Orthographic] = None
    type: str = None
    name: Optional[str] = None


@dataclass_json
@dataclass
class TextureInfo(Property):
    index: int = None  # required
    texCoord: Optional[int] = 0


@dataclass_json
@dataclass
class OcclusionTextureInfo(Property):
    index: Optional[int] = None
    texCoord: Optional[int] = None
    strength: Optional[float] = 1.0


@dataclass_json
@dataclass
class NormalMaterialTexture(Property):
    index: Optional[int] = None
    texCoord: Optional[int] = None
    scale: Optional[float] = 1.0


@dataclass_json
@dataclass
class PbrMetallicRoughness(Property):
    baseColorFactor: Optional[List[float]] = field(
        default_factory=lambda: [1.0, 1.0, 1.0, 1.0]
    )
    metallicFactor: Optional[float] = 1.0
    roughnessFactor: Optional[float] = 1.0
    baseColorTexture: Optional[TextureInfo] = None
    metallicRoughnessTexture: Optional[TextureInfo] = None


@dataclass_json
@dataclass
class Material(Property):
    pbrMetallicRoughness: Optional[PbrMetallicRoughness] = None
    normalTexture: Optional[NormalMaterialTexture] = None
    occlusionTexture: Optional[OcclusionTextureInfo] = None
    emissiveFactor: Optional[List[float]] = field(
        default_factory=lambda: [0.0, 0.0, 0.0]
    )
    emissiveTexture: Optional[TextureInfo] = None
    alphaMode: Optional[str] = OPAQUE
    alphaCutoff: Optional[float] = 0.5
    doubleSided: Optional[bool] = False
    name: Optional[str] = None


@dataclass_json
@dataclass
class Sampler(Property):
    """
    Samplers are stored in the samplers array of the asset.
    Each sampler specifies filter and wrapping options corresponding to the GL types
    """

    input: Optional[int] = None
    interpolation: Optional[str] = None
    output: Optional[int] = None
    magFilter: Optional[int] = None
    minFilter: Optional[int] = None
    wrapS: Optional[int] = REPEAT  # repeat wrapping in S (U)
    wrapT: Optional[int] = REPEAT  # repeat wrapping in T (V)


@dataclass_json
@dataclass
class Node(Property):
    mesh: Optional[int] = None
    skin: Optional[int] = None
    rotation: Optional[List[float]] = None
    translation: Optional[List[float]] = None
    scale: Optional[List[float]] = None
    children: Optional[List[int]] = field(default_factory=list)
    matrix: Optional[List[float]] = None
    camera: Optional[int] = None
    name: Optional[str] = None


@dataclass_json
@dataclass
class Skin(Property):
    inverseBindMatrices: Optional[int] = None
    skeleton: Optional[int] = None
    joints: Optional[List[int]] = field(default_factory=list)
    name: Optional[str] = None


@dataclass_json
@dataclass
class Scene(Property):
    name: Optional[str] = None
    nodes: Optional[List[int]] = field(default_factory=list)


@dataclass_json
@dataclass
class Texture(Property):
    sampler: Optional[int] = None
    source: Optional[int] = None
    name: Optional[str] = None


@dataclass_json
@dataclass
class Image(Property):
    uri: str = None
    mimeType: str = None
    bufferView: int = None
    name: Optional[str] = None

    @property
    def current_format(self):
        if self.bufferView is not None:
            return ImageFormat.BUFFERVIEW

        if self.uri is None:
            assert False

        if self.uri.startswith("data:"):
            return ImageFormat.DATAURI
        else:
            return ImageFormat.FILE


@dataclass_json
@dataclass
class AnimationChannelTarget(Property):
    node: Optional[int] = None
    path: str = None  # required


@dataclass_json
@dataclass
class AnimationSampler(Property):
    input: int = None  # required
    interpolation: Optional[str] = ANIM_LINEAR
    output: int = None  # required


@dataclass_json
@dataclass
class AnimationChannel(Property):
    sampler: int = None  # required
    target: AnimationChannelTarget = None  # required


@dataclass_json
@dataclass
class Animation(Property):
    name: Optional[str] = None
    channels: List[AnimationChannel] = field(default_factory=list)
    samplers: List[AnimationSampler] = field(default_factory=list)
