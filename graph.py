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

def displayError(errMsg):
    dialog = Gtk.Dialog()
    dialog.add_buttons("Ok", 1)
    dialog.vbox.pack_start(Gtk.Label("Error:\n%s" % errMsg), False, False, 0)
    dialog.show_all()
    dialog.run()
    dialog.destroy()

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
        self.titleBox = Gtk.HBox()
        self.titleBox.pack_start(Gtk.Label(self.name), True, True, 0)
        
        triggerButton = Gtk.Button("Trigger Collection")
        triggerButton.connect("clicked", lambda _: self.triggerCollectionSources())
        self.titleBox.pack_start(triggerButton, False, False, 0)
        

        removeButton = Gtk.Button("Remove Output")
        removeButton.connect("clicked", lambda _, data: self.remove_callback(data), self)
        self.titleBox.pack_start(removeButton, False, False, 0)

        self.output_box.pack_start(self.titleBox, False, False, 0)
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
        self.regenerateOutput()
    
    def regenerateOutput(self):
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

#Represents an axis on the graph
class PlotAxis:
    def __init__(self, name, unit, min_val, max_val):
        self.name = name
        self.unit = unit
        self.min_val = min_val
        self.max_val = max_val
        self.update_callback = lambda: None
    
    def setUpdateCallback(self, callback):
        self.update_callback = callback

    def setName(self, name):
        self.name = name
        self.update_callback()
    
    def setUnit(self, unit):
        try:
            self.unit = u.Unit(unit)
            self.update_callback()
        except:
            displayError("unit %s is invalid" % unit)
    
    def setMin(self, minv):
        self.min_val = minv
        self.update_callback()
    
    def setMax(self, maxv):
        self.max_val = maxv
        self.update_callback()

    #add an entry for axis input grid
    def addToGrid(self, grid, v_index, remove_callback):
        name_e = DevOptionGUI("", "string", self.setName, default=self.name, doLabel=False)
        grid.attach(name_e.getComponent(), 0, v_index, 1, 1)
        unit_e = DevOptionGUI("", "string", self.setUnit, default=str(self.unit), doLabel=False)
        grid.attach(unit_e.getComponent(), 1, v_index, 1, 1)
        mix_e = DevOptionGUI("", "float", self.setMin, default="", doLabel=False)
        max_e = DevOptionGUI("", "float", self.setMax, default="", doLabel=False)
        grid.attach(mix_e.getComponent(), 2, v_index, 1, 1)
        grid.attach(max_e.getComponent(), 3, v_index, 1, 1)
        remove_b = Gtk.Button("Remove Axis")
        remove_b.connect("clicked", lambda _:remove_callback())
        grid.attach(remove_b, 4, v_index, 1, 1)
    
    @staticmethod
    def makeAxesMenu(axes, remove_callback, add_callback):
        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(6)

        grid.attach(Gtk.Label("Axis Name"), 0, 0, 1, 1)
        grid.attach(Gtk.Label("Unit"), 1, 0, 1, 1)
        grid.attach(Gtk.Label("Min Value"), 2, 0, 1, 1)
        grid.attach(Gtk.Label("Max Value"), 3, 0, 1, 1)
        grid.attach(Gtk.Label("Remove"), 4, 0, 1, 1)

        v_index = 1
        for a in axes:
            def makeRemoveCallback(v_index):
                return lambda: remove_callback(v_index-1)

            a.addToGrid(grid, v_index, makeRemoveCallback(v_index))
            v_index += 1
        
        add_b = Gtk.Button("Add New Y Axis")
        add_b.connect("clicked", lambda _: add_callback())
        grid.attach(add_b, 0, v_index, 5, 1)
        
        return grid

class ComplexSelectionType:
    NONE = -1
    REAL = 0
    IMAGINARY = 1
    ANGLE_RAD = 2
    MAG = 3

