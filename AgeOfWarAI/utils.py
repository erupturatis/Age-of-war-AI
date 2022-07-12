import wandb
import pyautogui
import cv2


def initial_setup():
    a = pyautogui.getWindowsWithTitle("Adobe Flash Player 13")
    if len(a) == 0: return
    window = a[0]
    window.move(-window.left, -window.top)
    window.maximize()
    # window.resize(-window.size[0]+1800,-window.size[1]+600)
    window.resize(-window.size[0]+2600,-window.size[1]+900)


def screenshot():
    im = pyautogui.screenshot(region=(0,90,2600,800))
    opencvImage = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    cv2.imshow("fa",opencvImage)
    cv2.waitKey()
    return opencvImage
    

def plot_graph(values):
    pass

