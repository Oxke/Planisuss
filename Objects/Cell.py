#!/usr/bin/env python
from numpy.random import randint as rand
class Cell:
    """Class representing a cell in the world
    A cell can contain a vegetob, a herd of erbast and a pride of carviz"""
    def __init__(self, x: int, y: int, water: bool = False):
        self.x = x
        self.y = y
        self.herd = None
        self.pride = None
        self.water = water  # if true, no animal or vegetob can live there
        self.vegetob = None
        self.Ecosystem = None

    def spawn_vegetob(self, density: float):
        """Spawns a vegetob in the cell"""
        assert self.vegetob is None, f"{self} already has a vegetob"
        assert not self.water, f"Can't spawn vegetob in water at {self}"
        obj = __import__("Objects.Ecosystem")
        self.Ecosystem = obj.Ecosystem
        self.vegetob = self.Ecosystem.Vegetob(density, self)


    def add_herd(self, herd, world=None):
        """The world argument is only used when spawning a new herd when
        starting the simulation"""
        if world:
            erbasts = []
            for _ in range(10):
                erbasts.append(self.Ecosystem.Erbast.spawn(self, world))
            self.herd = self.Ecosystem.Herd(erbasts, self, world)
            for erbast in self.herd.members:
                erbast.herd = self.herd
        elif self.herd:
            if self.herd != herd:
                self.herd = self.herd.join(herd)
        else:
            self.herd = herd

    def remove_herd(self):
        self.herd = None

    def add_pride(self, pride, world=None):
        if world:
            carvizes = []
            if rand(10) < 5:
                carvizes.append(self.Ecosystem.Carviz.spawn(self, world))
            self.pride = self.Ecosystem.Pride(carvizes, self, world)
            for carviz in self.pride.members:
                carviz.pride = self.pride
        elif self.pride:
            if self.pride != pride:
                if pride.get_sa() + self.pride.get_sa() > 1:
                    self.pride = self.pride.join(pride)
                else:
                    self.pride = self.pride.fight(pride)
        else:
            self.pride = pride
            if self.herd:
                self.pride.hunt()

    def remove_pride(self):
        self.pride = None

    def __repr__(self):
        return f"Cell({self.x}, {self.y})"

    def __str__(self):
        return f"Cell({self.x}, {self.y})"

    def population(self):
        res = len(self.herd) if self.herd else 0
        return res+len(self.pride) if self.pride else res

class DeadVegetob:
    def __init__(self, graveyard):
        self.density = 0
        self.position = graveyard

class Graveyard(Cell):
    """A graveyard is a cell where animals go to die"""
    def __init__(self, x: int, y: int, reason: str):
        super().__init__(x, y)
        self.vegetob = DeadVegetob(self)
        self.reason_of_death = reason

    def __repr__(self):
        return f"Graveyard({self.x}, {self.y})"

    def __str__(self):
        return f"Graveyard({self.x}, {self.y})"

    def add_herd(self):
        pass

    def add_pride(self):
        pass

    def remove_herd(self):
        pass

    def remove_pride(self):
        pass

    def population(self):
        return 0
