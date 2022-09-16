# I created 23 files in game each one corresponding to one action
# To pass an action you need to put only one file in the shared objects directory and the
# modified version of the game will read it and take the corresponding action

from EnvironmentVars import Username
import shutil
def take_action(action):
    
    # this path might differ a bit for you depending on the location of your game(mine is on desktop)
    # you need to decompile the game and in the "base player" script
    # you will have a function called create actions that will generate
    # shared objects that will each memorize a number
    # you can copy paste with python those shared objects in the game 
    # in order to give it a number for an action
    # generating the sol objects will also generate a path similar to the one below
    # that you will need to copy and paste here

    PATH = r"C:\Users\user\AppData\Roaming\Macromedia\Flash Player\#SharedObjects\6ANAAZWR\localhost\projects\python\age_of_war_ai\AgeOfWarAI\FinalGameVersion\testnr.swf"

    
    PATH = PATH.replace("user", f"{Username}")

    src_path = r"AgeOfWarAI\ActionsSOLFiles\GameActionACTHERE.sol"
    src_path = src_path.replace("ACTHERE", f"{action}")

    dst_path = PATH
    shutil.copy(src_path, dst_path)
    print(f'Copied {action}')
