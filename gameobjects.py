#GameObjects.py
#Copyright (C) 2011 PyTeam

'''Game objects.'''

import os
from weakref import WeakSet 
import random
import pygame
from PodSixNet.Connection import connection, ConnectionListener
import events

IMAGE_DIR = "Data"

class GameObject(pygame.sprite.Sprite, events.AutoListeningObject):
    '''The base class for all visible entities in the game, which implements generic operations.
    See the base class documentation at http://pygame.org/docs/ref/sprite.html#pygame.sprite
    '''
    #: list of file names of images to load
    image_files=[]

    def __init__(self, game, x, y, groups=None):
        self.game = game
        self.x = x
        self.y = y
        if not hasattr(self, 'rect'):
            self.update_rect()
        super(GameObject, self).__init__(*(groups if groups is not None else []))
        #Sprite doesn't call super, so we have to do it manually in order for AutoListeningObject gets initialized
        events.AutoListeningObject.__init__(self)
        self.images=[]
        for f in self.image_files:
            self.images.append(self.load_image(f))
        if self.images:
            self.image = self.images[0]
        self._last_collided = WeakSet ()

    def update_rect(self):
        self.rect = pygame.rect.Rect(self.screen_x, self.screen_y, self.width, self.height)

    def update(self):
        """Updates the object's state.
        It is called on each core frame."""
        if self.image is not None:
            self.update_rect()

    @property
    def width(self):
        return self.game.side-1

    @property
    def height(self):
        return self.game.side-1

    def load_image(self, file_name):
        """Manages caching and transformation of image."""
        cache = getattr(GameObject, '_image_cache', {})
        image = cache.get(file_name, None)
        if image is None:
            image = pygame.transform.smoothscale(pygame.image.load(os.path.join(IMAGE_DIR, file_name)), (self.width, self.height))
            cache[file_name] = image
            setattr(GameObject, '_image_cache', cache)
        return image

    @classmethod
    def invalidate_cache(cls):
        cache = getattr(cls, '_image_cache')
        if cache is not None:
            cache.clear()

    @property
    def screen_x(self):
        return self.game.xcoord_to_screen(self.x)

    @property
    def screen_y(self):
        return self.game.ycoord_to_screen(self.y)

    def kill(self):
        super(GameObject, self).kill()
        self.unregister_all_event_handlers()
        
    def move(self,dx,dy):
        '''Manages collision detection on movement.'''
        oldx, oldy, oldrect = self.x, self.y, self.rect
        self.x+=dx
        self.y+=dy
        self.update_rect()
        collides=pygame.sprite.spritecollide(self,self.game.all,False)
        can_move=True
        for obj in collides:
            if obj is not self:
                can_move&=self.collide(obj)&obj.collide(self)
        if not can_move:
            self.x, self.y, self.rect = oldx, oldy, oldrect
        collides = WeakSet (collides)
        stop_colliding = self._last_collided-collides
        for obj in stop_colliding:
            obj.stop_colliding(self)
        self._last_collided=collides
        return can_move

    def collide(self, other):
        '''By default, it searches a method named 'collide_otherclassname' and calls it if exist.
        for example, if object implements method named 'collide_Player', it would be called when player collides with this object.
        @returns: whether the movement can be continued
        @rtype: bool
        '''
        func = getattr(self, 'collide_%s'%other.__class__.__name__, None)
        if func is not None:
            return func(other)  
        return True

    def stop_colliding(self, other):
        '''Called when obj moves out of self.'''
        pass


class Bonus(GameObject):
    '''Represents an item which affects the player on collision and then disappears.'''

    def __init__(self, game, x, y, groups=None):
        super(Bonus,self).__init__(game, x, y, groups)
        self.cur_ind = 0

    def collide_Player(self, player):
        self.affect_player(player)
        self.kill()
        return True #Player can move further
        
    def collide_Fire(self, fire):
        self.kill()
        return False
        
    def collide_Bomb(self, bomb):
        self.kill()
        self.affect_player(bomb.player)
        return True

    def affect_player(self, player):
        """Makes something fun with player.
        Should be overloaded in derived classes."""
        pass

    def update(self):
        self.cur_ind = (self.cur_ind + 1) % len(self.image_files)
        self.image = self.images[self.cur_ind]
        super(Bonus,self).update()

