import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import *    #basic Panda modules
from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import *  #for compound intervals
from direct.task import Task         #for update functions
import sys, math, random

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
        self.type2 = 'pig'
        #Linked to how fast it is sucked up
        self.weight = 1
        
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
        if self.type == 'animal':
            self.pickup = loader.loadModel(type2)
            self.weight = 1
        if self.type ==  'inanimate':
            self.pickup = loader.loadModel(type2)
            self.weight = 2
        if self.type ==  'hostile':
            self.pickup = loader.loadModel(type2)
            self.weight = 3           

        self.pickup.setScale(1)
        
    def create(self,x,y,z):
        self.alive = True
        self.pickup.reparentTo(render)
        self.pickup.setPos(0,0,0)
        
    def rise(self): #The ship should call this in one of its tasks on every animal that it is currently abducting.   
        self.height += .1 * self.weight
        if self.height >= self.abductheight:
            self.abducted()
            
    def abducted(self):
        self.die()
    
    def die(self):      #Set self to dead, remove from render node. For recycler.
        pickup.detachNode()
        self.alive = False
        
    def moveTask(self): #Responsible for falling when dropped, walking around(??)
        if abduct == False:
            if self.height > 0:
                self.fallspeed = self.fallspeed + ((.5 - self.fallspeed) * .05)
                self.height -= self.fallspeed
            elif self.height  < 0:
                self.height  == 0
            