#represents a source for a plot and options for it
class PlotSource:
    def __init__(self, channel, y_axes, update_callback):
        self.channel = channel
        self.color = Gdk.RGBA(np.random.random_sample(), np.random.random_sample(), np.random.random_sample())
        self.dimSelect = {}
        self.complexMode = ComplexSelectionType.NONE

        self.y_axis = None
        self.y_axes = y_axes
        self.update_callback = update_callback
    
    def setYAxes(self, y_axes):
        self.y_axes = y_axes
    
    def axisSelected(self, widget):
        index = widget.get_active()
        self.y_axis = self.y_axes[index]
        self.update_callback()
    
    def setColor(self, widget):
        self.color = widget.get_rgba()
        self.update_callback()

    def addToGrid(self, grid, v_index, remove_callback):
        grid.attach(Gtk.Label(self.channel.parent.name + ": " + self.channel.name), 0, v_index, 1, 1)

        y_axes_sel = Gtk.ComboBoxText()
        for axis in self.y_axes:
            y_axes_sel.append_text("%s [%s]" % (axis.name, str(axis.unit)))
        
        y_axes_sel.connect("changed", self.axisSelected)

        #check if our previous selection is in menu, and, if so, select it
        #else, choose axis 0
        if self.y_axis in self.y_axes:
            index = self.y_axes.index(self.y_axis)
            y_axes_sel.set_active(index)
        else:
            self.y_axis = self.y_axes[0]
            y_axes_sel.set_active(0)

        grid.attach(y_axes_sel, 1, v_index, 1, 1)

        color_b = Gtk.ColorButton()
        color_b.set_rgba(self.color)
        color_b.connect("color-set", self.setColor)
        grid.attach(color_b, 2, v_index, 1, 1)

        remove_b = Gtk.Button("Remove Source")
        remove_b.connect("clicked", lambda _:remove_callback())
        grid.attach(remove_b, 3, v_index, 1, 1)

        #now add attributes based on channel type
        h_index = 4
        if self.channel.isComplex():
            box = Gtk.HBox()
            box.pack_start(Gtk.Label("Complex Mode: "), False, False, 0)
            type_sel = Gtk.ComboBoxText()
            type_sel.append_text("Real Part")
            type_sel.append_text("Imaginary Part")
            type_sel.append_text("Angle")
            type_sel.append_text("Magnitude")

            if self.complexMode != -1:
                type_sel.set_active(self.complexMode)

            def setComplexType(widget):
                self.complexMode = widget.get_active()
                self.update_callback()

            type_sel.connect("changed", setComplexType)
            box.pack_start(type_sel, False, False, 0)
            grid.attach(box, h_index, v_index, 1, 1)
            h_index+=1
        for dim in self.channel.getAdditionalDims():
            if not dim in self.dimSelect:
                self.dimSelect[dim] = 0

            def makeSetDim(dim):
                def set(res):
                    self.dimSelect[dim] = res
                    self.update_callback()
                return set

            dim_input = DevOptionGUI("%s: " % dim, "int", makeSetDim(dim), doTypeLabel=False, default=self.dimSelect[dim])
            grid.attach(dim_input.getComponent(), h_index, v_index, 1, 1)
            h_index+=1
    


    def getXRData(self):
        if self.channel.getData() is None:
            return None, None, None, None
        #read data and add units
        xData = self.channel.getData()[self.channel.getXAxisDim()]
        yData = self.channel.getData().sel(self.dimSelect)

        yUnit = self.channel.getData().units['']
        xUnit = self.channel.getData().units[self.channel.getXAxisDim()]

        if self.complexMode != ComplexSelectionType.NONE:
            if self.complexMode == ComplexSelectionType.REAL:
                yData = yData.real
            elif self.complexMode == ComplexSelectionType.IMAGINARY:
                yData = yData.imag
            elif self.complexMode == ComplexSelectionType.ANGLE_RAD:
                yData = xr.ufuncs.angle(yData)
                yUnit = u.rad
            elif self.complexMode == ComplexSelectionType.MAG:
                yData = np.absolute(yData)

        return xData, yData, xUnit, yUnit
    
    def getData(self):
        xd, yd, xu, yu = self.getXRData()
        if xd is None:
            return None, None
        return xd.data*xu, yd.data*yu
            

    @staticmethod
    def makeSourceMenu(sources, remove_callback):
        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(6)

        grid.attach(Gtk.Label("Name"), 0, 0, 1, 1)
        grid.attach(Gtk.Label("Y-Axis"), 1, 0, 1, 1)
        grid.attach(Gtk.Label("Color"), 2, 0, 1, 1)
        grid.attach(Gtk.Label("Remove"), 3, 0, 1, 1)
        v_index = 1
        for src in sources:
            
            def makeRemoveCallback(v_index):
                return lambda: remove_callback(v_index-1)

            src.addToGrid(grid, v_index, makeRemoveCallback(v_index))
            v_index+=1
        
        return grid
        

