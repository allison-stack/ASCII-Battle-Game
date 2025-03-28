#!/usr/bin/env python3
"""
client.py
Skeleton for a networked ASCII "Battle Game" client in Python.

1. Connect to the server via TCP.
2. Continuously read user input (MOVE, ATTACK, QUIT).
3. Send commands to the server.
4. Spawn a thread to receive and display the updated game state from the server.

Usage:
   python client.py <SERVER_IP> <PORT>
"""

import sys
import socket
import threading
import select

BUFFER_SIZE = 1024
g_serverSocket = None  # shared by main thread and receiver thread

###############################################################################
# TODO: continuously receive updates (ASCII grid) from the server 
###############################################################################
def receiverThread():
    global g_serverSocket
    while True:
        try:
            data = g_serverSocket.recv(BUFFER_SIZE)
            if not data:
                print("Server disconnected")
                break
            print(data.decode('utf-8'))
        except ConnectionResetError:
            print("Connection to server lost")
            break
        except:
            print("Error receiving data")
            break

    g_serverSocket.close()
    sys.exit(0)

###############################################################################
# main: connect to server, spawn receiver thread, send commands in a loop
###############################################################################
def main():
    global g_serverSocket

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <SERVER_IP> <PORT>")
        sys.exit(1)

    serverIP = sys.argv[1]
    port = int(sys.argv[2])

    # TODO: create socket & connect to server
    g_serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Error checking server connection
    try:    
        g_serverSocket.connect((serverIP, port))
    except Exception as e:
        print(f"[ERROR] Unable to connect: {e}")
    print(f"Connected to server {serverIP}:{port}")

    #check if server full
    start_server = g_serverSocket.recv(BUFFER_SIZE).decode('utf-8')
    print(start_server)
    if "Server is full." in  start_server:
        g_serverSocket.close()
        sys.exit(0)

    # Spawn receiver thread
    t = threading.Thread(target=receiverThread)
    t.daemon = True
    t.start()

    # Main loop: read commands, send to server

    while True:
        try:
            cmd = input("Enter command (MOVE/ATTACK/FIREBALL/MSG (text)/QUIT): ")    
        except EOFError:
            # e.g., Ctrl+D
            print("Exiting client.")
            break

        if not cmd:  # empty line
            continue
        
        if (cmd.upper() not in ("MOVE UP", "MOVE DOWN", "MOVE LEFT", "MOVE RIGHT", "ATTACK", "QUIT", "FIREBALL")) and cmd.startswith("MSG ") == False:
            print("Please enter valid command.")
            continue   
        
        # TODO: send command to server
        g_serverSocket.sendall(cmd.encode('utf-8'))

        # If QUIT => break
        if cmd.upper().startswith("QUIT"):
            break

    # cleanup
    if g_serverSocket:
        g_serverSocket.close()
    sys.exit(0)

if __name__ == "__main__":
    main()
