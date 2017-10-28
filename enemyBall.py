# -*- coding: utf-8 -*-
"""
Created on Sun Jul 30 15:53:07 2017

@author: Alex
"""

import BallUnit as ball
import Projectile as rng
import pygame as py
import math
import random
screenSize = ball.screenSize

blue = (0,0,255)
white = (255,255,255)
black = (0,0,0)
grey = (128,128,128)
red = (255,0,0)
green = (0,255,0)
yellow = (255,255,0)
lightred = (255, 100, 100)
purple = (255,0,255)


def getRandPos():
    return (random.randint(100, 700), random.randint(100, 500))

def getRandomAngle():
    return (random.random() * math.pi - math.pi/2, random.random() * 2 // 2 - 1)


class GreenBall(ball.GroundedBall):
    def __init__(self):
        hp = 17
        radius = 60
        xspeed = 20
        expPrize = 50
        jumpSpeed = 35
        yaccel = -1.5
        
        bouncy = True
        ball.GroundedBall.__init__(self, "Green Ball", hp, radius, xspeed, expPrize, jumpSpeed, yaccel, bouncy)
        self.XLanding = 0
        self.maxShotTimer = 20
        self.shotTimer = self.maxShotTimer
        self.originalCollideDmg = 9
        self.collideDmg = self.originalCollideDmg
        self.healablePct = .33
        
        # Constants, in-battles states/attacks
        # Some Bounces cause shockwaves
        self.shotTracker = 0
        self.jumpsTillSwitch = 3
        self.DEFAULT = 0
        self.FOLLOWSHOOT = 1
        self.SLAMDOWN = 2
        self.FOURSHOT = 3
        self.SHOOTAROUND = 4
        self.GROUPSHOT = 5
        self.BOUNCYSHOTS = 6
        self.SPRAY = 7
        self.GROWTHSHOTS = 8
        self.JUMPON = 10
        self.HARDDEFAULT = 11
        self.currentAttack = self.HARDDEFAULT
        self.levelOneMoves = [self.DEFAULT, self.SLAMDOWN]
        
    def chooseAttack(self, rand):
        if self.lv == 1:
            if rand < .5:
                self.updateStats(self.SLAMDOWN)
            else:
                self.updateStats(self.FOURSHOT)
        elif self.lv == 2:
            pass
        else:
            pass
    
    
    def updateStats(self, newAtk):
        self.currentAttack = newAtk
        self.collideDmg = self.originalCollideDmg
        self.shotTracker = 0
        if newAtk == self.DEFAULT:
            const = 100
            stats = {'jumpspeed':35, 'yaccel':-1.5, 'jumpsTillSwitch':3, 'maxShotTimer':20, \
                     'xspeed':(self.playerPos[0] - self.pos[0])/const}
        elif newAtk == self.FOURSHOT:
            const = 100
            stats = {'jumpspeed':38, 'yaccel':-1.5, 'jumpsTillSwitch':1, 'maxShotTimer':25, \
                     'xspeed':(self.playerPos[0] - self.pos[0])/const}
        elif newAtk == self.SLAMDOWN:
            const = 30
            stats = {'jumpspeed':42, 'yaccel':-1.5, 'jumpsTillSwitch':3, 'maxShotTimer':30, \
                     'xspeed':(self.playerPos[0] - self.pos[0])/const}
        elif newAtk == self.JUMPON:
            const = 50
            stats = {'jumpspeed':35, 'yaccel':-1.5, 'jumpsTillSwitch':3, 'maxShotTimer':20, \
                     'xspeed':(self.playerPos[0] - self.pos[0])/const}
        elif newAtk == self.HARDDEFAULT:
            const = 50
            stats = {'jumpspeed':35, 'yaccel':-1.5, 'jumpsTillSwitch':2, 'maxShotTimer':10, \
                     'xspeed':(self.playerPos[0] - self.pos[0])/const}
        else:
            self.currentAttack = self.DEFAULT
            const = 100
            stats = {'jumpspeed':35, 'yaccel':-1.5, 'jumpsTillSwitch':3, 'maxShotTimer':20, \
                     'xspeed':(self.playerPos[0] - self.pos[0])/const}
        self.jumpspeed = stats['jumpspeed']
        self.yaccel = stats['yaccel']
        self.jumpsTillSwitch = stats['jumpsTillSwitch']
        self.maxShotTimer = stats['maxShotTimer']
        self.xspeed = stats['xspeed']
    
    def inBattleBounce(self):
        #print("JumpsTillSwitch:", self.jumpsTillSwitch)
        self.jumpsTillSwitch -= 1
        if self.jumpsTillSwitch < 0:
            if self.currentAttack == self.SLAMDOWN and self.xspeed == 0:
                self.shootAround()
            self.chooseAttack(random.random())
        
    
    
    def shootAround(self):
        self.addBullet(rng.greenBasicShot(self.pos[0], self.pos[1], 0, True))
        self.addBullet(rng.greenBasicShot(self.pos[0], self.pos[1], math.pi/4, True))
        self.addBullet(rng.greenBasicShot(self.pos[0], self.pos[1], math.pi/2, True))
        self.addBullet(rng.greenBasicShot(self.pos[0], self.pos[1], 0, False))
        self.addBullet(rng.greenBasicShot(self.pos[0], self.pos[1], math.pi/4, False))
    
    def updateFrame(self, groundY = screenSize[1]):
        if self.pos[1] > groundY - self.radius and not self.isGrounded(): # or land on a platform
            # Bounce
            self.touchGround()
            self.setPos(self.pos[0], groundY - self.radius)
            
            if self.isInBattle():
                self.inBattleBounce()
                if self.currentAttack == self.DEFAULT:
                    self.xspeed = (self.playerPos[0] - self.pos[0])/100
                elif self.currentAttack == self.JUMPON or self.currentAttack == self.HARDDEFAULT:
                    self.xspeed = (self.playerPos[0] - self.pos[0])/50                    
                elif self.currentAttack == self.SLAMDOWN and not self.xspeed == 0:
                    self.xspeed = (self.playerPos[0] - self.pos[0])/30
                elif self.currentAttack == self.SLAMDOWN and self.xspeed == 0:
                    self.jumpspeed = 35
                    self.yaccel = -1.5
                    self.xspeed = (self.playerPos[0] - self.pos[0])/50
                    self.dmg = 9
                    self.jumpsTillSwitch = 0
                    self.shotTimer = self.maxShotTimer
                    self.shootAround()
                    # Last bounce
            self.jump()
            # update targetXLanding
        elif not self.isGrounded(): # in air
            tempY = self.pos[1] - self.yspeed  
            self.yspeed += self.yaccel            
            self.setY(tempY)
    
        if self.isInBattle(): # X Movements and in air
            x, y = self.playerPos
            if self.currentAttack == self.SLAMDOWN and not self.xspeed == 0 and \
                    self.getHitBox().left < x and self.getHitBox().right > x and self.getY()<y and self.getY() < 450:
                self.xspeed = 0
                self.yspeed = min(-10, self.yspeed)
                self.yaccel = -5
                self.collideDmg = 20
            tempX = self.pos[0] + self.xspeed
            self.setX(tempX)
            if self.pos[0] > screenSize[0] - self.radius:
                self.setPos(screenSize[0] - self.radius, self.pos[1])
            if self.pos[0] < self.radius:
                self.setPos(self.radius, self.pos[1])
        
        # How to detect player position for Enemy?

    def shoot(self, angle, direction = True):
        if not self.isInBattle():
            self.addBullet(rng.greenBasicShot(self.pos[0], self.pos[1], angle, direction))
        else:
            if self.currentAttack == self.DEFAULT or self.currentAttack == self.SLAMDOWN \
                    or self.currentAttack == self.HARDDEFAULT or self.currentAttack == self.JUMPON:
                self.addBullet(rng.greenBasicShot(self.pos[0], self.pos[1], angle, direction))
            elif self.currentAttack == self.FOURSHOT:
                self.addBullet(rng.greenBasicShot(self.pos[0], self.pos[1], angle + math.pi/18, direction))
                self.addBullet(rng.greenBasicShot(self.pos[0], self.pos[1], angle - math.pi/18, direction))
                self.addBullet(rng.greenBasicShot(self.pos[0], self.pos[1], angle + math.pi/36, direction))
                self.addBullet(rng.greenBasicShot(self.pos[0], self.pos[1], angle - math.pi/36, direction))
            else:
                self.addBullet(rng.greenBasicShot(self.pos[0], self.pos[1], angle, direction))

    def tick(self):
        self.timers()
        if self.shotTimer <= 0:
            self.shotTimer = self.maxShotTimer
            return True # shoot a projectile
        else:
            self.shotTimer -= 1 
            return False
        
    def draw(self, display):
        if self.invincibilityCounter > 0:
            if self.invincibilityCounter % 6 == 0 or self.invincibilityCounter % 6 == 1  or self.invincibilityCounter % 6 == 2:
                py.draw.circle(display, lightred, self.getApproxPos(), self.radius, 0)
            else:
                py.draw.circle(display, green, self.getApproxPos(), self.radius, 0)
        else:
            py.draw.circle(display, green, self.getApproxPos(), self.radius, 0)


class RedBall(ball.GroundedBall):
    def __init__(self):
        hp = 20
        radius = 45
        xspeed = 20
        expPrize = 80
        jumpSpeed = 55
        yaccel = -5
        bouncy = True
        ball.GroundedBall.__init__(self, "Red Ball", hp, radius, xspeed, expPrize, jumpSpeed, yaccel, bouncy)
        self.XLanding = 0
        self.maxShotTimer = 25
        self.shotTimer = self.maxShotTimer
        self.collideDmg = 11
   
        self.DEFAULT = 0
        self.VCHARGE = 1
        self.HARDDEFAULT = 2
        self.VERTICALCHARGE = 3
        self.SHOWFIRE = 4
        self.FIREWHIP = 5
    
    
    def updateFrame(self, groundY = screenSize[1]):
        if self.pos[1] > groundY - self.radius and not self.isGrounded(): # or land on a platform
            # Bounce
            self.touchGround()
            
            if self.isInBattle:
                const = 50
                self.xspeed = (self.playerPos[0] - self.pos[0])/const
            self.setY(groundY - self.radius)
            self.jump()
            # update targetXLanding
        elif not self.isGrounded():
            
            tempY = self.pos[1] - self.yspeed  
            self.yspeed += self.yaccel            
            self.setY(tempY)
    
        if self.isInBattle():
            tempX = self.pos[0] + self.xspeed
            self.setX(tempX)
            if self.pos[0] > screenSize[0] - self.radius:
                self.setPos(screenSize[0] - self.radius, self.pos[1])
            if self.pos[0] < self.radius:
                self.setX(self.radius)
    
    
    
    def shoot(self, angle, direction = True):
        self.addBullet(rng.Fireball(self.pos[0], self.pos[1], angle, direction))
    
    def tick(self):
        self.timers()
        if self.shotTimer == 0:
            self.shotTimer = self.maxShotTimer
            return True # shoot a projectile
        else:
            self.shotTimer -= 1
            return False
    
    def draw(self, display):
        if self.invincibilityCounter > 0:
            if self.invincibilityCounter % 6 == 0 or self.invincibilityCounter % 6 == 1 or self.invincibilityCounter % 6 == 2:
                py.draw.circle(display, black, self.getApproxPos(), self.radius, 0)
            else:
                py.draw.circle(display, red, self.getApproxPos(), self.radius, 0)
        else:
            py.draw.circle(display, red, self.getApproxPos(), self.radius, 0)
            
class WingedBall(ball.FloatingBall):
    def __init__(self):
        hp = 30
        xspeed = 20
        radius = 30
        expPrize = 100
        amplitude = 100
        frequency = 0.15
        ball.FloatingBall.__init__(self, "Winged Ball", hp, radius, xspeed, expPrize, amplitude, frequency)    
        
        self.maxShotTimer = 35
        self.inBattlePos = (450, 350)
        self.collideDmg = 5
        self.shotCount = 0
        self.wallCount = 0
        self.inertia = 1
        self.moveEndTimer = 0
        self.waitTimer = 0
        
        self.DEFAULT = 0
        self.TRIARROW = 1 # COMPLETE
        self.CIRCLEARROW = 2
        self.BASICLIGHTPILLAR = 3
        self.RANDOMLIGHTPILLAR = 4
        self.CURVEDARROWS = 5 
        self.HARDCURVEDARROWS = 6
        self.SWOOP = 7
        self.CRISSCROSSSHOT = 8
        self.DROPARROWS = 9 # COMPLETE
        self.WINDMILLARROW = 10
        self.ACCELRAM = 11
        self.TRIANGLEATTACK = 12
        self.SPRAY = 13
        self.CIRCLESHOT = 14  # COMPLETE
        self.currentAttack = self.TRIARROW
        self.dir = 1
        self.xaccel = 1
        
        
        # Special Attacks: Heal,Raining arrows
     
    def chooseAttack(self, rand):
        if self.lv == 1:
            if rand < .25:
                self.updateStats(self.BASICLIGHTPILLAR)
            elif rand < .52:
                self.updateStats(self.CIRCLESHOT)
            elif rand < .72:
                self.updateStats(self.TRIARROW)
            else:
                self.updateStats(self.DROPARROWS)
        elif self.lv == 2:
            pass
        else:
            pass
        
    def updateStats(self, newAtk):
        self.currentAttack = newAtk
        self.shotCount = 0
        self.inertia = 1
        self.inPlace = False
        if newAtk == self.TRIARROW:
            stats = {"newY": 250, "newX": 450, "ySpeed": 4, "shotTimer": 25, "numshots": 3, "xSpeed": 10}
            if abs(self.getX() - stats["newX"]) < 150:
                stats["newX"] = -1
                self.inertia = 0
        elif newAtk == self.DROPARROWS:
            stats = {"newY": 350, "newX": -1, "ySpeed": 12, "shotTimer": 7, "numshots": -1, "xSpeed": 20}
            if random.random() > .5:
                self.dir = 1
            else:
                self.dir = -1
            self.wallCount = 4
        elif newAtk == self.CIRCLESHOT:
            timeTillShot = 25
            stats = {"shotTimer": -1, "numshots": 4}
            stats["newX"] = random.randint(100, 700)
            stats["newY"] = random.randint(100, 500)
            stats["ySpeed"] = abs(self.baseLineY - stats["newY"])//timeTillShot + 1
            stats["xSpeed"] = abs(self.getX() - stats["newX"])//timeTillShot + 1
        elif newAtk == self.BASICLIGHTPILLAR:
            stats = {"newY": 300, "newX": 400, "ySpeed": 12, "shotTimer": 13, "numshots": 7, "xSpeed": 12}
        
        self.yTarget = stats["newY"]
        self.xTarget = stats["newX"]
        self.yspeed = stats["ySpeed"]
        self.xspeed = stats["xSpeed"]
        self.maxShotTimer = stats["shotTimer"]
        self.shotCount = stats["numshots"]
        
        if self.getX() > self.xTarget:
            self.dir = -1
        else:
            self.dir = 1
        
    #def getHitBox():
    #    pass
    def inBattleState(self, newState):
        self.inBattle = newState
        if self.inBattle:
            self.inBattleHP = max(self.inBattleHP, self.hp)
            self.hp = self.inBattleHP
            self.baseLineY = self.inBattlePos[1]
            self.chooseAttack(random.random())
            # Choose an attack
        else:
            self.maxShotTimer = 35
            

    def draw(self, display):
        wingHeight = 20
        wingWidth = 80
        x, y = self.getApproxPos()
        py.draw.rect(display, grey, py.Rect(x - wingWidth, y - wingHeight, wingWidth, wingHeight))
        py.draw.rect(display, grey, py.Rect(x, y - wingHeight, wingWidth, wingHeight))
        
        if self.invincibilityCounter > 0:
            if self.invincibilityCounter % 6 == 0 or self.invincibilityCounter % 6 == 1  or self.invincibilityCounter % 6 == 2:
                py.draw.circle(display, lightred, self.getApproxPos(), self.radius, 0)
            else:
                py.draw.circle(display, yellow, self.getApproxPos(), self.radius, 0)
        else:
            py.draw.circle(display, yellow, self.getApproxPos(), self.radius, 0)
        
        
    def xHandler(self):
        inertiaChange = -.1
        
        self.shiftX(self.xspeed * self.inertia * self.dir)
        
        if not self.xTarget == -1 and self.getX() < self.xTarget and self.inertia == 1 and self.dir == -1:
            self.inertia += inertiaChange
                
        elif not self.xTarget == -1 and self.getX() > self.xTarget and self.inertia == 1 and self.dir == 1:
            self.inertia += inertiaChange
            
        if self.inertia < 1 and self.inertia > 0:
            self.inertia += inertiaChange
            if self.inertia <= 0:
                self.inertia = 0
        
        
    def updateFrame(self, groundY = screenSize[1]):
        if self.isInBattle():
            print("YSpeed", self.yspeed)
            if not self.yTarget == -1 and self.baseLineY < self.yTarget:
                self.baseLineY += self.yspeed
                print("Lowering Baseline", self.baseLineY, self.yTarget)
                if self.baseLineY > self.yTarget:
                    self.baseLineY = self.yTarget
                    self.yspeed = 0
            elif not self.yTarget == -1 and self.baseLineY > self.yTarget:
                self.baseLineY -= self.yspeed
                print("Raising Baseline", self.baseLineY, self.yTarget)
                if self.baseLineY < self.yTarget:
                    self.baseLineY = self.yTarget
                    self.yspeed = 0
            
            self.xHandler()
            print("Direction", self.dir)
            print("X", self.getX(), self.xTarget)
            print("Shotcount", self.shotCount)
            if self.currentAttack == self.DROPARROWS:
                if self.dir > 0 and self.getX() > 750:
                    self.dir *= -1
                    self.wallCount -= 1
                elif self.dir < 0 and self.getX() < 50:
                    self.dir *= -1
                    self.wallCount -= 1
                if self.wallCount <= 0:
                    self.wallCount = 0
                    self.chooseAttack(random.random())
            elif self.currentAttack == self.CIRCLESHOT:
                if self.inertia == 0 or self.baseLineY == self.yTarget:
                    timeTillShot = 25
                    self.inertia = 1
                    self.shotCount -= 1
                    
                    self.circleShot()
                    self.xTarget = random.randint(100, 700)
                    self.yTarget = random.randint(100, 500)
                    self.yspeed = abs(self.baseLineY - self.yTarget)//timeTillShot + 1
                    self.xspeed = abs(self.getX() - self.xTarget)//timeTillShot + 1
                    if self.getX() > self.xTarget:
                        self.dir = -1
                    else:
                        self.dir = 1
                                  
                    if self.shotCount < 0 and not self.moveEndTimer > 0:
                        self.moveEndTimer = 40
            
            self.updateAngle()
            self.updateY()
        else:
            self.updateAngle()
            self.updateY()
    
    def circleShot(self):
        self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], 0, True))
        self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], 0, False))
        
        self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], math.pi/3, True))
        self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], math.pi/6, True))
        self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], math.pi/2, True))
        self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], math.pi/3, False))
        self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], math.pi/6, False))
        
        self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], -math.pi/3, True))
        self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], -math.pi/6, True))
        self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], -math.pi/2, True))
        self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], -math.pi/3, False))
        self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], -math.pi/6, False))
    
    def shoot(self, angle, direction = 0):
        if self.isInBattle():
            if self.currentAttack == self.DROPARROWS:
                if random.random() > .78:
                    self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], angle, direction))
                else:    
                    self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], -math.pi/2, direction))
            elif self.currentAttack == self.TRIARROW and self.shotCount > 0:
                length = 80
                rightAngle = angle + math.pi/2
                xAdjust = abs(length/2 * math.cos(rightAngle))
                yAdjust = abs(length/2 * math.sin(rightAngle))
                
                if (angle < 0 and direction) or (angle > 0 and not direction):
                    yAdjust *= -1  
                self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], angle, direction))
                self.addBullet(rng.LightArrow(self.pos[0] - xAdjust, self.pos[1] - yAdjust, angle, direction))
                self.addBullet(rng.LightArrow(self.pos[0] + xAdjust, self.pos[1] + yAdjust, angle, direction))
                self.shotCount -= 1
                if self.shotCount == 0:
                    self.moveEndTimer = 30
            elif self.currentAttack == self.BASICLIGHTPILLAR:
                self.addBullet(rng.LightPillar(random.randint(0, 750)))
                self.shotCount -= 1
                if self.shotCount == 0:
                    self.moveEndTimer = 15
        else:
            self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], angle, direction))
            self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], angle + math.pi/6, direction))
            self.addBullet(rng.LightArrow(self.pos[0], self.pos[1], angle - math.pi/6, direction))
            
    def tick(self):
        self.timers()
        
        if self.moveEndTimer > 0:
            self.moveEndTimer -= 1
            if self.moveEndTimer == 0:
                self.chooseAttack(random.random())
        
        if not self.maxShotTimer <= -1:
            if self.shotTimer == 0:
                self.shotTimer = self.maxShotTimer
                return True # shoot a projectile
            else:
                self.shotTimer -= 1
                return False
        
