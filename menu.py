import pygame
from gameobjects import GameObject 

     
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
        super(Menu, self).__init__(game, 0, 0, groups=[game.all])
        self.background = self.load_image('menu.jpg')
        self.image=pygame.Surface((self.width,self.height))
        self.text_font = pygame.font.Font(None, self.text_size)
        self.rendered_title=self.text_font.render(self.title, True, (255,0,0))
        self.rect = pygame.rect.Rect(0, 0, self.width, self.height)
        #abs_height is computed in the way that all items of menu would be centralized
        self.abs_height=(self.height-len(self.str_func)*self.text_size)//2
        self.current=1
        
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
    

class MainMenu(Menu):
    items=(('Start Local Game', None), ('Start Network Game', None), ('Join Network Game', None), ('Credits', None), ('Quit', None))
    def __init__(self, game):
        super(MainMenu, self).__init__(game, MainMenu.items, 'Main Menu') 
