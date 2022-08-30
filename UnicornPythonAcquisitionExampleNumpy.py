import UnicornPy
import numpy as np
import csv
import pandas as pd
import time
#from curser import cursor
import random
import pygame
from pygame.locals import*

#from pyfirmata import Arduino, util
import random

class Arduino():
    def __init__(self,initial_data, glass, buzzer, motor, event, samplenumber, sr , length):
        self.glass = glass
        self.motor = motor
        self.event = event
        self.buzzer = buzzer
        self.sample = samplenumber
        self.datalength = sr*length
        self.data = initial_data
        self.current_state = 3  #1_objectA 2_ObjectB 3_Neutral
    def glasses_event(self):
        for i in range(len(self.glass)):
            start = self.glass[i][0]
            end  = self.glass[i][1]   
            if start <= self.sample and end >=self.sample  :
                self.data[self.sample][0] = 1
           
    def audio_event(self):
        for i in range(len(self.buzzer)):
            start = self.buzzer[i][0]
            end  = self.buzzer[i][1]          
            if start <= self.sample and end >=self.sample :
                self.data[self.sample][1] = 1
                
    def motor_event (self):
        states = [1,2,3]
        for index, tuple in enumerate(self.motor):
            start = tuple[0]
            end = tuple[1]
            state = tuple[2]
            
            if start <= self.sample and end >=self.sample :
                rand = random.randint(0, len(states)-1)
                self.current_state = states[rand]
                self.data[self.sample][2] = states[rand]
                
    def events(self,states):
        for i in range(len(self.event)):
            start = self.event[i][0]
            end  = self.event[i][1]
            num = self.event[i][2]
            if start <= self.sample and end >=self.sample:
                if num =="s1":
                    self.data[self.sample][3] = states[0]
                elif num =="s2":
                    self.data[self.sample][3] = states[1]
                elif num =="s3":
                    self.data[self.sample][3] = states[2]
                elif num =="s4":
                    self.data[self.sample][3] = states[3]

    def choose_random_state(self):
        states = [1,2]
        final_state = [0,1,0,2]
        pre_state = 0
        for j,i in enumerate(final_state):
            if i ==1 or i==2:
                if pre_state ==1:
                    final_state[j] = 2
                elif pre_state==2:
                    final_state[j] = 1
                else:
                    final_state[j] = states[random.randint(0, len(states)-1)]
                    pre_state = final_state[j]
        return final_state
    
    def main(self):
        self.glasses_event()
        self.audio_event()
        #self.motor_event()
        states = self.choose_random_state()
        self.events(states)
        return self.data
        
                
#cursor = cursor(width = 600 , length = 960)
        
