from pathlib import Path
from typing import Union
import pandas as pd
import itertools
import logging
import os


from urdf_analyzer.urdf_components.urdf_information import URDFInformation
from urdf_analyzer.urdf_components.joint import JointsMetaInformation
from urdf_analyzer.urdf_components.link import LinksMetaInformation
from urdf_analyzer.model_analysis import ModelAnalysis
from urdf_analyzer.urdf_parser import URDFparser
from urdf_analyzer.constants import *


def search_for_urdfs(dir: Union[str, Path]):
    l = logging.getLogger("urdf_analyzer")

    list_of_urdf_file_paths = []

    # Check that path exists
    if not Path(dir).exists():
        l.warning(f"The path '{dir}' for searching for urdf files does not exist. Returning empty list.")
        return list_of_urdf_file_paths

    for path in Path(dir).rglob("*.urdf"):
        list_of_urdf_file_paths.append(path)

    if len(list_of_urdf_file_paths) == 0:
        l.warning(f"No URDF files were found when searching in the path: {dir}")
    return list_of_urdf_file_paths


def schema_generator(schemas, files, **kwargs):
    urdf_parsing_comparison = None
    if "model-info" in schemas:
        generate_model_information_schema(files)
    if "urdf-parse-cmp" in schemas:
        urdf_parsing_comparison = generate_urdf_parsing_comparison_schema(files)
    if "tool-cmp" in schemas:
        urdf_parsing_comparison = urdf_parsing_comparison if not None else None
        generate_tool_comparison_schema(files, urdf_parsing_comparison)
    if "duplicates-cmp" in schemas:
        dup_cmp_parser = None
        if 'dup_cmp_parser' in kwargs:
            dup_cmp_parser = kwargs['dup_cmp_parser'] # TODO: implement dup_cmp_parser in the 'generate_duplicates_comparison_schema' function
        generate_duplicates_comparison_schema(kwargs['duplicates_dir'], dup_cmp_parser)


def _count_word_in_urdf_file(word, urdf_file):
    with open(urdf_file) as f:
        return int(f.read().count(word))

def _count_n_lines_in_file(file):
    with open(file, 'r') as fp:
        n_lines = len(fp.readlines())
    return n_lines

def _get_word_information(words, file):
    for word in list(words.keys()):
        words[word] = _count_word_in_urdf_file(word, file)
    return words


def generate_tool_comparison_schema(urdf_files, urdf_parsing_results=None, out=True):
    parsers = URDFparser.supported_parsers
    parser_results = {}
    for p in parsers:
        parser_results[p] = 0

    # read urdf file and check for words
    words = {'xacro': 0,'package': 0, 'author':0}

    tool_cmp_results_column_name = 'n_passed_urdfs'
    tool_cmp_results = pd.DataFrame(0, index=parsers, columns=[tool_cmp_results_column_name])

    if isinstance(urdf_files, list):
        if urdf_parsing_results is None:
            urdf_parsing_results = get_parsings_information(urdf_files, parsers)

        # add word columns
        for word in words.keys():
            urdf_parsing_results[word] = 0
            tool_cmp_results[word] = 0

        for urdf_file in urdf_files:
            words = _get_word_information(words, urdf_file)
            urdf_parsing_results.loc[urdf_file, list(words.keys())] = list(words.values())

        # dropping the count column, as we're not using it
        urdf_parsing_results = urdf_parsing_results.drop(['count'], axis=1)
        
        tool_cmp_results.loc[:,tool_cmp_results_column_name] = urdf_parsing_results.iloc[:,0:len(parsers)].sum()
        
        total_files_words = words
        for word in words:
            total_files_words[word] = urdf_parsing_results.query(f"{word} > 0").shape[0]
            for p in parsers:
                n_passed_with_word = urdf_parsing_results.query(f"{p} == True & {word} > 0").shape[0]
                tool_cmp_results.loc[p,word] = f"{n_passed_with_word}/{tool_cmp_results.loc[p,tool_cmp_results_column_name]}"
        
        n_urdf_files = urdf_parsing_results.shape[0]

        tool_cmp_results = tool_cmp_results.rename(columns={w:f"n_{w}_passed, total: {total_files_words[w]}" for w in words})
        tool_cmp_results.loc[:,tool_cmp_results_column_name] = tool_cmp_results.loc[:,tool_cmp_results_column_name].astype(str) + f"/{n_urdf_files}"
        
    if out == True:
        _save_information(tool_cmp_results, output_file=f"{DEFAULT_OUTPUT_DIR}/tool_comparison_schema")
    else:
        _save_information(tool_cmp_results, out)
    
    return tool_cmp_results


