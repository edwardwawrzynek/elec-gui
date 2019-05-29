from test_dev import *

#manages all of the devices, as well as handling triggers
#note: devices should be added through DeviceWindow, which handles rendering them
class Devices:
    def __init__(self, devs):
        self.devs = []
        for dev in devs:
            self.addDev(dev)
    
    def addDev(self, dev):
        self.devs.append(dev)
    
    def getDevs(self):
        return self.devs
    
    def triggerCollection(self):
        for dev in self.devs:
            dev.triggerChannelsCollection()


devices = Devices([])
devices_list = [TestDev("Test Dev 1"), TestDev("Test Dev 2")]