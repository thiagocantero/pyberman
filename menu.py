import pygame

class TextBox(pygame.sprite.Sprite):
    def __init__(self, text, x, y, width, height, groups=None):
        self.text_size = height
        self.text_font = pygame.font.Font(None, self.text_size)
        super(TextBox, self).__init__(*(groups if groups is not None else []))
        self.rect=pygame.rect.Rect(x,y,width,height)
        self.image = self.text_font.render(text, True, (23,100,255))
        
        
class Menu(pygame.sprite.Sprite):
    call={}
    image=pygame.image.load('Data\\menu.jpg')
    def __init__(self, h, w, groups=None):
        self.text_size = 72
        self.res_h = h
        self.res_w = w
        self.create_groups()
        self.load_menu(Menu.call)
        
    def create_groups(self):
        self.menu_all = pygame.sprite.RenderUpdates()
        
    def draw(self, surface):
        """Redraws the menu"""
        self.menu_all.draw(surface)

    def update(self):
        self.menu_all.update()
        
    def load_menu(self, names):
        absh=(self.res_h - (self.text_size*len(names)))//2
        absw=self.res_w//2
        for number,name in enumerate(names.keys()):
            TextBox(name, absw, absh+self.text_size*number, absw, self.text_size, groups=self.menu_all)

class MainMenu(Menu):
    call={'Start Local Game':'','Start Network Game':'','Quit':''}
    def __init__(self, h, w, groups=None):
        super().__init__(h, w, groups) 