class SpeedUpBonus(Bonus):
    '''Class representing bonus, increasing the player's speed by 0.5'''
    image_files=[os.path.join('bon_speed','1.png'),os.path.join('bon_speed','2.png'),os.path.join('bon_speed','3.png'),os.path.join('bon_speed','4.png')]

    def affect_player(self, player):
        player.speed+=0.5


class AddBombBonus(Bonus):
    '''Class representing bonus, increasing the capacity of player's bombs by one'''
    image_files=[os.path.join('bon_add','1.png'),os.path.join('bon_add','2.png'), os.path.join('bon_add','3.png'),os.path.join('bon_add','4.png')]

    def affect_player(self, player):
        player.bombs += 1


class MoveBombsBonus(Bonus) :
    '''Class representing bonus, allowing the player to move the bomb'''
    image_files=[os.path.join('bon_move','1.png'),os.path.join('bon_move','2.png'),os.path.join('bon_move','3.png'),os.path.join('bon_move','4.png')]
    #action of this class is still undone

    def affect_player(self, player):
        player.can_move_bombs = True


class IncreaseRadiusBonus(Bonus):
    '''Class representing bonus, increasing the radius of a player by one'''
    image_files=[os.path.join('bon_inc','1.png'),os.path.join('bon_inc','2.png'), os.path.join('bon_inc','3.png'),os.path.join('bon_inc','4.png')]

    def affect_player(self, player):
        player.radius += 1


class BadBonus(Bonus):
    '''Class representing bad bonus, that have their period of impact over the player'''
    image_files=[os.path.join('bon_bad','1.png'),os.path.join('bon_bad','2.png'), os.path.join('bon_bad','3.png'), os.path.join('bon_bad','4.png')]
    
    def __init__(self, game, x, y, groups=None):
        super(BadBonus, self).__init__(game, x, y, groups)
        self.time = 15
     
    def affect_player(self, player):
        pass
    
class SpeedDownBonus(BadBonus):
    '''Class representing bad bonus, decreasing speed to minimum for a while'''
    def affect_player(self, player):
        player.temp_speed = player.speed
        player.bad_speed=15
        player.speed = 1


class ReduceRadiusBonus(BadBonus):
    '''Class representing bad bonus, reducing radius to minimum for a while'''

    def affect_player(self, player):
        player.temp_radius = player.radius
        player.bad_radius=15
        player.radius = 1


class ExchangePlacesBonus(Bonus):
    '''Class representing bad bonus, when player changes place with random other player'''

    image_files=[os.path.join('bon_bad','1.png'),os.path.join('bon_bad','2.png'), os.path.join('bon_bad','3.png'), os.path.join('bon_bad','4.png')]
    
    def affect_player(self, player):
        tempx, tempy = player.x, player.y
        rand_player = random.choice(self.game.players[:self.game.players_alive ])
        while rand_player == player:  rand_player=random.choice(self.game.players[:self.game.players_alive])
        player.x = rand_player.x
        player.y = rand_player.y
        rand_player.x = tempx
        rand_player.y = tempy
        player.move_up_to()
        player.update_rect()
        rand_player.move_up_to()
        rand_player.update_rect()

