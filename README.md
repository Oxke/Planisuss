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

```pip install -r requirements.txt```

then start the simulation using the command

```python main.py [-h] [-n NUM_CELLS] [-d DAYS] [-b NEIGHBORHOOD] [-m DISTANCE]```

| short command | long command | explanation | default value
--- | --- | --- | ---
-h | --help | show a similar help message to this table and exit | ---
-n NUM_CELLS | --num_cells NUM_CELLS | The number of cells in the world. | 50
-d DAYS | --days DAYS | The number of days to run the simulation. | 10000
-b NEIGHBORHOOD | --neighborhood NEIGHBORHOOD | The number of cells that are considered to be nearby, hence visible by Erbasts. | 1
-m DISTANCE | --distance DISTANCE | The metric to be used. | Euclidean

### UI usage
the UI is made of two figures. The one on the left shows the current state of
the world, with red, green and blue respectively meaning carvizes, erbasts and
vegetob. The figure on the right shows past evolution of the demographic.
Possible UI commands are:
command | explanation | note
--- | --- | ---
spacebar / click on play button | stops and resumes the animation | -
right arrow / click on right arrow | starts animation forwards | -
left arrow / click on left arrow | start animation backwards | -
rigthmost button | proceed forwards one step | -
leftmost botton | proceed backwards one step | -
buttom slider | decide speed | it's in logarithmic scale
click on right figure | plots the corresponding day | only in pause
left click on left figure | shows information about the cell | if cell is water, then it becomes land. Only in pause
left click and drag on left | transforms all cells in the path to land | only in pause, if shift is pressed in the meanwhile, then all cells become water
right click on left figure | drops little bomb | only in pause
double click on left figure | drops big bomb | only in pause
press 'e' | Erbasts are revived and respawned all over the map | only in pause
press 'c' | Carvizes are revived and respawned all over the map | only in pause
press enter | A checkpoint is saved | unstable, only in pause
press 'r' | retrieve last checkpoint | unstable, only in pause




# Planisuss Report
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
- tracked: array of past positions and respective days, can be used to draw tracks of
  certain groups. At the current time there is no way of tracking and untracking
  groups, so this mechanic is not implemented fully, though the world plotting
  would support tracked groups.
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

However the Pride follows the exact same strategy in movement, except it uses the
total energy of the Herd as the value indicator and has a wider sight, around
1/10 of NUMCELLS.

## Day Events
The day is constituted of these phases:
- Grow:
    - Vegetob: growing
    - Erbast: Aging and eventually dying
    - Carviz: Aging and eventually dying
- Move:
    - Erbast: each Herd chooses where to move, then each member of its herd
      chooses if he wants to follow the herd or quit it, then the movement
      occurs. In case of collision of two or more herds, they join peacefully
    - Pride: each Pride chooses where to move, then similarly each member
      chooses and in case of collision of two or more prides they choose of
      either fighting or joining.
        - Fight: it consists of 10 attacks, in which the champion from each
          group combat against each other, and each duel is structured in this
          way: if champion A has more energy than champion B, then A's energy
          gets increased by half of B's energy, and B's energy becomes (3B-2A)/4
          energy that is likely to be negative, hence B probably dies, but not
          surely.
    - if a Pride and a Herd end up in the same cell, then a Hunt takes place,
      and in that case the champion of the Herd gets killed and its energy is
      shared between the members of the Pride

## Visualization
The visualization consists of two graphs, one on the left showing the status and
one on the right showing past evolution of the demographic. You can navigate in
time through it using the commands and change the speed of the animation using
the slider.
The visualization works by creating a custom subclass of the `FuncAnimation`
class from matplotlib, which plots a certain frame, and then the function
`World.plot` takes care of understanding if we are in a new frame or in an
already simulated one.
Clicking on the graph on the right you can go directely to a certain day, and
clicking on the left one you can either get information about the cell (left
click), throwing bombs (right click) or changing the geography (left click-and
drag)

## Work in Progress...
I'm trying to implement a saving mechanic, but I've encountered some issues, so
as of right now it is not stable, however it would work by pickling the grid and
history of the world, together with the variable CARVIZES and ERBASTS, and then
it should be possible to come back at those saved point in time.
