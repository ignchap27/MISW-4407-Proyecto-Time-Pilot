class CBossHealth:
    def __init__(self, max_health: int):
        self.max_health = max_health
        self.current_health = max_health
        self.is_defeated = False

    def take_damage(self, amount: int):
        if self.is_defeated: # No tomar más daño si ya está derrotado
            return

        self.current_health -= amount
        if self.current_health <= 0: # Usar <= 0 para ser más robusto
            self.current_health = 0
            self.is_defeated = True