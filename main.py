from device_gui import *
from dev_window import *
from test_dev import *

def main():
    dev = DeviceWindow()
    a = TestDev("hello")
    dev.addDev(TestDev("Test Dev 1"))
    dev.addDev(TestDev("Test Dev 2"))


    win = Gtk.Window()
    win.connect("delete-event", Gtk.main_quit)
    win.set_default_size(400, 300)
    win.set_title("Electronics GUI")

    win.add(dev.getComponent())
    win.show_all()
    Gtk.main()

main()