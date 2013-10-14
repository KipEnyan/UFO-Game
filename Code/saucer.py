import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import *    #basic Panda modules
from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import *  #for compound intervals
from direct.task import Task         #for update functions
import sys, math, random

class Saucer(DirectObject):
    def __init__(self):
    
        self.ship = loader.loadModel("Art\ufo.egg")
        #self.beam = loader.loadmodel("Art\
      
        #Dummy is used to position the tractor beam collisionsphere
        self.dummy = NodePath('dummy')
        self.dummy.reparentTo(render)
        
        #Dummy2 used to position abductees
        self.dummy2 =  NodePath('dummy2')
        self.dummy2.reparentTo(render)

        
        
        
        self.ship.reparentTo(render)
        self.ship.setScale(1)
        #self.ship.setH(180)
        self.ship.setPos(0,0,15)
        self.dummy.setPos(0,0,15)
        self.dummy2.setPos(0,0,15)
        
        #list of things currently abducting
        self.abductlist = []
        taskMgr.add(self.abductTask, "abductTask")
        self.stuntime = 50
        self.updown = False

    def pickUp(self,object):   #Pick up another pickupable 
        if object.stuncount < self.stuntime:
            object.stunned = True
        else:
            if (len(self.abductlist) < 5):
                object.resetStun()
                object.abduct = True
                self.abductlist.append(object)
                object.playAnimalSound()
                object.pickup.reparentTo(self.dummy2)
                object.pickup.setPos(0,0,-26)
            else:
                print ("Pickup list full.")
    
    def drop(self): #Drop all
        for object in self.abductlist:
            object.abduct = False
            object.pickup.reparentTo(render)
        self.abductlist = []
        
    def abductTask(self,task):
        if self.updown:
            self.dummy.setZ(self.ship.getZ())
            self.updown = False
        else:
            self.dummy.setZ(25)
            self.updown = True
    
        for obj in self.abductlist:
            obj.rise(self)
            
        return Task.cont
        