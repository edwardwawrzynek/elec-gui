import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from device_gui import DeviceGUI, ChannelGUI
from dev_gui_option import DevOptionGUIGroup, DevOptionGUI

import numpy as np
import xarray as xr
from astropy import units

class TestChannel(ChannelGUI):
    def __init__(self, dev, data):
        super().__init__(dev, data)

        self.setName(data)
        self.addOption(DevOptionGUI("max", "float", lambda x:x, default=1.0))
        self.addOption(DevOptionGUI("min", "float", lambda x:x, default=0.0))
        self.addOption(DevOptionGUI("unit", "string", lambda x:x, default="V"))
    
    def collectData(self):
        #return random data
        maxV = self.options.getStateByLabel("max")
        minV = self.options.getStateByLabel("min")
        
        return xr.DataArray(
            np.random.rand(100)*(maxV-minV)+minV, 
            dims=('t'), 
            coords={'t':np.arange(0.0, 10.0, 0.1)},
            attrs={'units':{'':units.Unit(self.options.getStateByLabel("unit")), 't':units.s}})

    def getXAxisDim(self):
        return 't'


class TestDev(DeviceGUI):
    def __init__(self, data):
        super().__init__(data)

        self.setName(data)

        self.addOption(DevOptionGUI("random device option", "string", lambda x:x))
        self.addOption(DevOptionGUI("random float", "float", lambda x:x))
        self.addOption(DevOptionGUI("random bool option", "bool", lambda x:x, default=True))
        self.addOption(DevOptionGUI("random button", "button", lambda x:x))
        self.addOption(DevOptionGUI("random int", "int", lambda x:x, default=-5))
        #Add ten channels
        for i in range(10):
            self.addChannel(TestChannel(self, "channel %i" % i))
