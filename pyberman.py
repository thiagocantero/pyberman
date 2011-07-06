#pyberman.py
#Copyright (C) 2011 PyTeam

"""The Pyberman runner."""

import sys
import pygame
from pygame.locals import *
from gameobjects import *
from ui import MainMenu, ChooseLevelMenu
import events


class Game(events.AutoListeningObject):
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
            'framerate': 50,
            }
        }

    def __init__(self):
        """Initializes the game."""
        pygame.init()
        pygame.display.set_caption('Pyberman')
        #self.surface = pygame.display.set_mode((self.config['screen']['width'], self.config['screen']['height']), FULLSCREEN|DOUBLEBUF     |HWSURFACE)
        # use default resolution
        self.surface = pygame.display.set_mode((0,0), FULLSCREEN|DOUBLEBUF     |HWSURFACE)
        self.screen_height = pygame.display.Info().current_h
        self.screen_width = pygame.display.Info().current_w
        self.create_groups()
        #: Whether the main loop should run
        self.done = False
        super(Game, self).__init__()

    def __del__(self):
        """Deinitializes the game."""
        pygame.quit ()

    def main_loop(self):
        """Starts the game's main loop."""
        #Todo: load a this actually should be done when users selects the level in the GUI
        #mainmenu=MainMenu(self)        
        #to control a framerate
        clock = pygame.time.Clock()
        self.load_level('Maps\\map1.bff')
        while not self.done:
            for event in pygame.event.get():
                events.Event.process_event(events.event_from_pygame_event(self, event))
            self.update()
            self.redraw()
            pygame.display.flip()
            #Let other processes to work a bit, limiting the framerate
            clock.tick(self.config['general']['framerate'])

    def event_keydown(self, event):
        if event.key==K_ESCAPE:
            event.stop_propagating = True
            events.Event.process_event(events.QuitEvent(self))

    def event_quit(self, event):
        self.done = True

    def load_level(self, filename):
        with open(filename) as f:
            self.height,self.width,self.max_players = [int(x) for x in f.readline().split()]
            self.side=min((self.screen_height//self.height,self.screen_width//self.width))
            self._absw = (self.screen_width-(self.width*self.side))//2
            self._absh = (self.screen_height-(self.height*self.side))//2
            for row_num, row in enumerate(f):
                if row_num == self.height: raise RuntimeError('Too many lines in the file')
                for col_num, col in enumerate(row.strip()):
                    if col_num == self.width: raise RuntimeError('Too many colums in row %d'%row_num+1)
                    if col == 'W':
                        Wall(self, col_num, row_num, groups=(self.all, self.obstacles))
                    elif col == 'B':
                        Box(self, col_num, row_num, groups=(self.all, self.dynamic, self.obstacles))
                    elif col == ' ': 
                        pass
                    elif col.isdigit() and int(col)<10:
                        Player(self, col_num, row_num, int(col)-1, groups=(self.all, self.dynamic))
                    else:
                        raise RuntimeError('Unknown symbol "%s" in row %d, col %d'%(col, row_num+1, col_num+1))
                if col_num<self.width-1:
                    raise RuntimeError('Insuficient number of colums in row %d'%row_num+1)
            if row_num<self.height-1:
                raise RuntimeError('Insuficient number of rows')

    def xcoord_to_screen(self, x):
        """Translates given x coordinate from the game coord system to screen coord system."""
        return self._absw+x*self.side

    def ycoord_to_screen(self, y):
        """Translates given y coordinate from the game coord system to screen coord system."""
        return self._absh+y*self.side

    def create_groups(self):
        self.all = pygame.sprite.RenderUpdates()
        self.obstacles = pygame.sprite.Group()
        self.dynamic = pygame.sprite.Group() #those objects which may progress over time

    def redraw(self):
        """Redraws the level. It is called each core pumb"""
        self.all.draw(self.surface)

    def update(self):
        self.all.update()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance=Game()
        return cls._instance

if __name__=="__main__":
    Game.instance().main_loop()
