import argparse
from logging.config import fileConfig
import logging
import api as api

from urdf_parser import URDFparser


def setup_logger(args):
    if args.logger_config is not None:
        fileConfig(args.logger_config)
    else:
        logging.basicConfig(level=logging.WARNING)
    return logging.getLogger("urdf_inspector")


def model_information(args):
    l = setup_logger(args)
    l.info("Obtaining model information")

    if args.urdf_search_dir is not None and args.urdf_root_dir is not None:
        l.warning(f"The urdf-root-dir argument was parsed together with the urdf-search-dir. Ignoring the urdf-root-dir argument, as the tool will be searching for urdf files in the directory specified using urdf-search-dir: {args.urdf_search_dir}.")


    if args.filename is not None:
        urdf_information: api.URDFInformation = api.get_model_information(**vars(args))
        print(f"urdf information {urdf_information.joint_information.joints[0].name}")
    elif args.urdf_search_dir is not None:
        urdf_files = api.search_for_urdfs(args.urdf_search_dir)
        urdfs_information: list[api.URDFInformation] = api.get_models_information(urdf_files=urdf_files, **vars(args))
        print(f"urdf information {urdfs_information[0].joint_information.joints[0].name}")
        print(f"len(urdfs_information): {len(urdfs_information)}")




def _init_parsers():
    args_parser = argparse.ArgumentParser(add_help=True)
    args_parser.add_argument('--logger-config', type=open, help="Logger configuration file.")

    subparsers = args_parser.add_subparsers(help="Information to obtain from analysis.")
    return subparsers, args_parser

def _create_model_information_parser(subparser):
    model_information_parser = subparser.add_parser("model-information")

    group = model_information_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--filename', type=str, help="URDF filename.")
    group.add_argument('--urdf-search-dir', type=str, help="The directory to perform a recursive search for URDF files and pass them for analysis.")
    

    model_information_parser.add_argument('--parser', required=False, default=URDFparser.supported_parsers[0], help=f"the urdf parser to use. Choose from: {URDFparser.supported_parsers}")
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
    create_urdf_analyzer(manual_test=False)


if __name__ == '__main__':
    main()