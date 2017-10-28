# -*- coding: utf-8 -*-
"""
Ball Adventures: basic structure for the ball units
    
Created on Tue Jun 27 21:03:03 2017

@author: Alex
"""

import Projectile as rng
import math
import pygame as py
import frameworks as fw
import random

# Useful Constants
screenSize = (800, 600)
blue = (0,0,255)
white = (255,255,255)
black = (0,0,0)
grey = (128,128,128)
red = (255,0,0)
green = (0,255,0)
yellow = (255,255,0)
lightred = (255, 100, 100)
purple = (255,0,255)

RANGE = 0
PHYS = 1
SPECIAL = 2

BASICSHOT = 0
ROCKET = 1
MULTIARROW = 2
LASER = 3
RAPIDFIRE = 4
ROCKETBOUNCE = 5
HOMINGROCKET = 6
BIGROCKET = 7
# Arc?

SCREENBOMB = 0
HEAL = 1          # Must take damage to use it again
DEFENSE = 2
SLOW = 3
FLOAT = 4
BIGLASER = 5      # Must be in battle
BIGSCREENBOMB = 6 # Must take damage to use it again
METEOR = 7

BASICHIT = 0
SWORD = 1
SPIKE = 2
FIRECHARGE = 3

'''
Passive:
Increase HP, MP
Sprint
Triple Jump
HP Regen (75% Healable)
Increase Damage
HP/MP Regen Speed
Drain
Increase EXP Gain
Reduce Special Timer
Half MP Cost
'''


# --- helper functions ---

def setScreenSize(x, y):
    global screenSize
    screenSize = (x, y)

def getCircleInnerBox(x, y, radius):
    # get inner box around given circle, for purpose of collide detection
    const = 1.414212
    rect = py.Rect(math.ceil(x - radius/const), math.ceil(y - radius/const), \
                       math.floor(radius * const), math.floor(radius * const))
    return rect

def getCircleOuterBox(x, y, radius):
    # get outer box around a circle, for purpose of colliding
    rect = py.Rect(math.ceil(x - radius), math.ceil(y - radius), \
                       math.floor(radius * 2), math.floor(radius * 2))
    return rect

# --- Ball Classes ---

class AbstractBall(object):
    def __init__(self, startingHP, radius):
        self.maxHP = startingHP
        self.hp = startingHP
        self.radius = radius
        self.lv = 1
        self.lives = 3
        
    def getLv(self):
        return self.lv
    
    def setLv(self, newLv):
        self.lv = newLv

    def getHP(self):
        return self.hp

    def getMaxHP(self):
        return self.maxHP
        
    def setHP(self, newHP):
        self.hp = newHP
    
    def healHP(self, amt):
        self.hp = min(self.hp + amt, self.maxHP)
    
    def hurt(self, dmg):
        self.hp -= dmg
        self.hp = max(self.hp, 0)
        return self.hp > 0
        # returns false if ball dies
        
    def fullRestore(self):
        self.hp = self.maxHP
    
    def setRadius(self, amt):
        self.radius = amt
    
    def getRadius(self):
        return self.radius
    
    def getHitBox(self):
        print("To be implemented in children")
    
    def draw(self, display):
        print("To be implemented in children")
        py.draw.circle(display, black, (0, 0), 10, 0)
        
    def tick(self):
        print("To be implemented in children")
        
        