class Bomb(GameObject):
    '''A class introducing Bomb, which can be put by player'''
    image_files = ['bomb.png']

    def __init__(self, player, game, x, y, *args, **kwargs):
        self.player, self.game, self.x, self.y =player, game, x, y
        self.time=7
        self.player_first_stands = True
        self.dest=None
        super(Bomb, self).__init__(game, x,y, *args, **kwargs)

    def collide_Player(self, player):
        if self.player_first_stands: 
            return True
        else:
            if player.can_move_bombs:
                if player.cur_dest!=None:
                    self.dest=player.cur_dest[:]
                else: self.dest=None
                return True
            else:
                self.dest=None
                return False

    def stop_colliding(self, obj):
        if isinstance(obj, Player):
            self.player_first_stands = False

    def collide_Fire(self, fire):
        self.kill()
        return False

    def collide_Bomb(self, bomb):
        return False

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
                elif isinstance(obj,Box):
                    obj.collide_Fire(fire)
                elif isinstance(obj,Player):
                    obj.collide_Fire(fire)
            ret=True
        if len(pygame.sprite.spritecollide(fire,self.game.walls,False))>0: 
            fire.kill()
            ret=True
        return ret

    def update(self):
        if self.dest != None:
            self.move(self.dest[0]*self.game.delta,self.dest[1]*self.game.delta)    
        self.time-=self.game.delta
        if self.time < 1.2:  
            if self.time<0.1:
                self.explode()
            else: self.image = self.load_image(os.path.join('bomb','%s.png'%str(int(self.time*10))))
        super(Bomb, self).update()


class Fire(GameObject):
    image_files = ['fire.jpg']

    '''The class representing the fire which appears straight after the bomb explosion'''
    def __init__(self, game, player, x, y, *args, **kwargs):
        self.player, self.game, self.x, self.y =player, game, x, y
        self.time = 1
        super(Fire, self).__init__(game, x,y, *args, **kwargs)
        
    def update(self):
        '''As fire exists 1 second, it's durance decreases'''
        self.time-=self.game.delta
        if self.time<0:
            self.kill()

    def collide_Player(self, player):
        return False #Player can move further

    def collide_Fire(self, fire):
        return True
        
    def collide_Bomb(self, bomb):
        return False


class Wall(GameObject):
    '''An obstacle which player can not get through.'''
    image_files = ['wall.jpg']

    def collide_Player(self, player):
        return False

    def collide_Fire(self, fire):
        return False
        
    def collide_Bomb(self, bomb):
        return False


class Box(Wall):
    '''An obstacle which can be ruined by a bomb explosion.'''
    image_files = ['box.jpg']

    def collide_Fire(self,fire):
        '''When colliding fire, the wall may generate bonus''' 
        x=random.choice([True,False])
        #Only good bonuses by now
        w=random.choice([SpeedUpBonus,AddBombBonus,MoveBombsBonus,IncreaseRadiusBonus, ExchangePlacesBonus, ReduceRadiusBonus, SpeedDownBonus,IncreaseRadiusBonus,SpeedUpBonus,AddBombBonus])
        if x: w(self.game,self.x,self.y,[self.game.all,self.game.destroyable,self.game.bonuses])
        return False
    
    def collide_Player(self, player):
        return False 

    def collide_Bomb(self, bomb):
        return False


