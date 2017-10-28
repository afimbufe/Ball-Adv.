# -*- coding: utf-8 -*-
"""
Ball Adventures Useful Constants

Created on Sat Jul  8 21:11:41 2017

@author: Alex
"""

import math
import pygame as py


class positionObj(object):
    def __init__(self, x=0, y=0):
        self.pos = (x, y)

    def getPos(self):
        return self.pos
    
    def getX(self):
        return self.pos[0]
    
    def getY(self):
        return self.pos[1]
    
    def setX(self, amt):
        self.pos = (amt, self.pos[1]) 
    
    def setY(self, amt):
        self.pos = (self.pos[0], amt)
    
    
    def setPos(self, x, y):
        self.pos = (x, y)
        
    def setPos2(self, pos):
        self.pos = pos
        
    def getApproxPos(self):
        return (math.floor(self.pos[0]), math.floor(self.pos[1]))    
        
    def shiftPos(self, xShift, yShift):
        x = self.pos[0]
        y = self.pos[1]
        x += xShift
        y += yShift
        self.pos = (x, y)
        
    def shiftX(self, xShift):
        x = self.pos[0]
        x += xShift
        self.pos = (x, self.pos[1])
        
    def shiftY(self, yShift):
        y = self.pos[1]
        y += yShift
        self.pos = (self.pos[0], y)


class PhysicalTarget(object):
    # Can only be damaged by a physical attack once in one strike
    def __init__(self):
        self.canBeHit = True
        
    def gotHit(self):
        self.canBeHit = False
        
    def isVulnerable(self):
        return self.canBeHit
        
    def physEnd(self):
        self.canBeHit = True



class Animations(object):
    def __init__(self):
        self.animationList = []
        self.paused = False
    
    def addAnimation(self, animation):
        self.animationList.append(animation)
        self.checkTimeStop()

    def removeAnimation(self, animation):
        self.animationList.remove(animation)
        self.checkTimeStop()

    def checkTimeStop(self):
        # Check every time an animation is added or removed
        self.paused = False
        for animation in self.animationList:
            self.paused = self.paused or animation.stopsTime()

    def pausesGame(self):
        return self.paused

    def updateAnimations(self):
        for animation in self.animationList:
            active = animation.tick()
            if not active:
                self.removeAnimation(animation)
    
    def drawAnimations(self, display):
        for animation in self.animationList:
            animation.draw(display)

    def shift(self, x, y):
        for animation in self.animationList:
            if not animation.isInPlace():
                animation.shiftPos(x, y)


class Animation(positionObj):
    # Just for aesthetic purposes
    
    def __init__(self, pos, timeStop = False, frameDelay = 0, length = -1):
        self.inProgress = True
        self.paused = False
        self.frameDelay = frameDelay
        self.timer = 0
        self.timeStop = timeStop
        self.pos = pos
        self.length = length
        self.inPlace = False
    
    def isInPlace(self):
        return self.inPlace
    
    def nextFrame(self):
        # TODO: Boolean to indicate whether its the last frame, False if it is
        pass
    
    def tick(self):
        if self.length > 0:
            self.length -= 1
            if self.length == 0:
                self.inProgress = False
                return self.inProgress   
        if self.timer == 0 and not self.frameDelay == 0:
            self.timer = self.frameDelay
            return True
        elif self.timer > 0 and not self.frameDelay == 0:
            self.timer -= 1
            return self.nextFrame()   
        else:
           return self.nextFrame()  
            
    def stopsTime(self):
        return self.timeStop
    
    def draw(self, display):
        print("To be implemented")
    
    def getRect(self):
        print("To be implemented")
    
    def isInProgress(self):
        return self.inProgress
    
    
class PyAnimation(Animation):
    def __init__(self, pos, timeStop = False, frameDelay = 0, length = -1):
        Animation.__init__(self, pos, timeStop, frameDelay, length)
        

