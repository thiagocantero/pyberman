#pyberman.py
#Copyright (C) 2011 PyTeam

'''The Pyberman runner.
version 0.1 alpha
It really works!
'''

import sys
import os
import random
import pygame
from pygame.locals import *
from gameobjects import *
from ui import MainMenu
import events
import controller


class Game(events.AutoListeningObject):
    '''Represents a high-level game instance.
    Should be a singleton.
    '''
    _instance = None
    #Todo: implement reading from a config file
    config = {
        'screen': {
            #'width': 800
            #'height': 600
            },
        'general': {
            'framerate': 50,
            }
        }

    def __init__(self):
        '''Initializes the game.'''
        pygame.init()
        pygame.mixer.init()
        self.menu_sound = pygame.mixer.Sound(os.path.join('Data','Pandemonium.ogg'))
        self.menu_click = pygame.mixer.Sound(os.path.join('Data','click.ogg'))
        self.explosions = [pygame.mixer.Sound(os.path.join('Data','explosion.ogg')),pygame.mixer.Sound(os.path.join('Data','explosion2.ogg')),pygame.mixer.Sound(os.path.join('Data','explosion3.ogg'))]
        pygame.display.set_caption('Pyberman')
        #self.surface = pygame.display.set_mode((self.config['screen']['width'], self.config['screen']['height']), FULLSCREEN|DOUBLEBUF     |HWSURFACE)
        # use default resolution
        self.surface = pygame.display.set_mode((0,0), FULLSCREEN|DOUBLEBUF     |HWSURFACE)
        self.screen_height = pygame.display.Info().current_h
        self.screen_width = pygame.display.Info().current_w
        self.controller = None
        self.create_groups()
        self.players_available = 0
        self.available=[]
        self.players=[None]*10
        self.players_alive=2
        self.ground = pygame.image.load(os.path.join('Data','ground.jpg'))
        #: Whether the main loop should run
        self.done = False
        super(Game, self).__init__()

    def __del__(self):
        '''Deinitializes the game.'''
        pygame.quit ()

    def main_loop(self):
        '''Starts the game's main loop.'''
        #to control a framerate
        clock = pygame.time.Clock()
        MainMenu(self)
        self.menu_sound.play()
        while not self.done:
            for event in pygame.event.get():
                events.Event.process_event(events.event_from_pygame_event(self, event)) 
            self.update()
            self.redraw()  
            pygame.display.flip()
            if self.players_alive<2:
                self.event_quit(event)
            #Let other processes to work a bit, limiting the framerate
            clock.tick(self.config['general']['framerate'])
        
    def event_keydown(self, event):
        if event.key==K_ESCAPE:
            event.stop_propagating = True
            events.Event.process_event(events.QuitEvent(self))

    def event_quit(self, event):
        '''Finish the main loop'''
        self.done = True

    def load_level(self, filename, num):
        '''Loads the chosen map for a needed amount of players'''
        self.players_alive=num
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
                        Wall(self, col_num, row_num, groups=(self.all, self.obstacles, self.walls))
                    elif col == 'B':
                        Box(self, col_num, row_num, groups=(self.all, self.dynamic, self.obstacles, self.destroyable))
                    elif col == ' ': 
                        pass
                    elif col=='S':
                        if self.players_available<num:
                            self.available.append((col_num,row_num))
                        self.players_available+=1
                    else:
                        raise RuntimeError('Unknown symbol "%s" in row %d, col %d'%(col, row_num+1, col_num+1))
                if col_num<self.width-1:
                    raise RuntimeError('Insuficient number of colums in row %d'%row_num+1)
            if row_num<self.height-1:
                raise RuntimeError('Insuficient number of rows')
        #Random generating of places where players may appear
        for x in range(num):
            while self.players[x] is None:
                y=random.choice(self.available)
                self.available.remove(y)
                self.players[x]=Player(self, y[0], y[1], x, groups=(self.all, self.dynamic, self.destroyable, self.gamers))
        self.controller = controller.LocalController(self.players[0],self.players[1])
        
    def xcoord_to_screen(self, x):
        '''Translates given x coordinate from the game coord system to screen coord system.'''
        return self._absw+x*self.side

    def ycoord_to_screen(self, y):
        '''Translates given y coordinate from the game coord system to screen coord system.'''
        return self._absh+y*self.side

    def create_groups(self):
        '''Creates sprite groups needed for the game'''
        self.all = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.dynamic = pygame.sprite.Group() 
        self.bombs = pygame.sprite.Group()
        self.gamers = pygame.sprite.Group()
        self.destroyable = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.bonuses = pygame.sprite.Group()
        
    def redraw(self):
        '''Redraws the level. It is called each core pumb'''
        #self.surface.blit(self.ground, (0,0))
        self.surface.fill((0,0,0))
        self.all.draw(self.surface)

    def update(self):
        '''Updates all the objects on the level'''
        self.all.update()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance=Game()
        return cls._instance

if __name__=="__main__":
    Game.instance().main_loop()
