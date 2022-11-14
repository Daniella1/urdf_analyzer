import argparse
from logging.config import fileConfig
import logging
import sys

import urdf_analyzer.api as api
from urdf_analyzer.urdf_parser import URDFparser


# TODO: remove when finished implementing
import warnings
warnings.filterwarnings('ignore')

def setup_logger(args):
    if args.logger_config is not None:
        fileConfig(args.logger_config)
    else:
        logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.ERROR)
    return logging.getLogger("urdf_analyzer")


def _validate_common_args(args, l):
    if args.urdf_search_dir is not None:
        if args.urdf_root_dir is not None:
            l.warning(f"The urdf-root-dir argument was parsed together with the urdf-search-dir. Ignoring the urdf-root-dir argument, as the tool will be searching for urdf files in the directory specified using urdf-search-dir: {args.urdf_search_dir}.")
        if args.filename is not None:
            l.warning(f"The filename argument was parsed together with the urdf-search-dir. Ignoring the filename argument, as the tool will be searching for urdf files in the directory specified using urdf-search-dir: {args.urdf_search_dir}.")


def generate_schemas(args):
    l = setup_logger(args)
    l.info("Generating schemas")

    _validate_common_args(args, l)


    if 'duplicates-cmp' in args.generate_schema and (args.duplicates_dir is None):
        l.error(f"The 'duplicates-cmp' is provided without the 'duplicates-dir'. Please provide the duplicates directory. Exiting.")
        return
    if 'dup-cmp-parser' in args.generate_schema and ('duplicates-cmp' not in args.generate_schema):
        l.warning(f"The 'dup-cmp-parser' argument is provided without the 'duplicates-cmp' argument. Ignoring.")
    if 'dup-cmp-sources' in args.generate_schema and ('duplicates-cmp' not in args.generate_schema):
        l.warning(f"The 'dup-cmp-sources' argument is provided without the 'duplicates-cmp' argument. Ignoring.")
    if args.duplicates_dir is not None:
        l.warning(f"The 'duplicates-dir' argument is provided without the 'duplicates-cmp' argument. Ignoring.")

    urdf_files = None
    if args.urdf_search_dir is not None:
        urdf_files = api.search_for_urdfs(args.urdf_search_dir)
        l.info(f"Found {len(urdf_files)} urdf files in the search directory {args.urdf_search_dir}")
    elif args.filename is not None:
        urdf_files = args.filename
    
    api.schema_generator(args.generate_schema, urdf_files, **vars(args))


    # TODO: if the user specifies out then they have to do this for each schema they want to generate



def model_information(args):
    l = setup_logger(args)
    l.info("Obtaining model information")

    _validate_common_args(args, l)

    if args.out is None and args.full is True:
        l.warning(f"The 'full' argument was provided although the 'out' was not. Ignoring the 'full' argument.") 

    if args.urdf_search_dir is not None:
        urdf_files = api.search_for_urdfs(args.urdf_search_dir)
        l.info(f"Found {len(urdf_files)} urdf files in the search directory {args.urdf_search_dir}")
        urdfs_information: list[api.URDFInformation] = api.get_models_information(urdf_files=urdf_files, **vars(args))
        
    elif args.filename is not None:
        urdfs_information: list[api.URDFInformation] = []
        urdfs_information.append(api.get_model_information(**vars(args)))

    if args.out is not None:
        if isinstance(args.out,str):
            api.save_model_information(urdfs_information, args.out, args.full)
        elif args.out is True:
            api.save_model_information(urdfs_information, full_results=args.full)

        
    return urdfs_information


def parsing_information(args):
    l = setup_logger(args)
    l.info("Obtaining parsing information")

    _validate_common_args(args, l)

    if args.parser is not None and args.parser not in URDFparser.supported_parsers:
        l.error(f"The provided parser: '{args.parser}' is not currently supported. The supported parsers are: '{URDFparser.supported_parsers}'. Exiting.")
        return None

    if args.all_parsers:
        parser = URDFparser.supported_parsers
    elif args.parser is not None:
        parser = args.parser

    if args.urdf_search_dir is not None:
        urdf_files = api.search_for_urdfs(args.urdf_search_dir)
        l.info(f"Found {len(urdf_files)} urdf files in the search directory {args.urdf_search_dir}")
        parsing_results = api.get_parsings_information(urdf_files, parser)

    elif args.filename is not None:
        parsing_results = api.get_parsing_information(args.filename, parser, args.urdf_root_dir)

    if args.out is not None:
        if isinstance(args.out,str):
            api.save_parsing_information(parsing_results, args.out)
        elif args.out is True:
            api.save_parsing_information(parsing_results)

    return parsing_results



def _init_parsers():
    args_parser = argparse.ArgumentParser(add_help=True, allow_abbrev=False)
    args_parser.add_argument('--logger-config', type=open, help="Logger configuration file.")

    subparsers = args_parser.add_subparsers(help="Information to obtain from analysis.")
    return subparsers, args_parser

def _add_common_arguments(subparser):
    group = subparser.add_mutually_exclusive_group(required=True)
    group.add_argument('--filename', type=str, help="URDF filename.")
    group.add_argument('--urdf-search-dir', type=str, help="The directory to perform a recursive search for URDF files and pass them for analysis.")

    subparser.add_argument("--urdf-root-dir", required=False, type=str, help="The root directory of the URDF file.")
    # if --out is provided with no argument, then store true, and save using default filename, otherwise if argument provided then use as filename 
    subparser.add_argument('--out', required=False, action='store', const=True, nargs="?", help="The name of the output file to save the results. Will be saved as .csv by default.")


