#pyberman.py
#Copyright (C) 2011 PyTeam

"""The Pyberman runner."""
import sys
import pygame
import GameObjects
from pygame.locals import *
pygame.init()

def main():
    screen = pygame.display.set_mode((800,600),FULLSCREEN)
    level=GameObjects.Level('D:\\projects\\pyberman\\Maps\\map1.bff')

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        screen.fill((100,100,100))
        for obj in level.objects:
            screen.blit(obj.pict,obj.pictrect)
        pygame.display.flip()

if __name__=="__main__":
    main()
