import pygame


from pygame_lidar_robot_simulator.environment import Environment
from pygame_lidar_robot_simulator.robot import Robot
from pygame_lidar_robot_simulator.laser_sensor import LaserSensor
from pygame_lidar_robot_simulator.tools import Colors
from pygame_lidar_robot_simulator.rate import Rate


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
clock = pygame.time.Clock()

# simulation loop
while running:
    clock.tick(10)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        robot.move(dt, event)

    dt = (pygame.time.get_ticks() - last_time) / 1000.0

    # update screen
    pygame.display.update()

    # clear screen
    environment.map.fill(Colors.black)
    environment.infomap = environment.map.copy()

    laser_data = laser.sensed_obstacles(dt, (robot.x, robot.y), robot.theta)
    if laser_data:
        environment.data_storage(laser_data)
        environment.show_sensor_data((robot.x, robot.y))
    environment.map.blit(environment.infomap, (0, 0))

    # process
    robot.move(dt)

    # draw
    environment.trail((robot.x, robot.y))
    robot.draw(environment)
    environment.robot_frame((robot.x, robot.y), robot.theta)
    environment.draw_info(robot.velocity, robot.theta)

    last_time = dt
