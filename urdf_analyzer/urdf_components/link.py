from dataclasses import dataclass
import pandas as pd

from urdf_analyzer.urdf_standard import LinkStandard

# following the standard defined in: https://wiki.ros.org/urdf/XML/link
# the types and required parameters are from (with a few modifications): https://github.com/ros/urdfdom/blob/master/xsd/urdf.xsd 

@dataclass
class Geometry:

    def __init__(self) -> None:
        self._set_argument_requirements()

    def _set_argument_requirements(self):
        assert self.geometry_type is not None, f"Error in the program, the geometry type of the Geomtry object is not specified."
        self.optional_arguments = LinkStandard.geometries_arguments[self.geometry_type]['optional']
        self.required_arguments = LinkStandard.geometries_arguments[self.geometry_type]['required']

@dataclass
class Box(Geometry):
     def __init__(self, size: str="0 0 0") -> None:
        """
        :param size: attribute contains the three side lengths of the box. The origin of the box is in its center.
        :type size: float
        """
        self.geometry_type = LinkStandard.geometry_types[3]
        super().__init__()
        self.size = size

@dataclass
class Cylinder(Geometry):
    def __init__(self, radius: float, length: float) -> None:
        """
        Specify the radius and length. The origin of the cylinder is in its center.

        :param radius: radius of the cylinder
        :type radius: float
        :param length: length of the cylinder
        type length: float
        """
        self.geometry_type = LinkStandard.geometry_types[2]
        super().__init__()
        self.radius = radius
        self.length = length

@dataclass
class Sphere(Geometry):

    def __init__(self, radius: float) -> None:
        """
        :param radius: Specify the radius. The origin of the sphere is in its center.
        :type radius: float
        """
        self.geometry_type = LinkStandard.geometry_types[1]
        super().__init__()
        self.radius = radius

@dataclass
class Mesh(Geometry):

    def __init__(self, filename: str, scale: str="1 1 1") -> None:
        """
        A trimesh element specified by a filename, and an optional scale that scales the mesh's axis-aligned-bounding-box. 
        Any geometry format is acceptable but specific application compatibility is dependent on implementation. 
        The recommended format for best texture and color support is Collada .dae files. 
        The mesh file is not transferred between machines referencing the same model. 
        It must be a local file. 
        Prefix the filename with package://<packagename>/<path> to make the path to the mesh file relative to the package <packagename>. 
        :param filename: name of trimesh element
        :type filename: str
        :param scale: scale of the mesh
        :type scale: int
        """
        self.geometry_type = LinkStandard.geometry_types[0]
        super().__init__()
        self.filename = filename
        self.scale = scale
    


@dataclass
class Link:

    def __init__(self, name: str, visual_geometry: Geometry=None, collision_geometry: Geometry=None) -> None:
        """
        A link element has one attribute: name.

        :param name: The name of the link itself 
        :type name: str
        """
        self.name = name
        self.visual_geometry = visual_geometry
        self.collision_geometry = collision_geometry





@dataclass
class LinksMetaInformation:

    def _obtain_mesh_types(self, link_geometry: Geometry, mesh_types):
        if link_geometry is not None and link_geometry.geometry_type == LinkStandard.geometry_types[0]:
            mesh_type = (link_geometry.filename.split('.',1)[1]).lower()
            if mesh_type not in mesh_types:
                mesh_types[mesh_type] = 1
            else:
                mesh_types[mesh_type] += 1
        return mesh_types

    def __init__(self, links: list[Link]) -> None:
        """
        
        returns self, which contains:
            - n_links: int
            - links: list of Link
        """
        assert type(links) == list, f"The type links is not a list. Expected a list of Link, instead got '{type(links)}'."
        for link in links:
            assert type(link) == Link, f"Expected type of link to be Link, instead got '{type(link)}'."
        
        # extract relevant parameters
        self.links = links
        self.n_links = len(links)

        self.visual_mesh_types = {}
        self.collision_mesh_types = {}
        for l in links:
            self.visual_mesh_types = self._obtain_mesh_types(l.visual_geometry, self.visual_mesh_types)
            self.collision_mesh_types = self._obtain_mesh_types(l.collision_geometry, self.collision_mesh_types)        

        # Save results to pandas DataFrame
        self.df_columns_short = ["n_links", "links_names"]
        self.df_columns_full = self.df_columns_short + ["visual_geometry", "collision_geometry"]
        

        self.df_results_full = pd.DataFrame(columns=self.df_columns_full)
        self.df_results_full.loc[0, self.df_columns_full[0]] = self.n_links # get number of links
        self.df_results_full.loc[0, self.df_columns_full[1]] = [l.name for l in self.links] # get link names
        self.df_results_full.loc[0, self.df_columns_full[2]] = [{f"{l.name}_visual": l.visual_geometry.geometry_type} for l in self.links if l.visual_geometry is not None]
        self.df_results_full.loc[0, self.df_columns_full[3]] = [{f"{l.name}_collision": l.collision_geometry.geometry_type} for l in self.links if l.collision_geometry is not None]

        if len(self.visual_mesh_types) > 0:
            self.df_columns_full = self.df_columns_full + ['visual_meshes']
            self.df_results_full.loc[0, self.df_columns_full[4]] = [self.visual_mesh_types]
        if len(self.collision_mesh_types) > 0:
            self.df_columns_full = self.df_columns_full + ['collision_meshes']
            self.df_results_full.loc[0, self.df_columns_full[len(self.df_columns_full)-1]] = [self.collision_mesh_types]       

        self.df_results = self.df_results_full[self.df_results_full.columns[0:len(self.df_columns_short)]]

