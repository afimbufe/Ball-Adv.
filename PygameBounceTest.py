# -*- coding: utf-8 -*-
"""
Main code for Ball Adventures that ties everything together

Created on Wed Jun 28 02:35:41 2017

@author: Alex
"""

import pygame, math
pygame.init()
import BallUnit as Ball
import Projectile as rng
import Platform as lv
import frameworks as fw
import UserInterface as ui
import os
x, y = 50, 50
os.environ['SDL_VIDEO_WINDOW_POS'] = "{},{}".format(x,y)

# TODO: "Slow" skill can also affect speed
# TODO: Almighty attack

# --- Important Game Variables and Set Up ---

# Constants:
screenWidth = 800
screenHeight = 600
gameWidth = 640
gameHeight = 480
#screenWidth = 960
#screenHeight = 640
inBattle_scale = 1.5

# States that affect what is displayed on screen
GAMEPLAY = 0
PAUSEMENU = 1
SHOP = 2
SKILLEQUIP = 3
OPTIONS = 4
STARTSCREEN = 5
DEATHSCREEN = 6


blue = (0,0,255)
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
lightred = (255, 100, 100)
grey = (192, 192, 192)

# Game State Management Variables and Initializations
#menu = False
gamePaused = False
animationPaused = False
crashed = False
gameState = GAMEPLAY
currentFloor = lv.levels.getCurrentLevel().getCurrentFloor()
gameAnimations = fw.Animations()
scale = 1
inBattleEndTimer = 0
inBattlePrepTimer = 0


gameDisplay = pygame.display.set_mode((screenWidth, screenHeight), 0, 0)
#gameDisplay = pygame.display.set_mode((gameWidth, gameHeight), 0, 0)

pygame.display.set_caption('Ball Adventures')
basicfont = pygame.font.SysFont('Ariel MS', 30)

Ball.setScreenSize(screenWidth, screenHeight)
lv.setScreenSize(screenWidth, screenHeight)
clock = pygame.time.Clock()

player = Ball.PlayerBall(50, 30, 0, 30, (False,False,False))
player.setPos2(currentFloor.getPlayerStartPos())
#player.setPos(100, 580)
lr = [0, 0]
inBattleEnemy = None  # Only one at a time

pauseButton = pygame.Rect(0, 0, 80, 22)

pauseMenu = ui.PauseMenu()
skillsUI = ui.SkillsUI(player)
#shopUI = ui.ShopUI()

# --- Functions related to displaying and drawing on screen ---

def makeHealthBar():
    barLength = 100
    barHeight = 20
    
    # Getting percents
    healthPct = player.getHP()/player.getMaxHP()
    healablePct = player.getHealableDmg()/player.getMaxHP()
    permaDmgPct = 1 - healthPct - healablePct
    mpPct = max(player.getMP()/player.getMaxMP(), 0)
    
    # defining bars and borders
    hpbarOutline = pygame.Rect(99, 30, barLength + 2, barHeight)    
    mpbarOutline = pygame.Rect(99, 60, barLength + 2, barHeight)
    
    healthBar = pygame.Rect(100, 31, math.ceil(barLength * healthPct), barHeight - 2)
    healableBar = pygame.Rect(100 + barLength * healthPct, 31, math.ceil(barLength * healablePct), barHeight - 2)
    dmgBar = pygame.Rect(100 + barLength * (healthPct + healablePct), 31, \
                         math.ceil(barLength * permaDmgPct), barHeight - 2)
    mpBar = pygame.Rect(100, 61, math.ceil(barLength * mpPct), barHeight - 2)
    
    # Drawing
    pygame.draw.rect(gameDisplay, black, hpbarOutline)
    pygame.draw.rect(gameDisplay, green, healthBar)
    if healthPct < 1:
        if not healablePct == 0:
            pygame.draw.rect(gameDisplay, lightred, healableBar)
        pygame.draw.rect(gameDisplay, red, dmgBar)
    
    pygame.draw.rect(gameDisplay, black, mpbarOutline)
    pygame.draw.rect(gameDisplay, blue, mpBar)
    # TODO: Make this a surface

