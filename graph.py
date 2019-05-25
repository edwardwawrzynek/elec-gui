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
    #called on every change in input sources (it should use a local variable as the component and adjust it)
    #override this
    def generateOutput(self):
        #TODO: call different method for changes?
        pass

    def generateComponent(self):
        #TODO: vbox with graph/whatever at top, other at bottom
        pass
    
    #add a channel to output (success (return None), or on failure return string describing error (some outputs can only take one channel, etc))
    def addSource(self, source):
        self.sources.append(source)
        return None
    
    #called on input trigger (probably redraw needed) -- override
    #TODO: get input directly from channels (no need to do duplicate load on channels in multiple outputs)
    def inputAvailable(self):
        pass

#A display for data output
class Graph: