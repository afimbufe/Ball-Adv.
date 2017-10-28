# -*- coding: utf-8 -*-
"""
Ball Adventures: basic structure for the projectiles shot

Created on Wed Jun 28 23:18:09 2017

@author: Alex
"""

import math
import pygame as py
import frameworks as fw

blue = (0,0,255)
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
lightred = (255, 100, 100)
yellow = (255, 255, 0)
lightyellow = (255, 255, 128)
purple = (255,0,255)
lightPurple = (255, 128, 255)

def getCircleInnerBox(x, y, radius):
    # get inner box around given circle, for purpose of collide detection
    const = 1.414212
    rect = py.Rect(math.ceil(x - radius/const), math.ceil(y - radius/const), \
                       math.floor(radius * const), math.floor(radius * const))
    return rect

def distance(pos1, pos2):
    return math.sqrt((pos1[0]-pos2[0]) ** 2 + (pos1[1]-pos2[1]) ** 2)

def getAngle(pos1, pos2):
    # Also returns whether pos1 is before pos2
    # TODO: Case where they have same y
    angle = math.atan((pos2[1]-pos1[1])/(pos2[0]-pos1[0]))
    if pos1[0] > pos2[0]:
        lr = 1
        
    elif pos1[0] == pos2[0]:
        lr = -1
        angle = -math.pi/2
    else: 
        lr = -1
    
    return (angle, lr)



class Bullet(fw.positionObj, fw.PhysicalTarget):
    def __init__(self, x, y, speed, angle, dmg, rightDir = True, mpCost = 0, playerShot = False):
        self.pos = (x,y)
        self.speed = speed
        self.angle = angle
        self.dmg = dmg
        self.rightDir = rightDir
        self.playerShot = playerShot
        self.throughWalls = False
        self.mpCost = mpCost
        self.isHoming = False
        self.dmgReduce = 0
        self.targetPos = (0, 0)
        self.endByContact = True
        fw.PhysicalTarget.__init__(self)
    
    def negate(self):
        self.dmg = 0
    
    def endsOnContact(self):
        return self.endByContact
    
    def updateTargetPos(self, targetPos):
        self.targetPos = targetPos
        
    def canFollow(self):
        return self.isHoming
    
    def damageAmt(self):
        return self.dmg - self.dmgReduce
    
    def reduceDmg(self, amt):
        self.dmgReduce += amt
        return self.dmgReduce >= self.dmg
        
    def update(self, activeEnemies = []):
        x, y = self.pos
        dirFlag = -1
        if self.rightDir:
            dirFlag = 1
        x += self.speed * math.cos(self.angle) * dirFlag
        y -= self.speed * math.sin(self.angle)
        
        self.pos = (x, y)
        
        if x < 10 or y <= 10 or x > 790 or y > 600:
            return False
        
        return True
    
    def getMPCost(self):
        return self.mpCost
    
    def setMPCost(self, cost):
        self.mpCost = cost
    
    def getHitBox(self):
        #print("Needs to be implemented in child classes")
        return getCircleInnerBox(self.pos[0], self.pos[1], 10)
    
    def draw(self, display):
        print("Needs to be implemented in child classes")
        py.draw.circle(display, black, self.getApproxPos(), 3, 0)
    
    def explode(self):
        # plays the explosion animation
        print("Needs to be implemented in child classes")
    
class arcBullet(Bullet):
    pass

# level of bullet strength
class basicShot(Bullet):
    def __init__(self, x, y, angle, rightDir, playerShot, dmgInc = 0):
        speed = 25
        dmg = 2 + dmgInc
        mpCost = 2
        Bullet.__init__(self, x, y, speed, angle, dmg, rightDir, mpCost, playerShot)
        self.radius = 10
        
    def getHitBox(self):
        return getCircleInnerBox(self.pos[0], self.pos[1], self.radius)
    
    def draw(self, display):
        py.draw.circle(display, black, self.getApproxPos(), self.radius, 0)


