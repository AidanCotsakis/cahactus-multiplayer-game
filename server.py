"""
main server script for running agar.io server

can handle multiple/infinite connections on the same
local network
"""
import socket
from _thread import *
import _pickle as pickle
import time
import random
import math

# setup sockets
S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
S.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Set constants
PORT = 5050

SURFACE_SIZE = [256, 144]

HOST_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(HOST_NAME)

# try to connect to server
try:
    S.bind((SERVER_IP, PORT))
except socket.error as e:
    print(str(e))
    print("[SERVER] Server could not start")
    quit()

S.listen()  # listen for connections

print(f"[SERVER] Server Started with local ip {SERVER_IP}")

# dynamic variables
players = {}
cacti = []
thorns = []
colour_variance = 30
colours = (
	(255-colour_variance,0+colour_variance,0+colour_variance),
	(0+colour_variance,0+colour_variance,255-colour_variance),
	(0+colour_variance,200-colour_variance,200-colour_variance),
	(200-colour_variance,0+colour_variance,200-colour_variance)
)

connections = 0
_id = 0
start = False

# FUNCTIONS

def calculate_thorns():

	global thorns

	for i in range(len(thorns)):
		thorns[i][0][0] = int((thorns[i][0][0]+thorns[i][1][0])*100)/100
		thorns[i][0][1] = int((thorns[i][0][1]+thorns[i][1][1])*100)/100

def thorn_collide(i):
	alive = True
	if i[0][0] < 0 or i[0][0] > SURFACE_SIZE[0] or i[0][1] < 0 or i[0][1] > SURFACE_SIZE[1]:
		alive = False

	return alive


def threaded_client(conn, _id):
	"""
	runs in a new thread for each player connected to the server

	:param con: ip address of connection
	:param _id: int
	:return: None
	"""
	global connections, players, cacti, thorns

	current_id = _id

	# Setup properties for each new player
	colour = colours[current_id]
	x = SURFACE_SIZE[0]/(len(colours)+1) + current_id*SURFACE_SIZE[0]/(len(colours)+1)
	y = SURFACE_SIZE[1]/2
	players[current_id] = {"x":x, "y":y,"colour":colour,"moving":0}  # x, y colour, score, name

	# pickle data and send initial info to clients
	conn.send(str.encode(str(current_id)))

	# server will recieve basic commands from client
	# it will send back all of the other clients info
	'''
	commands start with:
	move
	jump
	get
	id - returns id of client
	'''
	while True:
		try:
		# if True:
			# Recieve data from client
			data = conn.recv(32)

			if not data:
				break

			data = data.decode("utf-8")
			#print("[DATA] Recieved", data, "from client id:", current_id)

			if current_id == 0:
				calculate_thorns()
				thorns = [i for i in thorns if thorn_collide(i)]

			# look for specific commands from recieved data
			if data.split(" ")[0] == "move":
				split_data = data.split(" ")
				players[current_id]["x"] = float(split_data[1])
				players[current_id]["y"] = float(split_data[2])
				players[current_id]["moving"] += 1
				send_data = pickle.dumps((players, cacti, thorns))
			else:
				players[current_id]["moving"] = 0

			if data.split(" ")[0] == "id":
				send_data = str.encode(str(current_id))  # if user requests id then send it

			elif data.split(" ")[0] == "shoot":
				# x, y, direction, speed, power, id
				split_data = data.split(" ")
				# thorns [[x,y], dir[x,y], damage, ownerID]
				thorns.append([[float(split_data[1]), float(split_data[2])], [int((int(split_data[4]) * math.cos(float(split_data[3])))*100)/100, int((int(split_data[4]) * math.sin(float(split_data[3])))*100)/100], int(split_data[5]), int(split_data[6])])
				send_data = pickle.dumps((players, cacti, thorns))

			else:
				# any other command just send back list of players
				send_data = pickle.dumps((players, cacti, thorns))

			# send data back to clients
			conn.send(send_data)

		except Exception as e:
			print(e)
			break  # if an exception has been reached disconnect client

		time.sleep(0.001)

	# When user disconnects	
	print("[DISCONNECT] Client Id:", current_id, "disconnected")

	connections -= 1 
	del players[current_id]  # remove client information from players list
	conn.close()  # close connection


# MAINLOOP

print("[GAME] Setting up level")
print("[SERVER] Waiting for connections")

# Keep looping to accept new connections
while True:
	
	host, addr = S.accept()
	print("[CONNECTION] Connected to:", addr)

	# start game when a client on the server computer connects
	if addr[0] == SERVER_IP and not(start):
		start = True
		print("[STARTED] Game Started")

	# increment connections start new thread then increment ids
	connections += 1
	start_new_thread(threaded_client,(host,_id))
	_id += 1

# when program ends
print("[SERVER] Server offline")
