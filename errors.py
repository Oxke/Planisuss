class TotalExtinction(Exception):
    def __init__(self):
        super().__init__(self, "No animal left on the simulation")


class AlreadyDeadError(Exception):
    def __init(self, message):
        super().__init__(self, message)