def overworldEnemyHPBar(enemy):
    # Drawing the HP bar for overworld enemies when they're hit (fades)
    pxAbove = 30
    barLength = 64
    barHeight = 7
    ePos = enemy.getPos()
    r = enemy.getRadius()
    healthPct = enemy.getHP()/enemy.getMaxHP()
    
    #healthAdjust = ePos[0] - barLength/2 + math.ceil(barLength * healthPct)
    #healthBar = pygame.Rect(ePos[0] - barLength/2, ePos[1] - pxAbove - r, math.ceil(barLength * healthPct), barHeight)
    #dmgBar = pygame.Rect(healthAdjust, ePos[1] - pxAbove - r, math.floor(barLength * (1 - healthPct)), barHeight)
    healthBarPos = (ePos[0] - barLength/2, ePos[1] - pxAbove - r)
    healthAdjust = math.ceil(barLength * healthPct)
    healthBar = pygame.Rect(0, 0, math.ceil(barLength * healthPct), barHeight)
    dmgBar = pygame.Rect(healthAdjust, 0, math.floor(barLength * (1 - healthPct)), barHeight)
    
    # Drawing: Can this fade?
    healthBarSurface = pygame.Surface((barLength, barHeight))
    pygame.draw.rect(healthBarSurface, green, healthBar)
    pygame.draw.rect(healthBarSurface, red, dmgBar)
    
    if enemy.getHealthBarCount()==1:
        gameAnimations.addAnimation(fw.MovingFade(healthBarSurface, enemy, healthBarPos, 4))
    else:
        gameDisplay.blit(healthBarSurface, healthBarPos)


def inBattleEnemyHPBar():
    barLength = 150
    barHeight = 25
    
    if inBattleEnemy == None:
        return None
    
    # Text
    enemyName = basicfont.render("Lv " + str(inBattleEnemy.getLv()) + " " + \
                                 inBattleEnemy.getName(), False, (0,0,0))
    enemyHP = basicfont.render("HP: " + str(inBattleEnemy.getHP()) + "/" + str(inBattleEnemy.getMaxHP()), False, (0,0,0)) 
    gameDisplay.blit(enemyName, (550, 5))
    gameDisplay.blit(enemyHP, (550, 30))
    
    # Percents
    healthPct = inBattleEnemy.getHP()/inBattleEnemy.getMaxHP()
    healablePct = inBattleEnemy.getHealableDmg()/inBattleEnemy.getMaxHP()
    permaDmgPct = 1 - healthPct - healablePct
    
    # defining bars and borders
    hpbarOutline = pygame.Rect(644, 30, barLength + 2, barHeight)    
    
    healthBar = pygame.Rect(645, 31, math.ceil(barLength * healthPct), barHeight - 2)
    healableBar = pygame.Rect(645 + barLength * healthPct, 31, math.ceil(barLength * healablePct), barHeight - 2)
    dmgBar = pygame.Rect(645 + barLength * (healthPct + healablePct), 31, \
                         math.ceil(barLength * permaDmgPct), barHeight - 2)
    # Drawing
    pygame.draw.rect(gameDisplay, black, hpbarOutline)
    if not healthPct <= 0:
        pygame.draw.rect(gameDisplay, green, healthBar)
    if healthPct < 1:
        if not healablePct == 0:
            pygame.draw.rect(gameDisplay, lightred, healableBar)
        pygame.draw.rect(gameDisplay, red, dmgBar)

    # TODO: Make this a surface