class Rocket(Bullet):
    def __init__(self, x, y, angle, rightDir, playerShot, dmgInc = 0):
        speed = 35
        dmg = 8 + dmgInc
        mpCost = 5
        width = 40
        height = 15
        Bullet.__init__(self, x, y, speed, angle, dmg, rightDir, mpCost, playerShot)
        self.image = py.Surface((width , height), py.SRCALPHA)
        self.image.fill((255, 0, 0))
        self.rotatedImage = self.image
        
    #def getHitBox(self):
    #    pass
    
    def draw(self, display):
        #py.draw.rect(display, red, py.Rect(x, y, width, height))
        
        angl = self.angle * 180 / math.pi
        if not self.rightDir:
            angl *= -1
        
        self.rotatedImage = py.transform.rotate(self.image, angl)
        rect = self.rotatedImage.get_rect(center = self.pos)
        
        display.blit(self.rotatedImage, (rect.x, rect.y))
        #py.draw.rect(display, green, self.getHitBox())

class HomingRocket(Bullet):
    def __init__(self, x, y, angle, rightDir, playerShot, dmgInc = 0):
        speed = 20
        dmg = 6 + dmgInc
        mpCost = 5
        width = 40
        height = 15
        Bullet.__init__(self, x, y, speed, angle, dmg, rightDir, mpCost, playerShot)
        self.image = py.Surface((width , height), py.SRCALPHA)
        self.image.fill((255, 0, 0))
        self.rotatedImage = self.image
        self.isHoming = True
        self.maxRotation = math.pi/3
        self.originalAngle = angle
        self.rotationSpeed = 20 * math.pi/180 # per frame
    
    def update(self, activeEnemies = []):
        x, y = self.pos
        dirFlag = -1
        if self.rightDir:
            dirFlag = 1
        # find angle by scouting all enemies and their angle
        enemyLock = None
        shortestDist = -1
        currentAngle = self.angle
        for enemy in activeEnemies:
            tempAngle, adjust = getAngle(self.pos, enemy.getPos())
            tempAngle *= adjust
            if abs(tempAngle - self.originalAngle) <= self.maxRotation and -dirFlag/adjust > 0:
                dist = distance(self.pos, enemy.getPos())
                if not enemyLock:
                    enemyLock = enemy
                    shortestDist = dist
                    currentAngle = tempAngle
                elif dist < shortestDist:
                    enemyLock = enemy
                    shortestDist = dist
                    currentAngle = tempAngle
        
        if not currentAngle == self.angle:
            if abs(self.angle - currentAngle) <= self.rotationSpeed:
                self.angle = currentAngle
            else:
                if self.angle < currentAngle:
                    self.angle += self.rotationSpeed
                else:
                    self.angle -= self.rotationSpeed
        
        x += self.speed * math.cos(self.angle) * dirFlag
        y -= self.speed * math.sin(self.angle)
        self.pos = (x, y)
        
        if x < 10 or y <= 10 or x > 790 or y > 600:
            return False
        
        return True
    
    #def getHitBox(self):
    #    pass
    
    def draw(self, display):
        #py.draw.rect(display, red, py.Rect(x, y, width, height))
        
        angl = self.angle * 180 / math.pi
        if not self.rightDir:
            angl *= -1
        
        self.rotatedImage = py.transform.rotate(self.image, angl)
        rect = self.rotatedImage.get_rect(center = self.pos)
        
        display.blit(self.rotatedImage, (rect.x, rect.y))
        py.draw.rect(display, green, self.getHitBox())


class BigRocket(Bullet):
    def __init__(self, x, y, angle, rightDir, playerShot, dmgInc = 0):
        speed = 55
        dmg = 60 + dmgInc
        mpCost = 33
        width = 70
        height = 40
        Bullet.__init__(self, x, y, speed, angle, dmg, rightDir, mpCost, playerShot)
        self.image = py.Surface((width , height), py.SRCALPHA)
        self.image.fill((255, 0, 0))
        self.rotatedImage = self.image
        
    def getHitBox(self):
        return self.rotatedImage.get_rect(center=self.pos)
    
    def draw(self, display):
        angl = self.angle * 180 / math.pi
        if not self.rightDir:
            angl *= -1
        
        self.rotatedImage = py.transform.rotate(self.image, angl)
        rect = self.rotatedImage.get_rect(center = self.pos)
        
        display.blit(self.rotatedImage, (rect.x, rect.y))


