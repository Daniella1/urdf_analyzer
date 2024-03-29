<p align="center">
    <img alt="ViewCount" src="https://views.whatilearened.today/views/github/Daniella1/urdf_analyzer.svg">
    <br>
    Counting since 20-10-2023
</p>

# URDF Analyzer

This is a tool developed to analyze URDF Collections.
It is created to be used as a standalone tool or together with the [URDF Dataset](https://github.com/Daniella1/urdf_files_dataset).
It allows analyzing single URDF files, or directories containing URDF files where schemas of the results can be generated.

## Command Line Interface

The following shows the different use cases that the _urdf_analyzer_ supports.

### Generate schemas

Obtain the model-information of the urdf files found in a specific directory (recursively).
```
urdf_analyzer generate-schemas model-info --urdf-search-dir <directory-to-search-for-urdfs>
```
Compare parsing performance of urdf tools on urdf files found in a specific directory (recursively).
```
urdf_analyzer generate-schemas tool-cmp --urdf-search-dir <directory-to-search-for-urdfs>
```
Compare duplicates in a specified folder.
```
urdf_analyzer generate-schemas duplicates-cmp --duplicates-dir <directory-containing-duplicates>
```


### Todo tool:
* Testing
    - create tests for model_analysis
    - create tests for joint
    - create tests for link
    - create tests for urdf_parser
    - add testing of the 'full' argument in the cli tests
    - add testing of get_parsing_information in the api tests
    - add testing of parsing_information in the cli tests
    - add a test to check that the generated schema contains all of the necessary information, e.g. filenames..
* Development API
    - in the save information func, check that the checking of existence of the output file is done correctly with regards to the directory
    - figure out how to export the information, csv? txt? latex table?
    - add analysis of urdf using the urdf parsers
    - does it make sense to add an exclusion of files or subfolders when performing the urdf-search-dir?
    - add domain knowledge, e.g. the user should be able to specify the system is a robotic arm with X DOF, and then the URDF analyser can analyse it and check that this is correct
    - check if it would be better/faster to load one URDF loader, and then run through all the files, or if the current method is ok.
    - fix the checking of 'xacro' and 'package' to ensure it's not in the comments of the xml file
    - create a get_mesh_analysis_schema function that just takes out the mesh values from the model_information dataframe
    - consider adding a textual description of the differences between the duplicate urdfs
    - setup the check_urdf as a parser, and make that the default one
* Development CLI
    - add cli for geometry (.dae, .stl, .obj)
    - add cli for file analysis ('xacro' in file, 'package' in file)
* Documentation
    - describe the different schemas that can be generated

Notes:

To setup the package in development, run `python setup.py develop` from the root directory.
