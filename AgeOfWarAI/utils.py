import wandb
import pyautogui
import cv2
import numpy as np

class WindowManagement(object):
    windows = None
    def __init__(self, title = "Adobe Flash Player 32") -> None:
        self.windows = pyautogui.getWindowsWithTitle(title)

    def focus_window(self, number=0):

        if len(self.windows) == 0: return
        window = self.windows[number]
        window.move(-window.left, -window.top)
        # window.resize(-window.size[0]+1800,-window.size[1]+600)
        window.resize(-window.size[0]+2600,-window.size[1]+900)
        pyautogui.click(300,50)


    def screenshot(self, image_title = '0'):

        im = pyautogui.screenshot(region=(0,0,2600,885))
        opencvImage = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
        #cv2.imwrite(f'{image_title}.png', opencvImage)
        return opencvImage

    def defocus_window(self, number=0):

        if len(self.windows) == 0: return
        window = self.windows[number]
        window.move(-window.left + 100,-window.top + 100)

    

def get_mouse_position():
    while True:
        print(pyautogui.position())
        # ctrl c to end program


def plot_graph(values):
    pass

if __name__ == "__main__":
    a = WindowManagement("Adobe Flash Player 32")
    a.focus_window(0)

