import pygame

import math

import copy

from .tools import Colors


class Environment:
    def __init__(self, dimensions, map_img):
        # dimensions
        self.width = dimensions[0]
        self.height = dimensions[1]
        # window settings
        pygame.display.set_caption("Differential drive robot simulator")
        self.map = pygame.display.set_mode((self.width, self.height))

        self.external_map = pygame.image.load(map_img)
        self.map.blit(self.external_map, (0, 0))
        self.point_cloud = []

        # text variables
        self.font = pygame.font.SysFont("monospace", 20)
        self.text = self.font.render("Hello World", True, Colors.white, Colors.black)
        self.text_rect = self.text.get_rect()
        self.text_rect.center = (dimensions[0] - 200, dimensions[1] - 100)

        # trail
        self.trail_length = 500
        self.trail_list = []

    def draw_info(self, speed, theta):
        txt = (
            "v: {:.2f}".format(speed)
            + " m/s o: "
            + str(int(math.degrees(theta)))
            + " deg"
        )
        self.text = self.font.render(txt, True, Colors.white, Colors.black)
        self.map.blit(self.text, self.text_rect)

    def trail(self, pos):
        for i in range(len(self.trail_list) - 1):
            pygame.draw.line(
                self.map, Colors.yellow, self.trail_list[i], self.trail_list[i + 1]
            )
        if len(self.trail_list) > self.trail_length:
            self.trail_list.pop(0)
        self.trail_list.append(pos)

    def robot_frame(self, pos, rotation):
        n = 80
        centerx, centery = pos
        x_axis = (centerx + n * math.cos(-rotation), centery + n * math.sin(-rotation))
        y_axis = (
            centerx + n * math.cos(math.pi / 2 - rotation),
            centery + n * math.sin(math.pi / 2 - rotation),
        )
        pygame.draw.line(self.map, Colors.red, pos, y_axis, 3)
        pygame.draw.line(self.map, Colors.green, pos, x_axis, 3)
        pygame.draw.circle(self.map, Colors.blue, pos, 5)

    def AD2pos(self, distance, angle, robot_position):
        robot_x, robot_y = robot_position
        x = robot_x + distance * math.cos(angle)
        y = robot_y + distance * math.sin(angle)
        return (x, y, robot_x, robot_y)

    def data_storage(self, data):
        for element in data:
            point = self.AD2pos(element[0], element[1], element[2])
            if point not in self.point_cloud:
                self.point_cloud.append(point)
        if len(self.point_cloud) > 365:
            self.point_cloud.pop(0)

    def show_sensor_data(self, pos):
        self.infomap = self.map.copy()
        for point in self.point_cloud:
            pygame.draw.line(
                self.infomap,
                Colors.gray,
                (int(point[0]), int(point[1])),
                (int(point[2]), int(point[3])),
            )
            self.infomap.set_at((int(point[0]), int(point[1])), Colors.red)

        if len(self.point_cloud) > 1000:
            self.point_cloud.pop(0)
