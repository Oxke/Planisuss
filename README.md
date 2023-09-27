# Planisuss

## Variables
- CARVIZES and ERBASTS: lists containing all the Animals, the position in the list
    corrisponds to the id of the Animal
- DAYS: days of execution of the simulation
- NUM\_CELLS: the number of cells in the side of the square which contains the
  world 
- NEIGHBORHOOD: the distance under which cells are considered near
- DISTANCE: the chosen metric, see below
- CAUSE\_OF\_DEATH: the causes of death of the different species

## Usage
To run the execution, first satisfy the library requisites in the file
`requirements.txt` by executing the command

```pip install $(cat requirements.txt)```

then start the simulation using the command

```main.py [-h] [-n NUM_CELLS] [-d DAYS] [-b NEIGHBORHOOD] [-m DISTANCE]```

| short command | long command | explanation
--- | --- | ---
-h | --help | show a similar help message to this table and exit.
-n NUM_CELLS | --num_cells NUM_CELLS | The number of cells in the world.
-d DAYS | --days DAYS | The number of days to run the simulation.
-b NEIGHBORHOOD | --neighborhood NEIGHBORHOOD | The number of cells that are considered to be nearby, hence visible by Erbasts.
-m DISTANCE | --distance DISTANCE | The metric to be used.


## The Planisuss world
The world is stored as an Object of the Class World, which contains the variable
`world.grid`: a NUMCELLS x NUMCELLS array containing objects of type Cell.

Each Cell knows its position and can contain a Herd and a Pride, or being a
water cell.

Each Pride and Herd contains an array of indexes (`self.members_id`) which refer
to single Erbasts and Carvizes. The association id - Object is defined in the
two global variables ERBASTS and CARVIZES.


### The creation of the world
The world is created through an algorithm that works like a BFS, but at each
moment it diminuishes the probability of continuing a certain path. In other
words, it starts from a cell, called *pseudocenter* and goes through all of its
neighbors, adding them to a queue according to a probability decided by the
number 0 < *p* < 1. If a cell gets added to the "pangea", then *p* is lowered,
and the process continues until the queue is empty

### Distance and neighborhood
In the world distance can be defined in different ways, using the Chebyshev
metric (infty-norm), the Euclidean metric (2-norm) or the Manhattan metric
(1-norm) and the neighborhood is defined as the ball according to the chosen
metric. The default metric is the Euclidean. It can be changed from the variable
DISTANCE to the values `"Manhattan"` or `"Chebyshev"`.

## The Ecosystem
The world contains beings of three species:
- Vegetob: grows spontanously on land
- Erbast: eats vegetob, groups into Herd
- Carviz: eats Erbasts, groups into Pride

### Vegetob
Vegetobs store the value vegetob.density, which is between 0 and 100. Every turn
this value is increased, according to an uneven logistic curve which has the
highest slope after around 50 days, but takes around one year to fully restore.

### Animal
This is the parent class of Erbast and Carviz, and gives them the properties:
- position: Cell in which the animal lives
- world: the whole world
- energy: from 0 to 100, increased by grazing/hunting and consumed for
  movement/fight/aging, if it reaches a value less then 5 the animal is
  progressively more likely to die, when it reaches 0 the animal dies surely
- Lifetime: duration of the life expressed in days
- Age: Once an animal ages reaches the lifetime, it dies and generates children
- Social Attitude: 0 to 1, attitude of the animal to form groups and live in groups
- alive: boolean value useful to debug and check animals that are alive should be so
- id: (attribuited in subclasses) a number that at each point in time uniquely
  determines one Carviz or one Erbast

When it dies it saves into the variable CAUSE\_OF\_DEATH the reason of the
death, and if the reason is not having being killed (by other animals or the
bomb), it generates a prole of 2 children, with energies that sum to the one of
the parent, lifetimes that averages to the one of the parent and social attitude
generated using a normal distribution with mean the value of the parent and
standard deviation 0.1. The children are then inserted in the same herd or pride
as the parent.

> Note: actually the `die` method is implemented in subclasses, for convenience

### Erbast
An erbast can graze and gain energy by eating vegetob. The amout of energy
gained, however, is inversely proportional to the percentage of life of the
Erbast (in practice, `Energy gained = 1 * (lifetime / (age + .1)` where the `+ .1`.
is needed in order to avoid dividing by 0).


### Carviz
A Carviz, as an Erbast, can at each moment decide to leave its Pride (or Herd).
But this will be explained in further details later.


## Groups
In order to limit computations, most operations are done on groups instead of
single Animals, and so each animal is always contained in a social group, though
it might be of size 1.

### Group
Parent class of Herd and Pride, has the following properties:
- position and world
- members\_id: array containing the indeces of the contained Erbasts or Carvizes
- memory: a dictionary used to decide where to go next, unexplored cells are
  preferred
- tracked: array of past positions and respective days, used to draw tracks of
  certain groups
- members: method that yields the elements of the group as objects, often used
  as a property in order to pass through all the group elements easily.
  (implemented in subclasses)

and the following methods:
- \_\_len\_\_: size of the group
- add: adds a member to the group
- remove: removes a member from the group
- join: joins itself with another group 
- add\_energy: distributes a certain amount of energy between its members
- get\_energy: returns the total sums of all the energies of the animals
  contained in the group
- get\_sa, get\_lifetime and get\_age: respectively returns the average social
  attitude, lifetime and age of the members of the group
- clean: debug method used to remove members which have id numbers which are not
  associated to any animal
- suppress: as the name suggests, it kills instantly all the members of one herd

### Herd
Herd movement tend to follow the density of vegetob.
The choice of the next cell is made in the following way:
- Near cells are analysed and added to memory
- If the total energy of the Herd is smaller than the density of the cell, then
  the Herd doesn't move
- Otherwise it moves to the highest valued cell in memory, with a caveat: Since
  it wants to prefer unexplored cells, at each point in time stored values which
  are not checked again in memory gets halved, and eventually forgotten, so that
  the herd is discouraged from coming back on its steps to explore other rich
  cells.
- Chosen the destination cell, the Herd moves to the near cell that is nearest
  to the chosen destination cell.


### Pride
Pride movement seems more randomic since average life of Carvizes is much shorter
then the one of Erbasts, but the result is that prides, or their heir when they
die, tend to follow, trap and slow down the spread of Herds.

However the Pride follows the exact same strategy in movemnt, except it uses the
total energy of the Herd as the value indicator and has a wider sight, around
1/10 of NUMCELLS.

