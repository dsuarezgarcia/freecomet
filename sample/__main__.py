# -*- encoding: utf-8 -*-

'''
    The __main__ module.
'''
 
# PyObject imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Custom imports
from sample.model.model import Model
from sample.view.view import View
from sample.controller.controller import Controller
 


def main():
    
    Controller(Model(), View())

    # Start the GTK+ processing loop
    Gtk.main()

