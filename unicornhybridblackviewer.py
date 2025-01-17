# unicornhybridblackviewer: classes to visualize data from the unicornhybridblack
#
"""
Working notes
- Works best when run in external terminal

@author: Matt Pontifex
"""

import math
import numpy
import time
from threading import Thread, Lock
import matplotlib
import matplotlib.pyplot
import matplotlib.animation
from matplotlib.widgets import Button
import matplotlib.ticker as ticker
import unicornhybridblack as unicornhybridblack

#try:
#    import unicornhybridblack as unicornhybridblack
#except:
#    import Engine.unicornhybridblack as unicornhybridblack


matplotlib.rcParams['toolbar'] = 'None' 


class Viewer():
    
    
    def __init__(self):
        
        self.samplefreq = 250.0
        self.timeplotscale = 4.475
        self.computedscale = 0
        self.timeplotoffsetscale = 2000
        self.freqplotscale = 0.005
        self.numberOfAcquiredChannels = 8
        self.rollingspan = 13.5
        self.trimspanlead = 0.5
        self.trimspantrail = 2.0
        self.unicornchannels = 'FZ, FC1, FC2, C3, CZ, C4, CPZ, PZ, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
        self.channellabels = self.unicornchannels.split(',')[0:int(self.numberOfAcquiredChannels)]
        self.updatetime = 200 # update every x ms
        self.updatetimelog = []
        self._stop = False

        self._linewidth = 0.5
        self._data = []
        self.datamatrixforplotting = []
        self._datamatrixforplottinglock = Lock()
        self.frequencymatrixforplotting = []
        self._frequencymatrixforplottinglock = Lock()
        
        self.lowpassfilter = 26.0
        self.highpassfilter = 1.0
        self.controlband = [20, 40] # hz
        self.noiseband = [58, 62] # hz
        self.unicorn = 'UN-2021.05.36' 
        self.UnicornBlack = []
        
        self.WindowColor = '#D9D9D9'
        self.AxisColor = '#C7C7C7'
        self.AxisTickColor = '#828282'
        self.TimePlotColor = '#FFFFFF'
        self.FrequencyPlotColor = '#F5F5F5'
        self.AxisFontSize = 6
        self.DeviceLabelColor = '#828282'
        self.DeviceLabelSize = 8
        self.ButtonLabelSize = 7
        self.ButtonFaceColor = '#4D4D4D'
        self.ButtonTextColor = '#FFFFFF'
        self.ButtonHoverColor = '#BABABA'
        
        self.ChannelTextColorH = '#FFFFFF'
        self.ChannelTextColorC = '#000000'
        self.ChannelTextSize = 10
        
        self.eegspectdeltacenter = 2
        self.eegspectthetacenter = 6
        self.eegspectalphacenter = 9.5
        self.eegspectbetacenter = 20
        
        
        # initial
        #self.goodchannel = '#21B31E'
        #self.almostchannel = '#2BDAFF'
        #self.gettingtherechannel = '#D126FF'
        #self.badchannel = '#FF0046'
        
        
        # playful
        self.greatchannel = '#9bc53d'
        self.goodchannel = '#5bc0eb'
        self.almostchannel = '#fde74c'
        self.gettingtherechannel = '#e55934'
        self.badchannel = '#e55934'
        
        
        
    def prep(self):
        self.channellabels = self.unicornchannels.split(',')[0:int(self.numberOfAcquiredChannels)]
        
        self.trimspan = self.trimspanlead + self.trimspantrail
        
        #self.norm = matplotlib.colors.Normalize(vmin=500, vmax=4000.0)
        cm_subsection = numpy.linspace(0.0, 1.0, int(self.numberOfAcquiredChannels*1.5)) 
        self.colorpalet = [ matplotlib.pyplot.cm.viridis(x) for x in cm_subsection ]
        
        # figure out some spacing issues
        channellabelspacing = []
        gapping = (0.95-0.07-0.002) / float(self.numberOfAcquiredChannels)
        push = 0.017
        for cC in range(self.numberOfAcquiredChannels):
            channellabelspacing.append(((cC + 1) * gapping) + push)
        
        # Connect to device
        
        self.UnicornBlack = unicornhybridblack.UnicornBlackProcess() 
        self.UnicornBlack.printoutput = True
        self.UnicornBlack.connect(deviceID=self.unicorn, rollingspan=self.rollingspan)
        
        continueExperiment = False
        while not self.UnicornBlack.ready:
            continueExperiment = False
            
        self.powerlevel = self.UnicornBlack.check_battery()
        if (self.powerlevel == 0):
            print('The Unicorn is out of battery charge.')
        
        
        self.altchannellabels = self.channellabels[:]
        self.altchannellabels.reverse()
        
        # establish some parameters
        self.data = [[0.0] * self.numberOfAcquiredChannels] * int(math.floor( float(self.rollingspan) * float(self.samplefreq) ))
        if not (float(self.trimspan) == float(0)):
            self._trimspanleadpoints = int(math.floor( float(self.trimspanlead) * float(self.samplefreq) ))
            self._trimspantrailpoints = int(math.floor( float(self.trimspantrail) * float(self.samplefreq) ))
            self.rollingspan = float(self.rollingspan) - (float(self.trimspan))
            
        self._rollingspanpoints = int(math.floor( float(self.rollingspan) * float(self.samplefreq) ))
        self.xtime = numpy.ndarray.tolist(numpy.linspace(0, self.rollingspan, self._rollingspanpoints))
        self._baselinerollingspan = int(math.floor(self._rollingspanpoints / float(5.0)))
        self.xtimeticks = numpy.linspace(1,int(math.floor(self.rollingspan-1)),int(self.rollingspan-1)).tolist()
        self.xtimeticks = [int(i) for i in self.xtimeticks] 
        
        self.fig = matplotlib.pyplot.figure(figsize=[10, 6])
        self.fig.patch.set_facecolor(self.WindowColor)
        gs = self.fig.add_gridspec(1, 3)
        
        self.timeax = self.fig.add_subplot(gs[:, 0:2])
        self.freqax = self.fig.add_subplot(gs[:, -1])
                                     
        matplotlib.pyplot.gcf().canvas.set_window_title('Unicorn Hybrid Black')
        matplotlib.pyplot.tight_layout()
        matplotlib.pyplot.subplots_adjust(left=0.073, bottom=0.07, right=1, top=0.95, wspace=0.02, hspace=0)
        self.fig.canvas.window().statusBar().setVisible(False) # Remove status bar (bottom bar)
        self.fig.canvas.mpl_connect('close_event', self.handle_close)
        
        # Configure time plot
        self.timeax.spines['top'].set_visible(False)
        self.timeax.spines['right'].set_visible(False)
        self.timeax.spines['bottom'].set_visible(True)
        self.timeax.spines['bottom'].set_color(self.AxisColor) 
        self.timeax.tick_params(axis='x', colors=self.AxisColor)
        self.timeax.spines['left'].set_visible(False)
        self.timeax.get_yaxis().set_ticks([])
        self.timeax.set_xlim([0, self.rollingspan])
        self.timeax.xaxis.set_major_locator(ticker.FixedLocator(self.xtimeticks))
        self.timeax.set_ylim([0, (self.numberOfAcquiredChannels+1)*self.timeplotoffsetscale])
        self.timeax.use_sticky_edges = True
        self.timeax.patch.set_facecolor(self.TimePlotColor)
        
        for item in (self.timeax.get_xticklabels()):
            item.set_fontsize(self.AxisFontSize)
        self.timeax.tick_params(axis='x', colors=self.AxisTickColor)
        
        # Configure frequency plot
        self.freqax.spines['top'].set_visible(False)
        self.freqax.spines['right'].set_visible(False)
        self.freqax.spines['bottom'].set_visible(True)
        self.freqax.spines['bottom'].set_color(self.AxisColor)
        self.freqax.tick_params(axis='x', colors=self.AxisColor)
        self.freqax.spines['left'].set_visible(False)
        self.freqax.get_yaxis().set_ticks([])
        self.freqax.set_xlim([1, 33])
        self.freqax.xaxis.set_major_locator(ticker.FixedLocator([self.eegspectdeltacenter, self.eegspectthetacenter, self.eegspectalphacenter, self.eegspectbetacenter, 30]))
        self.freqax.set_xticklabels(['Delta', 'Theta', 'Alpha', 'Beta', 'raw 60hz'])
        self.freqax.set_ylim([0, (self.numberOfAcquiredChannels+1)*self.timeplotoffsetscale])
        self.freqax.use_sticky_edges = True
        self.freqax.patch.set_facecolor(self.FrequencyPlotColor)
                                        
        for item in (self.freqax.get_xticklabels()):
            item.set_fontsize(self.AxisFontSize)
        self.freqax.tick_params(axis='x', colors=self.AxisTickColor)
        
        # Add device information
        self.devicelabel = self.fig.text(0.03, 0.983, 'Device: unknown', horizontalalignment='left', verticalalignment='top', weight='medium', size=self.DeviceLabelSize, color=self.DeviceLabelColor)
        self.batterylabel = self.fig.text(0.97, 0.983, 'Battery: unknown', horizontalalignment='right', verticalalignment='top', weight='medium', size=self.DeviceLabelSize, color=self.DeviceLabelColor)
        self.devicelabel.set_text('Device: %s' % self.UnicornBlack.deviceID)
        self.batterylabel.set_text('Battery: %d%%' % int(self.powerlevel))
        
        # Add buttons
        self.timescalelabel = self.fig.text(0.685, 0.07, '1 microvolt', horizontalalignment='right', verticalalignment='bottom', weight='medium', size=self.AxisFontSize, color=self.DeviceLabelColor)
        
        self.eegscaleupbutton = Button(matplotlib.pyplot.axes([0.405, 0.005, 0.12, 0.03]), 'scale up', color=self.ButtonFaceColor, hovercolor=self.ButtonHoverColor)  #xpos, ypos, xsize, ysize
        self.eegscaleupbutton.label.set_fontsize(self.ButtonLabelSize)
        self.eegscaleupbutton.label.set_color(self.ButtonTextColor)
        self.eegscaleupbutton.on_clicked(self.eegscaleupbutton_clk)
        self.eegscaledownbutton = Button(matplotlib.pyplot.axes([0.53, 0.005, 0.12, 0.03]), 'scale down', color=self.ButtonFaceColor, hovercolor=self.ButtonHoverColor)  #xpos, ypos, xsize, ysize
        self.eegscaledownbutton.label.set_fontsize(self.ButtonLabelSize)
        self.eegscaledownbutton.label.set_color(self.ButtonTextColor)
        self.eegscaledownbutton.on_clicked(self.eegscaledownbutton_clk)
        self.freqscaleupbutton = Button(matplotlib.pyplot.axes([0.83, 0.005, 0.08, 0.03]), 'scale up', color=self.ButtonFaceColor, hovercolor=self.ButtonHoverColor)  #xpos, ypos, xsize, ysize
        self.freqscaleupbutton.label.set_fontsize(self.ButtonLabelSize)
        self.freqscaleupbutton.label.set_color(self.ButtonTextColor)
        self.freqscaleupbutton.on_clicked(self.freqscaleupbutton_clk)
        self.freqscaledownbutton = Button(matplotlib.pyplot.axes([0.915, 0.005, 0.08, 0.03]), 'scale down', color=self.ButtonFaceColor, hovercolor=self.ButtonHoverColor)  #xpos, ypos, xsize, ysize
        self.freqscaledownbutton.label.set_fontsize(self.ButtonLabelSize)
        self.freqscaledownbutton.label.set_color(self.ButtonTextColor)
        self.freqscaledownbutton.on_clicked(self.freqscaledownbutton_clk)
        
        # Add channel labels
        self.chanlables = []
        for cC in range(self.numberOfAcquiredChannels):
            channellabel = self.fig.text(0.046, channellabelspacing[cC], '%4s' % self.altchannellabels[cC], horizontalalignment='right', verticalalignment='center', weight='medium', size=self.ChannelTextSize, color=self.ChannelTextColorC, bbox=dict(facecolor=self.ChannelTextColorH, edgecolor=self.DeviceLabelColor, boxstyle='square,pad=1.83') )
            self.chanlables.append(channellabel)
        
        # Add lines
        _plottingdata = numpy.array(self.data, copy=True)
        if not (float(self.trimspan) == float(0)):
            _plottingdata = _plottingdata[self._trimspantrailpoints:-self._trimspanleadpoints,:]
        self.lines = []
        self.offset = []
        self.freqoffset = []
        for cC in range(self.numberOfAcquiredChannels):
            line, = self.timeax.plot(self.xtime, _plottingdata[:,cC], linewidth=0.6, color=self.colorpalet[cC]) 
            self.lines.append(line)
            self.offset.append(((cC + 1)*(self.timeplotoffsetscale+240)) - 1000)
            self.freqoffset.append(((cC + 1)*(self.timeplotoffsetscale+240)) - 2000)
        self.computedscale = ((self.offset[1]-self.offset[0]) / self.timeplotscale)
        
        # Prep data checks
        self.datacheck = unicornhybridblack.UnicornBlackCheckSignal()
        self.datacheck.controlband = self.controlband # hz
        self.datacheck.noiseband = self.noiseband # hz
        self.datacheck.highpassfilter = self.highpassfilter # hz
        self.datacheck.lowpassfilter = self.lowpassfilter # hz
        
        # test run
        self.datacheck.data = numpy.array(self.data, copy=True)   
        self.datacheck.check()
        self.freqxline = self.datacheck.freqdata[0]
                
        noisesegs = [numpy.argmin(abs(numpy.subtract(self.freqxline, 55.0))), numpy.argmin(abs(numpy.subtract(self.freqxline, 66.0)))]
        self.switchsegs = [numpy.argmin(abs(numpy.subtract(self.freqxline, 25.0)))]
        self.switchsegs.append(self.switchsegs[0] + (noisesegs[1]-noisesegs[0]))
        self.switchsegs.append(noisesegs[0])
        self.switchsegs.append(noisesegs[1])
        
        # populate frequency information
        self.freqlines = []
        for cC in range(self.numberOfAcquiredChannels):
            line, = self.freqax.plot(self.freqxline, self.datacheck.psddata[cC], linewidth=0.4, color=self.colorpalet[cC]) 
            self.freqlines.append(line)
            
        # start sampler
        #self._sampling = True
        #self._sthread = Thread(target=self.updatesamples, args=[], daemon=False)
        #self._sthread.name = 'samplestreamer'
        #self._sthread.start()
        
    def eegscaleupbutton_clk(self, *args): 
        tempvalue = self.timeplotscale * 2.0
        #if ((tempvalue) < 999999999):
        self.timeplotscale = tempvalue
        self.updatescale()
        
    def eegscaledownbutton_clk(self, *args): 
        tempvalue = self.timeplotscale / 2.0
        #if ((tempvalue) > 0.000000999):
        self.timeplotscale = tempvalue
        self.updatescale()
            
    def freqscaleupbutton_clk(self, *args): 
        tempvalue = self.freqplotscale * 2.0
        #if ((tempvalue) < 999999999):
        self.freqplotscale = tempvalue
        
    def freqscaledownbutton_clk(self, *args): 
        tempvalue = self.freqplotscale / 2.0
        #if ((tempvalue) > 0.000000999):
        self.freqplotscale = tempvalue
            
            
    def updatescale(self):
        if not self._stop:
            # update scale
            self.computedscale = ((self.offset[1]-self.offset[0]) / self.timeplotscale)
            textscale = self.computedscale
            
            textscaleunits = 'microvolts'
            if (textscale > 1000):
                textscaleunits = 'millivolts'
                textscale = textscale/1000
                if (textscale > 1000):
                    textscaleunits = 'volts'
                    textscale = textscale/1000
            elif (textscale < 1000):
                if (textscale < 1):
                    textscaleunits = 'nanovolts'
                    textscale = textscale*1000
                    if (textscale < 1):
                        textscaleunits = 'picovolts'
                        textscale = textscale*1000
                       
            self.timescalelabel.set_text('%d %s' % (int(textscale),textscaleunits))
            self.fig.canvas.draw_idle()
            #print(numpy.median(self.updatetimelog))
        
        
    def _computedataoffset(self, source):
        source = numpy.transpose(source)
        channelbaseline = numpy.mean(source[-self._baselinerollingspan:,:], axis=0)
        baselineddata = numpy.subtract(source, channelbaseline)
        scaleddata = numpy.multiply(baselineddata,self.timeplotscale)
        source = numpy.add(scaleddata, self.offset)
        return source
    
    def _computefreqoffset(self, source):
        source = numpy.transpose(source)
        scaleddata = numpy.multiply(source,self.freqplotscale)
        source = numpy.add(scaleddata, self.freqoffset)
        return source
        
        
    def run(self):
        print('Initializing Unicorn Hybrid Black Data Viewer...')
        self.prep()
        self.updatescale()
        
        #print('Close window to disconnect...')
        self.ani = matplotlib.animation.FuncAnimation(self.fig, self.update, interval=self.updatetime, blit=False)
        matplotlib.pyplot.show()
        
    def close(self):
        try:
            self.ani.event_source.stop()
        except:
            pass
        try:
            matplotlib.pyplot.close('all')
        except:
            pass
        try:
            self.UnicornBlack.p.terminate()
        except:
            pass
        try:
            self.UnicornBlack.p.join()
        except:
            pass
        try:
            # stop recording
            self.UnicornBlack.disconnect()
        except:
            pass
        
    def handle_close(self, evt, *args):
        self.fig.canvas.manager.window.destroy()
        self._stop = True
        self.close()
        
        
    def update(self, *args):
        if not self._stop:
            threspoints = [12, 16, 30, 60]
            self.freqax.collections.clear()
            self.freqfillbetween = []
    
            self.updatesamples()
            
            boolcont = True
            try:
                self.batterylabel.set_text('Battery: %d%%' % self.powerlevel)
            except:
                boolcont = False
                
            if boolcont:
                # takes about 8 ms to update all the channels info
                
                # loop through each channel
                for cP in range(self.numberOfAcquiredChannels):
                    try:
                        datavector = self.datamatrixforplotting[:,cP]
                        pstd = self.datacheck.pointstd[cP]
                        if (pstd < threspoints[0]):
                            newtexture = self.greatchannel
                        elif ((pstd >= threspoints[0]) and (pstd < threspoints[1])):
                            newtexture = self.goodchannel
                        elif ((pstd >= threspoints[1]) and (pstd < threspoints[2])):
                            newtexture = self.almostchannel
                        elif ((pstd >= threspoints[2]) and (pstd < threspoints[3])):
                            newtexture = self.gettingtherechannel
                        else:
                            newtexture = self.badchannel
                        self.chanlables[self.numberOfAcquiredChannels-1-cP].set_bbox(dict(facecolor=newtexture, edgecolor=newtexture, boxstyle='square,pad=1.83'))
                    except:
                        #print('error in time plot')
                        pass                    
                    try:
                        self.lines[cP].set_ydata(datavector)
                        self.freqlines[cP].set_ydata(self.frequencymatrixforplotting[:,cP])
                        self.freqfillbetween.append(self.freqax.fill_between(self.freqxline, y1=self.frequencymatrixforplotting[:,cP], y2=[self.freqoffset[cP]] * len(self.frequencymatrixforplotting[:,cP]), facecolor =self.colorpalet[cP], alpha=0.5))
                    except:
                        #print('error in freq plot')
                        pass  
            
        return self.batterylabel, self.chanlables[0], self.chanlables[1], self.chanlables[2], self.chanlables[3], self.chanlables[4], self.chanlables[5], self.chanlables[6], self.chanlables[7], self.lines[0], self.lines[1], self.lines[2], self.lines[3], self.lines[4], self.lines[5], self.lines[6], self.lines[7]
            
    def updatesamples(self):
        # this whole function takes about 60 ms to complete
        # it takes about 50 ms to pull the data
        # it takes about 15 ms to filter the data and compute the PSD
        # the rest is all pretty fast
        
        #while self._sampling:
            
        #t = time.perf_counter()
        if not self._stop:
            boolcont = True
            try:
                _plottingdata = numpy.array(self.UnicornBlack.sample_data(), copy=True)
            except:
                boolcont = False
            
            if boolcont:    
                try:
                    self.powerlevel = int(_plottingdata[-1,-3])
                
                   
                    self.datacheck.data = _plottingdata
                    self.datacheck.check()
                    
                    _plottingdata = numpy.array(self.datacheck.filtereddata, copy=True)
                    if not (float(self.trimspan) == float(0)):
                        _plottingdata = _plottingdata[:,self._trimspantrailpoints:-self._trimspanleadpoints]
                        
                    _plottingdata[0:8,:] = numpy.flipud(_plottingdata[0:8,:])
                    _plottingdata = self._computedataoffset(_plottingdata)
    
                    self.datamatrixforplotting = _plottingdata[:]
                    
                    # manage frequency data
                    _freqdatanoise = numpy.array(self.datacheck.psddata, copy=True)
                    _freqdata = numpy.array(self.datacheck.psdclean, copy=True)
                    # remove frequency bands not of interest - swap noise measure in
                    _freqdata[:,self.switchsegs[0]:self.switchsegs[1]] = _freqdatanoise[:,self.switchsegs[2]:self.switchsegs[3]]
                    _freqdata[0:8,:] = numpy.flipud(_freqdata[0:8,:])
                    _freqdata = self._computefreqoffset(_freqdata)
                    
                    self.frequencymatrixforplotting = _freqdata[:]
                    
                except:
                    boolcont = False
            
        
        #elapsed_time = time.perf_counter() - t
        #self.updatetimelog.append(elapsed_time)
            
if __name__ == '__main__':
    task = Viewer()
    task.unicornchannels = 'FZ, FC1, FC2, C3, CZ, C4, CPZ, PZ, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
    task.unicorn = 'UN-2021.05.36'
    task.run()