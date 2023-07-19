# Age-of-war-AI
Age of war AI, a project that I spent an abhorent amount of time on, that turned into massive spagheti code. It was my first big project and it showed me how much more I had to learn because I was lacking ( and I still do most likely ) in all fields. In the context of this project I did the following:

## HOW TO NOT DO A PROJECT 

- Get the vanilla age of war game, make a module that extracts data via openCV library as the game goes on and feeds it into the NEAT Algorithm. What I didn't realise is that evaluating 30 to 50 agents on a game that is not speed up with and average play-time of 10 minutes per session takes REALLY a lot of time to train and it yielded no significant results
- Get cheat engine, realise it does not work with this specific game for who knows what reason, then find a decompiler for flash games and inject a script into the game that spawns text files in order to circumvent the whole openCV thing for getting values. Got slightly better results since I managed to speed up the game x2 with cheat engine but still it was lacking a lot.
- Get unity going. Since I already found a way into the game code, I reverse engineered all it mechanics and made a quite faithful simulation in unity that had the exact same parameters as the original game.
- [Simulate 50 environments in unity](https://github.com/erupturatis/Age-of-war-unity-clone) with 10x speed and make them communicate via TCP with my python script that now had a GOD neat manager for all those environments and their respective actions. Here I actually started seeing some significant results and strategies developing and managing to win on NORMAL mode yay. But I wanted moe
- Switch up completely on unity ml agents essentially abandoning the python script, train and agent with PPO and get it after tons of switching up parameters and its functions get it to have quite a good strategy that wins the game on HARD mode
- Test it on the original game and record it winning and realise you lost 2 months on a project that could have been finished in under 3 weeks
- Still make a [visualization library](https://github.com/erupturatis/Neat-Manim) for NEAT using the mathematical engine MANIM because I found some cool youtube videos on the topic that didn't publish their repositories



You can see the overview of this pain [here](https://www.youtube.com/watch?v=cfAbN8-P_yM) - I will come back 100% to this channel to get it to at least 1M but for now I have other goals to pursue.

*Running on python 3.7.9*

#### Inputs:
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

#### Outputs:
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

