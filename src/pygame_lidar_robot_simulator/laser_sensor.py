import math
import pygame

import numpy as np

from .tools import Colors
from .tools import uncertainty_add


class LaserSensor:
    def __init__(self, range, map, uncertainty, min_angle=0, max_angle=2 * math.pi):
        self.range = range
        self.sigma = np.array([uncertainty[0], uncertainty[1]])
        self.position = (0, 0)
        self.orientation = 0
        self.rate = 1.0  # Hz
        self.angular_resolution = math.radians(1.0)  # rad
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.angular_position = np.mean([min_angle, max_angle])

        self.map = map
        self.width, self.height = pygame.display.get_surface().get_size()

    def distance(self, obstacle_pos):
        return np.linalg.norm(np.array(self.position) - np.array(obstacle_pos))

    def sensed_obstacles(self, dt, position, orientation):
        self.position = position
        self.orientation = orientation
        data = []
        x1, y1 = self.position

        # Check how many scans are due
        n_scans = int(dt * self.rate)
        if n_scans == 0:
            return False

        # Check if the angular position is within the limits
        if self.angular_position < self.min_angle:
            self.angular_position = self.min_angle
        elif self.angular_position > self.max_angle:
            self.angular_position = self.max_angle
        for i in range(n_scans):
            # Retrieve the angle of the scan
            angle = self.angular_position + self.orientation

            # Compute the end point of the scan
            x2 = x1 + self.range * math.cos(angle)
            y2 = y1 + self.range * math.sin(angle)

            # Scan the map
            for i in range(0, 1000):
                u = i / 1000.0
                x, y = int(x1 + u * (x2 - x1)), int(y1 + u * (y2 - y1))
                if x < 0 or x >= self.width or y < 0 or y >= self.height:
                    break
                if self.map.get_at((x, y)) == Colors.black:
                    distance = self.distance((x, y))
                    distance, angle = uncertainty_add(distance, angle, self.sigma)
                    data.append((distance, angle, self.position, self.orientation))
                    break
            # Update the angular position
            self.angular_position += self.angular_resolution
            if self.angular_position > 2 * math.pi:
                self.angular_position -= 2 * math.pi
            elif self.angular_position < 0:
                self.angular_position += 2 * math.pi
        return data
        """
        for angle in np.linspace(math.pi, 2 * math.pi, 20, False):
            print(angle)
            x2 = x1 + self.range * math.cos(angle)
            y2 = y1 + self.range * math.sin(angle)
            for i in range(0, 1000):
                u = i / 1000.0
                x, y = int(x1 + u * (x2 - x1)), int(y1 + u * (y2 - y1))
                if x < 0 or x >= self.width or y < 0 or y >= self.height:
                    break
                if self.map.get_at((x, y)) == Colors.black:
                    distance = self.distance((x, y))
                    angle = math.atan2(y - y1, x - x1) + self.orientation
                    distance, angle = uncertainty_add(distance, angle, self.sigma)
                    data.append((distance, angle, self.position, self.orientation))
                    break
        if len(data) == 0:
            return False
        else:
            return data
        """