class Player(GameObject, ConnectionListener):
    '''Represents a player in the game.'''
    player_images = None

    def __init__(self, game, x, y, id, *args, **kwargs):
        self.id = id
        self.cur_pic = self.cur_line = 0
        self.bombs, self.speed, self.radius, self.kills, self.time_moving = 1, 2.0, 1, 0, 0
        self.dest = self.cur_dest = None
        self.can_move_bombs=False
        self.temp_speed = self.temp_radius = None
        self.bad_speed, self.bad_radius=None, None
        super(Player, self).__init__(game, x,y, *args, **kwargs)
        if Player.player_images == None: self.create_images()
        self.image = Player.player_images[id][0][0]

    def collide_Player(self, player):
        return True #Player can move further

    def collide_Fire(self, fire):
        self.game.players_alive-=1
        if self is fire.player: 
            self.game.players_score[self.id]-=1
        else: self.game.players_score[fire.player.id]+=1
        self.kill()
        return True

    def create_images(self):
        Player.player_images = [dirs for dirs in os.listdir(os.path.join('Data','players'))]
        for dirs in os.listdir(os.path.join('Data','players')):
            Player.player_images[self.cur_line] = [dir for dir in sorted(os.listdir(os.path.join('Data','players',dirs)))]
            for dir in os.listdir(os.path.join('Data','players',dirs)):
                Player.player_images[self.cur_line][self.cur_pic] = [self.load_image(os.path.join('players',dirs,dir,filename)) for filename in os.listdir(os.path.join('Data','players',dirs,dir))]
                self.cur_pic += 1
            self.cur_line += 1
            self.cur_pic = 0
        self.line = 0
        self.pic = 0

    def go_up(self):
        self.dest = (0, -1)
        self.cur_line = 3
        if self.game.is_network_game:
            self.Send({'action': 'moved', 'player_id': self.id, 'dest': self.dest, 'cur_line': self.cur_line})

    def go_down(self):
        self.dest = (0, 1)
        self.cur_line = 0
        if self.game.is_network_game:
            self.Send({'action': 'moved', 'player_id': self.id, 'dest': self.dest, 'cur_line': self.cur_line})

    def go_left(self):
        self.dest = (-1, 0)
        self.cur_line = 1
        if self.game.is_network_game:
            self.Send({'action': 'moved', 'player_id': self.id, 'dest': self.dest, 'cur_line': self.cur_line})

    def go_right(self):
        self.dest = (1, 0)
        self.cur_line = 2
        if self.game.is_network_game:
            self.Send({'action': 'moved', 'player_id': self.id, 'dest': self.dest, 'cur_line': self.cur_line})

    def step(self):
        if self.dest!=None:
            if self.time_moving==0:
                self.time_moving = self.game.step_length/self.speed
                self.cur_dest=[self.dest[0]*self.speed,self.dest[1]*self.speed]

    def stop(self):
        self.dest=None
        if self.game.is_network_game:
            self.Send({'action': 'moved', 'player_id': self.id, 'dest': self.dest, 'cur_line': self.cur_line})

    def put_bomb(self):
        '''Current player puts the bomb if he has the one'''
        if not pygame.sprite.spritecollide(self,self.game.bombs,False):
            if self.bombs>0:
                if self.game.is_network_game:
                    connection.Send({'action': 'put_bomb', 'player_id': self.id})
                self.bombs-=1
                Bomb(self,self.game,round(self.x),round(self.y),groups=(self.game.all,self.game.bombs,self.game.destroyable))

    def Network_put_bomb(self, data):
        if not data['player_id']==self.id:
            return
        self.put_bomb()

    def Network_moved(self, data):
        if not data['player_id']==self.id:
            return
        self.dest = data['dest']
        self.cur_line = data['cur_line']

    def update(self):
        '''Moves player to his destination and checks whether he accepted any bonuses'''
        self.Pump()
        self.step()
        if self.temp_speed is not None:
            self.bad_speed-=self.game.delta
            if self.bad_speed<0:
                self.speed=self.temp_speed
                self.temp_speed=None
        if self.temp_radius is not None:
            self.bad_radius-=self.game.delta
            if self.bad_radius<0:
                self.radius=self.temp_radius
                self.temp_radius=None
        if self.dest != None:
            d=min(self.time_moving,self.game.delta)
            self.time_moving-=d
            self.move(self.cur_dest[0]*d,self.cur_dest[1]*d)    
            self.cur_pic = (self.cur_pic + 1)% len(Player.player_images[self.id][self.cur_line])
            self.image = Player.player_images[self.id][self.cur_line][self.cur_pic]
        else:
            self.image = Player.player_images[self.id][0][0]

    def move_up_to(self):
        '''Function for truncating the player added for easier getting to the position'''
        self.x=round(self.x)
        self.y=round(self.y)

    def kill(self):
        if self.game.players_alive<2:
            self.game.end_game()
        super(Player, self).kill()
