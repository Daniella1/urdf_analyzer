from dataclasses import dataclass
import logging
from joint import JointsMetaInformation
from model_analysis import ModelAnalysis


@dataclass
class URDFInformation:

    def __init__(self, joint_information: JointsMetaInformation=None):
        self.joint_information = joint_information


def get_model_information(parser: str, **kwargs):
    """
    Get information on the model of the URDF, i.e. joints, links, etc.

    :param parser: the urdf parser to use, can choose from: {yourdfpy, urdfpy, roboticstoolbox}
    :type parser: str
    :raises XX:
    :return YY:
    :rtype: pandas dataframe

    full description

    .. note::
        - uses the chosen parser to load the URDF file
        - filename structure etc.
    
    """
    l = logging.getLogger("urdf_inspector")
    model_analysis = ModelAnalysis(l)
    urdf_information = URDFInformation()
    
    if kwargs['joints'] == True and kwargs['filename'] is not None:
        urdf_root_dir = None
        if 'urdf_root_dir' in kwargs:
            urdf_root_dir = kwargs['urdf_root_dir']
        urdf_information.joint_information: JointsMetaInformation = model_analysis.get_joint_information(kwargs['filename'], urdf_root_dir)

    return urdf_information
