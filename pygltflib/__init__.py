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
from enum import Enum
import json
from pathlib import Path
from typing import Any, Dict, List
from typing import Callable, Optional, Tuple, TypeVar, Union
import struct
import warnings

from dataclasses_json import dataclass_json as _dataclass_json
from dataclasses_json.core import _decode_dataclass

try:
    from dataclasses_json.core import _ExtendedEncoder as JsonEncoder
except ImportError:  # backwards compat with dataclasses_json 0.0.25 and less
    from dataclasses_json.core import _CollectionEncoder as JsonEncoder

__version__ = "1.12.0"

"""
About the GLTF2 file format:

glTF uses a right-handed coordinate system, that is, the cross product of +X and +Y yields +Z. glTF defines +Y as up.
The front of a glTF asset faces +Z.
The units for all linear distances are meters.
All angles are in radians.
Positive rotation is counterclockwise.
"""

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

BYTE = 5120  # 1
UNSIGNED_BYTE = 5121  # 1
SHORT = 5122  # 2
UNSIGNED_SHORT = 5123  # 2 unsigned short (2 bytes)
UNSIGNED_INT = 5125  # 4
FLOAT = 5126  # 4 single precision float (4 bytes)

# The bufferView target that the GPU buffer should be bound to.
ARRAY_BUFFER = 34962  # eg vertex data
ELEMENT_ARRAY_BUFFER = 34963  # eg index data

POSITION = "POSITION"
NORMAL = "NORMAL"
TANGENT = "TANGENT"
TEXCOORD_0 = "TEXCOORD_0"
TEXCOORD_1 = "TEXCOORD_1"
COLOR_0 = "COLOR_0"
JOINTS_0 = "JOINTS_0"
WEIGHTS_0 = "WEIGHTS_0"

PERSPECTIVE = "perspective"
ORTHOGRAPHIC = "orthographic"

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


# backwards and forwards compat dataclasses-json and dataclasses
class LetterCase(Enum):
    CAMEL = 'camelCase'
    KEBAB = 'kebab-case'
    SNAKE = 'snake_case'


class AlphaMode(Enum):
    BLEND = "BLEND"
    MASK = "MASK"
    OPAQUE = "OPAQUE"


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


def dataclass_json(cls, *args, **kwargs):
    try:
        dclass = _dataclass_json(cls, *args, **kwargs)  # hopefully a future version of dataclass-json > 0.2.8
    except TypeError:  # dataclass-json < 0.2.8
        try:
            dclass = _dataclass_json(cls)
        except TypeError:  # dataclass-json == 0.2.8
            warnings.warn("Please upgrade your version of dataclasses-json.")
            dclass = _dataclass_json(cls, decode_letter_case=LetterCase.CAMEL, encode_letter_case=LetterCase.CAMEL)
    return dclass


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
class Asset:
    generator: str = f"pygltflib@v{__version__}"
    copyright: str = None
    version: str = "2.0"


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
class Property:
    extensions: Dict[str, Any] = field(default_factory=dict)
    extras: Dict[str, Any] = field(default_factory=dict)


@dataclass_json
@dataclass
class Primitive(Property):
    attributes: Attributes = None
    indices: int = None
    mode: int = None
    material: int = None
    targets: List[Attributes] = field(default_factory=list)


@dataclass_json
@dataclass
class Mesh(Property):
    primitives: List[Primitive] = field(default_factory=list)
    weights: List[float] = field(default_factory=list)
    name: str = None


@dataclass_json
@dataclass
class SparseAccessor(Property):  # TODO is this the same as Accessor
    bufferView: int = None
    byteOffset: int = None
    componentType: int = None


@dataclass_json
@dataclass
class Sparse(Property):
    count: int = 0
    indices: SparseAccessor = None  # TODO this might be an Accessor but that would couple the classes
    values: SparseAccessor = None


@dataclass_json
@dataclass
class Accessor(Property):
    bufferView: int = None
    byteOffset: int = None
    componentType: int = None
    normalized: bool = None
    count: int = None
    type: str = None
    sparse: Sparse = None
    max: List[float] = field(default_factory=list)
    min: List[float] = field(default_factory=list)
    name: str = None


@dataclass_json
@dataclass
class BufferView(Property):
    buffer: int = None
    byteOffset: int = None
    byteLength: int = None
    byteStride: int = None
    target: int = None
    name: str = None


@dataclass_json
@dataclass
class Buffer(Property):
    uri: str = ""
    byteLength: int = None


