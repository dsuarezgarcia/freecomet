# -*- encoding: utf-8 -*-

'''
    The sample module.
'''

# General imports
import itertools



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	Sample                                                                    #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class Sample(object):

    '''
        The Sample class.
    '''
    
    # The Sample ID generator
    new_id = itertools.count()

    DEFAULT_ZOOM_MODEL = [.1, .25, .33, .5, .67, .75, 1., 1.5, 
                          2., 2.5, 3., 4., 5., 6., 7., 8.]
    DEFAULT_ZOOM_INDEX = 6

    ''' Initialization method. '''
    def __init__(self, sample_name, image, comet_list=[]):

        self.__id = next(Sample.new_id)                        # The id (int)
        self.__name = sample_name                              # The name (str)
        self.__image = image                                   # The image (ndarray)
        self.__comet_list = comet_list.copy()                  # The comet_list (Comet[])
        self.__analyzed = False                                # The analyzed (bool)
        self.__zoom_model = Sample.DEFAULT_ZOOM_MODEL.copy()   # The zoom_model (float[])
        self.__zoom_index = Sample.DEFAULT_ZOOM_INDEX          # The zoom_index (int)
        self.__tail_contour_dict = {}                          # The tail_contour_dict (CanvasContour{})
        self.__head_contour_dict = {}                          # The head_contour_dict (CanvasContour{})
        self.__comet_being_edited_tail_contour_dict = {}       # The comet_being_edited_tail_contour_dict (CanvasContour{})
        self.__comet_being_edited_head_contour_dict = {}       # The comet_being_edited_head_contour_dict (CanvasContour{})
        self.__comet_being_edited_id = None                    # The comet_being_edited_id (int)
        self.__selected_comet_id = None                        # The selected_comet_id (int)
        


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                  Methods                                    #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
    
    ''' Adds given Comet at given position. '''
    def add_comet(self, comet, pos=None):

        # Append to the list
        if pos is None:
            self.__comet_list.append(comet)
        # Insert on given position
        else:
            self.__comet_list.insert(pos, comet)
        # Update analyzed (number of segmented comets should appear on the View)
        self.__analyzed = True
   
    ''' Deletes comet with given ID. '''
    def delete_comet(self, comet_id):

        pos = 0
        while pos < len(self.__comet_list):

            if self.__comet_list[pos].get_id() == comet_id:
                comet_copy = self.__comet_list[pos]
                del self.__comet_list[pos]

                # If after deleting, Sample has no segmented comets, Sample is
                # interpreted as not segmented and therefore the number of 
                # segmented comets should NOT appear on the View.
                if len(self.__comet_list) == 0:
                    self.__analyzed = False

                return (comet_copy, pos)

            pos += 1

    ''' Returns comet with given ID. '''
    def get_comet(self, comet_id):

        for comet in self.__comet_list:
            if comet.get_id() == comet_id:
                return comet


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              Getters & Setters                              #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_id(self):
        return self.__id

    def set_id(self, id):
        self.__id = id

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def get_image(self):
        return self.__image

    def set_image(self, image):
        self.__image = image

    def get_comet_list(self):
        return self.__comet_list

    def set_comet_list(self, comet_list):
        self.__comet_list = comet_list

    def get_analyzed(self):
        return self.__analyzed

    def set_analyzed(self, analyzed):
        self.__analyzed = analyzed

    def get_zoom_model(self):
        return self.__zoom_model

    def set_zoom_model(self, zoom_model):
        self.__zoom_model = zoom_model

    def get_zoom_index(self):
        return self.__zoom_index

    def set_zoom_index(self, zoom_index):
        self.__zoom_index = zoom_index
        
    def get_tail_contour_dict(self):
        return self.__tail_contour_dict
       
    def set_tail_contour_dict(self, tail_contour_dict):
        self.__tail_contour_dict = tail_contour_dict
        
    def get_head_contour_dict(self):
        return self.__head_contour_dict
       
    def set_head_contour_dict(self, head_contour_dict):
        self.__head_contour_dict = head_contour_dict
    
    def get_comet_being_edited_id(self):
        return self.__comet_being_edited_id
        
    def set_comet_being_edited_id(self, comet_being_edited_id):
        self.__comet_being_edited_id = comet_being_edited_id
        
    def get_selected_comet_id(self):
        return self.__selected_comet_id
        
    def set_selected_comet_id(self, selected_comet_id):
        self.__selected_comet_id = selected_comet_id
        
    def get_comet_being_edited_tail_contour_dict(self):
        return self.__comet_being_edited_tail_contour_dict
       
    def set_comet_being_edited_tail_contour_dict(self, comet_being_edited_tail_contour_dict):
        self.__comet_being_edited_tail_contour_dict = comet_being_edited_tail_contour_dict
        
    def get_comet_being_edited_head_contour_dict(self):
        return self.__comet_being_edited_head_contour_dict
       
    def set_comet_being_edited_head_contour_dict(self, comet_being_edited_head_contour_dict):
        self.__comet_being_edited_head_contour_dict = comet_being_edited_head_contour_dict
    
