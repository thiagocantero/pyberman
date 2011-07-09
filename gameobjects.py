#GameObjects.py
#Copyright (C) 2011 PyTeam

'''Game objects.'''

import os
import pygame
import events
import random

IMAGE_DIR = "Data"


class GameObject(pygame.sprite.Sprite, events.AutoListeningObject):
    '''The base class for all visible entities in the game, which implements generic operations.
    See the base class documentation at http://pygame.org/docs/ref/sprite.html#pygame.sprite
    '''
    #: list of file names of images to load
    image_files=[]

    def __init__(self, game, x, y, groups=None):
        self.game = game
        self.x, self.y = x,y
        super(GameObject, self).__init__(*(groups if groups is not None else []))
        #Sprite doesn't call super, so we have o do it manually in order for AUtoListeningObject gets initialized
        events.AutoListeningObject.__init__(self)
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
        return self.game.side-1

    @property
    def height(self):
        return self.game.side-1
    
    def load_image(self, file_name):
        return pygame.transform.smoothscale(pygame.image.load(os.path.join(IMAGE_DIR, file_name)), (self.width, self.height))

    @property
    def screen_x(self):
        return self.game.xcoord_to_screen(self.x)

    @property
    def screen_y(self):
        return self.game.ycoord_to_screen(self.y)

    def kill(self):
        super(GameObject, self).kill()
        self.unregister_all_event_handlers()
        
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
    '''Represents an item which affects the player on collision and then disappears.'''
    
    def __init__(self, game, x, y, groups=None):
        super(Bonus,self).__init__(game, x, y, groups)
        self.cur_ind = 0
    
    def collide_Player(self, player):
        self.affect_player(player)
        self.kill()
        return True #Player can move further

    def affect_player(self, player):
        """Makes something fun with player.
        Should be overloaded in derived classes."""
        pass

    def update(self):
        self.cur_ind = (self.cur_ind + 1) % len(self.image_files)
        self.image = self.load_image(self.image_files[self.cur_ind])
        super(Bonus,self).update()
        

class SpeedUpBonus(Bonus):
    '''Class representing bonus, increasing the player's speed by 0.05'''
    
    image_files=['bon_speed\\1.png','bon_speed\\2.png','bon_speed\\3.png','bon_speed\\4.png']

    def __init__(self,game,x,y,*args,**kwargs):
        super(SpeedUpBonus, self).__init__(game, x,y, *args, **kwargs)
        self.rect = pygame.rect.Rect(self.screen_x, self.screen_y, self.width, self.height)
        
    def affect_player(self, player):
        player.speed+=0.05

        
class AddBombBonus(Bonus):
    '''Class representing bonus, increasing the capacity of player's bombs by one'''
    
    image_files=['bon_add\\1.png','bon_add\\2.png','bon_add\\3.png','bon_add\\4.png']
    
    def __init__(self,game,x,y,*args,**kwargs):
        super(AddBombBonus, self).__init__(game, x,y, *args, **kwargs)
        self.rect = pygame.rect.Rect(self.screen_x, self.screen_y, self.width, self.height)
        
    def affect_player(self, player):
        player.bombs += 1

        
class MoveBombsBonus(Bonus) :
    '''Class representing bonus, allowing the player to move the bomb'''

    image_files=['bon_move\\1.png','bon_move\\2.png','bon_move\\3.png','bon_move\\4.png']
    #action of this class is still undone

    def __init__(self,game,x,y,*args,**kwargs):
        super(MoveBombsBonus, self).__init__(game, x,y, *args, **kwargs)
        self.rect = pygame.rect.Rect(self.screen_x, self.screen_y, self.width, self.height)
        
    def affect_player(self, player):
        player.can_move_bombs = True


class IncreaseRadiusBonus(Bonus):
    '''Class representing bonus, increasing the radius of a player by one'''

    image_files=['bon_inc\\1.png','bon_inc\\2.png','bon_inc\\3.png','bon_inc\\4.png']

    def __init__(self,game,x,y,*args,**kwargs):
        super(IncreaseRadiusBonus, self).__init__(game, x,y, *args, **kwargs)
        self.rect = pygame.rect.Rect(self.screen_x, self.screen_y, self.width, self.height)
        
    def affect_player(self, player):
        player.radius += 1

        
class BadBonus(Bonus):
    '''Class representing bad bonus, that have their period of impact over the player'''
    image_files=['bon_bad\\1.png','bon_bad\\2.png','bon_bad\\3.png','bon_bad\\4.png']
    def affect_player(self, player):
        # here timer is
        pass

        
