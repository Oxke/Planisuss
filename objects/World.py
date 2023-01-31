#!/usr/bin/env python
import numpy as np
from numpy import random as rd
from Cell import Cell
from matplotlib import pyplot as plt
NEIGHBORHOOD = 2
NUM_CELLS = 100


class World:
    """Class representing the world"""
    def __init__(self):
        self.num_cells = NUM_CELLS
        self.grid = [[Cell(x, y) for y in range(self.num_cells)]
                     for x in range(self.num_cells)]
        self.pseudocenter = self.start_life()

    def __repr__(self):
        return "World(" + str(self.num_cells) + ", " + str(self.pseudocenter) + ")"

    def distance(self, cell1, cell2):
        """Returns the distance between two cells"""
        return max(abs(cell1.x-cell2.x), abs(cell1.y-cell2.y))

    def get_neighbors(self, cell: Cell, near: int = NEIGHBORHOOD):
        """Returns the neighborhood of a cell"""
        neighborhood = []
        for x in range(cell.x-near, cell.x+near+1):
            for y in range(cell.y-near, cell.y+near+1):
                if 0 <= min(x, y) <= max(x, y) < self.num_cells:
                    neighborhood.append(self.grid[x][y])
        return neighborhood

    def get_adjacent(self, cell: Cell):
        """Returns the adjacent cells of a cell
        Context: I didn't like a continent where the cells were not connected,
        even though in theory they are since the "circle" of radius 1 is
        actually a square of side 3 around the cell. For the continent instead
        i'm using this other measure, where the distance is the minimum number
        of steps to connect two cells passing only through adjacent cells. This
        is a measure that is more similar to the one used in the game of life
        and I might consider in future including it as on option, since I just
        need to change the get_neighbors function.
        In particular the continent is now connected."""
        adjacent_cells = []
        if cell.x > 0:
            adjacent_cells.append(self.grid[cell.x-1][cell.y])
        if cell.x < self.num_cells-1:
            adjacent_cells.append(self.grid[cell.x+1][cell.y])
        if cell.y > 0:
            adjacent_cells.append(self.grid[cell.x][cell.y-1])
        if cell.y < self.num_cells-1:
            adjacent_cells.append(self.grid[cell.x][cell.y+1])
        return adjacent_cells

    def start_life(self):
        """Starts the life of the world, generating randomly a world"""
        x, y = rd.randint(0, self.num_cells), rd.randint(0, self.num_cells)
        start_cell = self.grid[x][y]
        pangea = [start_cell]
        done = []
        p = 1
        while len(pangea) > 0:
            cell = pangea.pop(0)
            if cell in done:
                continue
            cell.spawn_vegetob(rd.randint(0, 100))
            done.append(cell)
            for neighbor in self.get_adjacent(cell):
                if neighbor in done:
                    continue
                if rd.random() < p:
                    p -= 1 / self.num_cells**2
                    pangea.append(neighbor)
                else:
                    done.append(neighbor)
                    neighbor.water = True
        start_cell.add_herd(None, self)
        # for cell in grid, if not in done make it water
        for row in self.grid:
            for cell in row:
                # this is not necessary, but it makes the world more realistic,
                # since there are not little puddles of water in the middle of
                # the land, there are only lakes bigger than a cell
                if cell.water and all(c.vegetob is not None for c in self.get_adjacent(cell)):
                    cell.water = False
                    cell.spawn_vegetob(rd.randint(0, 100))
                    continue
                if cell not in done:
                    cell.water = True
        return start_cell

    def day(self):
        """Runs through the day's events"""
        # Growing: the vegetob grows everywhere
        for row in self.grid:
            for cell in row:
                if cell.vegetob is not None:
                    cell.vegetob.grow()
        # Movement: The individuals of animal species decide if move in another
        # area. Movement is articulated as individual and social group movement
        for row in self.grid:
            for cell in row:
                if cell.herd is not None:
                    cell.herd.choose()
        # Grazing: The animals which did not move can graze the Vegetob in the
        # area. Included in previous step
        # TODO: Struggle: Carviz insisting on the same area can fight or hunt
        # Spawning: Individuals of animal species can generate their offspring
        for row in self.grid:
            for cell in row:
                if cell.herd is not None:
                    cell.herd.proliferate()

    def plot(self, title="Planisuss"):
        """Plots the world"""
        # water = [[cell.water for cell in row] for row in self.grid]
        vegetob = [[0 if cell.vegetob is None else cell.vegetob.density/100
                    for cell in row] for row in self.grid]
        erbasts = [[0 if cell.herd is None else len(cell.herd)/16
                   for cell in row] for row in self.grid]
        carvizes = [[cell.n_carvizes() for cell in row] for row in self.grid]
        plt.title(title)
        # plt.imshow(np.dstack((np.zeros((self.num_cells, self.num_cells)),
        #                       vegetob, water)))
        plt.imshow(np.dstack((carvizes, erbasts, vegetob)))
        plt.xlabel("x")
        plt.ylabel("y")
        # write next to the image the total number of animals
        plt.text(-32, 20, "Erbasts: " + str(self.total_animals("erbasts")))
        plt.text(-32, 30, "Carvizes: " + str(self.total_animals("carvizes")))
        plt.text(-32, 40, "Total: " + str(self.total_animals()))
        plt.show()

    def total_animals(self, flag=None):
        res = 0
        for row in self.grid:
            for cell in row:
                if cell.herd is not None and flag in [None, "erbasts"]:
                    res += len(cell.herd)
                res += cell.n_carvizes() if flag in [None, "carvizes"] else 0
        return res


if __name__ == "__main__":
    world = World()
    i = 0
    while True:
        if i % 1000 == 0:
            world.plot()
        world.day()
        i += 1
