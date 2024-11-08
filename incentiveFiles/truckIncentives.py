from pynput.keyboard import Key, Controller
from playsound3 import playsound
import time
import random

#TODO #9 Get TTS working
#TODO #17 Mark conflicting functions

# Must add functions to this list
activeFunctions = ["parkingBrake","slalom","everyCam","cinematicCam","metalPipes","towToService"]

keyboard = Controller()

def templateIncentive(details=False):
    # FLOAT! Incentive Cost.  Used if ExtraLife integration is enabled
    cost = 12.3
    # STRING! Friendly name. Displayed in control panel
    fName = 'name'
    
    # Returns details
    if details == True:
        return cost, fName
    else:
        # Run action here
        pass


# # # Keypresses

def parkingBrake(details=False):
    """Enable parking brake
    """
    cost = 6.0
    fName = 'Throw \'er in park'
    
    if details == True:
        return cost, fName
    else:
        keyboard.press(Key.space)
        time.sleep(.5)  
        keyboard.release(Key.space)


#TODO #1 Fix Slalom command to accept float values correctly
def slalom(details=False,delay = "0.8"):
    cost = 3.0
    fName = 'Safety Car'
    
    if details == True:
        return cost, fName
    else:
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
def towToService(details=False):
    """Tow to nearest service centre
    """
    cost = 50.0
    fName = 'If it ain\'t broke, fix it'
    
    if details == True:
        return cost, fName
    else:
        keyboard.tap('f')
        keyboard.tap('e')
        keyboard.tap(Key.space)
        time.sleep(2)
        keyboard.tap(Key.f7)
        keyboard.tap('1')
        time.sleep(1)
        keyboard.press(Key.enter)
        time.sleep(.2)
        keyboard.release(Key.enter)
        

    
# # # Camera modifiers

def everyCam(details=False):
    cost = 13.37
    fName = 'Spam cam'
    
    if details == True:
        return cost, fName
    else:
        loop = 0
        while loop < 7:
            num = str(random.randrange(0,9))
            keyboard.tap(num)
            loop+=1
            time.sleep(.4)
        keyboard.tap('1')


def cinematicCam(details=False):
    """Enable cinematic camera (20 seconds)
    """
    cost = 5.0
    fName = 'Goto view'
    
    if details == True:
        return cost, fName
    else:
        count = 0
        while count < 5:
            keyboard.tap('8')
            time.sleep(5) 
            count +=1
        keyboard.tap('1')



# # # Sounds
# TODO #8 Get sounds from the web working

def metalPipes(details=False):
    """Play metal pipes sound
    """
    cost = 17.0
    fName = 'Did you hear something?'
    
    if details == True:
        return cost, fName
    else:
        playsound('sounds/metalPipe.mp3')



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

def createIncentiveDict():
    global activeFunctions
    incentives = {}
    # Run and collect function information
    for item in activeFunctions:
        resultDict = {}
        exec(f'itemDetails = {item}(details=True)',globals(),resultDict)
        resultItems = resultDict['itemDetails']
        incentives.update({
            f'{item}': {
                'cost': resultItems[0],
                'name': resultItems[1]
                    }
       })
    print(incentives)
    return incentives

def createPriceDict(): # Price dictionary
    global activeFunctions
    incentives = {}
    # Run and collect function information
    for item in activeFunctions:
        resultDict = {}
        exec(f'itemDetails = {item}(details=True)',globals(),resultDict)
        resultItems = resultDict['itemDetails']
        incentives.update({
            resultItems[0] : [resultItems[1],item]
       })
    print(incentives)
    return incentives