class SpeedDownBonus(BadBonus):
    '''Class representing bad bonus, decreasing speed to minimum for a while'''
    def affect_player(self, player):
        speed_temp = player.speed
        player.speed = 0.05
        #timer needed
        player.speed = speed_temp

        
class ReduceRadiusBonus(BadBonus):
    '''Class representing bad bonus, reducing radius to minimum for a while'''
    
    def __init__(self,game,x,y,*args,**kwargs):
        super(ReduceRadiusBonus, self).__init__(game, x,y, *args, **kwargs)
        self.rect = pygame.rect.Rect(self.screen_x, self.screen_y, self.width, self.height)
        
    def affect_player(self, player):
        radius_temp = player.radius
        player.radius = 1
        self.time = 150
        #not done yet
        player.radius = radius_temp
        
    def update(self):
        self.time-=1
        if self.time==0:
            kill(self)
                    
        super(Bomb, self).update()
        
        

class ExchangePlacesBonus(BadBonus):
    '''Class representing bad bonus, when player changes place with random other player'''
    def __init__(self,game,x,y,*args,**kwargs):
        super(ExchangePlacesBonus, self).__init__(game, x,y, *args, **kwargs)
        self.rect = pygame.rect.Rect(self.screen_x, self.screen_y, self.width, self.height)
        
    def affect_player(self, player):
        tempx, tempy = player.x, player.y
        print self.game.players[:self.game.players_alive - 1]
        print self.game.players
        print self.game.available
        print 
        rand_player = random.choice(self.game.players[:self.game.players_alive ])
        while rand_player == player:  rand_player=random.choice(self.game.players[:self.game.players_alive])
        player.x = rand_player.x
        player.y = rand_player.y
        rand_player.x = tempx
        rand_player.y = tempy
        
class Bomb(GameObject):
    '''A class introducing Bomb, which can be put by player'''
    def __init__(self, player, game, x, y, *args, **kwargs):
        self.player, self.game, self.x, self.y =player, game, x, y
        self.time=80
        super(Bomb, self).__init__(game, x,y, *args, **kwargs)
        self.image = self.load_image('bomb.png')
        self.rect = pygame.rect.Rect(self.screen_x, self.screen_y, self.width, self.height)

    def collide_Player(self, player):
        #Lex: what is it supposed to do?
        if player.can_move_bombs:pass
    
    def explode(self):
        '''Makes current bomb explode and releases the fire'''
        self.kill()
        random.choice(self.game.explosions).play()
        self.player.bombs+=1
        for xx in range(int(round(self.x)),int(round(self.x)+self.player.radius+1)):
            if xx<self.game.width-1 and self.check(xx,round(self.y)): break
            
        for xx in range(int(round(self.x)-1),int(round(self.x)-self.player.radius-1),-1):
            if xx>0 and self.check(xx,round(self.y)): break

        for yy in range(int(round(self.y)+1),int(round(self.y)+self.player.radius+1)):
            if yy<self.game.height-1 and self.check(round(self.x),yy): break

        for yy in range(int(round(self.y)-1),int(round(self.y)-self.player.radius-1),-1):
            if yy>0 and self.check(round(self.x),yy): break
            
    def check(self,dx,dy):
        '''Checks if fire can move futher'''
        ret=False
        fire=Fire(self.game,self.player,dx,dy,groups=(self.game.all,self.game.dynamic))
        destroyed=pygame.sprite.spritecollide(fire,self.game.destroyable,True)
        if len(destroyed)!=0:
            for obj in destroyed:
                if isinstance(obj,Bomb):
                    obj.explode()
                elif isinstance(obj,Player):
                    self.game.players_alive-=1
                    self.player.kills+=1
                elif isinstance(obj,Box):
                    obj.collide_Fire()
            ret=True
        if len(pygame.sprite.spritecollide(fire,self.game.walls,False))>0: 
            fire.kill()
            ret=True
        return ret
            
    def update(self):
        self.time-=1
        if self.time < 12:  
            if self.time==0:
                self.explode()
            else: self.image = self.load_image('bomb\\%s.png'%str(self.time))
        super(Bomb, self).update()
    
