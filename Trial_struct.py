import UnicornPy
import numpy as np
import pandas as pd
import random

class Arduino():
    def __init__(self,initial_data, samplenumber, sr, states,arduinoData):
        self.sr = sr
        self.sample = samplenumber
        self.data = initial_data
        self.current_state = 3  
        self.states = states
        self.arduinoData = arduinoData

    def buzzer_start(self,related_list):
        for i in range(len(related_list)):
            start = related_list[i][0] 
            st  = related_list[i][1] 
            if start == self.sample   :
                if st == 'bs1':
                    print("3 sec sound")
                    self.arduinoData.write(str.encode('7')) #longer soud (for 3 sec)
                else:
                    print("bip")
                    self.arduinoData.write(str.encode('5'))
                
    def glass_turnstart(self,related_list):
        for i in range(len(related_list)):
            start = related_list[i][0]  
            if start == self.sample   :
                print("glass : turn on")
                self.arduinoData.write(str.encode('6'))

    def turn_start(self,related_list):
        result = 0
        for i in range(len(related_list)):
            start = related_list[i][0]
            st  = related_list[i][1]
            if start == self.sample :
                if st== "t2":
                    if self.states[1] == 1:
                        print(1) #send 1
                        self.arduinoData.write(str.encode('1'))
                        result = 1
                    else:
                        print(2) #send 2
                        self.arduinoData.write(str.encode('2'))
                        result = 2
                elif st == "t3":
                    if self.states[1] == 1:
                        print(3) # show nothing
                        self.arduinoData.write(str.encode('3'))
                        result = 3
                    else:
                        print(4) # show nothing
                        self.arduinoData.write(str.encode('4'))
                        result = 4
                elif st== "t4":
                    if self.states[3] == 1:
                        print(1) #send 1
                        self.arduinoData.write(str.encode('1'))
                        result = 1
                    else:
                        print(2) #send 2
                        self.arduinoData.write(str.encode('2'))
                        result = 2
                elif st== "t5":
                    if self.states[3] == 1:
                        print(3) # show nothing
                        self.arduinoData.write(str.encode('4'))
                        result = 3
                    else:
                        print(4) # show nothing
                        self.arduinoData.write(str.encode('3'))
                        result = 4
                #print("glass : turn off")
                self.arduinoData.write(str.encode('8')) #print("glass : turn off")
        return result
                    
                
    def glasses_event(self,related_list):
        result = 0
        for i in range(len(related_list)):
            start = related_list[i][0]
            end  = related_list[i][1]   
            if start <= self.sample and end >=self.sample  :
                result = 1
        return result

           
    def audio_event(self,related_list):
        result = 0
        for i in range(len(related_list)):
            start = related_list[i][0]
            end  = related_list[i][1]          
            if start <= self.sample and end >=self.sample :
                result = 1
        return result
                
    def motor_turning_event (self,related_list):
        result = 0
        for i in range(len(related_list)):
            start = related_list[i][0]
            end = related_list[i][1]
            motor_num = related_list[i][2]
            if start <= self.sample and end >=self.sample :
                if motor_num == "g1":
                    result = self.states[1]
                    
                elif motor_num == "g2":
                    result = self.states[2]
                    
                elif motor_num == "g3":
                    result = self.states[3]

                elif motor_num == "g4":
                    result = self.states[0]
                    
        return result
                
    def obj_event(self, related_list):
        result = 0
        for i in range(len(related_list)):
            start = related_list[i][0]
            end  = related_list[i][1]
            num = related_list[i][2]
            if start <= self.sample and end >=self.sample:
                if num =="s1":
                    result = self.states[0]
                elif num =="s2":
                    result = self.states[1]
                elif num =="s3":
                    result =  self.states[2]
                elif num =="s4":
                    result =  self.states[3]
                elif num =="s5":
                    result =  self.states[0]
        return result

    def task_1(self):
        glass = [[0,6*self.sr,'g1'],[9*self.sr , 15*self.sr,'g2'],[18*self.sr, 24*self.sr,'g3'],[27*self.sr,33*self.sr,'g4'],[36*self.sr,42*self.sr,'g5']]
        
        buzzer = [[0*self.sr, 2*self.sr,'b1'],[12*self.sr, 13*self.sr,'b2'],[21*self.sr, 22*self.sr,'b3'], [30*self.sr, 31*self.sr,'b4'],[39*self.sr, 40*self.sr,'b5']]
        
        s,e = 0,6
        object_event =  [[s*self.sr , e*self.sr,'s1'],[(s+9)*self.sr, (e+9)*self.sr, 's2'], [(s+18)*self.sr, (e+18)*self.sr, 's3'], [(s+27)*self.sr, (e+27)*self.sr,'s4'],[(s+36)*self.sr, (e+36)*self.sr,'s5']]
        
        motor = [[(object_event[1][0]-(2)*self.sr), (object_event[1][0]-1) ,'g1'], [(object_event[2][0]-(2)*self.sr), (object_event[2][0]-1) ,'g2'], [(object_event[3][0]-(2)*self.sr), (object_event[3][0]-1) ,'g3'],
        [(object_event[4][0]-(2)*self.sr), (object_event[4][0]-1) ,'g4']]
        
        turnstart = [ [0,'t1'], [motor[0][0],'t2'], [motor[1][0],'t3'], [motor[2][0],'t4'],[motor[3][0],'t5']]
        buzzer_TurnStart = [[buzzer[0][0],'bs1'],[buzzer[1][0],'bs2'],[buzzer[2][0],'bs3'],[buzzer[3][0],'bs4'],[buzzer[4][0],'bs5']]
        
        glass_turnStatr = [[glass[0][0],'gs1'],[glass[1][0],'gs2'],[glass[2][0],'gs3'],[glass[3][0],'gs4'],[glass[4][0],'gs5']]

        v1 = self.glasses_event(glass)
        v2 = self.audio_event(buzzer)
        v3 = self.motor_turning_event(motor)
        v4 = self.obj_event(object_event)
        self.glass_turnstart(glass_turnStatr)
        v5 = self.turn_start(turnstart)
        self.buzzer_start(buzzer_TurnStart)
       

        self.data.append([v1,v2,v3,v4, v5, self.sample])
        return self.data

    def task_2(self):
        glass = [[9*self.sr , 15*self.sr,'g1'],[27*self.sr,33*self.sr,'g2']]
        buzzer = [[3*self.sr, 4*self.sr,'b1'],[21*self.sr, 22*self.sr,'b2'],[39*self.sr, 40*self.sr,'b3']]
        
        
        s,e = 0,6
        object_event =  [[s*self.sr , e*self.sr,'s1'],[(s+9)*self.sr, (e+9)*self.sr, 's2'], [(s+18)*self.sr, (e+18)*self.sr, 's3'], [(s+27)*self.sr, (e+27)*self.sr,'s4'],
        [(s+36)*self.sr, (e+36)*self.sr,'s5']]
        motor = [[(object_event[1][0]-2*self.sr), (object_event[1][0]-1) ,'g1'], [(object_event[2][0]-2*self.sr), (object_event[2][0]-1) ,'g2'], [(object_event[3][0]-2*self.sr), (object_event[3][0]-1) ,'g3'],
        [(object_event[4][0]-(2)*self.sr), (object_event[4][0]-1) ,'g4']]

        turnstart = [ [0,'t1'], [motor[0][0],'t2'], [motor[1][0],'t3'], [motor[2][0],'t4'],[motor[3][0],'t5']]
        buzzer_TurnStart = [[buzzer[0][0],'bs1'],[buzzer[1][0],'bs2']]
        glass_turnStatr = [[glass[0][0],'gs1'],[glass[1][0],'gs2'],[glass[2][0],'gs3'],[glass[3][0],'gs4'],[glass[4][0],'gs5']]
        

        v1 = self.glasses_event(glass)
        v2 = self.audio_event(buzzer)
        v3 = self.motor_turning_event(motor)
        v4 = self.obj_event(object_event)
        v5 = self.turn_start(turnstart)
        self.buzzer_start(buzzer_TurnStart)
        self.glass_turnstart(glass_turnStatr)

        self.data.append([v1,v2,v3,v4, v5, self.sample])
        return self.data