@dataclass_json
@dataclass
class Perspective(Property):
    aspectRatio: float = None
    yfov: float = None
    zfar: float = None
    znear: float = None


@dataclass_json
@dataclass
class Orthographic(Property):
    xmag: float = None
    ymag: float = None
    zfar: float = None
    znear: float = None


@dataclass_json
@dataclass
class Camera(Property):
    perspective: Perspective = None
    orthographic: Orthographic = None
    type: str = None
    name: str = None


@dataclass_json
@dataclass
class MaterialTexture(Property):
    index: int = None
    texCoord: int = None


@dataclass_json
@dataclass
class PbrMetallicRoughness(Property):
    baseColorFactor: List[float] = field(default_factory=list)
    metallicFactor: float = None
    roughnessFactor: float = None
    baseColorTexture: MaterialTexture = None
    metallicRoughnessTexture: MaterialTexture = None


@dataclass_json
@dataclass
class Material(Property):
    pbrMetallicRoughness: PbrMetallicRoughness = None
    normalTexture: MaterialTexture = None
    occlusionTexture: MaterialTexture = None
    emissiveFactor: List[float] = field(default_factory=list)
    emissiveTexture: MaterialTexture = None
    alphaMode: str = None
    alphaCutoff: float = None
    doubleSided: bool = None
    name: str = None


@dataclass_json
@dataclass
class Sampler(Property):
    """
    Samplers are stored in the samplers array of the asset.
    Each sampler specifies filter and wrapping options corresponding to the GL types
    """
    input: int = None
    interpolation: str = None
    output: int = None
    magFilter: int = None
    minFilter: int = None
    wrapS: int = None  # repeat wrapping in S (U)
    wrapT: int = None  # repeat wrapping in T (V)


@dataclass_json
@dataclass
class Node(Property):
    mesh: int = None
    skin: int = None
    rotation: List[float] = field(default_factory=list)
    translation: List[float] = field(default_factory=list)
    scale: List[float] = field(default_factory=list)
    children: List[int] = field(default_factory=list)
    matrix: List[float] = field(default_factory=list)
    camera: int = None
    name: str = None


@dataclass_json
@dataclass
class Skin(Property):
    inverseBindMatrices: int = None
    skeleton: int = None
    joints: List[int] = field(default_factory=list)
    name: str = None


@dataclass_json
@dataclass
class Scene(Property):
    name: str = ""
    nodes: List[int] = field(default_factory=list)


@dataclass_json
@dataclass
class Texture(Property):
    sampler: int = None
    source: int = None


@dataclass_json
@dataclass
class Image(Property):
    uri: str = None
    mimeType: str = None
    bufferView: int = None


@dataclass_json
@dataclass
class Target(Property):
    node: int = None
    path: str = None


@dataclass_json
@dataclass
class Channel(Property):
    sampler: int = None
    target: Target = None


@dataclass_json
@dataclass
class Animation(Property):
    name: str = None
    channels: List[Channel] = field(default_factory=list)
    samplers: List[Sampler] = field(default_factory=list)


@dataclass
class GLTF2(Property):
    accessors: List[Accessor] = field(default_factory=list)
    animations: List[Animation] = field(default_factory=list)
    asset: Asset = field(default_factory=Asset)
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

    def convert_buffers(self, buffer_format, override=False):
        """
        GLTF files can store the buffer data in three different formats: As a binary blob ready for glb, as a data
        uri string and as external bin files. This converts the buffers between the formats.

        buffer_format (BufferFormat.ENUM)
        override (bool): Override a bin file if it already exists and is about to be replaced
        """
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
                binfile_path = getattr(self, "_path", Path()) / filename
                buffer.uri = str(filename)
                if binfile_path.is_file() and not override:
                    warnings.warn(f"Unable to write buffer file, a file already exists at {binfile_path}")
                    continue
                with open(binfile_path, "wb") as f:  # save bin file with the gltf file
                    f.write(data)

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
        if not obj:
            return obj

        # in a GLB there is only one buffer. It has no uri and it is currently held in self._glb_data
        # the views for breaking up glb_data are in bufferViews.
        # TODO: Give option to put data into buffers
        """
        new_buffers = []
        for i, bufferView in enumerate(obj.bufferViews):
            bufferView.byteOffset
            bufferView.buffer = i
            bufferView.byteOffset = 0
            new_buffer = Buffer()
        """

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
