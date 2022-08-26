"""
To use:
link the glTF-Sample-Models into this directory eg:
ln -s /home/<user>/projects/pygltflib/glTF-Sample-Models .

To run:
pytest test_pygltflib.py

To see with regular print statements:
pytest -s test_pygltflib.py

A single test class:
pytest test_pygltflib.py::TextValidator
"""

import base64
from dataclasses import dataclass
import logging
import os
from pathlib import Path
import shutil
import tempfile

import pytest

import pygltflib
from pygltflib import (
    ARRAY_BUFFER,
    ELEMENT_ARRAY_BUFFER,
    FLOAT,
    SCALAR,
    UNSIGNED_BYTE,
    UNSIGNED_INT,
    UNSIGNED_SHORT,
    VEC3,
    Accessor,
    AccessorSparseIndices,
    Attributes,
    Buffer,
    BufferFormat,
    BufferView,
    GLTF2,
    Image,
    ImageFormat,
    Mesh,
    Material,
    Node,
    PbrMetallicRoughness,
    Primitive,
    Property,
    Scene,
    Sparse,
)
from pygltflib.utils import (
    add_primitive,
    add_indexed_geometry,
)
from pygltflib.validator import (
    validate,
    InvalidAcccessorComponentTypeException,
    InvalidBufferViewTarget,
)


PATH = "glTF-Sample-Models"
CPATH = "gltf-Sample-Copyrighted"
CPATH = "gltf-Sample-Copyrighted"

print(f"Testing version {pygltflib.__version__}")

KHRONOS_AVAILABLE = Path(PATH).exists()
COPYRIGHTED_AVAILABLE = Path(CPATH).exists()


class TestValidator:
    def setup_method(self, _test_method):
        path = Path(PATH)
        if not path.exists():
            raise NotADirectoryError("Unable to find Khronos sample files at ", path.absolute())

    def test_Triangle(self):
        fname = Path(PATH).joinpath("2.0/Triangle/glTF/Triangle.gltf")
        gltf = GLTF2().load(fname)
        assert gltf.asset.version == "2.0"

    def test_Triangles(self):
        fname = Path(PATH).joinpath("2.0/SimpleMeshes/glTF/SimpleMeshes.gltf")
        gltf = GLTF2().load(fname)
        assert gltf.asset.version == "2.0"
        assert gltf.bufferViews[0].buffer == gltf.bufferViews[1].buffer

    def test_BoxVertexColors(self):
        fname = Path(PATH).joinpath("2.0/BoxVertexColors/glTF-Embedded/BoxVertexColors.gltf")
        gltf = GLTF2().load(fname)
        assert gltf.asset.version == "2.0"
        assert gltf.accessors[0].bufferView == 0
        assert gltf.accessors[4].bufferView == 4


class TestIO:
    def test_load_glb(self):
        r = Path(PATH) / "2.0/Box/glTF-Binary/Box.glb"
        reference = GLTF2().load(r)
        assert len(reference.buffers) == 1
        assert type(reference) == GLTF2

    def test_load_glb_static(self):
        r = Path(PATH) / "2.0/Box/glTF-Binary/Box.glb"
        reference = GLTF2.load(r)
        assert len(reference.buffers) == 1
        assert type(reference) == GLTF2

    def test_load_glb_class(self):
        r = Path(PATH) / "2.0/Box/glTF-Binary/Box.glb"

        class GLTFGoose(GLTF2):
            pass

        reference = GLTFGoose.load(r)
        assert len(reference.buffers) == 1
