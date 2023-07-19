# Age-of-war-AI
Age of war AI
Running on python 3.7.9

# Age-of-war-AI
Age of war AI
Running on python 3.7.9

## Inputs:
- Number of troops in training (1 input)
- Enemy HP - percent of total health (1 input)
- My HP - percent of total health (1 input)
- Money - normalized by basic unit cost (money/cost_of_basic_unit) (1 input)
- XP - can upgrade age or not (1 input)
- Can activate ability - 0 to 1 cooldown (1 input)
- My troops on ground type 1, 2, 3, 4 (4 inputs)
- Enemy troops on ground type 1, 2, 3, 4 (4 inputs)
- Number of available cannon slots (1 input)
- Player age - one hot encoded (5 inputs)
- Enemy age - one hot encoded (5 inputs)
- Array with turrets and turrets age (max 4) (1 input for type since they get progressively stronger and 1 input for the age deprecation) (2 for each slot) (8 inputs)
- Where is the current battle taking place (0-1 your base to enemy base) (1 input)

## Outputs:
- Create troops tier 1, 2, 3 (3 actions)
- Create troops tier 4 for space age (1 action)
- Buy cannon slot (1 action)
- Buy cannon tier 1, 2, 3, first available slot (3 actions)
- Sell cannon on a certain slot (4 actions)
- wait(1 actions)
- use ability


Dependencies:

- numpy
- paddle ocr
- open-cv
- scipy
- neat-python

`
pip install numpy paddlepaddle paddleocr opencv-python scipy neat-python
`

The assets work only for the that specific resolution
If you want to modify the game resoltion you will have to change the assets size accordingly (eg: make the game and the assets x% smaller)


You can download the archive I used for the game from [here]("https://github.com/erupturatis/Decompiled-flash-games-archive")

