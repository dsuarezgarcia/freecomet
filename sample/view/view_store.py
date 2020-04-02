# -*- encoding: utf-8 -*-

'''
    The view_store module.
'''

# PyGObject imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Custom imports
from view.canvas import Canvas
from observer import Observable

 

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	ViewStore                                                                 #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class ViewStore(Observable):

    '''
        The ViewStore class. Keeps the sample temporary parameters for 
        the View components to use.
    '''

    ''' Initialization method. '''
    def __init__(self):

        self.__store = {}
        super().__init__(self.__store)

    ''' Restart. '''
    def restart(self):
        self.clear()


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                 Methods                                     #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Returns the CometView object with given ID. '''
    def get_comet_view(self, sample_id, comet_id):
    
        for comet_view in self.__store[sample_id].get_comet_view_list():
        
            if comet_view.get_id() == comet_id:
                return comet_view

    ''' 
        Sets the scaled contours for the comet with given ID that belongs
        to the sample with given ID.
    '''
    def set_comet_scaled_contours(self, sample_id, comet_id, tail_contour,
                                                                head_contour):

        for comet_view in self.__store[sample_id].get_comet_view_list():

            if comet_view.get_id() == comet_id:
                comet_view.set_scaled_tail_contour(tail_contour)
                comet_view.set_scaled_head_contour(head_contour)
                return

    '''
        Returns the comet number (position in list) of sample with given ID
        and given comet ID.
    '''
    def get_comet_number(self, sample_id, comet_id):
        
        comet_list = self.__store[sample_id].get_comet_view_list()

        pos = 0
        while pos < len(comet_list):
            if comet_list[pos].get_id() == comet_id:
                return (pos+1)
            pos += 1

    ''' 
        Returns the SampleParameters object associated with the given sample
        ID. 
    '''
    def get_sample_parameters(self, sample_id):
        return self.__store[sample_id]

    ''' 
        Adds the SampleParameters object associated with the given sample ID.
    '''
    def add(self, sample_id, sample_parameters):

        self.__store[sample_id] = sample_parameters
        # Notify observers
        self.notify()
        
    ''' 
        Removes the SampleParameters entry from the store associated with the 
        given sample ID.
    '''
    def remove(self, sample_id):

        del self.__store[sample_id]
        # Notify observers
        self.notify()

    ''' Clears the store '''
    def clear(self):

        self.__store.clear()
        # Notify observers
        self.notify()


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              Getters & Setters                              #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_store(self):
        return self.__store

    def set_store(self, store):
        self.__store = store



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	SampleParameters                                                          #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class SampleParameters(object):

    '''
        The SampleParameters class. Keeps the View enviroment parameters 
        for a specific sample.
    '''

    ''' Initialization method. '''
    def __init__(self, pixbuf, comet_view_list=[]):

        self.__original_pixbuf = pixbuf
        self.__displayed_pixbuf = pixbuf

        self.__scroll_x_position = Canvas.DEFAULT_SCROLLBAR_X_POSITION
        self.__scroll_y_position = Canvas.DEFAULT_SCROLLBAR_Y_POSITION

        self.__comet_view_list = comet_view_list
 


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                  Methods                                    #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
        
    ''' Adds a CometView object at given position. '''
    def add_comet(self, comet_view, pos=None):        

        if pos is None:
            self.get_comet_view_list().append(comet_view)
        else:
            self.get_comet_view_list().insert(pos, comet_view)

    ''' Deletes the CometView object at given position. '''
    def delete_comet(self, comet_id):

        i = 0
        while i < len(self.get_comet_view_list()):
            if self.get_comet_view_list()[i].get_id() == comet_id:
                del self.get_comet_view_list()[i]
                return True
            i += 1

        return False
        

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              Getters & Setters                              #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_original_pixbuf(self):
        return self.__original_pixbuf

    def set_original_pixbuf(self, original_pixbuf):
        self.__original_pixbuf = original_pixbuf

    def get_displayed_pixbuf(self):
        return self.__displayed_pixbuf

    def set_displayed_pixbuf(self, displayed_pixbuf):
        self.__displayed_pixbuf = displayed_pixbuf

    def get_scroll_x_position(self):
        return self.__scroll_x_position

    def set_scroll_x_position(self, scroll_x_position):
        self.__scroll_x_position = scroll_x_position

    def get_scroll_y_position(self):
        return self.__scroll_y_position

    def set_scroll_y_position(self, scroll_y_position):
        self.__scroll_y_position = scroll_y_position

    def get_comet_view_list(self):
        return self.__comet_view_list

    def set_comet_view_list(self, comet_view_list):
        self.__comet_view_list = comet_view_list

 
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	CometView                                                                 #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class CometView(object):

    '''
        The CometView class.
    '''
        
    ''' Initialization method. '''
    def __init__(self, comet_id, tail_contour, head_contour):

        self.__id = comet_id
        self.__scaled_tail_contour = tail_contour
        self.__scaled_head_contour = head_contour


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_id(self):
        return self.__id

    def get_scaled_tail_contour(self):
        return self.__scaled_tail_contour

    def set_scaled_tail_contour(self, scaled_tail_contour):
        self.__scaled_tail_contour = scaled_tail_contour

    def get_scaled_head_contour(self):
        return self.__scaled_head_contour

    def set_scaled_head_contour(self, scaled_head_contour):
        self.__scaled_head_contour = scaled_head_contour


