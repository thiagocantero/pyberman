#controllers.py
#Copyright (C) 2011 PyTeam

"""Player controllers which dispatch physical events to players."""

import time
import pygame
from pygame.locals import *
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from PodSixNet.Connection import connection, ConnectionListener
import events
import gameobjects

class LocalController(events.AutoListeningObject):
    '''Class which catches the events from the keyboard and resents these events to players of local game'''

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.actions={
            K_UP:self.player1.go_up,
            K_DOWN:self.player1.go_down,
            K_LEFT:self.player1.go_left,
            K_RIGHT: self.player1.go_right,
            K_SPACE: self.player1.put_bomb,
            K_w:self.player2.go_up,
            K_s:self.player2.go_down,
            K_a:self.player2.go_left,
            K_d: self.player2.go_right,
            K_LCTRL:self.player2.put_bomb
        }
        super(LocalController, self).__init__()
    
    def event_keydown(self, event):
        '''Manages to use the key down until it is released'''
        func = self.actions.get(event.key, None)
        if func is not None:
            func()

    def event_keyup(self, event):
        '''Release of currect key'''
        if event.key in [K_UP,K_DOWN,K_LEFT,K_RIGHT]: 
            self.player1.stop()
        elif event.key in [K_w,K_a,K_s,K_d]: 
            self.player2.stop()



class NetworkController(events.AutoListeningObject):
    '''Class which catches the events from the keyboard and resents these events to players of network game'''

    def __init__(self, player):
        self.player = player
        self.actions={
            K_UP:self.player.go_up,
            K_DOWN:self.player.go_down,
            K_LEFT:self.player.go_left,
            K_RIGHT: self.player.go_right,
            K_SPACE: self.player.put_bomb,
        }
        super(NetworkController, self).__init__()

    def event_keydown(self, event):
        '''Manages to use the key down until it is released'''
        func = self.actions.get(event.key, None)
        if func is not None:
            func()

    def event_keyup(self, event):
        '''Release of currect key'''
        if event.key in [K_UP,K_DOWN,K_LEFT,K_RIGHT]: 
            self.player1.stop()


class ClientChannel(Channel):
    def Network(data):
        self._server.SendToAll(data)

    def Close(self):
        self._server.send_to_all({'action': 'kill', 'player': self.player_id})

class GameServer(Server):
    channelClass = ClientChannel

    def __init__(self, game, *args, **kwargs):
        self.game = game
        Server.__init__(self, *args, **kwargs)
        self.game_started = False
        self._max_player_id = 0

    def Connected(self, channel, addr):
        if self.game_started:
            channel.close_when_done()
            return 
        channel.player_id = self._max_player_id
        self._max_player_id+=1
        self.game.active_players.append("%d: from %s"%(channel.player_id+1, addr))

    def send_to_all(self, data):
        for channel in self.channels:
            channel.send(data)

    def start_game(self, level):
        for player in self.channels:
            player.sent({'action': 'start_game', 'level': level, 'player_id': player.player_id, 'num_players': self._max_player_id, 'random_seed': int(time.time())})
        self.game_started = True