class Arrow(Bullet):
    def __init__(self, x, y, angle, rightDir, playerShot, dmgInc = 0):
        speed = 27
        dmg = 6 + dmgInc
        mpCost = 4
        width = 40
        height = 20
        Bullet.__init__(self, x, y, speed, angle, dmg, rightDir, mpCost, playerShot)
        self.image = py.Surface((width , height), py.SRCALPHA)
        self.image.fill(black)
        self.rotatedImage = self.image
        
    #def getHitBox(self):
    #    pass
    
    def draw(self, display):
        #py.draw.rect(display, red, py.Rect(x, y, width, height))
        
        angl = self.angle * 180 / math.pi
        if not self.rightDir:
            angl *= -1
        
        self.rotatedImage = py.transform.rotate(self.image, angl)
        rect = self.rotatedImage.get_rect(center = self.pos)
        
        display.blit(self.rotatedImage, (rect.x, rect.y))
        #py.draw.rect(display, green, self.getHitBox())

class SmallLaser(Bullet):
    def __init__(self, x, y, angle, rightDir, playerShot, dmgInc = 0):
        speed = 40
        dmg = 5 + dmgInc
        mpCost = 3
        width = 100
        height = 7
        Bullet.__init__(self, x, y, speed, angle, dmg, rightDir, mpCost, playerShot)
        self.image = py.Surface((width , height), py.SRCALPHA)
        self.image.fill(black)
        py.draw.rect(self.image, yellow, (0, 1, width, height-2))
        self.rotatedImage = self.image
        
    #def getHitBox(self):
    #    pass
    
    def draw(self, display):
        #py.draw.rect(display, red, py.Rect(x, y, width, height))
        
        angl = self.angle * 180 / math.pi
        if not self.rightDir:
            angl *= -1
        
        self.rotatedImage = py.transform.rotate(self.image, angl)
        rect = self.rotatedImage.get_rect(center = self.pos)
        
        display.blit(self.rotatedImage, (rect.x, rect.y))
        #py.draw.rect(display, green, self.getHitBox())


    
class greenBasicShot(Bullet):
    def __init__(self, x, y, angle, rightDir):
        speed = 25
        dmg = 3
        Bullet.__init__(self, x, y, speed, angle, dmg, rightDir)
        self.radius = 15
        
    def getHitBox(self):
        return getCircleInnerBox(self.pos[0], self.pos[1], self.radius)
    
    def draw(self, display):
        py.draw.circle(display, green, self.getApproxPos(), self.radius, 0)
        py.draw.circle(display, black, self.getApproxPos(), self.radius, 1) # Outline
        
                      
class Fireball(Bullet):
    def __init__(self, x, y, angle, rightDir):
        speed = 30
        dmg = 9
        Bullet.__init__(self, x, y, speed, angle, dmg, rightDir)
        self.radius = 13
        
    def getHitBox(self):
        return getCircleInnerBox(self.pos[0], self.pos[1], self.radius)
    
    def draw(self, display):
        py.draw.circle(display, red, self.getApproxPos(), self.radius, 0)
        py.draw.circle(display, black, self.getApproxPos(), self.radius, 3) 
        
        
class LightPillar(Bullet):
    def __init__(self, centerx, angle = math.pi/2):
        dmg = 12
        Bullet.__init__(self, centerx, 0, 0, angle, dmg)
        self.endByContact = False
        
        self.width = 1
        self.widthInc = 6
        self.maxWidth = 45
        
        self.height = 5
        self.heightInc = 40
        self.maxHeight = 600
        self.timer = 20
        
        self.rect = py.Rect(self.getX() - self.width, 0, self.width*2, self.height)
        
    def getHitBox(self):
        return self.rect
    
    def draw(self, display):
        width = self.width + 6 # outline
        py.draw.rect(display, lightyellow, py.Rect(self.getX() - width, 0, width*2, self.height))
        width = self.width + 1
        #py.draw.rect(display, black, py.Rect(self.getX() - width, 0, width*2, self.height))
        py.draw.rect(display, yellow, self.rect)
        
        
    def update(self,activeEnemies = []):
        
        if self.height < self.maxHeight:
            self.height = min(self.height + self.heightInc, self.maxHeight)
        else:
            self.timer -= 1
            self.width = min(self.width + self.widthInc, self.maxWidth)
        
        self.rect = py.Rect(self.getX() - self.width, 0, self.width*2, self.height)
        return self.timer > 0
    
    def damageAmt(self):
        if self.width >= self.maxWidth:
            return self.dmg - self.dmgReduce
        else:
            return 0

        
