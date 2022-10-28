from dataclasses import dataclass
from urdf_analyzer.urdf_standard import JointStandard
import pandas as pd

# following the standard defined in: https://wiki.ros.org/urdf/XML/joint

@dataclass
class Joint:

    def __init__(self, name: str, jtype: str):
        """
        A joint element has two attributes: name and type.

        :param name: Specifies a unique name of the joint 
        :type name: str
        :param type: Specifies the type of joint
        :type type: str
        :raises AssertionError: if the specified type is not part of the URDF standard
        """
        self.name = name
        assert jtype in JointStandard.joint_types, f"The type '{jtype}' of the joint '{name}' is not part of the defined URDF standard for joints. The allowed joints types from the standard are '{JointStandard.joint_types}'"
        self.type = jtype


    def get_explanantion_of_type(self):
        return JointStandard.joint_types_and_explanations[self.type]


# joints have types
# number of joints
# names of joints
# number of different joint types
# locations of joints ? 


@dataclass
class JointsMetaInformation:


    def __init__(self, joints: list[Joint]):
        """
        
        returns self, which contains:
            - n_joints: int
            - joints: list of Joint
            - n_joint_types: dict of joint type in keys and number of that type in values
        """
        assert type(joints) == list, f"The type joints is not a list. Expected a list of Joint, instead got '{type(joints)}'."
        for joint in joints:
            assert type(joint) == Joint, f"Expected type of joint to be Joint, instead got '{type(joint)}'."
        self.joints = joints
        self.n_joints = len(joints)
        self.n_joint_types = {}
        for joint_type in JointStandard.joint_types:
            self.n_joint_types[joint_type] = len([j for j in joints if j.type == joint_type])

        
        # Save results to pandas DataFrame
        self.df_columns_short = ["n_joints", "joint_names", "joint_types"]
        self.df_columns_full = self.df_columns_short + [f"n_{j}_joints" for j in JointStandard.joint_types]
        
        # self.df_results = pd.DataFrame(columns=self.df_columns_short)
        self.df_results_full = pd.DataFrame(columns=self.df_columns_full)
        self.df_results_full.loc[0, self.df_columns_full[0]] = self.n_joints # get number of joints
        self.df_results_full.loc[0, self.df_columns_full[1]] = [j.name for j in self.joints] # get joint names
        self.df_results_full.loc[0, self.df_columns_full[2]] = [j.type for j in self.joints] # get joint types
        for i in range(len(self.df_columns_short), len(self.df_columns_full)):
            self.df_results_full.loc[0, self.df_columns_full[i]] = self.n_joint_types[self.df_columns_full[i][2:-7]] # get number of joints of different types by slicing the name from the saved column names, i.e. remove 'n_' and '_joints'

        self.df_results = self.df_results_full[self.df_results_full.columns[0:len(self.df_columns_short)]]


        
