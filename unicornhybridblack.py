# unicornhybridblack: classes to communicate with g.tec Unicorn Hybrid Black
#
"""
UnicornBlackThreads provides direct access to the thread functions

UnicornBlackProcess provides the ability to run the device as a seperate process

UnicornBlackCheckSignal provides a class to evaluate signal quality


Working notes
- Sometimes works when run in Spyder, but seems to work best when run in external


@author: Matt Pontifex
"""

import os
import math
import numpy
import time
from datetime import datetime
from threading import Thread, Lock
from multiprocessing import Queue
import multiprocessing
import matplotlib.mlab as mlab
import scipy.signal
import UnicornPy as UnicornPy

# DEBUG #
#if __name__ == "__main__":
#    try:
#        import UnicornPy as UnicornPy
#    except:
#        import Engine.UnicornPy as UnicornPy
#else:
#    try:
#        import Engine.UnicornPy as UnicornPy
#    except:
#        import UnicornPy as UnicornPy



class UnicornBlackCheckSignal():
    
    def __init__(self):
        self.killcheck = multiprocessing.Event()
        self.nbchan = 8
        self.freqratio = []
        self.pointstd = []
        self.filtereddata = []
        self.psddata = []
        self.psdclean = []
        self.freqdata = []
        self._samplefreq = 250.0
        self.highpassfilter = 0.1
        self.lowpassfilter = 20
        self.notchfilter = 60
        self.scale = 500.0
        self.controlband = [20, 40]
        self.noiseband = [58, 62]
        self.data = []
        self.psdonfiltereddata = True
        
    def check(self):
        self.freqratio = []
        self.pointstd = []
        self.filtereddata = []
        self.psddata = []
        self.psdclean = []
        self.freqdata = []
        #start = time.perf_counter()
        for cP in range(self.nbchan):
            signalnoiseratio, signalvariability, datavector, _power, _freqs = UnicornGroomQuality(self.data[:,cP], self.controlband, self.noiseband, self._samplefreq, self.scale, self.highpassfilter, self.lowpassfilter, self.notchfilter)
            self.freqratio.append(signalnoiseratio)
            self.pointstd.append(signalvariability)
            self.filtereddata.append(datavector)
            self.psddata.append(_power)
            self.freqdata.append(_freqs)
            if self.psdonfiltereddata:
                _power, _freqs = UnicornGroomPSD(datavector, self._samplefreq, self.scale)
                self.psdclean.append(_power)
            #print('channel %d noise ratio: %0.2f' % (cP, signalnoiseratio))
            #print('channel %d variance: %0.2f' % (cP, signalvariability))
        #finish = time.perf_counter()
        #print(f'Finished in {round(finish-start,8)} seconds(s)')
        

def UnicornGroomPSD(datavector, samplefreq=250.0, scale=500):
    #print('UnicornGroomPSD: called')
    # function to obtain spectral power
    overlaplength = int(len(datavector)/3.0)
    if (int(scale) <= overlaplength):
        overlaplength = int(int(scale)/2.0)
    
    _power = []
    _freqs = []
    _power, _freqs = mlab.psd(x=datavector, NFFT=int(scale), Fs=samplefreq, noverlap=overlaplength, sides='onesided', scale_by_freq=True)
    return _power, _freqs
    #print('UnicornGroomPSD: complete')

