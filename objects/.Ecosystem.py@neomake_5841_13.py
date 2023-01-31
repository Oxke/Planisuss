#!/usr/bin/env python
import numpy as np
from Cell import Cell
from World import World


class Vegetob:
    """Class representing a vegetob, vegatation object"""
    def __init__(self, density: float, position):
        assert 0 <= density <= 100, "Not a valid density"
        self.density = density
        self.position = position

    def grow(self):
        # density growing according to logistic function, with a maximum of 100
        if self.density == 0:
            self.density = 1
        else:
            self.density += 100 / (1 + np.exp(-self.density / 10)) - 50


class Animal:
    """Parent class of both Carviz and Erbast"""
    def __init__(self, energy: int, lifetime: int, social_attitude: float,
                 position: Cell, world: World):
        assert energy >= 0, "Animal was born dead"
        assert lifetime >= 0, "Animal should have already died"
        assert 0 <= social_attitude <= 1, "Social Attitude not valid"
        self.energy = energy
        self.lifetime = lifetime
        self.social_attitude = social_attitude
        self.age = 0
        self.pos = position
        self.world = world


class Erbast(Animal):
    """Class representing an Erbast, a herbivore"""
    def __init__(self, energy: int, lifetime: int,
                 social_attitude: float, position: Cell, herb, world: World):
        super().__init__(energy, lifetime, social_attitude, position, world)
        self.herb = herb

    def graze(self, quantity):
        self.energy += quantity
        self.pos.vegetob.density -= quantity

    def move(self):
        self.pos = self.herb.pos
        self.energy -= 1

    def choose(self):
        if self.herb.pos.vegetob.density*self.social_attitude > self.pos.vegetob.density and self.energy > self.herb.pos.vegetob.density:
            self.move()
        else:
            self.herb.remove(self)
            if self.pos.herb is None:
                self.herb = Herb(self, self.pos, self.world)
            else:
                self.herb = self.pos.herb

            self.herb.add_erbast(self)


class Carviz(Animal):
    """Class representing a Carviz, """
    def __init__(self, energy: int, lifetime: int,
                 social_attitude: float, position: Cell, pride, world: World):
        super().__init__(energy, lifetime, social_attitude, position, world)
        self.pride = pride


class Group:
    """Class representing a group of Animals, parent of Herb and Pride"""
    def __init__(self, pos: Cell, world: World, members: Carviz or Erbast):
        self.pos = pos
        self.world = world
        self.members = []
        self.past_cells = []
        self.memory = {}

    def __len__(self):
        return len(self.members)

    def add(self, member: Carviz or Erbast):
        self.members.append(member)

    def remove(self, member: Carviz or Erbast):
        self.members.remove(member)

    def join(self, other_herb):
        self.members += other_herb.members
        self.memory += other_herb.memory
        del other_herb

    def check_near_cells(self):
        for cell in self.world.get_neighbors(self.pos):
            self.memory[[cell.x, cell.y]] = cell.vegetob.density

class Herb(Group):
    """Class representing a group of Erbast"""
    def __init__(self, erbasts: list[Erbast], position: Cell, world: World):
        super().__init__(position, world, erbasts)
        self.pos.add_herb(self)

    def move(self, new_cell):
        if new_cell == self.pos:
            for erbast in self.members:
                erbast.graze(1)
        self.pos = new_cell
        for erbast in self.members:
            erbast.choose()

    def choose(self):
        if self.pos.vegetob.density < 10:
            self.move(max(self.memory, key=self.memory.get))
        else:
            self.move(self.pos)

    def add_erbast(self, erbast: Erbast):
        self.erbasts.append(erbast)

    def remove_erbast(self, erbast: Erbast):
        self.erbasts.remove(erbast)
