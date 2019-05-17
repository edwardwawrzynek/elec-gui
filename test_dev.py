import re, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from device_gui import DeviceGUI, ChannelGUI
from dev_gui_option import DevOptionGUIGroup, DevOptionGUI

class TestChannel(ChannelGUI):
    def __init__(self, data):
        super().__init__(data)

        self.setName(data)
        self.addOption(DevOptionGUI("max", "float", lambda x:x))
        self.addOption(DevOptionGUI("min", "float", lambda x:x))


class TestDev(DeviceGUI):
    def __init__(self, data):
        super().__init__(data)

        self.setName(data)

        self.addOption(DevOptionGUI("num chans", "float", self.setChans))
        self.addOption(DevOptionGUI("trigger", "button", lambda x:
            self.addOption(DevOptionGUI("additional button", "button", lambda x:print("hi")))
        ))

    def setChans(self, numChans):
        for i in range(int(numChans)):
            self.addChannel(TestChannel("channel %i" % i))
