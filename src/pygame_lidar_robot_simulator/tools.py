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
    gray = (128, 128, 128)
