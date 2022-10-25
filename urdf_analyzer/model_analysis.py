import xml.etree.ElementTree as ET
import os
from logging import Logger
from joint import Joint, JointsMetaInformation


class ModelAnalysis:


    def __init__(self, logger: Logger):
        self.logger = logger


    def xml_urdf_reader(self, filename: str, urdf_root_dir:str=None):
        root_dir = os.getcwd()
        basename = os.path.abspath(filename)
        if urdf_root_dir is None:
            urdf_root_dir = os.path.dirname(basename)
        filename_only = os.path.basename(basename)
        try:
            os.chdir(urdf_root_dir)
            tree = ET.ElementTree(file=filename_only)
        except:
            self.logger.error(f"Error while loading {basename} using the xml reader")
            tree = None
            pass
        os.chdir(root_dir)
        if tree is None:
            return None
        self.root = tree.getroot()
        return self.root

    
    ### START ### Joint information ######

    def _get_joint_information(self, root: ET.ElementTree):
        joints = []
        for joint in root.iter("joint"):
            try:
                joints.append(Joint(joint.attrib['name'], joint.attrib['type']))
            except:
                pass
        joints_information = JointsMetaInformation(joints)
        return joints_information

    def get_joint_information(self):
        return self._get_joint_information(self.root)

    def get_joint_information(self, filename: str, urdf_root_dir:str=None):
        self.root = self.xml_urdf_reader(filename, urdf_root_dir)
        return self._get_joint_information(self.root)

    ### END ### Joint information ######