def main():
    # Specifications for the data acquisition.
    #-------------------------------------------------------------------------------------
    TestsignaleEnabled = False;
    FrameLength = 1;
    AcquisitionDurationInSeconds = 20;
    EEGFile = "EEG.csv";
    EventFile = "Event.csv"
    
    print("Unicorn Acquisition Example")
    print("---------------------------")
    print()
    
    
    # Get available devices.
    #-------------------------------------------------------------------------------------

    # Get available device serials.
    deviceList = UnicornPy.GetAvailableDevices(True)

    if len(deviceList) <= 0 or deviceList is None:
        raise Exception("No device available.Please pair with a Unicorn first.")

    # Print available device serials.
    print("Available devices:")
    i = 0
    for device in deviceList:
        print("#%i %s" % (i,device))
        i+=1

    # Request device selection.
    print()
    deviceID = int(input("Select device by ID #"))
    if deviceID < 0 or deviceID > len(deviceList):
        raise IndexError('The selected device ID is not valid.')

    # Open selected device.
    #-------------------------------------------------------------------------------------
    print()
    print("Trying to connect to '%s'." %deviceList[deviceID])
    device = UnicornPy.Unicorn(deviceList[deviceID])
    print("Connected to '%s'." %deviceList[deviceID])
    print()

    # Create a file to store data.
    file = open(EEGFile, "wb")
    #0eventfile = open(EventFile, "w")
    #header = "FZ, C3, CZ, C4, PZ, O1, OZ, O2, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample"
    #file.write(header + "\n")0

    # Initialize acquisition members.
    #-------------------------------------------------------------------------------------
    numberOfAcquiredChannels= device.GetNumberOfAcquiredChannels()
    configuration = device.GetConfiguration()

    # Print acquisition configuration
    print("Acquisition Configuration:");
    print("Sampling Rate: %i Hz" %UnicornPy.SamplingRate);
    print("Frame Length: %i" %FrameLength);
    print("Number Of Acquired Channels: %i" %numberOfAcquiredChannels);
    print("Data Acquisition Length: %i s" %AcquisitionDurationInSeconds);
    print();
    sr =UnicornPy.SamplingRate
    length = AcquisitionDurationInSeconds
    

    glass_event = [[0,6*sr,'g1'],[9*sr , 15*sr,'g2'],[18*sr, 24*sr,'g3'],[27*sr,33*sr,'g4']]
    
    Buzzer_event = [[12*sr, 13*sr,'b1'],[30*sr, 31*sr,'b2']]
    
    #object_event
    s = 0
    e = 6
    event =  [[s*sr , e*sr,'s1'],[(s+9)*sr, (e+9)*sr, 's2'], [(s+18)*sr, (e+18)*sr, 's3'], [(s+27)*sr, (e+27)*sr,'s4']]
    motor_turning_event = [[event[0][1]+1, event[0][1]+2 ,'g1'], [event[1][1]+1, event[1][1]+2 ,'g2'], [event[2][1]+1, event[2][1]+2 ,'g3']]

    #sm = 7
    #em = 9
    #motor_event = [(s*sr, em*sr,'m1'),((s+9)*sr, (em+9)*sr,'m2'),((s+18)*sr, (em+18)*sr,'m3'),
    #               ((s+27)*sr, (em+27)*sr,'m4')]
    
    

    # Allocate memory for the acquisition buffer.
    receiveBufferBufferLength = FrameLength * numberOfAcquiredChannels * 4
    receiveBuffer = bytearray(receiveBufferBufferLength)

    
    # Start data acquisition.
    #-------------------------------------------------------------------------------------
    device.StartAcquisition(TestsignaleEnabled)
    print("Data acquisition started.")

    # Calculate number of get data calls.
    numberOfGetDataCalls = int(AcquisitionDurationInSeconds * UnicornPy.SamplingRate / FrameLength);

    # Limit console update rate to max. 25Hz or slower to prevent acquisition timing issues.                   
    consoleUpdateRate = int((UnicornPy.SamplingRate / FrameLength) / 25.0);
    if consoleUpdateRate == 0:
        consoleUpdateRate = 1


    # Acquisition loop.
    
    
    
    timer = []
    initial_data = np.zeros((sr*length, 5))
    
    
    #-------------------------------------------------------------------------------------
    timer.append(time.strftime("%H%M%S"))
    
    img =  r'C:\Users\moacc\.spyder-py3\cursor.png'
    set_caption = 'cursor_control'

    
    width = 600
    length = 960
    
    pygame.init()
    screen = pygame.display.set_mode((length, width))
    pygame.display.set_caption(set_caption)
    image = pygame.image.load(img)
    image = pygame.transform.scale(image, (30, 30))
    image.convert()
    clock = pygame.time.Clock()
    color =  (255,255,255)
    
    loop = True
    count = 0
    while loop:
        
        if count == numberOfGetDataCalls:
            break
        
        
        screen.fill(color)
        for eventt in pygame.event.get():
            if eventt.type == pygame.QUIT:
                loop = False
                
                
        #x =  random.randint(33 , 930)
        x =  random.randint(33 , 35)
        y =  random.randint(33 , 35)  
        #y =  random.randint(33 , 560) 
        pos = tuple((x,y))
                       
        screen.blit(image,pos)
        pygame.display.update()
        
        #time.sleep(50)
        #clock.tick(10)
        
#for i in range (0,numberOfGetDataCalls):
        # Receives the configured number of samples from the Unicorn device and writes it to the acquisition buffer.
        device.GetData(FrameLength,receiveBuffer,receiveBufferBufferLength)
    
        # Convert receive buffer to numpy float array 
        data = np.frombuffer(receiveBuffer, dtype=np.float32, count=numberOfAcquiredChannels * FrameLength)
        data = np.reshape(data, (FrameLength, numberOfAcquiredChannels))
        np.savetxt(file,data,delimiter=',',fmt='%.3f',newline='\n')
        
        
        #initial_data[i][4] = count
        AR = Arduino(initial_data, glass_event, Buzzer_event, motor_turning_event, event, count , sr, length)
        initial_data = AR.main()
        #print('count :', count)
        
        #Write to event Events.csv
        #eventfile.write(str(i+1) + '\t' + '\t' + '\t' + str(glasses) + '\t' + str(audio) + '\t' + str(motor) + '\n') #WRITES THE SAMPLE POINTS IN FIRST COLUMN
    
        # Update console to indicate that the data acquisition is running.
        count += 1
        if count % consoleUpdateRate == 0:
            print('.',end='',flush=True)
        
                
    pygame.quit()
    device.StopAcquisition();
    timer.append(time.strftime("%H%M%S"))        
    # Stop data acquisition.
    #-------------------------------------------------------------------------------------
    
    print()
    print("Data acquisition stopped.");


    del receiveBuffer
    file.close()

    # Close device.
    #-------------------------------------------------------------------------------------
    del device
    print("Disconnected from Unicorn")

    return initial_data

        

#execute main
data = main()
timestr = time.strftime("%Y%m%d.csv")
pd.DataFrame(data).to_csv(timestr,header=["glass_event", "Buzzer_event", "motor_event","events","sample_num"], index=False)
