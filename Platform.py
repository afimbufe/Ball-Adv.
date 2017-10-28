# -*- coding: utf-8 -*-
"""
Ball Adventures: basic structure for the levels and platforms in them

Created on Mon Jul  3 15:17:54 2017

@author: Alex
"""

import pygame as py
import enemyBall as Ball
import frameworks as fw

# current implemtation: rectangles dressed up

# Constants:
blue = (0,0,255)
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
lightred = (255, 100, 100)

screenSize = (800, 600)
# Rectangle used to detect if an enemy or platform is on screen
screenBox = py.Rect(0, 0, screenSize[0], screenSize[1]) 
def setScreenSize(x, y):
    global screenSize, screenBox
    screenSize = (x, y)
    screenBox = py.Rect(0, 0, screenSize[0], screenSize[1])


class Floor(fw.positionObj):
    # Each floor is a list of platforms and enemies with a certain position relative to each other
    def __init__(self):
        self.platforms = []
        self.enemies = []
        self.doors = [] # Need at least one to get out
        
        self.length = screenSize[0]
        self.height = screenSize[1]
        
        self.activePlatforms = []
        self.activeEnemies = []
        self.activeDoors = []
        
        self.playerStartPos = (0,0) # starting position, also updated when inBattle
        self.pos = (0, 0) # top left of starting screen
        self.backgroundImg = None
        
        self.activeUpdateDelay = 2
        self.activeUpdateTimer = 0
    
    def XSideScroll(self, x):
        #print(self.pos[0])
        if x > self.pos[0] + screenSize[0] / 2 and x < self.pos[0] + self.length - screenSize[0] / 2:
            return screenSize[0] / 2 - x
        else:
            return 0
    
    def YSideScroll(self, y):
        if y < screenSize[1] / 2 + self.pos[1]:
            return screenSize[1] / 2 - y

        return 0
    
    def getGround(self):
#        print(self.pos[1], screenSize[1], self.pos[1] + screenSize[1])
        return self.pos[1] + screenSize[1]
        
    def shift(self, x, y):
        self.shiftPos(x, y)
        for platform in self.platforms:
            platform.shiftPos(x, y)
        for enemy in self.enemies:
            enemy.shiftPos(x, y)
            if enemy.isFloating():
                enemy.shiftBaseLineY(y)
            for bullet in enemy.getBullets():
                bullet.shiftPos(x, y)
            
        # also shift doors, moving platforms, etc
        
    
    
    def setDimensions(self, length, height):
        self.length = length
        self.height = height
    
    def getDimensions(self):
        return (self.length, self.height)
    
    def setPlayerStartPos(self, x, y):
        self.playerStartPos = (x, y)
        
    def getPlayerStartPos(self):
        return self.playerStartPos
    
    def getPlatforms(self):
        return self.platforms
    
    def getActivePlatforms(self):
        return self.activePlatforms
    
    def addPlatform(self, platform):
        self.platforms.append(platform)
        #self.activePlatforms.append(platform) # temp

    def addEnemy(self, enemy):
        self.enemies.append(enemy)
        # temp
        #self.activeEnemies.append(enemy)
        

    def clearAllBullets(self):
        for enemy in self.enemies:
            enemy.clearBullets()

    def resetVulnerability(self):
        for enemy in self.enemies:
            enemy.physEnd()
            for bullet in enemy.getBullets():
                bullet.physEnd()
            

    def removeEnemy(self, enemy):
        self.enemies.remove(enemy)
        self.activeEnemies.remove(enemy) # Must be on screen to kill it
                                 
    def getActiveEnemies(self):
        return self.activeEnemies
    
    def getEnemies(self):
        return self.enemies
    
    def updateActive(self):
        # Intensive, should not do every frame, perhaps every second
        self.activePlatforms = []
        self.activeEnemies = []
        for platform in self.platforms:
            if screenBox.colliderect(platform.getRect()):
                self.activePlatforms.append(platform)
        for enemy in self.enemies:
            if screenBox.colliderect(enemy.getHitBox()):
                self.activeEnemies.append(enemy)
    
    def loadEnemies(self, enemyList):
        for enemyItem in enemyList:
            enemy, pos = enemyItem
            enemy.setPos2(pos)
            self.addEnemy(enemy)

    def loadPlatforms(self, platformList):
        for platform in platformList:
            self.addPlatform(platform)

    def tick(self):
        self.activeUpdateTimer -= 1
        if self.activeUpdateTimer <= 0:
            self.activeUpdateTimer = self.activeUpdateDelay
            self.updateActive()
    
    
