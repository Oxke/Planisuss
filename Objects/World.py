#!/usr/bin/env python
# from matplotlib.animation import FuncAnimation
import tkinter as tk
from Visualization import Interactive_Animation
from matplotlib.widgets import Button
from matplotlib import animation
import matplotlib as mpl
import numpy as np
from numpy import random as rd
from Objects.Cell import Cell
from matplotlib import pyplot as plt
from errors import TotalExtinction
from variables import DAY_BY_DAY_RESULTS, ERBASTS, CARVIZES, CAUSE_OF_DEATH

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
        """Returns the neighborhood of a cell, according to the distance defined"""
        neighborhood = []
        for x in range(cell.x-near, cell.x+near+1):
            for y in range(cell.y-near, cell.y+near+1):
                if 0 <= min(x, y) <= max(x, y) < self.num_cells and self.distance(cell, self.grid[x, y]) <= near:
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
            cell.add_pride(None, self)
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

        water = np.array([[cell.water for cell in row] for row in self.grid])
        status = np.dstack((water, water, vegetob+water))
        DAY_BY_DAY_RESULTS.append((status, (0, 0)))
        return start_cell

    def day(self, frame, info=None, change_geology=[], invert=False,
            bomb=None, big=False, track_cancel=False, revive=None):
        """Main function for the simulation, it runs a day or plots a previous
        day if already simulated
        Args:
            frame: the day to simulate or plot

            info: the cell of which to show the info (about herd and/or pride
                living there etc)

            change_geology: a list of coordinates of cells to change the
                geology, i.e. to make them water or land, default makes water
                land, unless invert is True

            invert: if True, the change_geology list is used to make land water

            bomb: destroys te cells near to the coordinates given

            big: if True, the bomb is bigger (radius approximately 1/3 of the
                world size, wrt to the default 1/10)

            revive: revives either erbasts or carvizes, respawning them randomly
                all over the map

            track_cancel: if true, cancel all the future saved history and
                status and restarts simulating from today"""

        if info:
            c = self.grid[info]
            self.show_info(c, frame)

        for coordinates in change_geology:
            c = self.grid[coordinates]
            if c.water and not invert:
                c.water = False
                c.spawn_vegetob(rd.randint(0,100))
                DAY_BY_DAY_RESULTS[frame][0][c.x, c.y, :] = 0
            elif not c.water and invert:
                c.water = True
                c.vegetob = None
                if c.herd: c.herd.suppress()
                if c.pride: c.pride.suppress()
                DAY_BY_DAY_RESULTS[frame][0][c.x, c.y, :] = 1

        if bomb:
            center = self.grid[bomb]
            divisor = 3 if big else 10
            for c in self.get_neighbors(center, self.num_cells//divisor):
                if c.vegetob: c.vegetob.suppress()
                if c.herd: c.herd.suppress()
                if c.pride: c.pride.suppress()
                DAY_BY_DAY_RESULTS[frame][0][c.x, c.y, :] = 1 if c.water else 0

        if track_cancel:
            # for row in self.grid:
            #     for cell in row:
            #         if cell.herd: cell.herd.tracked = []
            #         if cell.pride: cell.pride.tracked = []
            del DAY_BY_DAY_RESULTS[frame:]

        if revive:
            for row in self.grid:
                for cell in row:
                    if revive == "erbasts" and not cell.water:
                        cell.add_herd(None, self)
                    elif revive == "carvizes" and not cell.water:
                        cell.add_pride(None, self)

        self.plot(frame)

    def day_events(self, frame):
        global ERBASTS, CARVIZES
        """Function defining the events of the day"""
        # Growing: the vegetob grows etverywhere, in this phase also all animals
        # age and eventually die.
        for row in self.grid:
            for cell in row:
                if cell.vegetob: cell.vegetob.grow()

        for animal in ERBASTS+CARVIZES:
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
        global CARVIZES, ERBASTS
        """Updates the indexes of the animals"""
        print(f"{len(CARVIZES)}, {len(ERBASTS)}", end=" -> ")

        i = 0
        for animal in list(CARVIZES):
            if not animal.alive:
                del CARVIZES[i]
            else:
                animal.id = i
                i += 1
        i = 0
        for animal in list(ERBASTS):
            if not animal.alive:
                del ERBASTS[i]
            else:
                animal.id = i
                i += 1

        for row in self.grid:
            for cell in row:
                if cell.herd:
                    cell.herd.clean(len(ERBASTS))
                if cell.pride:
                    cell.pride.clean(len(CARVIZES))

        print(f"{len(CARVIZES)}, {len(ERBASTS)}")

    def create_plot(self):
        fig, ax = plt.subplots(1, 2, figsize=(20, 10))
        mng = plt.get_current_fig_manager()
        # mng.full_screen_toggle()
        return fig, ax

    def plot(self, frame, create=False):
        """Plots the world"""
        # Time in years, months, days format
        ez_time = ""
        if frame >= 365:
            ez_time += f"({frame//365} years"
        if frame%365 >= 30:
            ez_time += ", " if ez_time else "("
            ez_time += f"{frame%365//30} months"
        if frame%365%30 >= 1 and ez_time:
            ez_time += f", {frame%365%30} days"
        if ez_time:
            ez_time += ")"

        if len(DAY_BY_DAY_RESULTS) <= frame:
            if len(ERBASTS) + len(CARVIZES) >= 50000:
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

        if num_carvizes+num_erbasts == 0 and frame != 0:
            self.plot_causes_of_death()
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

    def plot_causes_of_death(self):
        self.fig.canvas.draw_idle()
        fig, ax = plt.subplots(1, 3, figsize=(15, 7))
        fig.suptitle("(Animal) Life got extinct, here are the causes:",
                     fontsize=16)

        ax[1].set_title("Erbasts")
        erb_causes = CAUSE_OF_DEATH["Erbast"]
        ax[1].pie(erb_causes.values(), labels=erb_causes.keys())

        ax[2].set_title("Carvizes")
        car_causes = CAUSE_OF_DEATH["Carviz"]
        ax[2].pie(car_causes.values(), labels=car_causes.keys())

        ax[0].set_title("Total")
        total = {key: erb_causes.get(key, 0) + car_causes.get(key, 0) for
                 key in set(erb_causes) | set(car_causes)}
        ax[0].pie(total.values(), labels=total.keys())
        plt.show()

    def show_info(self, cell, frame):
        """Displays a little window with information about the cell, namely all
        the properties of the vegetob, herd and pride in it"""
        if cell.water:
            return
        info = ""
        if frame+1 >= len(DAY_BY_DAY_RESULTS):
            if cell.vegetob is not None:
                info += f"Vegetob:\n    density: {round(cell.vegetob.density)}%"
            if cell.herd is not None:
                info += f"""
    \nHerd ({len(cell.herd)} erbasts)):
        average energy:\t\t{0 if len(cell.herd) == 0 else round(cell.herd.get_energy()/len(cell.herd),2)}
        average age:\t\t{round(cell.herd.get_age(), 2)}
        average lifespan:\t{round(cell.herd.get_lifetime(), 2)}
        avg social attitude:\t{round(cell.herd.get_sa(), 2)} """
            if cell.pride is not None:
                info += f"""
    \nPride ({len(cell.pride)} carvizes):
        average energy:\t\t{0 if len(cell.pride) == 0 else round(cell.pride.get_energy()/len(cell.herd),2)}
        average age:\t\t{round(cell.pride.get_age(), 2)}
        average lifespan:\t{round(cell.pride.get_lifetime(), 2)}
        avg social attitude:\t{round(cell.pride.get_sa(), 2)}"""
        else:
            carvizes, erbasts, vegetob = DAY_BY_DAY_RESULTS[frame][0][cell.x, cell.y]
            if vegetob != 0:
                info += f"Vegetob: {round(vegetob*100)}%"
            if erbasts != 0:
                info += f"\nHerd: {'>=4' if erbasts == 1 else int(erbasts*4)} erbasts"
            if carvizes != 0:
                info += f"\nPride: {'>=4' if carvizes == 1 else int(carvizes*4)} carvizes"

        tk.messagebox.showinfo(title=f"Cell ({cell.x}, {cell.y})", message=info)

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
                    if len(cell.herd):
                        res += len(cell.herd)
                    else:
                        cell.remove_herd()
                if cell.pride and flag in [None, "carvizes"]:
                    if len(cell.pride):
                        res += len(cell.pride)
                    else:
                        cell.remove_pride()
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