def updateNumberDisplay():
    # Displaying the text and the health bars
    hpsurface = basicfont.render("HP: " + str(player.getHP()) + "/" + str(player.getMaxHP()), False, (0,0,0)) 
    mpsurface = basicfont.render("MP: " + str(player.getMP()) + "/" + str(player.getMaxMP()), False, (0,0,0))
    expsurface = basicfont.render("EXP: " + str(player.getEXP()), False, (0,0,0))
    specialsurface = basicfont.render("Cooldown: " + str(player.getSpecialSecs()), False, (0,0,0))
    
    minimenu = pygame.Surface((800, 118))
    minimenu.fill(black)
    pygame.draw.rect(minimenu, grey, pygame.Rect(0,0,800, 115))
    minimenu.set_alpha(100)
    gameDisplay.blit(minimenu, (0,0))
    #pygame.draw.rect(gameDisplay, grey, pygame.Rect(0,0,800, 115))
    
    gameDisplay.blit(hpsurface, (0,30))
    gameDisplay.blit(mpsurface, (0, 60))
    gameDisplay.blit(expsurface, (0, 90))
    gameDisplay.blit(specialsurface, (0, 120))
    
    makeHealthBar()
    
    menuText = basicfont.render("MENU", False, red)
    pygame.draw.rect(gameDisplay, black, pauseButton)  # This should be its own class
    gameDisplay.blit(menuText, (10,2))
                    
    if inBattleEnemy:
        inBattleEnemyHPBar()


def drawMainElements():
    # platform, then balls, then bullets
    gameDisplay.fill(white)
    drawEdges()
    if not inBattleEnemy:
        activeEnemies = currentFloor.getActiveEnemies()
        
        for platform in currentFloor.getActivePlatforms():
            platformBox = platform.getRect()
            pygame.draw.rect(gameDisplay, platform.getColor(), platformBox)
    
        for enemy in activeEnemies:    
            enemy.draw(gameDisplay)  
    elif inBattleEnemy and inBattleEnemy.getHP()>0:
        inBattleEnemy.draw(gameDisplay)
        
    player.draw(gameDisplay)
    
    for bullet in player.getBullets():
        bullet.draw(gameDisplay)
    
    bomb = player.getScreenBomb()
    if bomb:
        bomb.draw(gameDisplay)
    
    if not inBattleEnemy:
        for enemy in currentFloor.getEnemies():
            for ebullet in enemy.getBullets():
                ebullet.draw(gameDisplay)        
            if enemy.showHPBar():
                overworldEnemyHPBar(enemy)
    elif inBattleEnemy and inBattleEnemy.getHP()>0:
        for ebullet in inBattleEnemy.getBullets():
            ebullet.draw(gameDisplay)

    phys = player.getPhys()
    if phys:
        phys.draw(gameDisplay)

    gameAnimations.drawAnimations(gameDisplay)

    
        

# --- Helpful Helper Functions ---
def prepInBattle(enemy, left = True):
    global inBattlePrepTimer, inBattleEnemy
    
    inBattleEnemy = enemy
    player.clearBullets()
    currentFloor.clearAllBullets()
    player.savePosition(player.getPos(), player.isGrounded())
    
    inBattlePrepTimer = 15
    mid = midPoint(player.getPos(), inBattleEnemy.getPos())
    gameAnimations.addAnimation(fw.Spotlight(mid))


def toInBattle(left = True):
    global inBattleEnemy, scale, lr
    inBattleEnemy.inBattleState(True)
    inBattleEnemy.setPos2(inBattleEnemy.getInBattlePos())
    inBattleEnemy.updateInBattleHP()
    # enemy hp adjustment
    
    player.setPos2(player.getInBattlePos())
    player.fall()
    lr = [0,0]
    
    # TODO: Enemies should have starting in-battle positions, eg. Flying in the air
    scale = inBattle_scale
  
    
def endInBattle():
    global inBattleEndTimer
    inBattleEndTimer = 50


def midPoint(pos1, pos2):
    x = abs(pos1[0] - pos2[0])/2 + min(pos1[0], pos2[0])
    y = abs(pos1[1] - pos2[1])/2 + min(pos1[1], pos2[1])
    return (math.floor(x),math.floor(y))


def timers():
    global inBattleEndTimer, inBattlePrepTimer, gamePaused
    if not paused():
        if inBattleEndTimer > 0:
            inBattleEndTimer -= 1
            if inBattleEndTimer == 0:
                toOverworld()
    
    
    # Regardless of pause
    if inBattlePrepTimer > 0:
        gamePaused = True
        inBattlePrepTimer -= 1
        if inBattlePrepTimer == 0:
            gamePaused = False
            toInBattle()
    
    
      
