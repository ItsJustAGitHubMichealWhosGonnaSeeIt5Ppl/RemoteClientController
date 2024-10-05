import socket
import threading
import time
import re
from flask import Flask, render_template, request
from waitress import serve



#TODO #2 Make server IP and port changeable in program
# Server info


def inputValidator(message, validInputs, maxAttemps=10,exitOnFailure=True):
    """Basic input validation function.

    Args:
        message (string): Message to be sent requesting user input.
        validInputs (list): list of valid inputs. Not case sensitive.
        maxAttemps (int, optional): Maximum attempts allowed. Defaults to 10.
        exitOnFailure (bool, optional): Specifies whether entire program should close if no valid user input is given. Defaults to True.

    Returns:
        string: user input or failure code.
    """
    validInput = False
    attempts = 0
    while validInput == False and attempts < maxAttemps:
        usrInp = input(message)
        if usrInp.lower() in validInputs.lower():
            return usrInp
        else:
            print('Invalid response')
            attempts +=1

    if exitOnFailure == True:
        print('Max attempts reached, stopping program')
        exit()
    else:
        print('Max attempts reached, skipping')
        return 'maxAttemptsReached'
        

# I know I could use configparser, but I don't want more modules
print('Trying to load details from config')
try:
    config = open('config.txt', 'r')
    for line in config:
        if line.startswith('IP'):
            host = line.replace('IP=','')
        elif line.startswith('PORT'):
            port = int(line.replace('PORT=',''))
    config.close()
    configFound = True

except:
    configFound = False

# Offer to load existing config
if configFound == True:
    print(f'Existing config found\nIP/HOST: {host}\nPORT: {port}\n Would you like to use it?')    
    userResponse = inputValidator('Y/N: ',['y','yes','n','no'])
    if userResponse.lower().startswith('n'):
        print('Enter desired IP and port for the server')
        host = input('IP/Host: ')
        port = input('Port: ')



#TODO #12 add better input validation here
# Start server
try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port)) 
except:
    print('Server failed to start')
    exit()


# Offer to save config
print('Would you like to save the current server settings?')
userResponse = inputValidator('Y/N: ',['y','yes','n','no'],10,False)
if userResponse ==' maxAttemptsReached':
    pass
elif userResponse.lower().startswith('n'):
    print('config not saved')
else:
    try:
        config = open('config.txt', 'w')
        config.write(f"IP={host}\nPORT={port}")
        config.close()
    except:
        print('failed to save config, try again later')


#TODO #13 Make username and client list into dictionary
# Users
clientsList = []
#Usernames 
usernamesList = []


#Maximum clients
server.listen(20)

#Broadcast messages
def broadcast(message):
    for client in clientsList:
        client.send(message.encode('ascii'))
        
        
# Handling Messages From Clients
def lifeCheck(client):
    while True:
        time.sleep(1)
        try:
            # Check if client is still connected
            client.send('ALIVE'.encode('ascii'))
            if client.recv(1024).decode('ascii') == 'YES':
                continue
            else:
                index = clientsList.index(client)
                clientsList.remove(client)
                client.close()
                nickname = usernamesList[index]
                usernamesList.remove(nickname)
                print(f'{nickname} disconnected (timeout)')
                break
        except:
            print(client)
            # Removing And Closing Clients
            index = clientsList.index(client)
            clientsList.remove(client)
            client.close()
            nickname = usernamesList[index]
            usernamesList.remove(nickname)
            print(f'{nickname} disconnected (exception)')
            break
        


# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("New user connected from {}".format(str(address)))

        # Request And Store Nickname
        client.send('IDENT'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        usernamesList.append(nickname)
        clientsList.append(client)

        # Print And Broadcast Nickname
        print("Nickname is {}".format(nickname))

        # Start Handling Thread For Client
        thread = threading.Thread(target=lifeCheck, args=(client,))
        thread.start()



# Send commands
#TODO #10 This doesn't need to be a thread, convert to be used as needed.
# TODO #11 Switch command sending to use json.loads and json.dumps
def sendCommand(command,interactive,*extra):
    
    if command == 'STOP':
        server.close()
    broadcast(command)


# Start thread
receive_thread = threading.Thread(target=receive)
receive_thread.start()

#ommandThread = threading.Thread(target=sendCommand)
#commandThread.start()




incentives = ["parkingBrake","towToService","everyCam","cinematicCam","metalPipes","slalom"]
incentivesInteractive = []
# # # Flask 

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def main():
    
    # This is my genius way to allow the button name list to be easily updated
    if request.method == 'POST':
        incentiveName = list(request.form.listvalues())[0][0]
        print(f'{incentiveName} pressed')
        sendCommand(incentiveName+ "()", interactive = False)
        
    return render_template('control.html',items=incentives)


# Start webserver
if __name__ == '__main__': 
    serve(app, host = host, port=8888)
