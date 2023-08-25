#!/usr/bin/env python
import numpy as np
from Cell import Cell, Graveyard
from World import World
from variables import CAUSE_OF_DEATH


ANIMALS = {}
COUNT = 1
GRAVEYARD = Graveyard()

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
            # self.density += self.density * (100 - self.density) / 10000
            # self.density += (100 - self.density)/10
            self.density += self.density * (100 - self.density)**2 / 100000


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
        self._alive = True
        ANIMALS[self._id] = self

    @property
    def id(self):
        return self._id

    def __repr__(self):
        return f"{self.__class__.__name__}({self.energy}, {self.lifetime}, " \
               f"{self.social_attitude}, {self.pos}, {self.age})"

    def grow(self):
        # not to be confused with the grow method of Vegetob, this is just
        # changing the age of individual and checking if it's dead. This
        # function is called at the beginning of every turn and for convenience
        # has the same name as the grow method of Vegetob
        self.age += 1
        # overcrowding = np.random.random() / self.social_attitude * \
        # self.pos.population >= 100
        overcrowding = False
        overage = self.age > self.lifetime
        lack_energy = np.random.random()*self.energy < 5
        if overcrowding:
            CAUSE_OF_DEATH.append("overcrowding")
        if overage:
            CAUSE_OF_DEATH.append("overage")
        if lack_energy:
            CAUSE_OF_DEATH.append("lack_energy")
        if overcrowding or overage or lack_energy:
            self.die(overcrowding)

    def die(self, overcrowded=False):
        global COUNT, ANIMALS, GRAVEYARD
        self._alive = False
        try:
            del ANIMALS[self.id]
        except KeyError:
            print("OH NO")

        # this partitions randomly the energy and lifetime of the ancestor to
        # the children
        if self.energy > 5 and not overcrowded:
            for E, L in zip(part(self.energy, 2), part(self.lifetime*2, 2)):
                s_a = min(1, max(0.1, np.random.normal(self.social_attitude, 0.1)))
                if isinstance(self, Erbast):
                    self.herd.add(Erbast(E, L, s_a, self.herd.pos, self.herd, self.world))
                elif isinstance(self, Carviz):
                    self.pride.add(Carviz(E, L, s_a, self.pride.pos, self.pride, self.world))
        self.pos = GRAVEYARD


class Erbast(Animal):
    """Class representing an Erbast, a herbivore"""
    def __init__(self, energy: int, lifetime: int,
                 social_attitude: float, position: Cell, herd, world: World):
        super().__init__(energy, lifetime, social_attitude, position, world)
        self.herd = herd

    def graze(self, quantity):
        self.energy += quantity // (self.age+1) * self.lifetime
        # self.pos.vegetob.density -= quantity

    def stay_with_herd(self):
        self.energy -= self.world.distance(self.pos, self.herd.pos)
        if self.energy <= 0:
            self.die()
            CAUSE_OF_DEATH.append("lack_energy_movement")
        else:
            self.pos = self.herd.pos

    def quit_herd(self):
        self.herd.remove(self)
        if self.energy > self.pos.vegetob.density:
            destination = np.random.choice(self.world.get_neighbors(self.pos,
                                                                    flag="land"))
            self.energy -= self.world.distance(self.pos, destination)
            if self.energy <= 0:
                self.die()
                CAUSE_OF_DEATH.append("lack_energy_movement")
            else:
                self.pos = destination
        if self.pos.herd:
            self.herd = self.pos.herd
            self.herd.add(self)
        elif self._alive:
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
        return cls(1000, 100, 0.8, pos, pos.herd, wrld)


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
        else:
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
        self._members_id = [m.id for m in members]
        self._members = []
        self.past_cells = []
        self.memory = {}

    def __repr__(self):
        return str(self.members)

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for mid in self._members_id:
            if mid not in other._members_id:
                return False
        return True

    def __len__(self):
        return len(self._members_id)

    def __getitem__(self, item):
        return ANIMALS[self._members_id[item]]

    @property
    def members(self):
        for mid in self._members_id:
            try:
                yield ANIMALS[mid]
            except KeyError:
                continue

    def add(self, member: Carviz or Erbast):
        self._members_id.append(member.id)

    def remove(self, member: Carviz or Erbast or int):
        if isinstance(member, (Erbast, Carviz)):
            member = member.id
            # self._members_id = [mid for mid in self._members_id if mid != member.id]
        self._members_id = [mid for mid in self._members_id if mid != member]

    def join(self, other_group):
        self._members_id += other_group._members_id
        for key in other_group.memory:
            if key not in self.memory or np.random.random() < 0.5:
                self.memory[key] = other_group.memory[key]
        del other_group
        return self

    def add_energy(self, energy):
        extra = 0
        for mid, en in zip(self._members_id, part(energy, len(self))):
            en += extra
            extra = max(0, ANIMALS[mid].energy+en-100)
            en -= extra
            ANIMALS[mid].energy += en

    def grow(self):
        if len(self) == 0:
            if isinstance(self, Herd):
                self.pos.remove_herd()
            else:
                self.pos.remove_pride()

        for i, id_member in enumerate(list(self._members_id)):
            try:
                ANIMALS[id_member].grow()
            except KeyError:
                self.remove(id_member)

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
        return np.array([ANIMALS[mid].social_attitude for mid in
                         self._members_id]).mean()

    def get_champion(self):
        return ANIMALS[max(self._members_id, key=lambda mid: ANIMALS[mid].energy)]


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
        for i, id_erbast in enumerate(list(self._members_id)):
            try:
                m = ANIMALS[id_erbast]
            except KeyError:
                self.remove(id_erbast)
                continue
            if m._alive:
                m.choose()
            else:
                self.remove(id_erbast)
        if new_cell == self.pos:
            for i, id_erbast in enumerate(list(self._members_id)):
                try:
                    m = ANIMALS[id_erbast]
                except KeyError:
                    self.remove(id_erbast)
                    continue
                if m._alive:
                    m.graze(min(1, self.pos.vegetob.density/len(self)))
                else:
                    self.remove(id_erbast)
            self.pos.vegetob.density -= min(len(self), self.pos.vegetob.density)
        else:
            self.pos.remove_herd()
            self.pos = new_cell
            self.pos.add_herd(self)

    def move_towards(self, new_cell):
        if self.world.distance(self.pos, new_cell) <= 1:
            self.move(self.pos)
            return
        neigh = self.world.get_neightbors(self.pos, flag="land")
        actual_new_cell = neigh[np.argmin([self.world.distance(new_cell, n) for n in neigh])]
        self.move(actual_new_cell)

    def memory_value(self, cell):
        if cell in self.memory: return self.memory[cell]
        return 1

    def choose(self):
        self.check_near_cells()
        if self.pos.vegetob.density < self.get_energy():
            self.move(max(self.world.get_neighbors(self.pos, 3, flag="land"),
                          key=self.memory_value))
        else:
            self.move_towards(self.pos)


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


