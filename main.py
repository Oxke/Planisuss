#!/usr/bin/env python
from matplotlib import pyplot as plt
from Objects import World
from variables import NUM_CELLS, NEIGHBORHOOD, DAYS

if __name__ == "__main__":
    world = World.World(NUM_CELLS, NEIGHBORHOOD)
    anim = world.run(DAYS)
    plt.show()
