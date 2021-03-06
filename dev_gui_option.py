import re, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#An object specifying an option for a device or channel to display a graphical interface for
class DevOptionGUI:
    #label is the name of the option
    #optionType is one of "string", "bool", "float", (TODO: channel, int, file, etc)
    #callback is the function to call when the value changes
    def __init__(self, label, optionType, callback, default=None, doTypeLabel=True, doLabel=True):
        self.label = label
        self.doLabel = doLabel
        if doTypeLabel:
            self.labelText = "%s (%s)" % (label, optionType)
        else:
            self.labelText = label
        self.optionType = optionType
        self.callback = callback
        self.default = default
        #generate widget and initial state based on type
        self.component, self.state = self.generateComponent()

    def generateComponent(self):
        box = Gtk.HBox()
        label = Gtk.Label(self.labelText, halign=Gtk.Align.START)
        if self.doLabel:
            box.pack_start(label, True, True, 0)
        self.comp = False
        state = None
        if self.default != None:
            state = self.default
        #choose type
        if self.optionType == "string":
            self.comp = Gtk.Entry()
            if state == None:
                state = ""
            self.comp.set_text(state)

            def string_entry_activate(widget, callback):
                self.state = widget.get_text()
                callback(self.state)

            self.comp.connect("activate", string_entry_activate, self.callback)
            self.comp.connect("focus-out-event", lambda w, _, c: string_entry_activate(w, c), self.callback)

        elif self.optionType == "bool":
            self.comp = Gtk.CheckButton()
            if state == None:
                state = False
            
            self.comp.set_active(state)

            def bool_entry_toggle(widget, callback):
                self.state = widget.get_active()
                callback(self.state)


            self.comp.connect("toggled",bool_entry_toggle, self.callback)

        elif self.optionType == "float":
            self.comp = Gtk.Entry()
            if state == None:
                state = 0.0
            self.comp.set_text(str(state))

            def float_entry_activate(widget, callback):
                text = widget.get_text()
                if text=="":
                    callback(None)
                    return
                #make sure entry is a float, clear if not
                match = re.match(r"-?(\d+(\.\d+)?)", text)
                if match != None and match.group(0) == text:
                    self.state = float(text)
                    callback(self.state)
                else:
                    widget.set_text(str(self.state))

            self.comp.connect("activate", float_entry_activate, self.callback)
            self.comp.connect("focus-out-event", lambda w, _, c: float_entry_activate(w, c), self.callback)

        elif self.optionType == "int":
            self.comp = Gtk.Entry()
            if state == None:
                state = 0
            self.comp.set_text(str(state))

            def int_entry_activate(widget, callback):
                text = widget.get_text()
                #make sure entry is int
                match = re.match(r"-?\d*", text)
                if match != None and match.group(0) == text:
                    self.state = int(text)
                    callback(self.state)
                else:
                    widget.set_text(str(self.state))
            
            self.comp.connect("activate", int_entry_activate, self.callback)
            self.comp.connect("focus-out-event", lambda w, _, c: int_entry_activate(w, c), self.callback)


        elif self.optionType == "button":
            self.comp = Gtk.Button(self.label)
            if state == None:
                state = False

            def button_entry_activate(widget, callback):
                self.state = True
                callback(state)
                self.state = False

            self.comp.connect("clicked", button_entry_activate, self.callback)

        else:
            raise Exception("DevOptionGUI: no such input type: %s" % self.optionType)

        box.pack_start(self.comp, False, False, 0)
        return box, state

    def getComponent(self):
        return self.component
    
    def getUnlabeledComponent(self):
        return self.comp

#Group of DevOptionGUI's (handle's initing, grouping components, and loading/saving)
class DevOptionGUIGroup:
    #options is an array of DevOptionGUI's
    def __init__(self, options):
        self.widgets = []
        self.generateComponent()

        for opt in options:
            self.addOption(opt)

    def generateComponent(self):
        self.box = Gtk.VBox()

    def addOption(self, option):
        self.widgets.append(option)
        self.box.pack_start(option.getComponent(), False, False, 2)
        self.box.show_all()

    def getComponent(self):
        return self.box

    #get state of option with given label
    def getStateByLabel(self, label):
        for w in self.widgets:
            if w.label == label:
                return w.state

        return None