class AbstractPlayerBall(AbstractBall):
    #conceptual information on the ball, no skill based details
    def __init__(self, startingHP, startingMP, startingEXP, radius):    
        AbstractBall.__init__(self, startingHP, radius)
        self.maxMP = startingMP
        self.mp = startingMP
        self.exp = startingEXP
        
        self.activeSkills = [False, False, False]      
        # 0 index is close range attack, 1 is far range, 2 is special
        self.rangeSkills = []
        self.physSkills = []
        self.specialSkills = []
        self.skills = (self.rangeSkills, self.physSkills, self.specialSkills)
        self.passiveUpgrades = {}    # Should be a dictionary and True/False as value
        
    def setMP(self, newMP):
        self.mp = newMP
        
    def getMP(self):
        return self.mp
    
    def getMaxMP(self):
        return self.maxMP
    
    def regenMP(self, amt):
        self.mp = min(self.mp + amt, self.maxMP)
    
    def spendMP(self, amt):
        if self.mp - amt >= 0:
            self.mp -= amt
            return True
        else:
            return False
            
    def spendEXP(self, amt):
        if self.exp - amt >= 0:
            self.exp -= amt
            return True
        else:
            return False
    
    def gainEXP(self, amt):
        self.exp += amt
    
    def getEXP(self):
        return self.exp
    
    def getRangeSkill(self):
        return self.activeSkills[RANGE]
    
    def getPhysSkill(self):
        global PHYS
        return self.activeSkills[PHYS]
    
    def getSpecialSkill(self):
        return self.activeSkills[SPECIAL]
    
    def getAllSkills(self, skilltype):
        return self.skills[skilltype]
    
    def addSkill(self, skill, skillType):
        if skillType < len(self.skills) and skillType >= 0:
            self.skills[skillType].append(skill)
    
    def addPassive(self, passive):
        self.passiveUpgrades.append(passive)
    
    def replaceSkill(self, skill, skillType):
        # check if ball has skill in question, then replace it. For Equip
        success = False
        if skill in self.skills[skillType]:
            self.activeSkills[skillType] = skill
            return True        
        return success
        
    def setDefaultSkills(self, physSkill, rangeSkill, specialSkill):
        self.physSkills.append(physSkill)
        self.rangeSkills.append(rangeSkill)
        self.specialSkills.append(specialSkill)
        self.activeSkills[0] = physSkill
        self.activeSkills[1] = rangeSkill
        self.activeSkills[2] = specialSkill # None


