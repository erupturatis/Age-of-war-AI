# I created 23 files in game each one corresponding to one action
# To pass an action you need to put only one file in the shared objects directory and the
# modified version of the game will read it and take the corresponding action

from EnvironmentVars import Username
import shutil
def take_action(action):
    
    # this path might differ a bit for you depending on the location of your game(mine is on desktop)
    PATH = r"C:\Users\user\AppData\Roaming\Macromedia\Flash Player\#SharedObjects\K48AQ9JL\localhost\Users\user\Desktop\testnr.swf"
   
    
    PATH = PATH.replace("user", f"{Username}")

    src_path = r"AgeOfWarAI\ActionsSOLFiles\GameActionACTHERE.sol"
    src_path = src_path.replace("ACTHERE", f"{action}")

    dst_path = PATH
    shutil.copy(src_path, dst_path)
    print(f'Copied {action}')
