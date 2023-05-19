import logging
from pathlib import Path
from src.config_parser import load_config
from src.data_processing import fetch_data_from_dataset
from src.map_operations import initialise_map
from src.map_operations import process_odometry_and_laser_data

CONFIG_FILENAME = "config/config.yaml"

def main():
    # Ensure the configuration file exists
    config_path = Path(CONFIG_FILENAME)
    if not config_path.is_file():
        logging.error(f'Config file {config_path} does not exist')
        return

    # Load configuration and dataset
    config = load_config(config_path)
    laser, odometry = fetch_data_from_dataset(config["dataset"])
    
    # Initialise the map and process the data
    map = initialise_map(config, odometry)
    process_odometry_and_laser_data(config, odometry, laser, map)

if __name__ == '__main__':
    main()