def generate_model_information_schema(urdf_files, out=True):
    kwargs = {'joints': True, 'links': True}
    urdfs_information: list[URDFInformation] = []
    if isinstance(urdf_files, list):
        urdfs_information = get_models_information(urdf_files, **kwargs)
    else:
        urdfs_information.append(get_model_information(urdf_files, **kwargs))
    
    if out == True:
        save_model_information(urdfs_information, output_file=f"{DEFAULT_OUTPUT_DIR}/model_information_schema", full_results=True)
    else:
        save_model_information(urdfs_information, output_file=out, full_results=True)

    # TODO: change urdfs_information and return a pandas Dataframe instead, to be consistent with the other get_XX_schema functions

    return urdfs_information


def generate_urdf_parsing_comparison_schema(urdf_files, out=True):
    parsers = URDFparser.supported_parsers 
    if isinstance(urdf_files, list):
        parsing_results = get_parsings_information(urdf_files, parsers)
    else:
        parsing_results = get_parsing_information(urdf_files, parsers) # TODO: check up with the urdf_root_dir

    if out == True:
        _save_information(parsing_results, output_file=f"{DEFAULT_OUTPUT_DIR}/urdf_parsing_comparison_schema")
    else:
        _save_information(parsing_results, out)

    return parsing_results    


def generate_duplicates_comparison_schema(duplicates_dir, dup_cmp_parser=None, out=True):
    duplicates_subdirectories = _get_subdirectories(duplicates_dir)

    # create dataframe with indices as subdirs
    meta_information = _get_meta_information_duplicates(duplicates_subdirectories[0]) # get an example of the meta_information attributes
    meta_info_columns = [info for info in meta_information.keys()]
    duplicates_information_columns = meta_info_columns + ["source","n_urdf_files","n_joints","n_links","visual_meshes","collision_meshes","n_lines"]
    duplicates_comparisons_columns = meta_info_columns + ["sources","joints_diff","links_diff","mesh_diff","fk_diff","n_lines_diff"]
    duplicates_information = pd.DataFrame(columns=duplicates_information_columns)
    duplicates_comparisons = pd.DataFrame(columns=duplicates_comparisons_columns)
    
    for subdirectory in duplicates_subdirectories:
        duplicates_information, duplicates_comparisons = _get_duplicates_information(subdirectory, duplicates_information, duplicates_comparisons)

    if out == True:
        _save_information(duplicates_information, output_file=f"{DEFAULT_OUTPUT_DIR}/duplicates_information_schema.csv")
        _save_information(duplicates_comparisons, output_file=f"{DEFAULT_OUTPUT_DIR}/duplicates_comparison_schema.csv")
    else:
        _save_information(duplicates_information, out)
        _save_information(duplicates_comparisons, out)


