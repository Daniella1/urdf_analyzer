import xml.etree.ElementTree as ET
import os
from logging import Logger

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
        root = tree.getroot()
        return root


    ### START ### Link and mesh information #######
    def _get_link_info(self, root: ET.ElementTree):
        links_all_types = []
        links_visual = {}
        links_collision = {}
        for link in root.iter("link"):
            link_name = link.attrib["name"]
            links_all_types.append(link_name)
            tag_names = {x.tag:x for x in link.iter("*")}
            links_visual = self._add_mesh_info(links_visual, link_name, "visual", tag_names)
            links_collision = self._add_mesh_info(links_collision, link_name, "collision", tag_names)
        return links_all_types, links_visual, links_collision


    def _get_mesh_type_from(self,tag_names, visualisation_type):
        vis_type = tag_names[visualisation_type]
        try:
            return (list(vis_type.iter("mesh"))[0].attrib['filename']).split('.',1)[1]
        except:
            return None


    def _add_mesh_info(self,mesh_link_dict, link_name, mesh_type, tag_names):
        if mesh_type in tag_names:
            cur_mesh_type = self._get_mesh_type_from(tag_names,mesh_type)
            if cur_mesh_type is not None:
                mesh_link_dict[link_name] = cur_mesh_type.lower()
            else:
                mesh_link_dict[link_name] = None
        return mesh_link_dict
    ### END ### Link and mesh information #######


    
    ### START ### Joint information ######
    def _get_n_joint_type(self, joint_types, type):
        n_type_joints = len([j for j in list(joint_types.values()) if j == type])
        return n_type_joints

    def get_joint_information(self, root: ET.ElementTree):
        joint_types = {}
        for joint in root.iter("joint"):
            try:
                joint_types[joint.attrib['name']] = joint.attrib['type']
            except:
                pass
        # Joint type defined from: http://wiki.ros.org/urdf/XML/joint
        n_revolute_joints = self._get_n_joint_type(joint_types, 'revolute')
        n_fixed_joints = self._get_n_joint_type(joint_types, 'fixed')
        n_prismatic_joints = self._get_n_joint_type(joint_types, 'prismatic')
        n_continuous_joints = self._get_n_joint_type(joint_types, 'continuous')
        n_floating_joints = self._get_n_joint_type(joint_types, 'floating')
        n_planar_joints = self._get_n_joint_type(joint_types, 'planar')
        return joint_types, n_revolute_joints, n_fixed_joints, n_prismatic_joints, n_continuous_joints, n_floating_joints, n_planar_joints


    ### END ### Joint information ######
