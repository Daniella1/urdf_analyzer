from pathlib import Path
import unittest
import logging
import os

from urdf_analyzer.urdf_parser import URDFparser
from urdf_analyzer import api


class APITests(unittest.TestCase):


    @classmethod
    def setUpClass(self):
        """
        Runs when class is loaded.
        """
        logging.basicConfig(level=logging.ERROR)

        # Check that the chosen parser is supported
        self.parser = 'yourdfpy' if 'yourdfpy' in URDFparser.supported_parsers else None
        if self.parser == None:
            logging.error(f"The parser 'yourdfpy' is not one of the supported parsers '{URDFparser.supported_parsers}. Stopping test.")
            return

        # Check that the directory containing URDF files for testing exists
        self.urdf_files_dir = Path("resources/urdf_files")
        if not Path(self.urdf_files_dir).exists():
            logging.error(f"The path '{Path(self.urdf_files_dir)}' to the urdf files does not exist. Stopping test.")
            return

        # Check that the path to the test URDF file exists
        self.urdf_root_dir = Path("adept_mobile_robots")
        self.working_urdf_filename = "pioneer3dx.urdf"
        if not Path(self.urdf_files_dir/self.urdf_root_dir/self.working_urdf_filename).exists():
            logging.error(f"The path '{Path(self.urdf_files_dir/self.urdf_root_dir/self.working_urdf_filename)}' to the urdf file does not exist. Stopping test.")
            return

    ############# get_model_information(...) #################

    def test_get_model_information_joints(self):
        # Run the get_model_information function
        kwargs = {'urdf_root_dir': self.urdf_files_dir/self.urdf_root_dir, 'joints': True}
        urdf_information: api.URDFInformation = api.get_model_information(parser=self.parser, filename=self.working_urdf_filename, **kwargs)
        self.assertIsNotNone(urdf_information.joint_information)
        self.assertEqual(urdf_information.joint_information.n_joints, 10)
        
    def test_get_model_information_joints_not_passed_kwarg(self):
        kwargs = {'urdf_root_dir': self.urdf_files_dir/self.urdf_root_dir}
        urdf_information: api.URDFInformation = api.get_model_information(parser=self.parser, filename=self.working_urdf_filename, **kwargs)
        self.assertIsNone(urdf_information.joint_information) # expect the joint_information is None, as the joints are not passed in the kwargs

    def test_get_model_information_filename_none_joints_not_passed_kwarg(self):
        urdf_information: api.URDFInformation = api.get_model_information(parser=self.parser, filename=None)
        self.assertIsNone(urdf_information.joint_information) # expect the joint_information is None, as the joints are not passed in the kwargs

    def test_get_model_information_filename_none_joints_passed_kwarg(self):
        kwargs = {'joints': True}
        urdf_information: api.URDFInformation = api.get_model_information(parser=self.parser, filename=None, **kwargs)
        self.assertEqual(urdf_information, api.URDFInformation()) # expect empty URDFInformation object
        self.assertIsNone(urdf_information.joint_information) # expect the joint_information is None, as the joints cannot be checked if an error has occured with the file

    ############# search_for_urdfs(...) #################

    def test_search_for_urdfs(self):
        expected_urdf_files = ['pioneer-lx-devil.urdf', 'pioneer-lx.urdf', 'pioneer3at.urdf', 'pioneer3dx.urdf']
        dir = Path(self.urdf_files_dir,self.urdf_root_dir)
        list_of_urdf_file_paths = api.search_for_urdfs(dir)
        self.assertEqual(len(list_of_urdf_file_paths), len(expected_urdf_files))
        for path, expected_file in zip(list_of_urdf_file_paths, expected_urdf_files):
            file = os.path.basename(path)
            self.assertEqual(file, expected_file)


    def test_search_for_urdfs_folder_nonexistant(self):
        dir = Path("non_existing_folder")
        list_of_urdf_file_paths = api.search_for_urdfs(dir)
        self.assertEqual(list_of_urdf_file_paths,[])

    # TODO: create a test where there are multiple directories with urdf files

    ############# get_models_information(...) #################

    def test_get_models_information(self):
        kwargs = {'joints': True}
        urdf_files = [Path("./resources/urdf_files/adept_mobile_robots/pioneer-lx-devil.urdf"),
                    Path("./resources/urdf_files/adept_mobile_robots/pioneer-lx.urdf"),
                    Path("./resources/urdf_files/adept_mobile_robots/pioneer3at.urdf"),
                    Path("./resources/urdf_files/adept_mobile_robots/pioneer3dx.urdf")]
        urdfs_information: list[api.URDFInformation] = api.get_models_information(urdf_files=urdf_files, **kwargs)
        self.assertEqual(len(urdfs_information), len(urdf_files))
        for urdf_info in urdfs_information:
            self.assertIsNotNone(urdf_info)
        

    ############# save_information(...) #################



if __name__ == '__main__':
    unittest.main()