# Age-of-war-AI
Age of war AI


inputs:

number of troops in training (1 input)
enemy hp - percent of total health (1 input)
my hp - percent of total health (1 input)
money - normalized by basic unit cost (money/cost_of_basic_unit) (1 input)
xp - can upgrade age or not (1 input)
can activate ability - 0 to 1 cooldown (1 input)
my troops on ground type 1,2,3,4 (4 input)
enemy troops on ground type 1,2,3,4 (4 inputs)
number of available cannon slots (1 input)
player age - one hot encoded (5 inputs)
enemy age - one hot encoded (5 inputs)
array with turrets and turrets age (max 4) (1 input for type since they get progressively 
stronger and 1 input for cannon age)(2 for each slot)  (8 inputs) 
where is the current battle taking place(0-1 your base to enemy base) (1 input)


8 + 1 + 1 + 1 + 4 + 4 + 1 + 1 + 5 + 5 + 1 + 1 + 1 + 1 = 34 inputs

Maybe add other inputs?
Enemy age one hot encoded

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

The assets work only for the that specific resolution
If you want to modify the game resoltion you will have to change the assets size accordingly (eg: make the game and the assets x% smaller)


You can download the archive I used for the game from here:

Reward
+1 for valid actions (including wait)
+0.2 for each iteration it's still alive
+1000 for winning

