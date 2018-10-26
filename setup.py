import setuptools

from pygltflib import __version__


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pygltflib",
    version=__version__,
    author="Luke Miller",
    author_email="dodgyville@gmail.com",
    description="Python library for reading, writing and managing 3D objects in the Khronos Group gltf and gltf2 formats. Python 3.6+",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/dodgyville/pygltflib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