class PlayerBall(AbstractPlayerBall, fw.positionObj):
    # More detailed information on the player's ball
    def __init__(self, startingHP, startingMP, startingEXP, radius, defaultSkills):
        AbstractPlayerBall.__init__(self, startingHP, startingMP, startingEXP, radius)
        # movement variables
        #self.jumpSpeed = 22
        self.jumpSpeed = 30
        self.yspeed = self.jumpSpeed
        #self.yaccel = -1.25
        self.yaccel = -1.75
        self.xspeed = 15
        self.sprintSpeed = 30
        self.pos = (0,0)
        self.radius = radius # Hitbox?
        self.scale = 1
        self.xInertia = 0
        self.inBattlePos = (100, 500)
        self.savePos = [(0, 0), False]
        
        # specialized variables
        self.groundedFlag = False
        self.onPlatform = False
        self.dmgFlag = False
        self.maxJumps = 2
        self.jumpTracker = 0
        self.canDblJump = True
        self.setDefaultSkills(BASICSHOT,None, None)
        self.rangeSkills.append(self.activeSkills[RANGE])
        self.sprintFlag = False
        self.canSprint = True
        self.faceRight = True
        self.bullets = []
        self.phys = None
        self.healableDmg = 0
        self.accumDmg = 0
        self.screenBomb = None
        self.damageInc = 0
        self.dmgRatio= 1
        self.fireCharge = False
        
        # Time tracking variables
        self.invincibilityFrames = 10
        self.invincibilityCounter = 0
        self.specialTimer = 0
        self.specialRechargeSecs = 15 * 12       
        self.hpRegenDelay = 15
        self.hpRegenCounter = 0
        self.mpRegenDelay = 10
        #self.mpRegenDelay = 4
        self.mpRegenCounter = 0
        self.hpToRegenerate = 0
        self.specialAttackTimer = 0
    
    def getPhys(self):
        return self.phys
    
    def isFireCharge(self):
        return self.fireCharge
    
    def setFireCharge(self, new):
        self.fireCharge = new
        if not self.fireCharge:
            temp = self.jumpTracker
            self.inAir()
            self.jumpTracker = temp
            self.yspeed = 0
        
    def setDmgRatio(self, pct):
        self.dmgRatio = pct
        
    def resetDmgRatio(self):
        self.dmgRatio = 1
    
    def getInBattlePos(self):
        return self.inBattlePos
      
    def setSprinting(self, ind):
        self.canSprint = ind
    
    def getHitBox(self):
        return getCircleInnerBox(self.pos[0], self.pos[1], self.radius)
        
    def getOuterBox(self):
        return getCircleOuterBox(self.pos[0], self.pos[1], self.radius)
    
    def savePosition(self, pos, grounded):
        self.savePos[0] = pos
        self.savePos[1] = grounded
    
    def getSavePos(self):
        return self.savePos
    
    def setScreenBomb(self, bomb):
        mpCost = bomb.getMPCost()
        if self.screenBomb == None and mpCost <= self.mp and self.specialTimer == 0:    
            self.specialTimer = self.specialRechargeSecs #* 24   
            self.screenBomb = bomb
            self.spendMP(mpCost) 
            
    def getScreenBomb(self):
        return self.screenBomb
    
    def removeScreenBomb(self):
        self.screenBomb = None
    
    def takeDamage(self, dmg):    
        if self.invincibilityCounter == 0 or dmg > self.accumDmg:
            netDmg = math.floor(dmg * self.dmgRatio) - self.accumDmg
            
            self.healableDmg += netDmg//2
            self.dmgFlag = True
            self.hpRegenCounter = self.hpRegenDelay
            # hurt animation
        
            self.invincibilityCounter = self.invincibilityFrames 
            
            alive = self.hurt(netDmg)
            self.accumDmg = math.floor(dmg * self.dmgRatio)
            
            if not alive:
                self.healableDmg = 0
        
            return alive
        else:
            return True
    
    def getInertia(self):
        return self.xInertia
    
    def setInertia(self, amt):
        self.xInertia = amt
    
    
    def shootBullet(self, angle, shootRight = True):
        # mp check
        if self.phys:
            return
        
        x, y = self.pos        
        bullets = []
        
        bulletCode = self.activeSkills[RANGE]
        if bulletCode == BASICSHOT:
            bullets.append(rng.basicShot(x, y, angle, shootRight, True, self.damageInc))
            bullets.append(rng.basicShot(x, y, angle + math.pi/12, shootRight, True, self.damageInc))
            bullets.append(rng.basicShot(x, y, angle - math.pi/12, shootRight, True, self.damageInc))
        elif bulletCode == ROCKET:
            bullets.append(rng.Rocket(x, y, angle, shootRight, True, self.damageInc))
        elif bulletCode == MULTIARROW:
            bullets.append(rng.Arrow(x, y, angle, shootRight, True, self.damageInc))
            bullets.append(rng.Arrow(x, y, angle + math.pi/12, shootRight, True, self.damageInc))
            bullets.append(rng.Arrow(x, y, angle - math.pi/12, shootRight, True, self.damageInc))
            bullets.append(rng.Arrow(x, y, angle + math.pi/6, shootRight, True, self.damageInc))
            bullets.append(rng.Arrow(x, y, angle - math.pi/6, shootRight, True, self.damageInc))
        elif bulletCode == HOMINGROCKET:
            bullets.append(rng.HomingRocket(x, y, angle, shootRight, True, self.damageInc))
        elif bulletCode == LASER:
            length = 24
            rightAngle = angle + math.pi/2
            xAdjust = abs(length/2 * math.cos(rightAngle))
            yAdjust = abs(length/2 * math.sin(rightAngle))
            
            if (angle < 0 and shootRight) or (angle > 0 and not shootRight):
                yAdjust *= -1  
            bullets.append(rng.SmallLaser(x - xAdjust, y - yAdjust, angle, shootRight, True, self.damageInc))
            bullets.append(rng.SmallLaser(x + xAdjust, y + yAdjust, angle, shootRight, True, self.damageInc))
        elif bulletCode == BIGROCKET:
            bullets.append(rng.BigRocket(x, y, angle, shootRight, True, self.damageInc))
        else:
            bullets.append(rng.basicShot(x, y, angle, shootRight, True, self.damageInc))
            bullets.append(rng.basicShot(x, y, angle + math.pi/12, shootRight, True, self.damageInc))
            bullets.append(rng.basicShot(x, y, angle - math.pi/12, shootRight, True, self.damageInc))
        '''
        elif bulletCode == RAPIDFIRE:
            pass
        elif bulletCode == ROCKETBOUNCE:
            pass
        
        '''  
        mpCost = bullets[0].getMPCost()
        if mpCost <= self.mp:
            self.addBullets(bullets)
            self.spendMP(mpCost)
        else:
            self.addBullet(rng.basicShot(x, y, angle, shootRight, True))
            #self.addBullet(rng.basicShot(x, y, angle + math.pi/12, shootRight, True))
            #self.addBullet(rng.basicShot(x, y, angle - math.pi/12, shootRight, True))
            # TODO: Sound effect (soft) for ERROR 
    
    def usePhysical(self):
        if not self.phys:
            physCode = self.activeSkills[PHYS]
            #if not physCode:
            #    return
            attack = None
            if physCode == BASICHIT:
                attack = rng.BasicHit(self)
            elif physCode == FIRECHARGE:
                attack = rng.FireCharge(self)
            if attack:
                mpCost = attack.getMPCost()
            else:
                mpCost = self.mp + 1
                
            if mpCost <= self.mp:
                self.phys = attack
                self.spendMP(mpCost)
            else:
                self.phys = rng.BasicHit(self)
        
    def endPhys(self):
        self.phys = None
    
    def specialAttack(self):
        specialAtk = self.activeSkills[SPECIAL]
        if specialAtk:
            if specialAtk == HEAL:
                healRatio = .4
                self.healHP(self.healableDmg)
                self.healableDmg = 0
                self.healHP(self.maxHP * healRatio)
                
                
    def getSpecialAtk(self):
        return self.activeSkills[SPECIAL]
    
    def setDamageInc(self, amt):
        self.damageInc = amt
    
    def addBullets(self, bulletList):
        for bullet in bulletList:
            self.addBullet(bullet)
        
    def tick(self):
        if self.healableDmg > 0:
            if self.hpRegenCounter <= 0:
                self.hpRegenCounter = self.hpRegenDelay
                self.healHP(1)
                self.healableDmg -= 1
            else:
                self.hpRegenCounter -= 1
        
        if self.mp < self.maxMP:
            if self.mpRegenCounter < 0:
                self.mpRegenCounter = self.mpRegenDelay
                self.regenMP(1)
            else:
                self.mpRegenCounter -= 1
        
        if self.invincibilityCounter > 0:
            self.invincibilityCounter -= 1
            if self.invincibilityCounter == 0:
                self.accumDmg = 0
            
        if self.specialTimer > 0:
            self.specialTimer -= 1
    
    def getSpecialSecs(self):
        return self.specialTimer//24
            
    def getHealableDmg(self):
        return self.healableDmg
    
    def reduceHealableDmg(self, amt):
        self.healableDmg = max(0, self.healableDmg - amt)
        
    def isInvincible(self):
        return self.invincibilityCounter == 0
    
    def changeDir(self, right):
        self.faceRight = right
        self.xInertia = 0
    
    def isFacingRight(self):
        return self.faceRight
        
    def sprint(self, toggle):
        if self.canSprint:
            self.sprintFlag = toggle

    def jump(self):
        if self.jumpTracker < self.maxJumps:
            self.yspeed = self.jumpSpeed
            self.jumpTracker += 1
            self.groundedFlag = False
            self.onPlatform = False
            
    def setYSpeed(self, amt):
        self.yspeed = amt

    def setXSpeed(self, amt):
        self.xspeed = amt

    def bounce(self):
        self.yspeed *= -1

    def isFalling(self):
        return self.yspeed <= 0 and not self.isGrounded()

    def hasDblJumped(self):
        return self.dblFlag
    
    def isGrounded(self):
        return self.groundedFlag

    def isOnPlatform(self):
        return self.onPlatform

    def touchGround(self, onPlatform = False):
        self.groundedFlag = True
        self.canDblJump = True
        self.jumpTracker = 0
        self.yspeed = 0
        if onPlatform:
            self.onPlatform = True
        
    def inAir(self):
        self.groundedFlag = False
        self.jumpTracker = 1
        self.onPlatform = False

    def fall(self):
        self.yspeed = 0
        self.groundedFlag = False
        self.onPlatform = False
        self.jumpTracker = 0
    
    def getApproxPos(self):
        return (math.floor(self.pos[0]), math.floor(self.pos[1]))
    
    # only relevant for the heal special attack
    def hasBeenDamaged(self):
        self.dmgFlag = True
    
    def resetDmgFlag(self):
        self.dmgFlag = False
    
    def getSpeeds(self):
        return (self.xspeed, self.yspeed)
    
    def getRadius(self):
        return self.radius
    
    def changeXSpeed(self, amt):
        self.xspeed = amt

    def updateFrame(self, xMultiple):
        if self.pos[1] > screenSize[1] - self.radius and not self.isGrounded(): # or land on a platform
            self.touchGround()
            self.setPos(self.pos[0], screenSize[1] - self.radius)
        elif not self.isGrounded():
            if not self.fireCharge:
                tempY = self.pos[1] - self.yspeed  
                self.yspeed += self.yaccel
                self.yspeed = max(self.yspeed, -2 * self.radius)
                self.setY(tempY)
                
        if self.sprintFlag:
            tempX = self.pos[0] + self.sprintSpeed * xMultiple
        else: 
            tempX = self.pos[0] + self.xspeed * xMultiple
        self.setPos(tempX, self.pos[1])
        if self.pos[0] > screenSize[0] - self.radius:
            self.setPos(screenSize[0] - self.radius, self.pos[1])
        if self.pos[0] < self.radius:
            self.setPos(self.radius, self.pos[1])
            
        self.tick()
        
    def getBullets(self):
        return self.bullets
    
    def addBullet(self, bullet):
        self.bullets.append(bullet)

    def removeBullet(self, bullet):
        self.bullets.remove(bullet)
        # animation
    
    def removeInvincibility(self):
        self.invincibilityCounter = 0
    
    def clearBullets(self):
        self.bullets = []
    
    def death(self):
        pass
    
    def draw(self, display):
        if self.invincibilityCounter > 0:
            if self.invincibilityCounter % 6 == 0 or self.invincibilityCounter % 6 == 1  or self.invincibilityCounter % 6 == 2:
                py.draw.circle(display, lightred, self.getApproxPos(), self.radius, 0)
            else:
                py.draw.circle(display, blue, self.getApproxPos(), self.radius, 0)
        else:
            py.draw.circle(display, blue, self.getApproxPos(), self.radius, 0)
    
    '''
    colour? image?
    
    
    '''

