import re, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from dev_gui_option import DevOptionGUIGroup
#The interface to the gui for devices. Can be a standalone driver, or, more likely, a driver that will call a lower level-driver

class DeviceGUI:
    #data is arbitrary data (probably port info, etc) passed during construction
    def __init___(self, data):
        #dev name
        self.name = ""
        #channels (need to be added by subclass)
        self.channels = []
        #options (device wide)
        self.options = DevOptionGUIGroup([])

    #return a component with the dev options, and channel options
    def generateComponent(self):
        box = Gtk.HBox()
        box.pack_start()

class ChannelGUI:
    #data is arbitrary data passed to channel by dev
    def __init__(self, data):
        #name of channel
        self.name = ""
        #options (channel specific)
        self.options = DevOptionGUIGroup([])
