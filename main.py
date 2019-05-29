from device_gui import *
from dev_window import *
from test_dev import *
from graph import *
from devices import *

def main():
    app = AppWindow(
        devices_list,
        [Graph(None),
         Graph(None)]
    )


    win = Gtk.Window()
    win.connect("delete-event", Gtk.main_quit)
    win.set_default_size(400, 300)
    win.set_title("Electronics GUI")

    win.add(app.getComponent())
    win.show_all()
    Gtk.main()

main()