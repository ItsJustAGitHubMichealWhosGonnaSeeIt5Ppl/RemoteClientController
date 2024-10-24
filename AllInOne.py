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
            self.etag = headerInfo['etag'][1] # Get etag
            return json.loads(response.content.decode(encoding='ascii'))
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


    def activity(self,ID:int=None,idType:str='team'):
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
        
        newInfo = []
        for item in response:
            if datetime.fromisoformat(item['createdDateUTC']) < self.lastChecked:
                pass # Old item, ignore
            elif item['type'] != 'donation':
                pass # not a donation
            else:
                newInfo += [item]
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
textOutput('Script started, will scan for new donations every 15 - 20 seconds')

while True:
    data = el.activity()
    if data == False or data in [[],'',None]:
        textOutput('No new donations.')
    else:
        for item in data:
            try:
                command = priceList[item['amount']]
            except:
                textOutput(f'{item['title']} donated ${item['amount']} but no action is asigned')
                
            textOutput(f'{item['title']} donated ${item['amount']}. Activating {command}')
            try:
                exec(f"elTruck.{command}")
            except:
                textOutput(f'Failed to run {command}')           
    time.sleep(15) # Wait 15 seconds before doing another action

        

