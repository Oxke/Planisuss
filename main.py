#!/usr/bin/env python
from matplotlib import pyplot as pp
import numpy as np
from objects import World

NUMCELLS = 10
NEIGHBORHOOD = 1

if __name__ == "__main__":
    world = World.World(NUMCELLS, NEIGHBORHOOD)
    anim = world.run(300)
    plt.show()
