# -*- encoding: utf-8 -*-

'''
    The Main module.
'''
 
# General imports
import locale

# PyObject imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Custom imports
from model.model import Model
from view.view import View
from controller.controller import Controller
from i18n.strings import Strings 


def main():  # type: () -> None

    settings = Gtk.Settings.get_default()
    settings.set_property("gtk-theme-name", "Adwaita")

    # i18n
    strings = Strings()
    if locale.getlocale()[0] == 'es_ES':
        strings.translate_to_spanish()
    else:
        strings.translate_to_english()

    model = Model()
    view = View()
    Controller(model, view, strings)

    # Start the GTK+ processing loop
    Gtk.main()


if __name__ == "__main__":
    main()
    

