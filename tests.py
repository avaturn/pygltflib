"""
To use:
link the glTF-Sample-Models into this directory eg:
ln -s /home/user/projects/glTF-Sample-Models .

To run:
./python3.7 -m test

"""

import os.path
import unittest

from pygltflib import GLTF2

PATH = "glTF-Sample-Models"


class TestLoad(unittest.TestCase):

    def test_Triangle(self):
        fname = os.path.join(PATH, "2.0/Triangle/glTF/Triangle.gltf")
        gltf = GLTF2().load(fname)
        self.assertEqual(gltf.asset.version, "2.0")

    def test_Triangles(self):
        fname = os.path.join(PATH, "2.0/SimpleMeshes/glTF/SimpleMeshes.gltf")
        gltf = GLTF2().load(fname)
        self.assertEqual(gltf.asset.version, "2.0")
        self.assertEqual(gltf.bufferViews[0].buffer, gltf.bufferViews[1].buffer)

    def test_BoxVertexColors(self):
        fname = os.path.join(PATH, "2.0/BoxVertexColors/glTF-Embedded/BoxVertexColors.gltf")
        gltf = GLTF2().load(fname)
        self.assertEqual(gltf.asset.version, "2.0")
        self.assertEqual(gltf.accessors[0].bufferView, 0)
        self.assertEqual(gltf.accessors[4].bufferView, 4)


if __name__ == '__main__':
    unittest.main()
    #import doctest
    #doctest.testfile("README.md")