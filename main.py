#!/usr/bin/env python
import sys
from matplotlib import pyplot as plt
from Objects import World
from variables import argument_parser

if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    num_cells, neighborhood, days = argument_parser()
    world = World.World(num_cells, neighborhood)
    anim = world.run(days)
    plt.show()
