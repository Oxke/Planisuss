from IPython.display import HTML
from matplotlib.animation import FuncAnimation
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np
import pandas as pd
from scipy.signal import convolve2d

def play_game(size=(50, 50), initial_prob_life=0.5, animation_kwargs=None, marker_size=300):
    """Implementation of Conway's Game of Life

    Parameters
    ----------

    size: tuple
        Defines the size of the board (n by m)

    initial_prob_life: float
        Float in the range (0, 1] defines the initial probability of a square containing life at initialisation

    animation_kwargs: dict
        Dictionary of keyword arguments to be passed to FuncAnimation

    marker_size:
        Size of scatter plot markers

    Returns
    -------
        Instance of FuncAnimation

    """
    board = get_board(size)
    status = get_init_status(size, initial_prob_life)

    fig, axes = plt.subplots(figsize=(15, 15))
    scatter = axes.scatter(*board, animated=True, s=marker_size, edgecolor=None)
    axes.text(0.5, 0.965, "CONWAY'S ", transform=axes.transAxes, ha="right", va="bottom", color="w", fontsize=25,
              family="sans-serif", fontweight="light")
    axes.text(0.5, 0.965, "GAME OF LIFE", transform=axes.transAxes, ha="left", va="bottom", color="dodgerblue",
              fontsize=25, family="sans-serif", fontweight="bold")
    axes.set_facecolor("black")
    axes.get_xaxis().set_visible(False)
    axes.get_yaxis().set_visible(False)

    def update(frame):
        nonlocal status
        status, live_neigbors = apply_conways_game_of_life_rules(status)
        colors = get_updated_colors(status, live_neigbors)
        scatter.set_facecolor(colors)
        return scatter

    animation_kwargs = {} if animation_kwargs is None else animation_kwargs
    return FuncAnimation(fig, update, **animation_kwargs)

def get_board(size):
    xs = np.arange(0, size[0])
    ys = np.arange(0, size[1])
    board = np.meshgrid(xs, ys)
    return board

def get_init_status(size, initial_prob_life):
    status = np.random.uniform(0, 1, size=size) <= initial_prob_life
    return status

def apply_conways_game_of_life_rules(status):
    """Applies Conway's Game of Life rules given the current status of the game

    Rules:
        1. Any live cell with fewer than two live neighbors dies, as if by underpopulation.
        2. Any live cell with two or three live neighbors lives on to the next generation.
        3. Any live cell with more than three live neighbors dies, as if by overpopulation.
        4. Any dead cell with exactly three live neighbors becomes a live cell, as if by reproduction.

    Returns
    -------
    new_status, new_neighbors: tuple
        A tuple containing an array representing the new status of each square on the board, and a second array
        representing the number of neighbors post update

    """
    live_neighbors = count_live_neighbors(status)
    survive_underpopulation = live_neighbors >= 2
    survive_overpopulation = live_neighbors <= 3
    survive = status * survive_underpopulation * survive_overpopulation
    new_status = np.where(live_neighbors==3, True, survive)  # Reproduce
    new_neighbors = count_live_neighbors(new_status)
    return new_status, new_neighbors

def count_live_neighbors(status):
    """Counts the number of neighboring live cells"""
    kernel = np.array(
        [[1, 1, 1],
         [1, 0, 1],
         [1, 1, 1]]
    )
    c = convolve2d(status, kernel, mode='same', boundary="wrap")
    return c

def get_updated_colors(status, c):
    cmap = mpl.cm.Blues_r
    rescale = c / 8  # Maximum of 8 neighbors
    colors = [cmap(neighbors) for neighbors in rescale.flatten()]
    is_live = status.flatten()
    colors = [(r, g, b, 0.9) if live else (r, g, b, 0) for live, (r, g, b, a) in zip(is_live, colors)]
    return colors

for i in range(5):
    ani = play_game(
        size=(100, 100),
        marker_size=100,
        initial_prob_life=0.5,
        animation_kwargs={
            "frames": 300,
        }
    )

    ani.save(f'game_of_life_{i}.mp4',
             writer=animation.FFMpegFileWriter())
