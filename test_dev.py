import re, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from device_gui import DeviceGUI, ChannelGUI, DevOptionGUIGroup

class TestChannel(ChannelGUI):
    def __init__(self, data):
        self.name = data["name"]
        self.options = DevOptionGUIGroup([
            {"label": "max", "type": "float", "callback": lambda x:x},
            {"label": "min", "type": "float","callback": lambda x:x}
        ])


class TestDev(DeviceGUI):
    def __init__(self, data):
        self.name = data
        self.channels = []
        self.options = DevOptionGUIGroup([
            {"label": "num chans", "type": "float", "callback": self.setChans}
        ])

    def setChans(self, numChans):
        self.channels = []
        for i in range(numChans):
            self.channels.append(TestChannel("channel %i" % i))