def UnicornGroomFilter(datavector, highpassfilter=0.1, lowpassfilter=20.0, notchfilter=60.0, samplefreq=250.0):
    #print('UnicornGroomFilter: called')
    # function to return filtered data
        
    # Apply notch filter
    if not (float(notchfilter) == float(0.0)):
        b, a = scipy.signal.iirnotch(notchfilter, 30.0, samplefreq) # Design notch filter
        datavector = scipy.signal.filtfilt(b=b, a=a, x=datavector, padtype='constant', padlen=int(math.floor(len(datavector)/3.0)), method="pad") 
    
    continuefilt = False
    if not (float(highpassfilter) == float(0.0)):
        if not (float(lowpassfilter) == float(0.0)):
            # band pass
            b, a = scipy.signal.iirfilter(3, [highpassfilter, lowpassfilter], btype='bandpass', ftype='butter', fs=samplefreq, output='ba')
            #sos = scipy.signal.iirfilter(3, [highpassfilter, lowpassfilter], btype='bandpass', ftype='butter', fs=samplefreq, output='sos')
            continuefilt = True
        else:
            # high pass
            b, a = scipy.signal.iirfilter(3, highpassfilter, btype='highpass', ftype='butter', fs=samplefreq, output='ba')
            #sos = scipy.signal.iirfilter(3, highpassfilter, btype='highpass', ftype='butter', fs=samplefreq, output='sos')
            continuefilt = True
    elif not (float(lowpassfilter) == float(0.0)):
        # low pass
        b, a = scipy.signal.iirfilter(3, lowpassfilter, btype='lowpass', ftype='butter', fs=samplefreq, output='ba')
        #sos = scipy.signal.iirfilter(3, lowpassfilter, btype='lowpass', ftype='butter', fs=samplefreq, output='sos')
        continuefilt = True
    
    if continuefilt:     
        #datavector = scipy.signal.filtfilt(b=b, a=a, x=datavector, padtype='constant', padlen=int(math.floor(len(datavector)/3.0)), method="pad") 
        datavector = scipy.signal.filtfilt(b=b, a=a, x=datavector, padtype=None) 
        #datavector = scipy.signal.sosfilt(sos, datavector)    
        
    return datavector
    #print('UnicornGroomFilter: complete')

def UnicornGroomQuality(datavector, controlband, noiseband, samplefreq, scale, highpassfilter, lowpassfilter, notchfilter):
    # function to evaluate quality of signal
    signalnoiseratio = []
    signalvariability = []
    datavector = numpy.ravel(datavector)
    _power, _freqs = UnicornGroomPSD(datavector, samplefreq=samplefreq, scale=scale)
    controlpower = numpy.median(_power[numpy.argmin(abs(_freqs-(controlband[0]))):numpy.argmin(abs(_freqs-(controlband[1])))])
    noisepower = numpy.mean(_power[numpy.argmin(abs(_freqs-(noiseband[0]))):numpy.argmin(abs(_freqs-(noiseband[1])))])
    
    if (float(controlpower) == float(0.0)):
        controlpower = 0.0001
                
    signalnoiseratio = numpy.around(numpy.divide(noisepower, controlpower), decimals=1) # frequency ratio
                  
    datavector = UnicornGroomFilter(datavector, highpassfilter=highpassfilter, lowpassfilter=lowpassfilter, notchfilter=notchfilter, samplefreq=samplefreq)
    
    checkspan = int(math.floor((len(datavector) / 5.0))) * -1
    signalvariability = numpy.std(datavector[checkspan:-1])
    return signalnoiseratio, signalvariability, datavector, _power, _freqs



def UnicornJockey(deviceID, channellabels, rollingspan, logfilename, printoutput, startrecordingeeg, eegready, eegrecording, safetologevent, markeeg, markvalue, pulleegdata, conn, stoprecordingeeg):
    # this is the function that gets pushed to a seperate process that actually controls the device
    
    startedrecording = False
    
    # connect device
    UnicornBlack = UnicornBlackThreads() 
    UnicornBlack.channellabels = channellabels # change channel labels
    UnicornBlack.printoutput = printoutput
    UnicornBlack.connect(deviceID=deviceID, rollingspan=rollingspan, logfilename=logfilename)
    eegready.set()
                
    continueroutine = True
    while continueroutine:
        
        if markeeg.is_set():
            UnicornBlack.mark_event(markvalue.value) # Send trigger 
            markeeg.clear()
            
        if not startedrecording:
            if startrecordingeeg.is_set():
                UnicornBlack.startrecording() # rename file name here
                startedrecording = True
                eegrecording.set()
    
        if startedrecording:
            if stoprecordingeeg.is_set():
                UnicornBlack._safetolog = True # push any remaining items to file
                UnicornBlack.disconnect()
                continueroutine = False
                
        if safetologevent.is_set():
            UnicornBlack.safe_to_log(True)
        else:
            UnicornBlack.safe_to_log(False)
            
        if pulleegdata.is_set():
            sample = UnicornBlack.sample_data()
            #print('UnicornJockey: Battery at %0.1f percent' % numpy.array(sample)[-1,-3])
            if len(sample) > 0:
                conn.send(sample[:])
                pulleegdata.clear()

