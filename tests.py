"""
To use:
link the glTF-Sample-Models into this directory eg:
ln -s /home/user/projects/glTF-Sample-Models .

To run:
./python3 -m test

"""

import pathlib

from pygltflib import GLTF2

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

