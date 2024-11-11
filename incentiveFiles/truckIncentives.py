from pynput.keyboard import Key, Controller
from playsound3 import playsound
import time
import random
import json

#TODO #9 Get TTS working
#TODO #17 Mark conflicting functions

# Must add functions to this list
activeFunctions = ["parkingBrake","slalom","everyCam","cinematicCam","metalPipes","towToService"]

keyboard = Controller()

# # # Keypresses

def parkingBrake():
    """Enable parking brake
    """

    keyboard.press(Key.space)
    time.sleep(.5)  
    keyboard.release(Key.space)


def slalom(delay=.3):
    """Zig zag back and forth"""
    loop = 0
    while loop < 5:
        keyboard.press('a')
        time.sleep(delay)
        keyboard.release('a')
        time.sleep(.5)
        keyboard.press('d')
        time.sleep(delay)
        keyboard.release('d')
        time.sleep(.5)
        loop+=1
        

def towToService():
    """Tow to nearest service centre
    """

    keyboard.tap('f')
    keyboard.tap('e')
    keyboard.tap(Key.space)
    time.sleep(2)
    keyboard.tap(Key.f7)
    time.sleep(.5)
    keyboard.press(Key.enter)
    time.sleep(.2)
    keyboard.release(Key.enter)
    time.sleep(.2)
    keyboard.tap('1')
    time.sleep(1)
    keyboard.press(Key.enter)
    time.sleep(.2)
    keyboard.release(Key.enter)

    
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
    playsound('sounds/gotoView.mp3')
    count = 0
    while count < 5:
        keyboard.tap('8')
        time.sleep(5) 
        count +=1
    keyboard.tap('1')

# # # Sounds
# TODO #8 Get sounds from the web working
def metalPipes():
    """Play metal pipes sound
    """
    playsound('sounds/metalPipe.mp3')


# # # No actions
def wrongSide(): # No action to be performed
    pass

def hitCop():
    # FLOAT! Incentive Cost.  Used if ExtraLife integration is enabled
    pass


# # # Other
#TODO #6 allow function keys, windows key, etc to be used through here.
""" 
def anyKey(key):

    keyboard.tap(key)
    

def openLink(link):
    try:
        webbrowser.open(link)
    except:
        pass
    
 """
 
 
 # List creator
def incentiveDetails():
    """Generates two dictionaries for price and incentive IDs

    Returns:
        list: Two dictionaries.  1 Prices, 2 Incentive IDs
    """
    priceDict = {}
    incntIDDict = {}
    with open('incentiveFiles/truckIncentives.json', 'r') as jsonFile:
        incentives = json.load(jsonFile)
    for incentive in incentives:
        priceDict.update({incentive['Amount']: [incentive['Name'],incentive['Command']]})
        if incentive['IncentiveID'] != '': # Skip blank incentive IDs
            incntIDDict.update({incentive['IncentiveID']: [incentive['Name'],incentive['Command']]})
        else:
            continue
    return priceDict, incntIDDict
    