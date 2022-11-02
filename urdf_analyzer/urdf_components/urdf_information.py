from dataclasses import dataclass
import pandas as pd

from urdf_analyzer.urdf_components.joint import JointsMetaInformation
from urdf_analyzer.urdf_components.link import LinksMetaInformation

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