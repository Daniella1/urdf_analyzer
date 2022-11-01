from dataclasses import dataclass
from pathlib import Path
from typing import Union
import pandas as pd
import logging
import os


from urdf_analyzer.urdf_components.joint import JointsMetaInformation
from urdf_analyzer.urdf_components.link import LinksMetaInformation
from urdf_analyzer.model_analysis import ModelAnalysis
from urdf_analyzer.constants import *


@dataclass
class URDFInformation:

    def __init__(self, filename: str=None, joint_information: JointsMetaInformation=None, link_information: LinksMetaInformation=None):
        self.joint_information = joint_information
        self.link_information = link_information
        self.filename = filename
        self.df_results = None

    def compile_results(self, full_results=False):
        self.df_results = pd.DataFrame(index=[0])
        
        self._add_res_to_dataframe("joint_information", full_results)
        self._add_res_to_dataframe("link_information", full_results)
        
        self.df_results = self.df_results.rename(index={0:self.filename})

    
    def _add_res_to_dataframe(self, information, full_results=False):
        info = getattr(self, str(information))
        if info is not None:
            if full_results:
                self.df_results =  self.df_results.join(info.df_results_full)
            else:
                self.df_results =  self.df_results.join(info.df_results)
        

       

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


def get_model_information(parser: str='yourdfpy', filename: str=None, model_analysis: ModelAnalysis=None, **kwargs):
    """
    Get information on the model of the URDF, i.e. joints, links, etc.

    :param parser: the urdf parser to use, can choose from: {yourdfpy, urdfpy, roboticstoolbox}
    :type parser: str
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
        - uses the chosen parser to load the URDF file
        - filename structure etc.
    
    """
    l = logging.getLogger("urdf_analyzer")

    if filename is not None and model_analysis is None:
        model_analysis = ModelAnalysis(l)
        urdf_root_dir = None
        if 'urdf_root_dir' in kwargs:
            urdf_root_dir = kwargs['urdf_root_dir']
        root = model_analysis.xml_urdf_reader(filename, urdf_root_dir)

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
        - uses the chosen parser to load the URDF file
        - filename structure etc.
    
    """
    l = logging.getLogger("urdf_analyzer")
    model_analysis = ModelAnalysis(l)
    urdfs_information = []

    for urdf_file in urdf_files:

        urdf_root_dir = os.path.dirname(os.path.abspath(urdf_file))
        model_analysis.xml_urdf_reader(urdf_file, urdf_root_dir)
        if 'filename' in kwargs.keys():
            kwargs['filename'] = os.path.basename(urdf_file)
        urdf_information = get_model_information(model_analysis=model_analysis, **kwargs)

        urdfs_information.append(urdf_information)

    return urdfs_information




def save_information(urdfs_information: list[URDFInformation], output_file: str=None, full_results=False):
    l = logging.getLogger("urdf_analyzer")

    from datetime import datetime
    if output_file is None:
        output_file = f"{DEFAULT_OUTPUT_DIR}/{datetime.now().strftime('%Y_%m_%d-%I_%M_%S_%p')}.csv"
    dir = os.path.dirname(output_file)
    l.debug(f"Output directory for saving analysis information: '{dir}'")
    if not Path(dir).exists():
        l.debug(f"Creating directory for saving analysis information: '{Path(dir)}'")
        os.mkdir(dir)

    # check if provided filename has extension .csv
    ext = [".csv"]
    if output_file[-4:] != ext[0]:
        output_file += ext[0]
    elif Path(output_file).exists():
        l.warning(f"The file {output_file} exists. Overwriting it.")

    df_results = pd.DataFrame()
    for urdf_info in urdfs_information:
        urdf_info.compile_results(full_results)
        df_results = pd.concat([df_results, urdf_info.df_results]) # for each urdf file, add the urdf_info results to the dataframe

    df_results.to_csv(Path(output_file))

    return df_results
