import argparse
from logging.config import fileConfig
import logging


def setup_logger(args):
    if args.logger_config is not None:
        fileConfig(args.logger_config)
    else:
        logging.basicConfig(level=logging.WARNING)
    return logging.getLogger("urdf_analyzer")


def analyze_abc(args):
    l = setup_logger(args)
    l.info("Analyzing abc")



def create_urdf_analyzer():
    analyze_abc()


def main():
    create_urdf_analyzer()


if __name__ == '__main__':
    main()