def _create_model_information_parser(subparser):
    model_information_parser = subparser.add_parser("model-information", allow_abbrev=False)

    _add_common_arguments(model_information_parser)
    
    # potentially make a subparser for the joints and links, so that the user can specify if they want fully detailed results saved or not
    model_information_parser.add_argument('--joints', action='store_true', required=False, help="extract joint information: amount, types, names")
    model_information_parser.add_argument('--links', action='store_true', required=False, help="extract link information: amount, names")

    # if --out is true, then it should be possible to specify if you want full results or not. By default the shorter version of the results will be provided. The full results can be provided, by supplying the argument --full
    # TODO: make this argument only possible if --out is specified
    model_information_parser.add_argument('--full', required=False, action='store_true', default=False, help="save full version of results")

    model_information_parser.set_defaults(analyze=model_information)

    return model_information_parser

def _create_parsing_information_parser(subparser):
    parsing_information_parser = subparser.add_parser("parsing-information", allow_abbrev=False)

    _add_common_arguments(parsing_information_parser)

    group = parsing_information_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--parser', choices=URDFparser.supported_parsers, nargs="+", help=f"The urdf parser to use. Choose from: {URDFparser.supported_parsers}")
    group.add_argument('--all-parsers', action='store_true', help=f"Try parsing the urdf files with all the supported parsers: '{URDFparser.supported_parsers}'")

    parsing_information_parser.set_defaults(analyze=parsing_information)

    return parsing_information_parser    


def create_generate_schemas_parser(subparser):
    generate_schemas_parser = subparser.add_parser("generate-schemas", allow_abbrev=False)

    # TODO: fix
    # group = generate_schemas_parser.add_mutually_exclusive_group(required=True)
    # group.add_argument('--filename', type=str, help="URDF filename.")
    # group.add_argument('--urdf-search-dir', type=str, help="The directory to perform a recursive search for URDF files and pass them for analysis.")
    generate_schemas_parser.add_argument('--filename', type=str, help="URDF filename.")
    generate_schemas_parser.add_argument('--urdf-search-dir', type=str, help="The directory to perform a recursive search for URDF files and pass them for analysis.")
    generate_schemas_parser.add_argument("--urdf-root-dir", required=False, type=str, help="The root directory of the URDF file.")

    generate_schemas_parser.add_argument("generate_schema", choices=['tool-cmp','model-info','urdf-parse-cmp','duplicates-cmp'], default=[None, None, None, None], nargs="+", help=f"the types of schemas that can be generated.") # TODO: fix help description
    generate_schemas_parser.add_argument("--out-dir", type=str, required=False, help=f"The output directory for the generated schemas.")
    generate_schemas_parser.add_argument("--duplicates-dir", type=str, required=False, help="The directory where the duplicate urdf files are. Required only when 'duplicates-cmp' is provided.")
    generate_schemas_parser.add_argument("--dup-cmp-parser", type=str, required=False, help=f"The parser to run the duplicate urdf files through. Can choose from {URDFparser.supported_parsers}, or can also choose 'all' to run the files through each supported parser.")
    generate_schemas_parser.add_argument("--dup-cmp-sources", type=str, required=False, nargs="+", help="The sources you would like to compare the duplicates against.")
    # TODO: add argument duplicates-subdir, in case you only want to compare one robot
    generate_schemas_parser.set_defaults(analyze=generate_schemas)

    return generate_schemas_parser


def create_urdf_analyzer(manual_test:list=[]):
    subparsers, args_parser = _init_parsers()

    # model information
    _create_model_information_parser(subparsers)

    # parsing information
    _create_parsing_information_parser(subparsers)

    # generate schemas
    create_generate_schemas_parser(subparsers)

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
    manual_test_list3 = ['model-information','--filename','pioneer3dx.urdf','--urdf-root-dir','resources/urdf_files/adept_mobile_robots','--out','--full', '--joints']
    manual_test_list4 = ['parsing-information','--filename','pioneer3dx.urdf','--urdf-root-dir','resources/urdf_files/adept_mobile_robots','--parser','yourdfpy']
    manual_test_list5 = ['parsing-information','--filename','pioneer3dx.urdf','--urdf-root-dir','resources/urdf_files/adept_mobile_robots','--all-parsers','--out']
    manual_test_list6 = ['parsing-information','--urdf-search-dir','./resources/urdf_files/adept_mobile_robots/','--all-parsers','--out']
    manual_test_list7 = ['generate-schemas', 'model-info', '--urdf-search-dir','resources/urdf_files']
    manual_test_list8 = ['generate-schemas','tool-cmp', '--urdf-search-dir', 'resources/urdf_files']
    manual_test_list9 = ['generate-schemas','duplicates-cmp', '--duplicates-dir', 'resources/urdf_files_dataset/duplicates']
    manual_test_list10 = ['generate-schemas','model-info', 'tool-cmp', 'urdf-parse-cmp','duplicates-cmp','--urdf-search-dir', 'resources/urdf_files', '--duplicates-dir', 'resources/urdf_files_dataset/duplicates']
    manual_test_list11 = ['generate-schemas','urdf-parse-cmp', '--urdf-search-dir', 'resources/urdf_files']
    manual_test_list12 = ['generate-schemas','tool-cmp', '--urdf-search-dir', 'resources/urdf_files_dataset/urdf_files/random']
    manual_test_list13 = ['generate-schemas','duplicates-cmp', '--duplicates-dir', 'resources/urdf_files_dataset/duplicates','--dup-cmp-sources','matlab','ros-industrial']
    # TODO: add warning if the urdf search is done in a non-existing directory
    create_urdf_analyzer(manual_test=[])


if __name__ == '__main__':
    main()