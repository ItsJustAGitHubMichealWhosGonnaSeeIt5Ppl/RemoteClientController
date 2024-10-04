import socket
import threading
import time
from flask import Flask, render_template, request
from waitress import serve


#TODO #4 create web interface for actions

# Users connected
clientsList = []
#Usernames 
usernamesList = []

#TODO #2 Make server IP and port changeable in program
# Server info
host = '10.9.8.54'
port = 36950

# Start server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port)) 

#Maximum clients
server.listen(20)


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
                print(client)
                index = clientsList.index(client)
                clientsList.remove(client)
                client.close()
                nickname = usernamesList[index]
                usernamesList.remove(nickname)
                break
        except:
            print(client)
            # Removing And Closing Clients
            index = clientsList.index(client)
            clientsList.remove(client)
            client.close()
            nickname = usernamesList[index]
            usernamesList.remove(nickname)
            break
        


# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

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
    while True:
        if command == 'STOP':
            server.close()
            break
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
        sendCommand(incentiveName, interactive = False)
        
    return render_template('control.html',items=incentives)


# Start webserver
if __name__ == '__main__': 
    serve(app, host = host, port=8888)