def makePlot(x_axis, y_axes, axis_update_callback, is_polar):
    if len(y_axes) < 1:
        raise Exception("Plot needs at least one y-axis")
    if is_polar and len(y_axes) != 1:
        displayError("Polar plots can't have more than one y-axis")
        y_axes = [y_axes[0]]
    fig = Figure(figsize=(5, 4), dpi=100)
    subplot = None
    if is_polar:
        subplot = fig.add_subplot(1, 1, 1, projection='polar')
    else:
        subplot = fig.add_subplot(1, 1, 1)

    #we need to adjust the plot so that we have enough space for extra labels
    if len(y_axes) > 2:
        fig.subplots_adjust(right=0.75)
    #generate all axes
    subplots = [subplot]
    for axis in y_axes[1:]:
        subplots.append(subplot.twinx())
    
    #set labels, etc
    i = -1
    for axis, plot in zip(y_axes, subplots):
        axis.setUpdateCallback(axis_update_callback)
        if not is_polar:
            plot.set_ylabel("%s [%s]" % (axis.name, str(axis.unit)))
        else:
            label_position=plot.get_rlabel_position()
            plot.text(np.radians(label_position+10),plot.get_rmax()/2.0, "%s [%s]" % (axis.name, str(axis.unit)), rotation=label_position,ha='center',va='center')
        if axis.min_val is None and axis.max_val is None:
            plot.set_ylim(auto=True)
        else:
            plot.set_ylim(axis.min_val, axis.max_val)
        if i>=0:
            plot.spines['right'].set_position(('outward', i*50))
        i+=1
    
    subplot.set_xlabel("%s [%s]" % (x_axis.name, str(x_axis.unit)))
    if x_axis.min_val is None and x_axis.max_val is None:
        subplot.set_xlim(auto=True)
    else:
        subplot.set_xlim(x_axis.min_val, x_axis.max_val)
    subplot.grid(True)
    
    canvas = FigureCanvas(fig)
    canvas.set_size_request(600, 600)
    box = Gtk.VBox()
    toolbar = NavigationToolbar(canvas, box)

    box.pack_start(canvas, False, False, 0)
    box.pack_start(toolbar, False, False, 0)

    return box, canvas, subplots

class PlotType:
    CARTESIAN = 0
    POLAR = 1