class UnicornBlackProcess():  
    # this will be the class that the user interfaces with that intializes and maintains the multiprocessing
    
    def __init__(self):
        self.channellabels = 'FZ, C3, CZ, C4, PZ, O1, OZ, O2, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
        self.samplefreq = 250.0
        self.numberOfAcquiredChannels = 17
        self.ready = False
        self.recording = False
        self.printoutput = False
        
    def connect(self, deviceID=None, rollingspan=3.0, logfilename='default'):
        # because of the multiprocessing, to not create additional headaches, the file name needs to be initiallized at connect
        
        self.deviceID = deviceID
        self.rollingspan = rollingspan
        self.logfilename = logfilename
        
        # connect to Device
        self.startrecordingeeg = multiprocessing.Event()
        self.stoprecordingeeg = multiprocessing.Event()
        self.eegready = multiprocessing.Event()
        self.eegrecording = multiprocessing.Event()
        self.safetologevent = multiprocessing.Event()
        self.markeeg = multiprocessing.Event()
        self.markvalue = multiprocessing.Value('i', 0)
        
        # code to be able to pull data
        self.pulleegdata = multiprocessing.Event()
        self.pulleegdata1, self.pulleegdata2 = multiprocessing.Pipe()
        
        self.p = multiprocessing.Process(target=UnicornJockey, args=[self.deviceID, self.channellabels, self.rollingspan, self.logfilename, self.printoutput, self.startrecordingeeg, self.eegready, self.eegrecording, self.safetologevent, self.markeeg, self.markvalue, self.pulleegdata, self.pulleegdata2, self.stoprecordingeeg])
        self.p.start()
        self.eegready.wait(3.0) # wait up to 3 seconds
        self.ready = True
        
    def startrecording(self):
        self.startrecordingeeg.set()
        self.eegrecording.wait(3.0) # wait up to 3 seconds
        self.recording = True
        
    def disconnect(self):
        self.stoprecordingeeg.set()
        self.p.join()
        self.pulleegdata1.close() 
        
    def mark_event(self, event):
        self.markvalue.value = event
        self.markeeg.set()
        
    def safe_to_log(self, boolsafe=True):
        """Parameter to change logging settings
        """
        if boolsafe:
            self.safetologevent.set()
        else:
            self.safetologevent.clear()
        
    def sample_data(self):
        #t = time.perf_counter()
        self.pulleegdata.set() # tell process to obtain a sample
        data = self.pulleegdata1.recv() # takes about 20 ms
        #print(time.perf_counter() - t)
        #tempdata = numpy.array(data)
        #print('UnicornBlackProcess: Battery at %0.1f percent' % tempdata[-1,-3])
        return data
    
    def check_battery(self):
        _plottingdata = numpy.array(self.sample_data(), copy=True)
        powerlevel = 0
        try:
            powerlevel = int(_plottingdata[-1,-3]) # update power level
        except:
            powerlevel = 0
        if self.printoutput:
            print('Device battery at %d percent.' % powerlevel)
        return powerlevel

