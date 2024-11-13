# small network game that has differnt blobs
# moving around the screen

import pygame
from client import Network
import random
import os
import math
pygame.init()

# Constants
PLAYER_RADIUS = 10
START_VEL = 9
BALL_RADIUS = 5

SURFACE_SIZE = [256, 144]
WINDOW_SIZE = [1920, 1080]
VELOCITY = 2

BACKGROUND = pygame.image.load("images/background.png")
SHADOW = pygame.image.load("images/shadow.png")
CACTUS = pygame.image.load("images/cactus.png")
FACE = pygame.image.load("images/face.png")
FENCE = pygame.image.load("images/fence.png")

SPRITE_ORGIN = [4,12]
MAP_PADDING = [11, 6, 11, 11]

THORN_BASE_SPEED = 4
THORN_OFFSET = 6

# Dynamic Variables
players = {}
cacti = []
thorns = []

particle_list = []

# FUNCTIONS
class particle(object):
	def __init__(self, location, colour, colour_variance, speed_range, max_age_range, size_range):
		self.location = location
		self.colour_variance = colour_variance
		self.colour = (colour[0]+random.randint(-colour_variance, colour_variance),colour[1]+random.randint(-colour_variance, colour_variance),colour[2]+random.randint(-colour_variance, colour_variance))
		self.speed_range = speed_range
		self.max_age_range = max_age_range

		self.age = 0
		self.max_age = random.randint(max_age_range[0],max_age_range[1])
		self.size = random.randint(size_range[0],size_range[1])
		self.direction = random.randint(45, 135)
		self.speed = random.randint(speed_range[0], speed_range[1])-self.max_age/20

	def move(self):
		self.location[0] += self.speed*math.cos(math.radians(self.direction))
		self.location[1] += self.speed*math.sin(math.radians(self.direction))

		self.age += 1

	def boost_age(self):
		alive = True
		if self.age >= self.max_age:
			alive = False

		if self.age > 20:
			self.size = 1

		return alive

	def draw(self):
		pygame.draw.rect(surf, self.colour, (self.location[0]-int(self.size/2), self.location[1]-int(self.size/2), self.size, self.size))

def shoot(player, current_id):
	
	global thorns

	own_thorn_count = 0
	for i in thorns:
		if i[3] == current_id:
			own_thorn_count += 1
	if own_thorn_count < 2:
		mouseX, mouseY = pygame.mouse.get_pos()

		diffX = mouseX/WINDOW_SIZE[0]*SURFACE_SIZE[0]-player['x']
		diffY = mouseY/WINDOW_SIZE[1]*SURFACE_SIZE[1]-player['y']+THORN_OFFSET

		direction = math.atan(diffY/diffX)

		if diffY < 0 and diffX >= 0:
			direction += 2*math.pi

		if diffY >= 0 and diffX < 0:
			direction = math.pi-abs(direction)

		if diffY < 0 and diffX < 0:
			direction += math.pi

		# x, y, direction*100, speed, power, id
		server.send("shoot {} {} {} {} {} {}".format(int(player['x']*100)/100, int((player['y']-THORN_OFFSET)*100)/100, int(direction*100)/100, THORN_BASE_SPEED, 1, current_id))

def draw(players, cacti, thorns):
	surf.blit(BACKGROUND, (0,0))

	for i in range(len(particle_list)):
		particle_list[i].draw()

	sort_players = []
	for i in range(len(players)):
		sort_players.append([players[i]["y"],i])

	sorted_ids = []
	for i in sorted(sort_players, key=lambda x: x[0]):
		sorted_ids.append(i[1])

	for i in sorted_ids:

		animation_stage = 0

		if players[i]["moving"] % 15 >= 2 and players[i]["moving"] % 15 <= 13:
			if players[i]["moving"] % 15 >= 5 and players[i]["moving"] % 15 <= 10:
				animation_stage = 2
			else:
				animation_stage = 1

		surf.blit(SHADOW, (players[i]['x']-SPRITE_ORGIN[0], players[i]['y']-SPRITE_ORGIN[1]))
		if animation_stage >= 1:
			surf.blit(CACTUS, (players[i]['x']-SPRITE_ORGIN[0], players[i]['y']-SPRITE_ORGIN[1]-1))

		else:
			surf.blit(CACTUS, (players[i]['x']-SPRITE_ORGIN[0], players[i]['y']-SPRITE_ORGIN[1]))

		surf.blit(FACE, (players[i]['x']-SPRITE_ORGIN[0], players[i]['y']-SPRITE_ORGIN[1]-animation_stage))

	surf.blit(FENCE, (0,SURFACE_SIZE[1]-16))

	for thorn in thorns:
		pygame.draw.circle(surf, (150,150,150), [thorn[0][0], thorn[0][1]], 1)

	win.blit(pygame.transform.scale(surf, win.get_rect().size), (0, 0))
	pygame.display.update()


