import re, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from dev_gui_option import DevOptionGUIGroup, DevOptionGUI
from devices import devices

from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.figure import Figure
import numpy as np

#Channel Selection (callback when channel changes)
def ChannelChooser(callback):
    box = Gtk.VBox()
    dev_list = Gtk.ComboBoxText()
    chan_list = Gtk.ComboBoxText()
    for dev in devices:
        dev_list.append_text(dev.name)
    
    #when a device is chosen, we need to set the channel options
    def dev_selected(_):
        chan_list.remove_all()
        dev = [d for d in devices if d.name == dev_list.get_active_text()]
        if not dev:
            return
        dev = dev[0]
        for chan in dev.channels:
            chan_list.append_text(chan.name)
        
    #when a channel is selected, we need to trigger callback
    def chan_selected(_):
        dev = [d for d in devices if d.name == dev_list.get_active_text()]
        if not dev:
            return
        dev = dev[0]
        chan = [c for c in dev.channels if c.name == chan_list.get_active_text()]
        if not chan:
            return
        chan = chan[0]
        callback(chan)

    dev_list.connect("changed", dev_selected)
    chan_list.connect("changed", chan_selected)
    
    dev_list_labeled = Gtk.HBox()
    dev_list_labeled.pack_start(Gtk.Label("Device"), True, False, 0)
    dev_list_labeled.pack_start(dev_list, False, False, 0)

    chan_list_labeled = Gtk.HBox()
    chan_list_labeled.pack_start(Gtk.Label("Channel"), True, False, 0)
    chan_list_labeled.pack_start(chan_list, False, False, 0)

    box.pack_start(dev_list_labeled, False, False, 0)
    box.pack_start(chan_list_labeled, False, False, 0)
    
    return box


#Generic data output class (graph, raw values, data analyzer, etc)
class Output:
    def __init__(self, data):
        #custom options for output type
        self.options = DevOptionGUIGroup([])
        #channels to draw data from
        self.sources = []
        #create component
        self.generateComponent()
    
    #add option
    def addOption(self, option):
        self.options.addOption(option)
    
    #creates the component specific to this output type
    #called on every addition of input source (it should use a local variable as the component and adjust it)
    #override this
    def generateOutput(self):
        #TODO: call different method for changes?
        return Gtk.Label("Sample Output. Sources: " + str(len(self.sources)))

    def newSourceWindow(self, _):
        popup = Gtk.Dialog()
        popup.add_buttons("Add", 1, "Cancel", 2)
        chan = None
        def set_chan(new_chan):
            nonlocal chan
            chan = new_chan

        popup.vbox.pack_start(ChannelChooser(set_chan), False, False, 0)
        popup.show_all()

        if popup.run() != 1 or chan == None:
            popup.destroy()
            return
        
        popup.destroy()
        #actually add the channel as source
        self.addSource(chan)

    def generateComponent(self):
        #TODO: vbox with graph/whatever at top, then add source button, then type specific options
        self.output_box = Gtk.VBox()
        #TODO: add overridden component
        self.output_box.pack_start(self.generateOutput(), False, False, 0)

        #Add option to add new source
        new_source_button = Gtk.Button("New Data Source")
        new_source_button.connect("clicked", self.newSourceWindow)
        self.output_box.pack_start(new_source_button, False, False, 0)
        self.output_box.pack_start(self.options.getComponent(), False, False, 0)
    
    def getComponent(self):
        return self.output_box
    
    #check if a channel is okay to add (return string on failure)
    #override and call super
    def checkSource(self, source):
        if source in self.sources:
            return "This data source is already in use by this output"
        return None
    
    def addSource(self, source):
        check = self.checkSource(source)
        if check != None:
            errorWin = Gtk.Dialog()

            errorWin.add_buttons("Ok", 1)
            errorWin.vbox.pack_start(Gtk.Label("Can't add source: %s" % check), False, False, 0)

            errorWin.show_all()
            errorWin.run()
            errorWin.destroy()
            return

        self.sources.append(source)
        #regenerate output component
        self.output_box.remove(self.output_box.get_children()[0])
        new_out = self.generateOutput()
        self.output_box.pack_start(new_out, False, False, 0)
        self.output_box.reorder_child(new_out, 0)
        self.output_box.show_all()
    
    #called on input trigger (probably redraw needed) -- override
    #TODO: get input directly from channels (no need to do duplicate load on channels in multiple outputs)
    def inputAvailable(self):
        pass

#A display for data output
class Graph(Output):
    def __init__(self, data):
        super().__init__(data)

        self.addOption(DevOptionGUI("Test Param", "string", lambda x:x))
    
    def generateOutput(self):
        f = Figure(figsize=(5, 4), dpi=100)
        a = f.add_subplot(111)
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2*np.pi*t)
        a.plot(t, s)
        canvas = FigureCanvas(f)
        canvas.set_size_request(800, 600)
        return canvas