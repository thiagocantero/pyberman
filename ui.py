import glob
import os
import socket
import sys
import pygame
from pygame.locals import *
from PodSixNet.Connection import connection, ConnectionListener
from gameobjects import GameObject 
import events

class TextBox(GameObject):
    '''Basic class, which shows text lines and a title on a game screen'''
    def __init__(self, game, title, strings):
        self.strings=strings
        self.title  = title
        self.text_size = 50
        self.game = game # Magic! don't touch
        self.rect = pygame.rect.Rect(0, 0, self.width, self.height)
        super(TextBox, self).__init__(game, 0, 0, groups=[game.all])
        self.background = self.load_image('menu.jpg')
        self.image=pygame.Surface((self.width,self.height))
        self.text_font = pygame.font.Font(os.path.join('Data', 'freesansbold.ttf'), self.text_size)
        self.rendered_title=self.text_font.render(self.title, True, (255,0,0))

    @property
    def width(self):
        return self.game.screen_width
    
    @property
    def height(self):
        return self.game.screen_height
        
    @property
    def lines_count(self):
        return len(self.strings)
    
    @property
    def abs_height(self):
        return (self.height-(self.lines_count)*self.text_size)//2
        
    def update(self):
        pass


class Menu(TextBox):
    '''Shows the list of text items on the screen allowing to choose any from mouse or keyboard 
        It's a class which is responsible for creating GameObject called Menu, which will
        be showed on the screen in the main loop
    '''
    def __init__(self, game, str_func, title, strings=None):
        '''@param str_func: list of tuples(str,func), where str is displayed name, func is callable function   @type str_func:list
           @param title: title of the current menu                                                             @type title:str     '''
        self.str_func=str_func
        self.menu_length=len(str_func)
        super(Menu, self).__init__(game, title, strings if strings is not None else [])
        self.current=0
        self.menu_click = pygame.mixer.Sound(os.path.join('Data', 'click.ogg'))

    @property
    def lines_count(self):
        return super(Menu,self).lines_count+self.menu_length
    
    def update(self):
        self.image.blit(self.background,(0,0))
        self.image.blit(self.rendered_title,((self.width-self.rendered_title.get_width())//2,self.text_size))
        
        for number,text in enumerate(self.strings):
            self.image.blit(self.text_font.render(text, True, (0,128,255)),(self.width//2,self.abs_height+number*self.text_size))
        
        for number,(text,func) in enumerate(self.str_func):
            if number==self.current: self.image.blit(self.text_font.render(text, True, (0,255,0)),(self.width//2,self.abs_height+(super(Menu,self).lines_count+number)*self.text_size))
            else: self.image.blit(self.text_font.render(text, True, (0,154,205)),(self.width//2,self.abs_height+(super(Menu,self).lines_count+number)*self.text_size))
    
    def event_keydown(self,event):
        if event.key==K_DOWN:
            self.menu_click.play()
            self.current=(self.current+1)%self.menu_length
        elif event.key==K_UP:
            self.menu_click.play()
            self.current=(self.current-1)%self.menu_length
        elif event.key==K_RETURN: self.str_func[self.current][1]()
        
    def event_mousemotion(self, event):
        for line in range(self.menu_length):
            if (pygame.mouse.get_pos()[0] in range(self.width//2, self.width//2 + len(self.str_func[line][0]) * self.text_size + 1) and pygame.mouse.get_pos()[1] in range(self.abs_height+(super(Menu,self).lines_count+line) * self.text_size, self.abs_height+(super(Menu,self).lines_count+line) * self.text_size + self.text_size + 1)):
                self.menu_click.play()
                self.current = line
                return True
        return False
                
    
    def event_mousebuttondown(self, event):
        if self.event_mousemotion(event) == True: 
            self.str_func[self.current][1]()

class MainMenu(Menu):
    '''This menu is shown on a game startup'''
    def __init__(self, game):
        self.game=game
        self.items=(
            ('Start Local Game', self.start_local_game), 
            ('Start Network Game', self.start_network_game), 
            ('Join Network Game', self.join_network_game),
            ('Settings', self.settings),
            ('Credits', self.credits), 
            ('Quit', self.quit)
        )
        game.players_score=[0]*10
        super(MainMenu, self).__init__(game, self.items, 'Main Menu') 

    def start_local_game(self):
        self.kill()
        ChooseLevelMenu(self.game, 2)

    def start_network_game(self):
        self.kill()
        self.game.start_server()
        NetworkMenu(self.game)

    def join_network_game(self):
        self.kill()
        EnterIPBox(self.game)

    def settings(self):
        self.kill()
        SettingsMenu(self.game)
    
    def quit(self):
        events.Event.process_event(events.QuitEvent(self))

    def credits(self):
        self.kill()
        CreditsMenu(self.game)
        

class ChooseLevelMenu(Menu):
    '''This menu is shown when it comes to choosing the level'''
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
        self.game.start_local_game(self.file_names[self.current])


class CreditsMenu(Menu):
    '''This menu is a credits menu'''
    def __init__(self, game):
        self.items=(
            ('Back', self.back),
        )
        super(CreditsMenu, self).__init__(game, self.items, 'Credits',['Done by:','Oleksiy Sadoviy','Myroslava Stavnycha','Zakhar Gerych','Skrynnikova Anastasiya']) 

    def back(self):
        self.kill()
        MainMenu(self.game)
        

class SettingsMenu(Menu):
    '''This menu is a settings menu'''
    def __init__(self, game):
        self.items=(
            ('Player1', self.set_name0),
            ('Player2', self.set_name1),
            ('Music Settings',self.muz),
            ('Back', self.back),
        )
        super(SettingsMenu, self).__init__(game, self.items, 'Settings') 

    def back(self):
        self.kill()
        MainMenu(self.game)
    
    def muz(self):
        self.kill()
        MusicMenu(self.game)
        
    def set_name0(self):
        self.kill()
        ChoosePlayerName(self.game,0)

    def set_name1(self):
        self.kill()
        ChoosePlayerName(self.game,1)
        
        
        
class MusicMenu(Menu):
    '''This menu is a settings menu for musical settings'''
    def __init__(self, game):
        self.game=game
        self.vol=1.0
        self.items=(
            ('Volume+', self.vol_plus),
            ('Volume-', self.vol_minus),
            ('Back', self.back),
        )
        super(MusicMenu, self).__init__(game, self.items, 'Music Settings') 

    def back(self):
        self.kill()
        MainMenu(self.game)
    
    def vol_plus(self):
        if self.vol<1: self.vol+=0.1 
        self.game.menu_sound.set_volume(self.vol)
        
    def vol_minus(self):
        if self.vol>0: self.vol-=0.1
        self.game.menu_sound.set_volume(self.vol)
        
class Score(Menu):
    '''Shows score after the game''' 
    def __init__(self, game):
        self.game=game
        self.items=(
            ('Continue', self.start_local_game), 
            ('MainMenu', self.quit),
        )
        self.strings=[]
        for player in self.game.players:
            if player is not None:
                self.strings.append('%s        %s'%(self.game.player_names[player.id], self.game.players_score[player.id]))
        super(Score, self).__init__(self.game, self.items, 'Score', self.strings) 

    def update(self):
        self.image.blit(self.background,(0,0))
        self.image.blit(self.rendered_title,((self.width-self.rendered_title.get_width())//2,self.text_size))
        
        for number,text in enumerate(self.strings):
            self.image.blit(self.text_font.render(text, True, self.game.players_colors[number]),(self.width//2,self.abs_height+number*self.text_size))
        
        for number,(text,func) in enumerate(self.str_func):
            if number==self.current: self.image.blit(self.text_font.render(text, True, (0,255,0)),(self.width//2,self.abs_height+(super(Menu,self).lines_count+number)*self.text_size))
            else: self.image.blit(self.text_font.render(text, True, (0,154,205)),(self.width//2,self.abs_height+(super(Menu,self).lines_count+number)*self.text_size))
    
    
    def start_local_game(self):
        self.kill()
        ChooseLevelMenu(self.game, 2)

    def quit(self):
        self.kill()
        MainMenu(self.game)


class NetworkScore(Menu):
    '''Shows score after the game''' 
    def __init__(self, game):
        self.game=game
        self.items=(
            ('MainMenu', self.quit),
        )
        self.strings=[]
        for player in self.game.players:
            if player is not None:
                self.strings.append('%s        %s'%(self.game.player_names[player.id], self.game.players_score[player.id]))
        super(NetworkScore, self).__init__(self.game, self.items, 'Score', self.strings) 

    def update(self):
        self.image.blit(self.background,(0,0))
        self.image.blit(self.rendered_title,((self.width-self.rendered_title.get_width())//2,self.text_size))
        
        for number,text in enumerate(self.strings):
            self.image.blit(self.text_font.render(text, True, self.game.players_colors[number]),(self.width//2,self.abs_height+number*self.text_size))
        
        for number,(text,func) in enumerate(self.str_func):
            if number==self.current: self.image.blit(self.text_font.render(text, True, (0,255,0)),(self.width//2,self.abs_height+(super(Menu,self).lines_count+number)*self.text_size))
            else: self.image.blit(self.text_font.render(text, True, (0,154,205)),(self.width//2,self.abs_height+(super(Menu,self).lines_count+number)*self.text_size))
    
    def quit(self):
        self.kill()
        MainMenu(self.game)

        
class EditBox(TextBox):
    '''Shows the editbox, which can be used for the input of information 
    '''
    def __init__(self, game, inp , title, strings=None):
        '''@param inp: inp is parametr which we want to change    @type inp:str
           @param title: title of the current editbox             @type title:str     '''
        self.inp = inp
        super(EditBox, self).__init__(game, title, strings)
        self.cur_pos=len(inp)

    @property
    def lines_count(self):
        return super(EditBox,self).lines_count+1
    
    def update(self):
        self.image.blit(self.background,(0,0))
        self.image.blit(self.rendered_title,((self.width-self.rendered_title.get_width())//2,self.text_size))
        
        for number,text in enumerate(self.strings):
            self.image.blit(self.text_font.render(text, True, (0,128,255)),(self.width//2,self.abs_height+self.text_size))
        self.image.blit(self.text_font.render(self.inp, True, (255,0,0)),(self.width//2,self.abs_height+self.text_size*self.lines_count))
            
        
    def event_keydown(self,event):
        if event.key==K_LEFT:
            if self.cur_pos>0: self.cur_pos-=1
        elif event.key==K_RIGHT:
            if self.cur_pos<len(self.inp): self.cur_pos+=1
        elif event.key==K_HOME:
            self.cur_pos=0
        elif event.key==K_END:
            self.cur_pos=len(self.inp)
        elif event.key==K_RETURN: self.func()
        elif event.key==K_BACKSPACE: 
            if self.cur_pos>0: 
                self.inp = self.inp[:self.cur_pos-1]+self.inp[self.cur_pos:]
                self.cur_pos-=1
        elif event.key==K_DELETE: 
            if self.cur_pos<len(self.inp): 
                self.inp = self.inp[:self.cur_pos]+self.inp[self.cur_pos+1:]
        else:
            self.inp=self.inp[:self.cur_pos]+event.unicode+self.inp[self.cur_pos:]
            self.cur_pos+=1
        
class ChoosePlayerName(EditBox):
    '''This editbox is used to complete the information about players'''
    def __init__(self, game, id):
        self.id=id
        self.game = game
        super(ChoosePlayerName, self).__init__(game, self.game.player_names[id], 'Player Naming', ['Choose the name of the player'])

    def func(self):
        self.game.player_names[self.id]=self.inp
        self.kill()
        SettingsMenu(self.game)

class NetworkMenu(Menu):
    '''This menu is used for creating a network game'''
    def __init__(self, game):
        self.items=(
            ('Start Game', self.start_game), 
            ('Back', self.back)
        )
        self.game=game
        game.active_players.append("Your local IP: "+socket.gethostbyname(socket.gethostname()))
        super(NetworkMenu, self).__init__(game, self.items, 'Waiting for players...', self.game.active_players)

    def start_game(self):
        if self.game.server.num_players>1:
            self.kill()
            ChooseLevelNetworkMenu(self.game, self.game.server.num_players)

    def back(self):
        self.kill()
        MainMenu(self.game)

class EnterIPBox(EditBox):
    '''This editbox is used for joining the server'''
    def __init__(self, game):
        super(EnterIPBox, self).__init__(game, '192.168.1.1', 'Server IP', ['Enter server IP:'])

    def func(self):
        parts = self.inp.split('.')
        try:
            parts = map(int, parts)
        except ValueError:
            self.inp = 'Incorrect value!'
            return
        if not len(parts)==4 or not all(i<255 for i in parts):
            self.inp = 'Incorrect value!'
            return
        self.kill()
        self.game.inp=self.inp
        self.game.is_network_game = True
        self.game.Connect((self.inp, self.game.config['server']['port']))
        self.game._waitbox = WaitBox(self.game)


class ErrorMenu(Menu):
    '''This menu is shown if there are some problems with the connection'''
    def __init__(self, game, error):
        self.items = (
            ('Back', self.back),
        )
        super(ErrorMenu, self).__init__(game, self.items, 'Error', ['An error occured:', error])
    def back(self):
        self.kill()
        MainMenu(self.game)


class ChooseLevelNetworkMenu(ChooseLevelMenu):
    '''This menu allows to choose level for the network game'''
    def back(self):
        self.kill()
        NetworkMenu(self.game)

    def load_level(self):
        self.kill()
        self.game.server.start_game(open(self.file_names[self.current]).read())


class WaitBox(Menu):
    '''This Menu is shown while player is waiting for the network game start'''
    def __init__(self, game):
        self.items = (
            ('Back', self.back),
        )
        super(WaitBox, self).__init__(game, self.items, 'Waiting...', ['Wait until the game starts'])

    def back(self):
        self.kill()
        connection.Close()
        self.game.is_network_game = False
        MainMenu(self.game)
