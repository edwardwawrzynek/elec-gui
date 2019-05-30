import re, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from device_gui import DeviceGUI, ChannelGUI
from dev_gui_option import DevOptionGUIGroup, DevOptionGUI

import numpy as np
import xarray

class TestChannel(ChannelGUI):
    def __init__(self, dev, data):
        super().__init__(dev, data)

        self.setName(data)
        self.addOption(DevOptionGUI("max", "float", lambda x:x, default=1.0))
        self.addOption(DevOptionGUI("min", "float", lambda x:x, default=0.0))
    
    def collectData(self):
        #return random data
        maxV = self.options.getStateByLabel("max")
        minV = self.options.getStateByLabel("min")
        return xarray.DataArray(np.array([np.arange(0.0, 10.0, 0.1), minV+np.random.rand(100)*(maxV-minV), minV+np.random.rand(100)*(maxV-minV)]), coords={'x':['time', 'volts', 'frequency']}, dims=('x', 'y'))

    def getDataLabels(self):
        return ['time', 'volts', 'frequency']

class TestDev(DeviceGUI):
    def __init__(self, data):
        super().__init__(data)

        self.setName(data)

        self.addOption(DevOptionGUI("random device option", "string", lambda x:x))
        self.addOption(DevOptionGUI("random float", "float", lambda x:x))
        self.addOption(DevOptionGUI("random bool option", "bool", lambda x:x))
        self.addOption(DevOptionGUI("random button", "button", lambda x:x))
        #Add ten channels
        for i in range(10):
            self.addChannel(TestChannel(self, "channel %i" % i))