class PurpleBall(ball.FloatingBall):
    def __init__(self):
        hp = 46
        radius = 52
        expPrize = 125
        amplitude = 50
        frequency = 0.1
        ball.FloatingBall.__init__(self, "Winged Ball", hp, radius, 0, expPrize, amplitude, frequency)    
        
        self.maxShotTimer = 12
        self.inBattlePos = (450, 350)
        self.collideDmg = 15
        self.shotCount = 0

        self.DEFAULT = 0
        self.VERTICALBOUNCEBALLS = 1
        self.HORIZONTALBOUNCEBALLS = 2
        self.RECTALMIGHTY = 3
        self.PURPLELASER = 4
        self.PURPLEBALLSTORM = 5
        self.MATERIALIZESHOT = 6
        self.CHARGESHOT = 7
        self.TELEPORT = 8
        self.BIGBALL = 9
        self.BIGBALLBOUNCE = 10
        self.currentAttack = self.BIGBALLBOUNCE
        
        # Varying Speed Shots?
        # Teleports to new place and does its attack

    def chooseAttack(self, rand):
        if self.lv == 1:
            if rand < .0:
                self.updateStats(self.DEFAULT)
            elif rand < 1:
                self.updateStats(self.BIGBALLBOUNCE)
            elif rand < .55:
                self.updateStats(self.BIGBALL)
            else:
                self.updateStats(self.MATERIALIZESHOT)
        elif self.lv == 2:
            pass
        else:
            pass
        
    def updateStats(self, newAtk):
        self.currentAttack = newAtk
        self.shotCount = 0
        self.inPlace = False
        if newAtk == self.DEFAULT:
            stats = {"shotTimer": 15, "numshots": 10}
        elif newAtk == self.MATERIALIZESHOT:
            stats = {"shotTimer": 12, "numshots": 15}
        elif newAtk == self.BIGBALL:
            stats = {"shotTimer": 40, "numshots": 2}
        elif newAtk == self.BIGBALLBOUNCE:
            stats = {"shotTimer": 200, "numshots": 1}
        
        self.setPos2(getRandPos())
        self.maxShotTimer = stats["shotTimer"]
        self.shotCount = stats["numshots"]


    def draw(self, display):        
        if self.invincibilityCounter > 0:
            if self.invincibilityCounter % 6 == 0 or self.invincibilityCounter % 6 == 1  or self.invincibilityCounter % 6 == 2:
                py.draw.circle(display, red, self.getApproxPos(), self.radius, 0)
            else:
                py.draw.circle(display, purple, self.getApproxPos(), self.radius, 0)
        else:
            py.draw.circle(display, purple, self.getApproxPos(), self.radius, 0)
        py.draw.circle(display, black, self.getApproxPos(), self.radius, 3)
        
    def updateFrame(self, groundY = screenSize[1]):
        self.updateAngle()
        self.updateY()
        for bullet in self.bullets:
            if not bullet.isFullyGrown():
                bullet.updateAngle(self.playerPos)
        
        if self.isInBattle():
            pass
    
    def shootAt(self, pPos = [-1, -1]):
        playerPt = pPos
        if playerPt == [-1, -1]:
            playerPt = self.playerPos
        else:
            self.updatePlayerPos(pPos)
        
        if self.isInBattle and self.currentAttack == self.MATERIALIZESHOT:
            otherPos = getRandPos()    
        else:
            otherPos = self.pos
            
        if otherPos[0] - playerPt[0] == 0:
            angle = -math.pi/2
        else:
            if otherPos[0] - playerPt[0] == 0:
                angle = -math.pi/2
            else:
                angle = math.atan(-(otherPos[1] - playerPt[1])/(otherPos[0] - playerPt[0]))

        if otherPos[0] < playerPt[0]:
            angle *= -1
        angle += math.pi
        
        self.shoot(otherPos, angle, otherPos[0] > playerPt[0])
    
    
    def shoot(self, pos, angle, direction = 0):
        if self.isInBattle():
            self.shotCount -= 1
            if self.currentAttack==self.DEFAULT:
                self.addBullet(rng.PurpleShot(pos[0], pos[1], angle, direction))
            elif self.currentAttack==self.BIGBALL:
                self.addBullet(rng.BigPurpleShot(pos[0], pos[1], angle, direction))
            elif self.currentAttack == self.BIGBALLBOUNCE and len(self.bullets) == 0:
                self.addBullet(rng.BigPurpleBounce(random.random()-.5 > 0))
            else:
                self.addBullet(rng.PurpleShot(pos[0], pos[1], angle, direction))
            
            if self.shotCount <= 0:
                self.chooseAttack(random.random())
        else:
            self.addBullet(rng.PurpleShot(pos[0], pos[1], angle, direction))
        
            
    def tick(self):
        self.timers()
        
        if self.shotTimer == 0:
            self.shotTimer = self.maxShotTimer
            return True # shoot a projectile
        else:
            self.shotTimer -= 1
            return False