class UnicornBlackThreads():    
    """class for data collection using the g.tec Unicorn Hybrid Black
	"""
    
    def __init__(self):

        # establish variables
        self.collectversion = '2020.05.30.0'
        self.device = None;
        self.path = os.path.dirname(os.getcwd())
        self.outputfolder = 'Raw'
        
        # create a Queue and Lock
        self._queue = Queue()
        self._queuelock = Lock()
        self._logsamplequeue = Queue()
        self._logeventqueue = Queue()
        self._bufferlock = Lock()
        self._loglock = Lock()
        self._logeventlock = Lock()
        
        # initialize data collectors
        self.logdata = False
        self.logfilename = None
        self._timetemp = None
        self._safetolog = False
        self._dataheaderlog = False
                
        # establish parameters
        self._configuration = None
        self._numberOfAcquiredChannels = None
        self._frameLength = 1
        self._samplefreq = 250.0
        self._intsampletime = 1.0 / self._samplefreq / 10
        self.channellabels = 'FZ, C3, CZ, C4, PZ, O1, OZ, O2, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
        
        # activate
        self._receiveBuffer = None
        self.lastsampledpoint = None
        self.data = None
        self.printoutput = True
        self.ready = True
        self.deviceconnected = False
        
    
    def connect(self, deviceID=None, rollingspan=3.0, logfilename='default'):
        
        self.deviceID = deviceID;
        self.logfilename = logfilename
        # make sure everything is disconnected
        try:
            self.device.StopAcquisition()
        except:
            pass
        del self.device
        self.device = None
        # Did the user specify a particular device
        if (self.deviceID is None):
            try:
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
                deviceID = int(input("Select device by ID #"))
                if deviceID < 0 or deviceID > len(deviceList):
                    raise IndexError('The selected device ID is not valid.')
                self.deviceID = deviceList[deviceID]
        
            except UnicornPy.DeviceException as e:
                print(e)
            except Exception as e:
                print("An unknown error occured. %s" %e)
                
        # Open selected device.
        try:
            self.deviceconnected = 0
            try:
                self.device = UnicornPy.Unicorn(self.deviceID)
                self.deviceconnected = 1
            except:
                pass 
            
            if self.deviceconnected == 1:
                # Initialize acquisition members.
                self._rollingspan = rollingspan # seconds
                self._logchunksize = int(math.floor(5 * self._samplefreq))
                        
                self._numberOfAcquiredChannels = self.device.GetNumberOfAcquiredChannels()
                self._configuration = self.device.GetConfiguration()
            
                # Allocate memory for the acquisition buffer.
                self._receiveBufferBufferLength = self._frameLength * self._numberOfAcquiredChannels * 4
                self._receiveBuffer = bytearray(self._receiveBufferBufferLength)
                self.data = [[0.0] * self._numberOfAcquiredChannels] * math.floor( float(self._rollingspan) * float(self._samplefreq) )
                        
                try:
                    # initialize sample streamer
                    self._streaming = True
                    self._ssthread = Thread(target=self._stream_samples, args=[self._logsamplequeue], daemon=True)
                    self._ssthread.name = 'samplestreamer'
                except:
                    print("Error initializing sample streamer.")
                
                    
                try:
                    # initialize data recorder
                    self._recording = True
                    self._drthread = Thread(target=self._log_sample, args=[self._logsamplequeue], daemon=True)
                    self._drthread.name = 'datarecorder'
                    
                except:
                    print("Error initializing data recorder.")
                    
                    
                try:
                    # initialize event recorder
                    self._eventrecording = True
                    self._erthread = Thread(target=self._log_event, args=[self._logeventqueue], daemon=True)
                    self._erthread.name = 'eventrecorder'
                    
                except:
                    print("Error initializing event recorder.")
                    
                    
                try:
                    # start processes
                    self.device.StartAcquisition(False)  # True - test signal; False - measurement mode
                except:
                    print("Error starting acquisition.")
                    
                self.logdata = False
                self._ssthread.start()
                self._drthread.start()
                self._erthread.start()
                
                time.sleep(1) # give it some initialization time
                
                if self.printoutput:
                    print("Connected to '%s'." %self.deviceID)
            else:
                if self.printoutput:
                    print("Unable to connect to '%s'." %self.deviceID)
        except:
            if self.printoutput:
                print("Unable to connect to '%s'." %self.deviceID)
            
        
        
    def disconnect(self):
       
        time.sleep((self._intsampletime * float(10)))
        
        #self.stoprecording()       
        self._streaming = False
        try:
            self._ssthread.join()
            self._drthread.join()
            self._erthread.join()
        except:
            pass
	
        try:
            self.device.StopAcquisition()
        except:
            pass
                
        try:
            self._logfile.close()
        except:
            pass
        
        del self.device
        self.device = None
        if self.printoutput:
            print("Disconnected from '%s'." %self.deviceID)
        
    def _stream_samples(self, queue):
        """Continuously polls the device, and puts all new samples in a
		Queue instance
		
		arguments
		
		queue		--	a multithreading.Queue instance, to put samples
						into
		"""
		
        # keep streaming until it is signalled that we should stop
        while self._streaming:
            boolgetdata = False
            self._bufferlock.acquire(True)
            try:
                #sampledata = [numpy.ndarray.tolist(numpy.multiply(numpy.random.rand(int(self._numberOfAcquiredChannels)), 100))]
                # Receives the configured number of samples from the Unicorn device and writes it to the acquisition buffer.
                self.device.GetData(self._frameLength,self._receiveBuffer,self._receiveBufferBufferLength)
                # Convert receive buffer to numpy float array 
                sampledata = numpy.frombuffer(self._receiveBuffer, dtype=numpy.float32, count=self._numberOfAcquiredChannels * self._frameLength)
                sampledata = numpy.reshape(sampledata, (self._frameLength, self._numberOfAcquiredChannels))
                boolgetdata = True
            except:
                self._receiveBufferBufferLength = self._frameLength * self._numberOfAcquiredChannels * 4
                self._receiveBuffer = bytearray(self._receiveBufferBufferLength)
                if self.printoutput:
                    print('\n\nOverflow error in polling device.\n\n') 
            self._bufferlock.release()
            
            
            if boolgetdata:   
                self._queuelock.acquire(True)
                if not (str(int(float(self.data[-1][15]))) == str(int(float(sampledata[0][15])))): # protect against sampling the same point twice    
                    #self.lastsampledpoint = copy.deepcopy(sampledata[0][15])
                    self._logeventlock.acquire(True)
                    self.lastsampledpoint = str(int(float(sampledata[0][15])))
                    self._logeventlock.release()
                    queue.put(sampledata)
                    self.data.append(sampledata[0]) 
                    self.data.pop(0)
                self._queuelock.release()
                
                self._bufferlock.acquire(True)
                self._receiveBuffer = bytearray(self._receiveBufferBufferLength) # make sure everything is cleared
                self._bufferlock.release()
        
            #time.sleep(float(0.000000000001)) 
            # if it is in, then we suddenly start getting blocking and drop samples
            # if we comment it out then we get all the samples, but run into an issue with screen flips
            
        self._queuelock.acquire(True)
        queue.put(None) # poison pill approach
        self._queuelock.release()
        self._eventrecording = False
        

    def _log_sample(self, logqueue):
        """Continuously log samples
				
		queue		--	a multithreading.Queue instance, to read samples
						from
		"""
        
        templogholding = None
        finalpush = False
        # keep trying to log until it is signalled that we should stop
        while self._recording:   
            # read new item from the queue 
            while not logqueue.empty():
                self._loglock.acquire(True)
                sampledata = logqueue.get()
                self._loglock.release()
                
                if sampledata is None:
                    # Poison pill means shutdown
                    self._recording = False
                    finalpush = True
                    break
                    break
                else:
                    if self.logdata:
                        if templogholding is None:
                            templogholding = sampledata[:,0:-1]
                        else:
                            templogholding = numpy.vstack([templogholding, sampledata[:,0:-1]])
                            
                        # check if it is safe to log
                        if self._safetolog:
                            # only write chunks of data to save I/O overhead
                            if (len(templogholding) >= self._logchunksize):
                                numpy.savetxt(self._logfile,templogholding,delimiter=',',fmt='%.3f',newline='\n')
                                self._logfile.flush() # internal buffer to RAM
                                os.fsync(self._logfile.fileno()) # RAM file cache to disk
                                templogholding = None            
        if finalpush:
            if templogholding is not None:
                numpy.savetxt(self._logfile,templogholding,delimiter=',',fmt='%.3f',newline='\n')
                self._logfile.flush() # internal buffer to RAM
                os.fsync(self._logfile.fileno()) # RAM file cache to disk
                templogholding = None
                self._logfile.close()

    def _log_event(self, logeventqueue):
        """Continuously log events
				
		logeventqueue	--	a multithreading.Queue instance, to read samples
						from
		"""
        eventheaderlog = False
        templogholding = None
        # keep trying to log until it is signalled that we should stop
        while self._eventrecording:   
            # read new item from the queue 
            while not logeventqueue.empty():
                self._logeventlock.acquire(True)
                sampledata = logeventqueue.get()
                self._logeventlock.release()
            
                # wait to create file until we know there is a need
                if self.logdata:
                    if not eventheaderlog:
                        header = 'collect.....= UnicornPy_' + self.collectversion + '\n'
                        header = header + 'date........= ' + self._timetemp  + '\n'
                        header = header + 'filename....= ' + self.logfilename  + '\n'
                        header = header + 'Latency, Event' + '\n'
                        self._eventlogfile = open('%s.csve' % (self.logfilename), 'w')
                        self._eventlogfile.write(header) # to internal buffer
                        self._eventlogfile.flush() # internal buffer to RAM
                        os.fsync(self._eventlogfile.fileno()) # RAM file cache to disk  
                        eventheaderlog = True 
                    
                if sampledata is None:
                    # Poison pill means shutdown
                    self._eventrecording = False
                    break
                    break
                else:
                    if self.logdata:
                        if templogholding is None:
                            templogholding = sampledata
                        else:
                            templogholding = numpy.vstack([templogholding, sampledata])
                            
                        # check if it is safe to log
                        if self._safetolog:
                            # only write chunks of data to save I/O overhead
                            if (len(templogholding) >= self._logchunksize):
                                numpy.savetxt(self._eventlogfile,templogholding,delimiter=',',fmt='%.3f',newline='\n')
                                self._eventlogfile.flush() # internal buffer to RAM
                                os.fsync(self._eventlogfile.fileno()) # RAM file cache to disk
                                templogholding = None            
        
        if templogholding is not None:
                numpy.savetxt(self._eventlogfile,templogholding,delimiter=',',fmt='%s',newline='\n')
                self._eventlogfile.flush() # internal buffer to RAM
                os.fsync(self._eventlogfile.fileno()) # RAM file cache to disk
                templogholding = None
                self._eventlogfile.close()
        
        
    def startrecording(self):
        
        self.logdata = True
        timetemp = str(datetime.now()).split()
        self._timetemp = timetemp[0] + 'T' + timetemp[1]
        self._logfile = open('%s.csv' % (self.logfilename), 'w')
        self._safetolog = True
        self._log_header()
        
        # ensure we are getting data
        nc = 0
        while (str(int(float(self.data[-1][15]))) == str(int(float(0.0)))):
            nc = nc + 1
        
        if self.printoutput:
            print("Starting Recording")
	
                        
    def _log_header(self):
        """Logs a header to the data file
        """
        if not self._dataheaderlog: 
            header = 'collect.....= UnicornPy_' + self.collectversion + '\n'
            header = header + 'device......= ' + self.deviceID  + '\n'
            header = header + ('samplerate..= %.3f' % self._samplefreq)  + '\n'
            header = header + ('channels....= %d' % (self._numberOfAcquiredChannels - 1))  + '\n'
            header = header + 'date........= ' + self._timetemp  + '\n'
            header = header + 'filename....= ' + self.logfilename  + '\n'
            
            header = header + self.channellabels + '\n'
            #'FZ, C3, CZ, C4, PZ, O1, OZ, O2, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
            self._logfile.write(header) # to internal buffer
            self._logfile.flush() # internal buffer to RAM
            os.fsync(self._logfile.fileno()) # RAM file cache to disk
            self._dataheaderlog = True 
       
            
    def mark_event(self, event):
        """Logs data to the event file
        """
        if self.lastsampledpoint is not None:
            self._logeventlock.acquire(True)
            self._logeventqueue.put(numpy.array([str(self.lastsampledpoint), str(event)]))
            self._logeventlock.release()
        
    def safe_to_log(self, boolsafe=True):
        """Parameter to change logging settings
        """
        self._safetolog = boolsafe  
        
    def sample_data(self):
        try:
            datasample = self.data[:]
        except:
            datasample = []
        return datasample
            
    def check_battery(self):
        _plottingdata = numpy.array(self.sample_data(), copy=True)
        powerlevel = 0
        try:
            powerlevel = int(_plottingdata[-1,-3]) # update power level
        except:
            powerlevel = 0
            
        if self.printoutput:
            print('Device battery at %d percent.' % powerlevel)
        return powerlevel
    
