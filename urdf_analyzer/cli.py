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


def get_model_information(args):
    l = setup_logger(args)
    l.info("Obtaining model information")


    model_info_args = {'joints': True, 'filename': 'pioneer3dx.urdf', 'urdf_root_dir': 'C:\\Users\\tola\\OneDrive - Queensland University of Technology\\Desktop\\gitrepos\\urdf_analyzer\\resources\\urdf_files\\adept_mobile_robots'}
    urdf_information: api.URDFInformation = api.get_model_information(parser='yourdfpy', **model_info_args)

    return urdf_information




def create_urdf_analyzer():
    parser = argparse.ArgumentParser()
    parser.add_argument('--logger-config', type=open, help="Logger configuration file.")
    # parser.add_argument('--name', type=str, required=True)
    args = parser.parse_args()

    urdf_information: api.URDFInformation = get_model_information(args)
    print(f"urdf information {urdf_information.joint_information.joints[0].name}")





def main():
    create_urdf_analyzer()


if __name__ == '__main__':
    main()