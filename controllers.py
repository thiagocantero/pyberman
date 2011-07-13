#controllers.py
#Copyright (C) 2011 PyTeam

"""Player controllers which dispatch physical events to players."""

import pygame
from pygame.locals import *
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from PodSixNet.Connection import connection, ConnectionListener
import events
import gameobjects

class PlayerController(events.AutoListeningObject):
    """Controlles one player."""
    def __init__(self, game, player, movement_map, put_bomb_key):
        """Initializes a player controller.
        @param movement_map: a dictionary which maps key codes to appropriate player movement functions (such as player.move_left, player.move_right etc)
        @type movement_map: dict
        """
        self.game = game
        self.player = player
        super(PlayerController, self).__init__()
        self.movement_map = movement_map
        self.put_bomb_key = put_bomb_key
        self.movement_time = 0
        self.cur_move = None

    def event_keydown(self, event):
        if event.key == self.put_bomb_key:
            self.put_bomb()
        elif event.key in self.movement_map:
            self.movement_map[event.key](self.player)
            #self.move_player(self.movement_map[event.key])

    def event_keyup(self,event):
            if event.key in self.movement_map:
                self.player.stop()
            #self.cur_move = None # we do not move anymore

    def put_bomb(self):
            self.player.put_bomb()

    #def move_player(self, m):
    #     if self.player.can_move: # player can not move when it is already moving, e.g. in the process of a step
    #        self.cur_move = m
    #        self.movement_time = self.player.step_time #the duration of player step

    def update(self):
        self.player.step()
    #    if self.cur_move is not None:
    #        #we are moving somewhere...
    #        self.movement_time-=delta
    #        if self.movement_time<=0:
    #            self.cur_move() #call an appropriate function on a player to perform next step
    #            self.movement_time = self.player.step_time


class LocalController(events.AutoListeningObject):
    '''Class which catches the events from the keyboard and resents these events to players of local game'''

    def __init__(self, game, player1, player2):
        self.game=game
        self.first_player_map={
            K_UP:gameobjects.Player.go_up,
            K_DOWN:gameobjects.Player.go_down,
            K_LEFT:gameobjects.Player.go_left,
            K_RIGHT:gameobjects.Player.go_right
            }
        self.second_player_map={    
            K_w:gameobjects.Player.go_up,
            K_s:gameobjects.Player.go_down,
            K_a:gameobjects.Player.go_left,
            K_d:gameobjects.Player.go_right
        }
        self.player1 = player1
        self.player2 = player2
        self.player_controller_1=PlayerController(self.game, self.player1, self.first_player_map, K_SPACE)
        self.player_controller_2=PlayerController(self.game, self.player2, self.second_player_map, K_LCTRL)
        super(LocalController, self).__init__()
    
    #def event_keydown(self, event):
    #    '''Manages to use the key down until it is released'''
    #    func = self.actions.get(event.key, None)
    #    if func is not None:
    #        func()

    #def event_keyup(self, event):
    #    '''Release of currect key'''
    #    if event.key in [K_UP,K_DOWN,K_LEFT,K_RIGHT]: 
    #        self.player1.stop()
    #    elif event.key in [K_w,K_a,K_s,K_d]: 
    #        self.player2.stop()


class ClientChannel(Channel):
    def Network(data):
        self._server.SendToAll(data)

    def Close(self):
        self._server.send_to_all({'action': 'kill', 'player': self.player_id})

class GameServer(Server):
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.game_started = False
        self._max_player_id = 0

    def Connected(self, channel, addr):
        if self.game_started:
            channel.close_when_done()
            return 
        channel.player_id = self._max_player_id
        self._max_player_id+=1
        print ("connected client %d from %s"%(channel.player_id, addr))

    def send_to_all(self, data):
        for channel in self.channels:
            channel.send(data)

    def start_game(self, level):
        for player in self.channels:
            player.sent({'action': 'load_level', 'data': level, 'player_id': player.player_id})
        self.game_started = True


class NetworkController(events.AutoListeningObject, ConnectionListener):

    def __init__(self, game, local_player_id):
        self.game = game
        self.local_player_id = local_player_id
        super(NetworkController, self).__init__()
        self.actions={
            K_UP: 'go_up',
            K_DOWN: 'go_down',
            K_LEFT: 'go_left',
            K_RIGHT: 'go_right',
            K_SPACE: 'put_bomb',
        }

    def Network_player(self, data):
        getattr(self.game.players[data['player_id']], data['func'])()

    def event_keydown(self, event):
        func = self.actions.get(event.key, None)
        if func is not None:
            self.send({'action': 'player', 'func': func, 'player_id': self.local_player_id})
