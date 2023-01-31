#!/usr/bin/env python
from numpy import random as rd
from Cell import Cell
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
        start_cell = self.grid[rd.randint(0, self.num_cells)]
                    [rd.randint(0, self.num_cells)]
        start_cell.spawn_vegetob(50)
        for cell in self.get_neighbors(start_cell):
            cell.spawn_vegetob(10)