class Plot(Output):
    def __init__(self, name, remove_callback):
        self.y_axes = [PlotAxis("y-axis", u.V, None, None)]
        self.x_axis = PlotAxis("x-axis", u.s, None, None)

        self.box = Gtk.VBox()
        self.plotSources = []
        self.plotType = PlotType.CARTESIAN

        super().__init__(name, remove_callback)

    def newAxis(self):
        axis = PlotAxis("axis name", u.V, None, None)
        self.y_axes.append(axis)

        self.regenerateAxisMenu()
        self.regenerateOutput()
        self.updateSourceYAxes()

    def removeAxis(self, index):
        self.y_axes.pop(index)

        self.regenerateAxisMenu()
        self.regenerateOutput()
        self.updateSourceYAxes()
    
    def removeSource(self, index):
        self.plotSources.pop(index)
        self.sources.pop(index)

        self.regenerateOutput()
        self.regenerateSourceMenu()
    
    def updateSourceYAxes(self):
        for src in self.plotSources:
            src.setYAxes(self.y_axes)
        
        self.regenerateSourceMenu()
    
    def generateOutput(self):
        i = len(self.box.get_children())

        self.graph_vbox, self.canvas, self.subplots = makePlot(self.x_axis, self.y_axes, lambda: [self.regenerateOutput(), self.regenerateSourceMenu()], self.plotType == PlotType.POLAR)
        self.canvas.mpl_connect("motion_notify_event", self.handleMouseover)
        self.box.pack_start(self.graph_vbox, False, False, 0)
        self.value_trace = Gtk.Label("(Hover over plot to see trace of values)", halign=Gtk.Align.START)
        self.box.pack_start(self.value_trace, False, False, 0)
        self.box.pack_start(Gtk.Label("Y-axes"), False, False, 6)
        self.box.pack_start(PlotAxis.makeAxesMenu(self.y_axes, self.removeAxis, self.newAxis), False, False, 0)
        self.box.pack_start(Gtk.Label("X-Axis"), False, False, 6)
        grid = Gtk.Grid()
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        self.x_axis.addToGrid(grid, 0, lambda _:None)
        self.x_axis.setUpdateCallback(self.regenerateOutput)
        self.box.pack_start(grid, False, False, 0)

        combo_box = Gtk.ComboBoxText()
        combo_box.append_text("Cartesian Plot")
        combo_box.append_text("Polar Plot")
        combo_box.set_active(0)
        combo_box.connect("changed", self.setType)
        self.titleBox.pack_start(combo_box, False, False, 0)
        self.titleBox.reorder_child(combo_box, 1)

        self.box.pack_start(PlotSource.makeSourceMenu(self.plotSources, self.removeSource), False, False, 0)
        return self.box
    
    def setType(self, widget):
        self.plotType = widget.get_active()
        self.regenerateOutput()

    def regenerateOutput(self):
        self.box.remove(self.box.get_children()[0])
        self.graph_vbox, self.canvas, self.subplots = makePlot(self.x_axis, self.y_axes, lambda: [self.regenerateOutput(), self.regenerateSourceMenu()], self.plotType == PlotType.POLAR)
        self.canvas.mpl_connect("motion_notify_event", self.handleMouseover)

        self.box.pack_start(self.graph_vbox, False, False, 0)
        self.box.reorder_child(self.graph_vbox, 0)
        self.graphInput()
        self.canvas.draw()
        self.box.show_all()
    
    def regenerateAxisMenu(self):
        self.box.remove(self.box.get_children()[3])
        menu = PlotAxis.makeAxesMenu(self.y_axes, self.removeAxis, self.newAxis)
        self.box.pack_start(menu, False, False, 0)
        self.box.reorder_child(menu, 3)
        self.graphInput()
        self.box.show_all()
    
    def regenerateSourceMenu(self):
        self.box.remove(self.box.get_children()[6])
        menu = PlotSource.makeSourceMenu(self.plotSources, self.removeSource)
        self.box.pack_start(menu, False, False, 0)
        self.box.reorder_child(menu, 6)
        self.graphInput()
        self.box.show_all()

    #hook when adding source
    def checkSource(self, source):
        self.plotSources.append(PlotSource(source, self.y_axes, self.graphInput))
        self.regenerateSourceMenu()

    def inputAvailable(self):
        self.graphInput()
    
    def graphInput(self):
        #keep track of number of sources using each y-axis
        source_axis_usage = []
        for _ in self.subplots:
            source_axis_usage.append([])
        for plt in self.subplots:
            plt.lines = []
        for src in self.plotSources:
            if src.y_axis is None:
                continue
            if src.channel.getData() is None:
                continue
            #find which subplot to plot on based on axis selection
            subplot = self.subplots[self.y_axes.index(src.y_axis)]
            
            #getData through plotSource (allows it to do needed conversions)
            xData, yData = src.getData()
            
            #do unit conversion
            try:
                xData = xData.to(self.x_axis.unit)
                yData = yData.to(src.y_axis.unit)
            except:
                continue

            i = self.y_axes.index(src.y_axis)
            source_axis_usage[i].append(src)

            subplot.plot(xData, yData, color=[src.color.red, src.color.green, src.color.blue])
        
        for plot, i in zip(self.subplots, range(len(self.subplots))):
            if len(source_axis_usage[i]) == 1:
                src = source_axis_usage[i][0]
                plot.yaxis.label.set_color([src.color.red, src.color.green, src.color.blue])
            else:
                plot.yaxis.label.set_color('k')
        
        self.canvas.draw()
        self.box.show_all()
    
    def handleMouseover(self, event):
        #if we have previously drawn a line, remove it
        try:
            self.subplots[0].lines.remove(self.mouseover_line)
        except:
            pass

        if event.inaxes is None:
            return
        x_pos = event.xdata
        self.mouseover_line = self.subplots[0].axvline(x=x_pos, lw=1, ls='dashed', color='k')
        text = ""
        for src in self.plotSources:
            xData, yData, xUnit, yUnit = src.getXRData()
            if xData is None:
                continue
            y_pos = yData.interp({src.channel.getXAxisDim(): x_pos}).data * yUnit
            try:
                y_pos = y_pos.to(src.y_axis.unit)
            except:
                continue
        
            text += src.channel.parent.name + ": " + src.channel.name + ": " + str(y_pos) + "\n"
        
        self.value_trace.set_text(text)

        self.canvas.draw()
        self.box.show_all()
