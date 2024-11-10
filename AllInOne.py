
import requests as rq
from datetime import datetime, timezone
import json
import urllib.parse
import incentiveFiles.truckIncentives as elTruck
import time

### Access ExtraLife
# Donor Drive API link

BASE_URL = 'https://www.extra-life.org/api/'

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
            self.failedRequests = 0
            response = rq.request(rqType, BASE_URL + url, headers=headers)
            headerInfo = response.headers._store
            try:
                self.etag = headerInfo['etag'][1] # Get etag
            except:
                pass
            return json.loads(response.content.decode(encoding='utf-8'))
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


    def activity(self,ID:int=None,idType:str='team',testDonations=False):
        if testDonations == True:
            try:
                with open('test.json', 'r') as file:
                    testDonationList = json.load(file)
            except:
                print('Failed to find/run test donations')
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
            print(f'{teamID} is not a valid team ID, please double chekc and try again.')
            return False
        else:
            content = json.loads(response.content.decode(encoding='ascii'))
            confirm = input(f'Found team {content['name']}. If this is correct, press Y and hit Enter. Otherwise, press any other key\n:')
            if confirm.lower() not in ['y', 'yes']:
                return False
            else:
                self.teamID = teamID
                return True

def textOutput(text):
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print(f'[{now}] {text}')  
        
### Main program    
el = extraLife()
priceList = elTruck.createPriceDict()
verifed = False
while verifed == False:
    verifed = el.validateTeam(input('enter Extra Life Team ID: '))

testDono = False
userInp = input('Do you want to run test donations? [Y/N]: ')
if userInp.lower() in ['y','yes']:
    testDono = True
textOutput('Script started, will scan for new donations every 15 - 20 seconds. Open the game within the next 15 seconds')
time.sleep(15)

while True:
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
    time.sleep(15) # Wait 15 seconds before doing another action
    userAnswer = False

        
