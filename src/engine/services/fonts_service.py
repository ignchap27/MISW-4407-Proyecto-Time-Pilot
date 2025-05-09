import pygame.freetype

class FontsService:
    def __init__(self):
        self._fonts = {}

    def get(self, path: str, size: int):
        key = f"{path}_{size}"
        if key not in self._fonts:
            self._fonts[key] = pygame.freetype.Font(path, size)
        return self._fonts[key]