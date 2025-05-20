from dataclasses import dataclass
import pygame

@dataclass
class CSteer:
    max_speed: float = 120
    max_force: float = 600
    arrive_radius: float = 48
