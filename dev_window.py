import re, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from device_gui import DeviceGUI, ChannelGUI, DevOptionGUIGroup
from devices import devices

#The window showing the device subsytems (device selection, options, channel selection, options)
class DeviceWindow:
    def __init__(self):
        self.devs = devices
        self.dev_stack = Gtk.Stack()
        self.dev_switcher = Gtk.StackSwitcher()
        self.dev_switcher.set_stack(self.dev_stack)

        self.window = Gtk.ScrolledWindow()
        self.window.set_propagate_natural_width(True)
        self.component = Gtk.VBox()
        #self.component.pack_start(self.dev_switcher, False, False, 0)
        self.component.pack_start(self.dev_stack, True, True, 0)
        self.window.add_with_viewport(self.component)

        #combined channel and dev switcher
        self.switch = Gtk.VBox()
        self.switch.pack_start(self.dev_switcher, False, False, 0)
        #channel switcher is blank now, will be set properly once dev is selected by user
        self.chan_switch = Gtk.StackSwitcher()
        self.switch.pack_start(self.chan_switch, False, False, 0)

    def addDev(self, dev):
        self.devs.addDev(dev)
        comp = dev.getComponent()
        self.dev_stack.add_titled(comp, str(len(self.devs.getDevs())-1), dev.name)

        def setChanSwitch(_):
            index = int(self.dev_stack.get_visible_child_name())
            self.switch.remove(self.switch.get_children()[-1])
            self.switch.pack_start(self.devs.getDevs()[index].getSwitchComponent(), False, False, 0)
            self.switch.show_all()

        comp.connect("map", setChanSwitch)
        self.dev_stack.show_all()

    def getComponent(self):
        return self.window
    
    def getSwitchComponent(self):
        return self.switch

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

#Triggers area
class TriggersWindow:
    def __init__(self, devs, outputs):
        self.devs = devs
        self.outputs = outputs

        #collection trigger (TODO: refactor out, allow arbitrary trigger conditions)
        self.triggerBox = Gtk.VBox()
        self.triggerBox.pack_start(Gtk.HSeparator(), False, False, 0)
        self.triggerBox.pack_start(Gtk.Label("Data Collection Triggers"), False, False, 0)
        trigger = Gtk.Button("Trigger Data Collection")
        trigger.connect("clicked", lambda _: self.fullCollection())
        self.triggerBox.pack_start(trigger, False, False, 0)
    
    def fullCollection(self):
        self.devs.triggerCollection()
        for out in self.outputs:
            out.inputAvailable()
    
    def getComponent(self):
        return self.triggerBox

#Full app window
class AppWindow:
    def __init__(self, devs, outputs):
        self.devW = DeviceWindow()
        self.outW = OutputWindow()
        self.trigW = TriggersWindow(self.devW.devs, self.outW.outputs)
        
        self.box = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.dev_vbox = Gtk.VBox()
        self.dev_vbox.pack_start(self.devW.getComponent(), True, True, 0)
        self.dev_vbox.pack_start(self.trigW.getComponent(), False, False, 0)
        self.box.add1(self.dev_vbox)
        self.box.add2(self.outW.getComponent())
        #dev and channel switcher
        self.vbox = Gtk.VBox()
        self.vbox.pack_start(self.devW.getSwitchComponent(), False, False, 0)
        self.vbox.pack_start(self.box, True, True, 0)

        for d in devs:
            self.devW.addDev(d)
        
        for o in outputs:
            self.outW.addOutput(o)
    
    def getComponent(self):
        return self.vbox