class AbstractEnemyBall(AbstractBall, fw.positionObj, fw.PhysicalTarget):
    def __init__(self, name, startingHP, radius, xspeed, expPrize):    
        AbstractBall.__init__(self, startingHP, radius)
        fw.PhysicalTarget.__init__(self)
        self.name = name
        self.lv = 1
        
        # Stats
        self.collideDmg = 0
        self.inBattleHP = math.floor(self.hp/2)
        self.expPrize = expPrize
        
        # Movement and Position Variables
        self.xspeed = xspeed
        self.yspeed = 0
        self.xaccel = 0
        self.yaccel = 0
        self.flight = False
        self.pos = (0,0)
        self.scale = 1
        self.inBattlePos = (450, 450)
        self.playerPos = (0, 0)
        self.jumpspeed = 0
        
        # Other Attributes
        self.bullets = []
        self.patterns = []
        self.inBattle = False
        self.healablePct = 0.5 # change to 0 if not healable 
        self.healableDmg = 0
        
        # Timer Variables
        self.moveTimer = 0
        self.invincibilityFrames = 3
        self.invincibilityCounter = 0
        self.hpRegenDelay = 30
        self.hpRegenCounter = 0
        self.healthBarTime = 48
        self.healthBarCount = 0
        self.shotTimer = 0
        
    def getHealthBarCount(self):
        return self.healthBarCount
    
    def clearBullets(self):
        self.bullets = []
    
    def getInBattlePos(self):
        return self.inBattlePos
        
    def setInBattlePos(self, pos):
        self.inBattlePos = pos
    
    
    def takeDamage(self, dmg):
        if self.invincibilityCounter == 0:
            self.healableDmg += math.floor(dmg*self.healablePct)
            self.dmgFlag = True
            self.hpRegenCounter = self.hpRegenDelay
            self.healthBarCount = self.healthBarTime
            # hurt animation
        
            self.invincibilityCounter = self.invincibilityFrames 
        
            alive = self.hurt(dmg)
        
            if not alive:
                self.healableDmg = 0
        
            return alive
        else:
            return True
    
    def getHealableDmg(self):
        return self.healableDmg
    
    def reduceHealableDmg(self, amt):
        self.healableDmg = max(0, self.healableDmg - amt)
    
    def updateInBattleHP(self):
        self.hp += self.healableDmg
        self.healableDmg = 0
        self.hp = max(math.ceil(self.maxHP/2), self.hp)
        self.hp *= 2
        self.maxHP *= 2
        self.inBattleHP = self.hp
        
    def reverseInBattleHP(self):
        # Called when loses in battle hp
        self.hp = math.ceil(self.hp / 2)
        self.maxHP = math.ceil(self.maxHP / 2)
        
    def getSlamDmg(self):
        return self.collideDmg
    
    def getHitBox(self):
        return getCircleInnerBox(self.pos[0], self.pos[1], self.radius)
        
    def getOuterBox(self):
        return getCircleOuterBox(self.pos[0], self.pos[1], self.radius)
    
    def draw(self):
        print("Needs to be implemented in child classes")
    
    def isFloating(self):
        return self.flight
    
    def isFalling(self):
        return self.yspeed < 0
    
    def timers(self):
        if self.healableDmg > 0:
            #print("Timing")
            if self.hpRegenCounter <= 0:
                self.hpRegenCounter = self.hpRegenDelay
                self.healHP(1)
                self.healableDmg -= 1
            else:
                self.hpRegenCounter -= 1
        
        if self.invincibilityCounter > 0:
            self.invincibilityCounter -= 1
    
        if self.healthBarCount > 0:
            self.healthBarCount -= 1
        
        
    def isInBattle(self):
        return self.inBattle
    
    def inBattleState(self, newState):
        self.inBattle = newState
        if self.inBattle:
            self.inBattleHP = max(self.inBattleHP, self.hp)
            self.hp = self.inBattleHP

    def changeXSpeed(self, amt):
        self.xspeed = amt
        
    def changeYSpeed(self, amt):
        self.yspeed = amt
        
    def changeYAccel(self, amt):
        self.yaccel = amt
    
    def bounce(self):
        self.yspeed *= -1
    
    def addBullet(self, bullet):
        self.bullets.append(bullet)
        
    def getBullets(self):
        return self.bullets

    def removeBullet(self, bullet):
        self.bullets.remove(bullet)
        # animation
        
    def showHPBar(self):
        return self.healthBarCount > 0 and not self.inBattle
    
    def getEXPPrize(self):
        exp = self.expPrize
        if self.inBattle:
            exp = math.floor(exp * 3 * self.inBattleHP / self.maxHP)
        return exp
    
    def getName(self):
        return self.name
    
    def getLv(self):
        return self.lv
    
    def updatePlayerPos(self, newPos):
        self.playerPos = newPos
    
    def shootAt(self, pPos = [-1, -1]):
        playerPt = pPos
        if playerPt == [-1, -1]:
            playerPt = self.playerPos
        else:
            self.updatePlayerPos(pPos)
        if self.pos[0] - playerPt[0] == 0:
            angle = -math.pi/2
        else:
            if self.pos[0] - playerPt[0] == 0:
                angle = -math.pi/2
            else:
                angle = math.atan(-(self.pos[1] - playerPt[1])/(self.pos[0] - playerPt[0]))

        if self.pos[0] < playerPt[0]:
            angle *= -1
        angle += math.pi
        
        self.shoot(angle, self.pos[0] > playerPt[0])
    
    def updateFrame(self, groundY = 0):
        print("To be implemented in child class")
    
    def shoot(self, angle, direction = 0):
        print("To be implemented in child class")
    
    '''
    another inheritance for each race
        AI Attack pattern goes here
    '''
    

    
