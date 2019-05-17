import re, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

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

        self.vbox.pack_start(self.options.getComponent(), True, True, 0)
        self.vbox.pack_start(self.chan_switch, False, False, 0)
        self.vbox.pack_start(self.chan_stack, True, True, 0)

    def addChannel(self, chan):
        self.channels.append(chan)
        self.chan_stack.add_titled(chan.options.getComponent(), chan.name, chan.name)
        self.chan_stack.show_all()

    def getComponent(self):
        return self.vbox

class ChannelGUI:
    #data is arbitrary data passed to channel by dev
    def __init__(self, data):
        #name of channel
        self.name = ""
        #options (channel specific)
        self.options = DevOptionGUIGroup([])

    def setName(self, name):
        self.name = name

    def addOption(self, option):
        self.options.addOption(option)
