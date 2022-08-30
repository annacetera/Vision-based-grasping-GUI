import pygame
from pygame.locals import*
import time

class cursor():
    def __init__(self, width, length):
        self.image =  r'C:\Users\moacc\.spyder-py3\cursor.png'
        self.set_caption = 'cursor_control'
        self.width = width
        self.length = length
        self.color = (255,255,255)
        
    def draw_cursor(self, img_length, img_width, x,y):
        pygame.init()
        screen = pygame.display.set_mode((self.length, self.width))
        pygame.display.set_caption(self.set_caption)
        image = pygame.image.load(self.image)
        image = pygame.transform.scale(image, (img_length, img_width))
        image.convert()
        clock = pygame.time.Clock()
        loop = True
        while loop:
            screen.fill(self.color)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop = False
                        
            pos = tuple((x,y))
                           
            screen.blit(image,pos)
            pygame.display.update()
            clock.tick(2)
                    
        pygame.quit()
        
        
        
# white =  (255,255,255)
# cursor = cursor(width = 600 , length = 960)
# cursor.draw_cursor(img_length = 30, img_width = 30, x = 100 , y= 110)



