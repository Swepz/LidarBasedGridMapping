import numpy as np

class OccupancyGrid:
    """Represents an occupancy grid for robotic mapping."""

    def __init__(self, map_size, res, probability):
        """
        Initializes the occupancy grid.
        
        :param map_size: A 2-element list specifying the size of the map.
        :param res: The map resolution (size of each grid cell).
        :param probability: The initial probability for each cell.
        """
        self.res = res
        self.prob = probability
        self.log_prob_map = np.zeros([map_size[0] * res + 1, map_size[1] * res + 1], dtype=float)

    def fetch_prob_map(self):
        """
        Returns the current map represented as probabilities.
        
        :return: A 2D numpy array of probabilities.
        """
        return 1 - 1 / (1 + np.exp(self.log_prob_map))

    def add_prob(self, occupied):
        """
        Returns the log odds for a cell being occupied or free.

        :param occupied: A boolean indicating if the cell is occupied (True) or free (False).
        :return: Log odds of the cell being occupied or free.
        """
        A, B = self.prob, 1 - self.prob
        return np.log(A / B) if not occupied else np.log(B / A)

    def cells_between_points(self, x0, y0, x1, y1):
        """
        Returns the grid cells between two points.
        
        :param x0, y0: The coordinates of the first point.
        :param x1, y1: The coordinates of the second point.
        :return: A list of grid cells between the two points.
        """
        # Compute absolute differences between the two points
        p0, p1 = np.abs(np.diff([[x0, y0], [x1, y1]], axis=0))[0]

        # Determine the cells between the two points based on the larger difference
        if p0 >= p1: 
            return np.c_[np.linspace(x0, x1, p0), np.round(np.linspace(y0, y1, p0))]
        else:
            return np.c_[np.round(np.linspace(x0, x1, p1)), np.linspace(y0, y1, p1)]

    def laser_sweep(self, xi, zi):
        """
        Performs a laser sweep around the current robot pose.

        :param xi: The current pose of the robot.
        :param zi: The laser readings.
        :return: A list of points where the laser hits.
        """
        theta = np.linspace(-np.pi/2, np.pi/2, len(zi), axis=-1)
        return [xi[0] + zi * np.cos(xi[2] + theta), xi[1] + zi * np.sin(xi[2] + theta)]

    def check_cells(self, xi, zi):
        """
        Checks if the cells are occupied or free based on the laser sweep.

        :param xi: The current pose of the robot.
        :param zi: The laser readings.
        :return: A list of occupied cells and a list of free cells.
        """
        # Round the laser readings to get the occupied cells
        occ = np.round(np.array(self.laser_sweep(xi, zi)) * self.res).astype(int)

        # Round the robot pose to get the current cell
        xi = np.round(xi * self.res).astype(int)

        # Initialize a list of free cells
        free = np.array([[xi[0], xi[0]], [xi[1], xi[1]]])

        # Add all cells between the robot and each occupied cell to the list of free cells
        for i in range(len(occ[1])):
            free = np.append(free, self.cells_between_points(xi[0], xi[1], occ[0][i], occ[1][i]), axis=0)
        
        # Convert the list of free cells to the correct format
        free = np.array(free, dtype=int).T
        return occ, free

    def update(self, xi, zi):
        """
        Updates the map based on new laser readings.

        :param xi: The current pose of the robot.
        :param zi: The laser readings.
        """
        occ, free = self.check_cells(xi, zi)
        self.log_prob_map[occ[0], occ[1]] += self.add_prob(occupied=True)
        self.log_prob_map[free[0], free[1]] += self.add_prob(occupied=False)
