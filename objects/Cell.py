#!/usr/bin/env python


class Cell:
    """Class representing a cell in the world
    A cell can contain a vegetob, a herd of erbast and a pride of carviz"""
    def __init__(self, x: int, y: int, water: bool = False):
        self.x = x
        self.y = y
        self.herd = None
        self.prides = []
        self.water = water  # if true, no animal or vegetob can live there
        self.vegetob = None

    def spawn_vegetob(self, density: float):
        """Spawns a vegetob in the cell"""
        assert self.vegetob is None, f"{self} already has a vegetob"
        assert not self.water, f"Can't spawn vegetob in water at {self}"
        self.vegetob = __import__("Ecosystem").Vegetob(density, self)

    def n_carvizes(self):
        """return sum of all len(pride) for pride in self.prides"""
        return sum(len(pride) for pride in self.prides)

    def add_herd(self, herd, world=None):
        if world:
            erbast = __import__("Ecosystem").Erbast.spawn(self, world)
            self.herd = __import__("Ecosystem").Herd([erbast], self, world)
            self.herd.members[0].herd = self.herd
        elif self.herd:
            if self.herd != herd:
                self.herd = self.herd.join(herd)
        else:
            self.herd = herd

    def remove_herd(self):
        self.herd = None

    def add_pride(self, pride):
        self.prides.append(pride)

    def remove_pride(self, pride):
        self.prides.remove(pride)

    def __repr__(self):
        return f"Cell({self.x}, {self.y})"

    def __str__(self):
        return f"Cell({self.x}, {self.y})"
