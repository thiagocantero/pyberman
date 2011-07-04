#GameObjects.py#Copyright (C) 2011 PyTeam"""Module which contains main classes such as Bonus, Wall, Box, Player and levelLoads necessary images from Data folderVersion 1.0Needs:- rewrite all paths from absolute to relative- add all bonuses- add bomb class- add functionality to player"""import pygameabsw=absh=0class Bonus(object):    bonuses = {'speedup':'Data\\1.jpg','smthelse':'Data\\2.jpg'}    def __init__(self, id, x, y):        self.__id = id        self.pict = pygame.image.load('D:\\projects\\pyberman\\'+Bonus.bonuses[id])        self.pictrect = self.pict.get_rect(center=(absw+y*40,absh+x*40))                class Wall:    def __init__(self, x, y):        self.pict = pygame.image.load('D:\\projects\\pyberman\\Data\\wall.jpg')        self.x = x        self.y = y        self.pictrect = self.pict.get_rect(center=(absw+y*40,absh+x*40))class Box():    def __init__(self, x, y):        self.pict = pygame.image.load('D:\\projects\\pyberman\\Data\\box.jpg')        self.x = x        self.y = y        self.pictrect = self.pict.get_rect(center=(absw+y*40,absh+x*40))class Player():    players = ['Data\\1.jpg','Data\\2.jpg','Data\\3.jpg']    def __init__(self, id, x, y):        self.__id = id        self.pict = pygame.image.load('D:\\projects\\pyberman\\'+Player.players[id])        self.x = x        self.y = y        self.bombs=1        self.speed=5        self.radius=1        self.pictrect = self.pict.get_rect(center=(absw+y*40,absh+x*40))class Level:    def __init__(self, filename):        file=open(filename, 'r')        self.height,self.width,self.maxplayers=[int(x) for x in file.readline().split()]        global absw,absh        absw,absh=400-(self.width*20)+20,300-(self.height*20)+20        self.field=[list(line.rstrip()) for line in file]        self.objects = []        for row in range(self.height):            for col in range(self.width):                if self.field[row][col] == 'W':                    self.objects.append(Wall(row,col))                elif self.field[row][col] == 'B':                    self.objects.append(Box(row,col))                elif self.field[row][col] == ' ': pass                elif int(self.field[row][col]) in range(10):                    self.objects.append(Player(int(self.field[row][col])-1,row,col))                            