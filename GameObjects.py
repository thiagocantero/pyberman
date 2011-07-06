#GameObjects.py
#Copyright (C) 2011 PyTeam

"""Module which contains main classes such as Bonus, Wall, Box, Player and level
Loads necessary images from Data folder
Version 1.0

Needs:
- rewrite all paths from absolute to relative
- add all bonuses
- add bomb class
- add functionality to player
"""

import os
import pygame

IMAGE_DIR = "Data"


class GameObject(pygame.sprite.Sprite):
    """The base class for all visible entities in the game, which implements generic operations.
    See the base class documentation at http://pygame.org/docs/ref/sprite.html#pygame.sprite
    """
    #: list of file names of images to load
    image_files=[]

    def __init__(self, level, y,x, groups=None):
        self.level = level
        self.x, self.y = x,y
        super(GameObject, self).__init__(*(groups if groups is not None else []))
        self.images=[]
        if self.image_files:
            for f in self.image_files:
                self.images.append(GameObject.load_image(f))
        if self.images:
            self.image = pygame.transform.smoothscale(self.images[0],(self.side,self.side))

    def update(self):
        """Updates the object's state.
        It is called on each core frame."""
        if self.image is not None:
            self.rect = pygame.rect.Rect(self.screen_x, self.screen_y,self.side,self.side)

    @staticmethod
    def load_image(file_name):
        return pygame.image.load(os.path.join(IMAGE_DIR, file_name))

    @property
    def screen_x(self):
        return self.level.xcoord_to_screen(self.x)

    @property
    def screen_y(self):
        return self.level.ycoord_to_screen(self.y)

    @property
    def side(self):
        return self.level.side


    def collide(self, other):
        """By default, it searches a method named 'collide_otherclassname' and calls it if exist.
        for example, if object implements method named 'collide_Player', it would be called when player collides with this object.
        @returns: whether the movement can be continued
        @rtype: bool
        """
        func = getattr(self, 'collide_%s'%other.__class__.__name__, None)
        if func is not None:
            return func(other)  


class Bonus(GameObject):
    """Represents an item which affects the player on collision and then disappears."""

    def collide_Player(self, player):
        self.affect_player(player)
        self.kill()
        return True #Player can move further

    def affect_player(self, player):
        """Makes something fun with player.
        Should be overloaded in derived classes."""
        pass

class SpeedupBonus(Bonus):
    """Speeds the player up by a factor."""
    image_files=['1.jpg']

    def affect_player(self, player):
        player.speedup()

class AddBombBonus(Bonus):
    image_files=['1.jpg']

    def affect_player(self, player):
        player.bombs += 1

class MoveBombsBonus(Bonus) :
    image_files=['2.jpg']

    def affect_player(self, player):
        player.canmovebombs = True

class IncsreaseRadiusBonus(Bonus):
    image_files=['2.jpg']

    def affect_player(self, player):
        player.radius += 1

class BadBonus(Bonus):
    image_files=['2.jpg']
    def affect_player(self, player):
        # here timer is
        pass

class SpeedDown(BadBonus):
    
    def affect_player(self, player):
        speed_temp = player.speed
        player.speed = 3
        super().__init__(self, player) # timer here?
        player.speed = speed_temp

class ReduceRadius(BadBonus):

    def affect_player(self, player):
        radius_temp = player.radius
        player.radius = 3
        super().__init__(self, player) 
        player.radius = radius_temp

class Bomb(GameObject):

    def collide_Player(self, player):
        if player.canmovebombs:pass
        
class Wall(GameObject):
    """An obstacle which player can not get through."""
    image_files = ['wall.jpg']

    def collide_Player(self, player):
        return False #player can not move further


class Box(Wall):
    """An obstacle which can be ruined by a bomb explosion."""
    image_files = ['box.jpg']

    def collide_BombExplosion(self):
        self.kill()
        return True


class Player(GameObject):
    """Represents a player in the game."""
    player_images = ['1.jpg', '2.jpg', '3.jpg']
    def __init__(self, level, x, y, id, *args, **kwargs):
        self.id = id
        self.bombs = 1
        self.speed=5
        self.radius=1
        self.canmovebombs=False
        super(Player, self).__init__(level, x,y, *args, **kwargs)
        self.image = GameObject.load_image(Player.player_images[id])

class Level(object):
    """Manages a game level.
    It is responsilbe for loading and updating the level."""

    def __init__(self, filename, h, w):
        self.create_groups()
        self.res_h,self.res_w=h,w
        self.load_level(filename)
#        self.background = pygame.Surface(game.surface.get_size()).convert()
#        self.background.fill((100, 100, 100))
#        game.surface.blit(self.background, self.background.get_rect())
#        pygame.display.flip()

    def load_level(self, filename):
        with open(filename) as f:
            self.height,self.width,self.max_players = [int(x) for x in f.readline().split()]
            self.side=min([self.res_h//self.height,self.res_w//self.width])
            self._absw = (self.res_w-(self.width*self.side))//2
            self._absh = (self.res_h-(self.height*self.side))//2
            for row_num, row in enumerate(f):
                if row_num == self.height: raise RuntimeError('Too many lines in the file')
                for col_num, col in enumerate(row.strip()):
                    if col_num == self.width: raise RuntimeError('Too many colums in row %d'%row_num+1)
                    if col == 'W':
                        Wall(self, row_num, col_num, groups=(self.all, self.obstacles))
                    elif col == 'B':
                        Box(self, row_num, col_num, groups=(self.all, self.dynamic, self.obstacles))
                    elif col == ' ': 
                        pass
                    elif col.isdigit() and int(col)<10:
                        Player(self, row_num, col_num, int(col)-1, groups=(self.all, self.dynamic))
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

    def draw(self, surface):
        """Redraws the level. It is called each core pumb"""
        self.all.draw(surface)

    def update(self):
        self.all.update()
