import os
import logging
import unittest
from pathlib import Path

from urdf_analyzer import cli
from urdf_analyzer.constants import *



class CLITests(unittest.TestCase):


    @classmethod
    def setUpClass(self):
        """
        Runs when class is loaded.
        """
        logging.basicConfig(level=logging.ERROR)

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


    def set_model_information_arguments(self,
                    filename:str=None,
                    urdf_search_dir:str=None,
                    parser:str=None,
                    urdf_root_dir:str=None,
                    joints:bool=None,
                    links:bool=None,
                    out=None):
        subparsers,_ = cli._init_parsers()
        model_information_parser = cli._create_model_information_parser(subparsers)
        model_information_parser.logger_config = None
        model_information_parser.filename = filename
        model_information_parser.urdf_search_dir = urdf_search_dir
        model_information_parser.parser = parser
        model_information_parser.urdf_root_dir = urdf_root_dir
        model_information_parser.joints = joints
        model_information_parser.links = links
        model_information_parser.out = out
        return model_information_parser

    def test_model_information_filename_provided(self):
        parser = self.set_model_information_arguments(filename=self.working_urdf_filename,
                                                        urdf_root_dir=Path(self.urdf_files_dir, self.urdf_root_dir),
                                                        joints=True)
        urdfs_information = cli.model_information(parser)
        self.assertIsNotNone(urdfs_information)


    def test_model_information_urdf_search_dir_provided(self):
        parser = self.set_model_information_arguments(urdf_search_dir=Path(self.urdf_files_dir, self.urdf_root_dir),
                                                        joints=True)
        urdfs_information = cli.model_information(parser)
        self.assertIsNotNone(urdfs_information)
        self.assertTrue(len(urdfs_information) > 0)


    def test_model_information_filename_and_urdf_search_dir_provided(self):
        parser = self.set_model_information_arguments(filename=self.working_urdf_filename,
                                                        urdf_search_dir=Path(self.urdf_files_dir, self.urdf_root_dir),
                                                        joints=True)
        urdfs_information = cli.model_information(parser)
        self.assertIsNotNone(urdfs_information)
        self.assertTrue(len(urdfs_information) > 0)


    def test_model_information_urdf_search_dir_and_urdf_root_dir_provided(self):
        parser = self.set_model_information_arguments(urdf_root_dir=self.urdf_root_dir,
                                                        urdf_search_dir=Path(self.urdf_files_dir, self.urdf_root_dir),
                                                        joints=True)
        urdfs_information = cli.model_information(parser)
        self.assertIsNotNone(urdfs_information)
        self.assertTrue(len(urdfs_information) > 0)


    def test_model_information_out_filename_and_urdf_search_dir_provided(self):
        output_filename = "results/test_output.csv"
        parser = self.set_model_information_arguments(urdf_search_dir=Path(self.urdf_files_dir, self.urdf_root_dir),
                                                        joints=True,
                                                        out=output_filename)
        urdfs_information = cli.model_information(parser)
        self.assertIsNotNone(urdfs_information)
        self.assertTrue(len(urdfs_information) > 0)
        self.assertTrue(os.path.exists(output_filename))
        # delete the file afterwards
        os.remove(output_filename)

    def test_model_information_out_True_and_urdf_search_dir_provided(self):
        objects_in_folder_before = [name for name in os.listdir(DEFAULT_OUTPUT_DIR)]
        n_files_in_default_dir_before = len(objects_in_folder_before)
        parser = self.set_model_information_arguments(urdf_search_dir=Path(self.urdf_files_dir, self.urdf_root_dir),
                                                        joints=True,
                                                        out=True)
        _ = cli.model_information(parser)
        objects_in_folder_after = [name for name in os.listdir(DEFAULT_OUTPUT_DIR)]
        n_files_in_default_dir_after = len(objects_in_folder_after)
        self.assertEqual(n_files_in_default_dir_after, n_files_in_default_dir_before+1)
        # delete the file afterwards
        output_file = list(set(objects_in_folder_after) - set(objects_in_folder_before))
        os.remove(Path(DEFAULT_OUTPUT_DIR,output_file[0]))

