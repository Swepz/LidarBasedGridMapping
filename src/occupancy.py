import numpy as np

class OccupancyGrid:
    """Represents an occupancy grid for robotic mapping."""

    def __init__(self, map_size, config):
        """
        Initializes the occupancy grid.
        :param config: The configuration dictionary.
        :param map_size: The size of the map.
        """
        self.config = config
        self.resolution = self.config["map"]["resolution"]
        self.probability = self.config["map"]["prob_occ"]
        self.log_prob_map = np.zeros([map_size[0] * self.resolution + 1, map_size[1] * self.resolution + 1], dtype=float)

    def fetch_prob_map(self):
        """
        Converts the map from log odds representation to probabilities and returns it.

        This function applies the inverse of the log odds function to the map's log odds representation. 
        This transforms the map back into probabilities of cells being occupied. Each cell's value 
        represents the probability that the cell is occupied, ranging from 0 (certainly not occupied) to 
        1 (certainly occupied).

        The conversion is done using the logistic function, which is the inverse of the logit function 
        used to calculate log odds. The logistic function is defined as:

            f(x) = 1 / (1 + e^-x)

        where `x` is the log odds value. This function takes a real-valued input (the log odds) and 
        outputs a value between 0 and 1 (the probability).

        :return: A 2D numpy array where each cell's value is the probability that the cell is occupied.
        """
        log_odds_min = self.config['map']['log_odds_min']
        log_odds_max = self.config['map']['log_odds_max']
        clipped_log_odds = np.clip(self.log_prob_map, log_odds_min, log_odds_max)
        return 1 - 1 / (1 + np.exp(clipped_log_odds))

    def add_prob(self, occupied):
        """
        Returns the log odds for a cell being occupied or free.

        :param occupied: A boolean indicating if the cell is occupied (True) or free (False).
        :return: Log odds of the cell being occupied or free.
        """
        A, B = self.probability, 1 - self.probability
        return np.log(A / B) if not occupied else np.log(B / A)

    def bresenham_line(self, x0, y0, x1, y1):
        """
        Returns the grid cells between two points in the occupancy grid map using the Bresenham's line algorithm.

        :param x0, y0: The coordinates of the first point.
        :param x1, y1: The coordinates of the second point.

        :return: A 2D array where each row represents the (x, y) coordinates of a cell in the occupancy 
                grid that lies on the line between the start and end point.
        """
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                points.append((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                points.append((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy        
        points.append((x, y))
        return np.array(points)
        
    def laser_sweep(self, xi, zi):
        """
        Performs a laser sweep around the current robot pose.

        This function converts each laser reading from polar coordinates (distance, angle) 
        relative to the robot's current position and orientation, to global Cartesian coordinates (x, y). 

        The output is a 2D array where each column represents a point (x, y) in the global frame 
        where a laser beam has hit an obstacle.

        :param xi: The current pose of the robot, represented as a 1D array [x, y, theta].
                    x, y are the coordinates in the global frame and theta is the orientation of the robot.

        :param zi: The laser readings, represented as a 1D array. Each element of the array represents 
                    the distance from the robot to an obstacle at a specific angle. The angles are assumed 
                    to be evenly distributed in the range (-pi/2, pi/2).

        :return: A 2D array where each column is a point (x, y) in the global frame where a laser beam hit an obstacle.
        """
        theta = np.linspace(-np.pi/2, np.pi/2, len(zi), axis=-1)
        return [xi[0] + zi * np.cos(xi[2] + theta), xi[1] + zi * np.sin(xi[2] + theta)]

    def check_cells(self, xi, zi):
        """
        Checks which cells are occupied or free based on the laser sweep and current robot position.

        This function takes the current pose of the robot and the laser readings as input. It computes 
        a "laser sweep", which is the set of cells that the robot's laser scanner would intersect 
        given its current position and the range data. The cells that the laser hits are considered 
        occupied. All cells between the robot's current position and these hit cells are considered free, 
        since the laser would have to pass through these cells to reach the hit cells.

        Both sets of cells (occupied and free) are rounded to the nearest integer to fit on a discrete 
        grid, which is then multiplied by the map resolution to convert to the map's scale. 

        :param xi: The current pose of the robot [x, y, theta].
        :param zi: The laser readings.

        :return: A tuple containing two lists. The first list is the set of grid cells that the laser 
                readings indicate are occupied. The second list is the set of grid cells that are 
                between the robot's current position and the occupied cells, i.e., the cells that the 
                laser must have passed through to reach the occupied cells, thus indicating they are free.
        """
        # Round the laser readings to get the occupied cells
        occ = np.round(np.array(self.laser_sweep(xi, zi)) * self.resolution).astype(int)

        # Round the robot pose to get the current cell
        xi = np.round(xi * self.resolution).astype(int)

        # Initialize a list of free cells
        free = np.array([[xi[0], xi[0]], [xi[1], xi[1]]])

        # Add all cells between the robot and each occupied cell to the list of free cells
        for i in range(len(zi)):
            free = np.hstack((free, self.bresenham_line(xi[0], xi[1], occ[0][i], occ[1][i]).T))

        return occ, free

    def update(self, xi, zi):
        """
        Updates the occupancy grid based on the current robot pose and laser readings.

        This function uses the inverse sensor model to compute the log odds that each cell in the map is 
        occupied. The inverse sensor model takes the current robot pose and the laser readings as input 
        and outputs the log odds that each cell is occupied. 

        The function then updates the log odds for each cell in the occupancy grid by adding the log odds 
        computed by the inverse sensor model to the cell's current log odds. This effectively performs a 
        Bayesian update of the cell's occupancy probability, since log odds are additive in the same way 
        that probabilities are multiplicative.

        :param xi: The current pose of the robot [x, y, theta].
        :param zi: The laser readings.
        """
        occ, free = self.check_cells(xi, zi)
        for i in range(occ.shape[1]):
            self.log_prob_map[occ[0][i], occ[1][i]] += self.add_prob(True)
        for i in range(free.shape[1]):
            self.log_prob_map[free[0][i], free[1][i]] += self.add_prob(False)
