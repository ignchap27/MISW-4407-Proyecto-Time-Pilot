from enum import Enum


class CPlayerState:
    def __init__(self):
        self.state = PlayerState.IDLE
        self.visible = True


class PlayerState(Enum):
    IDLE = 0
    MOVE = 1
    DEAD = 2
