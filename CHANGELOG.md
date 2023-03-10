* 1.15.1:
  * Dataclasses install only required on python 3.6.x (cherry-pick from Saeid Akbari branch)
  * Removed deprecated `AlphaMode` after two years (use the `pygltflib.BLEND`, `pygltflib.MASK`, `pygltflib.OPAQUE` constants directly)
  * Removed deprecated `SparseAccessor` after two years (use `AccessorSparseIndices` and `AccessorSparseValues` instead)
  * Removed deprecated `MaterialTexture` after two years (use `TextureInfo` instead)
  * removed `deprecated` requirement from project

* 1.15.0: 
  * Significantly improved `save_to_bytes` performance (20x faster) (Florian Bruggisser)
    * NOTE: Underlying binary blob is now mutable instead of immutable. 

* 1.14.7
  * add `GLTF.get_data_from_buffer_uri` helper method to simplify access to buffer data (see bounding box example in README.md) (el_flamenco)

* 1.14.6
  * use compact json when save binary glb files (Laubeee)

* 1.14.5
  * unquote filepath in compliance with standard (irtimir)

* 1.14.4
  * Add `GLTF.export_image` method to export images from an GLTF2 file to any location (Khac Hoa Le)
  * remove extraneous print message when loading extensions (Michael Daw)

* 1.14.3
  * add ability to save data directly in the uri field to `save_to_bytes` (Israel)
  * fix issue where attributes field is shared between two instances of Primitive (Konstantin Sinitsyn)

* 1.14.2
  * improve mimetype handling (Gabriel Unmüßig)

* 1.14.1
  * fix unicode error in setup.py (Andrew Stockton)

* 1.14.0
   * NOTE: Converting image.bufferView to image file now obeys "override" flag and also uses object path
   * fix issue where image.bufferView with value '0' is interpreted as false (Dzmitry Stabrouski)
   * fix issue where override flag ignored when converting image.bufferView to image file
   * change image.bufferView export to image path handling to be same as image.uri export
   * add longer example of mesh->bytes->mesh (Alexander Druz)
   * add GLTF.convert_images takes a 'path' argument that overrides the origin or destination
     path when convert from or to files.

* 1.13.10
   * NOTE: `GLTF2.load` now throws `FileNotFoundError` instead of failing silently on missing file.
   * fix issue where extensions with empty but valid dicts were not saving 
   * add `GLTF2.set_binary_blob` for improved access of binary data
   * split `GLTF2.save_binary` into two methods
     * GLTF2.save_binary - functions the same way as the original method
     * GLTF2.save_to_bytes - returns an array containing a binary GLTF file in an array structure 

* 1.13.9
   * split `GLTF2.load_binary` into more useful class methods (Patiphan Wongklaew)
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
