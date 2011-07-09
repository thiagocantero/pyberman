#controller.py
#Copyright (C) 2011 PyTeam

"""Contains the LocalController class."""

import pygame
from pygame.locals import *
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
        events.AutoListeningObject.__init__(self)
        
    def event_keydown(self, event):
        '''Manages to use the key down until it is released'''
        func = self.actions.get(event.key, None)
        if func is not None:
            func()
            event.stop_propagating = True
        
    def event_keyup(self, event):
        '''Release of currect key'''
        if event.key in [K_UP,K_DOWN,K_LEFT,K_RIGHT]: 
            self.player1.dest = None
            self.player1.move_up_to()
        elif event.key in [K_w,K_a,K_s,K_d]: 
            self.player2.dest = None
            self.player2.move_up_to()
        else: event.stop_propagating = True
        
        
        