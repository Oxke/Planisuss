#!/usr/bin/env python
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

    def start_life(self):
        """Starts the life of the world"""
        x, y = rd.randint(0, self.num_cells), rd.randint(0, self.num_cells)
        start_cell = self.grid[x][y]
        pangea = [start_cell]
        done = []
        while len(pangea) > 0:
            cell = pangea.pop(0)
            if cell in done:
                continue
            cell.spawn_vegetob(rd.randint(0, 100))
            done.append(cell)
            self.plot()
            for neighbor in self.get_neighbors(cell, 1):
                if neighbor in done:
                    continue
                if rd.random() < 0.4:
                    pangea.append(neighbor)
                else:
                    done.append(neighbor)
                    neighbor.water = True

    def plot(self, title="World"):
        """Plots the world"""
        water = [[cell.water for cell in row] for row in self.grid]
        vegetob = [[cell.vegetob is not None for cell in row] for row in self.grid]
        plt.title(title)
        plt.imshow(vegetob)
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
