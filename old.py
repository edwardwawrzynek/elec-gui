import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.backends.backend_gtk3 import (
    NavigationToolbar2GTK3 as NavigationToolbar)
from matplotlib.figure import Figure
import numpy as np

win = Gtk.Window()
win.connect("delete-event", Gtk.main_quit)
win.set_default_size(400, 300)
win.set_title("Embedding in GTK")

f = Figure(figsize=(5, 4), dpi=100)
a = f.add_subplot(111)
t = np.arange(0.0, 3.0, 0.01)
s = np.sin(2*np.pi*t) * np.tan(10*t)
a.plot(t, s)

vbox = Gtk.VBox()
win.add(vbox)

sw = Gtk.ScrolledWindow()
vbox.add(sw)
# A scrolled window border goes outside the scrollbars and viewport
sw.set_border_width(0)

canvas = FigureCanvas(f)  # a Gtk.DrawingArea
canvas.set_size_request(100, 200)
sw.add_with_viewport(canvas)

toolbar = NavigationToolbar(canvas, win)
vbox.pack_start(toolbar, False, False, 0)

win.show_all()
Gtk.main()