class Fire(GameObject):
    '''The class representing the fire which appears straight after the bomb explosion'''
    def __init__(self, game, player, x, y, *args, **kwargs):
        self.player, self.game, self.x, self.y =player, game, x, y
        self.time = 3
        super(Fire, self).__init__(game, x,y, *args, **kwargs)
        self.image = self.load_image('fire.jpg')
        super(Fire, self).update()
    
    def update(self):
        '''As fire exists 3 reloads, it's durance decreases'''
        self.time-=1
        if self.time<0:
            self.kill()

class Wall(GameObject):
    '''An obstacle which player can not get through.'''
    image_files = ['wall.jpg']

    def collide_Player(self, player):
        return False #player can not move further


class Box(Wall):
    '''An obstacle which can be ruined by a bomb explosion.'''
    image_files = ['box.jpg']

    def collide_Fire(self):
        '''When colliding fire, the wall may generate bonus''' 
        x=random.choice([True,False])
        #Only good bonuses by now
        w=random.choice([SpeedUpBonus,AddBombBonus,MoveBombsBonus,IncreaseRadiusBonus, ExchangePlacesBonus])
        if x: w(self.game,self.x,self.y,[self.game.all,self.game.destroyable,self.game.bonuses])

class Player(GameObject):
    '''Represents a player in the game.'''
    player_images = None
    
    def __init__(self, game, x, y, id, *args, **kwargs):
        self.used=False
        self.game = game
        self.id = id
        self.cur_pic = 0
        self.cur_line = 0
        if Player.player_images == None: self.create_images()
        self.bombs = 1
        self.speed=0.1
        self.radius=1
        self.kills=0
        self.dest = None
        self.can_move_bombs=False
        super(Player, self).__init__(game, x,y, *args, **kwargs)
        self.image = Player.player_images[id][0][0]
        self.rect = pygame.rect.Rect(self.screen_x, self.screen_y, self.width, self.height)

    def create_images(self):
        Player.player_images = [dirs for dirs in os.listdir('Data\\players')]
        for dirs in os.listdir('Data\\players'):
            Player.player_images[self.cur_line] = [dir for dir in sorted(os.listdir(os.path.join('Data\\players',dirs)))]
            for dir in os.listdir(os.path.join('Data\\players',dirs)):
                Player.player_images[self.cur_line][self.cur_pic] = [self.load_image(os.path.join('players',dirs,dir,filename)) for filename in os.listdir(os.path.join('Data\\players',dirs,dir))]
                self.cur_pic += 1
            self.cur_line += 1
            self.cur_pic = 0
        self.line = 0
        self.pic = 0
    
    def go_up(self):
        self.move_forward([0, -self.speed])
    
    def go_down(self):
        self.move_forward([0,self.speed])
        
    def go_left(self):
        self.move_forward([-self.speed,0])
        
    def go_right(self):
        self.move_forward([self.speed,0])
    
    def put_bomb(self):
        '''Current player puts the bomb if he has the one'''
        if self.bombs>0:
            self.bombs-=1
            Bomb(self,self.game,round(self.x),round(self.y),groups=(self.game.all,self.game.bombs,self.game.destroyable))
    
    def move_forward(self, dest):
        '''Moves player to his destination'''
        self.dest = dest
        
    def update(self):
        '''Moves player to his destination and checks whether he accepted any bonuses'''
        if self.dest != None:
            self.x += self.dest[0]
            self.rect = pygame.rect.Rect(self.screen_x, self.screen_y, self.width, self.height)
            if len(pygame.sprite.spritecollide(self,self.game.obstacles,False))!=0:
                self.x-=self.dest[0]
            self.y += self.dest[1]
            self.rect = pygame.rect.Rect(self.screen_x, self.screen_y, self.width, self.height)
            if len(pygame.sprite.spritecollide(self,self.game.obstacles,False))!=0:
                self.y-=self.dest[1]
            if self.dest[1]>0: self.cur_line = 0
            if self.dest[1]<0: self.cur_line = 3
            if self.dest[0]>0: self.cur_line = 2
            if self.dest[0]<0: self.cur_line = 1
            self.cur_pic = (self.cur_pic + 1)% len(Player.player_images[self.id][self.cur_line])
            self.image = Player.player_images[self.id][self.cur_line][self.cur_pic]
        else:
            self.image = Player.player_images[self.id][0][0]
            
        bonus=pygame.sprite.spritecollide(self,self.game.bonuses,True)
        if len(bonus)>0:
            for x in bonus:
                x.affect_player(self)
        super(Player, self).update()
    
    def move_up_to(self):
        '''Function for truncating the player added for easier getting to the position'''
        self.x=round(self.x)
        self.y=round(self.y)
        