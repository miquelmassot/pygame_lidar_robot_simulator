import pygame
import math


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

    def move(self, dt, event=None):
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
