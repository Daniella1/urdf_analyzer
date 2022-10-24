# Script related packages
import os
from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET
from urdf_analyzer.urdf_parser import URDFparser


class URDFanalyzer:


    def __init__(self, parser: URDFparser) -> None:
        self.parser = parser



