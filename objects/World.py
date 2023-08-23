#!/usr/bin/env python
# from matplotlib.animation import FuncAnimation
from Interactive_Animation import Interactive_Animation
from matplotlib.widgets import Button
from matplotlib import animation
import matplotlib as mpl
import numpy as np
from numpy import random as rd
from Cell import Cell
from matplotlib import pyplot as plt
from errors import *

DAYS = 1000

NUM_CELLS = 50
NEIGHBORHOOD = 1
DAY_BY_DAY_RESULTS = []


class World:
    """Class representing the world"""
    def __init__(self, num_cells, neighborhood):
        self.num_cells = num_cells
        self.neighborhood = neighborhood
        self.grid = [[Cell(x, y) for y in range(self.num_cells)]
                     for x in range(self.num_cells)]
        self.pseudocenter = self.start_life()
        self.fig, self.ax = self.plot_new(0, create=True)

    def __repr__(self):
        return f"World({str(self.num_cells)}, {str(self.pseudocenter)})"

    def distance(self, cell1, cell2):
        """Returns the distance between two cells"""
        return np.linalg.norm([abs(cell1.x-cell2.x), abs(cell1.y-cell2.y)])

    def get_neighbors(self, cell: Cell, near=None, flag=None):
        if near is None: near=self.neighborhood
        """Returns the neighborhood of a cell"""
        neighborhood = []
        for x in range(cell.x-near, cell.x+near+1):
            for y in range(cell.y-near, cell.y+near+1):
                if 0 <= min(x, y) <= max(x, y) < self.num_cells:
                    if flag is None:
                        neighborhood.append(self.grid[x][y])
                    elif flag == "water":
                        if self.grid[x][y].water:
                            neighborhood.append(self.grid[x][y])
                    elif flag == "land":
                        if not self.grid[x][y].water:
                            neighborhood.append(self.grid[x][y])
        return neighborhood

    def get_adjacent(self, cell: Cell, flag=None):
        """Returns the adjacent cells of a cell
        Context: I didn't like a continent where the cells were not connected,
        even though in theory they are since the "circle" of radius 1 is
        actually a square of side 3 around the cell. For the continent instead
        i'm using the measure where the distance is the minimum number
        of steps to connect two cells passing only through adjacent cells. This
        is a measure that is more similar to the one used in the game of life
        and I might consider in future including it as on option, since I just
        need to change the get_neighbors function.
        In particular the continent is now connected."""
        adjacent_cells = []
        if cell.x > 0 and (flag is None or (flag == "land" and not self.grid[cell.x-1][cell.y].water)):
            adjacent_cells.append(self.grid[cell.x-1][cell.y])
        if cell.x < self.num_cells-1 and (flag is None or (flag == "land" and not self.grid[cell.x+1][cell.y].water)):
            adjacent_cells.append(self.grid[cell.x+1][cell.y])
        if cell.y > 0 and (flag is None or (flag == "land" and not self.grid[cell.x][cell.y-1].water)):
            adjacent_cells.append(self.grid[cell.x][cell.y-1])
        if cell.y < self.num_cells-1 and (flag is None or (flag == "land" and not self.grid[cell.x][cell.y+1].water)):
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
        vegetob = [[0 if cell.vegetob is None else cell.vegetob.density/100
                    for cell in row] for row in self.grid]

        z = np.zeros((self.num_cells, self.num_cells))
        status = np.dstack((z, z, vegetob))
        DAY_BY_DAY_RESULTS.append((status, (0, 0, 0)))

        start_cell.add_herd(None, self)
        carviz_cell = np.random.choice(self.get_neighbors(start_cell,
                                                          self.num_cells, "land"))
        carviz_cell.add_pride(None, self)
        carviz_cell = np.random.choice(self.get_neighbors(carviz_cell,
                                                          self.num_cells, "land"))
        carviz_cell.add_pride(None, self)
        carviz_cell = np.random.choice(self.get_neighbors(carviz_cell,
                                                          self.num_cells, "land"))
        carviz_cell.add_pride(None, self)
        return start_cell

    def day(self, frame):
        """Runs through the day's events"""
        if frame <= len(DAY_BY_DAY_RESULTS)-1:
            self.plot_old(frame)
        else:
            # Growing: the vegetob grows everywhere
            for row in self.grid:
                for cell in row:
                    population = cell.population()
                    if cell.vegetob: cell.vegetob.grow()
                    if cell.herd:
                        if len(cell.herd) == 0:
                            cell.herd = None
                        else:
                            for erbast in list(cell.herd.members):
                                if erbast._alive:
                                    erbast.grow(population)
                                else:
                                    cell.herd.members.remove(erbast)
                    if cell.pride:
                        if len(cell.pride) == 0:
                            cell.pride = None
                        else:
                            for carviz in list(cell.pride.members):
                                if carviz._alive:
                                    carviz.grow(population)
                                else:
                                    cell.pride.members.remove(carviz)
            # Movement: The individuals of animal species decide if move in another
            # area. Movement is articulated as individual and social group movement
            for row in self.grid:
                for cell in row:
                    if cell.herd: cell.herd.choose()
                    if cell.pride: cell.pride.choose()
            # Grazing: The animals which did not move can graze the Vegetob in the
            # area. Included in previous step
            # Spawning: Individuals of animal species can generate their offspring
            # for row in self.grid:
            #     for cell in row:
            #         if cell.herd is not None:
            #             pass
            #             # cell.herd.proliferate()
            self.plot_new(frame)

    def plot_old(self, frame):
        self.fig.suptitle(f"Planisuss: Day {frame}", fontsize=24)
        self.ax[0].clear()
        self.ax[1].clear()
        status = DAY_BY_DAY_RESULTS[frame][0]
        self.ax[0].imshow(status)
        num_erbasts, num_carvizes, num_total = DAY_BY_DAY_RESULTS[frame][1]
        self.ax[1].axvline(x=frame, c="r", lw=2, label="TODAY")
        self.ax[1].plot([x[1][0] for x in DAY_BY_DAY_RESULTS], label=f"Erbasts: {num_erbasts}")
        self.ax[1].plot([x[1][1] for x in DAY_BY_DAY_RESULTS], label=f"Carvizes: {num_carvizes}")
        # self.ax[1].plot([x[1][2] for x in DAY_BY_DAY_RESULTS], label=f"Total: {num_total}")
        self.ax[1].legend()

    def plot_new(self, frame, create=False):
        """Plots the world"""
        # water = [[cell.water for cell in row] for row in self.grid]
        vegetob = [[0 if cell.vegetob is None else cell.vegetob.density/100
                    for cell in row] for row in self.grid]
        erbasts = [[0 if cell.herd is None else min(len(cell.herd)/4, 1.0)
                    for cell in row] for row in self.grid]
        carvizes = [[0 if cell.pride is None else min(len(cell.pride)/4, 1.0)
                    for cell in row] for row in self.grid]
        if create:
            fig, ax = plt.subplots(1, 2, figsize=(20, 10))
            fig.suptitle("Planisuss: Day 0", fontsize=24)
            ax[0].get_xaxis().set_visible(False)
            ax[0].get_yaxis().set_visible(False)
            return fig, ax
        self.fig.suptitle(f"Planisuss: Day {frame}", fontsize=24)
        self.ax[1].clear()
        self.ax[0].clear()
        status = np.dstack((carvizes, erbasts, vegetob))
        self.ax[0].imshow(status)

        num_erbasts = self.total_animals("erbasts")
        num_carvizes = self.total_animals("carvizes")
        # num_total = self.total_animals()

        DAY_BY_DAY_RESULTS.append((status, (num_erbasts, num_carvizes,
                                            num_erbasts+num_carvizes)))

        self.ax[1].plot([x[1][0] for x in DAY_BY_DAY_RESULTS], label=f"Erbasts: {num_erbasts}")
        self.ax[1].plot([x[1][1] for x in DAY_BY_DAY_RESULTS], label=f"Carvizes: {num_carvizes}")
        # self.ax[1].plot([x[1][2] for x in DAY_BY_DAY_RESULTS], label=f"Total: {num_total}")
        self.ax[1].legend()
        self.ax[1].set_xlabel("Days")
        self.ax[1].set_ylabel("Number of animals")
        if num_erbasts+num_carvizes == 0 and frame != 0:
            raise TotalExtinction

    def run(self, days=1000):
        ani = Interactive_Animation(self.fig, self.day, mini=0, maxi=10000,
                                    cache_frame_data=False, interval=10)
        return ani

    def total_animals(self, flag=None):
        """flag can be None, "erbasts" or "carvizes" and returns respectively
        the total number of animals in the world, the total number of erbasts
        and the total number of carvizes"""
        res = 0
        for row in self.grid:
            for cell in row:
                if cell.herd and flag in [None, "erbasts"]:
                    res += len(cell.herd)
                if cell.pride and flag in [None, "carvizes"]:
                    res += len(cell.pride)
        return res


if __name__ == "__main__":
    world = World(NUM_CELLS, NEIGHBORHOOD)
    anim = world.run(300)
    plt.show()