'''
#A display for data output
class Plot(Output):
    def __init__(self, name, remove_callback):
        super().__init__(name, remove_callback)
        #array of {'color', 'dimSelect'}
        self.sourceOptions = []

        self.addOption(DevOptionGUI("x-axis unit", "string", lambda _:self.graphInput(), default="s"))
        self.addOption(DevOptionGUI("y-axis unit", "string", lambda _:self.graphInput(), default="V"))
        self.addOption(DevOptionGUI("second y-axis unit", "string", lambda _: self.graphInput(), default=""))

        self.addOption(DevOptionGUI("x-axis label", "string", lambda _:self.graphInput(), default=""))
        self.addOption(DevOptionGUI("y-axis label", "string", lambda _:self.graphInput(), default=""))
    
    
    def generateOutput(self):
        self.graph_vbox = Gtk.VBox()
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.subplot = self.fig.add_subplot(1, 1, 1)
        self.subplot2 = self.subplot.twinx()
        self.subplot2.set_visible(False)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(600, 600)
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
        h = 1
        for src in self.sources:
            grid.attach(Gtk.Label(src.parent.name + ": " + src.name), 0, h, 1, 1)

            #create a color selection button
            colorButton = Gtk.ColorButton()
            color = None
            #check if this is a new source, or if we can reuse existing data
            if len(self.sourceOptions) <= i-1:
                #random color
                color = Gdk.RGBA(np.random.random_sample(), np.random.random_sample(), np.random.random_sample())
                #check if we need to do additional dimension selection options
                dims = src.getAdditionalDims()
                addDims=[]
                for dim in dims:
                    addDims.append({'name': dim, 'value': 0})
                
                self.sourceOptions.append({'color': [color.red, color.green, color.blue], 'dimSelect': addDims})
            else:
                colorList = self.sourceOptions[i-1]['color']
                color = Gdk.RGBA(colorList[0], colorList[1], colorList[2])
            colorButton.set_rgba(color)

            colorButton.connect("color-set", self.setSourceColor, i-1)

            grid.attach(colorButton, 1, h, 1, 1)

            removeButton = Gtk.Button("Remove Source")
            removeButton.connect("clicked", self.removeSource, i-1)
            grid.attach(removeButton, 2, h, 1, 1)

            #create button for dimensions
            for dim in self.sourceOptions[i-1]["dimSelect"]:
                h+=1
                #generator needed to keep dim static for future callbacks
                def genSetDim(dim):
                    def setDim(val):
                        dim['value']=val
                        self.inputAvailable()
                    
                    return setDim

                entry = DevOptionGUI("%s: " % dim['name'], "int", genSetDim(dim), default=0, doTypeLabel=False)
                grid.attach(entry.getComponent(), 1, h, 1, 1)

            i+=1
            h+=1
        return grid
    
    def setSourceColor(self, widget, index):
        color = widget.get_rgba()
        self.sourceOptions[index]['color'] = [color.red, color.green, color.blue]
        self.inputAvailable()
    
    def removeSource(self, widget, index):
        self.sources.pop(index)
        self.sourceOptions.pop(index)
        self.regenerateOutput()

    def inputAvailable(self):
        self.graphInput()

    def graphInput(self):
        lines = []
        xUnitName = self.options.getStateByLabel("x-axis unit")
        yUnitName = self.options.getStateByLabel("y-axis unit")
        yUnit2Name = self.options.getStateByLabel("second y-axis unit")
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
        
        try:
            yUnit2 = u.Unit(yUnit2Name)
        except:
            self.displayError("%s is not a valid unit name" % yUnit2Name)
            return


        xLabel = self.options.getStateByLabel("x-axis label")
        yLabel = self.options.getStateByLabel("y-axis label")
        self.subplot.clear()
        self.subplot2.clear()
        self.subplot2.set_visible(False)
        self.subplot.set_xlabel("%s [%s]" % (xLabel, xUnitName))
        self.subplot.set_ylabel("%s [%s]" % (yLabel, yUnitName))
        self.subplot.grid(True)
        i=0

        #the sources that actually got graphed on each axis (if only one, we color the axis that color)
        subplot1i = []
        subplot2i = []
        for src in self.sources:
            finalYUnitName = yUnitName
            xData = None
            yData = None
            subplot = self.subplot
            try:
                ySels = {}
                for dim in self.sourceOptions[i]['dimSelect']:
                    ySels[dim['name']] = dim['value']
                
                if src.getData() is None:
                    i+=1
                    continue

                xData = src.getData()[src.getXAxisDim()].data * src.getData().units[src.getXAxisDim()]
                yData = src.getData().sel(ySels).data * src.getData().units['']
            except:
                #specified labels aren't present
                i+=1
                continue
            try:
                #convert units (they get stripped when matplotlib graphs them)
                xData = xData.to(xUnit)
                yData = yData.to(yUnit)
                subplot1i.append(i)
            except u.core.UnitConversionError:
                #try second y-axis
                try:
                    xData = xData.to(xUnit)
                    yData = yData.to(yUnit2)
                    subplot = self.subplot2
                    self.subplot2.set_ylabel("(%s)" % yUnit2Name)
                    self.subplot2.set_visible(True)
                    finalYUnitName = yUnit2Name
                    subplot2i.append(i)
                except u.core.UnitConversionError:
                    #no unit on graph that we can graph this data with
                    i+=1
                    continue
            lines += subplot.plot(xData, yData, color=self.sourceOptions[i]['color'], label=src.parent.name + ": " + src.name + " (" + finalYUnitName + ")")
            i+=1
        if len(subplot1i) == 1:
            self.subplot.tick_params(axis='y', labelcolor=self.sourceOptions[subplot1i[0]]['color'])
        else:
            self.subplot.tick_params(axis='y', labelcolor='k')
        if len(subplot2i) == 1:
            self.subplot2.tick_params(axis='y', labelcolor=self.sourceOptions[subplot2i[0]]['color'])
        else:
            self.subplot2.tick_params(axis='y', labelcolor='k')
        self.fig.legend(lines, [l.get_label() for l in lines])
        self.canvas.draw()
        self.output_box.show_all()
'''    