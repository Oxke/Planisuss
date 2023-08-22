#!/usr/bin/env python
import numpy as np
from Cell import Cell
from World import World

COUNT = 1

def part(n: int, m: int):
    if m == 1:
        return [n]
    i = np.random.randint(1, n-m+2)
    return [i, *part(n-i, m-1)]


class Vegetob:
    """Class representing a vegetob, vegetation object"""
    def __init__(self, density: float, position):
        assert 0 <= density <= 100, "Not a valid density"
        self.density = density
        self.position = position

    def grow(self):
        # density growing according to logistic function, with a maximum of 100
        if self.density < 1:
            self.density = 1
        else:
            self.density += self.density * (100 - self.density) / 10000


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
        self._id = id(self)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.energy}, {self.lifetime}, " \
               f"{self.social_attitude}, {self.pos}, {self.age})"

    def grow(self):
        # not to be confused with the grow method of Vegetob, this is just
        # changing the age of individual and checking if it's dead. This
        # function is called at the beginning of every turn and for convenience
        # has the same name as the grow method of Vegetob
        self.age += 1
        overcrowding = np.random.random() / self.social_attitude * \
        self.pos.population() >= 100
        overage = self.age > self.lifetime
        lack_energy = np.random.random()*self.energy < 5
        if overcrowding or overage or lack_energy:
            self.die(overcrowding)

    def die(self, overcrowding=False):
        """To be implemented in subclasses"""
        raise NotImplementedError


class Erbast(Animal):
    """Class representing an Erbast, a herbivore"""
    def __init__(self, energy: int, lifetime: int,
                 social_attitude: float, position: Cell, herd, world: World):
        super().__init__(energy, lifetime, social_attitude, position, world)
        self.herd = herd

    def graze(self, quantity):
        self.energy += quantity
        # self.pos.vegetob.density -= quantity

    def stay_with_herd(self):
        self.energy -= self.world.distance(self.pos, self.herd.pos)
        if self.energy <= 0:
            self.die()
        self.pos = self.herd.pos

    def quit_herd(self):
        self.herd.remove(self)
        if self.energy > self.pos.vegetob.density:
            destination = np.random.choice(self.world.get_neighbors(self.pos,
                                                                    flag="land"))
            self.energy -= self.world.distance(self.pos, destination)
            if self.energy <= 0:
                self.die()
            self.pos = destination
        if self.pos.herd:
            self.herd = self.pos.herd
            self.herd.add(self)
        else:
            self.herd = Herd([self], self.pos, self.world)
            self.pos.add_herd(self.herd)

    def choose(self):
        if (self.herd.pos.vegetob.density*self.social_attitude >
            self.pos.vegetob.density and self.energy >
            self.herd.pos.vegetob.density and
            len(self.herd)*self.social_attitude < 100):
            self.stay_with_herd()
        else:
            self.quit_herd()

    @classmethod
    def spawn(cls, pos: Cell, wrld):
        return cls(100, 10, 0.8, pos, pos.herd, wrld)

    def die(self, overcrowded=False):
        global COUNT
        # This is a bug of the GC i think, it doesn't delete the object
        try:
            self.herd.members.remove(self)
        except ValueError:
            if len(self.herd.members) == 0:
                self.pos.remove_herd()
                del self.herd
            else:
                del self.herd.members[-1]
        # this partitions randomly the energy and lifetime of the ancestor to
        # the children
        if self.energy > 5 and not overcrowded:
            COUNT += 2
            for E, L in zip(part(self.energy*2, 2), part(self.lifetime*2, 2)):
                s_a = min(1, max(0.1, np.random.normal(self.social_attitude, 0.1)))
                self.herd.add(Erbast(E, L, s_a, self.herd.pos, self.herd, self.world))
        del self
        COUNT -= 1
        print(COUNT)


class Carviz(Animal):
    """Class representing a Carviz, """
    def __init__(self, energy: int, lifetime: int,
                 social_attitude: float, position: Cell, pride, world: World):
        super().__init__(energy, lifetime, social_attitude, position, world)
        self.pride = pride

    def move(self):
        self.energy -= self.world.distance(self.pos, self.pride.pos)
        if self.energy <= 0:
            self.die()
        self.pos = self.pride.pos

    def choose(self):
        if self.pride.pos.herd.get_energy()*self.social_attitude > \
        self.pos.herd.get_energy() and self.energy > \
        self.pride.pos.herd.get_energy():
            self.move()
        else:
            self.pride.remove(self)
            self.pride = Herd([self], self.pos, self.world)
            self.pos.add_pride(self.pride)
            self.pride.add(self)

    @classmethod
    def spawn(cls, pos: Cell, wrld):
        return cls(100, 10, 0.8, pos, pos.pride, wrld)

    def die(self, overcrowded=False):
        self.pride.remove(self)
        # partitions randomly to ancestors like before
        if self.energy > 5 and not overcrowded:
            for E, L in zip(part(self.energy*2, 2), part(self.lifetime*2, 2)):
                s_a = min(1, max(0.1, np.random.normal(self.social_attitude, 0.1)))
                self.pride.add(Carviz(E, L, s_a, self.pride.pos, self.pride, self.world))
        del self


