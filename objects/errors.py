class TotalExtinction(Exception):
    def __init__(self):
        super().__init__(self, "No animal left on the simulation")
