#!/usr/bin/env python3
"""
server.py
Skeleton for a networked ASCII "Battle Game" server in Python.

1. Create a TCP socket and bind to <PORT>.
2. Listen and accept up to 4 client connections.
3. Maintain a global game state (grid + players + obstacles).
4. On receiving commands (MOVE, ATTACK, QUIT, etc.), update the game state
   and broadcast the updated state to all connected clients.

Usage:
   python server.py <PORT>
"""

import sys
import socket
import threading

MAX_CLIENTS = 4
BUFFER_SIZE = 1024
GRID_ROWS = 5
GRID_COLS = 5

###############################################################################
# Data Structures
###############################################################################

# Each player can be stored as a dict, for instance:
# {
#    'x': int,
#    'y': int,
#    'hp': int,
#    'active': bool
# }

# The global game state might be stored in a dictionary:
# {
#   'grid': [ [char, ...], ... ],        # 2D list of chars
#   'players': [ playerDict, playerDict, ...],
#   'clientCount': int
# }

g_gameState = {}
g_clientSockets = [None] * MAX_CLIENTS  # track client connections
g_stateLock = threading.Lock()          # lock for the game state


###############################################################################
# Initialize the game state
###############################################################################
def initGameState():
    global g_gameState
    # Create a 2D grid filled with '.'
    grid = []
    for r in range(GRID_ROWS):
        row = ['.'] * GRID_COLS
        grid.append(row)

    # Example: place a couple of obstacles '#'
    # (Feel free to add more or randomize them.)
    grid[2][2] = '#'
    grid[1][3] = '#'

    # Initialize players
    players = []
    for i in range(MAX_CLIENTS):
        p = {
            'x': -1,
            'y': -1,
            'hp': 100,
            'active': False,
            'msg': ""
        }
        players.append(p)

    g_gameState = {
        'grid': grid,
        'players': players,
        'clientCount': 0
    }

###############################################################################
# Refresh the grid with current player positions.
# We clear old player marks (leaving obstacles) and re-place them according
# to the players' (x,y).
###############################################################################
def refreshPlayerPositions():
    """Clear old positions (leaving obstacles) and place each active player."""
    grid = g_gameState['grid']
    players = g_gameState['players']

    # Clear non-obstacle cells
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if grid[r][c] != '#':
                grid[r][c] = '.'

    # Place each active player
    for i, player in enumerate(players):
        if player['active'] and player['hp'] > 0:
            px = player['x']
            py = player['y']
            grid[px][py] = chr(ord('A') + i)  # 'A', 'B', 'C', 'D'

###############################################################################
# TODO: Build a string that represents the current game state (ASCII grid), 
# which you can send to all clients.
###############################################################################
def buildStateString():
    # e.g., prefix with "\n--- GAME STATE ---\n", then rows of the grid, then player info
    buffer = []
    buffer.append("\n--- GAME STATE ---\n")

    # Copy the grid
    grid = g_gameState['grid']
    for i in grid:
        row_string = ''.join(i)
        buffer.append(row_string + '\n')
    
    # ...
    # Optionally append player info

    buffer.append('\n')
    buffer.append('Players:\n')
    players = g_gameState['players']

    for i, player in enumerate(players):
        if player['active'] and player['hp'] > 0:
            current = chr(ord('A') + i)
            row_string = f"Player {current}: HP={player['hp']} Pos=({player['x']}, {player['y']})"
            buffer.append(row_string + '\n')

    

    for j, player in enumerate(players):
        if player['msg'] != "" and player['active']:
            buffer.append('\n')
            buffer.append('New Message:\n')
            current = chr(ord('A') + j)
            row_string = f"Player {current} says: {player['msg']}"
            buffer.append(row_string + '\n')
            player['msg'] = ""
    

    return ''.join(buffer)


###############################################################################
# Broadcast the current game state to all connected clients
###############################################################################
def broadcastState():
    stateStr = buildStateString().encode('utf-8')
    
    # send buffer to each active client
    for sock in g_clientSockets:
        if sock is not None:
            try:
                sock.sendall(stateStr)
            except:
                continue
    



