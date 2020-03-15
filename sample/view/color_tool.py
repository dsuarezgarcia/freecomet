# -*- encoding: utf-8 -*-

'''
    The color_tool module.
'''

# PyGObject imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	ColorTool                                                                 #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class ColorTool(object):

    '''
        The ColorTool class.
    '''

    def __init__(self, gtk_builder, view):

        self.__view = view

        # Gtk Components
        self.__tail_color_button = gtk_builder.get_object(
            "drawing-area-toolbar-tail-color-button")
        self.__tail_color_button_image = gtk_builder.get_object(
            "drawing-area-toolbar-tail-color-button-image")
        self.__head_color_button = gtk_builder.get_object(
            "drawing-area-toolbar-head-color-button")
        self.__head_color_button_image = gtk_builder.get_object(
            "drawing-area-toolbar-head-color-button-image")

        self.initialize()

    ''' Attributes initialization. '''
    def initialize(self):

        # Atributtes
        self.__tail_color = Gdk.RGBA(1., 0., 0., 1.) # Red by default 
        self.__head_color = Gdk.RGBA(0., 1., 0., 1.) # Green by default


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                  Methods                                    #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Parses given rgba to hexadecimal. '''
    def __rgba_to_hexadecimal(self, rgba_color):
 
        red = int(rgba_color.red * 255) << 24
        green = int(rgba_color.green * 255) << 16
        blue = int(rgba_color.blue * 255) << 8
        alpha = int(rgba_color.alpha * 255)
        return red | green | blue | alpha        

    ''' Sets the color for the tail contours. '''
    def set_tail_color(self, gdk_rgba_color):

        self.__tail_color = gdk_rgba_color
        # Paint tail button image color
        self.__tail_image_pixbuf.fill(
            self.__rgba_to_hexadecimal(gdk_rgba_color))
        # Set to image
        self.__tail_color_button_image.set_from_pixbuf(
            self.__tail_image_pixbuf)

        if self.__view.get_controller() is not None:
            self.__view.get_controller().set_tail_color_use_case(self.__tail_color)
        self.__view.get_main_window().get_canvas().update()
      
    ''' Sets the color for the heads contours. '''
    def set_head_color(self, gdk_rgba_color):

        self.__head_color = gdk_rgba_color
        # Paint head button image color
        self.__head_image_pixbuf.fill(
            self.__rgba_to_hexadecimal(gdk_rgba_color))
        # Set to image
        self.__head_color_button_image.set_from_pixbuf(
            self.__head_image_pixbuf)

        if self.__view.get_controller() is not None:
            self.__view.get_controller().set_head_color_use_case(self.__head_color)
        self.__view.get_main_window().get_canvas().update()

    ''' Sets the tail button image pixbuf. '''
    def set_tail_button_image_pixbuf(self, tail_image_pixbuf):
        
        self.__tail_image_pixbuf = tail_image_pixbuf
        self.__tail_color_button_image.set_from_pixbuf(
            self.__tail_image_pixbuf)
        # Set to image
        self.__tail_image_pixbuf.fill(
            self.__rgba_to_hexadecimal(self.__tail_color))

        if self.__view.get_controller() is not None:
            self.__view.get_controller().set_tail_color_use_case(self.__tail_color)
        self.__view.get_main_window().get_canvas().update()

    ''' Sets the head button image pixbuf. '''
    def set_head_button_image_pixbuf(self, head_image_pixbuf):

        self.__head_image_pixbuf = head_image_pixbuf
        self.__head_color_button_image.set_from_pixbuf(
            self.__head_image_pixbuf)
        self.__head_image_pixbuf.fill(
            self.__rgba_to_hexadecimal(self.__head_color))

        if self.__view.get_controller() is not None:
            self.__view.get_controller().set_head_color_use_case(self.__head_color)
        self.__view.get_main_window().get_canvas().update()


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              Getters & Setters                              #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_tail_color(self):
        return self.__tail_color

    def set_tail_color(self, tail_color):
        self.__tail_color = tail_color

    def get_head_color(self):
        return self.__head_color

    def set_head_color(self, head_color):
        self.__head_color = head_color

    def get_tail_color_button(self):
        return self.__tail_color_button

    def set_tail_color_button(self, tail_color_button):
        self.__tail_color_button = tail_color_button

    def get_head_color_button(self):
        return self.__head_color_button

    def set_head_color_button(self, head_color_button):
        self.__head_color_button = head_color_button

    def get_tail_color_button_image(self):
        return self.__tail_color_button_image

    def set_tail_color_button_image(self, tail_color_button_image):
        self.__tail_color_button_image = tail_color_button_image

    def get_head_color_button_image(self):
        return self.__head_color_button_image

    def set_head_color_button_image(self, head_color_button_image):
        self.__head_color_button_image = head_color_button_image







