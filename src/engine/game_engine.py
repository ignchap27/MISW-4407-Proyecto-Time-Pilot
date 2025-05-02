class GameEngine:
    def __init__(self) -> None:
        self.is_running = False

    def run(self) -> None:
        self._create()
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
        self._clean()

    def _create(self):
        pass

    def _calculate_time(self):
        pass

    def _process_events(self):
        pass

    def _update(self):
        pass

    def _draw(self):
        pass

    def _clean(self):
        pass
