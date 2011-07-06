#pyberman.py
#Copyright (C) 2011 PyTeam

"""The Pyberman runner."""

import sys
import pygame
import ctypes
from pygame.locals import *
import ctypes
import GameObjects


class Game(object):
    """Represents a high-level game instance.
    Should be a singleton.
    """
    _instance = None
    #Todo: implement reading from a config file
    config = {
        'screen': {
            #'width': ctypes.windll.user32.GetSystemMetrics(0), 
            #'height': ctypes.windll.user32.GetSystemMetrics(1),
            },
        'general': {
            'framerate': 1,
            }
        }

    def __init__(self):
        """Initializes the game."""
        pygame.init()
        pygame.display.set_caption('Pyberman')
        #self.surface = pygame.display.set_mode((self.config['screen']['width'], self.config['screen']['height']), FULLSCREEN|DOUBLEBUF     |HWSURFACE)
        self.surface = pygame.display.set_mode((0,0), FULLSCREEN|DOUBLEBUF     |HWSURFACE)
        self.height = pygame.display.Info().current_h
        self.width = pygame.display.Info().current_w
        self.level = None

    def __del__(self):
        """Deinitializes the game."""
        pygame.quit ()

    def main_loop(self):
        """Starts the game's main loop."""
        #Todo: load a this actually should be done when users selects the level in the GUI
        self.level = GameObjects.Level('Maps\\map1.bff',self.height,self.width)
        #to control a framerate
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): return
            self.level.update()
            #self.surface.fill(pygame.Color.b)
            self.level.draw(self.surface)
            pygame.display.flip()
            #Let other processes to work a bit, limiting the framerate
            clock.tick(self.config['general']['framerate'])

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance=Game()
        return cls._instance

if __name__=="__main__":
    Game.instance().main_loop()
