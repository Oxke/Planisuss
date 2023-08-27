#!/usr/bin/env python
# from matplotlib.animation import FuncAnimation
from Visualization import Interactive_Animation
from matplotlib.widgets import Button
from matplotlib import animation
import matplotlib as mpl
import numpy as np
from numpy import random as rd
from Objects.Cell import Cell
from matplotlib import pyplot as plt
from errors import *
from variables import *

class World:
    """Class representing the world"""
    def __init__(self, num_cells, neighborhood):
        self.num_cells = num_cells
        self.neighborhood = neighborhood
        self.grid = np.array([[Cell(x, y) for y in range(self.num_cells)]
                     for x in range(self.num_cells)])
        self.pseudocenter = self.start_life()
        self.fig, self.ax = self.create_plot()

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
                        neighborhood.append(self.grid[x, y])
                    elif flag == "water":
                        if self.grid[x, y].water:
                            neighborhood.append(self.grid[x, y])
                    elif flag == "land":
                        if not self.grid[x, y].water:
                            neighborhood.append(self.grid[x, y])
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
        x, y = rd.randint(0, self.num_cells, 2)
        start_cell = self.grid[x, y]
        pangea = [start_cell]
        done = []
        p = 1
        while len(pangea) > 0:
            cell = pangea.pop(0)
            if cell in done:
                continue
            cell.spawn_vegetob(rd.randint(0, 100))
            cell.add_herd(None, self)
            # cell.add_pride(None, self)
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

        # start_cell.add_herd(None, self)

        water = np.array([[cell.water for cell in row] for row in self.grid])
        status = np.dstack((water, water, vegetob+water))
        DAY_BY_DAY_RESULTS.append((status, (0, 0, 0)))

        # start_cell.add_herd(None, self)
        # carviz_cell = np.random.choice(self.get_neighbors(start_cell,
        #                                                   self.num_cells, "land"))
        # carviz_cell.add_pride(None, self)
        # carviz_cell = np.random.choice(self.get_neighbors(carviz_cell,
        #                                                   self.num_cells, "land"))
        # carviz_cell.add_pride(None, self)
        # carviz_cell = np.random.choice(self.get_neighbors(carviz_cell,
        #                                                   self.num_cells, "land"))
        # carviz_cell.add_pride(None, self)
        return start_cell

    def day(self, frame, to_track=None, cancel=False):
        """Main function for the simulation, it runs a day or plots a previous
        day if already simulated"""
        if to_track:
            c = self.grid[to_track]
            if c.vegetob: c.vegetob.density=100
            if c.herd: c.herd.tracked = [] if c.herd.tracked else [(frame, c)]
            if c.pride: c.pride.tracked = [] if c.pride.tracked else [(frame, c)]

        if cancel:
            for row in self.grid:
                for cell in row:
                    if cell.herd: cell.herd.tracked = []
                    if cell.pride: cell.pride.tracked = []

        self.plot(frame)

    def day_events(self, frame):
        global ANIMALS
        """Function defining the events of the day"""
        # Growing: the vegetob grows everywhere, in this phase also all animals
        # age and eventually die.
        for row in self.grid:
            for cell in row:
                population = cell.population()
                if cell.vegetob: cell.vegetob.grow()
                # if cell.herd: cell.herd.grow(cell)
                # if cell.pride: cell.pride.grow(cell)
        for animal in ANIMALS:
            if animal.alive:
                animal.grow()
        # Movement: The individuals of animal species decide if move in another
        # area. Movement is articulated as individual and social group movement,
        # in this phase it is also included Struggle, Fighting and Hunting.
        for row in self.grid:
            for cell in row:
                if cell.herd: cell.herd.choose(frame)
                if cell.pride: cell.pride.choose(frame)

    def update_animals_indexes(self):
        global ANIMALS
        """Updates the indexes of the animals"""
        i = 0
        print(len(ANIMALS), end=" -> ")
        for animal in list(ANIMALS):
            if not animal.alive:
                del ANIMALS[i]
            else:
                animal.id = i
                i += 1

        for row in self.grid:
            for cell in row:
                if cell.herd:
                    cell.herd.clean(len(ANIMALS))
                if cell.pride:
                    cell.pride.clean(len(ANIMALS))

        print(len(ANIMALS))

    def plot_old(self, frame):
        self.fig.suptitle(f"Planisuss: Day {frame}", fontsize=24)
        self.ax[0].clear()
        self.ax[0].axis("off")
        self.ax[1].clear()
        status = DAY_BY_DAY_RESULTS[frame][0]
        self.ax[0].imshow(status)
        num_erbasts, num_carvizes, num_total = DAY_BY_DAY_RESULTS[frame][1]
        self.ax[1].axvline(x=frame, c="b", lw=2, label="TODAY")
        self.ax[1].plot([x[1][0] for x in DAY_BY_DAY_RESULTS], 'g', label=f"Erbasts: {num_erbasts}")
        self.ax[1].plot([x[1][1] for x in DAY_BY_DAY_RESULTS], 'r', label=f"Carvizes: {num_carvizes}")
        self.ax[1].legend()

    def create_plot(self):
        return plt.subplots(1, 2, figsize=(20, 10))

    def plot(self, frame, create=False):
        """Plots the world"""

        # Time in years, months, days format
        ez_time = ""
        if frame >= 365:
            ez_time += f"({frame//365} years"
        if frame%365 >= 30:
            ez_time = ", " if ez_time else "("
            ez_time += f"{frame%365//30} months"
        if frame%30 >= 1 and ez_time:
            ez_time += f", {frame%30} days"
        if ez_time:
            ez_time += ")"

        if len(DAY_BY_DAY_RESULTS) <= frame:
            if not frame % 100:
                self.update_animals_indexes()
            self.day_events(frame)

            water = np.array([[cell.water for cell in row] for row in self.grid])
            vegetob = np.array([[0 if cell.vegetob is None else cell.vegetob.density/100
                        for cell in row] for row in self.grid])
            erbasts = np.array([[0 if cell.herd is None else min(len(cell.herd)/4, 1.0)
                        for cell in row] for row in self.grid])
            carvizes = np.array([[0 if cell.pride is None else min(len(cell.pride)/4, 1.0)
                        for cell in row] for row in self.grid])
            num_erbasts = self.total_animals("erbasts")
            num_carvizes = self.total_animals("carvizes")

            status = np.dstack((carvizes+water, erbasts+water, vegetob+water))
            DAY_BY_DAY_RESULTS.append((status, (num_erbasts, num_carvizes)))
        else:
            status, (num_erbasts, num_carvizes) = DAY_BY_DAY_RESULTS[frame]


        self.fig.suptitle(f"Planisuss: Day {frame} {ez_time}", fontsize=24)
        self.ax[0].clear()
        self.ax[0].axis("off")
        self.ax[0].imshow(status)

        self.ax[1].clear()
        self.ax[1].plot([x[1][0] for x in DAY_BY_DAY_RESULTS], 'g',
                        label=f"Erbasts: {num_erbasts}")
        self.ax[1].plot([x[1][1] for x in DAY_BY_DAY_RESULTS], 'r',
                        label=f"Carvizes: {num_carvizes}")
        self.ax[1].axvline(x=frame, c="b", lw=2, label="TODAY")

        self.ax[1].legend()
        self.ax[1].set_xlabel("Days")
        self.ax[1].set_ylabel("Number of animals")

        if num_erbasts+num_carvizes == 0 and frame != 0:
            self.fig.canvas.draw_idle()
            fig, ax = plt.subplots()
            fig.suptitle("(Animal) Life got extinct, here are the causes:",
                         fontsize=16)
            ax.pie(CAUSE_OF_DEATH.values(), labels=CAUSE_OF_DEATH.keys())
            plt.show()
            raise TotalExtinction

        # showing the tracked groups
        for row in self.grid:
            for cell in row:
                if cell.herd and cell.herd.tracked:
                    X = [el[1].x for el in cell.herd.tracked if el[0] <= frame]
                    Y = [el[1].y for el in cell.herd.tracked if el[0] <= frame]
                    self.ax[0].plot(Y, X, "go-", markersize=6, lw=3)
                if cell.pride and cell.pride.tracked:
                    X = [el[1].x for el in cell.pride.tracked if el[0] <= frame]
                    Y = [el[1].y for el in cell.pride.tracked if el[0] <= frame]
                    self.ax[0].plot(Y, X, "ro-", markersize=6, lw=3)

    def run(self, days=1000):
        ani = Interactive_Animation(self.fig, self.ax, self.day, mini=0,
                                    maxi=days,
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

    def total_energy(self, flag=None):
        res = 0
        for row in self.grid:
            for cell in row:
                if cell.herd and flag in [None, 'erbasts']:
                    res += cell.herd.get_energy()
                if cell.pride and flag in [None, 'carvizes']:
                    res += cell.pride.get_energy()
        return res

