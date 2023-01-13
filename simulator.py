import pygame
import math
import numpy as np


def uncertainty_add(distance, angle, sigma):
    mean = np.array([distance, angle])
    cov = np.diag(sigma**2)
    distance, angle = np.random.multivariate_normal(mean, cov)
    distance = max(distance, 0)
    angle = max(angle, 0)
    return distance, angle


class Colors:
    black = (0, 0, 0)
    white = (255, 255, 255)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    red = (255, 0, 0)
    yellow = (255, 255, 0)
    orange = (255, 165, 0)


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

    def AD2pos(self, distance, angle, robot_position, robot_orientation):
        x, y = robot_position
        x += distance * math.cos(angle - robot_orientation)
        y += distance * math.sin(angle - robot_orientation)
        return (x, y)

    def data_storage(self, data):
        for element in data:
            point = self.AD2pos(element[0], element[1], element[2], element[3])
            if point not in self.point_cloud:
                self.point_cloud.append(point)

    def show_sensor_data(self):
        self.infomap = self.map.copy()
        for point in self.point_cloud:
            self.infomap.set_at((int(point[0]), int(point[1])), Colors.red)
        if len(self.point_cloud) > 1000:
            self.point_cloud.pop(0)


class LaserSensor:
    def __init__(self, range, map, uncertainty):
        self.range = range
        self.sigma = np.array([uncertainty[0], uncertainty[1]])
        self.position = (0, 0)
        self.orientation = 0

        self.map = map
        self.width, self.height = pygame.display.get_surface().get_size()

    def distance(self, obstacle_pos):
        return np.linalg.norm(np.array(self.position) - np.array(obstacle_pos))

    def sensed_obstacles(self, position, orientation):
        self.position = position
        self.orientation = orientation
        data = []
        x1, y1 = self.position
        for angle in np.linspace(0, 2 * math.pi, 20, False):
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


class Robot:
    def __init__(self, start_position, robot_img, width):
        # Robot dimensions
        self.x = start_position[0]
        self.y = start_position[1]
        self.theta = 0
        self.width = width
        self.meters2pixels = 10
        self.velocity = 0.01 * self.meters2pixels
        self.max_velocity = 0.1 * self.meters2pixels
        self.min_velocity = -self.max_velocity

        # Graphics
        self.img = pygame.image.load(robot_img)
        self.rotated_img = self.img
        self.rect = self.img.get_rect(center=(self.x, self.y))

    def draw(self, environment):
        # draw robot
        environment.map.blit(self.rotated_img, self.rect)

    def move(self, event=None):
        if event is not None:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.velocity += 0.001 * self.meters2pixels
                if event.key == pygame.K_DOWN:
                    self.velocity -= 0.001 * self.meters2pixels
                if event.key == pygame.K_LEFT:
                    self.theta += 0.1
                if event.key == pygame.K_RIGHT:
                    self.theta -= 0.1

        # Reset theta
        if self.theta > 2 * math.pi:
            self.theta -= 2 * math.pi
        if self.theta < 0:
            self.theta += 2 * math.pi

        # Limit speeds
        if self.velocity > self.max_velocity:
            self.velocity = self.max_velocity
        if self.velocity < self.min_velocity:
            self.velocity = self.min_velocity

        # Motion model
        self.x += self.velocity * math.cos(self.theta) * dt
        self.y -= self.velocity * math.sin(self.theta) * dt

        self.rotated_img = pygame.transform.rotate(self.img, math.degrees(self.theta))
        self.rect = self.rotated_img.get_rect(center=(self.x, self.y))


# Init
pygame.init()

# start position
start = (300, 200)

# create environment
environment = Environment((1200, 600), "images/map.png")
robot = Robot(start, "images/robot.png", 40)
laser = LaserSensor(1000, environment.external_map, (0.5, 0.01))

environment.map.fill(Colors.black)
environment.infomap = environment.map.copy()


running = True

dt = 0
last_time = pygame.time.get_ticks()

# simulation loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        robot.move(event)

    laser_data = laser.sensed_obstacles((robot.x, robot.y), robot.theta)
    if laser_data:
        environment.data_storage(laser_data)
        environment.show_sensor_data()
    environment.map.blit(environment.infomap, (0, 0))

    dt = (pygame.time.get_ticks() - last_time) / 1000.0

    # update screen
    pygame.display.update()

    # clear screen
    environment.map.fill(Colors.black)
    environment.infomap = environment.map.copy()

    # draw info
    environment.draw_info(robot.velocity, robot.theta)

    # draw robot
    robot.move()
    environment.trail((robot.x, robot.y))
    robot.draw(environment)
    environment.robot_frame((robot.x, robot.y), robot.theta)
    last_time = dt
