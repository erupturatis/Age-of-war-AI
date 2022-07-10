# Age-of-war-AI
Age of war AI


inputs:

enemy hp - percent of total health
my hp - percent of total health
money - normalized by basic unit cost (money/cost_of_basic_unit)
xp - can upgrade age or not
player age - one hot encoded
can activate ability - 0 to 1 cooldown
my troops on ground -  number from memory 
how far the battle/ some information about enemy troops and distance to base my base
n troops in training - calculated while playing
number of available cannon slots - calculated while playing
array with cannon and cannon age (max 4) - calculated while playing


outputs:

create troops tier 1,2,3
buy cannon slot
buy cannon tier 1,2,3, first available slot
sell cannon on certain slot
evolve next age