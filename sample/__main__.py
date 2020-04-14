# -*- encoding: utf-8 -*-

'''
    The Main module.
'''
 
# PyObject imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Custom imports
from model.model import Model
from view.view import View
from controller.controller import Controller
 


def main():  # type: () -> None

    settings = Gtk.Settings.get_default()
    settings.set_property("gtk-theme-name", "Adwaita")
    
    Controller(Model(), View())

    # Start the GTK+ processing loop
    Gtk.main()


if __name__ == "__main__":
    main()
    

