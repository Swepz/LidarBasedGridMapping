"""
This module is responsible for reading data from files and processing it.
This includes parsing and cleaning the dataset.
"""
import numpy as np

def fetch_data_from_dataset(file_path):
    """
    Reads data from the given file_path and extracts laser and odometry data.
    
    :param file_path: The path to the data file to be read.
    :return: Two numpy arrays containing the laser data and odometry data.
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
    laser_data = []
    odometry_data = []
    
    for line in lines:
        if line.startswith('FLASER'):
            line = line.strip().split()
            num_laser_values = int(line[1])  # Extracting number of laser values
            values = line[2:]  # Extracting laser and odometry values
            laser_data.append([float(value) for value in values[:num_laser_values]])
            odometry_data.append([float(value) for value in values[num_laser_values:num_laser_values+3]])
    
    return np.array(laser_data), np.array(odometry_data)