class Group:
    """Class representing a group of Animals, parent of herd and Pride"""
    def __init__(self, pos: Cell, world: World, members: Carviz or Erbast):
        self.pos = pos
        self.world = world
        self.members = members
        self.past_cells = []
        self.memory = {}

    def __repr__(self):
        return str(self.members)

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
        self.members = [m for m in self.members if m != member]

    def join(self, other_group):
        self.members += other_group.members
        for key in other_group.memory:
            if key in self.memory and np.random.random() < 0.5:
                self.memory[key] = other_group.memory[key]
            else:
                self.memory[key] = other_group.memory[key]
        del other_group
        return self

    def add_energy(self, energy):
        extra = 0
        for m, en in zip(self.members, part(energy, len(self))):
            en += extra
            extra = max(0, m.energy+en-100)
            en -= extra
            m.energy += en

    def proliferate(self):
        for member in list(self.members):  # list() is used to avoid changing the list while iterating over it
            m = np.random.choice([0, 1, 2, 3, 4],
                                 p=[0.95, 0.04, 0.007, 0.002, 0.001])
            if member.energy < 5:
                m = np.floor(np.random.random()*member.energy)
            if m == 0:
                continue
            for E, L in zip(part(member.energy*m, m),
                            part(member.lifetime*m, m)):
                self.add(Erbast(E, L, member.social_attitude, self.pos, self, self.world))

    def get_energy(self):
        return sum([m.energy for m in self.members])

    def get_sa(self):
        return np.array([m.social_attitude for m in self.members]).mean()

    def get_champion(self):
        return max(self.members, key=lambda m: m.energy)


class Herd(Group):
    """Class representing a group of Erbast"""
    def __init__(self, erbasts: list[Erbast], position: Cell, world: World):
        super().__init__(position, world, erbasts)
        self.pos.add_herd(self)

    def check_near_cells(self):
        # Can still go to far cells but each time is preferable to stay near, if
        # less than some threshold it might be forgotten (TODO)
        self.memory = {c: d/2 for c, d in self.memory.items()}
        for cell in self.world.get_neighbors(self.pos):
            if cell.vegetob:
                self.memory[cell] = cell.vegetob.density

    def move(self, new_cell):
        if new_cell == self.pos:
            for erbast in self.members:
                erbast.graze(min(1, self.pos.vegetob.density/len(self)))
            self.pos.vegetob.density -= min(len(self), self.pos.vegetob.density)
        else:
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


class Pride(Group):
    def __init__(self, carvizes: list[Carviz], position: Cell, world: World):
        super().__init__(position, world, carvizes)
        self.pos.add_pride(self)

    def check_near_cells(self):
        # Can still go to far cells but each time is preferable to stay near, if
        # less than some threshold it might be forgotten (TODO)
        self.memory = {c: e/2 for c, e in self.memory.items()}
        for cell in self.world.get_neighbors(self.pos):
            if cell.herd:
                self.memory[cell] = cell.herd.get_energy()

    def move(self, new_cell):
        self.pos.remove_pride()
        self.pos = new_cell
        self.pos.add_pride(self)

    def choose(self):
        self.check_near_cells()
        if self.pos.herd.get_energy()/len(self) > 40:
            self.hunt()
        else:
            self.move(max(self.memory, key=self.memory.get))
        for carviz in self.members:
            carviz.choose()

    def fight(self, other_pride):
        while len(self)*len(other_pride) > 0:
            self_champion = self.get_champion()
            other_champion = other_pride.get_champion()
            if self_champion.energy > other_champion.energy:
                self_champion.die()
            else:
                other_champion.die()
        if len(self) > 0:
            del other_pride
            return self
        del self
        return other_pride

    def hunt(self):
        if self.pos.herd:
            prey = self.pos.herd.get_champion()
            self.add_energy(prey.energy)
            prey.die()


