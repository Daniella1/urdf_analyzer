import argparse
from logging.config import fileConfig
import logging
import urdf_analyzer.api as api
import sys

from urdf_analyzer.urdf_parser import URDFparser



def setup_logger(args):
    if args.logger_config is not None:
        fileConfig(args.logger_config)
    else:
        logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.WARNING)
    return logging.getLogger("urdf_analyzer")


def model_information(args):
    l = setup_logger(args)
    l.info("Obtaining model information")

    if args.urdf_search_dir is not None:
        if args.urdf_root_dir is not None:
            l.warning(f"The urdf-root-dir argument was parsed together with the urdf-search-dir. Ignoring the urdf-root-dir argument, as the tool will be searching for urdf files in the directory specified using urdf-search-dir: {args.urdf_search_dir}.")
        if args.filename is not None:
            l.warning(f"The filename argument was parsed together with the urdf-search-dir. Ignoring the filename argument, as the tool will be searching for urdf files in the directory specified using urdf-search-dir: {args.urdf_search_dir}.")

    if args.out is None and args.full is True:
        l.warning(f"The 'full' argument was provided although the 'out' was not. Ignoring the 'full' argument.") 

    if args.urdf_search_dir is not None:
        urdf_files = api.search_for_urdfs(args.urdf_search_dir)
        urdfs_information: list[api.URDFInformation] = api.get_models_information(urdf_files=urdf_files, **vars(args))
        
    elif args.filename is not None:
        urdfs_information: list[api.URDFInformation] = []
        urdfs_information.append(api.get_model_information(**vars(args)))

    if args.out is not None:
        if isinstance(args.out,str):
            api.save_information(urdfs_information, args.out, args.full)
        elif args.out is True:
            api.save_information(urdfs_information, full_results=args.full)
        
    return urdfs_information


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

    # potentially make a subparser for the joints and links, so that the user can specify if they want fully detailed results saved or not
    model_information_parser.add_argument('--joints', action='store_true', required=False, help="extract joint information: amount, types, names")
    model_information_parser.add_argument('--links', action='store_true', required=False, help="extract link information: amount, names")

    # if --out is provided with no argument, then store true, and save using default filename, otherwise if argument provided then use as filename 
    model_information_parser.add_argument('--out', required=False, action='store', const=True, nargs="?", help="The name of the output file to save the results. Will be saved as .csv by default.")
    # if --out is true, then it should be possible to specify if you want full results or not. By default the shorter version of the results will be provided. The full results can be provided, by supplying the argument --full
    # TODO: make this argument only possible if --out is specified
    model_information_parser.add_argument('--full', required=False, action='store_true', default=False, help="save full version of results")

    model_information_parser.set_defaults(analyze=model_information)

    return model_information_parser


def create_urdf_analyzer(manual_test:list=[]):
    subparsers, args_parser = _init_parsers()

    # model information
    _create_model_information_parser(subparsers)

    # Force help display when error occurrs. See https://stackoverflow.com/questions/3636967/python-argparse-how-can-i-display-help-automatically-on-error
    args_parser.usage = args_parser.format_help().replace("usage: ", "")
    
    if len(manual_test) > 0:
        args = args_parser.parse_args(manual_test)
    else:
        args = args_parser.parse_args()


        # If no arguments are passed
        if len(sys.argv) == 1:
            args_parser.print_help()
            sys.exit()

    args.analyze(args)


def main():
    manual_test_list1 = ['model-information','--joints','--links','--urdf-search-dir','./resources/urdf_files/adept_mobile_robots/','--out','--full']
    manual_test_list2 = ['model-information','--joints', '--filename', 'pioneer3dx.urdf','--urdf-root-dir','./resources/urdf_files/adept_mobile_robots/']
    create_urdf_analyzer(manual_test=[])


if __name__ == '__main__':
    main()