"""
pygltflib : A Python library for reading, writing and handling GLTF files.


Copyright (c) 2018, 2019 Luke Miller

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
import base64
import copy
from dataclasses import (
    _is_dataclass_instance,
    dataclass,
    field,
    fields,
)
from datetime import date, datetime
from deprecated import deprecated
from enum import Enum
import json
from pathlib import Path
from typing import Any, Dict, List
from typing import Callable, Optional, Tuple, TypeVar, Union
import struct
import warnings

import mimetypes
from dataclasses_json import dataclass_json as dataclass_json
from dataclasses_json.core import _decode_dataclass
from dataclasses_json.core import _ExtendedEncoder as JsonEncoder

__version__ = "1.13.3"

"""
About the GLTF2 file format:

glTF uses a right-handed coordinate system, that is, the cross product of +X and +Y yields +Z. glTF defines +Y as up.
The front of a glTF asset faces +Z.
The units for all linear distances are meters.
All angles are in radians.
Positive rotation is counterclockwise.
"""

A = TypeVar('A')

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

MESH_PRIMITIVE_MODES = [POINTS, LINES, LINE_LOOP, LINE_STRIP, TRIANGLES, TRIANGLE_STRIP, TRIANGLE_FAN]

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

IMAGEJPEG = 'image/jpeg'
IMAGEPNG = "image/png"

IMAGE_MIMETYPES = [IMAGEJPEG, IMAGEPNG]

NEAREST = 9728
LINEAR = 9729
NEAREST_MIPMAP_NEAREST = 9984
LINEAR_MIPMAP_NEAREST = 9985
NEAREST_MIPMAP_LINEAR = 9986
LINEAR_MIPMAP_LINEAR = 9987

MAGNIFICATION_FILTERS = [NEAREST, LINEAR]
MINIFICATION_FILTERS = [NEAREST, LINEAR, NEAREST_MIPMAP_NEAREST, LINEAR_MIPMAP_NEAREST, NEAREST_MIPMAP_LINEAR,
                        LINEAR_MIPMAP_LINEAR]

PERSPECTIVE = "perspective"
ORTHOGRAPHIC = "orthographic"

CAMERA_TYPES = [PERSPECTIVE, ORTHOGRAPHIC]

BLEND = "BLEND"
MASK = "MASK"
OPAQUE = "OPAQUE"

MATERIAL_ALPHAMODES = [OPAQUE, MASK, BLEND]


@deprecated("Please use the pygltflib.BLEND, pygltflib.MASK, pygltflib.OPAQUE constants directly.")
class AlphaMode(Enum):
    BLEND = "BLEND"
    MASK = "MASK"
    OPAQUE = "OPAQUE"


JSON = "JSON"
BIN = "BIN\x00"
MAGIC = b'glTF'
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
    CAMEL = 'camelCase'
    KEBAB = 'kebab-case'
    SNAKE = 'snake_case'


def delete_empty_keys(dictionary):
    """
    Delete keys with the value ``None`` in a dictionary, recursively.

    This alters the input so you may wish to ``copy`` the dict first.

    Courtesy Chris Morgan and modified from:
    https://stackoverflow.com/questions/4255400/exclude-empty-null-values-from-json-serialization
    """
    for key, value in list(dictionary.items()):
        if value is None or (hasattr(value, '__iter__') and len(value) == 0):
            del dictionary[key]
        elif isinstance(value, dict):
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
    elif isinstance(obj, tuple) and hasattr(obj, '_fields'):
        return type(obj)(*[_asdict_inner(v, dict_factory) for v in obj])
    elif isinstance(obj, (list, tuple)):

        return type(obj)(_asdict_inner(v, dict_factory) for v in obj)
    elif isinstance(obj, dict):
        return type(obj)((_asdict_inner(k, dict_factory),
                          _asdict_inner(v, dict_factory))
                         for k, v in obj.items())
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
    def __init__(self,
                 POSITION=None,
                 NORMAL=None,
                 TANGENT=None,
                 TEXCOORD_0=None,
                 TEXCOORD_1=None,
                 COLOR_0: int = None,
                 JOINTS_0: int = None,
                 WEIGHTS_0=None, *args, **kwargs):
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
        return self.__class__.__qualname__ + f'(' + ', '.join([f"{f}={v}" for f, v in self.__dict__.items()]) + ')'

    def to_json(self, *args, **kwargs):
        # Attributes objects can have custom attrs, so use our own json conversion methods.
        data = copy.deepcopy(self.__dict__)
        return json.dumps(data)

    @staticmethod
    def from_json():
        warnings.warn("To allow custom attributes on Attributes, we don't use dataclasses-json on this class."
                      "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues")


@dataclass_json
@dataclass
class Primitive(Property):
    attributes: Attributes = Attributes()  # required
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


@deprecated("Please use AccessorSparseIndices and AccessorSparseValues instead")
@dataclass_json
@dataclass
class SparseAccessor(Property):
    bufferView: int = None  # required
    byteOffset: Optional[int] = 0
    componentType: int = None  # required


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
    uri: Optional[str] = ""
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


@deprecated("Please use TextureInfo instead.")
@dataclass_json
@dataclass
class MaterialTexture(Property):
    index: int = None  # required
    texCoord: Optional[int] = 0


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
    baseColorFactor: Optional[List[float]] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    metallicFactor: Optional[float] = 1.0
    roughnessFactor: Optional[float] = 1.0
    baseColorTexture: Optional[TextureInfo] = None
    metallicRoughnessTexture: Optional[MaterialTexture] = None


@dataclass_json
@dataclass
class Material(Property):
    pbrMetallicRoughness: Optional[PbrMetallicRoughness] = None
    normalTexture: Optional[NormalMaterialTexture] = None
    occlusionTexture: Optional[OcclusionTextureInfo] = None
    emissiveFactor: Optional[List[float]] = field(default_factory=lambda: [0.0, 0.0, 0.0])
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
    rotation: Optional[List[float]] = field(default_factory=lambda: [0.0, 0.0, 0.0, 1.0])
    translation: Optional[List[float]] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    scale: Optional[List[float]] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    children: Optional[List[int]] = field(default_factory=list)
    matrix: Optional[List[float]] = field(
        default_factory=lambda: [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0], )
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


@dataclass
class GLTF2(Property):
    accessors: List[Accessor] = field(default_factory=list)
    animations: List[Animation] = field(default_factory=list)
    asset: Asset = field(default_factory=Asset)  # required
    bufferViews: List[BufferView] = field(default_factory=list)
    buffers: List[Buffer] = field(default_factory=list)
    cameras: List[Camera] = field(default_factory=list)
    extensionsUsed: List[str] = field(default_factory=list)
    extensionsRequired: List[str] = field(default_factory=list)
    images: List[Image] = field(default_factory=list)
    materials: List[Material] = field(default_factory=list)
    meshes: List[Mesh] = field(default_factory=list)
    nodes: List[Node] = field(default_factory=list)
    samplers: List[Sampler] = field(default_factory=list)
    scene: int = None
    scenes: List[Scene] = field(default_factory=list)
    skins: List[Skin] = field(default_factory=list)
    textures: List[Texture] = field(default_factory=list)
#    _glb_data: Any = None
#    _path: Any = None

    def binary_blob(self):
        """ Get the binary blob associated with glb files if available

            Returns
                (bytes): binary data
        """
        return getattr(self, "_glb_data", None)

    def destroy_binary_blob(self):
        if hasattr(self, "_glb_data"):
            self._glb_data = None

    def load_file_uri(self, uri):
        """
        Loads a file pointed to by a uri
        """
        path = getattr(self, "_path", Path())
        with open(Path(path, uri), 'rb') as fb:
            data = fb.read()
        return data

    @staticmethod
    def decode_data_uri(uri):
        """
        Decodes the binary portion of a data uri.
        """
        data = uri.split(DATA_URI_HEADER)[1]
        data = base64.decodebytes(bytes(data, "utf8"))
        return data

    def identify_uri(self, uri):
        """
        Identify the format of the requested buffer. File, data or binary blob.

        Returns
            buffer_type (str)
        """
        path = getattr(self, "_path", Path())
        uri_format = None

        if uri == '':  # assume loaded from glb binary file
            uri_format = BufferFormat.BINARYBLOB
            if len(self.buffers) > 1:
                warnings.warn("GLTF has multiple buffers but only one buffer binary blob, pygltflib might corrupt data."
                              "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues")
        elif uri.startswith("data"):
            uri_format = BufferFormat.DATAURI
        elif Path(path, uri).is_file():
            uri_format = BufferFormat.BINFILE
        else:
            warnings.warn("pygltf.GLTF.identify_buffer_format can not identify buffer."
                          "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues")
        return uri_format

    def remove_bufferView(self, buffer_view_id):
        """
        Remove a bufferView and update all the bufferView pointers in the GLTF object
        """
        bufferView = self.bufferViews.pop(buffer_view_id)
        for objs in [self.accessors, self.images, [accessor.sparse for accessor in self.accessors]]:
            for obj in objs:
                if obj.bufferView >= buffer_view_id:
                    obj.bufferView -= 1
        return bufferView

    def export_image_to_file(self, image_index, override=False):
        image = self.images[image_index]
        path: Path = getattr(self, "_path", Path())
        if image.uri and not image.uri.startswith('data:'):
            # already in file format
            if not (path / image.uri).exists():
                warnings.warn(f"Image {image_index} is already stored in a file {path / image.uri} but file"
                              f"does not appear to exist.")
            return None
        elif image.bufferView:
            # TODO: remove bufferView from GLTF when create images or datauris from buffer data
            bufferView = self.bufferViews[image.bufferView]
            buffer = self.buffers[bufferView.buffer]
            if buffer.uri:  # buffer is stored as a data uri or an uri pointing to a non-existent file
                warnings.warn("pygltflib currently unable to convert image stored buffers to image file."
                              "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues")
            else:  # buffer is stored in the binary blob
                warnings.warn(
                    "pygltflib currently does not remove image data from the buffer when converting to files."
                    "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues")
                data = self.binary_blob()
                extension = mimetypes.guess_extension(image.mimeType)
                file_name = f"{image_index}{extension}"
                with open(file_name, "wb") as f:
                    f.write(data[bufferView.byteOffset:bufferView.byteOffset + bufferView.byteLength])
                return file_name
            return None
        elif image.uri.startswith('data:'):
            #  convert data uri to image file
            header, encoded = image.uri.split(",", 1)
            mime = header.split(":")[1].split(";")[0]
            if image.name:  # use image.name
                file_name = image.name
            else:
                extension = mimetypes.guess_extension(mime)
                file_name = f"{image_index}{extension}"
            image_path = path / file_name
            if image_path.is_file() and not override:
                warnings.warn(f"Unable to write image file, a file already exists at {image_path}")
                return None
            data = base64.b64decode(encoded)

            with open(image_path, "wb") as image_file:
                image_file.write(data)
            return file_name

    def convert_images(self, image_format, override=False):
        """
        GLTF files can store the image data in three different formats: In the buffers, as a data
        uri string and as external images files. This converts the images between the formats.

        image_format (ImageFormat.ENUM)
        override (bool): Override an image file if it already exists and is about to be replaced

        """
        path: Path = getattr(self, "_path", Path())
        for image_index, image in enumerate(self.images):
            if image_format == ImageFormat.DATAURI:  # convert to data uri
                # load an image file or pull from the buffer
                if image.uri:  # either already in a datauri format, or in a file
                    if not image.uri.startswith('data:'):  # not in data format, so assume a file name
                        # data is stored in a file, so load into data uri
                        image_path = path / image.uri
                        if not image_path.exists():
                            warnings.warn(f"Expected image file at {image_path} not found.")
                            continue
                        mime: str
                        mime, _ = mimetypes.guess_type(image_path)

                        with open(image_path, "rb") as image_file:
                            encoded_string = str(base64.b64encode(image_file.read()).decode('utf-8'))
                            image.name = copy.copy(image.uri) if not image.name else image.name
                            image.uri = f'data:{mime};base64,{encoded_string}'
                elif image.bufferView:
                    # TODO: remove bufferView from GLTF when create images or datauris from buffer data
                    warnings.warn("pygltflib currently does not remove image data from the buffer when converting to data uri."
                                  "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues")
                    data = self.binary_blob()
                    bufferView = self.bufferViews[image.bufferView]
                    buffer = self.buffers[bufferView.buffer]
                    image_data = data[bufferView.byteOffset:bufferView.byteOffset + bufferView.byteLength]
                    encoded_string = str(base64.b64encode(image_data).decode('utf-8'))
                    image.uri = f'data:{image.mimeType};base64,{encoded_string}'
                else:
                    warnings.warn(f"Image {image_index} appears to have neither a uri nor a buffer view.")

            elif image_format == ImageFormat.BUFFERVIEW:  # convert to buffer
                #  load image data into the buffer and and add a bufferView
                if image.bufferView:
                    # already in bufferview format
                    continue
                warnings.warn("pygltflib currently unable to add image data to buffers."
                              "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues")
                continue
            elif image_format == ImageFormat.FILE:   # convert to images
                file_name = self.export_image_to_file(image_index, override)
                if file_name: # replace data uri with pointer to file
                    image.uri = file_name


    def convert_buffers(self, buffer_format, override=False):
        """
        GLTF files can store the buffer data in three different formats: As a binary blob ready for glb, as a data
        uri string and as external bin files. This converts the buffers between the formats.

        buffer_format (BufferFormat.ENUM)
        override (bool): Override a bin file if it already exists and is about to be replaced
        """
        path: Path = getattr(self, "_path", Path())

        for i, buffer in enumerate(self.buffers):
            current_buffer_format = self.identify_uri(buffer.uri)
            if current_buffer_format == buffer_format:  # already in the format
                continue

            if current_buffer_format == BufferFormat.BINFILE:
                warnings.warn(f"Conversion will leave {buffer.uri} file orphaned since data is now in the GLTF object.")
                data = self.load_file_uri(buffer.uri)
            elif current_buffer_format == BufferFormat.DATAURI:
                data = self.decode_data_uri(buffer.uri)
            elif current_buffer_format == BufferFormat.BINARYBLOB:
                data = self.binary_blob()
            else:
                return

            self.destroy_binary_blob()  # free up any binary blob floating around

            if buffer_format == BufferFormat.BINARYBLOB:
                if len(self.buffers) > 1:
                    warnings.warn("pygltflib currently unable to convert multiple buffers to a single binary blob."
                                  "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues")
                    return
                self._glb_data = data
                buffer.uri = ''
            elif buffer_format == BufferFormat.DATAURI:
                # convert buffer
                data = base64.b64encode(data).decode('utf-8')
                buffer.uri = f'{DATA_URI_HEADER}{data}'
            elif buffer_format == BufferFormat.BINFILE:
                filename = Path(f"{i}").with_suffix(".bin")
                binfile_path = path / filename
                if binfile_path.is_file() and not override:
                    warnings.warn(f"Unable to write buffer file, a file already exists at {binfile_path}")
                    continue
                with open(binfile_path, "wb") as f:  # save bin file with the gltf file
                    f.write(data)
                buffer.uri = str(filename)

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
        """
        to_json and from_json from dataclasses_json
        courtesy https://github.com/lidatong/dataclasses-json
        """

        data = gltf_asdict(self)
        data = delete_empty_keys(data)
        return json.dumps(data,
                          cls=JsonEncoder,
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
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            result = _decode_dataclass(cls, init_kwargs, infer_missing)  # type: GLTF2
        for mesh in result.meshes:
            for primitive in mesh.primitives:
                raw_attributes = primitive.attributes
                if raw_attributes:
                    attributes = Attributes(**raw_attributes)
                    primitive.attributes = attributes
        return result

    def gltf_to_json(self) -> str:
        return self.to_json(default=json_serial, indent="  ", allow_nan=False, skipkeys=True)

    def save_json(self, fname):
        path = Path(fname)
        original_buffers = copy.deepcopy(self.buffers)
        for i, buffer in enumerate(self.buffers):
            if buffer.uri == '':  # save glb_data as bin file
                # update the buffer uri to point to our new local bin file
                glb_data = self.binary_blob()
                if glb_data:
                    buffer.uri = str(Path(path.stem).with_suffix(".bin"))
                    with open(path.with_suffix(".bin"), "wb") as f:  # save bin file with the gltf file
                        f.write(glb_data)
                else:
                    warnings.warn(f"buffer {i} is empty: {buffer}")

        with open(path, "w") as f:
            f.write(self.gltf_to_json())

        self.buffers = original_buffers  # restore buffers
        return True

    def save_binary(self, fname):
        with open(fname, 'wb') as f:
            # setup

            buffer_blob = b''
            original_buffer_views = copy.deepcopy(self.bufferViews)
            original_buffers = copy.deepcopy(self.buffers)

            offset = 0
            new_buffer = Buffer()
            path = getattr(self, "_path", Path())
            for i, bufferView in enumerate(self.bufferViews):
                buffer = self.buffers[bufferView.buffer]
                if buffer.uri == '':  # assume loaded from glb binary file
                    data = self.binary_blob()
                elif buffer.uri.startswith("data"):
                    warnings.warn(f"Unable to save data uri bufferView {buffer.uri[:20]} to glb, "
                                  "please save in gltf format instead or use the convert_buffers method first."
                                  "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues")
                    return False
                elif Path(path, buffer.uri).is_file():
                    with open(Path(path, buffer.uri), 'rb') as fb:
                        data = fb.read()
                else:
                    warnings.warn(f"Unable to save bufferView {buffer.uri[:20]} to glb, skipping. "
                                  "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues")
                    continue
                byte_offset = bufferView.byteOffset if bufferView.byteOffset is not None else 0
                byte_length = bufferView.byteLength
                if byte_length % 4 != 0:  # pad each segment of binary blob
                    byte_length += 4 - byte_length % 4

                buffer_blob += data[byte_offset:byte_offset + byte_length]

                bufferView.byteOffset = offset
                bufferView.byteLength = byte_length
                bufferView.buffer = 0
                offset += byte_length

            new_buffer.byteLength = len(buffer_blob)
            self.buffers = [new_buffer]

            json_blob = self.gltf_to_json().encode("utf-8")

            # pad each blob if needed
            if len(json_blob) % 4 != 0:
                json_blob += b'   '[0:4 - len(json_blob) % 4]

            version = struct.pack('<I', GLTF_VERSION)
            chunk_header_len = 8
            length = len(MAGIC) + len(version) + 4 + chunk_header_len * 2 + len(json_blob) + len(buffer_blob)
            self.bufferViews = original_buffer_views  # restore unpacked bufferViews
            self.buffers = original_buffers  # restore unpacked buffers

            # header
            f.write(MAGIC)
            f.write(version)
            f.write(struct.pack('<I', length))

            # json chunk
            f.write(struct.pack('<I', len(json_blob)))
            f.write(bytes(JSON, 'utf-8'))
            f.write(json_blob)

            # buffer chunk
            f.write(struct.pack('<I', len(buffer_blob)))
            f.write(bytes(BIN, 'utf-8'))
            f.write(buffer_blob)

        return True

    def save(self, fname, asset=Asset()):
        self.asset = asset
        self._path = Path(fname).parent
        self._name = Path(fname).name
        ext = Path(fname).suffix
        if ext.lower() in [".glb"]:
            return self.save_binary(fname)
        else:
            if getattr(self, "_glb_data", None):
                warnings.warn(
                    f"This file ({fname}) contains a binary blob loaded from a .glb file, "
                    "and this will be saved to a .bin file next to the json file.")
            return self.save_json(fname)

    @classmethod
    def gltf_from_json(cls, json_data):
        return cls.from_json(json_data, infer_missing=True)

    @classmethod
    def load_json(cls, fname):
        with open(fname, "r") as f:
            obj = cls.gltf_from_json(f.read())
        return obj

    @classmethod
    def load_binary(cls, fname):
        with open(fname, "rb") as f:
            data = f.read()
        magic = struct.unpack("<BBBB", data[:4])
        version, length = struct.unpack("<II", data[4:12])
        if bytearray(magic) != MAGIC:
            raise IOError("Unable to load binary gltf file. Header does not appear to be valid glb format.")
        if version > GLTF_MAX_VERSION:
            warnings.warn(f"pygltflib supports v{GLTF_MAX_VERSION} of the binary gltf format, "
                          "this file is version {version}, "
                          "it may not import correctly. "
                          "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues")
        index = 12
        i = 0
        obj = None
        while index < length:
            chunk_length = struct.unpack("<I", data[index:index + 4])[0]
            index += 4
            chunk_type = bytearray(struct.unpack("<BBBB", data[index:index + 4])).decode()
            index += 4
            if chunk_type not in [JSON, BIN]:
                warnings.warn(f"Ignoring chunk {i} with unknown type '{chunk_type}', probably glTF extensions. "
                              "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues")
            elif chunk_type == JSON:
                raw_json = data[index:index + chunk_length].decode("utf-8")
                obj = cls.from_json(raw_json, infer_missing=True)
            else:
                obj._glb_data = data[index:index + chunk_length]
            index += chunk_length
            i += 1
        return obj

    @classmethod
    def load(cls, fname):
        path = Path(fname)
        if not path.is_file():
            print("ERROR: File not found", fname)
            return None
        ext = path.suffix
        if ext.lower() in [".bin", ".glb"]:
            obj = cls.load_binary(fname)
        else:
            obj = cls.load_json(fname)
        obj._path = path.parent
        obj._name = path.name
        return obj


def main():
    import doctest
    doctest.testfile("../README.md")


if __name__ == "__main__":
    main()
