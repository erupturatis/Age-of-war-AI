# Age-of-war-AI
Age of war AI


inputs:

enemy hp - percent of total health (1 input)
my hp - percent of total health (1 input)
money - normalized by basic unit cost (money/cost_of_basic_unit) (1 input)
xp - can upgrade age or not (1 input)
player age - one hot encoded (5 inputs)
can activate ability - 0 to 1 cooldown (1 input)
where is the current battle taking place(0-1 your base to enemy base) (1 input)

my troops on ground type 1 and 2 (2 input)
enemy troops on ground type 1 and 2 (2 inputs)

special troops on ground for enemy and for player,last age (2 inputs)


number of troops in training (1 input)
number of available cannon slots (1 input)
array with cannon and cannons age (max 4) (1 input for type since they get progressively stronger and 1 input for cannon age)(2 for each slot)  (8 inputs) 

OPTIONAL INPUTS:
Troops cost relative to basic per age (3)
Cannon cost relative to basic per age (3)

8 + 1 + 1 + 1 + 2 + 2 + 1 + 1 + 5 + 1 + 1 + 1 + 1 = 26 inputs

outputs:

create troops tier 1,2,3 (3 actions)
create troops tier 4 for space age (1 actions)
buy cannon slot (1 action)
buy cannon tier 1,2,3, first available slot (3 actions)
sell cannon on certain slot (4 actions)
evolve next age (1 action)
wait(1 actions)

14 actions

Dependencies

numpy
pytesseract
open-cv
neat-python

You can install the archive I used for the game from here:

