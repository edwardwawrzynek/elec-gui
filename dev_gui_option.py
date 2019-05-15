import re, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#An object specifying an option for a device or channel to display a graphical interface for
class DevOptionGUI:
    #label is the name of the option
    #optionType is one of "string", "bool", "float", (TODO: channel, int, file, etc)
    #callback is the function to call when the value changes
    def __init__(self, label, optionType, callback):
        self.label = label
        self.labelText = "%s (%s)" % (label, optionType)
        self.optionType = optionType
        self.callback = callback
        #generate widget and initial state based on type
        self.component, self.state = self.generateComponent()

    def generateComponent(self):
        box = Gtk.HBox()
        label = Gtk.Label(self.labelText, halign=Gtk.Align.START)
        box.pack_start(label, True, True, 6)
        comp = False
        state = None
        #choose type
        if self.optionType == "string":
            comp = Gtk.Entry()
            state = ""

            def string_entry_activate(widget, callback):
                self.state = widget.get_text()
                callback(self.state)

            comp.connect("activate", string_entry_activate, self.callback)

        elif self.optionType == "bool":
            comp = Gtk.CheckButton()
            state = False

            def bool_entry_toggle(widget, callback):
                self.state = widget.get_active()
                callback(self.state)

            comp.connect("toggled",bool_entry_toggle, self.callback)

        elif self.optionType == "float":
            comp = Gtk.Entry()
            state = 0.0

            def float_entry_activate(widget, callback):
                text = widget.get_text()
                #make sure entry is a float, clear if not
                match = re.match(r"(\d+(\.\d+)?)", text)
                if match != None and match.group(0) == text:
                    self.state = float(text)
                    callback(self.state)
                else:
                    widget.set_text("")

            comp.connect("activate", float_entry_activate, self.callback)

        else:
            raise Exception("DevOptionGUI: no such input type: %s" % self.optionType)

        box.pack_start(comp, False, False, 6)

        return box, state

    def getComponent(self):
        return self.component

#Group of DevOptionGUI's (handle's initing, grouping components, and loading/saving)
class DevOptionGUIGroup:
    #options is an array of dictionaries of the form {"label":string, "type":string, "callback":func,}
    def __init__(self, options):
        self.options = options
        self.widgets = self.fromDict(options)
        self.component = self.generateComponent()

    def fromDict(self, options):
        widgets = []
        for opt in self.options:
            widgets.append(DevOptionGUI(opt["label"], opt["type"], opt["callback"]))

        return widgets

    def generateComponent(self):
        box = Gtk.VBox()

        for wid in self.widgets:
            box.pack_start(wid.getComponent(), False, False, 6)

        return box

    def getComponent(self):
        return self.component

    #get state of option with given label
    def getStateByLabel(self, label):
        for w in self.widgets:
            if w.label == label:
                return w.state

        return None