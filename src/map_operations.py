from occupancy import OccupancyGrid
from plot_operations import plot_map
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
"""
This module is responsible for operations related to the OccupancyGrid map.
This includes initializing and updating the map with odometry and laser data.
"""

def initialise_map(config, odometry):
    """
    Initialises the map based on the given configuration and odometry data.
    
    :param config: The configuration dictionary.
    :param odometry: The odometry data array.
    :return: An initialised OccupancyGrid object.
    """
    probability = config["prob_occ"]
    map_x_size, map_y_size = config['map']['size']  # Map dimensions from configuration
    # Adjust odometry start position to the center of x-axis and 1/3 of y-axis
    odometry[:, 0] += map_x_size / 2
    odometry[:, 1] += map_y_size / 3
    resolution = config['map']['resolution']  # Map resolution multiplier from configuration
    map_size = [map_x_size, map_y_size]
    return OccupancyGrid(map_size, resolution, config["prob_occ"])

def process_odometry_and_laser_data(config, odometry, laser, map):
    """
    Processes odometry and laser data and updates the map.
    
    :param config: The configuration directory.
    :param odometry: The odometry data array.
    :param laser: The laser data array.
    :param map: The OccupancyGrid object to be updated.
    """
    plt.figure(1)
    plt.ion()
    laser_range = config["laser"]["max_range"]
    laser = np.clip(laser, 0, laser_range)  # Limit the sensor readings to the max range

    # Loop through each odometry and laser data point to update the map
    for i in tqdm(range(len(odometry)), desc="Processing data"):
        # Your data processing code here
        map.update(odometry[i], laser[i])
        plot_map(config, odometry, laser, map, i)