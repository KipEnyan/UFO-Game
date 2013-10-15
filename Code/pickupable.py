import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import *    #basic Panda modules
from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import *  #for compound intervals
from direct.task import Task         #for update functions
import sys, math, os, random

class Pickupable(DirectObject):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0 
    
        #For recycling
        self.alive = False
        
        #Type = class of object (animal, inanimate, hostile)
        self.type = 'animal'
        #Type2 = what kind of object of that class? (pig, cow, tank, car)
        self.type2 = 'cow'
        #Linked to how fast it is sucked up
        self.weight = 1
        #self.pickup = loader.loadModel("Art/" + self.type2 + ".egg")
        #self.pickup.setScale(1)
    
        #code to add sounds
        #thebase = ShowBase()
        self.cowsound = base.loadMusic("Sounds/cow.wav")
        self.cowsound2 = base.loadMusic("Sounds/cow1.wav")
        self.cowsound3 = base.loadMusic("Sounds/cow2.wav")
        self.cowsound4 = base.loadMusic("Sounds/cow3.wav")
        self.sheepsound = base.loadMusic("Sounds/sheep.wav")
        self.sheepsound2 = base.loadMusic("Sounds/sheep1.wav")
        self.sheepsound3 = base.loadMusic("Sounds/sheep2.wav")
        self.sheepsound4 = base.loadMusic("Sounds/sheep3.wav")
        self.pigsound = base.loadMusic("Sounds/cow.wav")
        self.pigsound2 = base.loadMusic("Sounds/cow1.wav")
        self.pigsound3 = base.loadMusic("Sounds/cow2.wav")
        self.pigsound4 = base.loadMusic("Sounds/cow3.wav")
        self.screamsound = base.loadMusic("Sounds/scream.wav")
        self.screamsound2 = base.loadMusic("Sounds/scream1.wav")
        self.screamsound3 = base.loadMusic("Sounds/scream2.wav")
        self.screamsound4 = base.loadMusic("Sounds/scream3.wav")
        
        #add animal sounds to lists
        self.cowsounds = [self.cowsound, self.cowsound2, self.cowsound3, self.cowsound4]
        self.sheepsounds = [self.sheepsound, self.sheepsound2, self.sheepsound3, self.sheepsound4]
        self.pigsounds = [self.pigsound, self.pigsound2, self.pigsound3, self.pigsound4]
        self.screamsounds = [self.screamsound, self.screamsound2, self.screamsound3, self.screamsound4]
        
        
        #Should point to player
        self.player = 0
        
        #Being abducted?
        self.abduct = False 
        #When pickupable height reaches this level, it is abducted.
        self.abductheight = 30
        
        #Height off of ground
        self.height = 0
        self.fallspeed = 0
        taskMgr.add(self.moveTask, "moveTask")
        
    def setType(self,type,type2):
        self.type = type
        self.type2 = type2
        if self.type == 'animal':
            self.pickup = loader.loadModel("Art/" + self.type2 + ".egg")
            self.weight = 1
        if self.type ==  'inanimate':
            self.pickup = loader.loadModel("Art/" + self.type2 + ".egg")
            self.weight = 2
        if self.type ==  'hostile':
            self.pickup = loader.loadModel("Art/" + self.type2 + ".egg")        

        self.pickup.setScale(1)
        
    def create(self,x,y,z):
        self.alive = True
        self.pickup.reparentTo(render)
        self.pickup.setPos(0,0,0)
        
    def rise(self): #The ship should call this in one of its tasks on every animal that it is currently abducting.   
        self.height += .1 * self.weight
        if self.height >= self.abductheight:
            self.abducted()
    
    def playAnimalSound(self):
        if self.type2 == 'pig':
            randSound = random.choice(self.pigsounds)
            randSound.play()
        if self.type2 == 'cow':
            randSound = random.choice(self.cowsounds)
            randSound.play()
        if self.type2 == 'sheep':
            randSound = random.choice(self.sheepsounds)
            randSound.play()    
        if self.type2 == 'panda':
            randSound = random.choice(self.pandasounds)
            randSound.play()
        if self.type == 'hostile':
            randSound = random.choice(self.screamsounds)
            randSound.play()
            
    
    
    
    def abducted(self):
        self.die()
    
    def die(self):      #Set self to dead, remove from render node. For recycler.
        pickup.detachNode()
        self.alive = False
        
    def moveTask(self,task): #Responsible for falling when dropped, walking around(??)
        if self.abduct == False:
            if self.height > 0:
                self.fallspeed = self.fallspeed + ((.5 - self.fallspeed) * .05)
                self.height -= self.fallspeed
            elif self.height  < 0:
                self.height  == 0
            