def main():
	global players, particle_list, thorns, server

	# start by connecting to the network
	server = Network()
	current_id = server.connect()
	players, cacti, thorns = server.send("get")

	# setup the clock, limit to 30fps
	clock = pygame.time.Clock()

	run = True
	while run:
		
		clock.tick(30) # 30 fps max
		
		player = players[current_id]
		data = ""
		
		for event in pygame.event.get():
			# if user hits red x button close window
			if event.type == pygame.QUIT:
				run = False

			if event.type == pygame.KEYDOWN:
				# if user hits a escape key close program
				if event.key == pygame.K_ESCAPE:
					run = False

			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				
				# 1 - left click, 2 - middle click, 3 - right click, 4 - scroll up, 5 - scroll down
				
				shoot(player, current_id)


		# get key presses
		keys = pygame.key.get_pressed()
		moving = False

		# movement based on key presses
		if (keys[pygame.K_LEFT] or keys[pygame.K_a]):
			if player['x'] - VELOCITY <= 0 + MAP_PADDING[2]:
				player['x'] = 0 + MAP_PADDING[2]
			elif keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_DOWN] or keys[pygame.K_s]:
				player["x"] -= 2
			else:
				player["x"] -= 2.5
			moving = True

		if (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
			if player['x'] + VELOCITY >= SURFACE_SIZE[0] - MAP_PADDING[3]:
				player['x'] = SURFACE_SIZE[0] - MAP_PADDING[3]
			elif keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_DOWN] or keys[pygame.K_s]:
				player["x"] += 2
			else:
				player["x"] += 2.5
			moving = True

		if (keys[pygame.K_UP] or keys[pygame.K_w]):
			if player['y'] - VELOCITY <= 0 + MAP_PADDING[0]:
				 player['y'] = 0 + MAP_PADDING[0]
			elif keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]:
				player["y"] -= 1.5
			else:
				player["y"] -= 2
			moving = True

		if (keys[pygame.K_DOWN] or keys[pygame.K_s]):
			if player['y'] + VELOCITY >= SURFACE_SIZE[1] - MAP_PADDING[1]:
				player['y'] = SURFACE_SIZE[1] - MAP_PADDING[1]
			elif keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]:
				player["y"] += 1.5
			else:
				player["y"] += 2
			moving = True

		if moving:
			data = "move " + str(player["x"]) + " " + str(player["y"])
			# send data to server and recieve back all players information
			players, cacti, thorns = server.send(data)

		else:
			players, cacti, thorns = server.send("get")
		
		for i in range(len(players)):
			# location, colour, colour_variance, speed_range, max_age_range, size_range
			for j in range(2):
				particle_list.append(particle([players[i]['x'], players[i]['y']-3], players[i]['colour'], 30, (1,1), (0,35), (1,2)))

		for i in range(len(particle_list)):
			particle_list = [i for i in particle_list if i.boost_age()]

		for i in range(len(particle_list)):
			particle_list[i].move()

		# redraw window then update the frame
		draw(players, cacti, thorns)

	server.disconnect()
	pygame.quit()
	quit()

# make window start in top left hand corner
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)

# setup pygame window
surf = pygame.Surface(SURFACE_SIZE)
win = pygame.display.set_mode(WINDOW_SIZE, pygame.NOFRAME)
pygame.display.set_caption("Cacti")

# start game
main()