###############################################################################
# TODO: Handle a client command: MOVE, ATTACK, QUIT, etc.
#  - parse the string
#  - update the player's position or HP
#  - call refreshPlayerPositions() and broadcastState()
###############################################################################
def handleCommand(playerIndex, cmd):
    with g_stateLock:
        players = g_gameState['players']
        nx = players[playerIndex]['x']
        ny = players[playerIndex]['y']

        # parse and handle "MOVE UP", "MOVE DOWN", "MOVE LEFT", "MOVE RIGHT" commands
        if cmd.startswith("MOVE"):
            if "UP" in cmd:
                nx -= 1
                if 0 <= nx < GRID_ROWS and g_gameState['grid'][nx][ny] != '#':
                    players[playerIndex]['x'] = nx
            elif "DOWN" in cmd:
                nx += 1
                if nx < GRID_ROWS and g_gameState['grid'][nx][ny] != '#':
                    players[playerIndex]['x'] = nx
            elif "LEFT" in cmd:
                ny -= 1
                if 0 <= ny < GRID_COLS and g_gameState['grid'][nx][ny] != '#':
                    players[playerIndex]['y'] = ny
            elif "RIGHT" in cmd:
                ny += 1
                if ny < GRID_COLS and g_gameState['grid'][nx][ny] != '#':
                    players[playerIndex]['y'] = ny
        # parse and handle "ATTACK" command (subtract -10hp from other player)
        elif cmd.startswith("ATTACK"):
            x_lower = max(0, nx - 1)
            x_upper = min(GRID_ROWS, nx + 1)
            y_lower = max(0, ny - 1)
            y_upper = min(GRID_COLS, ny + 1)

            for i, value in enumerate(players):
                if i != playerIndex and value['active'] and value['hp'] > 0:
                      if x_lower <= value['x'] <= x_upper and y_lower <= value['y'] <= y_upper:
                            value['hp'] -= 10
        # parse and handle "FIREBALL" command (subtract -20hp from other player)
        elif cmd.startswith("FIREBALL"):
            x_lower = max(0, nx - 2)
            x_upper = min(GRID_ROWS - 1, nx + 2)
            y_lower = max(0, ny - 2)
            y_upper = min(GRID_COLS - 1, ny + 2)

            for i, value in enumerate(players):
                if i != playerIndex and value['active'] and value['hp'] > 0:
                    if x_lower <= value['x'] <= x_upper and y_lower <= value['y'] <= y_upper:
                        value['hp'] -= 20
        # parse and handle "MSG" command (message broadcasted to all clients)
        elif cmd.startswith("MSG "):
            players[playerIndex]['msg'] = cmd[4:]
            
                
        # ...
        # elif cmd.startswith("QUIT"):
        # ...

        # Refresh and broadcast
        refreshPlayerPositions()
        broadcastState()

###############################################################################
# Thread function: handle communication with one client
###############################################################################
def clientHandler(playerIndex, clientSock):
    sock = g_clientSockets[playerIndex]

    # Initialize player
    with g_stateLock:
        g_gameState['players'][playerIndex]['x'] = playerIndex  # naive example
        g_gameState['players'][playerIndex]['y'] = 0
        g_gameState['players'][playerIndex]['hp'] = 100
        g_gameState['players'][playerIndex]['active'] = True
        g_gameState['clientCount'] += 1 # Increment num of active clients
    refreshPlayerPositions()
    broadcastState()

    
    while True:
        try:
            data = sock.recv(BUFFER_SIZE)
            if not data:
                break  # client disconnected
            
            print(f"Player {chr(ord('A') + playerIndex)}: {data}")
            handleCommand(playerIndex, data.decode('utf-8').strip())
        except:
            break  # On error, break out

    # Cleanup on disconnect
    print(f"Player {chr(ord('A') + playerIndex)} disconnected.")
    sock.close()

    with g_stateLock:
        g_clientSockets[playerIndex] = None
        g_gameState['players'][playerIndex]['active'] = False
        g_gameState['clientCount'] -= 1
        refreshPlayerPositions()
        broadcastState()

###############################################################################
# main: set up server socket, accept clients, spawn threads
###############################################################################
def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <PORT>")
        sys.exit(1)

    port = int(sys.argv[1])

    initGameState()

    # TODO: create server socket, bind, listen
    # Example:
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSock.bind(('', port))
    serverSock.listen(5)
    
    print(f"Server listening on port {port}...")

    while True:
        try:
            # TODO: accept new connection
            clientSock, addr = serverSock.accept()
            print(f"Accepted new client from {addr}")

            # 1) Lock state
            with g_stateLock:
                # 2) Check if g_gameState['clientCount'] < MAX_CLIENTS
                #    otherwise, reject
                if g_gameState['clientCount'] >= MAX_CLIENTS:
                    clientSock.sendall("Server is full.".encode('utf-8'))
                    clientSock.close()
                    continue
                else:
                    # 3) find a free slot in g_clientSockets
                    for slot in range (MAX_CLIENTS):
                        if g_clientSockets[slot] == None:
                            g_clientSockets[slot] = clientSock
                            # 4) spawn a thread => threading.Thread(target=clientHandler, args=(slot,))
                            thread = threading.Thread(target=clientHandler, args=(slot, clientSock))
                            thread.start()
                            break
        except socket.timeout:
            continue
        except Exception as e:
            print(f"[ERROR] Accepting a connection: {e}") 
    serverSock.close()

if __name__ == "__main__":
    main()