# # # # #
# DEBUG #
if __name__ == "__main__":
    
    duration = 5 # seconds
    example = 'Thread' # Process or Thread
    
    if example == 'Thread':
        # Example code for calling the Unicorn device as a process
        UnicornBlack = UnicornBlackProcess()  
    else:    
        # Example code for calling the Unicorn device as a thread
        UnicornBlack = UnicornBlackThreads()   
        
    # all other functions and calls remain the same    
    UnicornBlack.connect(deviceID='UN-2021.05.36', rollingspan=3, logfilename='recordeddata_thread')
    
    UnicornBlack.startrecording()
    
    for incrX in range(duration):
        time.sleep(1)
        UnicornBlack.safe_to_log(False)
        UnicornBlack.mark_event(incrX)
        print("Time Lapsed: %d second" % (incrX+1))
        UnicornBlack.safe_to_log(True)
        
    example = numpy.array(UnicornBlack.sample_data())
    print('Battery at %0.1f percent' % example[-1,-3])
    UnicornBlack.disconnect()
    
    # Plotting function to check for dropped samples
    #
    #selectsampleddata = []
    #for incrX in range(len(sampleddata)):
    #    if not (sampleddata[incrX][0] == float(0)):
    #        selectsampleddata.append(sampleddata[incrX])
    #sampleddata = numpy.array(selectsampleddata)
    #del selectsampleddata
    
    #if (sampleddata.shape[0]) > 2:
    #    x = numpy.arange(sampleddata[0][15],sampleddata[-1][15],1) 
    #    y = numpy.array([0] * len(x))
    #    for incrX in range(len(sampleddata)):
    #        index_min = numpy.argmin(abs(x-(sampleddata[incrX][15])))
    #        #y[index_min] = sampleddata[incrX][15]
    #        y[index_min] = 1
    #    del index_min, incrX
    #    x = x * (1/ 250.0)
    #    plt.plot(x,y)
    #    print('The streamer had a total of %d dropped samples (%0.1f%%).' %(len(y)-numpy.count_nonzero(y), ((len(y)-numpy.count_nonzero(y))/len(y))*100))
        
    # show saved data
    #lis = []
    #with open("C:\\Studies\\Python Collect\\Gentask\\Raw\\recordeddata.csv", "rb") as f: 
    #    for cnt, line in enumerate(f):
    #        lis.append(line.decode("utf-8").split(','))
    #f.close()
    #del cnt, line
    #lis = lis[7:-1]
    #x2 = numpy.arange(int(float(lis[0][15])),int(float(lis[-1][15])),1) 
    #y2 = numpy.array([0] * len(x2))
    #for incrX in range(len(lis)):
    #    index_min = numpy.argmin(abs(x2-(int(float(lis[incrX][15])))))
    #    y2[index_min] = 1
    #del index_min, incrX
    
    
    # read in event markers
    #eventlis = []
    #with open("C:\\Studies\\Python Collect\\Gentask\\Raw\\recordeddata.csve", "rb") as f: 
    #    for cnt, line in enumerate(f):
    #        eventlis.append(line.decode("utf-8").split(','))
    #f.close()
    #del cnt, line
    #eventlis = eventlis[4:-1]
    
    #y3 = numpy.array([0] * len(x2))
    #for incrX in range(len(eventlis)):
    #    index_min = numpy.argmin(abs(x2-(int(float(eventlis[incrX][0])))))
    #    y3[index_min] = 2
    #del index_min, incrX
    # 
    # x2 = x2 * (1/ 250.0)
    #plt.plot(x2,y2)
    #plt.plot(x2,y3)
    #print('The recording had a total of %d dropped samples (%0.1f%%).' %(len(y2)-numpy.count_nonzero(y2), ((len(y2)-numpy.count_nonzero(y2))/len(y2))*100))
    
    
    # core.wait was responsible for the dropped samples!
    

# # # # #
