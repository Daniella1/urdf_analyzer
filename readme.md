Todo tool:
* Testing
    - create tests for api
    - create tests for cli
    - create tests for model_analysis
    - create tests for joint
    - create tests for urdf_parser
* Development API
    - save information on analysis (currently only joint)
    - in the save information func, check that the checking of existence of the output file is done correctly with regards to the directory
    - add link information analysis
    - save information to a file
    - figure out how to export the information, csv? txt? latex table?
    - add analysis of urdf using the urdf parsers
    - does it make sense to add an exclusion of files or subfolders when performing the urdf-search-dir?
* Development CLI
    - add checking of '--out' parameter
    - add cli for geometry (.dae, .stl, .obj)
    - add cli for file analysis ('xacro' in file, 'package' in file)



Notes:

To setup the package in development, run `python setup.py develop` from the root directory.