def _get_duplicates_information(dir, duplicates_information, duplicates_comparisons):
    logger = logging.getLogger("urdf_analyzer")
    meta_information = _get_meta_information_duplicates(dir)
    subdirectories = _get_subdirectories(dir)

    model_information_kwargs = {'joints': True, 'links': True}
    transformations = {}
    
    # for each subdirectory in the current directory, get the urdf files, and run the analysis. Add results to dataframe
    for subdir in subdirectories:
        source_information = _get_source_information_duplicates(subdir)
        urdf_files = search_for_urdfs(subdir)

        # perform analysis
        n_urdf_files = len(urdf_files)

        if n_urdf_files > 1:
            urdfs_information: list(URDFInformation) = get_models_information(urdf_files, **model_information_kwargs)
            n_joints = 0
            n_links = 0
            n_lines = 0
            visual_meshes = {}
            collision_meshes = {}
            for urdf in urdfs_information:
                n_joints += urdf.joint_information.n_joints
                n_links += urdf.link_information.n_links
                # n_lines += _count_n_lines_in_file(Path(subdir,urdf.filename)) # TODO: implement n_lines
                visual_meshes = _get_n_mesh_types(visual_meshes, urdf.link_information.visual_mesh_types)
                collision_meshes = _get_n_mesh_types(collision_meshes, urdf.link_information.collision_mesh_types)
            transformations[f"{meta_information['name']}_{source_information['source']}"] = None
        else:
            filename = urdf_files[0]
            urdf_information: URDFInformation = get_model_information(filename, **model_information_kwargs)
            n_joints = urdf_information.joint_information.n_joints
            n_links = urdf_information.link_information.n_links
            visual_meshes = urdf_information.link_information.visual_mesh_types
            collision_meshes = urdf_information.link_information.collision_mesh_types
            n_lines = _count_n_lines_in_file(filename)
            try:
                model = _parser_urdf(logging.getLogger("urdf_analyzer"),filename,'roboticstoolbox')
                transformations[f"{meta_information['name']}_{source_information['source']}"] = model.fkine(model.q)
            except:
                transformations[f"{meta_information['name']}_{source_information['source']}"] = None

        # consider adding number of urdf_parsers that each file can sucessfully pass through
        

        # TODO: make it more flexible, so if new parameters are added to the meta_information or source_information, then they will also be incldued in the results
        information_results = {'name': meta_information['name'], 
                    'source': source_information['source'], 
                    'type': meta_information['type'],
                    'manufacturer': meta_information['manufacturer'],
                    'n_urdf_files': n_urdf_files,
                    'n_joints': n_joints,
                    'n_links': n_links,
                    'visual_meshes': str(visual_meshes),
                    'collision_meshes': str(collision_meshes),
                    'n_lines': n_lines}

        
        
        duplicates_information = pd.concat([duplicates_information, pd.DataFrame(data=information_results, index=[0])])
        
        # accumulate to one index using: pd.MultiIndex.from_frame(df)
    
    n_duplicates = len(subdirectories)

    if len(transformations) > 1:
        for transformation1,transformation2 in itertools.combinations(transformations, 2):
            if transformations[transformation1] != transformations[transformation2]: 
                if not Path(DEFAULT_TRANFORMATION_COMPARISON_DIR).exists():
                    os.mkdir(DEFAULT_TRANFORMATION_COMPARISON_DIR)
                # TODO: fix this, so the same transformation isn't saved multiple times (waste of resources)
                try:
                    import numpy as np
                    transformation_a = np.array(transformations[transformation1])
                    transformation_b = np.array(transformations[transformation2])
                    np.savetxt(Path(DEFAULT_TRANFORMATION_COMPARISON_DIR,f"{transformation1}.txt"),transformation_a,fmt='%.4f')
                    np.savetxt(Path(DEFAULT_TRANFORMATION_COMPARISON_DIR,f"{transformation2}.txt"),transformation_b,fmt='%.4f')
                    transformation_diff = np.subtract(transformation_a, transformation_b)
                    np.savetxt(Path(DEFAULT_TRANFORMATION_COMPARISON_DIR,f"{meta_information['name']}_diff_{transformation1.split('_')[-1]}_{transformation2.split('_')[-1]}.txt"),np.array(transformation_diff),fmt='%.4f')
                except:
                    logger.warning("Error occurred when saving the transformations of the duplicates.")
                fk_diff = True
                # duplicates_information.iloc[len(duplicates_information)-n_duplicates:len(duplicates_information), duplicates_information.columns.get_loc('fk_same')] = False
            else:
                fk_diff = ""
                # duplicates_information.iloc[len(duplicates_information)-n_duplicates:len(duplicates_information), duplicates_information.columns.get_loc('fk_same')] = True


    
    comparison_results = {'name': meta_information['name'], 
                    'type': meta_information['type'],
                    'manufacturer': meta_information['manufacturer'],
                    'sources': [],
                    'joints_diff': None,
                    'links_diff': None,
                    'mesh_diff': None,
                    'fk_diff': fk_diff,
                    'n_lines_diff': n_lines
                    }



    cur_urdf_files_index = len(duplicates_information)-n_duplicates
    joints_info = duplicates_information.iloc[cur_urdf_files_index:len(duplicates_information),duplicates_information.columns.get_loc("n_joints")]
    links_info = duplicates_information.iloc[cur_urdf_files_index:len(duplicates_information),duplicates_information.columns.get_loc("n_links")]
    visual_mesh_info = duplicates_information.iloc[cur_urdf_files_index:len(duplicates_information),duplicates_information.columns.get_loc("visual_meshes")]
    collision_mesh_info = duplicates_information.iloc[cur_urdf_files_index:len(duplicates_information),duplicates_information.columns.get_loc("collision_meshes")]
    n_lines_info = duplicates_information.iloc[cur_urdf_files_index:len(duplicates_information),duplicates_information.columns.get_loc("n_lines")]

    sources = list(duplicates_information.iloc[cur_urdf_files_index:len(duplicates_information),duplicates_information.columns.get_loc("source")])
    comparison_results['sources'] = str(sources)

    comparison_results = _compare_information(joints_info, comparison_results, "joints_diff")
    comparison_results = _compare_information(links_info, comparison_results, "links_diff")
    comparison_results = _compare_information(visual_mesh_info, comparison_results, "mesh_diff")
    if comparison_results["mesh_diff"] != "":
        comparison_results = _compare_information(collision_mesh_info, comparison_results, "mesh_diff")
    comparison_results = _compare_information(n_lines_info, comparison_results, "n_lines_diff")
    

    duplicates_comparisons = pd.concat([duplicates_comparisons, pd.DataFrame(data=comparison_results, index=[0])])
    
    return duplicates_information, duplicates_comparisons


