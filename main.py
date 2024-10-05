import tkinter as tk
from tkinter import ttk

import socket 
import threading
import incentiveFiles.truckIncentives as incnt # THIS IS USED



username = None
pauseConnection = True
socketConnected = False # Connected True/False


# Listening to Server and Sending Nickname
def receive():
    global username
    global socketConnected
    global pauseConnection
    while True:
        
        # Client not doing anything
        if socketConnected == False and pauseConnection == True:
            continue
        
        # Client trying to disconnect
        elif socketConnected == True and pauseConnection == True:
            socketConnected = False
            cButtonText.set('Connect')
            connectionStatus.set('Disconnected')
            client.close()
        
        # Client is connected and ready to receive commands
        elif socketConnected == True:
            try:
                raw = client.recv(1024)
                message = raw.decode('ascii')
            except:
                socketConnected = False
                pauseConnection = True
                cButtonText.set('Connect')
                connectionStatus.set('Server Crashed')
                client.close()
            
            # Server crashed
            if raw == b'':
                socketConnected = False
                pauseConnection = True
                cButtonText.set('Connect')
                connectionStatus.set('Server Error')
                client.close()
            
            # Server requesting username
            elif message == 'IDENT':
                client.send(username.encode('ascii'))
            
            # Server trying to see if client is still alive
            elif message == 'ALIVE':
                client.send('YES'.encode('ascii'))
            else:
                try:
                    # TODO #3 Allow commands to be sent without parenthesis
                    exec(f"incnt.{message}")
                except:
                    print(f'No incentive with name {message}')
        
        # Allow client to try to connect            
        elif socketConnected == False and pauseConnection == False:
            try:
                socketConnected = True
                cButtonText.set('Disconnect')
                connectionStatus.set('Connected')
            except:
                socketConnected = False
                cButtonText.set('Connect')
                connectionStatus.set('Connection Failed')
                pauseConnection = True
                client.close()
        else:
            continue
        
                

# Create receive thread
receive_thread = threading.Thread(target=receive)
# Start thread to receive commands
receive_thread.start()


def connectionToggle():
    global socketConnected, client
    global username
    global pauseConnection
    
    if socketConnected == False:
        
        # Basic input validation
        if usernameField.get() == '':
            connectionStatus.set('invalid username')
        elif ipField.get() == '':
            connectionStatus.set('invalid IP/Host')
        elif portField.get() == '' or portField.get().isdigit() == False:
            connectionStatus.set('invalid Port')
        else:
        # Get values
            username = str(usernameField.get())
            ip = str(ipField.get())
            port = int(portField.get())
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connectionStatus.set('Connecting')
            try:
                client.connect((ip, port))
                pauseConnection = False
            except socket.gaierror:
                connectionStatus.set('invalid IP/Host')
            except ConnectionRefusedError:
                connectionStatus.set('Connection Refused')
        
    else:
        #Stop receiving commands
        pauseConnection = True

# # # # Tkinter # # # # 

# TKinter UI
guiRoot = tk.Tk()
guiRoot.title('ExtraLife Incentives Client')
guiFrame = ttk.Frame(guiRoot)



# TKinter variables
cButtonText = tk.StringVar() # Connection toggle button
cButtonText.set('Connect')
connectionStatus = tk.StringVar()
connectionStatus.set('Not Connected')




#Fields
usernameField = tk.Entry(guiFrame,text='username')
ipField = tk.Entry(guiFrame,text='ip')
portField = tk.Entry(guiFrame,text='port')

# Buttons and status
connectButton = tk.Button(guiFrame,textvariable=cButtonText, width=10,command=connectionToggle)
statusLabel = ttk.Label(guiFrame,textvariable=connectionStatus,justify='center') 

#Text
usernameText = ttk.Label(guiFrame,text='Username')
ipText = ttk.Label(guiFrame,text='IP/Host')
portText = ttk.Label(guiFrame,text='Port')

# Pack everything
usernameText.grid(column=0,row=0)
ipText.grid(column=0,row=1)
portText.grid(column=0,row=2)
statusLabel.grid(column=0,row=3)
usernameField.grid(column=1,row=0)
ipField.grid(column=1,row=1)
portField.grid(column=1,row=2)
connectButton.grid(column=1,row=3)
guiFrame.pack()

# Start it
guiRoot.mainloop()