def sideScroll(x, y):
    currentFloor.shift(x, y)
    gameAnimations.shift(x, y)
    player.shiftPos(x, y)
    phys = player.getPhys()
    if phys:
        phys.shiftPos(x, y)
    for bullet in player.getBullets():
        bullet.shiftPos(x, y)


def toOverworld():
    global scale, inBattleEnemy
    
    player.clearBullets()
    
    inBattleEnemy = None
    
    #gameState = OVERWORLD
    # TODO: Set up floor
    scale = 1
    prevPos = player.getSavePos()
    player.setPos2(prevPos[0])
    if not prevPos[1]:
        player.fall()    
    
    # Grounded Check
    

def collideWithPlatforms(bulletRect):
    if not inBattleEnemy:
        for platform in currentFloor.getActivePlatforms():
            if platform.canBlockBullets() and platform.getRect().colliderect(bulletRect):
                return True
    return False


def collideWithEnemy(bulletRect, dmg):
    for enemy in activeEnemies:
        enemyBox = enemy.getOuterBox()
        if bulletRect.colliderect(enemyBox):
            alive = enemy.takeDamage(dmg)
            if not alive:
                enemyKill(enemy)
            return True
    return False


def togglePause():
    global gamePaused
    gamePaused = not gamePaused


def targetShoot(x, y, pos):
    global player
    pPos = player.getPos()
    if not x - pPos[0] == 0:
        angle = math.atan(-(y - pPos[1])/(x - pPos[0]))
    else: 
        angle = math.pi/2

    if x < pPos[0]:
        angle *= -1
    player.shootBullet(angle, x >= pPos[0])


def adjustInertia(inertia, grounded):
    global lr
    airSlow = 0.08
    groundSlow = 0.15
    
    #airSlow = 1
    #groundSlow=1
    if not inertia == 0 and not grounded:
        # In Air
        lr[inertia - 1] -= airSlow
        if lr[inertia - 1] <= 0:
            lr[inertia - 1] = 0
            return True
    elif not inertia == 0:
        lr[inertia - 1] -= groundSlow
        if lr[inertia - 1] <= 0:
            lr[inertia - 1] = 0
            return True
    return False


def playerHit(dmg):
    if player.takeDamage(dmg) == False:
        playerDeath()
        
def enemyKill(enemy):
    global currentFloor, gameAnimations
    expGain = enemy.getEXPPrize()
    
    x, y = enemy.getApproxPos() 
    r = enemy.getRadius()
    gameAnimations.addAnimation(fw.ShowEXP(expGain, (x - r, y - r)))
    
    player.gainEXP(expGain)
    if inBattleEnemy:
        endInBattle()
    currentFloor.removeEnemy(enemy)
    

def playerDeath():
    
    player.setYSpeed(0)
    player.inAir()
    player.clearBullets()
    #currentFloor.clearAllBullets()
    player.setPos(100, 500)
    player.removeInvincibility()
    player.fullRestore()

# --- Event Listeners ---

def gameKeyboardListener(event):
    if not paused() and not player.isFireCharge():                
        if event.type == pygame.KEYDOWN:
            gameKeyDownListener(event.key)
            
        elif event.type == pygame.KEYUP:
            gameKeyUpListener(event.key)
    

def gameKeyDownListener(key):
    global lr
    if key == pygame.K_UP or key == pygame.K_w:
        player.jump()
    elif key == pygame.K_LEFT or key == pygame.K_a:
        lr[0] = 1
        lr[1] = 0
        player.changeDir(False)
    elif key == pygame.K_RIGHT or key == pygame.K_d:
        lr[1] = 1
        lr[0] = 0
        player.changeDir(True)
    elif key == pygame.K_LSHIFT or key == pygame.K_RSHIFT:
        player.sprint(True)
    elif key == pygame.K_SPACE:
        player.usePhysical()


