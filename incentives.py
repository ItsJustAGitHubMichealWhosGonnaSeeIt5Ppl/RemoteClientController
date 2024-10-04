from pynput.keyboard import Key, Controller
from playsound3 import playsound
import time
import random
import webbrowser

keyboard = Controller()

# # # Keypresses

def parkingBrake():
    """Enable parking brake
    """
    keyboard.press(Key.space)
    time.sleep(.5)  
    keyboard.release(Key.space)


def slalom(delay = 0.6):
    delay = float(delay) if delay.isdigit() else 0.6
    loop = 0
    while loop < 5:
        keyboard.press('a')
        time.sleep(delay)
        keyboard.release('a')
        keyboard.press('d')
        time.sleep(delay)
        keyboard.release('d')
        loop+=1
        
    
def towToService():
    """Tow to nearest service centre
    """
    keyboard.tap(Key.f7)
    time.sleep(1)  
    keyboard.tap(Key.enter)
    time.sleep(.5)
    keyboard.tap('1')

    
# # # Camera modifiers

def everyCam():
    loop = 0
    while loop < 7:
        num = str(random.randrange(0,9))
        keyboard.press(num)
        keyboard.release(num)
        loop+=1
        time.sleep(.4)
    keyboard.press('1')
    keyboard.release('1')
    
def cinematicCam():
    """Enable cinematic camera (20 seconds)
    """
    count = 0
    while count < 5:
        keyboard.press('8')
        keyboard.release('8')
        time.sleep(5) 
        count +=1
    keyboard.press('1')
    keyboard.release('1')


# # # Sound

def metalPipes():
    """Play metal pipes sound
    """
    playsound('sounds/metalPipe.mp3')


# # # Other
    
def anyKey(key):
    """
    """
    keyboard.press(key)
    keyboard.release(key)
    

def openLink(link):
    """
    """
    try:
        webbrowser.open(link)
    except:
        pass
    
