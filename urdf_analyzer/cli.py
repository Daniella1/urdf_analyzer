import argparse
from logging.config import fileConfig
import logging
import api as api


def setup_logger(args):
    if args.logger_config is not None:
        fileConfig(args.logger_config)
    else:
        logging.basicConfig(level=logging.WARNING)
    return logging.getLogger("urdf_inspector")


def model_information(args):
    l = setup_logger(args)
    l.info("Obtaining model information")

    urdf_information: api.URDFInformation = api.get_model_information(parser='yourdfpy', **vars(args))

    print(f"urdf information {urdf_information.joint_information.joints[0].name}")

    return urdf_information



def _init_parsers():
    args_parser = argparse.ArgumentParser(add_help=True)
    args_parser.add_argument('--logger-config', type=open, help="Logger configuration file.")

    subparsers = args_parser.add_subparsers(help="Information to obtain from analysis.")
    return subparsers, args_parser

def _create_model_information_parser(subparser):
    model_information_parser = subparser.add_parser("model-information")
    model_information_parser.add_argument("--filename", required=True, type=str, help="URDF filename")
    model_information_parser.add_argument("--urdf-root-dir", required=False, type=str, help="The root directory of the URDF file.")
    model_information_parser.add_argument('--joints', action='store_true', required=False, help="extract joint information: amount, types, names")
    model_information_parser.add_argument('--links', required=False, help="extract link information: amount, names")
    model_information_parser.add_argument('--out', required=False, help="The name of the output file to save the results")

    model_information_parser.set_defaults(analyze=model_information)

    return model_information_parser


def create_urdf_analyzer(manual_test=False):
    subparsers, args_parser = _init_parsers()

    # model information
    _create_model_information_parser(subparsers)

    # Force help display when error occurrs. See https://stackoverflow.com/questions/3636967/python-argparse-how-can-i-display-help-automatically-on-error
    args_parser.usage = args_parser.format_help().replace("usage: ", "")
    
    if manual_test:
        args = args_parser.parse_args(['model-information','--joints', '--filename', 'pioneer3dx.urdf','--urdf-root-dir','./resources/urdf_files/adept_mobile_robots/'])
    else:
        args = args_parser.parse_args()

    args.analyze(args)


def main():
    create_urdf_analyzer(manual_test=True)


if __name__ == '__main__':
    main()