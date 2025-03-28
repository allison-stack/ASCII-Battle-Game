[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/GT67vYVA)
# Networked ASCII "Battle Game"

## Additional Documentation
****

## Overview

This program implements a **client-server** ASCII-based game using **TCP sockets**.  
You will:
1. **Design an application-level protocol** (how clients and server exchange messages).
2. **Implement the socket code** (on both the server and client side).
3. **Manage concurrency** on the server (e.g., using threads or I/O multiplexing).
4. **Implement game logic** for a simple “battle” scenario with movement, attacks, and obstacles.


---

## Game Logic
The following commands can be used on the client-side:
1. "MOVE (DOWN/UP/RIGHT/LEFT)": Moves the client one position in the specified direction
2. "ATTACK": Any adjacent players (in the upper, lower, left, or right positions) decrease in 10 HP when this command is called.
3. "FIREBALL": Causes players within a 2x2 grid of the client who called the command to decrease in 20 HP.
4. "MSG (text)": Causes a specified message from the client to be broadcasted to all players of the game.
5. "QUIT": Ends the game connection for that specific player.

## Features and Protocol

1. **Server**
    - Listens on a TCP socket.
    - Accepts up to 4 clients.
    - Maintains a **GameState** (a 2D grid).
    - Supports commands : **MOVE (UP/DOWN/LEFT/RIGHT)**, **ATTACK**, **FIREBALL**, **MSG (TEXT)**, **QUIT**, etc.
    - After each valid command, it **broadcasts** the updated game state to all players.

2. **Client**
    - Connects to the server via TCP.
    - Sends user-typed commands.
    - Continuously **receives** and displays updates of the ASCII grid (plus any extra info).

3. **Protocol**
    - Documented (in code comments or a separate file/section).
    - Server responds to client in real-time to handle any errors or changes in state.  

4. **Game Logic**
    - 2D grid (e.g., 5×5).
    - **Obstacles** (`#`) block movement.
    - **Players** are labeled `'A', 'B', 'C', 'D'`.
    - **Attacks**: Deducts 10 HP from adjacent players, or deducts 20 HP if a fireball attack is used. 
    - **Quit**: On `QUIT`, the client disconnects, and the server updates the state accordingly.

5. **Extra Features** 
    - Chat features: The server broadcasts messages to each client if a client uses a "MSG" command.
    - Advanced attack: the "FIREBALL" attack can be used by clients to deduct more HP onto other players.

---


## Instructions 

1. Open `server.py` and `client.py`.
2. Complete all **TODO** sections.
3. **Run**:
```shell
# Server
python server.py 12345

# Client
python client.py 127.0.0.1 12345
```
Where `12345` is your chosen port, and `127.0.0.1` is the server IP (local host).

