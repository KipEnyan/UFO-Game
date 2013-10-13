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
        self.ship.reparentTo(render)
        self.ship.setScale(1)
        #self.ship.setH(180)
        self.ship.setPos(0,0,0)
        
        #list of things currently abducting
        self.abductlist = []
        
    def pickUp(self,object):   #Pick up another pickupable
        if len(self.abductlist < 5):
            object.abduct = True
            self.abductlist.append(object)
            object.playAnimalSound()
        else:
            print ("Pickup list full.")
    
    def drop(self): #Drop all
        for object in self.abductlist:
            object.abduct = False
        self.abductlist = []
        