def gameKeyUpListener(key):
    global lr, player, gameState
    pSpeeds = player.getSpeeds()
    if key == pygame.K_UP or key == pygame.K_w:
        if pSpeeds[1] > 8:
            player.setYSpeed(12)
    elif key == pygame.K_z:
        if inBattleEnemy:
            player.shootBullet(0, player.getX() <= inBattleEnemy.getX())    
        else:
            player.shootBullet(0, player.isFacingRight())
    elif key == pygame.K_DOWN or key == pygame.K_s:
        player.setScreenBomb(rng.ScreenBomb(player.getPos()[0], player.getPos()[1]))
    elif key == pygame.K_q:
        togglePause()
        gameState = SKILLEQUIP
    elif key == pygame.K_r:
        pass
    elif key == pygame.K_f:
        pass
    elif key == pygame.K_t:
        pass
    else:
        slowdownCheck(key)

def gameMouseListener():
    # TODO: When clicking side bar, don't shoot
    global player, gamePaused
    
    mouseX = pygame.mouse.get_pos()[0]
    mouseY = pygame.mouse.get_pos()[1]
    
    # Pause Button
    if pauseButton.collidepoint(mouseX, mouseY):
        togglePause()
    elif not paused():
        targetShoot(mouseX, mouseY, player.getPos())
        
def menuKeyboardListener(event):
    global gameState
    
    # connects the menu instance to the keyboard
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            if pauseMenu.hasSelection():
                pauseMenu.prevItem()
            else:
                pauseMenu.selectLastButton()
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            if pauseMenu.hasSelection():
                pauseMenu.nextItem()
            else:
                pauseMenu.selectItem(0)
        elif event.key == pygame.K_RETURN:
            if not pauseMenu.hasSelection():
                togglePause()
                gameState = GAMEPLAY
            else:
                newState = pauseMenu.clickSelection()
                if newState == GAMEPLAY:
                    togglePause()
                gameState = newState
        elif event.key == pygame.K_q:
            gameState = SKILLEQUIP

def slowdownCheck(key):
    if key == pygame.K_LSHIFT or key == pygame.K_RSHIFT:
        player.sprint(False)
    elif key == pygame.K_LEFT or key == pygame.K_a:
        player.setInertia(1)
    elif key == pygame.K_RIGHT or key == pygame.K_d:
        player.setInertia(2)

def SkillEquipKeyListener(event):
    global gameState
    if event.key == pygame.K_x:
        gameState = PAUSEMENU  
    elif event.key == pygame.K_r:
        pass
    elif event.key == pygame.K_f:
        pass
    elif event.key == pygame.K_t:
        pass


# --- Updating State ---

def updateEnemies(enemies):
    global player
    playerRect = player.getHitBox()
    pPos = player.getPos()
    if not inBattleEnemy:
        enemyList = enemies
    elif inBattleEnemy and inBattleEnemy.getHP()>0:
        inBattleEnemy.updatePlayerPos(pPos)
        enemyList = [inBattleEnemy]
    else:
        enemyList = []
    for enemy in enemyList:
        if inBattleEnemy:
            enemy.updateFrame()
        else:
            enemy.updateFrame(currentFloor.getGround())
        ePos = enemy.getPos()
        if enemy.tick():
            # Shooting a new bullet, change this section to be more flexible    
            enemy.shootAt(pPos)
        enemyRect = enemy.getHitBox()
        if enemyRect.colliderect(playerRect):
            # Player Touches Enemy
            if inBattleEnemy:
                dmg = enemy.getSlamDmg() if not player.isFireCharge() else enemy.getSlamDmg()/2
                playerHit(dmg)
            elif not player.isFireCharge():
                prepInBattle(enemy, pPos[0] <= ePos[0])

        # TODO: Interact with platforms
        
        # Bullet Actions
        for ebullet in enemy.getBullets():
            if ebullet.update():
                bulletRect = ebullet.getHitBox()
                dmg = ebullet.damageAmt()
                if bulletRect.colliderect(playerRect) and dmg > 0:
                    playerHit(dmg)
                    if ebullet.endsOnContact():
                        enemy.removeBullet(ebullet) 
                    else:
                        ebullet.negate()
                elif collideWithPlatforms(bulletRect):
                    enemy.removeBullet(ebullet)
            else:
                # Goes Off Screen
                enemy.removeBullet(ebullet)


