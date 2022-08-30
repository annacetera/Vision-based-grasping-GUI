# import pygame module in this program
import pygame
from pygame.locals import *
# activate the pygame library .
# initiate pygame and give permission
# to use pygame's functionality.
pygame.init()

screen_width = 800
screen_height = 700
# create the display surface object
# of specific dimension..e(500, 500).
win = pygame.display.set_mode((screen_width, screen_height))

# set the pygame window name
pygame.display.set_caption("Center_Out")

# object current co-ordinates
x = 400
y = 350

# dimensions of the object
width = 20
height = 20

# velocity / speed of movement
vel = 10


####################display text
green = (0, 255, 0)
blue = (0, 0, 128)

x_text = 400
y_text = 100

font = pygame.font.Font('freesansbold.ttf', 32)

text = font.render('Moving to A/B', True, green, blue)
 
# create a rectangular object for the
# text surface object
textRect = text.get_rect()
textRect.center = (x_text, y_text)
# Indicates pygame is running

###########################################################


run = True

# infinite loop
while run:
	# creates time delay of 10ms
	pygame.time.delay(10)
	pygame.draw.circle(win, (255,255,255),
                    (60, 300), (120, 300), 4)
	# iterate over the list of Event objects
	# that was returned by pygame.event.get() method.
	for event in pygame.event.get():
		
		# if event object type is QUIT
		# then quitting the pygame
		# and program both.
		if event.type == pygame.QUIT:
			
			# it will make exit the while loop
			run = False
	# stores keys pressed
    #pygame.draw.circle(win,[100, 100, 100], [100, 100], 20, draw_top_right=True,draw_top_left=True)

	keys = pygame.key.get_pressed()
	
	# if left arrow key is pressed
	if keys[pygame.K_LEFT] and x>0:
		
		# decrement in x co-ordinate
		x -= vel
		
	# if left arrow key is pressed
	if keys[pygame.K_RIGHT] and x<screen_width-width:
		
		# increment in x co-ordinate
		x += vel
		
	# if left arrow key is pressed
	if keys[pygame.K_UP] and y>0:
		
		# decrement in y co-ordinate
		y -= vel
		
	# if left arrow key is pressed
	if keys[pygame.K_DOWN] and y<screen_height-height:
		# increment in y co-ordinate
		y += vel



	# completely fill the surface object
	# with black colour
	win.fill((0, 0, 0))
	win.blit(text, textRect)
    
	# drawing object on screen which is rectangle here
	pygame.draw.rect(win, (255, 0, 0), (x, y, width, height))

	
	# it refreshes the window
	pygame.display.update()
  
# closes the pygame window
pygame.quit()
