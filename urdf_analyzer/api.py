from dataclasses import dataclass
import logging
import os
from pathlib import Path

from joint import JointsMetaInformation
from model_analysis import ModelAnalysis


@dataclass
class URDFInformation:

    def __init__(self, joint_information: JointsMetaInformation=None):
        self.joint_information = joint_information


def search_for_urdfs(dir: str):
    list_of_urdf_file_paths = []
    for path in Path(dir).rglob("*.urdf"):
        list_of_urdf_file_paths.append(path)
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
    :return YY:
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
    l = logging.getLogger("urdf_inspector")

    if filename is not None and 'model_analysis' not in kwargs:
        model_analysis = ModelAnalysis(l)
        urdf_root_dir = None
        if 'urdf_root_dir' in kwargs:
            urdf_root_dir = kwargs['urdf_root_dir']
        root = model_analysis.xml_urdf_reader(filename, urdf_root_dir)

    urdf_information = URDFInformation()
    
    if kwargs['joints'] == True:
        urdf_information.joint_information: JointsMetaInformation = model_analysis.get_joint_information()

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
    l = logging.getLogger("urdf_inspector")
    model_analysis = ModelAnalysis(l)
    urdfs_information = []

    for urdf_file in urdf_files:

        urdf_root_dir = os.path.dirname(os.path.abspath(urdf_file))
        model_analysis.xml_urdf_reader(urdf_file, urdf_root_dir)
        urdf_information = get_model_information(model_analysis=model_analysis, **kwargs)

        urdfs_information.append(urdf_information)

    return urdfs_information
