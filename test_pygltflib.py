"""
To use:
link the glTF-Sample-Models into this directory eg:
ln -s /home/user/projects/glTF-Sample-Models .

To run:
pytest test_pygltflib.py

To see with regular print statements:
pytest -s test_pygltflib.py

A single test class:
pytest test_pygltflib.py::TextValidator


"""

import base64
from dataclasses import dataclass
import pathlib
import shutil
import tempfile
import warnings

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
    VEC2, VEC3, VEC4,
    Accessor,
    Asset,
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
    json_serial,
)
from pygltflib.utils import (
    add_primitive,
    add_indexed_geometry,
    validator,
    InvalidAcccessorComponentTypeException
)

PATH = "glTF-Sample-Models"

print(f"Testing version {pygltflib.__version__}")


class TestValidator:
    def setup_method(self, _test_method):
        path = pathlib.Path(PATH)
        if not path.exists():
            raise NotADirectoryError("Unable to find Khronos sample files at ", path.absolute())

    def test_Triangle(self):
        fname = pathlib.Path(PATH).joinpath("2.0/Triangle/glTF/Triangle.gltf")
        gltf = GLTF2().load(fname)
        assert gltf.asset.version == "2.0"

    def test_Triangles(self):
        fname = pathlib.Path(PATH).joinpath("2.0/SimpleMeshes/glTF/SimpleMeshes.gltf")
        gltf = GLTF2().load(fname)
        assert gltf.asset.version == "2.0"
        assert gltf.bufferViews[0].buffer == gltf.bufferViews[1].buffer

    def test_BoxVertexColors(self):
        fname = pathlib.Path(PATH).joinpath("2.0/BoxVertexColors/glTF-Embedded/BoxVertexColors.gltf")
        gltf = GLTF2().load(fname)
        assert gltf.asset.version == "2.0"
        assert gltf.accessors[0].bufferView == 0
        assert gltf.accessors[4].bufferView == 4


