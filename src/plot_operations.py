import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np
from pathlib import Path
"""
This module is responsible for operations related to plotting.
This includes generating a plot based on the OccupancyGrid map and data.
"""

def plot_map(config, odometry, laser, map, i):
    """
    Plots the map after processing each odometry and laser data point.
    
    :param config: The configuration directory.
    :param odometry: The odometry data array.
    :param laser: The laser data array.
    :param map: The OccupancyGrid object to be plotted.
    :param i: The current index in the odometry and laser data arrays.
    """
    parent_dir = Path(__file__).resolve().parent.parent
    output_name = parent_dir / config['plot']['plot_output_filename']
    resolution = config['map']['resolution']
    plt.clf()  # Clear the current figure.

    # Set plot limits based on the map size
    plt.xlim(0, config['map']['size'][0] * resolution)
    plt.ylim(0, config['map']['size'][1] * resolution)

    if i != len(odometry) - 1:  # If it's not the last iteration, plot the robot and Lidar.
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
        print("Saving the figure to path {}".format(output_name))
        plt.savefig(output_name)  # Save the figure to a file.