#        assert type(reference) == GLTFGoose

    def test_save_glb2glb(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            r = Path(PATH) / "2.0/Box/glTF-Binary/Box.glb"
            reference = GLTF2().load(r)

            f = Path(PATH) / "2.0/Box/glTF-Binary/Box.glb"
            glb1 = GLTF2().load(r)

            t = Path(tmpdirname) / "glb2glb.glb"
            glb1.save(t)
            glb2 = GLTF2().load(t)

            reference.convert_buffers(BufferFormat.DATAURI)
            glb2.convert_buffers(BufferFormat.DATAURI)

            #assert glb2.binary_blob() == reference.binary_blob() == None

            #assert glb2.buffers == reference.buffers

        # assert glb2.binary_blob() == reference.binary_blob()


class TestOutput:
    def test_box(self):
        """ Load a GLB saved by us from the original GLTF"""
        input_fname = Path("glTF-Sample-Models/2.0/Box/glTF/Box.gltf")
        input_gltf = GLTF2().load(input_fname)
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_fname = Path(tmpdirname) / "Box.glb"
            input_gltf.save_binary(output_fname)

            # load from glb
            gltf = GLTF2().load(output_fname)
        assert gltf.asset.version == "2.0"
        assert len(gltf.bufferViews) == 2
        assert gltf.accessors[2].bufferView == 1

    def test_animated_triangle(self):
        """ Load a GLB saved by us from the original GLTF"""
        input_fname = Path("glTF-Sample-Models/2.0/AnimatedTriangle/glTF/AnimatedTriangle.gltf")
        input_gltf = GLTF2().load(input_fname)
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_fname = Path(tmpdirname) / "AnimatedTriangle.glb"
            input_gltf.save_binary(output_fname)

            # load from glb
            gltf = GLTF2().load(output_fname)

        assert gltf.asset.version == "2.0"
        assert [(i, x.bufferView) for i, x in enumerate(gltf.accessors)] == [(0, 0), (1, 1), (2, 2), (3, 2)]

    def test_avocado(self):
        """ Load a GLB saved by us from the original GLTF"""
        input_fname = Path(PATH).joinpath("2.0/Avocado/glTF/Avocado.gltf")
        input_gltf = GLTF2().load(input_fname)

        with tempfile.TemporaryDirectory() as tmpdirname:
            output_fname = Path(tmpdirname) / "Avocado.glb"
            input_gltf.save_binary(output_fname)

            # load from glb
            our_glb = GLTF2().load(output_fname)

            # load reference glb

            ref_fname = Path(PATH).joinpath("2.0/Avocado/glTF-Binary/Avocado.glb")
            ref_glb = GLTF2().load(ref_fname)

        assert our_glb.asset.version == "2.0"
        # assert ref_glb.bufferViews == our_glb.bufferViews


class TestConversion:
    def setup_method(self, _test_method):
        path = Path(PATH)
        if not path.exists():
            raise NotADirectoryError("Unable to find Khronos sample files at ", path.absolute())

    def test_load_glb(self):
        f = "BrainStem"
        fname = Path(PATH).joinpath(f"2.0/{f}/glTF-Binary/{f}.glb")
        glb = GLTF2().load(fname)
        print("data", glb._glb_data[:100])
        fnamejson = Path(PATH).joinpath(f"2.0/{f}/glTF/{f}.gltf")
        gltf = GLTF2().load(fnamejson)
        gltf.save("test.glb")
        glbed = GLTF2().load("test.glb")
        print("data", glbed._glb_data[:100])
        assert len(glb.scenes) > 0

    def test_loadGLBsaveGLB(self):
        f = "BrainStem"
        fname = Path(PATH).joinpath(f"2.0/{f}/glTF-Binary/{f}.glb")
        glb = GLTF2().load(fname)
        return

        with tempfile.TemporaryDirectory() as tmpdirname:
            t = Path(tmpdirname) / "test.glb"
            glb.save(t)
            glbed = GLTF2().load(t)

        assert glbed._glb_data == glb._glb_data

    def test_loadGLBsaveGLTF(self):
        f = "BrainStem"
        fname = Path(PATH).joinpath(f"2.0/{f}/glTF-Binary/{f}.glb")
        glb = GLTF2().load(fname)

        fnamejson = Path(PATH).joinpath(f"2.0/{f}/glTF/{f}.gltf")
        gltf = GLTF2().load(fnamejson)

        glb.save("test.gltf")
        gltfed = GLTF2().load("test.gltf")
        assert gltfed.buffers[0].uri == "test.bin"
        assert gltfed.bufferViews == gltf.bufferViews


class TestUtils:
    def test_add_primitive(self):
        add_primitive(None)
        indices = [(0, 1, 2)]
        vertices = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
        gltf = GLTF2()
        scene = Scene()
        scene.nodes.append(0)
        gltf.scene = 0
        gltf.scenes.append(scene)

        add_indexed_geometry(gltf, indices, vertices)
        gltf.save("test_primitive.gltf")
        pass


class TestBufferConversions:
    def test_identify_datauri(self):
        gltf = GLTF2()
        uri = "data:application/octet-stream;base64,AAABAAIAAAAAAAAAAAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAACAPwAAAAA="
        buffer_format = gltf.identify_uri(uri)
        assert buffer_format == BufferFormat.DATAURI

    def test_identify_binfile(self):
        gltf = GLTF2()
        uri = "test.bin"
        buffer_format = gltf.identify_uri(uri)
        assert buffer_format == BufferFormat.BINFILE

    def test_identify_binfile(self):
        gltf = GLTF2()
        uri = b'\x00\x00\x01\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x00'
        uri = ''  # empty uri means data blob
        buffer_format = gltf.identify_uri(uri)
        assert buffer_format == BufferFormat.BINARYBLOB

    def test_buffer_conversions(self):
        buffer = Buffer()
        buffer.uri = data = "data:application/octet-stream;base64,AAABAAIAAAAAAAAAAAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAACAPwAAAAA="
        buffer.byteLength = 44
        gltf = GLTF2()
        gltf.buffers.append(buffer)

        with tempfile.TemporaryDirectory() as tmpdirname:
            gltf._path = tmpdirname
            assert gltf.buffers[0].uri == data

            gltf.convert_buffers(BufferFormat.BINARYBLOB)

            assert gltf.buffers[0].uri == ""
            assert len(gltf.binary_blob()) > 0
            print("binary blob success", gltf.binary_blob())

            gltf.convert_buffers(BufferFormat.BINFILE)

            assert gltf.buffers[0].uri == "0.bin"
            assert not gltf.binary_blob()

            print("binary bin file success")

            gltf.convert_buffers(BufferFormat.DATAURI)
            print("final test")

            assert gltf.buffers[0].uri == data

    def test_buffer_conversions_realworld(self):
        fembedded = Path(PATH) / "2.0/Box/glTF-Embedded/Box.gltf"
        embedded = GLTF2().load(fembedded)

        fbinary = Path(PATH) / "2.0/Box/glTF-Binary/Box.glb"
        binary = GLTF2().load(fbinary)

        ffilebased = Path(PATH) / "2.0/Box/glTF/Box.gltf"
        filebased = GLTF2().load(ffilebased)

        assert len(embedded.buffers) == 1
        assert len(binary.buffers) == 1
        assert len(filebased.buffers) == 1

        binary.convert_buffers(BufferFormat.DATAURI)

        # so binary to datauri
        assert binary.buffers == embedded.buffers

        # reload binary
        binary = GLTF2().load(fbinary)

        # datauri to binary
        embedded.convert_buffers(BufferFormat.BINARYBLOB)
        assert binary.buffers == embedded.buffers

    def test_buffer_conversions_binfile(self):
        src = Path(PATH) / "2.0/Box/glTF-Embedded/Box.gltf"
        with tempfile.TemporaryDirectory() as tmpdirname:
            dest = Path(tmpdirname) / "Box.gltf"
            bindest = Path(tmpdirname) / "Box.glb"
            shutil.copy(str(src), str(dest))
            embedded = GLTF2().load(dest)

            embedded.convert_buffers(BufferFormat.BINFILE)
            embedded.save(bindest)

            assert (Path(tmpdirname) / "0.bin").is_file()


class TestExtensions:
    def test_load_mesh_primitive_extensions(self):
        f = Path(PATH).joinpath(f"2.0/ReciprocatingSaw/glTF-Draco/ReciprocatingSaw.gltf")
        gltf = GLTF2().load(f)
        assert gltf.meshes[0].primitives[0].extensions != None

        extensions = gltf.meshes[0].primitives[0].extensions
        assert "KHR_draco_mesh_compression" in extensions

        extension = gltf.meshes[0].primitives[0].extensions["KHR_draco_mesh_compression"]
        assert extension == {'bufferView': 0, 'attributes': {'NORMAL': 0, 'POSITION': 1}}

        extension = gltf.meshes[2].primitives[0].extensions["KHR_draco_mesh_compression"]
        assert extension == {'bufferView': 2, 'attributes': {'NORMAL': 0, 'POSITION': 1}}

    def test_save_mesh_primitive_extensions(self):
        f = Path(PATH).joinpath(f"2.0/ReciprocatingSaw/glTF-Draco/ReciprocatingSaw.gltf")
        gltf = GLTF2().load(f)
        with tempfile.TemporaryDirectory() as tmpdirname:
            t = Path(tmpdirname) / "extensions.gltf"
            gltf.save(t)
            gltf2 = GLTF2().load(t)
        extension = gltf2.meshes[2].primitives[0].extensions["KHR_draco_mesh_compression"]
        assert extension == {'bufferView': 2, 'attributes': {'NORMAL': 0, 'POSITION': 1}}

    def test_save_mesh_primitive_extensions_glb(self):
        f = Path(PATH).joinpath(f"2.0/ReciprocatingSaw/glTF-Draco/ReciprocatingSaw.gltf")
        gltf = GLTF2().load(f)
        with tempfile.TemporaryDirectory() as tmpdirname:
            t = Path(tmpdirname) / "extensions.glb"
            gltf.save(t)
            glb = GLTF2().load(t)
        extension = glb.meshes[2].primitives[0].extensions["KHR_draco_mesh_compression"]
        assert extension == {'bufferView': 2, 'attributes': {'NORMAL': 0, 'POSITION': 1}}

    def test_extension_khr_materials_unlit(self):
        # tests when extensions are empty but valid
        # uses a production file we can't distribute
        # TODO: replace with alternative
        if not COPYRIGHTED_AVAILABLE:
            return
        f = Path(CPATH).joinpath(f"ahri/gltf/ahri.gltf")
        gltf = GLTF2().load(f)
        with tempfile.TemporaryDirectory() as tmpdirname:
            t = Path(tmpdirname) / "extensions.gltf"
            gltf.save(t)
            gltf2 = GLTF2().load(t)
        extension = gltf2.materials[0].extensions["KHR_materials_unlit"]
        assert extension == {}

    def test_extension_khr_materials_unlit_glb(self):
        # tests when extensions are empty but valid
        # uses a production file we can't distribute
        # TODO: replace with alternative
        if not COPYRIGHTED_AVAILABLE:
            return
        f = Path(CPATH).joinpath(f"ahri/gltf/ahri.gltf")
        gltf = GLTF2().load(f)
        with tempfile.TemporaryDirectory() as tmpdirname:
            t = Path(tmpdirname) / "extensions.glb"
            gltf.save(t)
            gltf2 = GLTF2().load(t)
        extension = gltf2.materials[0].extensions["KHR_materials_unlit"]
        assert extension == {}

    def test_top_level(self):
        gltf = GLTF2()
        gltf.extensionsUsed = extensionsUsed = [
            "KHR_lights_punctual"
        ]
        gltf.extensionsRequired = extensionsRequired = [
            "KHR_lights_punctual"
        ]
        gltf.extensions = extensions = {
            "KHR_lights_punctual": {
                "lights": [{}]
            }
        }

        gltf = gltf.gltf_from_json(gltf_to_json(gltf))

        assert gltf.extensionsUsed == extensionsUsed
        assert gltf.extensionsRequired == extensionsRequired
        assert gltf.extensions == extensions


class TestAttributes:
    def basic_gltf(self):
        g = GLTF2()
        m = Mesh()
        p = Primitive()

        g.meshes.append(m)
        m.primitives.append(p)

        aa = Attributes()
        aa._MYCUSTOMATTRIBUTE = 123
        p.attributes = aa
        return g

    def test_application_specific_semantics_good(self):
        aa = Attributes()

        aa._MYCUSTOMATTRIBUTE = 123

        data = aa.to_json()
        result = '{"POSITION": null, "NORMAL": null, "TANGENT": null, "TEXCOORD_0": null, "TEXCOORD_1": null, "COLOR_0": null, "JOINTS_0": null, "WEIGHTS_0": null, "_MYCUSTOMATTRIBUTE": 123}'
        assert data == result

    def test_application_specific_semantics_bad(self):
        aa = Attributes()

        @dataclass
        class CustomClass:
            hello: str = "world"

        aa._MYCUSTOMATTRIBUTE = CustomClass()

        with pytest.raises(TypeError):
            data = aa.to_json()

    def test_attribute_inside_gltf(self):
        gltf = self.basic_gltf()
        data = gltf_to_json(gltf)
        assert '"attributes": {\n            "_MYCUSTOMATTRIBUTE": 123\n          }' in data

    def test_attribute_save(self):
        gltf = self.basic_gltf()
        gltf.meshes[0].primitives[0].attributes._MYCUSTOMATTRIBUTE = 124
        gltf.meshes[0].primitives[0].attributes.POSITION = 1
        with tempfile.TemporaryDirectory() as tmpdirname:
            t = Path(tmpdirname) / "attributes.gltf"
            gltf.save(t)
            gltf2 = GLTF2().load(t)

        attributes = gltf2.meshes[0].primitives[0].attributes
        assert attributes.POSITION == 1
        assert attributes._MYCUSTOMATTRIBUTE == 124


class TestBuffers:
    def test_buffer_datauri_load_gltf(self):
        f = Path(PATH) / "2.0/Triangle/glTF-Embedded/Triangle.gltf"
        gltf = GLTF2().load(f)

        assert gltf.buffers[
                   0].uri == "data:application/octet-stream;base64,AAABAAIAAAAAAAAAAAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAACAPwAAAAA="

    def test_buffer_datauri_save_gltf2gltf(self):
        f = Path(PATH) / "2.0/Triangle/glTF-Embedded/Triangle.gltf"
        gltf = GLTF2().load(f)
        with tempfile.TemporaryDirectory() as tmpdirname:
            t = Path(tmpdirname) / "buffers.gltf"
            gltf.save(t)
            gltf2 = GLTF2().load(t)
        assert gltf2.buffers[
                   0].uri == "data:application/octet-stream;base64,AAABAAIAAAAAAAAAAAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAACAPwAAAAA="

    def test_buffer_datauri_save_gltf2glb(self):
        f = Path(PATH) / "2.0/Box/glTF-Embedded/Box.gltf"
        gltf = GLTF2().load(f)
        with tempfile.TemporaryDirectory() as tmpdirname:
            t = Path(tmpdirname) / "buffers.glb"
            gltf.convert_buffers(BufferFormat.BINARYBLOB)
            gltf.save(t)
            print("buff", gltf.binary_blob())
            glb = GLTF2().load(t)
            r = Path(PATH) / "2.0/Box/glTF-Binary/Box.glb"
            reference = GLTF2().load(r)

       # assert glb.binary_blob() == reference.binary_blob()


class TestAccessors:
    def test_accessors(self):
        gltf = GLTF2()
        obj = Accessor()
        obj.componentType = UNSIGNED_INT
        gltf.accessors.append(obj)
        assert '"componentType": 5125' in gltf_to_json(gltf)


class TestTextureConvert:
    def test_(self):
        pass


def gltf_to_json(gltf: GLTF2, separators=None, indent="  "):
    gltf.asset.generator = 'test'
    return gltf.gltf_to_json(separators=separators, indent=indent)


class TestDefaults:
    def test_property(self):
        """ test that Property class defaults and optionals work """
        obj = Property()
        assert obj.extensions == {}
        assert obj.extras == {}
        assert obj.to_json() == '{"extensions": {}, "extras": {}}'

    def test_node(self):
        """ test that Node class defaults and optionals work """
        obj = Node()
        assert obj.children == []
        assert obj.matrix is None
        assert obj.rotation is None
        assert obj.scale is None
        assert obj.translation is None

    def test_primitive(self):
        gltf = GLTF2()
        obj = Primitive()
        mesh = Mesh()
        mesh.primitives.append(obj)
        gltf.meshes.append(mesh)
        assert obj.mode == 4  # TRIANGLE
        assert gltf_to_json(gltf) == """{
  "asset": {
    "generator": "test",
    "version": "2.0"
  },
  "meshes": [
    {
      "primitives": [
        {
          "attributes": {},
          "mode": 4
        }
      ]
    }
  ]
}"""

    def test_primitive_factory(self):
        """ Make sure primitive attributes are made using a factory
            https://gitlab.com/dodgyville/pygltflib/-/issues/43
        """
        p1 = Primitive()
        assert p1.attributes.POSITION is None

        p1.attributes.POSITION = 1
        assert p1.attributes.POSITION == 1

        p2 = Primitive()
        assert p1.attributes.POSITION is 1

        p2.attributes.POSITION = 2
        assert p1.attributes.POSITION == 1


    def test_accessor(self):
        gltf = GLTF2()
        obj = Accessor()
        gltf.accessors.append(obj)
        assert obj.byteOffset == 0
        assert obj.normalized is False
        assert gltf_to_json(gltf) == """{
  "accessors": [
    {
      "byteOffset": 0,
      "normalized": false
    }
  ],
  "asset": {
    "generator": "test",
    "version": "2.0"
  }
}"""

    def test_material(self):
        gltf = GLTF2()
        obj = Material()
        gltf.materials.append(obj)
        assert obj.emissiveFactor == [0.0, 0.0, 0.0]
        assert obj.alphaCutoff == 0.5
        assert obj.alphaMode == "OPAQUE"
        assert obj.doubleSided is False
        assert gltf_to_json(gltf) == """{
  "asset": {
    "generator": "test",
    "version": "2.0"
  },
  "materials": [
    {
      "alphaCutoff": 0.5,
      "alphaMode": "OPAQUE",
      "doubleSided": false,
      "emissiveFactor": [
        0.0,
        0.0,
        0.0
      ]
    }
  ]
}"""

    def test_material_pbrMetallicRoughness(self):
        gltf = GLTF2()
        obj = Material()
        obj.pbrMetallicRoughness = pbr = PbrMetallicRoughness()
        gltf.materials.append(obj)
        a = gltf_to_json(gltf)
        assert pbr.baseColorFactor == [1.0, 1.0, 1.0, 1.0]
        assert pbr.metallicFactor == 1.0
        assert pbr.roughnessFactor == 1.0

        assert gltf_to_json(gltf) == """{
  "asset": {
    "generator": "test",
    "version": "2.0"
  },
  "materials": [
    {
      "alphaCutoff": 0.5,
      "alphaMode": "OPAQUE",
      "doubleSided": false,
      "emissiveFactor": [
        0.0,
        0.0,
        0.0
      ],
      "pbrMetallicRoughness": {
        "baseColorFactor": [
          1.0,
          1.0,
          1.0,
          1.0
        ],
        "metallicFactor": 1.0,
        "roughnessFactor": 1.0
      }
    }
  ]
}"""


class TestOurValidator:
    def test_avalidate_accessors_sparse_validator(self):
        # test pygltflib wont raise InvalidBufferViewTarget
        gltf = GLTF2()
        obj = Accessor()
        obj.componentType = UNSIGNED_BYTE
        gltf.accessors.append(obj)
        try:
            validate(gltf) is True
        except InvalidBufferViewTarget:
            pytest.fail("InvalidBufferViewTarget was raised")


    def test_accessor_componentType_validator(self):
        # test pygltflib wont raise InvalidAcccessorComponentTypeException
        gltf = GLTF2()
        obj = Accessor()
        obj.componentType = UNSIGNED_BYTE
        gltf.accessors.append(obj)
        try:
            validate(gltf) is True
        except InvalidAcccessorComponentTypeException:
            pytest.fail("InvalidAcccessorComponentTypeException was raised")

    def test_accessor_componentType_validator_exception(self):
        gltf = GLTF2()
        obj = Accessor()
        obj.componentType = 666
        gltf.accessors.append(obj)

        with pytest.raises(InvalidAcccessorComponentTypeException):
            validate(gltf)


class TestBufferViews:
    def setup_method(self):
        # set up a gltf to test bufferViews
        self.gltf = GLTF2()
        buffer = Buffer()
        self.gltf.buffers.append(buffer)
        self.bV1 = BufferView(buffer=0)
        self.bV2 = BufferView(buffer=0)
        self.bV3 = BufferView(buffer=0)
        self.gltf.bufferViews.extend([self.bV1, self.bV2, self.bV3])

        accessor1 = Accessor()
        accessor1.bufferView = 0

        accessor2 = Accessor()
        accessor2.bufferView = 1

        accessor3 = Accessor()
        accessor3.bufferView = 2
        self.gltf.accessors.extend([accessor1, accessor2, accessor3])

        image1 = Image()
        image1.bufferView = 0
        image2 = Image()
        image2.bufferView = 1
        image3 = Image()
        image3.bufferView = 2

        self.gltf.images.extend([image3, image2, image1])  # backwards for variety

    def test_remove_bufferView(self):
        self.gltf.remove_bufferView(1)
        assert self.gltf.bufferViews == [self.bV1, self.bV3]

    def test_accessors(self):
        # make sure accessors using buffer views update OK too, (bufferViews >= 1 should decrement
        self.gltf.remove_bufferView(1)
        assert self.gltf.accessors[0].bufferView == 0
        assert self.gltf.accessors[1].bufferView == 0  # this should prompt a warning
        assert self.gltf.accessors[2].bufferView == 1

    def test_images(self):
        # make sure images using buffer views update OK too, (bufferViews >= 1 should decrement
        self.gltf.remove_bufferView(1)
        assert self.gltf.images[0].bufferView == 1
        assert self.gltf.images[1].bufferView == 0  # this should prompt a warning
        assert self.gltf.images[2].bufferView == 0

    def test_sparse(self):
        sparse1 = Sparse()
        sparse1.indices = AccessorSparseIndices()
        sparse1.indices.bufferView = 2
        self.gltf.accessors[0].sparse = sparse1

        sparse2 = Sparse()
        sparse2.indices = AccessorSparseIndices()
        sparse2.indices.bufferView = 1
        self.gltf.accessors[1].sparse = sparse2

        self.gltf.remove_bufferView(1)
        assert self.gltf.accessors[0].sparse.indices.bufferView == 1
        assert self.gltf.accessors[1].sparse.indices.bufferView == 0  # should have prompted a warning


class TestConvertImages:
    def test_from_datauri_to_file_with_name(self):
        # test that converting a data uri image to a PNG file works
        gltf = GLTF2()
        image = Image()
        image_data = "iVBORw0KGgoAAAANSUhEUgAAAAQAAAADCAIAAAA7ljmRAAAAGElEQVQIW2P4DwcMDAxAfBvMAhEQMYgcACEHG8ELxtbPAAAAAElFTkSuQmCC"
        image.uri = f"data:image/png;base64,{image_data}"
        image.name = "test_pygltflib.png"
        gltf.images.append(image)

        with tempfile.TemporaryDirectory() as tmpdirname:
            t = Path(tmpdirname) / "images.gltf"
            gltf.save(t)
            gltf = GLTF2().load(t)

            assert gltf.images[0].uri.endswith("kSuQmCC") is True
            gltf.convert_images(ImageFormat.FILE)

            p = Path(tmpdirname) / "test_pygltflib.png"

            assert gltf.images[0].uri == p.name
            assert p.exists()

            # check that running twice doesn't munge data
            gltf.convert_images(ImageFormat.FILE)
            assert gltf.images[0].uri == p.name

            with open(p, "rb") as image_file:
                data = image_file.read()
            assert data == base64.b64decode(image_data)

    def test_from_datauri_to_file_without_name(self):
        # test that converting a data uri image to a PNG file works
        gltf = GLTF2()
        image = Image()
        image_data = "iVBORw0KGgoAAAANSUhEUgAAAAQAAAADCAIAAAA7ljmRAAAAGElEQVQIW2P4DwcMDAxAfBvMAhEQMYgcACEHG8ELxtbPAAAAAElFTkSuQmCC"
        image.uri = f"data:image/png;base64,{image_data}"
        gltf.images.append(image)

        with tempfile.TemporaryDirectory() as tmpdirname:
            t = Path(tmpdirname) / "images.gltf"
            gltf.save(t)
            gltf = GLTF2().load(t)

            assert gltf.images[0].uri.endswith("kSuQmCC") is True
            gltf.convert_images(ImageFormat.FILE)

            # verify auto generated name has worked
            p = Path(tmpdirname) / "0.png"
            assert gltf.images[0].uri == p.name
            assert p.exists()

    def test_from_file_to_datauri(self):
        # test that converting a PNG image to a data uri
        image_data = "iVBORw0KGgoAAAANSUhEUgAAAAQAAAADCAIAAAA7ljmRAAAAGElEQVQIW2P4DwcMDAxAfBvMAhEQMYgcACEHG8ELxtbPAAAAAElFTkSuQmCC"
        image_uri = f"data:image/png;base64,{image_data}"

        gltf = GLTF2()
        image = Image()
        image.uri = "test_pygltflib.png"  # a real image file
        gltf.images.append(image)

        with tempfile.TemporaryDirectory() as tmpdirname:
            png_path = Path(tmpdirname) / "test_pygltflib.png"

            # setup PNG file
            with open(png_path, "wb") as image_file:
                data = base64.b64decode(image_data)
                image_file.write(data)

            gltf.convert_images(ImageFormat.DATAURI)

            assert gltf.images[0].uri == image_uri

    def test_from_binaryblob_to_file(self):
        # test that converting a PNG image stored in binary blob to a file
        if not KHRONOS_AVAILABLE:
            logging.warning("khronos sample data not available in %s"%os.getcwd())
            return
        filename = "glTF-Sample-Models/2.0/BoxTextured/glTF-Binary/BoxTextured.glb"
        gltf = GLTF2().load(filename)
        with tempfile.TemporaryDirectory() as tmpdirname:
            gltf._path = tmpdirname
            gltf.convert_images(ImageFormat.FILE)
            assert gltf.images[0].uri == "0.png"  # will now be 0.png and the texture image will be saved in 0.png

    def test_from_binaryblob_to_datauri(self):
        # test that converting a PNG image stored in binary blob to a data uri
        filename = "glTF-Sample-Models/2.0/BoxTextured/glTF-Binary/BoxTextured.glb"
        gltf = GLTF2().load(filename)
        with tempfile.TemporaryDirectory() as tmpdirname:
            gltf._path = tmpdirname
            gltf.convert_images(ImageFormat.DATAURI)
            assert gltf.images[0].uri.startswith("data:image/png;base64")  # will now be populated

    def test_export_image_to_file_bufferview_zero(self):
        fname = Path(PATH).joinpath("2.0/Avocado/glTF-Binary/Avocado.glb")
        glb = GLTF2().load(fname)
        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = glb.export_image_to_file(0, tmpdirname, True)
            assert (Path(tmpdirname) / fname).exists()


class TestBytesBuffer:
    def test_buffer_blob_padding_underrun(self):
        pass
        """
        buffer_blob += data[byte_offset:byte_offset + byte_length]
        The problem is that byte_offset + byte_length is clamped to the actual size of data, so no padding is copied if data is at the end and buffer_blob is smaller than required.
        Maybe it is further a good idea to explicitly use zeroes for padding instead of reading any unspecified data from data.
        """
        # filename = "glTF-Sample-Models/2.0/Box/glTF-Binary/Box.glb"
        # gltf = GLTF2().load(filename)
        # buffer_blob = gltf.buffers_to_binary_blob()

        # assert buffer_blob == gltf._glb_data

    def test_buffer_view_byte_length(self):
        #  it is better to use the unpadded size as length for the buffer view:
        # https://gitlab.com/dodgyville/pygltflib/-/blob/87ec1eb2ee44e69c14c41114b69485bbc180005b/pygltflib/__init__.py#L986
        #buffers_to_binary_blob
        pass


class TestJSON:
    def test_compact(self):
        gltf = GLTF2()
        output = gltf_to_json(gltf, separators=(',', ':'), indent=None)
        assert output == '{"asset":{"generator":"test","version":"2.0"}}'

    def test__default(self):
        gltf = GLTF2()
        output = gltf_to_json(gltf)
        assert output == """{
  "asset": {
    "generator": "test",
    "version": "2.0"
  }
}"""

class TestExamples:
    def test_a_simple_mesh(self):
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
        with tempfile.TemporaryDirectory() as tmpdirname:
            gltf.save("triangle.gltf")


