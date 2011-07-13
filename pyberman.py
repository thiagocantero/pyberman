#pyberman.py
#Copyright (C) 2011 PyTeam

'''The Pyberman runner.
'''

import os
import sys
from cStringIO import StringIO
import random
import pygame
from pygame.locals import *
from PodSixNet.Connection import connection, ConnectionListener
from gameobjects import *
from ui import MainMenu, Score
import events
import controllers


class Game(events.AutoListeningObject, ConnectionListener):
    '''Represents a high-level game instance.
    Should be a singleton.
    '''
    _instance = None
    #Todo: implement reading from a config file
    config = {'general':
             {'framerate': 50},
             'server': {'port': 8000}}

    def __init__(self):
        '''Initializes the game.'''
        pygame.init()
        pygame.mixer.init()
        self.menu_sound = pygame.mixer.Sound(os.path.join('Data', 'Pandemonium.ogg'))
        self.explosions = [
            pygame.mixer.Sound(os.path.join('Data', 'explosion.ogg')),
            pygame.mixer.Sound(os.path.join('Data', 'explosion2.ogg')),
            pygame.mixer.Sound(os.path.join('Data', 'explosion3.ogg'))
        ]
        pygame.display.set_caption('Pyberman')
        #self.surface = pygame.display.set_mode((self.config['screen']['width'], self.config['screen']['height']), FULLSCREEN|DOUBLEBUF     |HWSURFACE)
        # use default resolution
        self.surface = pygame.display.set_mode((0,0), FULLSCREEN|DOUBLEBUF     |HWSURFACE)
        self.screen_height = pygame.display.Info().current_h
        self.screen_width = pygame.display.Info().current_w
        self.step_length=0.25
        self.controller = None
        self.create_groups()
        self.player_names=['Player %s'%num for num in range(10)]
        self.players_colors=[(148,0,211),(255,255,0),(255,0,0),(0,255,0),(0,250,154),(0,0,238),(255,20,147),(255,140,0)]
        #: Whether the main loop should run
        self.done = False
        self.is_network_game = self.is_server = False
        super(Game, self).__init__()

    def __del__(self):
        '''Deinitializes the game.'''
        pygame.quit ()

    def main_loop(self):
        '''Starts the game's main loop.'''
        #to control a framerate
        clock = pygame.time.Clock()
        MainMenu(self)
        self.menu_sound.play(loops=100)
        while not self.done:
            for event in pygame.event.get():
                events.Event.process_event(events.event_from_pygame_event(self, event)) 
            self.delta=clock.get_time()/1000.0
            self.update()
            self.redraw()  
            pygame.display.flip()
            #Let other processes to work a bit, limiting the framerate
            clock.tick(self.config['general']['framerate'])

    def event_keydown(self, event):
        if event.key==K_ESCAPE:
            event.stop_propagating = True
            self.create_groups()
            MainMenu(self)
            #events.Event.process_event(events.QuitEvent(self))

    def event_quit(self, event):
        '''Finish the main loop'''
        self.done = True

    def load_level(self, f):
        '''Loads the chosen map for a needed amount of players'''
        self.available=[]
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
                        self.available.append((col_num,row_num))
                else:
                    raise RuntimeError('Unknown symbol "%s" in row %d, col %d'%(col, row_num+1, col_num+1))
            if col_num<self.width-1:
                raise RuntimeError('Insuficient number of colums in row %d'%row_num+1)
        if row_num<self.height-1:
            raise RuntimeError('Insuficient number of rows')
        random.shuffle(self.available)
        self.players = []
        for i in range(self.num_players):
            self.players.append(Player(self, self.available[i][0], self.available[i][1], i, groups=(self.all, self.destroyable)))

    def start_local_game(self, level):
        self.num_players = 2
        self.load_level(open(level))
        self.controller = controllers.LocalController(*self.players)
        self.players_alive = 2

    def end_game(self):
        if self.is_network_game:
            connection.Close()
        for obj in self.all:
            obj.unregister_all_event_handlers()
        self.create_groups()
        Score(self)

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
        self.destroyable = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.bonuses = pygame.sprite.Group()

    def Network_start_game(self, data):
    	self._waitbox.kill()
    	del self._waitbox
        self.is_network_game = True
        random.seed(data['random_seed'])
        self.player_id = data['player_id']
        self.num_players = data['num_players']
        self.load_level(StringIO(data['level']))
        self.controller = controllers.NetworkController(self.players[self.player_id])
        self.players_alive = self.num_players

    def redraw(self):
        """Redraws the level. It is called each core pumb"""
        #self.surface.blit(self.ground, (0,0))
        self.surface.fill((0,0,0))
        self.all.draw(self.surface)

    def update(self):
        '''Updates all the objects on the level'''
        self.all.update()
        if self.is_network_game:
            connection.Pump()
            self.Pump()
            if self.is_server:
                self.server.Pump()

    def start_server(self):
        self.active_players = [] # for displaying in the network menu
        self.server = controllers.GameServer(self, localaddr=('0.0.0.0', self.config['server']['port']))
        self.is_network_game = True
        self.is_server = True
        self.Connect(('localhost', self.config['server']['port']))

    def Network_error(self, data):
        ErrorMenu(self, data['error'][1])
        connection.Close()

    def Network_disconnected(self, data):
        ErrorMenu(self, data)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance=Game()
        return cls._instance

if __name__=="__main__":
    #sys.stderr = open('stderr.txt', 'w')
    Game.instance().main_loop()
