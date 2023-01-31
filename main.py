#!/usr/bin/env python
from matplotlib import pyplot as pp
import numpy as np
import Planisuss.World
import Planisuss.Ecosystem


NUMCELLS = 4
NEIGHBORHOOD = 1

def main():
    world = World.World(NUMCELLS, NEIGHBORHOOD)
    world.run()
