import re, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import numpy as np, xarray

from dev_gui_option import DevOptionGUIGroup


#The interface to the gui for devices. Can be a standalone driver, or, more likely, a driver that will call a lower level-driver

class DeviceGUI:
    #data is arbitrary data (probably port info, etc) passed during construction
    def __init__(self, data):
        #dev name
        self.name = ""
        #channels (need to be added by subclass)
        self.channels = []
        #options (device wide)
        self.options = DevOptionGUIGroup([])

        self.generateComponent()

    #set name
    def setName(self, name):
        self.name = name

    #add option
    def addOption(self, option):
        self.options.addOption(option)

    #create the initial component structure
    def generateComponent(self):
        self.vbox = Gtk.VBox()
        #TODO: VBox with channel switcher, HBox withs scrolled window of dev options on left, channel options on right

        self.chan_stack = Gtk.Stack()
        self.chan_switch = Gtk.StackSwitcher()
        self.chan_switch.set_stack(self.chan_stack)

        self.vbox.pack_start(Gtk.Label("Device Options:"), False, False, 0)
        self.vbox.pack_start(self.options.getComponent(), True, True, 0)
        self.vbox.pack_start(Gtk.HSeparator(), False, False, 0)
        self.vbox.pack_start(Gtk.Label("Channel Options:"), False, False, 0)
        self.vbox.pack_start(self.chan_stack, True, True, 0)

    def addChannel(self, chan):
        self.channels.append(chan)
        self.chan_stack.add_titled(chan.options.getComponent(), chan.name, chan.name)
        self.chan_stack.show_all()

    def getComponent(self):
        return self.vbox
    
    def getSwitchComponent(self):
        return self.chan_switch
    
    #trigger a collection on all children
    def triggerChannelsCollection(self):
        for chan in self.channels:
            #TODO: make this actually be called async
            chan.triggerCollection()
    

class ChannelGUI:
    #data is arbitrary data passed to channel by dev
    def __init__(self, dev, data):
        #name of channel
        self.name = ""
        #options (channel specific)
        self.options = DevOptionGUIGroup([])
        #most recent data collection
        self.data = xarray.DataArray([[]], dims=('x', 'y'))
        #device that owns the channel
        self.parent = dev

    def setName(self, name):
        self.name = name

    def addOption(self, option):
        self.options.addOption(option)
    
    #callback on trigger for data collection
    #this will be run in a separate thread, so it should block until data is ready and then return it
    #it should return a 2-dimensional xarray with dimension labels x and y, and labeled x coordinates coresponding to the type of data (time, volts, etc)
    def collectData(self):
        #return random data
        return xarray.DataArray(np.random.randn(3,20), coords={'x':['time', 'volts', 'frequency']}, dims=('x', 'y'))

    def triggerCollection(self):
        self.data = self.collectData()
        return self.data
    
    #get most recently collected data
    def getData(self):
        #TODO: locking (for async), etc ?
        return self.data