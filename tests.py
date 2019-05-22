"""
To use:
link the glTF-Sample-Models into this directory eg:
ln -s /home/user/projects/glTF-Sample-Models .

To run:
./python3 -m test

"""
import base64

import pathlib

from pygltflib import GLTF2, Scene
from pygltflib.utils import add_primitive, add_indexed_geometry, buffer_to_uri, buffers_to_uri

PATH = "glTF-Sample-Models"


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
        assert gltf.accessors[0].bufferView == 0
        assert gltf.accessors[4].bufferView == 4

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
        glb.bufferViews.sort()
        glbed.bufferViews.sort()
        print("data", glbed._glb_data[:100])
        assert len(glb.scenes) > 0

    def test_loadGLBsaveGLB(self):
        f = "BrainStem"
        fname = pathlib.Path(PATH).joinpath(f"2.0/{f}/glTF-Binary/{f}.glb")
        glb = GLTF2().load(fname)
        glb.save("test.glb")
        glbed = GLTF2().load("test.glb")
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
        gltf.scene = 0
        gltf.scenes.append(scene)

        add_indexed_geometry(gltf, indices, vertices)
        gltf.save("test_primitive.gltf")
        pass

    def test_buffer_identify(self):
        gltf = add_primitive(None)
        data = gltf.buffers[0].uri
        data = base64.decodebytes(data)
        pass

    def test_buffer_from_blob_to_uri(self):
        binblob = b'\x00\x00\x01\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x00'
        uridata = 'AAABAAIAAAAAAAAAAAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAACAPwAAAAA='
        gltf = add_primitive(None)
        buffer_to_uri(gltf, 0)

    def test_buffer_to_uri(self):
        fname = pathlib.Path(PATH).joinpath("2.0/Avocado/glTF-Binary/Avocado.glb")
        glb = GLTF2().load(fname)

        buffers_to_uri(glb)
        import pdb; pdb.set_trace()
        glb.save("test_buffer_convert.gltf")
