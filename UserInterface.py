# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 01:28:29 2017

@author: Alex
"""

import pygame as py
import frameworks as fw


# Constants
GAMEPLAY = 0
PAUSEMENU = 1
SHOP = 2
SKILLEQUIP = 3
OPTIONS = 4
STARTSCREEN = 5
DEATHSCREEN = 6

RANGE = 0
PHYS = 1
SPECIAL = 2

blue = (0,0,255)
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
lightred = (255, 100, 100)
grey = (192, 192, 192)
yellow = (255,255,0)

basicfont = py.font.SysFont('Ariel MS', 40)


class AbstractButton(fw.positionObj):
    # Typically for the UI or menu, so the positions are fixed
    def __init__(self, pos, width, height, text):
        self.pos = pos
        self.width = width
        self.height = height
        self.text = text
        self.active = False
        # Should account for different button types
        
    def click(self):
        print("to be implemented in child classes")
        # performs the action of the button

    def getBox(self):
        pass
        # for checking if its being hovered over

    def draw(self):
        pass
        # Typically has different look depending on whether the button is selected or not


    def activate(self):
        self.active = True
        
    def deactivate(self):
        self.active = False
        

class PauseMenuButton(AbstractButton):
    def __init__(self, pos, text, width = 200, height = 50):
        AbstractButton.__init__(self, pos, width, height, text)
        self.image = py.Surface((width, height))
        
    def click(self):
        newState = PAUSEMENU
        if self.text == "Equip Skills":
            newState = SKILLEQUIP
        elif self.text == "Upgrades Shop":
            # newState = SHOP
            pass
        elif self.text == "Options":
            # newState = OPTIONS
            pass
        elif self.text == "Quit":
            # Should ask for confirmation
            newState = -1
        elif self.text == "Continue":
            newState = GAMEPLAY
        else:
            print("Don't Recognize Action")
        # Returns new gameState
        return newState
        
    def draw(self, display):
        self.image.fill(black)
        rect = py.Rect(1, 1, self.width - 2, self.height - 2)
        buttonText = basicfont.render(self.text, False, black)
        textRect = buttonText.get_rect()
        if not self.active:
            py.draw.rect(self.image, yellow, rect)
        else:
            py.draw.rect(self.image, green, rect)
        self.image.blit(buttonText, (self.width / 2 - textRect.width/2, self.height / 2 - textRect.height/2))
        display.blit(self.image, (self.getX(), self.getY()))


class AbstractMenu(object):
    # has options and selected and move selection functions
    def __init__(self, items, isVertical = True, index = -1):
        self.items = items
        self.index = index # -1 means nothing is selected when created, which is default
        self.isVertical = isVertical
        
    def getSelected(self):
        return self.items[self.index]
    
    def nextItem(self):
        self.index = min(self.index + 1, len(self.items) - 1)
        # How to handle moving after you hit an end? stop or start from beginning?    
    
    def prevItem(self):
        self.index = max(0, self.index - 1)
    
    def selectItem(self, index):
        if index >= 0 and index < len(self.items):
            self.index = index
    
    def verticallyAligned(self):
        return self.isVertical


class ButtonMenu(AbstractMenu):
    def __init__(self, items, buttonList, width = 800, height = 600, isVertical = True):
        AbstractMenu.__init__(self, items)
        self.height = height
        self.width = width
        self.buttons = buttonList
        
    def updateButtons(self):
        for i in range(len(self.buttons)):
            if i==self.index:
                self.buttons[i].activate()
            else:
                self.buttons[i].deactivate()
    
    def nextItem(self):
        AbstractMenu.nextItem(self)
        self.updateButtons()
        # How to handle moving after you hit an end? stop or start from beginning?    
    
    def prevItem(self):
        AbstractMenu.prevItem(self)
        self.updateButtons()
        
    def selectItem(self, index):
        # for mouse hovers... do I need it? ehhh probably not, just mouse click
        AbstractMenu.selectItem(self, index)
        self.updateButtons()

    def hasSelection(self):
        return self.index >= 0 and self.index < len(self.items)
    
    def getButtons(self):
        return self.buttons
    
    def selectLastButton(self):
        self.selectItem(len(self.items))

    def unSelect(self):
        self.index = -1
        self.updateButtons()

    def clickSelection(self):
        if self.hasSelection:
            newState = self.buttons[self.index].click()
            if newState == GAMEPLAY:
                self.unSelect()
            return newState
        else:
            return PAUSEMENU

    def draw(self, display):
        # just draws the buttons, not the background
        #print("button draw")
        for button in self.buttons:
            button.draw(display)


class PauseMenu(ButtonMenu):
    def __init__(self):
        buttonList = []
        
        width = 350
        height = 500
        self.x = 800 / 2 - width/2
        self.y = 600 / 2 - height/2
        buttonWidth = 250
        buttonHeight = 45
        buttonX = width / 2 - buttonWidth / 2
        buttonPositions = [(buttonX, 100), (buttonX, 175), \
                           (buttonX, 250), (buttonX, 325), (buttonX, 400)] # Must be same length as number of items in menu
        menuItems = ["Continue", "Equip Skills", "Upgrades Shop", "Options", "Quit"]
        
        self.color = grey
        self.display = py.Surface((width, height))
        
        
        for i in range(len(menuItems)):
            buttonList.append(PauseMenuButton(buttonPositions[i], menuItems[i], buttonWidth, buttonHeight))
        ButtonMenu.__init__(self, menuItems, buttonList, width, height)
        
        
        # These names need a change. Also, order is important
        # Quit needs an "Are you sure?" prompt
        # Need a "run from battle" option in the in-battle phase, where the player loses a life
        # confirmation is definitely part of this
        
    def draw(self, display):
        # Rounded edges anyone? 
        # draw background and overall text
        bordersize = 1
        self.display.fill(black)
        
        py.draw.rect(self.display, self.color, py.Rect(bordersize, bordersize, self.width - 2 * bordersize, \
                                                       self.height - 2 * bordersize))
        ButtonMenu.draw(self, self.display) # draw buttons
        
        menuText = basicfont.render("Paused", False, black)
        menuTextBox = menuText.get_rect()
        self.display.blit(menuText, (self.width/2 - menuTextBox.width/2, 40))
                       
        display.blit(self.display, (self.x, self.y))
        
        
class ShopUI(object):
    # series of menus and buttons, laid out in a certain way
    pass


class skillButton(AbstractButton):
    # has skill associated with it
    def __init__(self, pos, width, height, skill):
        AbstractButton.__init__(self, pos, width, height, skill.getName())
        self.skill = skill
    

class SkillButtonMenu(ButtonMenu):
    def __init__(self, items, buttonList, width, height):
        ButtonMenu.__init__(self, items, buttonList, width, height)



class SkillsUI(object):
    # Also displays stats
    def __init__(self, player):
        skillTypes = ["Upgrades", "Range", "Physical", "Special"]
        activeSkills = [player.getRangeSkill(), player.getPhysSkill(), player.getSpecialSkill()] # change this to the actual code
        allSkills = [player.getAllSkills(RANGE), player.getAllSkills(PHYS), player.getAllSkills(SPECIAL)]
        skillTypeButtons = ["Range", "Physical", "Special"]
                       
        self.skillTypeMenu = AbstractMenu(["Upgrades", "Range", "Physical", "Special"])
        self.skillTypeMenu.selectItem(0)
        self.descriptionBox = py.Surface((550, 100))
        self.display = py.Surface((600, 400))
        
    def updatePlayerSkills(self, player):
        # updates data depending on what skills the player has
        # call whenever a skill or upgrade is bought or sold
        pass
    
    def equipSkill(self, player):
        pass
    
    def draw(self, display):
        self.display.fill(black)
        display.blit(self.display, (100, 100))
    
    
class Skill(object):
    def __init__(self, skillType, name, dealsDmg, baseDmg = 0, mpCost = 0, hpCost = 0):
        # Has information about skill, not in execution, for shop purposes
        self.description = ""
        self.name = name
        self.skillType = skillType
        self.dealsDamage = dealsDmg
        self.skillCode = None
        self.baseDmg = baseDmg
        self.mpCost = mpCost
        self.hpCost = hpCost
        
    def setDescription(self, dsc):
        self.description = dsc
        
    def isDamaging(self):
        return self.dealsDamage
    
    def getSkillType(self):
        return self.skillType

    def getDamage(self):
        return self.baseDmg
    
    def getMPCost(self):
        return self.mpCost
    
    def getName(self):
        return self.name