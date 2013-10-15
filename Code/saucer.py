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
        self.animals = []
        self.inanimates = []
        taskMgr.add(self.abductTask, "abductTask")
        self.stuntime = 20
        self.stunbase = 20
        self.updown = False
        self.beamspeed = 1
        self.basebeamspeed = 1

    def pickUp(self,object):   #Pick up another pickupable 
        if object.stuncount < self.stuntime:
            object.stunned = True
        else:
            if (len(self.abductlist) < 15):
                if object.type == 'inanimate':
                    self.inanimates.append(object)
                elif object.type == 'hostile':
                    self.inanimates.append(object)
                elif object.type == 'animal':
                    self.animals.append(object)
                    
                self.findSpeed()
                
                object.resetStun()
                object.abduct = True
                self.abductlist.append(object)
                object.playAnimalSound()
                object.pickup.reparentTo(self.dummy2)
                object.pickup.setHpr(0,0,0)
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

    def cowbig(self,me):
        if me > self.panda and me > self.pigs and me > self.sheep:
            return True
    def pigbig(self,me):
        if me > self.cows and me > self.sheep and me > self.panda:
            return True
    def sheepbig(self,me):
        if me > self.cows and me > self.pigs and me > self.panda:
            return True
    def pandabig(self,me):
        if me > self.cows and me > self.pigs and me > self.sheep:
            return True            


    def biggest(self):
        if self.cowbig(self.cows):
            return self.cows - ((self.pigs + self.sheep + self.panda) / 3)
        if self.pigbig(self.pigs):
            return self.pigs - ((self.cows + self.sheep + self.panda) / 3)
        if self.sheepbig(self.sheep):
            return self.sheep - ((self.pigs + self.cows + self.panda) / 3)
        if self.pandabig(self.panda):
            return self.panda - ((self.pigs + self.sheep + self.cows) / 3)
          
        return 0
    def findSpeed(self):
        self.cows = 0
        self.pigs = 0
        self.sheep = 0
        self.panda = 0
        for animal in self.animals:
            if animal.type2 == 'cow':
                self.cows += 1
            if animal.type2 == 'pig':
                self.pigs += 1
            if animal.type2 == 'sheep':
                self.sheep += 1
            if animal.type2 == 'panda':
                self.panda += 1
        
        speedadd = self.biggest() * 2
        
        speeddeduct = len(self.inanimates)
        self.beamspeed = self.basebeamspeed - speeddeduct + speedadd
        self.stuntime = self.stunbase - (self.beamspeed * 1.5)
        
        if self.stuntime < 2:
            self.stuntime = 2
        
        if self.beamspeed < .6:
            self.beamspeed = .6