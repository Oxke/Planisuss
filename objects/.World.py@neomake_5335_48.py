#!/usr/bin/env python
import numpy as np
from numpy import random as rd
from Cell import Cell
from matplotlib import pyplot as plt
NEIGHBORHOOD = 2
NUM_CELLS = 10


class World:
    """Class representing the world"""
    def __init__(self):
        self.num_cells = NUM_CELLS
        self.grid = [[Cell(x, y) for y in range(self.num_cells)]
                     for x in range(self.num_cells)]
        self.start_life()

    def get_neighbors(self, cell: Cell, near: int = NEIGHBORHOOD):
        """Returns the neighborhood of a cell"""
        neighborhood = []
        for x in range(cell.x-near, cell.x+near+1):
            for y in range(cell.y-near, cell.y+near+1):
                if 0 <= min(x, y) <= max(x, y) < self.num_cells:
                    neighborhood.append(self.grid[x][y])
        return neighborhood

    def get_adjacent(self, cell: Cell):
        """Returns the adjacent cells of a cell"""
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
        """Starts the life of the world"""
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
                    p -= self.num_cells**2/100000
                    pangea.append(neighbor)
                else:
                    done.append(neighbor)
                    neighbor.water = True

    def plot(self, title="World"):
        """Plots the world"""
        water = [[cell.water for cell in row] for row in self.grid]
        vegetob = [[cell.vegetob is not None for cell in row] for row in self.grid]
        plt.title(title)
        plt.imshow(np.array(vegetob) + np.array(water)/2)
        plt.show()


if __name__ == "__main__":
    world = World()
    #    for x in range(world.num_cells):
    #        for y in range(world.num_cells):
    #            if world.grid[x][y].water:
    #                plt.scatter(x, y, color="blue")
    #            elif world.grid[x][y].vegetob is None:
    #                plt.scatter(x, y, color="black")
    #            else:
    #                plt.scatter(x, y, color="green")
    world.plot()