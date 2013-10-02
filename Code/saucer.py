import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import *    #basic Panda modules
from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import *  #for compound intervals
from direct.task import Task         #for update functions
import sys, math, random

class Saucer(DirectObject):
    def __init__(self):
        self.ship = Actor("panda-model", {"walk":"panda-walk4"})
        self.ship.reparentTo(render)
        self.ship.setScale(0.005)
        self.ship.setH(180)
        self.ship.setPos(0,0,15)
        