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
# TODO: continuously receive updates (ASCII grid) from the server (Involves the buffer i think)
###############################################################################
def receiverThread(kill: threading.Event):
    global g_serverSocket
    while not kill.is_set():
        # Buffer from server to check if game is ending
        tr,_,_ = select.select([g_serverSocket], [], [], 0)
        if tr:
            data = g_serverSocket.recv(BUFFER_SIZE).decode()

            # TODO: implement end of game on server side
            if "Game over" in data:
                break

    # g_serverSocket.close()
    # sys.exit(0)

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

    # Spawn receiver thread
    # TODO: Implement threading for client 
    kill = threading.Event()
    t = threading.Thread(target=receiverThread, args=(kill,), daemon=True)
    t.start()

    # Main loop: read commands, send to server
    while True:
        try:
            cmd = input("Enter command (MOVE/ATTACK/QUIT): ")    
        except EOFError:
            # e.g., Ctrl+D
            print("Exiting client.")
            break

        if not cmd:  # empty line
            continue
        
        if cmd.upper() not in ("MOVE", "ATTACK", "QUIT"):
                print("Please enter valid command.")
                continue   
        
        # TODO: send command to server
        g_serverSocket.sendall(cmd.encode('utf-8').ljust(BUFFER_SIZE, b' '))

        # If QUIT => break
        if cmd.upper().startswith("QUIT"):
            break

    # cleanup
    kill.set()
    t.join()
    if g_serverSocket:
        g_serverSocket.close()
    sys.exit(0)

if __name__ == "__main__":
    main()
