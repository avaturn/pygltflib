* 1.13.10
   * Add GLTF2.set_binary_blob for improved access of binary data
   * splot GLTF2.save_binary into two methods
     * GLTF2.save_binary - functions the same way as the original method
     * GLTF2.save_to_bytes - returns an array containing a binary GLTF file in an array structure 

* 1.13.9
   * split GLTF2.load_binary into more useful class methods (Patiphan Wongklaew)
      * GLTF2.load_binary - functions the same way as the original method
      * GLTF2.load_from_bytes - takes raw bytes directly
      * GLTF2.load_binary_from_file_object - loads from a file-like object
    * add missing test image

* 1.13.8
   * removed deprecated encoding argument from json parsers (deprecated since python 3.1)
   * add support for python 3.9 (Margarida Silva)

* 1.13.7
    * change docs and code to be more readable
* 1.13.6
    * add 4th array element to `baseColorFactor` to match specification
* 1.13.5
    * fix Matrix, Translation, Scale, and Rotation to default to None
    * change `utils.validator` by moving to `validator.validate`
    * add `validator.summary` to provide human readable output of validator
    * add some more unit tests

* 1.13.4
    * add warning to `remove_bufferView` if leaving dangling references to removed bufferView
    * add tests for `remove_bufferView`
    * add node access and remove_bufferView examples to README
    * add validation for animation channels
    * change `metallicRoughnessTexture` to use `TextureInfo`
    * change requirements to not install dataclasses in python 3.7 and above
    * fix `remove_bufferView` when sparse accessor is None
    * fix spelling of `InvalidAccessorSparseIndicesComponentTypeException`

* 1.13.3
    * add support to `GLTF.convert_images` to convert from buffers to image files. NOTE: Does not update buffer yet.
    * add support to `GLTF.convert_images` to convert from buffers to data uris. NOTE: Does not update buffer yet.
    * add accessor sparse indices bufferview check to validator 
    * fix test suite to write tmp files to tmp directory instead of install directory
    * remove support for old versions of dataclasses-json
    * renamed CUBICSPLINE, LINEAR and STEP to ANIM_LINEAR, ANIM_STEP, ANIM_CUBICSPLINE to fix clash with webGL constants 
    * change bin file conversion to only lose binary blob on successful file export

* 1.13.2 
    * add deprecated to pip setup

* 1.13.1
    * add `GLTF.convert_images` method for converting texture image data from data uris to files and vice versa
    * add 'name' attribute to `Image`
    * add more unittests
    * change `Primitive` so that `Attributes` is created on init 

* 1.13.0
    * NOTE: There are a few small deprecations in this version to tighten up the library that will be removed in version 2.0.0
    * deprecate class `SparseAccessor` in favour of `AccessorSparseIndices` and `AccessorSparseValues` (please update your code)
    * deprecate class `MaterialTexture` in favour of `TextureInfo` to better match GLTF2 specification (please update your code)
    * deprecate `AlphaMode` ENUM in favour of constants (eg replace `AlphaMode.OPAQUE` with `OPAQUE` (please update your code)
    * fix support for `material.occlusionTextureInfo`  
    * fix support for `material.normalTextureInfo`
    * fix sampler support in `Animation` class by adding `AnimationSampler`
    * add default values for Accessor, AnimationSampler, BufferView, Material, PbrMetallicRoughness, Primitive, Sampler
    * add Optional to attributes for better type hinting
    * add initial `utils.validator` to validate GLTF2 object accessor and bufferViews
    
* 1.12.0
    * fix bug with binfile path handling
    
* 1.11.10
    * convert load methods from staticmethod to classmethods

* 1.11.9
    * change GLTF.load to a staticmethod
    * add AlphaMode enum type

* 1.11.8
    * add missing top level extensions
    
* 1.11.7
    * add missing `normalized` flag to Accessor

* 1.11.6
    * add support for extensions
    * add support for extras
    * add support for custom attributes on Attributes
    * set Primitive.attributes to `None` by default (use `primitive.attributes = Attributes()`)
    * remove warning about byteStride as that is not the responsibility of this library
    * add lots of tests

* 1.11.5
    * reorder `identify_uri` to avoid using lengthy byte strings as file names
    * assign parent path when saving so bin files save to same path

* 1.11.4
    * remove padding
    * improve dataclasses-json backwards compatibility

* 1.11.3
    * fix import issue with setup.py

* 1.11.2
    * fix issue with long data uris saving in glb
    * fix compatibility issue with different versions of dataclasses-json
    
* 1.11.1
    * update documentation
    * improve packaging

* 1.11
    * add access to internal glb binary data via `GLTF.binary_blob()`
    * add `convert_buffers` method to switch buffer formats between data uri, binary files and binary blobs
* 1.10
    * handle empty buffers on save
    * warn about unsupported data uri bufferViews
    * allow transparent textures (with alpha channel)
* 1.9
    * use factories to create Attributes and Asset objects
* 1.8
    * allow images to point to bufferViews
* 1.7
    * preserve order of bufferViews when saving to glb
    * pad binary chunks within embedded data correctly
* 1.6
    * provide better support for binary (.glb) files (bug fixes)
    * promote `load_json`, `load_binary`, `save_json` and `save_binary` from internal methods 
* 1.5
    * align embedded data correctly
    * add `glb2gltf` and `gltf2glb` util functions to `pygltflib.utils` for easy file conversion
* 1.4 
    * add basic support for saving to binary GLTF (.glb) files
    * move undocumented non-core methods to `pygltfib.utils`
* 1.3 
    * add basic support for reading binary GLTF (.glb) files
* 1.2 
    * provide better json support
    * remove numpy requirement
    * suppress infer warning
    * add basic default methods
* 1.0 
    * initial release
