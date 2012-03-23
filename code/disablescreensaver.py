#!/usr/bin/env python

import dbus

import pygtk
pygtk.require('2.0')
import gtk

class App:
    
    def delete_event(self, widget, event, data=None):
        """If returns False, destroy signal emitted.  If True, window 
        not destroyed."""
        return False
    
    def destroy(self, widget, data=None):
        if self.cookie is not None:
            # This shouldn't be necessary, but hey...
            self.inhibit(None)
        gtk.main_quit()
    
    def __init__(self):
        """Create a new window."""
        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(5)
        self.window.set_title("Screensaver Control")
        self.window.set_resizable(False)
        
        self.button = gtk.ToggleButton("Enabled")
        self.button_im = gtk.Image()
        self.button_im.set_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_BUTTON)
        self.button.set_image(self.button_im)
        self.button.connect("toggled", self.inhibit, None)
        
        exit_button = gtk.Button("Exit")
        exit_button_im = gtk.Image()
        exit_button_im.set_from_stock(gtk.STOCK_QUIT, gtk.ICON_SIZE_BUTTON)
        exit_button.set_image(exit_button_im)
        exit_button.connect("clicked", self.destroy, None)
        #exit_button.set_use_stock(True)
        
        label = gtk.Label("Screensaver is ")
        box = gtk.HBox()
        box.pack_start(label, False)
        box.pack_start(self.button, False)
        box.pack_end(exit_button, False)
        
        self.window.add(box)
        # These shouldn't be necessary, and didn't use to be...
        self.button_im.show()
        exit_button_im.show()
        
        self.window.show_all()
        w,h = box.size_request()
        box.set_size_request(w+10, h) # Creates room before exit_button

        bus = dbus.SessionBus()
        self.ss = bus.get_object('org.gnome.ScreenSaver','/org/gnome/ScreenSaver')
        self.cookie = None
    
    def main(self):
        gtk.main()
    
    def inhibit(self, widget, data=None):
        if self.cookie is None:
            self.cookie = self.ss.Inhibit("Disable Screensaver", "That's what I do.")
            self.button.set_label("Disabled")
            self.button_im.set_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_BUTTON)
        else:
            self.ss.UnInhibit(self.cookie)
            self.cookie = None
            self.button.set_label("Enabled")
            self.button_im.set_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_BUTTON)
        self.button_im.show() # Why is this necessary?

if __name__ == "__main__":
    app = App()
    app.main()
