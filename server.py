import socket
import threading
import time


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
        client.send(message)
        
        
# Handling Messages From Clients
def lifeCheck(client):
    while True:
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
        time.sleep(1)


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
        
def write():
    while True:
        message = input('')
        if message == '[STOP]':
            server.close()
            break
        
        broadcast(message.encode('ascii'))
        
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()



