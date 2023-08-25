#!/usr/bin/env python
import numpy as np
from Cell import Cell
from World import World


def part(n, m):
    i = np.random.randint(1, n-m+2)
    return [n] if m == 1 else [i, *part(n-i, m-1)]


class Vegetob:
    """Class representing a vegetob, vegatation object"""
    def __init__(self, density: float, position):
        assert 0 <= density <= 100, "Not a valid density"
        self.density = density
        self.position = position

    def grow(self):
        # density growing according to logistic function, with a maximum of 100
        if self.density < 1:
            self.density = 1
        else:
            self.density += self.density * (100 - self.density) / 1000


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

    def grow(self):
        # not to be confused with the grow method of Vegetob, this is just
        # changing the age of individual and checking if it's dead. This
        # function is called at the beginning of every turn and for convenience
        # has the same name as the grow method of Vegetob
        self.age += 1
        if self.age > self.lifetime:
            self.die()


class Erbast(Animal):
    """Class representing an Erbast, a herdivore"""
    def __init__(self, energy: int, lifetime: int,
                 social_attitude: float, position: Cell, herd, world: World):
        super().__init__(energy, lifetime, social_attitude, position, world)
        self.herd = herd

    def __eq__(self, other):
        return id(self) == id(other)

    def graze(self, quantity):
        self.energy += quantity
        self.pos.vegetob.density -= quantity

    def move(self):
        self.pos = self.herd.pos
        self.energy -= 1

    def choose(self):
        if self.herd.pos.vegetob.density*self.social_attitude > self.pos.vegetob.density and self.energy > self.herd.pos.vegetob.density:
            self.move()
        else:
            self.herd.remove(self)
            if self.pos.herd is None:
                self.herd = Herd(self, self.pos, self.world)
            else:
                self.herd = self.pos.herd

            self.herd.add_erbast(self)

    @classmethod
    def spawn(cls, pos: Cell, wrld):
        return cls(100, 10, 0.8, pos, pos.herd, wrld)

    def die(self):
        self.herd.remove(self)


class Carviz(Animal):
    """Class representing a Carviz, """
    def __init__(self, energy: int, lifetime: int,
                 social_attitude: float, position: Cell, pride, world: World):
        super().__init__(energy, lifetime, social_attitude, position, world)
        self.pride = pride


class Group:
    """Class representing a group of Animals, parent of herd and Pride"""
    def __init__(self, pos: Cell, world: World, members: Carviz or Erbast):
        self.pos = pos
        self.world = world
        self.members = members
        self.past_cells = []
        self.memory = {}

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for member in self.members:
            if member not in other.members:
                return False
        return True

    def __len__(self):
        return len(self.members)

    def add(self, member: Carviz or Erbast):
        self.members.append(member)

    def remove(self, member: Carviz or Erbast):
        self.members.remove(member)

    def join(self, other_herd):
        self.members += other_herd.members
        self.memory += other_herd.memory
        del other_herd

    def check_near_cells(self):
        for cell in self.world.get_neighbors(self.pos):
            self.memory[[cell.x, cell.y]] = cell.vegetob.density

    def proliferate(self):
        for member in self.members:
            # random number of children, between 0 and 4, but with 2 and 3 much
            # more likely
            m = np.random.choice([0, 1, 2, 3, 4],
                                 p=[0.05, 0.1, 0.4, 0.4, 0.05])
            for E, L, S in zip(part(member.energy, m),
                               part(member.lifetime*m, m),
                               part(member.social_attitude * m * 100, m)/100):
                self.add(Erbast(E, L, S, self.pos, self, self.world))


class Herd(Group):
    """Class representing a group of Erbast"""
    def __init__(self, erbasts: list[Erbast], position: Cell, world: World):
        super().__init__(position, world, erbasts)
        self.pos.add_herd(self)

    def move(self, new_cell):
        if new_cell == self.pos:
            for erbast in self.members:
                erbast.graze(1)
        self.pos.remove_herd()
        self.pos = new_cell
        self.pos.add_herd(self)
        for erbast in self.members:
            erbast.choose()

    def choose(self):
        self.check_near_cells()
        if self.pos.vegetob.density < 10:
            self.move(max(self.memory, key=self.memory.get))
        else:
            self.move(self.pos)
