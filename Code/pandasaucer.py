import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import *    #basic Panda modules
from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import *  #for compound intervals
from direct.task import Task         #for update functions
import sys, math, random

class World(DirectObject): #necessary to accept events
    #initializer
    def __init__(self):
        #turn off default mouse control, otherwise camera isn't repositionable
        base.disableMouse()
        camera.setPosHpr(0, -30, 55, 0, -15, 0)
        self.loadModels()
        self.setupLights()
        self.setupCollisions()
        self.keyMap = {"left":0, "right":0, "forward":0}
        taskMgr.add(self.move, "moveTask")
        self.prevtime = 0
        self.isMoving = False
        #self.pandawalk = self.panda.posInterval(1, (0, 5, 0))
        self.accept("escape", sys.exit) #message name, function to call, optional list of arguments
        # "mouse1" is the event called on a left-click
        
        #inverval methods include: start(), loop(), pause(), resume(), finish()
        #start() can take optional arguments: (starttime, endtime, playrate)
        self.accept("arrow_up", self.setKey, ["forward", 1])
        #self.accept("arrow_down", self.movePanda,[0,1,0])
        self.accept("arrow_right", self.setKey, ["right", 1])
        self.accept("arrow_left", self.setKey, ["left", 1])
        self.accept("arrow_up-up", self.setKey, ["forward", 0])
        self.accept("arrow_right-up", self.setKey, ["right", 0])
        self.accept("arrow_left-up", self.setKey, ["left", 0])
        self.accept("ate-smiley", self.eat)
        
        taskMgr.add(self.rotateWorld, "rotateWorldTask")
        self.xspeed = 0
        self.yspeed = 0
        
    def setKey(self, key, value):
        self.keyMap[key] = value
        
    def movePanda(self, x,y,z):
            p=self.panda.getPos()
            p += Vec3 (x,y,z)
            self.panda.setPos(p)
            #camera.lookAt(self.panda)
            
    def rotateWorld(self,task):
            elapsed = task.time - self.prevtime
            
            # Create a handle for pointer device #0
            m = base.win.getPointer( 0 )
            # Get the absolute [x,y] screen coordinates of the cursor
            x = m.getX( )
            y = m.getY( )

            centerx = 400
            centery = 300

            
            if base.win.movePointer( 0, centerx, centery ):
                   xmov = ( x - centerx ) * 1.5
                   ymov = ( y - centery ) * 1.5

            self.xspeed = self.xspeed + ( (xmov - self.xspeed) * .1)
            self.yspeed = self.yspeed + ( (ymov - self.yspeed) * .1)
              
            self.env.setR(self.env.getR() + elapsed * -self.xspeed)
            self.env.setP(self.env.getP() + elapsed * -self.yspeed)
         
            self.panda.setR(-self.xspeed * .1)
            self.panda.setP(-self.yspeed * .1)
                
            return Task.cont
            
    def loadModels(self):
        """load the default panda and env models"""
        self.panda = Actor("panda-model", {"walk":"panda-walk4"})
        self.panda.reparentTo(render)
        self.panda.setScale(0.005)
        self.panda.setH(180)
        self.panda.setPos(0,0,15)

        self.env = loader.loadModel("smiley")
        self.env.reparentTo(render)
        self.env.setScale(30)
        self.env.setPos(0, 0, -20)
        

        
        #load targets
        self.targets = []
        
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
        
    def walk(self):
        dist = 5
        angle = deg2Rad(self.panda.getH())
        dx = dist* math.sin(angle)
        dy = dist * -math.cos(angle)
        pandaWalk = Parallel(self.panda.posInterval(1, (self.panda.getX() + dx, self.panda.getY() + dy, 0)), self.panda.actorInterval("walk", duration=1, loop=1))
        pandaWalk.start()
        
    def turn(self, direction):
        """turn the panda"""
        pandaTurn = self.panda.hprInterval(.2, (self.panda.getH() - (10 * direction), 0, 0))
        pandaTurn.start()
      
    def move(self, task):
        #get our current dt
        elapsed = task.time - self.prevtime
        
        #change pos based on keyMap
        if self.keyMap["left"]:
            self.panda.setH(self.panda.getH() + elapsed * 50)
        if self.keyMap["right"]:
            self.panda.setH(self.panda.getH() - elapsed * 50)
        if self.keyMap["forward"]:
            dist = 6 * elapsed
            angle = deg2Rad(self.panda.getH())
            dx = dist* math.sin(angle)
            dy = dist * -math.cos(angle)
            self.panda.setPos(self.panda.getX() + dx, self.panda.getY() + dy, 10)
        camera.lookAt(self.panda)
        #animate based on keyMap
        if self.keyMap["left"] or self.keyMap["right"] or self.keyMap["forward"]:
            if self.isMoving == False:
                self.isMoving = True
                self.panda.loop("walk")
        else: #no movement keys are depressed
            if self.isMoving:
                self.isMoving = False
                self.panda.stop()
                self.panda.pose("walk", 4)
        
        #store current time and let the task manager know we want this to remain
        self.prevtime = task.time
        return Task.cont
        
    def setupCollisions(self):
        #make a collision traverser
        base.cTrav = CollisionTraverser()
        #set the collision handler to send event messages on collision
        self.cHandler = CollisionHandlerEvent()
        # %in is substituted with the name of the into object
        self.cHandler.setInPattern("ate-%in")
        
        #panda collider
        cSphere = CollisionSphere((0,0,0), 500) #because the panda is scaled down
        cNode = CollisionNode("panda")
        cNode.addSolid(cSphere)
        #set panda to only be a "from" object
        cNode.setIntoCollideMask(BitMask32.allOff())
        cNodePath = self.panda.attachNewNode(cNode)
        #cNodePath.show()
        base.cTrav.addCollider(cNodePath, self.cHandler)
        
        #target colliders
        for target in self.targets:
            cSphere = CollisionSphere((0,0,0), 2)
            cNode = CollisionNode("smiley")
            cNode.addSolid(cSphere)
            cNodePath = target.attachNewNode(cNode)
            #cNodePath.show()
        
    def eat(self, cEntry):
        """handles panda eating a smiley"""
        self.targets.remove(cEntry.getIntoNodePath().getParent())
        cEntry.getIntoNodePath().getParent().remove()
        
w = World()
run()