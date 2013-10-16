##Module to use 360 controller
import direct.directbase.DirectStart
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from pygame import *
init()

class pyPad360(DirectObject):
    
    def setupGamepads(self):        
        #Get the number of controllers so we know how many to init
        count = joystick.get_count()
        
        
        #Initialize the 360 controllers
        if count > 0:
            c1=joystick.Joystick(0)
            c1.init()
        if count > 1:
            c2=joystick.Joystick(1)
            c2.init()
        if count > 2:
            c3=joystick.Joystick(2)
            c3.init()          
        if count > 3:
            c4=joystick.Joystick(3)
            c4.init()                
    #def setupGamepads()
        return count
                
    def gamepadPollingTask(self, task):    
        for e in event.get():  
            #Get which controller this is and add it to the eventName
            if e.dict["joy"] == 0:
                c_number = "C1_"
            elif e.dict["joy"] == 1:
                c_number = "C2_"
            elif e.dict["joy"] == 2:
                c_number = "C3_"
            elif e.dict["joy"] == 3:
                c_number = "C4_"                                             
                                
            #Handle the BUTTON DOWN events
            if e.type == JOYBUTTONDOWN:
                if (e.dict["button"] == 0):
                    eventName = c_number +  "A_DOWN"
                    messenger.send(eventName, [])                   
                elif (e.dict["button"] == 1):
                    eventName = c_number +  "B_DOWN"
                    messenger.send(eventName, [])                                      
                elif (e.dict["button"] == 2):
                    eventName = c_number +  "X_DOWN"
                    messenger.send(eventName, [])                     
                elif (e.dict["button"] == 3):
                    eventName = c_number +  "Y_DOWN"
                    messenger.send(eventName, [])                     
                elif (e.dict["button"] == 4):
                    eventName = c_number +  "LB_DOWN"
                    messenger.send(eventName, [])                       
                elif (e.dict["button"] == 5):
                    eventName = c_number +  "RB_DOWN"
                    messenger.send(eventName, [])                         
                elif (e.dict["button"] == 6):
                    eventName = c_number +  "BACK_DOWN"
                    messenger.send(eventName, [])                     
                elif (e.dict["button"] == 7):
                    eventName = c_number +  "START_DOWN"
                    messenger.send(eventName, [])                       
                elif (e.dict["button"] == 8):
                    eventName = c_number +  "LSTICK_DOWN"
                    messenger.send(eventName, [])                       
                elif (e.dict["button"] == 9):
                    eventName = c_number +  "RSTICK_DOWN"
                    messenger.send(eventName, [])  
                                                                                                                                                
            #Handle the BUTTONUP events 
            elif e.type == JOYBUTTONUP:
                if (e.dict["button"] == 0):
                    eventName = c_number +  "A_UP"
                    messenger.send(eventName, [])                   
                elif (e.dict["button"] == 1):
                    eventName = c_number +  "B_UP"
                    messenger.send(eventName, [])                                       
                elif (e.dict["button"] == 2):
                    eventName = c_number +  "X_UP"
                    messenger.send(eventName, [])                     
                elif (e.dict["button"] == 3):
                    eventName = c_number +  "Y_UP"
                    messenger.send(eventName, [])                     
                elif (e.dict["button"] == 4):
                    eventName = c_number +  "LB_UP"
                    messenger.send(eventName, [])                        
                elif (e.dict["button"] == 5):
                    eventName = c_number +  "RB_UP"
                    messenger.send(eventName, [])                        
                elif (e.dict["button"] == 6):
                    eventName = c_number +  "BACK_UP"
                    messenger.send(eventName, [])                     
                elif (e.dict["button"] == 7):
                    eventName = c_number +  "START_UP"
                    messenger.send(eventName, [])                        
                elif (e.dict["button"] == 8):
                    eventName = c_number +  "LSTICK_UP"
                    messenger.send(eventName, [])                       
                elif (e.dict["button"] == 9):
                    eventName = c_number +  "RSTICK_UP"
                    messenger.send(eventName, [])  
                                   
            #Handle the directional pad
            elif e.type == JOYHATMOTION:
                if (e.dict["value"] == (0,0)):
                    eventName = c_number +  "DPAD_NONE"
                    messenger.send(eventName, [])                        
                elif (e.dict["value"] == (0,1)):
                    eventName = c_number +  "DPAD_UP"
                    messenger.send(eventName, [])
                elif (e.dict["value"] == (1,1)):
                    eventName = c_number +  "DPAD_UPRIGHT"
                    messenger.send(eventName, [])                                         
                elif (e.dict["value"] == (1,0)):
                    eventName = c_number +  "DPAD_RIGHT"
                    messenger.send(eventName, [])                    
                elif (e.dict["value"] == (1,-1)):
                    eventName = c_number +  "DPAD_DOWNRIGHT"
                    messenger.send(eventName, [])                                        
                elif (e.dict["value"] == (0,-1)):
                    eventName = c_number +  "DPAD_DOWN"
                    messenger.send(eventName, [])                    
                elif (e.dict["value"] == (-1,-1)):
                    eventName = c_number +  "DPAD_DOWNLEFT"
                    messenger.send(eventName, [])                                         
                elif (e.dict["value"] == (-1,0)):
                    eventName = c_number +  "DPAD_LEFT"
                    messenger.send(eventName, [])                     
                elif (e.dict["value"] == (-1,1)):
                    eventName = c_number +  "DPAD_UPLEFT"
                    messenger.send(eventName, [])                                         
                   
            #Handle the analog sticks
            elif e.type == JOYAXISMOTION:                
                #Handle the left analog stick X axis
                if (e.dict["axis"] == 0):
                    if (e.dict["value"] > 0 and e.dict["value"] < 0.3):
                        eventName = c_number +  "LSTICK_SLIGHTRIGHT"
                        messenger.send(eventName, []) 
                        #print "x=", e.dict["value"]
                    elif (e.dict["value"] > 0.3 and e.dict["value"] < 1):
                        eventName = c_number +  "LSTICK_HARDRIGHT"
                        messenger.send(eventName, [])  
                        #print "x=", e.dict["value"]
                    elif (e.dict["value"] < 0 and e.dict["value"] > -0.3):
                        eventName = c_number +  "LSTICK_SLIGHTLEFT"
                        messenger.send(eventName, [])   
                        #print "x=", e.dict["value"]
                    elif (e.dict["value"] < -0.3 and e.dict["value"] > -1):
                        eventName = c_number +  "LSTICK_HARDLEFT"
                        messenger.send(eventName, []) 
                        #print "x=", e.dict["value"]
                        
                #Handle the left analog stick Y axis
                elif (e.dict["axis"] == 1):
                    if (e.dict["value"] < -0.3 and e.dict["value"] > -1):
                        eventName = c_number +  "LSTICK_HARDUP"
                        messenger.send(eventName, [])  
                        #print "y=", e.dict["value"]
                    elif (e.dict["value"] < 0 and e.dict["value"] > -0.3):
                        eventName = c_number +  "LSTICK_SLIGHTUP"
                        messenger.send(eventName, [])  
                        #print "y=", e.dict["value"]
                    elif (e.dict["value"] > 0 and e.dict["value"] < 0.3):
                        eventName = c_number +  "LSTICK_SLIGHTDOWN"
                        messenger.send(eventName, [])      
                        #print "y=", e.dict["value"]
                    elif (e.dict["value"] > 0.3 and e.dict["value"] < 1):
                        eventName = c_number +  "LSTICK_HARDDOWN"
                        messenger.send(eventName, [])
                        #print "y=", e.dict["value"]

                        
                #Handle the right analog stick X axis
                elif (e.dict["axis"] == 4):
                    if (e.dict["value"] > 0 and e.dict["value"] < 0.5):
                        eventName = c_number +  "RSTICK_SLIGHTRIGHT"
                        messenger.send(eventName, [])                     
                    elif (e.dict["value"] > 0.5 and e.dict["value"] < 1):
                        eventName = c_number +  "RSTICK_HARDRIGHT"
                        messenger.send(eventName, [])                                  
                    elif (e.dict["value"] < 0 and e.dict["value"] > -0.5):
                        eventName = c_number +  "RSTICK_SLIGHTLEFT"
                        messenger.send(eventName, [])                             
                    elif (e.dict["value"] < -0.5 and e.dict["value"] > -1):
                        eventName = c_number +  "RSTICK_HARDLEFT"
                        messenger.send(eventName, [])                                                                                        
                #Handle the right analog stick Y axis
                elif (e.dict["axis"] == 3):
                    if (e.dict["value"] < -0.5 and e.dict["value"] > -1):
                        eventName = c_number +  "RSTICK_HARDUP"
                        messenger.send(eventName, [])                         
                    elif (e.dict["value"] < 0 and e.dict["value"] > -0.5):
                        eventName = c_number +  "RSTICK_SLIGHTUP"
                        messenger.send(eventName, [])                           
                    elif (e.dict["value"] > 0 and e.dict["value"] < 0.5):
                        eventName = c_number +  "RSTICK_SLIGHTDOWN"
                        messenger.send(eventName, [])                         
                    elif (e.dict["value"] > 0.5 and e.dict["value"] < 1):
                        eventName = c_number +  "RSTICK_HARDDOWN"
                        messenger.send(eventName, [])
                                                                                                     
                #Handle the triggers              
                elif (e.dict["axis"] == 2):
                    #Handle the left trigger                  
                    if (e.dict["value"] > 0 and e.dict["value"] < 0.5):
                        eventName = c_number +  "LT_SLIGHTDOWN"
                        messenger.send(eventName, [])                           
                    elif (e.dict["value"] < 1 and e.dict["value"] > 0.5):
                        eventName = c_number +  "LT_HARDDOWN"
                        messenger.send(eventName, [])                                     
                    #Handle the right trigger
                    elif (e.dict["value"] < 0 and e.dict["value"] > -0.5):
                        eventName = c_number +  "RT_SLIGHTDOWN"
                        messenger.send(eventName, [])                           
                    elif (e.dict["value"] < -0.5 and e.dict["value"] > -1 ):
                        eventName = c_number +  "RT_HARDDOWN"
                        messenger.send(eventName, [])                                                                                      
        return Task.cont
    #def gamepadPollingTask()
#class pyPad360()