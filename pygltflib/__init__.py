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
import mimetypes
from pathlib import Path
from shutil import copyfile
from typing import Any, Dict, List
from typing import Callable, Optional, Tuple, TypeVar, Union
from urllib.parse import unquote
import struct
import warnings

from dataclasses_json import dataclass_json as dataclass_json
from dataclasses_json.core import _decode_dataclass
from dataclasses_json.core import _ExtendedEncoder as JsonEncoder

from .types import *

__version__ = "1.15.3"

"""
About the GLTF2 file format:

glTF uses a right-handed coordinate system, that is, the cross product of +X and +Y yields +Z. glTF defines +Y as up.
The front of a glTF asset faces +Z.
The units for all linear distances are meters.
All angles are in radians.
Positive rotation is counterclockwise.
"""


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
        """Get the binary blob associated with glb files if available

        Returns
            (bytes): binary data
        """
        return getattr(self, "_glb_data", None)

    def set_binary_blob(self, blob):
        setattr(self, "_glb_data", blob)

    def destroy_binary_blob(self):
        if hasattr(self, "_glb_data"):
            setattr(self, "_glb_data", None)

    def load_file_uri(self, uri):
        """
        Loads a file pointed to by a uri
        """
        path = getattr(self, "_path", Path())
        with open(Path(path, uri), "rb") as fb:
            data = fb.read()
        return data

    @staticmethod
    def decode_data_uri(uri, header=None):
        """
        Decodes the binary portion of a data uri.
        """
        data = uri.split(header or DATA_URI_HEADER)[1]
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

        if uri is None:  # assume loaded from glb binary file
            uri_format = BufferFormat.BINARYBLOB
            if len(self.buffers) > 1:
                warnings.warn(
                    "GLTF has multiple buffers but only one buffer binary blob, pygltflib might corrupt data."
                    "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues"
                )
        elif uri.startswith("data"):
            uri_format = BufferFormat.DATAURI
        elif Path(path, uri).is_file():
            uri_format = BufferFormat.BINFILE
        else:
            warnings.warn(
                "pygltf.GLTF.identify_buffer_format can not identify buffer."
                "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues"
            )
        return uri_format

    def get_data_from_buffer_uri(self, uri):
        """
        No matter how the buffer data is stored (the uri may be a long string, a file name or imply
        a binary blob), strip off any headers and do any conversions are return a universal binary
        blob for manipulation.
        """
        current_buffer_format = self.identify_uri(uri)

        if current_buffer_format == BufferFormat.BINFILE:
            data = self.load_file_uri(uri)
        elif current_buffer_format == BufferFormat.DATAURI:
            data = self.decode_data_uri(uri)
        elif current_buffer_format == BufferFormat.BINARYBLOB:
            data = self.binary_blob()
        else:
            return None

        return data

    # noinspection PyPep8Naming
    def remove_bufferView(self, buffer_view_id):
        """
        Remove a bufferView and update all the bufferView pointers in the GLTF object
        """
        bufferView = self.bufferViews.pop(buffer_view_id)

        def update_obj(title, obj):

            if not obj:
                print(f"{obj} empty")

            if not obj.bufferView:
                return

            if obj.bufferView == buffer_view_id:
                warnings.warn(
                    f"Removing bufferView {buffer_view_id} but "
                    f"{title}.bufferView still points to it. This may corrupt the GLTF."
                )
            if obj.bufferView >= buffer_view_id:
                obj.bufferView -= 1

        for i, accessor in enumerate(self.accessors):
            update_obj(f"gltf.accessors[{i}]", accessor)
            if accessor and accessor.sparse:
                update_obj(
                    f"gltf.accessors[{i}].sparse.indices", accessor.sparse.indices
                )
                update_obj(f"gltf.accessors[{i}].sparse.values", accessor.sparse.values)

        for i, obj in enumerate(self.images):
            update_obj(f"gltf.images[{i}]", obj)

        for i, cur_buffer_view in enumerate(self.bufferViews):
            if cur_buffer_view.byteOffset > bufferView.byteOffset:
                cur_buffer_view.byteOffset -= bufferView.byteLength

            if cur_buffer_view.byteStride is not None:
                warnings.warn(f"ByteStride is not None, may cause issues in GLTF")

        # self.convert_buffers(BufferFormat.BINARYBLOB)
        data: bytes = self.binary_blob()

        # Shrink the buffer
        data = (
            data[: bufferView.byteOffset]
            + data[bufferView.byteOffset + bufferView.byteLength :]
        )
        self.set_binary_blob(data)

        # Update meta
        self.buffers[0].byteLength = len(data)
        # self.convert_buffers(BufferFormat.DATAURI)

        return bufferView

    def export_datauri_as_image_file(
        self, data_uri, name, destination, override=False, index=0
    ):
        """convert data uri to image file
        If destination is full path and file name, use that.
        If destination is just a directory, use the name of the data_uri
        """
        header, encoded = data_uri.split(",", 1)
        mime = header.split(":")[1].split(";")[0]
        if name:  # use image.name
            file_name = name
        else:
            extension = mimetypes.guess_extension(mime)
            file_name = f"{index}{extension}"
        destination = Path(destination)
        if destination.is_dir():
            image_path = destination / unquote(file_name)
        else:  # assume filepath
            image_path = destination
        if image_path.is_file() and not override:
            warnings.warn(
                f"Unable to write image file, a file already exists at {image_path}"
            )
            return None
        data = base64.b64decode(encoded)

        with open(image_path, "wb") as image_file:
            image_file.write(data)
        return file_name

    def export_fileuri_as_image_file(self, file_uri, destination, override=False):
        """Export file uri as another image file (ie copy out of GLTF into own location)"""
        path = getattr(self, "_path", Path())
        image_path = Path(path / unquote(file_uri))
        if not image_path.exists():
            warnings.warn(f"Unable to find image {image_path} for export.")
            return None
        if image_path.is_file() and not override:
            warnings.warn(
                f"Unable to write image file, a file already exists at {image_path}"
            )
            return None

        copyfile(image_path, destination)
        return file_uri

    def convert_images(self, image_format, path=None):
        """
        GLTF files can store the image data in three different formats: In the buffers, as a data
        uri string and as external images files. This converts the images between the formats.

        image_format (ImageFormat.ENUM): Destination format to convert images
        path (str|Path): Path to the directory to use for loading or saving images
        override (bool): Override an image file if it already exists and is about to be replaced

        """
        if path is None:
            path = getattr(self, "_path", Path())
        else:
            path = Path(path)

        target_format = image_format

        for image_index, image in enumerate(self.images):

            if image.current_format == target_format:
                continue

            image_bytes = image_get_bytes(image, self, path)

            #############################
            # Clean up old representation
            #############################
            if image.current_format == ImageFormat.BUFFERVIEW:
                # self.convert_buffers(BufferFormat.BINARYBLOB)

                # data: bytes = self.binary_blob()
                # bufferView = self.bufferViews[image.bufferView]

                # # Shrink the buffer
                # data = (
                #     data[: bufferView.byteOffset]
                #     + data[bufferView.byteOffset + bufferView.byteLength :]
                # )
                # self.set_binary_blob(data)

                # # Update meta
                # self.buffers[0].byteLength = len(data)

                # Remove the bufferView
                idx = image.bufferView
                image.bufferView = None

                self.remove_bufferView(idx)

                # self.convert_buffers(BufferFormat.DATAURI)

            image.uri = None

            ########################
            # Convert to new format
            ########################
            if target_format == ImageFormat.DATAURI:  # convert to data uri
                encoded_string = str(base64.b64encode(image_bytes).decode("utf-8"))
                image.name = copy.copy(image.uri) if not image.name else image.name
                image.uri = f"data:{image.mimeType};base64,{encoded_string}"
            elif target_format == ImageFormat.BUFFERVIEW:
                # self.convert_buffers(BufferFormat.BINARYBLOB)

                # Add to buffer
                data = self.binary_blob()
                byte_offset, byte_len = len(data), len(image_bytes)
                pad_num = 4 - len(image_bytes) % 4
                data = data + image_bytes + ("0" * pad_num).encode()
                self.set_binary_blob(data)

                # Update meta
                self.buffers[0].byteLength = byte_offset + byte_len + pad_num

                # Create buffer view
                new_buffer_view = BufferView(
                    buffer=0, byteOffset=byte_offset, byteLength=byte_len
                )
                self.bufferViews.append(new_buffer_view)

                image.bufferView = len(self.bufferViews) - 1

                # Back to DATAURI format
                # self.convert_buffers(BufferFormat.DATAURI)

            elif target_format == ImageFormat.FILE:  # convert to images

                extension = mimetypes.guess_extension(image.mimeType)
                file_name = f"{image.name}{extension}"
                image_path = path / file_name

                with open(image_path, "wb") as f:
                    f.write(image_bytes)

                if file_name:  # replace data uri with pointer to file
                    image.uri = file_name

            else:
                raise Exception(f"{image_format=} incorrect argument")

    def convert_buffers(self, buffer_format, override=True, path=None):
        """
        GLTF files can store the buffer data in three different formats: As a binary blob ready for glb, as a data
        uri string and as external bin files. This converts the buffers between the formats.

        buffer_format (BufferFormat.ENUM)
        override (bool): Override a bin file if it already exists and is about to be replaced
        """

        print("CONVERT BINARY BLOB: ----> ", buffer_format.value)
        if path is not None:
            path = Path(path)
        else:
            path: Path = getattr(self, "_path", Path())

        for i, buffer in enumerate(self.buffers):
            current_buffer_format = self.identify_uri(buffer.uri)
            if current_buffer_format == buffer_format:  # already in the format
                continue
            if current_buffer_format == BufferFormat.BINFILE:
                warnings.warn(
                    f"Conversion will leave {buffer.uri} file orphaned since data is now in the GLTF object."
                )
            data = self.get_data_from_buffer_uri(buffer.uri)

            if not data:
                return

            self.destroy_binary_blob()  # free up any binary blob floating around

            if buffer_format == BufferFormat.BINARYBLOB:
                if len(self.buffers) > 1:
                    warnings.warn(
                        "pygltflib currently unable to convert multiple buffers to a single binary blob."
                        "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues"
                    )
                    return
                self.set_binary_blob(data)
                buffer.uri = None
            elif buffer_format == BufferFormat.DATAURI:
                # convert buffer to a data uri
                data = base64.b64encode(data).decode("utf-8")
                buffer.uri = f"{DATA_URI_HEADER}{data}"
            elif buffer_format == BufferFormat.BINFILE:
                filename = Path(f"{i}").with_suffix(".bin")
                binfile_path = path / filename
                if binfile_path.is_file() and not override:
                    warnings.warn(
                        f"Unable to write buffer file, a file already exists at {binfile_path}"
                    )
                    continue
                with open(binfile_path, "wb") as f:  # save bin file with the gltf file
                    f.write(data)
                buffer.uri = str(filename)

    def to_json(
        self,
        *,
        skipkeys: bool = False,
        ensure_ascii: bool = True,
        check_circular: bool = True,
        allow_nan: bool = True,
        indent: Optional[Union[int, str]] = None,
        separators: Tuple[str, str] = None,
        default: Callable = None,
        sort_keys: bool = False,
        **kw,
    ) -> str:
        """
        to_json and from_json from dataclasses_json
        courtesy https://github.com/lidatong/dataclasses-json
        """

        data = gltf_asdict(self)
        data = delete_empty_keys(data)
        return json.dumps(
            data,
            cls=JsonEncoder,
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            indent=indent,
            separators=separators,
            default=default,
            sort_keys=sort_keys,
            **kw,
        )

    @classmethod
    def from_json(
        cls: A,
        s: str,
        *,
        parse_float=None,
        parse_int=None,
        parse_constant=None,
        infer_missing=False,
        **kw,
    ) -> A:
        init_kwargs = json.loads(
            s,
            parse_float=parse_float,
            parse_int=parse_int,
            parse_constant=parse_constant,
            **kw,
        )
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

    def gltf_to_json(self, separators=None, indent="  ") -> str:
        return self.to_json(
            default=json_serial,
            indent=indent,
            allow_nan=False,
            skipkeys=True,
            separators=separators,
        )

    def save_json(self, fname):
        path = Path(fname)
        original_buffers = copy.deepcopy(self.buffers)
        for i, buffer in enumerate(self.buffers):
            if buffer.uri is None:  # save glb_data as bin file
                # update the buffer uri to point to our new local bin file
                glb_data = self.binary_blob()
                if glb_data:
                    buffer.uri = str(Path(path.stem).with_suffix(".bin"))
                    with open(
                        path.with_suffix(".bin"), "wb"
                    ) as f:  # save bin file with the gltf file
                        f.write(glb_data)
                else:
                    warnings.warn(f"buffer {i} is empty: {buffer}")

        with open(path, "w") as f:
            f.write(self.gltf_to_json())

        self.buffers = original_buffers  # restore buffers
        return True

    def buffers_to_binary_blob(self):
        """Flatten all buffers into a single buffer"""
        buffer_blob = bytearray()

        offset = 0
        path = getattr(self, "_path", Path())
        binary_blob: Optional[bytearray] = None

        for i, bufferView in enumerate(self.bufferViews):
            buffer = self.buffers[bufferView.buffer]
            if buffer.uri is None:  # assume loaded from glb binary file
                if binary_blob is None:
                    binary_blob = self.binary_blob()
                data = binary_blob
            elif buffer.uri.startswith("data"):
                data = self.decode_data_uri(buffer.uri)
            elif Path(path, buffer.uri).is_file():
                with open(Path(path, buffer.uri), "rb") as fb:
                    data = fb.read()
            else:
                warnings.warn(
                    f"Unable to save bufferView {buffer.uri[:20]} to glb, skipping. "
                    "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues"
                )
                continue
            byte_offset = (
                bufferView.byteOffset if bufferView.byteOffset is not None else 0
            )
            byte_length = bufferView.byteLength
            if byte_length % 4 != 0:  # pad each segment of binary blob
                byte_length += 4 - byte_length % 4

            buffer_blob += data[byte_offset : byte_offset + byte_length]

            bufferView.byteOffset = offset
            bufferView.byteLength = byte_length
            bufferView.buffer = 0
            offset += byte_length

        return buffer_blob

    def save_to_bytes(self):
        # setup
        original_buffer_views = copy.deepcopy(self.bufferViews)
        original_buffers = copy.deepcopy(self.buffers)
        new_buffer = Buffer()

        buffer_blob = self.buffers_to_binary_blob()
        new_buffer.byteLength = len(buffer_blob)

        self.buffers = [new_buffer]
        json_blob = self.gltf_to_json(separators=(",", ":"), indent=None).encode(
            "utf-8"
        )

        # pad each blob if needed
        if len(json_blob) % 4 != 0:
            json_blob += b"   "[0 : 4 - len(json_blob) % 4]

        version = struct.pack("<I", GLTF_VERSION)
        chunk_header_len = 8
        length = (
            len(MAGIC)
            + len(version)
            + 4
            + chunk_header_len * 2
            + len(json_blob)
            + len(buffer_blob)
        )

        self.bufferViews = original_buffer_views  # restore unpacked bufferViews
        self.buffers = original_buffers  # restore unpacked buffers

        # header is MAGIC, version, length
        # json chunk is json_blob length, JSON, json_blob
        # buffer chunk is length of buffer_blob, utf-8, buffer_blob
        return [
            MAGIC,
            version,
            struct.pack("<I", length),
            struct.pack("<I", len(json_blob)),
            bytes(JSON, "utf-8"),
            json_blob,
            struct.pack("<I", len(buffer_blob)),
            bytes(BIN, "utf-8"),
            buffer_blob,
        ]

    def save_binary(self, fname):
        with open(fname, "wb") as f:
            glb_structure = self.save_to_bytes()
            if not glb_structure:
                return False
            for data in glb_structure:
                f.write(data)
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
                    "and this will be saved to a .bin file next to the json file."
                )
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
    def load_from_bytes(cls, data):
        magic = struct.unpack("<BBBB", data[:4])
        version, length = struct.unpack("<II", data[4:12])
        if bytearray(magic) != MAGIC:
            raise IOError(
                "Unable to load binary gltf file. Header does not appear to be valid glb format."
            )
        if version > GLTF_MAX_VERSION:
            warnings.warn(
                f"pygltflib supports v{GLTF_MAX_VERSION} of the binary gltf format, "
                "this file is version {version}, "
                "it may not import correctly. "
                "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues"
            )
        index = 12
        i = 0
        obj = None
        while index < length:
            chunk_length = struct.unpack("<I", data[index : index + 4])[0]
            index += 4
            chunk_type = bytearray(
                struct.unpack("<BBBB", data[index : index + 4])
            ).decode()
            index += 4
            if chunk_type not in [JSON, BIN]:
                warnings.warn(
                    f"Ignoring chunk {i} with unknown type '{chunk_type}', probably glTF extensions. "
                    "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues"
                )
            elif chunk_type == JSON:
                raw_json = data[index : index + chunk_length].decode("utf-8")
                obj = cls.from_json(raw_json, infer_missing=True)
            else:
                obj.set_binary_blob(data[index : index + chunk_length])
            index += chunk_length
            i += 1
        return obj

    @classmethod
    def load_binary(cls, fname):
        with open(fname, "rb") as f:
            data = f.read()
        return cls.load_from_bytes(data)

    @classmethod
    def load_binary_from_file_object(cls, f):
        data = f.read()
        return cls.load_from_bytes(data)

    @classmethod
    def load(cls, fname):
        path = Path(fname)
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


def image_get_bytes(image: Image, gltf: GLTF2, path):

    if image.current_format == ImageFormat.FILE:
        image_path = Path(path / unquote(image.uri))
        if not image_path.exists():
            warnings.warn(f"Expected image file at {image_path} not found.")

        with open(image_path, "rb") as image_file:
            return image_file.read()

    elif image.current_format == ImageFormat.BUFFERVIEW:
        # gltf.convert_buffers(BufferFormat.BINARYBLOB)
        data = gltf.binary_blob()
        # gltf.convert_buffers(BufferFormat.DATAURI)

        bufferView = gltf.bufferViews[image.bufferView]
        image_data: bytes = data[
            bufferView.byteOffset : bufferView.byteOffset + bufferView.byteLength
        ]
        return image_data
    elif image.current_format == ImageFormat.DATAURI:
        return gltf.decode_data_uri(
            image.uri, image.uri[: image.uri.find("base64,") + 7]
        )
