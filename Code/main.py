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

from saucer import*
from pickupable import*

del base

class World(DirectObject):
    def __init__(self):

        self.saucer = Saucer()
        base.disableMouse()
        camera.setPosHpr(0, -40, 80, 0, -15, 0)
        self.loadModels()
        self.loadHUD()
        self.setupLights()
        self.keyMap = {"left":0, "right":0,"w":0,"a":0,"s":0,"d":0}
        self.prevtime = 0
        self.accept("escape", sys.exit)
        
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
        
        
        
        
        
        self.setupWASD()
        
        taskMgr.add(self.rotateWorld, "rotateWorldTask")
        self.xspeed = 0
        self.yspeed = 0
        camera.lookAt(self.saucer.ship)
        #For recycler
        self.xbounds = 92
        self.currentpickupable = 0
        

    def setupWASD(self):
        self.accept("w", self.setKey, ["w", 1])
        self.accept("w-up", self.setKey, ["w", 0])
        self.accept("s", self.setKey, ["s", 1])
        self.accept("s-up", self.setKey, ["s", 0])
        self.accept("a", self.setKey, ["a", 1])
        self.accept("a-up", self.setKey, ["a", 0])
        self.accept("d", self.setKey, ["d", 1])
        self.accept("d-up", self.setKey, ["d", 0])
            
        
    def setKey(self, key, value):
        self.keyMap[key] = value
        
    def rotateWorld(self,task):
        elapsed = task.time - self.prevtime
        self.prevtime = task.time
        
        # Create a handle for pointer device #0
        m = base.win.getPointer( 0 )
        # Get the absolute [x,y] screen coordinates of the cursor
        x = m.getX( )
        y = m.getY( )

        centerx = 400
        centery = 300

        xmov = 0
        ymov = 0
        
        if self.keyMap["w"]:
            ymov = -40
        if self.keyMap["s"]:
            ymov = 40
        if self.keyMap["a"]:
            xmov = -40
        if self.keyMap["d"]:
            xmov = 40   
            
        if base.win.movePointer( 0, centerx, centery ):
               xmov += ( x - centerx ) * 2
               ymov += ( y - centery ) * 2

        if self.env.getX() > self.xbounds:
            if xmov < 0:
                xmov = 0
        elif self.env.getX() < -self.xbounds:
            if xmov > 0:
                xmov = 0
               
        self.xspeed = self.xspeed + ( (xmov - self.xspeed) * .1)
        self.yspeed = self.yspeed + ( (ymov - self.yspeed) * .1)
          
          
        self.env.setX(self.env.getX() + elapsed * -self.xspeed)
        self.env.setP(self.env.getP() + elapsed * -self.yspeed)
     
        self.saucer.ship.setR(self.xspeed * .2)
        self.saucer.ship.setP(self.yspeed * .2)
            
        print self.env.getX()
        return Task.cont
            
    def loadModels(self):
        self.env = loader.loadModel("Art/cylinder.egg")
        self.env.reparentTo(render)
        self.env.setScale(40)
        self.env.setPos(0, 0, -55)
        
        #Shadow Code:
        proj = render.attachNewNode(LensNode('proj'))
        lens = PerspectiveLens()
        proj.node().setLens(lens)
        #The following is for debugging:
        proj.node().showFrustum()  
        proj.find('frustum').setColor(1, 0, 0, 1)
        proj.reparentTo(render)
        proj.setPos(self.saucer.ship.getPos())
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
        timeroutline = OnscreenImage(image = 'Art/timer.png', pos = (1.1, 0, .86), scale = (.15,.1,.1))
       
        #Draw num of animals left
        num = str(200000)
        AnimalsLeft = OnscreenText(text="Animals Left:",style=1, fg=(0,0,0,1),pos=(-1,.9), scale = .07,mayChange = 1)
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
        
        
        self.AnimalsLeftText.setText(str(self.animalsleft))
        return Task.cont
    
    def loadPickupables(self):
        #This function just loads a bunch of pickupables of random types.
        
        self.pickupables = []
        self.possibletypes = ['animal','inanimate','hostile']
        self.animaltypes = ['cow','pig','panda']
        self.inanimatetypes = ['house','car','tree']
        self.hostiletypes = ['tank','helicopter','launcher']
        for x in range(30):
            temp = Pickupable()
            type = random.choice(possibletypes)
            if type == 'animal':
                type2 = random.choice(animaltypes)
                temp.setType(type,type2)
            elif type == 'inanimate':
                type2 = random.choice(inanimatetypes)
                temp.setType(type,type2)
            elif type == 'hostile':
                type2 = random.choice(hostiletypes)
                temp.setType(type,type2)
                
        self.pickupables.append(temp)
        
    def spawnPickupable(self):  #Spawn the next pickupable in line from pickupable list
        self.pickupables[self.currentpickupable].alive = True
        self.currentpickupable += 1
        if self.currentpickupable > (len(self.pickupables) - 1):
            self.currentpickupable = 0
        
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
        
      
        
w = World()
run()