class PurpleShot(Bullet):
    def __init__(self, x, y, angle, rightDir, maxRadius = 50, angleUpdate = True):
        speed = 30
        dmg = 16
        
        Bullet.__init__(self, x, y, speed, angle, dmg, rightDir)
        self.radius = 3
        self.maxRadius = maxRadius
        self.grow = 4
        self.angleUpdate = angleUpdate
        
    def damageAmt(self):
        if self.isFullyGrown():
            return self.dmg - self.dmgReduce
        else:
            return 0
        
    def getHitBox(self):
        return getCircleInnerBox(self.pos[0], self.pos[1], self.radius)
    
    def draw(self, display):
        py.draw.circle(display, lightPurple, self.getApproxPos(), self.radius, 0)
        py.draw.circle(display, black, self.getApproxPos(), self.radius, 2)

    def updateAngle(self, targetPos):
        if self.angleUpdate:
            self.targetPos = targetPos
            if self.getX() - targetPos[0] == 0:
                self.angle = -math.pi/2    
            else:
                self.angle = math.atan(-(self.getY() - targetPos[1])/(self.getX() - targetPos[0]))
                if self.getX() > targetPos[0]:
                    self.angle *= -1
            self.rightDir = self.getX() < targetPos[0]

    def isFullyGrown(self):
        return self.radius >= self.maxRadius 

    def update(self):
        if self.radius < self.maxRadius:
            self.radius += self.grow
            return True
        else:
            return Bullet.update(self)

class BigPurpleShot(PurpleShot):
    def __init__(self, x, y, angle, rightDir, angleUpdate = True):
        PurpleShot.__init__(self, x, y, angle, rightDir, 120, angleUpdate)
        self.dmg = 20
        self.speed = 20

class BigPurpleBounce(BigPurpleShot):
    def __init__(self, rightDir):
        y = 600 - 80
        if rightDir:
            x = 100
        else:
            x = 700
        PurpleShot.__init__(self, x, y, 0, rightDir, 120, False)
        self.dmg = 20
        self.timer = 200
        self.endByContact = False
        self.speed = 20
        self.maxRadius = 80
        
    def update(self, activeEnemies = []):
        norm = PurpleShot.update(self)
        print("Angle", self.angle)
        self.timer -= 1
        if self.rightDir and self.getX() >= 800-self.radius/2 or not self.rightDir and self.getX() <= self.radius/2:
            self.rightDir = not self.rightDir
        if self.timer <= 0:
            return False
        else:
            return norm
            
        
        

class LightArrow(Bullet):
    def __init__(self, x, y, angle, rightDir):
        speed = 27
        dmg = 7
        width = 40
        height = 20
        Bullet.__init__(self, x, y, speed, angle, dmg, rightDir)
        self.image = py.Surface((width , height), py.SRCALPHA)
        self.image.fill(yellow)
        self.rotatedImage = self.image
        
    #def getHitBox(self):
    #    pass
    
    def draw(self, display):
        angl = self.angle * 180 / math.pi
        if not self.rightDir:
            angl *= -1
        
        self.rotatedImage = py.transform.rotate(self.image, angl)
        rect = self.rotatedImage.get_rect(center = self.pos)
        
        display.blit(self.rotatedImage, (rect.x, rect.y))



class PhysicalAttack(fw.positionObj):
    def __init__(self, user, dmg, mpCost, timeLength):
        self.user = user
        self.direction = user.isFacingRight()
        self.dmg = dmg
        self.mpCost = mpCost
        self.timeLength = timeLength
        
    def update(self):
        pass
    
    def getHitBox(self):
        pass

    def draw(self):
        pass
    
    def damageAmt(self):
        return self.dmg
    
    def getMPCost(self):
        return self.mpCost
    
    def setMPCost(self, amt):
        self.mpCost = amt

    def collide(self, obj):
        pass
    

