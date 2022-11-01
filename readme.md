Todo tool:
* Testing
    - create tests for model_analysis
    - create tests for joint
    - create tests for link
    - create tests for urdf_parser
    - add testing of the 'full' argument in the cli tests
* Development API
    - in the save information func, check that the checking of existence of the output file is done correctly with regards to the directory
    - figure out how to export the information, csv? txt? latex table?
    - add analysis of urdf using the urdf parsers
    - does it make sense to add an exclusion of files or subfolders when performing the urdf-search-dir?
    - add domain knowledge, e.g. the user should be able to specify the system is a robotic arm with X DOF, and then the URDF analyser can analyse it and check that this is correct
* Development CLI
    - add cli for geometry (.dae, .stl, .obj)
    - add cli for file analysis ('xacro' in file, 'package' in file)



Notes:

To setup the package in development, run `python setup.py develop` from the root directory.