class ImgAnimation(Animation):
    def __init__(self, pos, timeStop = False, frameDelay = 0):
        Animation.__init__(self, pos, timeStop, frameDelay)
        self.imageList = []
        self.currentIndex = 0
    
    def nextFrame(self):
        if self.currentIndex >= len(self.imageList) - 1:
            self.inProgress = False
        else:
            self.currentIndex += 1
        return self.inProgress
    
    def addImages(self, moreImages):
        self.imageList.extend(moreImages)
    
    def draw(self, display):
        display.blit(self.imageList[self.currentIndex], self.pos)
    
    
    # getRect

class FadeOut(PyAnimation):
    def __init__(self, surface, pos, length = -1, startingAlpha = 255, timeStop = False, frameDelay = 0):
        PyAnimation.__init__(self, pos, timeStop, frameDelay, length)
        self.surface = surface
        self.alpha = startingAlpha
        self.isFading = True
        if length > 0:
            self.alphaChange = self.alpha / length
        else:
            self.alphaChange = 1
    
    def setAlphaChange(self, amt):
        if amt > 0:
            self.alphaChange = amt
    
    def draw(self, display):
        display.blit(self.surface, self.pos)
        
    def nextFrame(self):
        if (self.isFading):
            self.alpha -= self.alphaChange
            self.surface.set_alpha(max(0, math.floor(self.alpha)))
            self.inProgress = self.alpha > 0
            return self.inProgress
        else:
            return True

class ShowEXP(PyAnimation):
    def __init__(self, exp, pos, timeStop = False, duration = 50):
        Animation.__init__(self, pos, timeStop, length = duration)
        self.height = 0
        self.yIncrease = 3
        self.fontSize = 40
        self.font = py.font.SysFont('Ariel MS', self.fontSize)
        self.text = "+ " + str(exp) + " EXP"
        self.surface = self.font.render(self.text, False, (0, 200, 0))
        
    def draw(self, display):
        x = self.getApproxPos()[0]
        y = self.getApproxPos()[1] + self.height
        display.blit(self.surface, (x, y))

    def nextFrame(self):
        self.height -= self.yIncrease
        return self.inProgress


class ObjAnimation(Animation):
    # Animation position moves with another object that has a position attribute
    def __init__(self, obj, relativePos, timeStop = False, frameDelay = 0):
        x, y = obj.getPos()
        xChange, yChange = relativePos
        Animation.__init__(self, (x+xChange, y+yChange), timeStop, frameDelay)
        self.obj = obj
        self.relativePos = relativePos
        
    def nextFrame(self):
        x, y = self.obj.getPos()
        xChange, yChange = self.relativePos
        self.pos = (x+xChange, y+yChange)
        return self.inProgress
    
class MovingFade(ObjAnimation, FadeOut):
    def __init__(self, surface, obj, currentPos, length = -1, startingAlpha = 255, timeStop = False, frameDelay = 0):   
        objX, objY = obj.getPos()
        thisX, thisY = currentPos
        ObjAnimation.__init__(self, obj, (thisX - objX, thisY - objY), timeStop, frameDelay)
        FadeOut.__init__(self, surface, currentPos, length, startingAlpha, timeStop, frameDelay)
        
    def nextFrame(self):
        A = ObjAnimation.nextFrame(self)
        B = FadeOut.nextFrame(self)
        return A and B
    
    #def tick(self):
    #    return FadeOut.tick(self)
    
class Spotlight(FadeOut):
    def __init__(self, pos):
        surface = py.Surface((800,600))
        FadeOut.__init__(self, surface, pos)
        self.surface.set_colorkey((0, 255, 255))
        self.isFading = False
        self.fadeLength = 4
        self.timeStop = True
        self.radius = 500
        self.radiusChange = 40
        
    def draw(self, display):
        display.blit(self.surface, (0, 0))
        
    def nextFrame(self):
        if self.radius < 0:
            self.radius = 0
            self.length = 4
            self.alphaChange = self.alpha / self.length
            self.isFading = True
            return True
            
        elif self.radius == 0:
            FadeOut.nextFrame(self)
            return self.alpha > 0
        else:
            self.radius -= self.radiusChange
            self.surface.fill((0,0,0))
            if self.radius > 0:
                py.draw.circle(self.surface, (0, 255, 255), self.getApproxPos(), self.radius)
            return True
        


