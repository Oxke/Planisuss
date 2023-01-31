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
        self.grid = [[Cell(x, y) for x in range(self.num_cells)]
                     for y in range(self.num_cells)]
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
        start_cell = self.grid[rd.randint(0, self.num_cells)][rd.randint(0, self.num_cells)]
        pangea = [start_cell]
        done = []
        while len(pangea) > 0:
            cell = pangea.pop()
            cell.spawn_vegetob(50)
            done.append(cell)
            for neighbor in self.get_neighbors(cell):
                if neighbor in done:
                    continue
                if rd.random() < 0.3:
                    pangea.append(neighbor)
                else:
                    done.append(cell)
                    neighbor.water = True


if __name__ == "__main__":
    world = World()
    for x in range(world.num_cells):
        for y in range(world.num_cells):
            if world.grid[x][y].water:
                plt.scatter(x, y, color="blue")
            else:
                plt.scatter(x, y, color="green")
    plt.show()

