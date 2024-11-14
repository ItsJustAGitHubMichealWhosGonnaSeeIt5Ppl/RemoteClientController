
import requests as rq
from datetime import datetime, timezone,timedelta
import json
import urllib.parse
import incentiveFiles.truckIncentives as elTruck
import time

### Access ExtraLife
#TODO add option to change intensity of "safety car"

version = '6'
lastUpdated = '2024/11/11'
BASE_URL = 'https://www.extra-life.org/api/'
defaultID = '68305' # Change this every year
blacklist = [] # DonorIDs to blacklist.  Defaults to empty


class ExtraLife:
    """ExtraLife API
    """
    def __init__(self):
        self.teamID = ''
        self.etag = ''
        self.lastChecked = datetime.now(timezone.utc) # set to when program first runs
        self.failedRequests = 0
    
    def _requester(self,
            rqType:str,
            endpoint:str,
            query:dict=None,
            forceUpdate:bool=False):
        """Send requests to Extra Life API.
        Per Extra Life API guidelines, first sends only a header request to check ETag.  If the ETag has changed, then a full request is sent.

        Args:
            rqType (str): Request Type. valid request types are currently only 'get' and 'head' but only 'get' should be used.
            endpoint (str): Endpoint to make request to.  See Donordrive documentation for full list of valid endpoints.
            query (dict, optional): Query (if any) to be sent. Defaults to None.
            forceUpdate (bool, optional): If set to True, ETag will be ignored and a normal request is sent. Do not abuse. Defaults to False.

        Raises:
            e: Errors from API request

        Returns:
            any: False if no changes have been detected between checks, otherwise returns JSON dump of content.
        """
        
        headers = {
            'If-None-Match': self.etag,
            'User-Agent': 'Automated Incentives Script',
        }
        
        if forceUpdate == False: # If true, this will bypass the header check, meaning a full response will be returned.
            try:
                response = rq.request('head', BASE_URL + endpoint, headers=headers,params=query)
            except Exception as e:
                raise e
            code = response.status_code
        else:
            code = 200
        
        
        if code == 200:
            response = rq.request(rqType, BASE_URL + endpoint, headers=headers,params=query)
            if response.status_code == 304: # Sometimes header returns 200, but this returns 304.  IDK why.
                self.failedRequest = 0
                return False
            try:
                self.etag = response.headers._store['etag'][1] # Get etag from Header
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
            self.failedRequest = 0
            return False
    
        else:
            if self.failedRequests > 4:
                textOutput(f'FINAL WARNING. 5 donation checks have failed in a row.  Something is wrong, contact Finn.\nError: {code}:{response.reason}')
            else:
                textOutput('WARNING! Last donation check failed!')
                self.failedRequests += 1


    def donations(self,
                 ID:int=None,
                 idType:str='team',
                 testDonations:bool=False
                 ):
        """Check donations

        Args:
            ID (int | None, optional): Extra Life ID. If none provided, will default to the TeamID set earlier.
            idType (str, optional): Can be set to 'team', 'participant' or 'event'. Defaults to 'team'.
            testDonations (bool, optional): Whether to run test donations (external JSON file). Defaults to False.

        Raises:
            TypeError: Invalid ID provided
        
        Returns:
            any: List of donations OR False if no new donations.

        """
        ID = ID if ID != None else self.teamID # Set ID
        
        if idType.lower() not in ('team','participant','event'): # Validate ID 
            raise TypeError('Invalid ID type')
        else:
            url = idType.lower() + 's' + '/' + str(ID) + '/donations' # TODO make this an fstring
        
        if testDonations == True: # Run test donations
            try:
                print('Test donations enabled, trying to load file.')
                with open('test.json', 'r') as file:
                    testDonationList = json.load(file)
                print('Test donations loaded, you now have 15 seconds to get into the game before they start running.')
            except:
                print('Failed to find/run test donations.')
                return False
            time.sleep(15)
            return testDonationList # Return list of test donations
        
        
        queryString = {'limit': "20"} # Limits to most recent 20 donations (automatically sorted by most recent)
        response = self._requester('get',url, query=queryString)
        if response == False: # No change
            return False
            

        newInfo = []
        for item in response: # Go through responses 
            if datetime.fromisoformat(item['createdDateUTC']) < self.lastChecked and testDonations == False: # Ignore old items
                pass
            else:
                newInfo += [item]
        self.lastChecked = datetime.now(timezone.utc) # Update last checked time after parsing new responses.
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
            confirm = input(f'Found team {content['name']}. Is this correct [Y/N]: ')
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
        try:
            amsterdam = rq.get('https://timeapi.io/api/time/current/zone?timeZone=Europe/Amsterdam')
            localTime = datetime.now()
            if amsterdam.status_code != 200:
                noData = True
                failedRequests +=1 # Cannot get time
            else:
                decoded = json.loads(amsterdam.content.decode())
                realTime = datetime.fromisoformat(decoded['dateTime'])
                offsetSeconds = realTime.second - localTime.second
                return offsetSeconds
                    
        except ConnectionError:
            failedRequests +=1
            print('Failed to reach timeserver')


