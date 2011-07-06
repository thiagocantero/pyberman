#GameObjects.py
#Copyright (C) 2011 PyTeam

"""Game objects."""

import os
import pygame

IMAGE_DIR = "Data"


class GameObject(pygame.sprite.Sprite):
    """The base class for all visible entities in the game, which implements generic operations.
    See the base class documentation at http://pygame.org/docs/ref/sprite.html#pygame.sprite
    """
    #: list of file names of images to load
    image_files=[]

    def __init__(self, game, x, y, groups=None):
        self.game = game
        self.x, self.y = x,y
        super(GameObject, self).__init__(*(groups if groups is not None else []))
        self.images=[]
        if self.image_files:
            for f in self.image_files:
                self.images.append(self.load_image(f))
        if self.images:
            self.image = self.images[0]
    
    def update(self):
        """Updates the object's state.
        It is called on each core frame."""
        if self.image is not None:
            self.rect = pygame.rect.Rect(self.screen_x, self.screen_y, self.width, self.height)

    @property
    def width(self):
        return self.game.side

    @property
    def height(self):
        return self.game.side
    
    def load_image(self, file_name):
        return pygame.transform.smoothscale(pygame.image.load(os.path.join(IMAGE_DIR, file_name)), (self.width, self.height))

    @property
    def screen_x(self):
        return self.game.xcoord_to_screen(self.x)

    @property
    def screen_y(self):
        return self.game.ycoord_to_screen(self.y)

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
        player.speed+=1

        
class AddBombBonus(Bonus):
    image_files=['1.jpg']

    def affect_player(self, player):
        player.bombs += 1

        
class MoveBombsBonus(Bonus) :
    image_files=['2.jpg']

    def affect_player(self, player):
        player.can_move_bombs = True


class IncreaseRadiusBonus(Bonus):
    image_files=['2.jpg']

    def affect_player(self, player):
        player.radius += 1

        
class BadBonus(Bonus):
    image_files=['2.jpg']
    def affect_player(self, player):
        # here timer is
        pass

        
class SpeedDownBonus(BadBonus):
    
    def affect_player(self, player):
        speed_temp = player.speed
        player.speed = 3
        #Lex: WTF??? calling a constructor when object is already created?
        #Zmolodchenko: this is win!
        super().__init__(self, player) # timer here?
        player.speed = speed_temp

        
class ReduceRadiusBonus(BadBonus):

    def affect_player(self, player):
        radius_temp = player.radius
        player.radius = 3
        #and yet another win
        super().__init__(self, player) 
        player.radius = radius_temp

        
class Bomb(GameObject):

    def collide_Player(self, player):
        #Lex: what is it supposed to do?
        if player.can_move_bombs:pass

        
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
    def __init__(self, game, x, y, id, *args, **kwargs):
        self.id = id
        self.bombs = 1
        self.speed=5
        self.radius=1
        self.can_move_bombs=False
        super(Player, self).__init__(game, x,y, *args, **kwargs)
        self.image = self.load_image(Player.player_images[id])