class GroundedBall(AbstractEnemyBall):
    def __init__(self, name, startingHP, radius, xspeed, expPrize, jumpspeed, yaccel, bouncy):
        AbstractEnemyBall.__init__(self, name, startingHP, radius, xspeed, expPrize)
        self.jumpspeed = jumpspeed
        self.bouncy = bouncy
        self.yaccel = yaccel
        self.groundedFlag = False
        self.collideDmg = 5
        
        
    def jump(self):
        self.yspeed = self.jumpspeed
        self.groundedFlag = False
        
    def isBouncy(self):
        return self.bouncy

    def isGrounded(self):
        return self.groundedFlag

    def touchGround(self):
        self.groundedFlag = True
         

class FloatingBall(AbstractEnemyBall):
    # Fluctuates like a metronome, doesn't operate off of yspeed and yaccel
    def __init__(self, name, startingHP, radius, xspeed, expPrize, amplitude, frequency):
        AbstractEnemyBall.__init__(self, name, startingHP, radius, xspeed, expPrize)
        self.baseLineY = 0
        self.flight = True
        self.collideDmg = 5
        self.angle = 0
        self.amplitude = amplitude
        self.frequency = frequency
        self.yTarget = self.baseLineY
        self.xTarget = self.getX()
        self.inPlace = False

    def updateAngle(self):
        self.angle += self.frequency

    def shiftBaseLineY(self, amt):
        self.baseLineY += amt
        
    def updateY(self):
        if not self.inPlace:
            self.setY(math.sin(self.angle) * self.amplitude + self.baseLineY)

    def setPos2(self,pos):
        self.pos = pos
        self.baseLineY = pos[1]
        






        
    

