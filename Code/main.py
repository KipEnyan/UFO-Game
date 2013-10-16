from pyPad360 import*
import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import *    #basic Panda modules
from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import *  #for compound intervals
from direct.task import Task         #for update functions
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage

import sys, math, random
import os
from panda3d.core import Filename
from utilities import resource_path
from saucer import*
from pickupable import*
from missile import *

del base

class World(DirectObject):
    def __init__(self):

        self.accept("escape", sys.exit) 
        self.accept("enter", self.loadGame)
        self.accept("C1_START_DOWN", self.loadGame)
        self.tractorbeamsound = base.loader.loadSfx("Sounds/tractorbeam.wav")
        Lvl = 1
        self.Lvl = Lvl
        
        gamepads = pyPad360()
        ##print gamepads.setupGamepads()
        if gamepads.setupGamepads() > 0:
            gamepads.setupGamepads()
            taskMgr.add(gamepads.gamepadPollingTask, "gamepadPollingTask")
            self.gameControls360()
        
        self.title = loader.loadModel("Art/skybox.egg")
        self.title.reparentTo(render)
        self.title.setScale(1)
        self.title.setPos(0, 0, -55)
        
        self.text1 = OnscreenText(text="Press Enter to Start",style=1, fg=(0.8,0,0.1,1),pos=(0, -0.88), scale = .2,mayChange = 1,align=TextNode.ACenter)
        self.inGame = False
        #print self.text1
        
        
    def loadGame(self):
        
        if not self.inGame:
            self.inGame = True
            self.title.removeNode()          
            del self.title
            self.text1.destroy()
            del self.text1
            
            self.startGame()
 
    def startGame(self):        
        #if self.inGame == True:
        
        self.saucer = Saucer()
        base.disableMouse()
        camera.setPosHpr(0, -40, 73, 0, 0, 0)
        camera.lookAt(self.saucer.ship)
        camera.setP(camera.getP() -8)
        self.loadModels()
        self.loadHUD()
            
        self.setupLights()
        self.keyMap = {"left":0, "right":0,"w":0,"a":0,"s":0,"d":0,"k":0,"l":0}
        self.prevtime = 0
  
        self.accept("arrow_right", self.setKey, ["right", 1])
        self.accept("arrow_left", self.setKey, ["left", 1])
        self.accept("arrow_right-up", self.setKey, ["right", 0])
        self.accept("arrow_left-up", self.setKey, ["left", 0])
        self.accept("w", self.setKey, ["w", 1])
        self.accept("w-up", self.setKey, ["w", 0])
        self.accept("s", self.setKey, ["s", 1])
        self.accept("s-up", self.setKey, ["s", 0])
        self.accept("a", self.setKey, ["a", 1])
        self.accept("a-up", self.setKey, ["a", 0])
        self.accept("d", self.setKey, ["d", 1])
        self.accept("d-up", self.setKey, ["d", 0])
        
        self.accept("k", self.setKey, ["k", 1])
        self.accept("k-up", self.setKey, ["k", 0])       
        self.accept("l", self.setKey, ["l", 1])
        self.accept("l-up", self.setKey, ["l", 0]) 
        
        
        self.accept("enter", self.blank)
        self.accept("C1_START_DOWN", self.blank)
        
        self.mydir = os.path.abspath(sys.path[0])
        self.mydir = Filename.fromOsSpecific(self.mydir).getFullpath()
        self.mydir = Filename(self.mydir)
        self.mydir = self.mydir.toOsSpecific()
       
        self.setupWASD()
            
        taskMgr.add(self.rotateWorld, "rotateWorldTask")
        taskMgr.add(self.missileSeek, "missileSeekTask")
            
        self.animalsleft = 2
        self.missiles = []
            
        taskMgr.add(self.textTask, "textTask")

        self.saucer.ship.setColorScale(1,1,1,1)
        self.missileSound = base.loader.loadSfx("Sounds/tankshot.wav")
        self.missileHitSound = base.loader.loadSfx("Sounds/missile.wav")
        self.xspeed = 0
        self.yspeed = 0
        #For recycler
        self.xbounds = 130
        self.currentpickupable = 0
        self.loadLevel()
        
        base.cTrav = CollisionTraverser()
        #set the collision handler to send event messages on collision
        self.cHandler = CollisionHandlerEvent()
        # %in is substituted with the name of the into object
        self.cHandler.setInPattern("%fn-%in")
        self.setupCollisions()
        self.accept("beam-pickupable", self.beamCollide)
        self.accept("ship-tankdetect", self.tankShoot)
        self.accept("missile-ship", self.missileHit)

       #print "Level " + str(self.Lvl) 
        self.accept("space", self.loseGame)#Goes to Level Failed screen. For testing purposes
        self.accept("C1_X_DOWN", self.loseGame)
        self.accept("backspace", self.winGame) #Goes to Level Complete screen. For testing purposes
        self.accept("C1_Y_DOWN", self.winGame)
      
    def loseGame(self):
        self.levelComplete = False
        #Clear stuff
        taskMgr.remove('rotateWorldTask')
        taskMgr.remove('textTask')
        taskMgr.remove('abductTask')
        taskMgr.remove('moveTask')
        
        self.env.removeNode()          
        del self.env
        self.saucer.ship.removeNode()         
        del self.saucer.ship
        self.saucer.beam.removeNode()         
        del self.saucer.beam
        self.timeroutline.removeNode()
        del self.timeroutline
        self.TimeText.destroy()
        del self.TimeText
        
        for i in range(0,len(self.pickupables)):
            self.pickupables[i].pickup.removeNode()
            del self.pickupables[i].pickup
        
        self.texte = OnscreenText(text="You Lose!",style=1, fg=(0.8,0,0.1,1),pos=(0, 0), scale = .2,mayChange = 1,align=TextNode.ACenter)
        self.textd = OnscreenText(text="Press Enter or Start to restart!",style=1, fg=(0.8,0,0.1,1),pos=(0, -.88), scale = .06,mayChange = 1,align=TextNode.ACenter)
        self.accept("enter", self.nextLevel)
        self.accept("C1_START_DOWN", self.nextLevel)
        
    def winGame(self):
        self.levelComplete = True
        #Clear Stuff
        taskMgr.remove('rotateWorldTask')
        taskMgr.remove('textTask')
        taskMgr.remove('abductTask')
        taskMgr.remove('moveTask')
        
        
        self.env.removeNode()          
        del self.env
        self.saucer.ship.removeNode()         
        del self.saucer.ship
        self.saucer.beam.removeNode()         
        del self.saucer.beam
        
        self.AnimalsLeft.destroy()
        del self.AnimalsLeft
        self.AnimalsLeftText.destroy()
        del self.AnimalsLeftText
        for i in range(0,len(self.pickupables)):
            self.pickupables[i].pickup.removeNode()
            del self.pickupables[i].pickup
        
        if self.medal == "Gold":
            self.medalImage = OnscreenImage(image = 'Art/gold.png', pos = (1.1, 0, .46), scale = (.2,1,.2))
        elif self.medal == "Silver":
            self.medalImage = OnscreenImage(image = 'Art/silver.png', pos = (1.1, 0, .46), scale = (.125,1,.225))
        elif self.medal == "Bronze":
            self.medalImage = OnscreenImage(image = 'Art/bronze.png', pos = (1.1, 0, .46), scale = (.15,.1,.2))    
        
        if self.Lvl < 4:
            self.texte = OnscreenText(text="Level Complete!",style=1, fg=(0.8,0,0.1,1),pos=(0, 0), scale = .2,mayChange = 1,align=TextNode.ACenter)
            self.textd = OnscreenText(text="Press Enter or Start to go to next level!",style=1, fg=(0.8,0,0.1,1),pos=(0, -.88), scale = .06,mayChange = 1,align=TextNode.ACenter)
            self.Lvl += 1
            self.accept("enter", self.nextLevel)
            self.accept("C1_START_DOWN", self.nextLevel)
        else:
            self.texte = OnscreenText(text="You Finished the Game!",style=1, fg=(0.8,0,0.1,1),pos=(0, 0), scale = .2,mayChange = 1,align=TextNode.ACenter)
    def nextLevel(self):
        self.skybox.removeNode()          
        del self.skybox
        self.texte.destroy()
        del self.texte
        self.textd.destroy()
        del self.textd
        
        if self.levelComplete == True:
            self.timeroutline.removeNode()
            del self.timeroutline
            self.TimeText.destroy()
            del self.TimeText
            self.medalImage.removeNode()          
            del self.medalImage
        if self.levelComplete == False:
            self.AnimalsLeft.destroy()
            del self.AnimalsLeft
            self.AnimalsLeftText.destroy()
            del self.AnimalsLeftText   

        self.startGame()
        
    def gameControls360(self):   
        #Accept each message and do something based on the button
        self.accept("C1_A_DOWN", self.setKey, ["k", 1])
        self.accept("C1_A_UP", self.setKey,["k",0])
        self.accept("C1_B_DOWN", self.setKey, ["l", 1])
        self.accept("C1_B_UP", self.setKey,["l",0])
        
        self.accept("C1_DPAD_UP", self.setKey, ["w", 1])
        self.accept("C1_DPAD_DOWN", self.setKey,["s",1])
        self.accept("C1_DPAD_LEFT", self.setKey, ["a", 1])
        self.accept("C1_DPAD_RIGHT", self.setKey, ["d", 1])
        self.accept("C1_DPAD_NONE", self.stop,["w",0,"s",0,"a",0,"d",0])
        self.accept("C1_DPAD_UPLEFT", self.diagkeys, ["w",1,"a",1])
        self.accept("C1_DPAD_UPRIGHT", self.diagkeys, ["w",1,"d",1])
        self.accept("C1_DPAD_DOWNLEFT", self.diagkeys, ["s",1,"a",1])
        self.accept("C1_DPAD_DOWNRIGHT", self.diagkeys, ["s",1,"d",1])
        
        self.accept("C1_LSTICK_HARDUP", self.setKey, ["w", 1])
        self.accept("C1_LSTICK_SLIGHTUP", self.setKey, ["w", 0])
        self.accept("C1_LSTICK_HARDDOWN", self.setKey,["s",1])
        self.accept("C1_LSTICK_SLIGHTDOWN", self.setKey,["s",0])
        self.accept("C1_LSTICK_HARDLEFT", self.setKey, ["a", 1])
        self.accept("C1_LSTICK_SLIGHTLEFT", self.setKey, ["a", 0])
        self.accept("C1_LSTICK_HARDRIGHT", self.setKey, ["d", 1])
        self.accept("C1_LSTICK_SLIGHTRIGHT", self.setKey, ["d", 0])
        
    def blank(self):
        x=1
        
        
    def stop(self, key1, value1, key2, value2, key3, value3, key4, value4):
        self.keyMap[key1] = value1
        self.keyMap[key2] = value2
        self.keyMap[key3] = value3
        self.keyMap[key4] = value4
    def diagkeys(self, key1, value1, key2, value2):
        self.keyMap[key1] = value1
        self.keyMap[key2] = value2    



    def setupWASD(self):
        self.accept("w", self.setKey, ["w", 1])
        self.accept("w-up", self.setKey, ["w", 0])
        self.accept("s", self.setKey, ["s", 1])
        self.accept("s-up", self.setKey, ["s", 0])
        self.accept("a", self.setKey, ["a", 1])
        self.accept("a-up", self.setKey, ["a", 0])
        self.accept("d", self.setKey, ["d", 1])
        self.accept("d-up", self.setKey, ["d", 0])
            

    def loadLevel(self):
        #self.map = open("C:\Users\Vanded3\Documents\ufo-game2\Code\Levels\level1.txt")
        #self.map = "CC0CCCCCCCC000CCCCCCCCCC00CCCCCCCCCCCCC"
        self.map = open (self.mydir + "\Levels\level" + str(self.Lvl) + ".txt")
        self.map = [line.rstrip() for line in self.map]
        #self.terrainlist = []
        tsize = 4
                
        self.pickupables = []
        #self.animals = []
        #self.inanimates = []
        #self.hostiles = []
        worldhalfwidth = 240
        worldradius = 43
        
        for i, row in enumerate(self.map):
            for j, column in enumerate(row):
                if column == "-":
                    pass
                if column == "C":
                    temp = Pickupable("animal","cow")
                    temp.pickup.reparentTo(self.env)
                    #print("in cow")
                    temp.pickup.setScale(1)
                    angle = i * .1
                    y = worldradius * math.cos(angle)
                    z = worldradius * math.sin(angle)
                    temp.pickup.setPos((j * tsize)-worldhalfwidth, y, z)
                    rotangle = math.degrees(math.atan2((z - 0), (y - 0)))
                    temp.pickup.setHpr(0,rotangle - 90,0)
                    temp.pickup.setH(temp.pickup, random.randint(0,360))
                    #positioning : i*tsize
                    #temp.pickup.reparentTo(self.env)
                    self.pickupables.append(temp)
                   #print (len(self.pickupables)) 
                if column == "S":
                    temp = Pickupable("animal", "sheep")
                    temp.pickup.setScale(1)
                    angle = i * .1
                    y = worldradius * math.cos(angle)
                    z= worldradius * math.sin(angle)
                    temp.pickup.setPos((j * tsize)-worldhalfwidth, y, z)
                    rotangle = math.degrees(math.atan2((z - 0), (y - 0)))
                    temp.pickup.setHpr(0,rotangle - 90,0)
                    temp.pickup.setH(temp.pickup, random.randint(0,360))
                    #positioning : i*tsize
                    temp.pickup.reparentTo(self.env)
                    self.pickupables.append(temp)
                   #print("in S")
                if column == "P":
                    temp = Pickupable("inanimate", "silo")
                    temp.pickup.setScale(1)
                    angle = i * .1
                    y = worldradius * math.cos(angle)
                    z= worldradius * math.sin(angle)
                    temp.pickup.setPos((j * tsize)-worldhalfwidth, y, z)
                    rotangle = math.degrees(math.atan2((z - 0), (y - 0)))
                    temp.pickup.setHpr(0,rotangle - 90,0)
                    temp.pickup.setH(temp.pickup, random.randint(0,360))
                    #positioning : i*tsize
                    temp.pickup.reparentTo(self.env)
                    self.pickupables.append(temp)
                    #print("in P")
                if column == "0":
                    temp = Pickupable("animal", "pig")
                    temp.pickup.setScale(1)
                    angle = i * .1
                    y = worldradius * math.cos(angle)
                    z= worldradius * math.sin(angle)
                    temp.pickup.setPos((j * tsize)-worldhalfwidth, y, z)
                    rotangle = math.degrees(math.atan2((z - 0), (y - 0)))
                    temp.pickup.setHpr(0,rotangle - 90,0)
                    temp.pickup.setH(temp.pickup, random.randint(0,360))
                    #positioning : i*tsize
                    temp.pickup.reparentTo(self.env)
                    self.pickupables.append(temp)
                    #print("in B")
                if column == "M":    
                    temp = Pickupable("hostile", "tank")
                    temp.pickup.setScale(1)
                    angle = i * .1
                    y = worldradius * math.cos(angle)
                    z= worldradius * math.sin(angle)
                    temp.pickup.setPos((j * tsize)-worldhalfwidth, y, z)
                    rotangle = math.degrees(math.atan2((z - 0), (y - 0)))
                    temp.pickup.setHpr(0,rotangle - 90,0)
                    temp.pickup.setH(temp.pickup, random.randint(0,360))
                    #positioning : i*tsize
                    temp.pickup.reparentTo(self.env)
                    self.pickupables.append(temp)
                    #print("in M")
                if column == "N":
                    temp = Pickupable("inanimate", "tractor")
                    temp.pickup.setScale(1)
                    angle = i * .1
                    y = worldradius * math.cos(angle)
                    z= worldradius * math.sin(angle)
                    temp.pickup.setPos((j * tsize)-worldhalfwidth, y, z)
                    rotangle = math.degrees(math.atan2((z - 0), (y - 0)))
                    temp.pickup.setHpr(0,rotangle - 90,0)
                    temp.pickup.setH(temp.pickup, random.randint(0,360))
                    #positioning : i*tsize
                    temp.pickup.reparentTo(self.env)
                    self.pickupables.append(temp)    
                   #print("in N")
                if column == "B":
                    temp = Pickupable("inanimate", "barn")
                    temp.pickup.setScale(1)
                    angle = i * .1
                    y = worldradius * math.cos(angle)
                    z= worldradius * math.sin(angle)
                    temp.pickup.setPos((j * tsize)-worldhalfwidth, y, z)
                    rotangle = math.degrees(math.atan2((z - 0), (y - 0)))
                    temp.pickup.setHpr(0,rotangle - 90,0)
                    temp.pickup.setH(temp.pickup, random.randint(0,360))
                    #positioning : i*tsize
                    temp.pickup.reparentTo(self.env)
                    self.pickupables.append(temp)    
                   #print("in N")
                if column == "W":
                    temp = Pickupable("inanimate", "cage")
                    temp.pickup.setScale(1)
                    angle = i * .1
                    y = worldradius * math.cos(angle)
                    z= worldradius * math.sin(angle)
                    temp.pickup.setPos((j * tsize)-worldhalfwidth, y, z)
                    rotangle = math.degrees(math.atan2((z - 0), (y - 0)))
                    temp.pickup.setHpr(0,rotangle - 90,0)
                    temp.pickup.setH(temp.pickup, random.randint(0,360))
                    #positioning : i*tsize
                    temp.pickup.reparentTo(self.env)
                    self.pickupables.append(temp)    
                   #print("in N")
                   #print len(self.pickupables)    
        #self.env.setX(self.env.getX() - 60)
        #self.env.setP(self.env.getP() + 60)
      
    def setKey(self, key, value):
        self.keyMap[key] = value
        
    def rotateWorld(self,task): #Handles saucer movement, world rotation etc
        elapsed = task.time - self.prevtime
        self.prevtime = task.time
        
        # Create a handle for pointer device #0
        #m = base.win.getPointer( 0 )
        # Get the absolute [x,y] screen coordinates of the cursor
        #x = m.getX( )
        #y = m.getY( )

        centerx = 400
        centery = 300

        xmov = 0
        ymov = 0
        accel = 0
        dir = -1
        
        if self.keyMap["l"]:
            self.saucer.drop(self.env)
            #for object in self.saucer.abductlist:
                #object.abduct = False
                #object.pickup.wrtReparentTo(self.env)
                #object.pickup.setPos(self.saucer.dummy2.getX(),self.saucer.dummy2.getY(),self.saucer.dummy2.getZ())
                #camera.lookAt(object.pickup)

        if self.keyMap["k"]:
            if self.tractorbeamsound.status() != AudioSound.PLAYING:
                self.tractorbeamsound.play()
        
            self.saucer.beamon = True
            
            if self.xspeed > 30:
                self.xspeed = 30
            elif self.xspeed < -30:
                self.xspeed = -30
            if self.yspeed > 30:
                self.yspeed = 30
            elif self.yspeed < -30:
                self.yspeed = -30
            
            if self.keyMap["w"]:
                dir = 270
            if self.keyMap["s"]:
                dir = 90
            if self.keyMap["a"]:
                dir = 180
            if self.keyMap["d"]:
                dir = 0
            if self.keyMap["w"] and self.keyMap["d"]:
                dir = 315
            if self.keyMap["w"] and self.keyMap["a"]:
                dir = 225
            if self.keyMap["s"] and self.keyMap["a"]:
                dir = 135
            if self.keyMap["s"] and self.keyMap["d"]:
                dir = 45
            
            if dir != -1:
                xmov = 26 * math.cos(math.radians(dir))
                ymov = 26 * math.sin(math.radians(dir))
            
            if xmov == 0 and ymov == 0:   
                accel = .1
            else:   
                accel = .035
        else:
            self.saucer.beamon = False
            if self.tractorbeamsound.status() == AudioSound.PLAYING:
                self.tractorbeamsound.stop()
            
            if self.keyMap["w"]:
                dir = 270
            if self.keyMap["s"]:
                dir = 90
            if self.keyMap["a"]:
                dir = 180
            if self.keyMap["d"]:
                dir = 0
            if self.keyMap["w"] and self.keyMap["d"]:
                dir = 315
            if self.keyMap["w"] and self.keyMap["a"]:
                dir = 225
            if self.keyMap["s"] and self.keyMap["a"]:
                dir = 135
            if self.keyMap["s"] and self.keyMap["d"]:
                dir = 45
            
            if dir != -1:
                xmov = 40 * math.cos(math.radians(dir))
                ymov = 40 * math.sin(math.radians(dir))
            accel = .07

            
        #if base.win.movePointer( 0, centerx, centery ):
        #       xmov += ( x - centerx ) * 1
        #       ymov += ( y - centery ) * 1

        if self.env.getX() > self.xbounds:
            if xmov < 0:
                xmov = 0
        elif self.env.getX() < -self.xbounds:
            if xmov > 0:
                xmov = 0
               
        self.xspeed = self.xspeed + ( (xmov - self.xspeed) * accel)
        self.yspeed = self.yspeed + ( (ymov - self.yspeed) * accel)
          
        
          
        self.env.setX(self.env.getX() + elapsed * -self.xspeed)
        self.env.setP(self.env.getP() + elapsed * -self.yspeed)
        
        self.skybox.setX(self.skybox.getX() + elapsed * -.3 * self.xspeed)
        self.skybox.setP(self.skybox.getP() + elapsed * -.1 * self.yspeed)
     
        self.saucer.ship.setR(self.xspeed * .2)
        self.saucer.ship.setP(self.yspeed * .2)
            
        ##print self.env.getX()
        return Task.cont
            
    def loadModels(self):
        self.env = loader.loadModel("Art/world.egg")
        self.env.reparentTo(render)
        self.env.setScale(1)
        self.env.setPos(0, 0, -55)
        
        self.skybox = loader.loadModel("Art/skytube.egg")
        self.skybox.reparentTo(render)
        self.skybox.setScale(2)
        self.skybox.setPos(0, 0, 0)
        self.skybox.setHpr(0,-60,0)
        
        
        #Shadow Code:
        proj = render.attachNewNode(LensNode('proj'))
        lens = PerspectiveLens()
        proj.node().setLens(lens)
        #The following is for debugging:
        #proj.node().showFrustum()  
        #proj.find('frustum').setColor(1, 0, 0, 1)
        proj.reparentTo(render)
        proj.setPos(self.saucer.ship.getPos())
        proj.setZ(-2)
        proj.setHpr(0,-90,0)
        tex = loader.loadTexture('Art\UFO_Shadow.png')
        tex.setWrapU(Texture.WMBorderColor)
        tex.setWrapV(Texture.WMBorderColor)
        tex.setBorderColor(VBase4(1, 1, 1, 0))
        ts = TextureStage('ts')
        ts.setSort(1)
        ts.setMode(TextureStage.MDecal)
        self.env.projectTexture(ts, tex, proj)

    def loadHUD(self):
        #Draw image as outline for timer
        self.timeroutline = OnscreenImage(image = 'Art/timer.png', pos = (1.1, 0, .86), scale = (.15,.1,.1))
       
        #Draw num of animals left
        num = str(200000)
        self.AnimalsLeft = OnscreenText(text="Animals Left:",style=1, fg=(0,0,0,1),pos=(-1,.9), scale = .07,mayChange = 1)
        self.AnimalsLeftText = OnscreenText(text=num,style=1, fg=(0,0,0,1),pos=(-1,0.8), scale = .09,mayChange = 1,align = TextNode.ALeft)
       
       #Draw time        
        t = "0:00"
        self.TimeText = OnscreenText(text=t,style=1, fg=(0,0,0,1),pos=(1,0.85), scale = .09, mayChange = 1, align = TextNode.ALeft)

    def dCharstr(self,number):
        theString = str(number)
        if len(theString) != 2:
            theString = '0' + theString
        return theString
        
    def textTask(self,task):
        secondsTime = int(task.time)
        minutesTime = int(secondsTime/60)
        
        self.seconds = secondsTime%60
        self.minutes = minutesTime
        
        self.mytimer = str(self.minutes) + ":" + self.dCharstr(int(self.seconds))
       #self.mytimer = str(self.seconds)

        self.TimeText.setText(self.mytimer)
        
        medal = "No Medal"
        self.medal = medal
        if task.time <= 5:
            self.medal = "Gold"
        elif task.time > 5 and task.time <=10:
            self.medal = "Silver"
        elif task.time > 10:
            self.medal = "Bronze"
        
        self.AnimalsLeftText.setText(str(self.animalsleft))
        return Task.cont
    

    def setupLights(self):
        """loads initial lighting"""
        self.dirLight = DirectionalLight("dirLight")
        self.dirLight.setColor((.6, .6, .6, 1))
        #create a NodePath, and attach it directly into the scene
        self.dirLightNP = render.attachNewNode(self.dirLight)
        self.dirLightNP.setHpr(0, -25, 0)
        #the NP that calls setLight is what gets lit
        render.setLight(self.dirLightNP)
        # clearLight() turns it off
        
        self.ambientLight = AmbientLight("ambientLight")
        self.ambientLight.setColor((.25, .25, .25, 1))
        self.ambientLightNP = render.attachNewNode(self.ambientLight)
        render.setLight(self.ambientLightNP)
        
    def setupCollisions(self):

        cSphere = CollisionSphere((0,0,0), 2)
        cNode = CollisionNode("ship")
        cNode.addSolid(cSphere)
        cNodePath = self.saucer.ship.attachNewNode(cNode)
        base.cTrav.addCollider(cNodePath, self.cHandler)

        
        #saucer collider
        cSphere = CollisionSphere((0,0,0), 2)
        cNode = CollisionNode("beam")
        cNode.addSolid(cSphere)
        #set to only be a "from" object
        cNode.setIntoCollideMask(BitMask32.allOff())
        cNodePath = self.saucer.dummy.attachNewNode(cNode)
        cNodePath.setZ(-36)
        #cNodePath.show()
        base.cTrav.addCollider(cNodePath, self.cHandler)
        
        #target colliders
        for p in self.pickupables:
            cSphere = CollisionSphere((0,0,0), 1)
            cNode = CollisionNode("pickupable")
            cNode.addSolid(cSphere)
            cNodePath = p.pickup.attachNewNode(cNode)

            if p.type2 == "tank":
                cSphere = CollisionSphere((0,0,0), 45)
                cNode = CollisionNode("tankdetect")
                cNode.addSolid(cSphere)
                cNodePath = p.pickup.attachNewNode(cNode)
                #cNodePath.show()
    
    def beamCollide(self, cEntry):
        if self.saucer.beamon:
            obj = cEntry.getIntoNodePath().getParent()
            
            for x in self.pickupables:
                if (x.pickup == obj):
                    self.saucer.pickUp(x)
                    return

    def tankShoot(self, cEntry):
        tank = cEntry.getIntoNodePath()
        newMissile = Missile()
        newMissile.model.reparentTo(tank.getParent())
        cSphere = CollisionSphere((0,0,0), 2)
        cNode = CollisionNode("missile")
        cNode.addSolid(cSphere)
        cNodePath = newMissile.model.attachNewNode(cNode)
        base.cTrav.addCollider(cNodePath, self.cHandler)
        self.missiles.append(newMissile)
        self.missileSound.play()

    def missileSeek(self, task):
        for i in self.missiles:
            i.seek(self.saucer.ship)

        return Task.cont

    def missileHit(self, cEntry):
        aMissile = cEntry.getFromNodePath().getParent()
        for i in self.missiles:
            if i.model == aMissile:
                self.missileHitSound.play()
                i.model.removeNode()
                self.missiles.remove(i)
                self.saucer.health -= 20
                if self.saucer.health <=0:
                    self.loseGame()
                elif self.saucer.health <= 50:
                    self.saucer.ship.setColorScale(1,.5,.5,1)
                return
        
w = World()
run()