def updatePlayerBullets():
    global player, currentFloor
    
    bullets = player.getBullets()
    for bullet in bullets:
        if bullet.canFollow():
            onScreen = bullet.update(currentFloor.getActiveEnemies())
        else:
            onScreen = bullet.update()
        
        if onScreen: 
            bulletRect = bullet.getHitBox()
            
            if collideWithPlatforms(bulletRect):
                player.removeBullet(bullet)
            else:
                if collideWithEnemy(bulletRect, bullet.damageAmt()):
                    player.removeBullet(bullet)            
        else:
            # Off Screen
            player.removeBullet(bullet)

    updatePlayerAttack()


def updatePlayerAttack():
    phys = player.getPhys()
    
    if phys:
        ongoing = phys.update()
        for enemy in currentFloor.getActiveEnemies():
            if enemy.isVulnerable and phys.collide(enemy.getHitBox()):
                alive = enemy.takeDamage(phys.damageAmt())
                enemy.gotHit()
                if not alive:
                    enemyKill(enemy)
            
            for bullet in enemy.getBullets():
                if bullet.isVulnerable() and phys.collide(bullet.getHitBox()):    
                    destroyed = bullet.reduceDmg(phys.damageAmt())
                    if destroyed:
                        enemy.removeBullet(bullet)
                    
        # collideWithEnemy(phys.getHitBox(), phys.damageAmt())
        if not ongoing:
            player.endPhys()
            currentFloor.resetVulnerability()
            


