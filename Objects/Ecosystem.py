#!/usr/bin/env python
import numpy as np
from Objects.Cell import Cell, Graveyard
from Objects.World import World
from errors import AlreadyDeadError
from variables import ANIMALS, CAUSE_OF_DEATH


def part(n: float, m: int):
    assert isinstance(m, int)
    if m == 1:
        return [min(n,100)]
    i = np.random.random()*n
    return [*part(i, m//2), *part(n-i, m//2+m%2)]


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
            self.density += self.density * (100 - self.density)**2 / 100000


class Animal:
    """Parent class of both Carviz and Erbast"""
    def __init__(self, energy: int, lifetime: int, social_attitude: float,
                 position: Cell, world: World):
        global ANIMALS
        assert energy >= 0, "Animal was born dead"
        assert lifetime >= 0, "Animal should have already died"
        assert 0 <= social_attitude <= 1, "Social Attitude not valid"
        self.energy = energy
        self.lifetime = lifetime
        self.social_attitude = social_attitude
        self.age = 0
        self.pos = position
        self.world = world
        self._id = len(ANIMALS)
        ANIMALS.append(self)
        self._alive = True

    @property
    def alive(self):
        return self._alive

    def __repr__(self):
        return f"{self.__class__.__name__}({self.pos}, {self.id}, {self._alive})"

    def grow(self, population=0):
        # not to be confused with the grow method of Vegetob, this is just
        # changing the age of individual and checking if it's dead. This
        # function is called at the beginning of every turn and for convenience
        # has the same name as the grow method of Vegetob

        self.age += 1
        while self.energy >= 150:
            self.energy -= 50
            self.lifetime += 1

        # While the making of the project, I considered the possibility of
        # having an overcrowding mechanic, it turned out it wasn't necessary but
        # in case I want to implement it in the future, I'll leave this code
        overcrowding = False
        overage = self.age >= self.lifetime
        lack_energy = np.random.random()*self.energy < 5

        if overcrowding or overage or lack_energy:
            reason = "overcrowding" if overcrowding else "overage" if overage \
                else "lack_energy"
            self.die(reason)

    def die(self, overcrowding=False):
        """To be implemented in subclasses"""
        raise NotImplementedError


class Erbast(Animal):
    """Class representing an Erbast, a herbivore"""
    def __init__(self, energy: int, lifetime: int,
                 social_attitude: float, position: Cell, herd, world: World):
        super().__init__(energy, lifetime, social_attitude, position, world)
        self.herd = herd

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        try:
            self.herd.remove(self)
        except ValueError:
            print("\n\nError in Erbast.id.setter")
            print(self._id, end = " not in ")
            print(self.herd.members_id)
            print(self, self.herd, self.pos.herd)
            raise ValueError
        self._id = value
        self.herd.add(self)

    def graze(self, quantity):
        self.energy += 10 * quantity // (self.age+1) * self.lifetime
        # self.energy += quantity
        # self.pos.vegetob.density -= quantity

    def stay_with_herd(self, new_herd_pos):
        self.energy -= self.age**2 * self.world.distance(self.pos, new_herd_pos)
        if self.energy <= 0:
            # self.die("lack_energy_movement")
            pass
        else:
            self.pos = new_herd_pos

    def quit_herd(self):
        self.herd.remove(self)
        if not self._alive:
            return
        if self.energy > self.pos.vegetob.density:
            destination = np.random.choice(self.world.get_adjacent(self.pos,
                                                                    flag="land"))
            self.energy -= self.age**2 * self.world.distance(self.pos, destination)
            if self.energy <= 0:
                # self.die("lack_energy_movement")
                return
            self.pos = destination
        if self.pos.herd:
            self.herd = self.pos.herd
            self.herd.add(self)
        else:
            self.herd = Herd([self], self.pos, self.world,
                             list(self.herd.tracked))
            self.pos.add_herd(self.herd)

    def choose_erbast(self, new_herd_pos):
        if (new_herd_pos.vegetob.density*self.social_attitude >
            self.pos.vegetob.density and self.energy >
            new_herd_pos.vegetob.density and
            len(self.herd)*self.social_attitude < 100):
            self.stay_with_herd(new_herd_pos)
        else:
            self.quit_herd()

    @classmethod
    def spawn(cls, pos: Cell, wrld):
        return cls(1000, 100, 0.8, pos, pos.herd, wrld)

    def die(self, reason=None):
        if not self._alive:
            raise AlreadyDeadError(f"{self} is already dead by \
{self.pos.reason_of_death}, and now {reason}")
        self._alive = False
        try:
            CAUSE_OF_DEATH[reason] += 1
        except KeyError:
            CAUSE_OF_DEATH[reason] = 1
        self.herd.remove(self)
        # this partitions randomly the energy and lifetime of the ancestor to
        # the children
        if self.energy > 5 and reason not in ["overcrowding", "hunted_down"]:
            for E, L in zip(part(self.energy, 2), part(self.lifetime*2, 2)):
                s_a = min(1, max(0.1, np.random.normal(self.social_attitude, 0.1)))
                try:
                    self.herd.add(Erbast(E, L, s_a, self.herd.pos, self.herd, self.world))
                except Exception as e:
                    print(e)

        self.pos = Graveyard(self.pos.x, self.pos.y, reason)
        del self


class Carviz(Animal):
    """Class representing a Carviz, """
    def __init__(self, energy: int, lifetime: int,
                 social_attitude: float, position: Cell, pride, world: World):
        super().__init__(energy, lifetime, social_attitude, position, world)
        self.pride = pride

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self.pride.remove(self)
        self._id = value
        self.pride.add(self)

    def stay_with_pride(self):
        self.energy -= self.world.distance(self.pos, self.pride.pos)
        if self.energy <= 0:
            # self.die("lack_energy_movement")
            return
        self.pos = self.pride.pos

    def quit_pride(self):
        self.pride.remove(self)
        if self.energy > 10:
            destination = np.random.choice(self.world.get_neighbors(self.pos,
                                                                    flag="land"))
            self.energy -= self.world.distance(self.pos, destination)
            if self.energy <= 0:
                # self.die()
                return
            self.pos = destination
        if self.pos.pride:
            self.pride = self.pos.pride
            self.pride.add(self)
        else:
            self.pride = Pride([self], self.pos, self.world,
                               list(self.pride.tracked))
            self.pos.add_pride(self.pride)

    def choose_carviz(self):
        if np.random.random() > (1-self.social_attitude)/100:
            self.stay_with_pride()
        else:
            self.quit_pride()

    @classmethod
    def spawn(cls, pos: Cell, wrld):
        return cls(100, 10, 0.8, pos, pos.pride, wrld)

    def die(self, reason=None):
        if not self._alive:
            inpride = []
            for row in self.world.grid:
                for cell in row:
                    if cell.pride and self in cell.pride.members:
                        inpride.append(cell.pride)
            raise AlreadyDeadError(f"{self} is already dead by \
{self.pos.reason_of_death}, and now {reason}\n\nself was in prides: \
{inpride}\n and its pride is {self.pride} or {self.pos.pride if self.pos.pride else None}")
        self._alive = False
        # try:
        #     self.pride.members.remove(self)
        # except ValueError:
        #     print("OH NO!!!")
        #     if len(self.pride.members) == 0:
        #         self.pos.remove_pride()
        #         del self.pride
        #     else:
        #         del self.pride.members[-1]
        self.pride.remove(self)
        # this partitions randomly the energy and lifetime of the ancestor to
        # the children
        if self.energy > 5 and reason not in ["overcrowding", "fight"]:
            number = np.random.randint(2, 4)
            # print(self.energy*2, 2, "energy")
            # print(self.lifetime*2, 2, "lifetime")
            for E, L in zip(part(self.energy*2, 3), part(self.lifetime*3, 3)):
                s_a = min(1, max(0.1, np.random.normal(self.social_attitude, 0.1)))
                try:
                    self.pride.add(Carviz(E, L, s_a, self.pride.pos, self.pride, self.world))
                except AssertionError:
                    pass

        self.pos = Graveyard(self.pos.x, self.pos.y, reason)
        del self


class Group:
    """Class representing a group of Animals, parent of herd and Pride"""
    def __init__(self, pos: Cell, world: World, members: Carviz or Erbast,
                 tracked=[]):
        self.pos = pos
        self.world = world
        self._members = []
        self.members_id = [m.id for m in members]
        self.past_cells = []
        self.memory = {}
        self.tracked = tracked

    def __repr__(self):
        return f"{self.__class__.__name__}(({self.pos.x}, {self.pos.y}), {self.members_id})"

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for member in self.members:
            if member not in other.members:
                return False
        return True

    def __len__(self):
        return len(self.members_id)

    def __getitem__(self, key):
        global ANIMALS
        return ANIMALS[self.members_id[key]]

    def add(self, member: Carviz or Erbast):
        # print(f"ADDING {member.id} to {self}")
        # self.members.append(member)
        self.members_id.append(member.id)

    def remove(self, member: Carviz or Erbast):
        # self.members.remove(member)
        # self.members = [m for m in self.members if m != member]
        self.members_id = [m for m in self.members_id if m != member.id]
        # self.members_id.remove(member.id)

    def join(self, other_group):
        # self.members += other_group.members
        self.members_id += other_group.members_id
        for key in other_group.memory:
            if key in self.memory and np.random.random() < 0.5:
                self.memory[key] = other_group.memory[key]
            else:
                self.memory[key] = other_group.memory[key]
        del other_group
        return self

    @property
    def members(self):
        global ANIMALS
        for member_id in self.members_id:
            yield ANIMALS[member_id]

    def add_energy(self, energy):
        extra = 0
        for m, en in zip(self.members, part(energy, len(self))):
            en += extra
            extra = max(0, m.energy+en-100)
            en -= extra
            m.energy += en

    def get_energy(self):
        return sum([m.energy for m in self.members])

    def get_sa(self):
        return np.array([m.social_attitude for m in self.members]).mean()

    def get_champion(self):
        return max(self.members, key=lambda m: m.energy if m._alive else 0)

    def clean(self, max_id):
        for member_id in list(self.members_id):
            if member_id >= max_id:
                self.members_id.remove(member_id)



class Herd(Group):
    """Class representing a group of Erbast"""
    def __init__(self, erbasts: list[Erbast], position: Cell, world: World,
                 tracked=[]):
        super().__init__(position, world, erbasts, tracked)
        self.pos.add_herd(self)

    def check_near_cells(self):
        # Can still go to far cells but each time is preferable to stay near, if
        # less than a threshold it gets forgotten
        self.memory = {c: d/2 for c, d in self.memory.items() if d > 1}
        for cell in self.world.get_neighbors(self.pos):
            if cell.vegetob:
                self.memory[cell] = cell.vegetob.density

    def memory_value(self, cell):
        if cell in self.memory: return self.memory[cell]
        return 1

    def move_towards(self, new_cell):
        if self.world.distance(self.pos, new_cell) <= 1:
            self.move(self.pos)
            return
        neigh = self.world.get_neighbors(self.pos, flag="land")
        actual_new_cell = neigh[np.argmin([self.world.distance(new_cell, n) for n in neigh])]
        self.move(actual_new_cell)

    def move(self, new_cell):
        for erbast in list(self.members):
            if erbast._alive:
                erbast.choose_erbast(new_cell)
            else:
                self.remove(erbast)
        if new_cell == self.pos:
            for erbast in self.members:
                erbast.graze(min(1, self.pos.vegetob.density/len(self)))
            self.pos.vegetob.density -= min(len(self), self.pos.vegetob.density)
        else:
            self.pos.remove_herd()
            self.pos = new_cell
            self.pos.add_herd(self)

    def choose(self, i):
        self.check_near_cells()
        if self.pos.vegetob.density < self.get_energy() and len(self.memory) > 0:
            self.move_towards(max(self.memory, key=self.memory_value))
        else:
            self.move(self.pos)
        if self.tracked:
            self.tracked.append((i, self.pos))

    def grow(self, cell):
        assert cell == self.pos, "Trying to grow in a cell that is not the current one"
        if len(self) == 0:
            self.pos.herd = None
        else:
            population = cell.population()
            for erbast in list(cell.herd.members):
                if erbast._alive:
                    erbast.grow(population)
                else:
                    cell.herd.remove(erbast)


class Pride(Group):
    def __init__(self, carvizes: list[Carviz], position: Cell, world: World,
                 tracked=[]):
        super().__init__(position, world, carvizes, tracked)
        self.pos.add_pride(self)

    def check_near_cells(self):
        self.memory = {c: e/2 for c, e in self.memory.items() if e > 0.5}
        for cell in self.world.get_neighbors(self.pos, self.world.num_cells//10):
            if cell.herd:
                self.memory[cell] = cell.herd.get_energy()
            elif cell in self.memory:
                self.memory[cell] = 0


    def move_towards(self, new_cell):
        if self.world.distance(self.pos, new_cell) <= 1:
            self.move(self.pos)
            return
        neigh = self.world.get_adjacent(self.pos, flag="land")
        actual_new_cell = neigh[np.argmin([self.world.distance(new_cell, n) for n in neigh])]
        self.move(actual_new_cell)


    def move(self, new_cell):
        self.pos.remove_pride()
        self.pos = new_cell
        self.pos.add_pride(self)

    def choose(self, i):
        self.check_near_cells()
        if self.pos.herd:
            self.hunt()
        else:
            self.move_towards(max(self.memory, key=self.memory.get,
                                  default=np.random.choice(self.world.get_neighbors(self.pos, flag="land"))))
        for carviz in list(self.members):
            if carviz._alive:
                carviz.choose_carviz()
            else:
                self.remove(carviz)
        if self.tracked:
            self.tracked.append((i, self.pos))

    def fight(self, other_pride):
        while len(self)*len(other_pride) > 0:
            self_champion = self.get_champion()
            other_champion = other_pride.get_champion()
            try:
                if self_champion.energy > other_champion.energy:
                    self_champion.energy -= other_champion.energy/2
                    self_champion.die("fight")
                else:
                    other_champion.energy -= self_champion.energy/2
                    other_champion.die("fight")
            except AlreadyDeadError:
                print("Just killed dead carviz, stopping the fight...")
                break
        if len(self) > 0:
            del other_pride
            return self
        del self
        return other_pride

    def hunt(self):
        prey = self.pos.herd.get_champion()
        if prey.energy * np.random.random() < self.get_energy() * np.random.random():
            self.add_energy(prey.energy)
            try:
                prey.die("hunted_down")
            except AlreadyDeadError:
                print("Just killed dead erbast, continuing the hunt (likely \
he got killed also by a different pride)...")
        else:
            # damage inflicted by unsuccessful hunt
            self.get_champion().energy -= prey.energy
            if self.get_energy() > self.pos.herd.get_champion().energy:
                self.hunt()

    def grow(self, cell):
        assert cell == self.pos, "Trying to grow in a cell that is not the current one"
        if len(self) == 0:
            self.pos.pride = None
        else:
            population = cell.population()
            for carviz in list(cell.pride.members):
                if carviz._alive:
                    carviz.grow(population)
                else:
                    cell.pride.remove(carviz)