class BasicHit(PhysicalAttack):
    def __init__(self, user):
        mpCost = 2
        dmg = 4
        timeLength = 4
        
        PhysicalAttack.__init__(self, user, dmg, mpCost, timeLength)
        self.width = 70 # square for now
        self.speed = 20
        self.length = -self.speed + 5
        x, y = self.user.getApproxPos()
        r = self.user.getRadius()
        if self.direction:
            self.pos = (x + r  + self.length, y - self.width/2)
        else:
            self.pos = (x - r - self.length - self.width, y - self.width/2)
            self.speed *= -1

        self.surface = py.Surface((self.width, self.width))            
        self.surface.fill(black)

    def collide(self, otherBox):
        rect = py.Rect(self.pos[0], self.pos[1], self.width, self.width)
        return rect.colliderect(otherBox)
            

    def getHitBox(self):
        return py.Rect(self.pos[0], self.pos[1], self.width, self.width)
    
    def draw(self, display):
        display.blit(self.surface, self.pos)

    def update(self):
        if self.timeLength == 0:
            return False
        else:
            self.timeLength -= 1
            
            r = self.user.getRadius()
            x, y = self.user.getApproxPos()
            if self.direction:
                self.length += self.speed
                self.pos = (x + r  + self.length, y - self.width/2)
            else:
                self.length -= self.speed
                self.pos = (x - r - self.length - self.width, y - self.width/2)
            return True
         
class FireCharge(PhysicalAttack):
    def __init__(self, user):
        mpCost = 6
        dmg = 12
        timeLength = 10
        
        PhysicalAttack.__init__(self, user, dmg, mpCost, timeLength)
        self.radiusExtra = 10 # square for now
        self.speed = 30
        x, y = self.user.getApproxPos()
        r = self.user.getRadius()
        
        self.radius = self.radiusExtra + r
        self.pos = (x - self.radius, y - self.radius)

        self.surface = py.Surface((self.radius * 2, self.radius * 2))            
        self.surface.set_alpha(128)
        self.surface.set_colorkey((0, 255, 255))
        
    def collide(self, otherBox):
        rect = self.user.getOuterBox()
        return rect.colliderect(otherBox)
            
    def getHitBox(self):
        return self.user.getOuterBox()
    
    def draw(self, display):
        self.surface.fill((0, 255, 255))
        py.draw.circle(self.surface, red, (self.radius, self.radius), self.radius, 0)
        display.blit(self.surface, self.pos)

    def update(self):
        if self.timeLength == 0:
            self.user.setFireCharge(False)
            return False
        else:
            self.timeLength -= 1
            
            self.user.setFireCharge(True)
            multiple = 1
            if not self.direction:
                multiple = -1
            self.user.shiftX(self.speed * multiple)
            
            x, y = self.user.getApproxPos()
            self.pos = (x - self.radius, y - self.radius)
            return True
            
class ScreenBomb(fw.positionObj):
    def __init__(self, x, y, dmgInc = 0):
        self.pos = (x,y)
        self.growth = 25
        self.dmg = 15  + dmgInc
        self.mpCost = 8
        self.radius = 5
    
    def damageAmt(self):
        return self.dmg
            
    def update(self):
        self.radius += self.growth
        return True
    
    def getMPCost(self):
        return self.mpCost
    
    def setMPCost(self, cost):
        self.mpCost = cost
    
    def getHitBox(self):
        return getCircleInnerBox(self.pos[0], self.pos[1], self.radius)

    def getRadius(self):
        return self.radius
        
    def draw(self, display):
        x = self.getApproxPos()[0]
        y = self.getApproxPos()[1]
        bombSurface = py.Surface((self.radius*2, self.radius*2))
        bombSurface.fill(blue)
        bombSurface.set_colorkey(blue)
        bombSurface.set_alpha(150)
        py.draw.circle(bombSurface, lightred, (self.radius, self.radius), self.radius, 0)
        py.draw.circle(bombSurface, black, (self.radius, self.radius), self.radius, 2)
        if self.radius > 200:
            py.draw.circle(bombSurface, red, (self.radius, self.radius), self.radius - 200, 0)
            py.draw.circle(bombSurface, black, (self.radius, self.radius), self.radius - 200, 2)
        
        display.blit(bombSurface, (x - self.radius, y - self.radius))