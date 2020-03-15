# -*- encoding: utf-8 -*-

'''
    The zoom_tool module.
'''


# PyGObject imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	ZoomTool                                                                  #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class ZoomTool(object):

    '''
        The ZoomTool class.
    '''

    NO_ICON = None
    CLEAR_ICON = "edit-clear-symbolic"

    UNLIMITED = 0
    MAX_LENGTH = 3
    #PRIMARY_POSITION = Gtk.EntryIconPosition.PRIMARY
    SECONDARY_POSITION = Gtk.EntryIconPosition.SECONDARY
        

    ''' Initialization method. '''
    def __init__(self, view, gtk_builder):

        self.__view = view

        # # Gtk Components

        # The ComboBox
        self.__combobox = Gtk.ComboBox.new_with_model_and_entry(
                                           Gtk.ListStore(str, float))
        self.__combobox.set_entry_text_column(0)
        #self.__combobox.set_active(ZoomTool.DEFAULT_ZOOM_INDEX)
        self.__entry = self.__combobox.get_child()      
        gtk_builder.get_object(
            "toolbar-combobox-container").add(self.__combobox)

        # The Zoom In and Zoom Out buttons
        self.__zoom_in_button = gtk_builder.get_object("toolbar-zoom-in")
        self.__zoom_out_button = gtk_builder.get_object("toolbar-zoom-out")

        self.__initialize()

    ''' Attributes initialization. '''
    def __initialize(self):
       
        # # The scaled images cache
        self.__cache = {}
        self.__entry.set_text("")
        self.__combobox.get_model().clear()
        self.switch_off()

    ''' Restart behaviour. '''
    def restart(self):
        self.__initialize()
        

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                Methods                                      #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Switch off. '''
    def switch_off(self):
        self.__combobox.set_sensitive(False)
        self.__zoom_in_button.set_sensitive(False)
        self.__zoom_out_button.set_sensitive(False)

    ''' Switch on. '''
    def switch_on(self):
        self.__combobox.set_sensitive(True)  
        self.__update_buttons_sensitivity()

    ''' Update method.'''
    def update(self, sample_id):

        # Set zoom model
        sample_zoom_model = self.__view.get_controller().get_sample_zoom_model(sample_id)
        self.__combobox.set_model(self.__build_model(sample_zoom_model)) 
        # Set zoom index      
        self.__combobox.set_active(
            self.__view.get_controller().get_sample_zoom_index(sample_id))
        # Set icon 
        self.set_entry_icon(ZoomTool.NO_ICON)

    ''' Returns the active scale ratio. '''
    def get_active_scale_ratio(self):
        return self.__combobox.get_model()[self.__combobox.get_active()][1]        

    ''' Adds a scaled pixbuf to the cache which belongs to a sample determined
        by its ID. 
    '''
    def __add_cache(self, sample_id, zoom_level, scaled_pixbuf):

        if not sample_id in self.__cache:
            self.__cache[sample_id] = {zoom_level:scaled_pixbuf}
        else:
            self.__cache[sample_id][zoom_level] = scaled_pixbuf

    ''' Set Entry max length. '''
    def set_entry_max_length(self, length):
        self.__entry.set_max_length(length)

    ''' Set Entry icon. '''
    def set_entry_icon(self, icon_name):
        self.__entry.set_icon_from_icon_name(
            ZoomTool.SECONDARY_POSITION, icon_name)

    ''' Set active index. '''
    def set_active(self, index):
        self.__combobox.set_active(index)

    ''' Get active index. '''
    def get_active(self):
        return self.__combobox.get_active()

    ''' Get model. '''
    def get_model(self):
        return self.__combobox.get_model()

    ''' Set model. '''
    def set_model(self, model):
        self.__combobox.set_model(model)

    ''' Apply zoom to given image. '''
    def apply_zoom(self, sample_id, pixbuf):

        # Update buttons sensitivity
        self.__update_buttons_sensitivity()

        # Get zoom value 
        zoom_value = self.__combobox.get_model()[self.__combobox.get_active()][1]
        # See if stored in cache
        if sample_id in self.__cache:
            if zoom_value in self.__cache[sample_id]:
                return self.__cache[sample_id][zoom_value]
        
        # Otherwise, scale and save to cache
        scaled_pixbuf = pixbuf.scale_simple(pixbuf.get_width() * zoom_value, 
                                            pixbuf.get_height() * zoom_value, 2)
        # Add image to cache
        self.__add_cache(sample_id, zoom_value, scaled_pixbuf)

        return scaled_pixbuf

    ''' Validate combobox entry input. '''
    def validate_entry_text(self):

        new_text = ""
        for char in self.__entry.get_text():
            if char.isdigit():
                new_text += char

        return new_text

    ''' Zoom Out. '''
    def zoom_out(self):

        self.__zoom_in_button.set_sensitive(True)
        self.__combobox.set_active(self.__combobox.get_active()-1)
        if self.__combobox.get_active() == 0:
            self.__zoom_out_button.set_sensitive(False)

    ''' Zoom In. '''
    def zoom_in(self):

        self.__zoom_out_button.set_sensitive(True)
        self.__combobox.set_active(self.__combobox.get_active()+1)
        if self.__combobox.get_active() == len(self.__combobox.get_model())-1:
            self.__zoom_in_button.set_sensitive(False)
           
    ''' Adds given zoom_value if new. '''           
    def add_new_zoom_value(self, zoom_value, index):

        if self.get_model()[index][1] != zoom_value:
        
            zoom_text = self.__zoom_value_to_string(zoom_value)
            self.get_model().insert(index, (zoom_text, zoom_value))
            self.set_active(index)


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              Private methods                                #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Builds a Gtk.ListStore with given zoom model. '''
    def __build_model(self, zoom_model):

        list_store = Gtk.ListStore(str, float)
        for zoom_value in zoom_model:
            list_store.append((self.__zoom_value_to_string(zoom_value),
                               zoom_value)
                             )
        
        return list_store

    ''' Parse given zoom value to its string representation. '''
    def __zoom_value_to_string(self, zoom_value):
        return (str(int(zoom_value * 100)) + "%")

    ''' Update zoom buttons sensitivity. '''
    def __update_buttons_sensitivity(self):
    
        index = self.__combobox.get_active()
        # Zoom out button is sensitive if a lower combobox zoom level is available 
        value = (index > 0) 
        self.__zoom_out_button.set_sensitive(value)
        # Zoom in button is sensitive if a higher combobox zoom level is available 
        value = (index < len(self.__combobox.get_model())-1)  
        self.__zoom_in_button.set_sensitive(value)


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

    def get_combobox(self):
        return self.__combobox

    def set_combobox(self, combobox):
        self.__combobox = combobox

    def get_zoom_out_button(self):
        return self.__zoom_out_button

    def set_zoom_out_button(self, zoom_out_button):
        self.__zoom_out_button = zoom_out_button

    def get_zoom_in_button(self):
        return self.__zoom_in_button

    def set_zoom_in_button(self, zoom_in_button):
        self.__zoom_in_button = zoom_in_button

    def get_entry(self):
        return self.__entry

    def set_entry(self, entry):
        self.__entry = entry

    def get_cache(self):
        return self.__cache

    def set_cache(self, cache):
        self.__cache = cache
