from logging import Logger
from pathlib import Path
import subprocess
import os

import matlab.engine
eng = matlab.engine.start_matlab()


class URDFparser:

    supported_parsers = ['yourdfpy','urdfpy','pybullet','roboticstoolbox','matlab','check_urdf'] 


    def _set_default_parser(self):
        default_parser = self.supported_parsers[0]
        import yourdfpy
        self.parser[default_parser] = yourdfpy

    def __init__(self, parser: str, logger: Logger):
        self.logger = logger
        assert len(self.supported_parsers) == len(set(self.supported_parsers)), f"The list of parsers ({self.supported_parsers}) contains duplicates. Each parser should be unique." # should mathematically be a set, as we do not want duplicates
        if parser not in self.supported_parsers:
            self.logger.error(f"The chosen parser '{parser}' is not currently supported. Please choose a parser that is supported from: '{self.supported_parsers}'")
            return
            # TODO: do something other than just return
        self.parser = {}
        if parser == 'yourdfpy':
            import yourdfpy
            self.parser[parser] = yourdfpy
        elif parser == 'urdfpy':
            import urdfpy
            self.parser[parser] = urdfpy
        elif parser == 'roboticstoolbox':
            import roboticstoolbox as rtb
            self.parser[parser] = rtb
        elif parser == 'matlab':
            try:
                self.parser[parser] = eng
            except ImportError as e:
                self.logger.error(f"The matlab engine for python is not installed. Skipping it, and defaulting to {self.supported_parsers[0]}")
                self._set_default_parser()

        elif parser == 'check_urdf':
            self.parser[parser] = 'check_urdf'

        elif parser == 'pybullet':
            import pybullet
            pybullet.connect(pybullet.DIRECT)
            self.parser[parser] = pybullet

        self._set_urdf_loader()



    # programmed as a function instead of just defining in a dictionary with the supported_parser, since some parsers may require multiple steps for parsing urdf files
    def _set_urdf_loader(self):
        parser = list(self.parser.keys())[0]
        # yourdfpy
        if 'yourdfpy' == parser:
            self.urdf_loader = self.parser[parser].URDF.load
        # urdfpy
        elif 'urdfpy' == parser:
            self.urdf_loader = self.parser[parser].URDF.load
        # roboticstoolbox
        elif 'roboticstoolbox' == parser:
            self.urdf_loader = self.parser[parser].ERobot.URDF
        # matlab
        elif 'matlab' == parser:
            self.urdf_loader = self.parser[parser].importrobot
        # urdfdom check_urdf
        elif 'check_urdf' == parser:
            def check_urdf(filename):
                res = subprocess.run(f'check_urdf {filename}', shell=True, capture_output=True, text=True)
                if res.returncode == 0: # success
                    return res.stdout
                else:
                    return None
            self.urdf_loader = lambda filename : check_urdf(filename)
        # pybullet
        elif 'pybullet' == parser:
            def parse_urdf(filename):
                try:
                    res = self.parser[parser].loadURDF(filename)
                    return res
                except:
                    return None
            self.urdf_loader = lambda filename : parse_urdf(filename)
        return self.urdf_loader

    
    def load_urdf(self, filename: str, urdf_root_dir: str=None):
        root_dir = os.getcwd()
        basename = os.path.abspath(filename)
        if urdf_root_dir is None:
            urdf_root_dir = os.path.dirname(basename)
        filename_only = os.path.basename(basename)
        try:
            os.chdir(urdf_root_dir)
            self.logger.info(f"Trying to load urdf file: {urdf_root_dir}/{filename_only}")
            model = self.urdf_loader(str(Path(urdf_root_dir,filename_only)))
            self.logger.info(f"Successfully loaded {urdf_root_dir}/{filename_only} using the urdf loader {list(self.parser.keys())[0]}")
        except:
            self.logger.warning(f"Failed to load {urdf_root_dir}/{filename_only}")
            model = None
            pass
        os.chdir(root_dir)
        return model