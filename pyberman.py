#pyberman.py
#Copyright (C) 2011 PyTeam

"""The Pyberman runner."""

import sys
import pygame
from pygame.locals import *
import GameObjects


class Game(object):
    """Represents a high-level game instance.
    Should be a singleton.
    """
    #Todo: implement reading from a config file
    config = {
        'screen': {
            'width': 800, 
            'height': 600,
            },
        'general': {
            'framerate': 50,
            }
        }

    def __init__(self):
        """Initializes the game."""
        pygame.init()
        pygame.display.set_caption('Pyberman')
        self.surface = pygame.display.set_mode((self.config['screen']['width'], self.config['screen']['height']), FULLSCREEN)
        #Todo: load a this actually should be done when users selects the level in the GUI
        self.level = GameObjects.Level('D:\\projects\\pyberman\\Maps\\map1.bff')

    def __del__(self):
        """Deinitializes the game."""
        pygame.quit ()

    def main_loop(self):
        """Starts the game's main loop."""
        #to control a framerate
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: break
            self.surface.fill((100,100,100))
            for obj in self.level.objects:
                self.surface.blit(obj.pict,obj.pictrect)
            pygame.display.update()
            #Let other processes to work a bit, limiting the framerate
            clock.tick(self.config['general']['framerate'])

if __name__=="__main__":
    game = Game()
    game.main_loop()
