class CSpecialCharge:
    def __init__(self, max_charge: int = 100, charge_rate: int = 25):
        self.current_charge = 0
        self.max_charge = max_charge
        self.charge_rate = charge_rate

    def add_charge(self):
        self.current_charge = min(self.max_charge, self.current_charge + self.charge_rate)

    def reset_charge(self):
        self.current_charge = 0

    def get_charge(self) -> int:
        return self.current_charge

    def is_fully_charged(self) -> bool:
        return self.current_charge == self.max_charge