
import requests as rq
from datetime import datetime, timezone
import json
import urllib.parse
import incentiveFiles.truckIncentives as elTruck
import time

### Access ExtraLife
#TODO add option to change intensity of "safety car"
#TODO Add timezone sync https://worldtimeapi.org/api
#TODO use timezone sync initially, then switch to internal clock.

version = '5'
lastUpdated = '2024/11/11'
BASE_URL = 'https://www.extra-life.org/api/'
defaultID = '68305' # Change this next year


class extraLife:
    """ExtraLife API
    """
    def __init__(self):
        self.teamID = ''
        self.etag = ''
        self.lastChecked = datetime.now(timezone.utc) # set to when program first runs
        self.failedRequests = 0
    
    def _requester(self,rqType,url,forceUpdate=False):
        headers = {
            'If-None-Match': self.etag,
            'User-Agent': 'Automated Incentives Script',
        }
        
        if forceUpdate==False: 
            try:
                response = rq.request('head', BASE_URL + url, headers=headers)
            except Exception as e:
                raise e
            code = response.status_code
        
        else:
            code = 200
        
    
        if code == 200:
            response = rq.request(rqType, BASE_URL + url, headers=headers)
            headerInfo = response.headers._store
            try:
                self.etag = headerInfo['etag'][1] # Get etag
            except:
                print('WARNING! Failed to set Etag.  This can be ignored unless it happens repeatedly.')
                pass
            try:
                self.failedRequests = 0
                return json.loads(response.content.decode(encoding='utf-8'))
            except:
                print('WARNING! Failed to parse response in JSON format.  This can be ignored unless it happens again')
                self.failedRequests += 1
                return False
        elif code == 304: # No changes
            self.failedRequests = 0
            return False
        else:
            if self.failedRequests > 4:
                textOutput(f'FINAL WARNING. 5 donation checks have failed in a row.  Something is wrong, contact Finn.\nError: {code}:{response.reason}')
            else:
                textOutput('WARNING! Last donation check failed!')
                self.failedRequests += 1
            
            return False


    def activity(self,
                 ID:int=None,
                 idType:str='team',
                 testDonations=False
                 ):
        """Check activity

        Args:
            ID (int, optional): Extra Life ID. If none provided, will default to the TeamID set earlier.
            idType (str, optional): Can be set to 'team', 'participant' or 'event'. Defaults to 'team'.
            testDonations (bool, optional): Whether to run test donations (external JSON file). Defaults to False.

        Raises:
            TypeError: Invalid ID provided

        """
        if testDonations == True:
            try:
                print('Test donations enabled, trying to load file.')
                with open('test.json', 'r') as file:
                    testDonationList = json.load(file)
                print('Test donations loaded, you now have 15 seconds to get into the game before they start running.')
            except:
                print('Failed to find/run test donations.')
                return False
        
        url = ''
        ID = ID if ID != None else self.teamID
        
        if idType.lower() not in ('team','participant','event'):
            raise TypeError('Invalid ID type')
        else:
            url += idType.lower() + 's' + '/' + str(ID) + '/activity'
        
        url += '&' + urllib.parse.urlencode({'orderBy': 'createdDateUTC'}) # Sort most recent first
        response = self._requester('get',url)
        if response == False: # No change
            return False
        if testDonations == True:
            time.sleep(15)
            response = testDonationList
        
        
        newInfo = []
        for item in response:
            if datetime.fromisoformat(item['createdDateUTC']) < self.lastChecked and testDonations == False:
                pass # Old item, ignore
            elif item['type'] != 'donation':
                pass # not a donation
            else:
                newInfo += [item]
        self.lastChecked = datetime.now(timezone.utc)
        return newInfo
    
    def validateTeam(self,teamID): # Validate team ID
        if teamID.isnumeric() == False:
            print(f'Team IDs can only contain numbers.  {teamID} is not a valid ID.')
            return False
        
        url = '/teams/' + str(teamID) +'/'
        response = rq.request('get', BASE_URL + url)
        if response.status_code != 200:
            print(f'{teamID} is not a valid team ID, please double check and try again.')
            return False
        else:
            content = json.loads(response.content.decode(encoding='ascii'))
            confirm = input(f'Found team {content['name']}. Press Y to continue, press any other key if this is not the correct team: ')
            if confirm.lower() not in ['y', 'yes']:
                return False
            else:
                self.teamID = teamID
                return True


def textOutput(text):
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print(f'[{now}] {text}')

def syncTime():
    """Sync to global time so all clients are offset similarly

    Returns:
        _type_: _description_
    """
    noData = True
    failedRequests = 0
    while noData == True:
        if failedRequests > 10:
            return False # Return if time sync continues to fail
        amsterdam = rq.get('http://worldtimeapi.org/api/timezone/Europe/Amsterdam')
        if amsterdam.status_code != 200:
            noData = True
            failedRequests +=1 # Cannot get time
        else:
            decoded = json.loads(amsterdam.content.decode())
            time = datetime.fromisoformat(decoded['datetime'])
            print(time)
            remainder = time.second % 10
            if remainder != 0:
                return 10 - remainder
            else:
                return 0
### Main program    
el = extraLife()
priceList = elTruck.createPriceDict()

print(f'Extra Life donation monitoring script.\nVersion: {version}, Last updated: {lastUpdated}')
time.sleep(.5)
textOutput(f'Trying to load Default team, ID: {defaultID}')
verifed = el.validateTeam(defaultID) # Default ID
while verifed == False:
    verifed = el.validateTeam(input('enter Extra Life Team ID: '))

testDono = False
userInp = input('Do you want to run test donations? [Y/N]: ')
if userInp.lower() in ['y','yes']:
    testDono = True
textOutput('\n\n\n\n\n\n\n\n\nScript started.  Donations will be checked every 10 - 15 seconds in order to comply with API usage rules.')


# Main loop
while True:
    sleep = syncTime()
    time.sleep(sleep if sleep != False else 10) # Avoid issues if time cannot be synced
    data = el.activity(testDonations=testDono)
    testDono = False
    if data == False or data in [[],'',None]:
        textOutput('No new donations.')
    else:
        for item in data:
            try:
                user = item['title']
            except:
                user = 'Anonymous'
            validCommand = False
            try:
                command = priceList[item['amount']]
                validCommand = True
            except:
                textOutput(f'{user} donated ${item['amount']} but no action is asigned')

            if validCommand == True:
                try:
                    textOutput(f'{user} donated ${item['amount']}. Activating {command[0]}')
                    exec(f"elTruck.{command[1]}()")
                except:
                    textOutput(f'Failed to run {command[0]}')
    time.sleep(5) # Wait 5 seconds (this avoids the time API from freaking tf out)
    userAnswer = False