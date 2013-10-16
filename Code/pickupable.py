import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import *    #basic Panda modules
from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import *  #for compound intervals
from direct.task import Task         #for update functions
import sys, math, os, random

from panda3d.core import Filename
from utilities import resource_path

from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect

class Pickupable(DirectObject):
    def __init__(self, type1, type2):
        self.type1 = type1
        self.type2 = type2
        self.weight = 1
        self.pickupSounds = []

        if self.type1 == "animal":
            for i in range(4):
                sound = base.loader.loadSfx("Sounds/" + self.type2 + str(i) + ".wav")
                self.pickupSounds.append(sound)

            self.suckSound = base.loader.loadSfx("Sounds/suck.wav")
            self.splatSound = base.loader.loadSfx("Sounds/splat.wav")

        else:
            sound = base.loader.loadSfx("Sounds/crunch.wav")
            self.pickupSounds.append(sound)
            self.splatSound = base.loader.loadSfx("Sounds/explosion.wav")
            

        self.pickup = loader.loadModel("Art/" + self.type2 + ".egg")
        self.pickup.setScale(1)  
        
        #Being abducted?
        self.abduct = False 
        #When pickupable height reaches this level, it is abducted.
        self.abductheight = 35
       
        #Height off of ground
        self.height = 0
        self.fallspeed = 0
        self.stunned = False
        self.falling = False
        self.lr = False
        self.shakex = 0
        self.shakey = 0 
        self.shakez = 0
        self.stuncount = 0
        taskMgr.add(self.moveTask, "moveTask")
        taskMgr.add(self.particleTask, "particleTask")
        base.enableParticles()
        

        
        self.mydir = os.path.abspath(sys.path[0])
        self.mydir = Filename.fromOsSpecific(self.mydir).getFullpath()
        self.mydir = Filename(self.mydir)
        #self.mydir = self.mydir.toOsSpecific()
        
        self.bloodp = ParticleEffect()
        self.bloodp.loadConfig(self.mydir + '/blood.ptf')
        self.explodep = ParticleEffect()
        self.explodep.loadConfig(self.mydir + '/explode.ptf')
        self.particle = ParticleEffect()
        self.particle.loadConfig(self.mydir + '/blood.ptf')
        
        
        self.pcount = -6.66 #init to this number!
        self.particletime = 70
        
        self.willdie = False
        
    def setType(self,type1,type2):
        self.type1 = type1
        self.type2 = type2
        if self.type1 == 'animal':
            self.pickup = loader.loadModel("Art/" + self.type2 + ".egg")
            self.weight = 1
        if self.type1 ==  'inanimate':
            self.pickup = loader.loadModel("Art/" + self.type2 + ".egg")
            self.weight = 2
        if self.type1 ==  'hostile':
            self.pickup = loader.loadModel("Art/" + self.type2 + ".egg")        
            self.weight = 2
            
        self.pickup.setScale(1)
        
    def create(self,x,y,z):
        self.alive = True
        self.pickup.reparentTo(render)
        self.pickup.setPos(0,0,0)
        
    def rise(self,ship): #The ship should call this in one of its tasks on every animal that it is currently abducting. 
        self.stunned = False
        self.lr = False
        self.stuncount = 0
        self.myship = ship
        self.pickup.setZ(-36 + self.height)


        if self.type1 == 'animal':
            if self.height < self.abductheight:
                self.height += .01 * self.weight * ship.beamspeed
                self.pickup.setHpr(self.pickup.getH() + 1,0,0)
            else:
                self.abducted()
        else:
            if self.height < self.abductheight:
                self.height += .01 * self.weight * ship.beamspeed
                self.pickup.setHpr(self.pickup.getH() + .5,0,0)
            else:
                ship.abductlist.remove(self)
                self.explode()

        
    
    def playPickupSound(self):
        randSound = random.choice(self.pickupSounds)
        randSound.play()

    def abducted(self):
        self.suckSound.play()
        self.die()
    
    def die(self):      #Set self to dead, remove from render node. For recycler.
        self.myship.abductAnimal()
        self.pickup.detachNode()
        self.pickup.remove()
        if self in self.myship.abductlist: 
            self.myship.abductlist.remove(self)
            if self in self.myship.animals: 
                self.myship.animals.remove(self)
            if self in self.myship.inanimates: 
                self.myship.inanimates.remove(self)
            self.myship.findSpeed()
        self.alive = False
        self.particle.disable()
        
    def particleTask(self,task):
        if self.pcount > 0:
            self.pcount -= 1
        elif (self.pcount <= 0) and (self.pcount != -6.66):
            self.pcount = -6.66
            self.particle.disable()
            if self.willdie:
                self.die()
        return task.cont
    
    def moveTask(self,task): #Responsible for falling when dropped, walking around(??)
        if not self.willdie:
            if self.stunned:    
                if self.lr == False:
                    self.lr = True
                    self.shakex = self.pickup.getX()
                    self.shakey = self.pickup.getY()
                    self.shakez = self.pickup.getZ()
                else:
                    self.pickup.setPos(self.shakex + random.uniform(-.1,.1),self.shakey + random.uniform(-.1,.1),self.shakez + random.uniform(-.1,.1))
                self.stuncount += 1
                if self.stuncount > 30:
                    self.resetStun()
                    
            
            if self.abduct == False:
                if self.height > 0:
                    self.falling = True
                    self.fallspeed = self.fallspeed + ((2 - self.fallspeed) * .01)
                    self.height -= self.fallspeed
                    self.pickup.setZ(self.pickup,-self.fallspeed)
                elif self.height  <= 0:
                    if self.falling:
                        self.height  = 0
                        self.explode()
                        self.falling = False

        return task.cont
        
    def resetStun(self):
        self.stunned = False
        self.lr = False
        self.stuncount = 0
        self.pickup.setPos(self.shakex,self.shakey,self.shakez)
        
    def explode(self):
        self.pcount = self.particletime
        if self.type1 == 'animal':
            self.particle = self.bloodp
        else:
            self.particle = self.explodep
        self.particle.start(parent = self.pickup, renderParent = self.pickup)
        self.splatSound.play()
        #self.myship.isSplat = True
        self.pickup.setAlphaScale(0) 
        self.pickup.setTransparency(TransparencyAttrib.MAlpha)
        self.willdie = True
        self.falling = False  
