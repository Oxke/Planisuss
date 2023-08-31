import argparse
CARVIZES = []
ERBASTS = []

DAYS = 10000

NUM_CELLS = 50
NEIGHBORHOOD = 1
DAY_BY_DAY_RESULTS = []
CAUSE_OF_DEATH = {"Erbast": {},
                  "Carviz": {}}
desc = 'Simulation of a three-species ecosystem: Vegetobs, Erbasts and \
Carvizes; which are respectevely plants, herbivores and carnivores.'

def argument_parser():
    global NUM_CELLS, NEIGHBORHOOD, DAYS
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-n', '--num_cells', type=int, default=NUM_CELLS,
                        help='The number of cells in the world.')
    parser.add_argument('-d', '--days', type=int, default=DAYS,
                        help='The number of days to run the simulation.')
    parser.add_argument('-b', '--neighborhood', type=int, default=NEIGHBORHOOD,
                        help='The number of cells that are considered to be \
nearby, hence visible by Erbasts')
    args = parser.parse_args()
    NUM_CELLS = args.num_cells
    DAYS = args.days
    NEIGHBORHOOD = args.neighborhood
    return NUM_CELLS, NEIGHBORHOOD, DAYS