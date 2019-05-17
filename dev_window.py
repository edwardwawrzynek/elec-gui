import re, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from device_gui import DeviceGUI, ChannelGUI, DevOptionGUIGroup

#The window showing the device subsytems (device selection, options, channel selection, options)
class DeviceWindow:
    def __init__(self):
        self.devs = []
        self.dev_stack = Gtk.Stack()
        self.dev_switcher = Gtk.StackSwitcher()
        self.dev_switcher.set_stack(self.dev_stack)

        self.window = Gtk.ScrolledWindow()

        self.component = Gtk.VBox()
        self.component.pack_start(self.dev_switcher, False, False, 0)
        self.component.pack_start(self.dev_stack, True, True, 0)
        self.window.add_with_viewport(self.component)

    def addDev(self, dev):
        self.devs.append(dev)
        self.dev_stack.add_titled(dev.getComponent(), dev.name, dev.name)
        self.dev_stack.show_all()

    def getComponent(self):
        return self.window