def updateScreenBomb():
    global player, gamePaused
    bomb = player.getScreenBomb()
    if bomb:
        gamePaused = True
        bomb.update()
        bombRect = bomb.getHitBox()
        if bomb.getRadius() > screenWidth:
            dmg = bomb.damageAmt()
            for enemy in activeEnemies:
                enemyBox = enemy.getHitBox()
                if bombRect.colliderect(enemyBox):
                    alive = enemy.takeDamage(dmg)
                    enemy.reduceHealableDmg(dmg//2)
                    if not alive:
                        enemyKill(enemy)
            player.removeScreenBomb()
            gamePaused = False
            
        for enemy in currentFloor.getEnemies():
            for ebullet in enemy.getBullets():
                if bombRect.colliderect(ebullet.getHitBox()):
                    enemy.removeBullet(ebullet)    
            # removes bullets too
        
            
            
def handlePlatformHit():
    currentFloor.tick()
    playerOnPlatform = False
    pPos = player.getPos()
    playerOuterRect = player.getOuterBox()
    playerRect = player.getHitBox()
    for platform in currentFloor.getActivePlatforms():
        platformBox = platform.getRect()
        if platformBox.colliderect(playerOuterRect):
            playerOnPlatform = True # Marks that player is touching platform
            r = player.getRadius()
            
            if not player.isFalling() and not platform.canJumpThrough() \
                                      and pPos[1] > platformBox.bottom and pPos[0] <= platformBox.right and pPos[0] >= platformBox.left:
                    # Hit head from bottom
                    player.setPos(pPos[0], platformBox.bottom + r)
                    player.bounce()
            elif player.isFalling():
                if pPos[1] <= platformBox.top:
                    # Land on platform
                    player.setPos(pPos[0], platformBox.top - r + 1)
                    player.touchGround(True)
                elif playerOuterRect.left >= platformBox.left:
                    player.setPos(platformBox.right + r - 1, pPos[1])
                elif playerOuterRect.right <= platformBox.right:
                    player.setPos(platformBox.left - r + 1, pPos[1])
            elif not platform.canJumpThrough() and playerRect.bottom > platformBox.top and playerRect.top <= platformBox.bottom:
                # blocked if walking into a pillar
                if playerOuterRect.left >= platformBox.left:
                    player.setPos(platformBox.right + r - 1, pPos[1])
                elif playerOuterRect.right <= platformBox.right:
                    player.setPos(platformBox.left - r + 1, pPos[1])
        
        if not platform.canJumpThrough():
            for enemy in currentFloor.getEnemies():
                enemyBox = enemy.getOuterBox()
                enemyPos = enemy.getPos()
                if platformBox.colliderect(enemyBox):
                    # Need to check if falling
                    r = enemy.getRadius()
                    if enemyPos[1] + 2 * r > platformBox.top and enemy.isFalling():
                        enemy.setY(platformBox.top - r - 1)
                        enemy.jump()
                    elif enemyPos[1] - 2 * r < platformBox.bottom and not enemy.isFalling():
                        enemy.setY(platformBox.bottom + r + 1)
                        enemy.bounce()
                    #enemy.changeYSpeed(0)
                    
            
                        
    if not playerOnPlatform and player.isOnPlatform():
        player.fall()

def paused():
    return gamePaused or animationPaused


def drawEdges():
    floorPos = currentFloor.getPos()
    floorDim = currentFloor.getDimensions()
    rect1 = pygame.Rect(floorPos[0], 0, screenWidth/2 , screenHeight)
    rect2 = pygame.Rect(floorPos[0] + floorDim[0] - screenWidth / 2, 0, screenWidth/2, screenHeight)
    rect3 = pygame.Rect(0, screenHeight/2 + floorDim[1], screenWidth , screenHeight / 2)
    #rect4 = None
    #pygame.draw.rect(gameDisplay, lightred, rect1)
    #pygame.draw.rect(gameDisplay, lightred, rect2)
    #pygame.draw.rect(gameDisplay, lightred, rect3)

# ----- Main Game Loop ------
def inputHandling():
    global crashed, gameState
    
    # lots of ifs in one loop or a loop in each if
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True
        
        if gameState == GAMEPLAY:
            if event.type == pygame.MOUSEBUTTONUP:
                gameMouseListener()
            if event.type == pygame.KEYUP and (event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE):
                togglePause()
                gameState = PAUSEMENU
            gameKeyboardListener(event)
        else:
            if gamePaused and event.type == pygame.KEYUP:
                # Menu and keys that can be pressed while paused
                slowdownCheck(event.key)
            
            # key presses for non-game states
            if gameState == PAUSEMENU:
                if event.type == pygame.KEYUP and (event.key == pygame.K_ESCAPE or \
                                                   event.key == pygame.K_x):
                    togglePause()
                    gameState = GAMEPLAY
                    pauseMenu.unSelect()
                menuKeyboardListener(event)
            elif gameState == SHOP:
                if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                    togglePause()
                    gameState = GAMEPLAY
                    pauseMenu.unSelect()
            elif gameState == SKILLEQUIP: 
                if event.type == pygame.KEYUP and (event.key == pygame.K_ESCAPE or \
                                                   event.key == pygame.K_q):
                    togglePause()
                    gameState = GAMEPLAY
                    pauseMenu.unSelect()
                SkillEquipKeyListener(event)

    if gameState == -1:
        crashed = True
    
    
def displayHandling():
    global gameState
    if gameState == GAMEPLAY:
        drawMainElements()
        updateNumberDisplay()
    elif gameState == PAUSEMENU:
        pauseMenu.draw(gameDisplay)
    elif gameState == SHOP:
        pass
    elif gameState == SKILLEQUIP:
        skillsUI.draw(gameDisplay)
    
        # draw the game then draw the menu then draw the shop, or only redraw when moves from shop back to menu
    pygame.display.update()
    clock.tick(24)


def gameUpdate():
    global activeEnemies, animationPaused
    if not paused():
        if adjustInertia(player.getInertia(), player.isGrounded()):
            player.setInertia(0)
        
        player.updateFrame(lr[1] - lr[0])
        
        activeEnemies = currentFloor.getActiveEnemies()
        
        updatePlayerBullets()
        updateEnemies(currentFloor.getEnemies())
        if not inBattleEnemy:
            handlePlatformHit()
            pPos = player.getApproxPos()
            shiftX = currentFloor.XSideScroll(pPos[0])
            shiftY = currentFloor.YSideScroll(pPos[1])
            sideScroll(shiftX, shiftY)
        
        
    gameAnimations.updateAnimations()
    animationPaused = gameAnimations.pausesGame()
    timers()
    updateScreenBomb()


def gameLoop():
    global crashed, gameState
    while not crashed:
        inputHandling()
        if gameState == GAMEPLAY:
            gameUpdate()
        displayHandling()


gameLoop()
pygame.quit()
quit()