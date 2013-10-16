import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import *    #basic Panda modules
from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import *  #for compound intervals
from direct.task import Task         #for update functions
import sys, math, random,os

from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect

class Saucer(DirectObject):
    def __init__(self):
    
        self.ship = loader.loadModel("Art\ufo.egg")
        self.beam = loader.loadModel("Art\eam.egg")
        self.health = 100
      
        #Dummy is used to position the tractor beam collisionsphere
        self.dummy = NodePath('dummy')
        self.dummy.reparentTo(render)
        
        #Dummy2 used to position abductees
        self.dummy2 =  NodePath('dummy2')
        self.dummy2.reparentTo(render)

        self.beam.reparentTo(self.dummy2)
        
        self.glownode = self.ship.find("**/l_glownode")
        self.glownode.setColor(0,0,.5,1)
        
        self.glownode2 = self.ship.find("**/r_glownode")
        self.glownode2.setColor(0,0,.5,1)
            
        self.ship.reparentTo(render)
        self.ship.setScale(1)
        #self.ship.setH(180)
        self.ship.setPos(0,0,25)
        self.dummy.setPos(0,0,25)
        self.dummy2.setPos(0,0,25)
        
        #list of things currently abducting
        self.abductlist = []
        self.animals = []
        self.inanimates = []
        taskMgr.add(self.abductTask, "abductTask")
        taskMgr.add(self.lightTask, "lightTask")
        self.stuntime = 30
        self.stunbase = 30
        self.updown = False
        self.beamspeed = 1
        self.basebeamspeed = 1
        
        self.collected = 0
        
        self.beamon = True
        
        taskMgr.add(self.particleTask, "shipparticleTask")

        self.mydir = os.path.abspath(sys.path[0])
        self.mydir = Filename.fromOsSpecific(self.mydir).getFullpath()
        self.mydir = Filename(self.mydir)
        #self.mydir = self.mydir.toOsSpecific()
        
        self.abductp = ParticleEffect()
        self.abductp.loadConfig(self.mydir + '/abduct.ptf')
        self.pcount = 0
        self.particletime = 60 #Must be integer 

    def pickUp(self,object):   #Pick up another pickupable 
        if object.stuncount < self.stuntime:
            object.stunned = True
        else:
            if (len(self.abductlist) < 15):
                if object.type1 == 'inanimate':
                    self.inanimates.append(object)
                elif object.type1 == 'hostile':
                    self.inanimates.append(object)
                elif object.type1 == 'animal':
                    self.animals.append(object)
                    
                self.findSpeed()
                
                object.resetStun()
                object.abduct = True
                self.abductlist.append(object)
                object.playPickupSound()
                object.pickup.reparentTo(self.dummy2)
                object.pickup.setHpr(0,0,0)
                object.pickup.setPos(0,0,-37)
            else:
                print ("Pickup list full.")
    
    def drop(self,env): #Drop all
        for object in self.abductlist:
            object.abduct = False
            object.pickup.wrtReparentTo(env)
            #object.pickup.setPos(self.dummy2.getX(),self.dummy2.getY(),self.dummy2.getZ())
        self.abductlist[:] = []
 
    def lightTask(self,task):
        if not self.beamon:
            self.glownode.setColor(.1,.06,.92,1)
            self.glownode2.setColor(.1,.06,.92,1)
        if self.beamon:
            s = self.beamspeed/25     
            self.glownode.setColor(.12 - s/10,1 - s,.08 - s/10,1)
            self.glownode2.setColor(.12 - s/10,1 - s,.08- s/10,1)
        return task.cont
            
    def abductTask(self,task):
        if self.updown:
            self.dummy.setZ(self.ship.getZ())
            self.updown = False
        else:
            self.dummy.setZ(36)
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
        
        speedadd = self.biggest() * 1.7
        
        speeddeduct = len(self.inanimates)
        self.beamspeed = self.basebeamspeed - speeddeduct + speedadd
        self.stuntime = self.stunbase - (self.beamspeed * 1.5)
        
        if self.stuntime < 2:
            self.stuntime = 2
        
        #Minimum beam speed
        if self.beamspeed < 1:
            self.beamspeed = 1
            
    def abductAnimal(self):
        self.pcount = self.particletime
        self.abductp.start(parent = self.ship, renderParent = self.ship)
        self.collected += 1

        
    def particleTask(self,task):
        if self.pcount > 0:
            self.pcount -= 1
        elif self.pcount == 0:
            self.pcount = -1
            #self.abductp.reset()
            self.abductp.disable()
            
        return task.cont
