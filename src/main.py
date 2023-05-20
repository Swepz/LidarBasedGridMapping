import logging
from config_parser import load_config
from data_processing import fetch_data_from_dataset
from map_operations import initialise_map
from map_operations import process_odometry_and_laser_data
from pathlib import Path

# Get the directory of the current script
parent_dir = Path(__file__).resolve().parent.parent

# Construct the path to the config file
CONFIG_FILENAME = parent_dir / "config" / "config.yaml"

def main():
    # Ensure the configuration file exists
    config_path = Path(CONFIG_FILENAME)
    if not config_path.is_file():
        logging.error(f'Config file {config_path} does not exist')
        return

    # Load configuration and dataset
    config = load_config(config_path)
    dataset_path = parent_dir / config["dataset"]["dir"] / config["dataset"]["map1"]
    laser, odometry = fetch_data_from_dataset(dataset_path)

    # Initialise the map and process the data
    map = initialise_map(config, odometry)
    process_odometry_and_laser_data(config, odometry, laser, map)

if __name__ == '__main__':
    main()