import re, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

from dev_gui_option import DevOptionGUIGroup, DevOptionGUI
from dev_window import devices

from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.backends.backend_gtk3 import (
    NavigationToolbar2GTK3 as NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from astropy import units as u

#Channel Selection (callback is called when channel changes)
def ChannelChooser(callback):
    box = Gtk.VBox()
    dev_list = Gtk.ComboBoxText()
    chan_list = Gtk.ComboBoxText()
    for dev in devices.getDevs():
        dev_list.append_text(dev.name)
    
    #when a device is chosen, we need to set the channel options
    def dev_selected(_):
        chan_list.remove_all()
        dev = [d for d in devices.getDevs() if d.name == dev_list.get_active_text()]
        if not dev:
            return
        dev = dev[0]
        for chan in dev.channels:
            chan_list.append_text(chan.name)
        
    #when a channel is selected, we need to trigger callback
    def chan_selected(_):
        dev = [d for d in devices.getDevs() if d.name == dev_list.get_active_text()]
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
    def __init__(self, name, remove_callback):
        #custom options for output type
        self.options = DevOptionGUIGroup([])
        #channels to draw data from
        self.sources = []
        #output name
        self.name = name
        self.remove_callback = remove_callback
        #create component
        self.generateComponent()
    
    #add option
    def addOption(self, option):
        self.options.addOption(option)
    
    #creates the component specific to this output type
    #called on every addition of input source
    #override this
    def generateOutput(self):
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
        #vbox with graph/whatever at top, then add source button, then type specific options
        self.output_box = Gtk.VBox()
        #add title and removal button
        titleBox = Gtk.HBox()
        titleBox.pack_start(Gtk.Label(self.name), True, True, 0)
        
        triggerButton = Gtk.Button("Trigger Collection")
        triggerButton.connect("clicked", lambda _: self.triggerCollectionSources())
        titleBox.pack_start(triggerButton, False, False, 0)
        

        removeButton = Gtk.Button("Remove Output")
        removeButton.connect("clicked", lambda _, data: self.remove_callback(data), self)
        titleBox.pack_start(removeButton, False, False, 0)

        self.output_box.pack_start(titleBox, False, False, 0)
        #add overridden component
        self.output_box.pack_start(self.generateOutput(), False, False, 0)

        #Add option to add new source
        new_source_button = Gtk.Button("Add Data Source")
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
        self.regenateOutput()
    
    def regenateOutput(self):
        #regenerate output component
        self.output_box.remove(self.output_box.get_children()[1])
        new_out = self.generateOutput()
        self.output_box.pack_start(new_out, False, False, 0)
        self.output_box.reorder_child(new_out, 1)
        self.output_box.show_all()
    
    #collect data on all input sources
    def triggerCollectionSources(self):
        for src in self.sources:
            src.triggerCollection()
        
        self.inputAvailable()

    #called on input trigger (probably redraw needed) -- override
    def inputAvailable(self):
        pass
    
    #create a dialog for errors
    def displayError(self, errMsg):
        dialog = Gtk.Dialog()
        dialog.add_buttons("Ok", 1)
        dialog.vbox.pack_start(Gtk.Label("Output '%s' Raised an Error:\n%s" % (self.name, errMsg)), False, False, 0)
        dialog.show_all()
        dialog.run()
        dialog.destroy()

#A display for data output
class Graph(Output):
    def __init__(self, name, remove_callback):
        super().__init__(name, remove_callback)
        self.sourceColors = []

        self.addOption(DevOptionGUI("x-axis label", "string", lambda _:self.graphInput(), default=""))
        self.addOption(DevOptionGUI("y-axis label", "string", lambda _:self.graphInput(), default=""))

        self.addOption(DevOptionGUI("x-axis unit", "string", lambda _:self.graphInput(), default="s"))
        self.addOption(DevOptionGUI("y-axis unit", "string", lambda _:self.graphInput(), default="V"))
    
    
    def generateOutput(self):
        self.graph_vbox = Gtk.VBox()
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.subplot = self.fig.add_subplot(1, 1, 1)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(600, 400)
        self.toolbar = NavigationToolbar(self.canvas, self.graph_vbox)
        self.graph_vbox.pack_start(self.canvas, True, True, 0)
        self.graph_vbox.pack_start(self.toolbar, False, False, 0)
        self.graph_vbox.pack_start(Gtk.Label("Data Sources:"), False, False, 6)
        self.graph_vbox.pack_start(self.generateSourcesComponent(), False, False, 0)

        self.inputAvailable()

        return self.graph_vbox
    
    #generate a list of all the channels currently in use, as well as options for each
    def generateSourcesComponent(self):
        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(6)
        grid.attach(Gtk.Label("Source Name"), 0, 0, 1, 1)
        grid.attach(Gtk.Label("Color"), 1, 0, 1, 1)
        
        i = 1
        for src in self.sources:
            grid.attach(Gtk.Label(src.parent.name + ": " + src.name), 0, i, 1, 1)

            colorButton = Gtk.ColorButton()
            color = None
            if len(self.sourceColors) <= i-1:
                color = Gdk.RGBA(np.random.random_sample(), np.random.random_sample(), np.random.random_sample())
                self.sourceColors.append([color.red, color.green, color.blue])
            else:
                colorList = self.sourceColors[i-1]
                color = Gdk.RGBA(colorList[0], colorList[1], colorList[2])
            colorButton.set_rgba(color)

            colorButton.connect("color-set", self.setSourceColor, i-1)

            grid.attach(colorButton, 1, i, 1, 1)

            removeButton = Gtk.Button("Remove Source")
            removeButton.connect("clicked", self.removeSource, int((i/2)-1))
            grid.attach(removeButton, 2, i, 1, 1)
            i+=1
        return grid
    
    def setSourceColor(self, widget, index):
        color = widget.get_rgba()
        self.sourceColors[index] = [color.red, color.green, color.blue]
        self.inputAvailable()
    
    def removeSource(self, widget, index):
        self.sources.pop(index)
        self.sourceColors.pop(index)
        self.regenateOutput()

    def inputAvailable(self):
        self.graphInput()

    def graphInput(self):
        xUnitName = self.options.getStateByLabel("x-axis unit")
        yUnitName = self.options.getStateByLabel("y-axis unit")
        if xUnitName == None:
            return

        #make sure units can be converted to an astropy unit
        xUnit, yUnit = None, None
        try:
            xUnit = u.Unit(xUnitName)
        except:
            self.displayError("%s is not a valid unit name" % xUnitName)
            return
        
        try:
            yUnit = u.Unit(yUnitName)
        except:
            self.displayError("%s is not a valid unit name" % yUnitName)
            return

        xLabel = self.options.getStateByLabel("x-axis label")
        yLabel = self.options.getStateByLabel("y-axis label")
        self.subplot.clear()
        self.subplot.set_xlabel("%s (%s)" % (xLabel, xUnitName))
        self.subplot.set_ylabel("%s (%s)" % (yLabel, yUnitName))
        self.subplot.grid(True)
        i=0
        for src in self.sources:
            xData = None
            yData = None
            try:
                xData = src.getData()[src.getXAxisDim()].data * src.getData().units[src.getXAxisDim()]
                yData = src.getData().data * src.getData().units['']
                #convert units (they get stripped when matplotlib graphs them)
                xData = xData.to(xUnit)
                yData = yData.to(yUnit)
            except:
                #the specified labels aren't present in the data
                #TODO: warning?
                i+=1
                continue
            self.subplot.plot(xData, yData, color=self.sourceColors[i])
            i+=1
        
        self.canvas.draw()
        self.output_box.show_all()

    