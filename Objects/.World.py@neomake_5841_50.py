#!/usr/bin/env python
from Cell import Cell
NEIGHBORHOOD = 2
NUM_CELLS = 10


class World:
    """Class representing the world"""
    def __init__(self):
        self.num_cells = NUM_CELLS
        self.near = NEIGHBORHOOD
        self.grid = [[Cell(x, y) for x in range(self.num_cells)]
                     for y in range(self.num_cells)]
        self.start_life()

    def get_neighbors(self, cell: Cell):
        """Returns the neighborhood of a cell"""
        neighborhood = []
        for x in range(cell.x-self.near, cell.x+self.near+1):
            for y in range(cell.y-self.near, cell.y+self.near+1):
                if 0 <= min(x, y) <= max(x, y) < self.num_cells:
                    neighborhood.append(self.grid[x][y])
        return neighborhood

    def start_life(self):
        """Starts the life of the world"""
        

