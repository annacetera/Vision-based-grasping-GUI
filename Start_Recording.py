import UnicornPy
import numpy as np
import csv
import pandas as pd
from datetime import date
import os
import time
from Trial_struct import *
import get_param
import serial
arduinoData = serial.Serial('COM6', 115200)

class Start_Recording():
    def __init__(self, len_trial_rec, eeg_filename, event_filename ,TestsignaleEnabled ,trial_number,  patient_name, Unicorn_id, task_number):
        self.AcquisitionDurationInSeconds =  len_trial_rec
        self.EEG_file_name = eeg_filename
        self.event_file_name = event_filename
        self.numberOfAcquiredChannels = 0
        self.configuration = 0
        self.SamplingRate = 0
        self.FrameLength = 1
        self.device = 0
        self.TestsignaleEnabled = TestsignaleEnabled
        self.patient_name = patient_name
        self.trial = trial_number
        self.unicorn_id = Unicorn_id
        self.task_number = task_number
        self.header = 'FZ, FC1, FC2, C3, CZ, C4, CPZ, PZ, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample, Unkown'

    def eeg_devices(self):
        if self.unicorn_id == False:
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
            else:
                unicorn_dev_id = deviceList[deviceID]
        else:
            unicorn_dev_id = self.unicorn_id

        return unicorn_dev_id

    def eeg_connect(self):
        dev_ID = self.eeg_devices()
        print("Trying to connect to '%s'." %dev_ID)
        self.device = UnicornPy.Unicorn(dev_ID)
        print("Connected to '%s'." %dev_ID)
        print()
        self.numberOfAcquiredChannels = self.device.GetNumberOfAcquiredChannels()
        self.configuration = self.device.GetConfiguration()
        self.SamplingRate = UnicornPy.SamplingRate


    def start_acquisition(self, eeg_path, event_path):
        #running for different trials
        states = self.choose_random_state(self.trial)
        
        
        self.device.StartAcquisition(self.TestsignaleEnabled)
        for j in range(self.trial):
            receiveBufferBufferLength = self.FrameLength * self.numberOfAcquiredChannels * 4
            receiveBuffer = bytearray(receiveBufferBufferLength)
            
            print("Data acquisition started.")

            numberOfGetDataCalls = int(self.AcquisitionDurationInSeconds * self.SamplingRate / self.FrameLength)
            # Limit console update rate to max. 25Hz or slower to prevent acquisition timing issues.                   
            consoleUpdateRate = int((self.SamplingRate / self.FrameLength) / 25.0)
            if consoleUpdateRate == 0:
                consoleUpdateRate = 1

        
            sr = self.SamplingRate
            self.current_eeg = eeg_path + "/" + str(j) + "_"+ self.task_number + "_"+ self.EEG_file_name
            file = open(self.current_eeg, "a")
            file.write(self.header)

            initial_data = []
            # i is sample point in trial j 
            count = 0
            for i in range (0,numberOfGetDataCalls):
                # Receives the configured number of samples from the Unicorn device and writes it to the acquisition buffer.
                self.device.GetData(self.FrameLength,receiveBuffer,receiveBufferBufferLength)
            
                # Convert receive buffer to numpy float array 
                dataa = np.frombuffer(receiveBuffer, dtype=np.float32, count=self.numberOfAcquiredChannels * self.FrameLength)
                data = np.reshape(dataa, (self.FrameLength, self.numberOfAcquiredChannels))
                #write 
                data[0][15] = count 
                
                AR = Arduino(initial_data, count , sr, states[j],arduinoData)
                if self.task_number =="task_1" or self.task_number =="task_3" or self.task_number =="task_4" or self.task_number =="task_5" :
                    initial_data = AR.task_1()

                elif self.task_number == "task_2":
                    initial_data = AR.task_2()

                np.savetxt(file,data,delimiter=',',fmt='%.3f',newline='\n')
                
                # Update console to indicate that the data acquisition is running.
                count += 1
                if count % consoleUpdateRate == 0:
                    print('.',end='',flush=True)
    

            self.current_event = event_path + "/" + str(j) + "_"+ self.task_number + "_"+ self.event_file_name
            array = np.array(initial_data)
            pd.DataFrame(array).to_csv(  self.current_event ,header=["glass_event", "Buzzer_event","motor_turning_event","events","TursnStart", "sample_number"], index=False)

            #convert a list to data frame to store in a csv file 
            print("Data ", str(j) , "acquisition stopped.")
            

            # Close device.
            #-------------------------------------------------------------------------------------
            
            print("Disconnected from Unicorn")
            file.close()
        del receiveBuffers
        self.device.StopAcquisition()
        del self.device


    def make_dir(self, pathname):
        os.chdir('C:\\Users\\annacetera\\Documents')
        curworkdir = os.getcwd()
        path = os.path.join(curworkdir, "EEGdata") 
        #patient_name
        today = date.today()
        dateee = today.strftime("%b-%d-%Y")
        path = os.path.join(path, dateee) 

        directory = self.patient_name
        path = os.path.join(path, directory)  

        directory = self.task_number
        path = os.path.join(path, directory)  

        directory = pathname
        path = os.path.join(path, directory)  

        if not os.path.exists(path):

            
            os.makedirs(path)  
        return path

    def choose_random_state(self,trial_number):
        states = [1,2]
        a = states[random.randint(0, len(states)-1)]
        b = states[random.randint(0, len(states)-1)]
        final_state = [0,a,0,b,0]
        trial_list = []
        
        for i in range(0,trial_number):
            a = []
            b = []
            pre_state = 0
            for j,i in enumerate(final_state):
                if i ==1 or i==2:
                    if pre_state ==1:
                        final_state[j] = 2
                        b.append(2)
                        pre_state = 2
                    elif pre_state==2:
                        final_state[j] = 1
                        b.append(1)
                        pre_state = 1
                        
                    else:
                        final_state[j] = states[random.randint(0, len(states)-1)]
                        b.append(final_state[j])
                        pre_state = final_state[j]
                else:
                    a.append(0)
            
            trial_list.append([a[0],b[0],a[1],b[1],a[2]])
        return trial_list

    def main(self):
        eeg_path = self.make_dir("eeg")
        event_path = self.make_dir("event")
        self.eeg_connect()
        self.start_acquisition(eeg_path, event_path)

data_recording = Start_Recording(len_trial_rec = get_param.Trial_duration, 
                                eeg_filename = "EEG.csv", 
                                event_filename ="Event.csv" ,
                                TestsignaleEnabled = False, 
                                trial_number= get_param.Trial_number ,
                                patient_name= get_param.Username,
                                Unicorn_id  = get_param.Unicorn_ID,
                                task_number = get_param.task_list)
data_recording.main()