class TestIO:
    def test_load_glb(self):
        r = pathlib.Path(PATH) / "2.0/Box/glTF-Binary/Box.glb"
        reference = GLTF2().load(r)
        assert len(reference.buffers) == 1
        assert type(reference) == GLTF2

    def test_load_glb_static(self):
        r = pathlib.Path(PATH) / "2.0/Box/glTF-Binary/Box.glb"
        reference = GLTF2.load(r)
        assert len(reference.buffers) == 1
        assert type(reference) == GLTF2

    def test_load_glb_class(self):
        r = pathlib.Path(PATH) / "2.0/Box/glTF-Binary/Box.glb"

        class GLTFGoose(GLTF2):
            pass

        reference = GLTFGoose.load(r)
        assert len(reference.buffers) == 1
        assert type(reference) == GLTFGoose

    def test_save_glb2glb(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            r = pathlib.Path(PATH) / "2.0/Box/glTF-Binary/Box.glb"
            reference = GLTF2().load(r)

            f = pathlib.Path(PATH) / "2.0/Box/glTF-Binary/Box.glb"
            glb1 = GLTF2().load(r)

            t = pathlib.Path(tmpdirname) / "glb2glb.glb"
            glb1.save(t)
            glb2 = GLTF2().load(t)

            reference.convert_buffers(BufferFormat.DATAURI)
            glb2.convert_buffers(BufferFormat.DATAURI)

            assert glb2.binary_blob() == reference.binary_blob() == None

            assert glb2.buffers == reference.buffers

        # assert glb2.binary_blob() == reference.binary_blob()


class TestOutput:
    def test_Box(self):
        """ Load a GLB saved by us from the original GLTF"""
        fname = pathlib.Path("validator/Box_gltf.glb")
        gltf = GLTF2().load(fname)
        assert gltf.asset.version == "2.0"
        assert len(gltf.bufferViews) == 2
        assert gltf.accessors[2].bufferView == 1

    def test_AnimatedTriangle(self):
        """ Load a GLB saved by us from the original GLTF"""
        fname = pathlib.Path("validator/AnimatedTriangle_gltf.glb")
        gltf = GLTF2().load(fname)
        assert gltf.asset.version == "2.0"
        assert [(i, x.bufferView) for i, x in enumerate(gltf.accessors)] == [(0, 0), (1, 1), (2, 2), (3, 2)]

    def test_Avocado(self):
        """ Load a GLB saved by us from the original GLTF"""
        fname = pathlib.Path(PATH).joinpath("2.0/Avocado/glTF/Avocado.gltf")
        gltf = GLTF2().load(fname)
        gltf.save("validator/Avocado_gltf.glb")

        fname = pathlib.Path(PATH).joinpath("2.0/Avocado/glTF-Binary/Avocado.glb")
        glb = GLTF2().load(fname)

        fname = pathlib.Path("validator/Avocado_gltf.glb")
        glbnew = GLTF2().load(fname)
        assert glb.asset.version == "2.0"


class TestConversion:
    def setup_method(self, _test_method):
        path = pathlib.Path(PATH)
        if not path.exists():
            raise NotADirectoryError("Unable to find Khronos sample files at ", path.absolute())

    def test_loadGLB(self):
        f = "BrainStem"
        fname = pathlib.Path(PATH).joinpath(f"2.0/{f}/glTF-Binary/{f}.glb")
        glb = GLTF2().load(fname)
        print("data", glb._glb_data[:100])
        fnamejson = pathlib.Path(PATH).joinpath(f"2.0/{f}/glTF/{f}.gltf")
        gltf = GLTF2().load(fnamejson)
        gltf.save("test.glb")
        glbed = GLTF2().load("test.glb")
        print("data", glbed._glb_data[:100])
        assert len(glb.scenes) > 0

    def test_loadGLBsaveGLB(self):
        f = "BrainStem"
        fname = pathlib.Path(PATH).joinpath(f"2.0/{f}/glTF-Binary/{f}.glb")
        glb = GLTF2().load(fname)
        return

        with tempfile.TemporaryDirectory() as tmpdirname:
            t = pathlib.Path(tmpdirname) / "test.glb"
            glb.save(t)
            glbed = GLTF2().load(t)

        assert glbed._glb_data == glb._glb_data

    def test_loadGLBsaveGLTF(self):
        f = "BrainStem"
        fname = pathlib.Path(PATH).joinpath(f"2.0/{f}/glTF-Binary/{f}.glb")
        glb = GLTF2().load(fname)

        fnamejson = pathlib.Path(PATH).joinpath(f"2.0/{f}/glTF/{f}.gltf")
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

        print("data1")
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
        fembedded = pathlib.Path(PATH) / "2.0/Box/glTF-Embedded/Box.gltf"
        embedded = GLTF2().load(fembedded)

        fbinary = pathlib.Path(PATH) / "2.0/Box/glTF-Binary/Box.glb"
        binary = GLTF2().load(fbinary)

        ffilebased = pathlib.Path(PATH) / "2.0/Box/glTF/Box.gltf"
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
        src = pathlib.Path(PATH) / "2.0/Box/glTF-Embedded/Box.gltf"
        with tempfile.TemporaryDirectory() as tmpdirname:
            dest = pathlib.Path(tmpdirname) / "Box.gltf"
            bindest = pathlib.Path(tmpdirname) / "Box.glb"
            shutil.copy(str(src), str(dest))
            embedded = GLTF2().load(dest)

            embedded.convert_buffers(BufferFormat.BINFILE)
            embedded.save(bindest)

            assert (pathlib.Path(tmpdirname) / "0.bin").is_file()


class TestExtensions:
    def test_load_mesh_primitive_extensions(self):
        f = pathlib.Path(PATH).joinpath(f"2.0/ReciprocatingSaw/glTF-Draco/ReciprocatingSaw.gltf")
        gltf = GLTF2().load(f)
        assert gltf.meshes[0].primitives[0].extensions != None

        extensions = gltf.meshes[0].primitives[0].extensions
        assert "KHR_draco_mesh_compression" in extensions

        extension = gltf.meshes[0].primitives[0].extensions["KHR_draco_mesh_compression"]
        assert extension == {'bufferView': 0, 'attributes': {'NORMAL': 0, 'POSITION': 1}}

        extension = gltf.meshes[2].primitives[0].extensions["KHR_draco_mesh_compression"]
        assert extension == {'bufferView': 2, 'attributes': {'NORMAL': 0, 'POSITION': 1}}

    def test_save_mesh_primitive_extensions(self):
        f = pathlib.Path(PATH).joinpath(f"2.0/ReciprocatingSaw/glTF-Draco/ReciprocatingSaw.gltf")
        gltf = GLTF2().load(f)
        with tempfile.TemporaryDirectory() as tmpdirname:
            t = pathlib.Path(tmpdirname) / "extensions.gltf"
            gltf.save(t)
            gltf2 = GLTF2().load(t)
        extension = gltf2.meshes[2].primitives[0].extensions["KHR_draco_mesh_compression"]
        assert extension == {'bufferView': 2, 'attributes': {'NORMAL': 0, 'POSITION': 1}}

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

        gltf = gltf.gltf_from_json(gltf.gltf_to_json())

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
        data = gltf.gltf_to_json()
        assert '"attributes": {\n            "_MYCUSTOMATTRIBUTE": 123\n          }' in data

    def test_attribute_save(self):
        gltf = self.basic_gltf()
        gltf.meshes[0].primitives[0].attributes._MYCUSTOMATTRIBUTE = 124
        gltf.meshes[0].primitives[0].attributes.POSITION = 1
        with tempfile.TemporaryDirectory() as tmpdirname:
            t = pathlib.Path(tmpdirname) / "attributes.gltf"
            gltf.save(t)
            gltf2 = GLTF2().load(t)

        attributes = gltf2.meshes[0].primitives[0].attributes
        assert attributes.POSITION == 1
        assert attributes._MYCUSTOMATTRIBUTE == 124


class TestBuffers:
    def test_buffer_datauri_load_gltf(self):
        f = pathlib.Path(PATH) / "2.0/Triangle/glTF-Embedded/Triangle.gltf"
        gltf = GLTF2().load(f)

        assert gltf.buffers[
                   0].uri == "data:application/octet-stream;base64,AAABAAIAAAAAAAAAAAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAACAPwAAAAA="

    def test_buffer_datauri_save_gltf2gltf(self):
        f = pathlib.Path(PATH) / "2.0/Triangle/glTF-Embedded/Triangle.gltf"
        gltf = GLTF2().load(f)
        with tempfile.TemporaryDirectory() as tmpdirname:
            t = pathlib.Path(tmpdirname) / "buffers.gltf"
            gltf.save(t)
            gltf2 = GLTF2().load(t)
        assert gltf2.buffers[
                   0].uri == "data:application/octet-stream;base64,AAABAAIAAAAAAAAAAAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAACAPwAAAAA="

    def test_buffer_datauri_save_gltf2glb(self):
        f = pathlib.Path(PATH) / "2.0/Box/glTF-Embedded/Box.gltf"
        gltf = GLTF2().load(f)
        with tempfile.TemporaryDirectory() as tmpdirname:
            t = pathlib.Path(tmpdirname) / "buffers.glb"
            gltf.convert_buffers(BufferFormat.BINARYBLOB)
            gltf.save(t)
            print("buff", gltf.binary_blob())
            glb = GLTF2().load(t)
            r = pathlib.Path(PATH) / "2.0/Box/glTF-Binary/Box.glb"
            reference = GLTF2().load(r)

        assert glb.binary_blob() == reference.binary_blob()


class TestAccessors:
    def test_accessors(self):
        gltf = GLTF2()
        obj = Accessor()
        obj.componentType = UNSIGNED_INT
        gltf.accessors.append(obj)
        assert '"componentType": 5125' in gltf.gltf_to_json()


class TestTextureConvert:
    def test_(self):
        pass


class TestDefaults:
    def test_property(self):
        """ test that Property class defaults and optionals work """
        obj = Property()
        assert obj.extensions == {}
        assert obj.extras == {}
        assert obj.to_json() == '{"extensions": {}, "extras": {}}'

    def test_primitive(self):
        gltf = GLTF2()
        obj = Primitive()
        mesh = Mesh()
        mesh.primitives.append(obj)
        gltf.meshes.append(mesh)
        assert obj.mode == 4  # TRIANGLE
        assert gltf.gltf_to_json() == """{
  "asset": {
    "generator": "pygltflib@v1.13.1",
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

    def test_accessor(self):
        gltf = GLTF2()
        obj = Accessor()
        gltf.accessors.append(obj)
        assert obj.byteOffset == 0
        assert obj.normalized is False
        assert gltf.gltf_to_json() == """{
  "accessors": [
    {
      "byteOffset": 0,
      "normalized": false
    }
  ],
  "asset": {
    "generator": "pygltflib@v1.13.1",
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
        assert gltf.gltf_to_json() == """{
  "asset": {
    "generator": "pygltflib@v1.13.1",
    "version": "2.0"
  },
  "materials": [
    {
      "emissiveFactor": [
        0.0,
        0.0,
        0.0
      ],
      "alphaMode": "OPAQUE",
      "alphaCutoff": 0.5,
      "doubleSided": false
    }
  ]
}"""

    def test_material_pbrMetallicRoughness(self):
        gltf = GLTF2()
        obj = Material()
        obj.pbrMetallicRoughness = pbr = PbrMetallicRoughness()
        gltf.materials.append(obj)
        a = gltf.gltf_to_json()
        assert pbr.baseColorFactor == [1.0, 1.0, 1.0]
        assert pbr.metallicFactor == 1.0
        assert pbr.roughnessFactor == 1.0

        assert gltf.gltf_to_json() == """{
  "asset": {
    "generator": "pygltflib@v1.13.1",
    "version": "2.0"
  },
  "materials": [
    {
      "pbrMetallicRoughness": {
        "baseColorFactor": [
          1.0,
          1.0,
          1.0
        ],
        "metallicFactor": 1.0,
        "roughnessFactor": 1.0
      },
      "emissiveFactor": [
        0.0,
        0.0,
        0.0
      ],
      "alphaMode": "OPAQUE",
      "alphaCutoff": 0.5,
      "doubleSided": false
    }
  ]
}"""



class TestOurValidator:
    def test_accessor_componentType_validator(self):
        # test pygltflib wont raise InvalidAcccessorComponentTypeException
        gltf = GLTF2()
        obj = Accessor()
        obj.componentType = UNSIGNED_BYTE
        gltf.accessors.append(obj)
        try:
            validator(gltf) is True
        except InvalidAcccessorComponentTypeException:
            pytest.fail("InvalidAcccessorComponentTypeException was raised")

    def test_accessor_componentType_validator_exception(self):
        gltf = GLTF2()
        obj = Accessor()
        obj.componentType = 666
        gltf.accessors.append(obj)

        with pytest.raises(InvalidAcccessorComponentTypeException):
            validator(gltf)


class TestConvertImages:
    def test_remove_bufferView(self):
        gltf = GLTF2()
        buffer = Buffer()
        gltf.buffers.append(buffer)
        bV1 = BufferView(buffer=0)
        bV2 = BufferView(buffer=0)
        bV3 = BufferView(buffer=0)

        gltf.bufferViews.extend([bV1, bV2, bV3])


    def test_from_datauri_to_file_with_name(self):
        # test that converting a data uri image to a PNG file works
        gltf = GLTF2()
        image = Image()
        image_data = "iVBORw0KGgoAAAANSUhEUgAAAAQAAAADCAIAAAA7ljmRAAAAGElEQVQIW2P4DwcMDAxAfBvMAhEQMYgcACEHG8ELxtbPAAAAAElFTkSuQmCC"
        image.uri = f"data:image/png;base64,{image_data}"
        image.name = "test.png"
        gltf.images.append(image)

        with tempfile.TemporaryDirectory() as tmpdirname:
            t = pathlib.Path(tmpdirname) / "images.gltf"
            gltf.save(t)
            gltf = GLTF2().load(t)

            assert gltf.images[0].uri.endswith("kSuQmCC") is True
            gltf.convert_images(ImageFormat.FILE)

            p = pathlib.Path(tmpdirname) / "test.png"

            assert gltf.images[0].uri == p.name
            assert p.exists()

            # check that running twice doesn't munge data
            gltf.convert_images(ImageFormat.FILE)
            assert gltf.images[0].uri == p.name

            p2 = pathlib.Path("/home/luke/Projects/pygltflib/test.png")
            shutil.copy(p, p2)

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
            t = pathlib.Path(tmpdirname) / "images.gltf"
            gltf.save(t)
            gltf = GLTF2().load(t)

            assert gltf.images[0].uri.endswith("kSuQmCC") is True
            gltf.convert_images(ImageFormat.FILE)

            # verify auto generated name has worked
            p = pathlib.Path(tmpdirname) / "0.png"
            assert gltf.images[0].uri == p.name
            assert p.exists()

    def test_from_file_to_datauri(self):
        # test that converting a PNG image to a data uri
        gltf = GLTF2()
        image = Image()
        image_data = "iVBORw0KGgoAAAANSUhEUgAAAAQAAAADCAIAAAA7ljmRAAAAGElEQVQIW2P4DwcMDAxAfBvMAhEQMYgcACEHG8ELxtbPAAAAAElFTkSuQmCC"
        image_uri = f"data:image/png;base64,{image_data}"
        image.uri = "test.png"
        gltf.images.append(image)

        with tempfile.TemporaryDirectory() as tmpdirname:
            png_path = pathlib.Path(tmpdirname) / "test.png"

            # setup PNG file
            with open(png_path, "wb") as image_file:
                data = base64.b64decode(image_data)
                image_file.write(data)

            gltf.convert_images(ImageFormat.DATAURI)

            assert gltf.images[0].uri == image_uri


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
