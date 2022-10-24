from logging import Logger
import os

class URDFparser:


    def __init__(self, parser: str, logger: Logger):
        self.logger = logger
        self.supported_parsers = ['yourdfpy','urdfpy','roboticstoolbox'] 
        assert len(self.supported_parsers) == len(set(self.supported_parsers)), f"The list of parsers ({self.supported_parsers}) contains duplicates. Each parser should be unique." # should mathematically be a set, as we do not want duplicates
        if parser not in self.supported_parsers:
            self.logger.error(f"The chosen parser '{parser}' is not currently supported. Please choose a parser that is supported from: '{self.supported_parsers}'")
            return
            # TODO: do something other than just return
        if parser == self.supported_parsers[0]:
            import yourdfpy
            self.parser[parser] = yourdfpy
        elif parser == self.supported_parsers[1]:
            import urdfpy
            self.parser[parser] = urdfpy
        elif parser == self.supported_parsers[2]:
            import roboticstoolbox as rtb
            self.parser[parser] = rtb
        # elif parser == self.supported_parsers[3]:
        #     import matlab.engine
        #     eng = matlab.engine.start_matlab()
        #     self.parser[parser] = eng
        self._parser_load_urdf()
        return self.parser




    def _parser_load_urdf(self):
        # yourdfpy
        if self.supported_parsers[0] == self.parser.keys()[0]:
            self.urdf_loader = self.parser[self.supported_parsers[0]].URDF.load
        # urdfpy
        elif self.supported_parsers[1] == self.parser.keys()[0]:
            self.urdf_loader = self.parser[self.parser.keys()[0]].URDF.load
        # roboticstoolbox
        elif self.supported_parsers[2] == self.parser.keys()[0]:
            self.urdf_loader = self.parser[self.parser.keys()[0]].ERobot.URDF
        # matlab
        # elif self.supported_parsers[3] == self.parser.keys()[0]:
        #     self.urdf_loader = self.parser[self.parser.keys()[0]].importrobot
        return self.urdf_loader


    
    def load_urdf(self, filename: str, urdf_root_dir: str=None):
        root_dir = os.getcwd()
        basename = os.path.abspath(filename)
        if urdf_root_dir is None:
            urdf_root_dir = os.path.dirname(basename)
        filename_only = os.path.basename(basename)
        try:
            os.chdir(urdf_root_dir)
            model = self.urdf_loader(urdf_root_dir + "/" + filename_only)
            self.logger.debug(f"Successfully loaded {basename} using the urdf loader {self.parser.keys()[0]}")
        except:
            self.logger.error(f"Failed to load {basename}")
            model = None
            pass
        os.chdir(root_dir)
        return model