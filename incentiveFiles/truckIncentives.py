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


class TruckControls:
    def __init__(self,wheelToggle):
        self.wheel = wheelToggle
    
    
    def parkingBrake():
        """Enable parking brake"""
        keyboard.tap(Key.space)


    def slalom(self):
        """Zig zag back and forth"""
        if self.wheel == True: # Using a wheel
            hold= .3
            delay = .5
        else:
            hold= .8
            delay = 0
            
        loop = 0
        while loop < 5:
            keyboard.press('a')
            time.sleep(hold)
            keyboard.release('a')
            time.sleep(delay)
            keyboard.press('d')
            time.sleep(hold)
            keyboard.release('d')
            time.sleep(delay)
            loop+=1
            

    def towToService(self):
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
    def everyCam(self):

        loop = 0
        while loop < 7:
            num = str(random.randrange(0,9))
            keyboard.tap(num)
            loop+=1
            time.sleep(.4)
        keyboard.tap('1')


    def cinematicCam(self):
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
    def metalPipes(self):
        """Play metal pipes sound
        """
        playsound('sounds/metalPipe.mp3')


    # # # No actions
    def wrongSide(self): # No action to be performed
        pass

    def hitCop(self):
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
    