def _compare_information(information, comparison_results, key):
    for info1, info2 in itertools.combinations(information, 2):
            if info1 != info2: 
                comparison_results[key] = True
            else:
                comparison_results[key] = ""
    return comparison_results



def _get_meta_information_duplicates(duplicates_dir):
    import json
    
    with open(f"{Path(duplicates_dir, META_INFORMATION_FILENAME)}", 'r') as f:
        meta_information = json.load(f)

    return meta_information

def _get_source_information_duplicates(dir):
    import json
    
    try:
        with open(f"{Path(dir, SOURCE_INFORMATION_FILENAME)}", 'r') as f:
            source_information = json.load(f)
    except:
        sources_information_files = []
        for path in Path(dir).rglob(f"{SOURCE_INFORMATION_FILENAME}"):
            sources_information_files.append(path)
        with open(f"{Path(sources_information_files[0])}", 'r') as f:
            source_information = json.load(f)

    return source_information


def _get_n_mesh_types(mesh, link_mesh_dict):
    for mesh_type in link_mesh_dict.keys():
        if mesh_type not in mesh:
            mesh[mesh_type] = link_mesh_dict[mesh_type]
        else:
            mesh[mesh_type] += link_mesh_dict[mesh_type]
    return mesh

def _get_subdirectories(dir):
    subdirectories = [f.path for f in os.scandir(dir) if f.is_dir()]
    return subdirectories

def get_model_information(filename: str=None, model_analysis: ModelAnalysis=None, **kwargs):
    """
    Get information on the model of the URDF, i.e. joints, links, etc.

    :param filename: the URDF filename
    :type filename: str
    :param \**kwargs:
        See below
    :raises XX:
    :return urdf_information: a URDFInformation object consisting of the analysed data
    :rtype: URDFInformation


    :Keyword Arguments:
        * *urdf_root_dir* (``str``) --
          The root directory of the URDF file. This is mainly used if the URDF file is not in the current directory. It is also used to be able to localise the meshes.
        * *joints* (``boolean``) --
          If True, then the joint information is obtained and sved in the returned URDFInformation.
        * *model_analysis* (``ModelAnalysis``) --
          A ModelAnalysis object. It is expected that the urdf file has been loaded using the xml_urdf_reader() function, thus there is no need to reload the file.

    full description

    .. note::
        - filename structure etc.
    
    """
    l = logging.getLogger("urdf_analyzer")

    if filename is not None and model_analysis is None:
        model_analysis = ModelAnalysis(l)
        urdf_root_dir = None
        if 'urdf_root_dir' in kwargs:
            urdf_root_dir = kwargs['urdf_root_dir']
        model_analysis.xml_urdf_reader(filename, urdf_root_dir)

    # checking that the file has been parsed by the xml reader in model_analysis
    if model_analysis is None or model_analysis.root is None:
        l.warning("The filename has not be properly passed to the xml reader. Returning empty URDFInformation object.")
        return URDFInformation()

    urdf_information = URDFInformation(filename)

    if 'joints' in kwargs and kwargs['joints'] == True:
        urdf_information.joint_information: JointsMetaInformation = model_analysis.get_joint_information()
    if 'links' in kwargs and kwargs['links'] == True:
        urdf_information.link_information: LinksMetaInformation = model_analysis.get_link_information()
        
    return urdf_information



