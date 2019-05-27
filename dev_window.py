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
        self.window.set_propagate_natural_width(True)
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
    
#outputs pane
class OutputWindow:
    def __init__(self):
        self.outputs = []
        self.outputBox = Gtk.VBox()
        self.window = Gtk.ScrolledWindow()
        self.window.set_propagate_natural_width(True)
        self.window.add_with_viewport(self.outputBox)
    
    def addOutput(self, output):
        self.outputs.append(output)
        self.outputBox.pack_start(output.getComponent(), False, False, 6)
        self.outputBox.pack_start(Gtk.VSeparator(), False, False, 6)
        self.outputBox.show_all()
    
    def getComponent(self):
        return self.window

#Full app window
class AppWindow:
    def __init__(self, devs, outputs):
        self.devW = DeviceWindow()
        self.outW = OutputWindow()
        #self.box = Gtk.HBox()
        self.box = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        #self.box.pack_start(self.devW.getComponent(), False, False, 6)
        #self.box.pack_start(self.outW.getComponent(), True, True, 6)
        self.box.add1(self.devW.getComponent())
        self.box.add2(self.outW.getComponent())

        for d in devs:
            self.devW.addDev(d)
        
        for o in outputs:
            self.outW.addOutput(o)
    
    def getComponent(self):
        return self.box