import yaml
from pathlib import Path
import logging

def load_config(config_filename: Path):
    """
    Load the main config file for all settings.

    Parameters:
    config_filename (Path): The file path of the configuration file.

    Returns:
    dict: Parsed YAML file as a dictionary.
    """
    try:
        with open(config_filename, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"File {config_filename} not found.")
        return None
    except yaml.YAMLError as exc:
        logging.error(f"Error in configuration file: {exc}")
        return None
