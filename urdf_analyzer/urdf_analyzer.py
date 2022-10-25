# Script related packages
import os
from pathlib import Path
import pandas as pd
from logging import Logger
from urdf_parser import URDFparser
from model_analysis import ModelAnalysis


class URDFanalyzer:


    def __init__(self, logger: Logger, parser: URDFparser) -> None:
        self.logger = logger
        self.parser = parser
        self.model_analysis = ModelAnalysis(self.logger)


    def get_joint_information(self, filename: str, urdf_root_dir:str=None):
        return self.model_analysis.get_joint_information(filename, urdf_root_dir)

    

