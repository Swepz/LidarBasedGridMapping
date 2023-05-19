"""
This is a script to process odometry and laser data, and plot the results using an Occupancy Grid map.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import logging
from pathlib import Path
from src.config_parser import load_config
from src.occupancy import OccupancyGrid

CONFIG_FILENAME = "config/config.yaml"

def main():
    # Ensure the configuration file exists
    config_path = Path(CONFIG_FILENAME)
    if not config_path.is_file():
        logging.error(f'Config file {config_path} does not exist')
        return

    # Load configuration and dataset
    config = load_config(config_path)
    odometry = np.genfromtxt(config["datasets"]['odom'], delimiter=',')
    laser = np.genfromtxt(config["datasets"]['flaser'], delimiter=',')

    # Initialise the map and process the data
    map = initialise_map(config, odometry)
    process_odometry_and_laser_data(config, odometry, laser, map)

def initialise_map(config, odometry):
    """
    Initialises the map based on the given configuration and odometry data.

    :param config: configuration dictionary.
    :param odometry: odometry data array.
    :return: initialised OccupancyGrid object.
    """
    probability = config["prob_occ"]
    laser_range = config["laser"]["max_range"]
    map_x_size, map_y_size = config['map']['size']  # Map dimensions from configuration
    # Adjust odometry start position to the center of x-axis and 1/3 of y-axis
    odometry[:, 0] += map_x_size / 2
    odometry[:, 1] += map_y_size / 3
    resolution = config['map']['resolution']  # Map resolution multiplier from configuration
    map_size = [map_x_size, map_y_size]
    return OccupancyGrid(map_size, resolution, probability)

def process_odometry_and_laser_data(config, odometry, laser, map):
    """
    Processes odometry and laser data and updates the map.

    :param config: configuration directory
    :param odometry: odometry data array.
    :param laser: laser data array.
    :param map: OccupancyGrid object to be updated.
    """
    plt.figure(1)
    plt.ion()
    laser_range = config["laser"]["max_range"]
    laser = np.clip(laser, 0, laser_range)  # Limit the sensor readings to the max range

    # Loop through each odometry and laser data point to update the map
    for i in range(len(odometry)):
        map.update(odometry[i], laser[i])
        plot_map(config, odometry, laser, map, i)

def plot_map(config, odometry, laser, map, i):
    """
    Plots the map after processing each odometry and laser data point. 
    After drawing all robot positions and maps, it saves the figure to a specified file.

    :param config: configuration directory
    :param odometry: The odometry data array.
    :param laser: The laser data array.
    :param map: The OccupancyGrid object to be plotted.
    :param i: The current index in the odometry and laser data arrays.
    """
    resolution = config['map']['resolution']
    plt.clf()  # Clear the current figure.

    # Create a wedge (half-circle) representing the LIDAR's field of view
    pos = odometry[i] * resolution # Compute the robot's position with the resolution taken into account.
    theta = odometry[i, 2]  # Robot's heading angle

    # Adjust the radius of the wedge according to the resolution
    wedge_radius = config["laser"]["max_range"] * resolution

    lidar_fov = patches.Wedge(center=(pos[0], pos[1]), r=wedge_radius, 
                              theta1=np.degrees(theta - np.pi/2), 
                              theta2=np.degrees(theta + np.pi/2), 
                              color=config['plot']['lidar_color'], alpha=config['plot']['lidar_alpha'])  
    
    # Create a circle representing the robot.
    rob = patches.Circle((pos[0], pos[1]), resolution, fc=config['plot']['robot_color'])  

    plt.gca().add_patch(lidar_fov)
    plt.gca().add_patch(rob)

    # Display the occupancy grid map with a grayscale colormap, origin at the lower left corner.
    plt.imshow(map.fetch_prob_map().T, cmap='gray', origin='lower')
    plt.pause(config['plot']['liveplot_speed'])  # Pause to update the figure.

    if i == len(odometry) - 1:  # If it is the last iteration, save the figure.
        plt.savefig(config['plot']['plot_output_filename'])  # Save the figure to a file.

if __name__ == '__main__':
    main()