class Level(object):
    def __init__(self):
        self.floors = []
        self.currentFloor = None
        self.floorIndx = 0
        
    def addFloor(self, floor):
        self.floors.append(floor)
        if len(self.floors) == 1:
            self.currentFloor = floor
    
    # FloorData should be a dictionary
    def loadFloors(self, floorData):
        for floorInfo in floorData:
            floor = Floor()
            floor.setDimensions(floorInfo[2])
            floor.setPlayerStartPos(floorInfo[3])
            floor.loadPlatforms(floorData[0])
            floor.loadEnemies(floorData[1])
            self.addFloor(floor)
            
    def getCurrentFloor(self):
        return self.currentFloor
    
    def getCurrentFloorNum(self):
     pass


class Levels(object):
    def __init__(self):
        self.list = []
        self.currentLevel = None
        
    def getLevels(self):
        return self.list
    
    def addLevel(self, lv):
        self.list.append(lv)
        if len(self.list) == 1:
            self.currentLevel = lv
    
    def getCurrentLevel(self):
        return self.currentLevel
    
    def setCurrentLevel(self, lv):
        self.currentLevel = lv
    
    def gotoNextLevel(self):
        pass
    
        
class Door(fw.positionObj):
    def __init__(self, x, y):
        self.pos = (x, y)
    
class Platform(fw.positionObj):
    def __init__(self, x, y, width, height, angle, color):
        self.pos = (x, y) # top left corner
        self.width = width
        self.height = height
        self.angle = angle
        self.color = color
        self.hp = 0             # non-zero is destructable
        self.jumpThrough = False
        self.moving = False
        self.trampoline = False
        self.canBlockBullet = True
    
    def getDim(self):
        return (self.width, self.height)
    
    def getColor(self):
        return self.color
    
    def getRect(self):
        rect = py.Rect(self.pos[0], self.pos[1], self.width, self.height)
        return rect
    
    def canJumpThrough(self):
        return self.jumpThrough
    
    def isTrampoline(self):
        self.trampoline = True
        
    def canBlockBullets(self):
        return self.canBlockBullet

    def draw(self, display):
        pass
    

class MovingPlatform(Platform):
    def __init__(self, x, y, width, height, angle, color):
        Platform.__init__(self, x, y, width, height, angle, color)
        self.xspeed = 0
        self.yspeed = 0
        self.xLength = 0
        self.yLength = 0
            


    

# Initializing: Should be in a different file?
floor1 = Floor()
floor1.setDimensions(2000, 1000)
floor1.setPlayerStartPos(400, 300)
floor1Platforms = [Platform(300, 450, 200, 35, 0, black),
                   Platform(700, 300, 50, 300, 0, black),
                   Platform(1000, 100, 80, 500, 0, black),
                   Platform(1300, 300, 50, 300, 0, black),
                   Platform(1650, 200, 200, 30, 0, black),
                   Platform(1650, 450, 200, 30, 0, black)]
#floor1Enemies = [(Ball.GreenBall(), (600, 300)),
#                 (Ball.RedBall(), (1750, 300)),
#                 (Ball.WingedBall(), (1350, 350))]
floor1Enemies = [(Ball.WingedBall(), (1350, 150)),
#                 (Ball.PurpleBall(), (500, 250)),
#                 (Ball.WingedBall(), (500, 250)),
                 (Ball.GreenBall(), (1750, 300))]


floor1.loadPlatforms(floor1Platforms)
floor1.loadEnemies(floor1Enemies)

level1Data = [(floor1Platforms, floor1Enemies, (2000, 1000), (400, 300))]

level1 = Level()
level1.addFloor(floor1)

levels = Levels()
levels.addLevel(level1)