from pynput.keyboard import Key, Controller
from playsound3 import playsound
import time
import random
import webbrowser

#TODO #7 run actions in their own thread so it doesn't prevent multiple actions from being done at once OR create a queue system
#TODO #9 Get TTS working
#TODO #17 Mark conflicting functions


incentives = ["parkingBrake","slalom","everyCam","cinematicCam","metalPipes","towToService"]


keyboard = Controller()

# # # Keypresses

def parkingBrake():
    """Enable parking brake
    """
    keyboard.press(Key.space)
    time.sleep(.5)  
    keyboard.release(Key.space)


#TODO #1 Fix Slalom command to accept float values correctly
def slalom(delay = "0.8"):
    delay = float(delay)
    loop = 0
    while loop < 5:
        keyboard.press('a')
        time.sleep(delay)
        keyboard.release('a')
        keyboard.press('d')
        time.sleep(delay)
        keyboard.release('d')
        loop+=1
        

#TODO #5 confirm this works
def towToService():
    """Tow to nearest service centre
    """
    keyboard.tap(Key.f7)
    time.sleep(1)  
    keyboard.tap(Key.enter)
    time.sleep(.5)
    keyboard.tap('1')
    time.sleep(.5)
    keyboard.tap(Key.enter)

    
# # # Camera modifiers

def everyCam():
    loop = 0
    while loop < 7:
        num = str(random.randrange(0,9))
        keyboard.tap(num)
        loop+=1
        time.sleep(.4)
    keyboard.tap('1')


def cinematicCam():
    """Enable cinematic camera (20 seconds)
    """
    count = 0
    while count < 5:
        keyboard.tap('8')
        time.sleep(5) 
        count +=1
    keyboard.tap('1')



# # # Sound
# TODO #8 Get sounds from the web working

def metalPipes():
    """Play metal pipes sound
    """
    playsound('sounds/metalPipe.mp3')


# # # Other

#TODO #6 allow function keys, windows key, etc to be used through here.
def anyKey(key):
    """
    """
    keyboard.tap(key)
    

def openLink(link):
    """
    """
    try:
        webbrowser.open(link)
    except:
        pass
    
