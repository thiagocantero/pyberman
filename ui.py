import sys
import pygame
from pygame.locals import *
import glob
import os
from gameobjects import GameObject 
import events

class Menu(GameObject):
    '''Shows the list of text items on the screen allowing to choose any from mouse or keyboard 
        It's a class which is responsible for creating GameObject called Menu, which will
        be showed on the screen in the main loop
    '''
    def __init__(self, game, str_func, title):
        '''
        @param str_func: list of tuples(str,func), where str is displayed name, func is callable function
        @type str_func:list
        @param title: title of the current menu
        @type title:str
        '''
        self.str_func=str_func
        self.title  = title
        self.text_size = 50
        self.menu_length=len(self.str_func)
        super(Menu, self).__init__(game, 0, 0, groups=[game.all])
        self.background = self.load_image('menu.jpg')
        self.image=pygame.Surface((self.width,self.height))
        self.text_font = pygame.font.Font(None, self.text_size)
        self.rendered_title=self.text_font.render(self.title, True, (255,0,0))
        self.rect = pygame.rect.Rect(0, 0, self.width, self.height)
        #abs_height is computed in the way that all items of menu would be centralized
        self.abs_height=(self.height-self.menu_length*self.text_size)//2
        self.current=0

    @property
    def width(self):
        return self.game.screen_width
    
    @property
    def height(self):
        return self.game.screen_height
        
    def update(self):
        self.image.blit(self.background,(0,0))
        self.image.blit(self.rendered_title,((self.width-self.rendered_title.get_width())//2,self.text_size))
        for number,(text,func) in enumerate(self.str_func):
            if number==self.current: self.image.blit(self.text_font.render(text, True, (0,255,0)),(self.width//2,self.abs_height+number*self.text_size))
            else: self.image.blit(self.text_font.render(text, True, (0,0,255)),(self.width//2,self.abs_height+number*self.text_size))
    
    def event_keydown(self,event):
        if event.key==K_DOWN:
            self.game.menu_click.play()
            self.current=(self.current+1)%self.menu_length
        elif event.key==K_UP:
            self.game.menu_click.play()
            self.current=(self.current-1)%self.menu_length
        elif event.key==K_RETURN: self.str_func[self.current][1]()
            

class MainMenu(Menu):
    '''This menu is shown on a game startup'''
    def __init__(self, game):
        self.items=(
            ('Start Local Game', self.start_local_game), 
            ('Start Network Game', None), 
            ('Join Network Game', None), 
            ('Credits', None), 
            ('Quit', self.quit)
        )
        super(MainMenu, self).__init__(game, self.items, 'Main Menu') 

    def start_local_game(self):
        self.kill()
        ChooseLevelMenu(self.game, 2)

    def quit(self):
        events.Event.process_event(events.QuitEvent(self))


class ChooseLevelMenu(Menu):
    '''This menu is shown on a game startup'''
    def __init__(self, game, players):
        self.list_of_good_maps=[]
        self.file_names = []
        self.game = game
        self.players = players
        for filename in glob.glob(os.path.join('Maps', '*.bff')):
            if int(open(filename).readline().split()[2])>=players:
                self.list_of_good_maps.append((os.path.split(filename)[1].split('.')[0].capitalize(), self.load_level))
                self.file_names.append(filename)
        self.list_of_good_maps.append(['Back', self.back])
        super(ChooseLevelMenu, self).__init__(game, self.list_of_good_maps, 'Choose Map') 

    def back(self):
        self.kill()
        MainMenu(self.game)
        
    def load_level(self):
        self.kill()
        self.game.load_level(self.file_names[self.current], self.players)
