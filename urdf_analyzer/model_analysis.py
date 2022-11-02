import xml.etree.ElementTree as ET
import os
from logging import Logger
from urdf_analyzer.urdf_components.joint import Joint, JointsMetaInformation
from urdf_analyzer.urdf_components.link import Link, LinksMetaInformation, Mesh, Box, Sphere, Cylinder
from urdf_analyzer.urdf_standard import LinkStandard

class ModelAnalysis:


    def __init__(self, logger: Logger):
        self.logger = logger
        self.root = None


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


    def get_information_from_file(self, filename: str, info_type: str="joint", root_dir: str=None):
        info_types = ["joint", "link"]
        if info_type not in info_types:
            self.logger.warn(f"The chosen information type '{info_type}' is not supported. The supported types are '{info_types}'. Returning None.")
            return None
        self.root = self.xml_urdf_reader(filename, root_dir)

        if info_type == info_types[0]:
            if self.root is None:
                self.logger.warning(f"The XML file {filename} has been read incorrectly. Returning empty joint information.")
                return JointsMetaInformation([])
            return self._get_joint_information(self.root)
        elif info_type == info_types[1]:
            if self.root is None:
                self.logger.warning(f"The XML file {filename} has been read incorrectly. Returning empty link information.")
                return LinksMetaInformation([])
            return self._get_link_information(self.root)

        # code should not get here, but if so, then return None
        return None
    
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

    ### END ### Joint information ######


    ### START ### Link information ######

    def _check_optional_and_required_args_geometry(self, search_geometry, geometry):
        if len(geometry.required_arguments) > 0:
            for required_arg in geometry.required_arguments:
                setattr(geometry, required_arg, search_geometry[0].attrib[required_arg])
        if len(geometry.optional_arguments) > 0:
            for optional_arg in geometry.optional_arguments:
                if optional_arg in search_geometry[0].attrib:
                    setattr(geometry, optional_arg, search_geometry[0].attrib[optional_arg])
        return geometry
        

    def _get_link_geometry_information(self, tag_names, geometry_visualisation_type):
        if geometry_visualisation_type in tag_names:
            # TODO: see if it is possible to dynamically pass the number of required variables as None when instantiating the Geometry types
            try:
                # check if mesh
                search_mesh = list(tag_names[geometry_visualisation_type].iter(LinkStandard.geometry_types[0]))
                if len(search_mesh) == 1: # TODO: double check that it makes sense to only take the first value of the list
                    mesh = Mesh(None)
                    return self._check_optional_and_required_args_geometry(search_mesh, mesh)
                         
                # check if box
                search_box = list(tag_names[geometry_visualisation_type].iter(LinkStandard.geometry_types[3]))
                if len(search_box) == 1: # TODO: double check that it makes sense to only take the first value of the list
                    box = Box()
                    return self._check_optional_and_required_args_geometry(search_box, box)
       
                # check if cylinder
                search_cylinder = list(tag_names[geometry_visualisation_type].iter(LinkStandard.geometry_types[2]))
                if len(search_cylinder) == 1:
                    cylinder = Cylinder(None, None)
                    return self._check_optional_and_required_args_geometry(search_cylinder, cylinder)

                # check if sphere
                search_sphere = list(tag_names[geometry_visualisation_type].iter(LinkStandard.geometry_types[1]))
                if len(search_sphere) == 1:
                    sphere = Sphere(None)
                    return self._check_optional_and_required_args_geometry(search_sphere, sphere)
            except:
                pass
        #self.logger.warning("The link geometry could not be determined.")
        return None

    def _get_link_information(self, root: ET.ElementTree):
        links = []
        for link in root.iter("link"):
            tag_names = {x.tag:x for x in link.iter("*")}
            try:
                name = link.attrib["name"]
                visual_geometry = self._get_link_geometry_information(tag_names, LinkStandard.visualisation_types[0])
                collision_geometry = self._get_link_geometry_information(tag_names, LinkStandard.visualisation_types[1])
                links.append(Link(name=name,visual_geometry=visual_geometry,collision_geometry=collision_geometry))
            except:
                pass
        links_information = LinksMetaInformation(links)
        return links_information

    def get_link_information(self):
        return self._get_link_information(self.root)


    ### END ### Link information ######

# TODO: add domain knowledge, e.g. the user should be able to specify the system is a robotic arm with X DOF, and then the URDF analyser can analyse it and check that this is correct