def get_models_information(urdf_files: list[str], **kwargs):
    """
    Get information on the models of the URDF files, i.e. joints, links, etc.

    :param urdf_files:
    :param \**kwargs:
        See below
    :raises XX:
    :return YY:
    :rtype: list[URDFInformation]

    :Keyword Arguments:
        * *urdf_files* (``list``) --
          List of URDF files to analyse
        * *joints* (``boolean``) --
          If True, then the joint information is obtained and sved in the returned URDFInformation.


    full description

    .. note::
        - filename structure etc.
    
    """
    l = logging.getLogger("urdf_analyzer")
    model_analysis = ModelAnalysis(l)
    urdfs_information = []

    for urdf_file in urdf_files:

        urdf_root_dir = os.path.dirname(os.path.abspath(urdf_file))
        model_analysis.xml_urdf_reader(urdf_file, urdf_root_dir)
        # if 'filename' in kwargs.keys():
        #     kwargs['filename'] = os.path.basename(urdf_file)
        # else:
        kwargs['filename'] = os.path.basename(urdf_file) # TODO: check if this is working or if I messed everything up
        urdf_information = get_model_information(model_analysis=model_analysis, **kwargs)

        urdfs_information.append(urdf_information)

    return urdfs_information


def _parser_urdf(logger: logging.Logger, filename: str, parser: str, urdf_root_dir: str=None):
    tool_parser = URDFparser(parser, logger)
    model = tool_parser.load_urdf(filename, urdf_root_dir)
    return model


def get_parsing_information(filename: str, parser: Union[str, list[str]]=URDFparser.supported_parsers, urdf_root_dir: str=None):
    l = logging.getLogger("urdf_analyzer")
    if isinstance(parser, str):
        parser = [parser]

    # results on urdf files and tools
    urdfs_and_tools_results_column_names = parser
    urdfs_and_tools_results = pd.DataFrame(columns=urdfs_and_tools_results_column_names)

    for p in parser:
        model = _parser_urdf(l, filename, p, urdf_root_dir)
        urdfs_and_tools_results.loc[0, p] = True if model is not None else False

    # Update urdfs_and_tools_results with sum of tools where the URDF file passes
    urdfs_and_tools_results.loc[:,'count'] = urdfs_and_tools_results.sum(numeric_only=False, axis=1)
    urdfs_and_tools_results = urdfs_and_tools_results.sort_values(by='count', ascending=False)

    # TODO: unify the saving method, e.g. if the 'filename' should only be the file or also the directory
    urdfs_and_tools_results = urdfs_and_tools_results.rename(index={0:filename})

    return urdfs_and_tools_results


def get_parsings_information(urdf_files: list[str], parser: Union[str, list[str]]=URDFparser.supported_parsers):
    l = logging.getLogger("urdf_analyzer")
    parsing_results = pd.DataFrame()

    for urdf_file in urdf_files:
        urdf_root_dir = os.path.dirname(os.path.abspath(urdf_file))
        parsing_result = get_parsing_information(urdf_file, parser, urdf_root_dir)
        parsing_results = pd.concat([parsing_results, parsing_result])

    return parsing_results


def save_model_information(urdfs_information: list[URDFInformation], output_file: str=None, full_results=False):
    l = logging.getLogger("urdf_analyzer")

    df_results = pd.DataFrame()
    for urdf_info in urdfs_information:
        urdf_info.compile_results(full_results)
        df_results = pd.concat([df_results, urdf_info.df_results]) # for each urdf file, add the urdf_info results to the dataframe

    df_results = _save_information(df_results, output_file)

    return df_results



def _save_information(df_results, output_file: str=None):
    l = logging.getLogger("urdf_analyzer")
    from datetime import datetime
    if output_file is None:
        output_file = f"{DEFAULT_OUTPUT_DIR}/{datetime.now().strftime('%Y_%m_%d-%I_%M_%S_%p')}.csv"
    dir = os.path.dirname(output_file)
    l.info(f"Output directory for saving analysis information: '{dir}'")
    if not Path(dir).exists():
        l.info(f"Creating directory for saving analysis information: '{Path(dir)}'")
        os.mkdir(dir)

    # check if provided filename has extension .csv
    # TODO: check if the provided filename has an extension, if not use .csv as default
    ext = ["csv", "md", "json", "xlsx"]
    if output_file.split(".")[-1] not in ext:
        output_file += "." + ext[0]
    elif Path(output_file).exists():
        l.warning(f"The file {output_file} exists. Overwriting it.")

    if output_file.split(".")[-1] == ext[0]:
        df_results.to_csv(Path(output_file))
    elif output_file.split(".")[-1] == ext[1]:
        df_results.to_markdown(Path(output_file))
    elif output_file.split(".")[-1] == ext[2]:
        df_results.to_json(Path(output_file))
    elif output_file.split(".")[-1] == ext[3]:
        df_results.to_excel(Path(output_file))

    return df_results