### Main program    
el = ExtraLife()
pricesAndIncentives = elTruck.incentiveDetails()
priceDict = pricesAndIncentives[0]
IncentiveIDsDict = pricesAndIncentives[1]

print(f'Extra Life donation monitoring script.\nVersion: {version}, Last updated: {lastUpdated}')
time.sleep(.5)
print(f'Trying to load default team, ID {defaultID}')
verifed = el.validateTeam(defaultID) # Default ID
while verifed == False:
    verifed = el.validateTeam(input('enter Extra Life Team ID: '))

userInp = input('Are you using a wheel? [Y/N]: ')
if userInp.lower() in ['y','yes']:
    wheel = True
    print('Wheel mode Enabled')
else:
    wheel = False
    print('Wheel mode Disabled')
runCommands = elTruck.TruckControls(wheel) # Set wheel mode


userInp = input('Do you want to run test donations? [Y/N]: ')
if userInp.lower() in ['y','yes']:
    testDono = True
else:
    testDono = False

print('\n\n\n\n\n\n\n\n\nScript started.  Donations will be checked every 10 - 15 seconds in order to comply with API usage rules.')

offset = syncTime()
syncedTime = datetime.now()
# Main loop
while True:
    localTime = datetime.now()
    sleepyTime = 10 - ((localTime.second + offset) % 10)
    time.sleep(sleepyTime)
    if (syncedTime + timedelta(minutes=10)) < localTime: # Resync time every 10 minutes.
        offset = syncTime()
        syncedTime = datetime.now()

    
    newDonations = el.donations(testDonations=testDono)
    testDono = False # Prevents test donations from running more than once
    if newDonations == False or newDonations in [[],'',None]:
        textOutput('No new donations.')
    
    else:
        for donation in newDonations:
            validCommand = False
            try:
                user = donation['displayName']
            except:
                user = 'Anonymous'
            
            if 'incentiveID' in donation: # Incentive ID present, use this instead of amount.
                try:
                    command = IncentiveIDsDict[donation['incentiveID']]
                    validCommand = True
                except:
                    pass
                    
            if validCommand == False: # If incentive ID is not present or failed to get correct item from ID
                try:
                    command = priceDict[donation['amount']]
                    validCommand = True
                except:
                    textOutput(f'{user} donated ${donation['amount']} but no action is asigned')
                    validCommand = False

            if validCommand == True:
                try:
                    textOutput(f'{user} donated ${donation['amount']}. Activating {command[0]}')
                    exec(f"runCommands.{command[1]}()")
                except:
                    textOutput(f'Failed to run {command[0]}')
    time.sleep(1) # Wait 1 second (avoids script rounding down and running like 5 times in 5 seconds)