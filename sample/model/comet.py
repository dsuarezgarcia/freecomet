# -*- encoding: utf-8 -*-

'''
    The comet module.
'''

# General imports
import itertools
import numpy

# Custom imports
import sample.model.utils as utils



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	Comet                                                                     #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class Comet(object):

    '''
        The Comet class.
    '''

    # The ID Generator
    new_id = itertools.count()                               

    ''' Initialization method. '''
    def __init__(self, sample, tail_contour, head_contour):
        
        self.__id = next(Comet.new_id)
        self.__sample = sample
        
        # Contours
        self.__tail_contour = tail_contour
        self.__head_contour = head_contour 
        
        # CometParameters
        self.__parameters = CometParameters()
        self.__updated = False


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                 Methods                                     #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Builds the comet's parameters. '''
    def build_parameters(self):

        # Reinitialize parameters values
        self.__parameters.initialize()

        grayscale_image = utils.to_gray_image(
            self.__sample.get_image().copy()).astype(numpy.float64)

        # Comet has tail -> comet_contour = tail_contour
        # Comet has no tail -> comet_contour = head_contour
        comet_contour = None
        if self.__tail_contour is not None: 
            comet_contour = self.__tail_contour.copy()
        else:
            comet_contour = self.__head_contour.copy()

        
        # [1] Build Comet overall parameters
        x, y, width, height = utils.create_enclosing_rectangle(
                                  comet_contour)
        # Comet Mask
        comet_mask = utils.create_contour_mask(comet_contour, 
                         grayscale_image, (x, y, width, height))
        # Comet ROI
        comet_roi = numpy.copy(grayscale_image[y:y+height, x:x+width])
        comet_roi[numpy.where(comet_mask == 0)] = 0

        # Comet Attributes
        comet_area = utils.get_contour_area(comet_contour)
        comet_length = width
        coordinates = numpy.where(comet_mask != 0)
        comet_dna_content = numpy.sum(comet_roi[coordinates])
        
        nonzero = numpy.count_nonzero(comet_mask)
        if nonzero == 0:
            comet_average_intensity = 0.
        else:
            comet_average_intensity = comet_dna_content / nonzero

        # [2] Build Head parameters

        if self.__tail_contour is None:

            # Head attributes
            head_area = comet_area
            head_length = comet_length
            head_dna_content = comet_dna_content
            head_average_intensity = comet_average_intensity
            head_dna_percentage = 1.

        else:

            head_contour = self.__head_contour.copy()
            # Head Mask
            head_mask = utils.create_contour_mask(head_contour, 
                            grayscale_image, (x, y, width, height))
            # Head ROI
            head_roi = numpy.copy(grayscale_image[y:y+height, x:x+width])
            head_roi[numpy.where(head_mask == 0)] = 0

            # Head attributes
            head_area = utils.get_contour_area(head_contour)
            _, _, head_length, _ = utils.create_enclosing_rectangle(
                                       head_contour)
            coordinates = numpy.where(head_mask != 0)
            head_dna_content = numpy.sum(head_roi[coordinates])
        
            nonzero = numpy.count_nonzero(head_mask)
            if nonzero == 0:
                head_average_intensity = 0.
            else:
                head_average_intensity = head_dna_content / nonzero
                                  
            if comet_dna_content == 0:
                head_dna_percentage = 0.
            else:
                head_dna_percentage = head_dna_content / comet_dna_content


        # [3] Build Tail parameters
        if self.__tail_contour is not None:

            # Tail Mask
            tail_mask = comet_mask - head_mask

            nonzero = numpy.count_nonzero(tail_mask)
            if nonzero > 0:
            
                # Tail ROI
                tail_roi = numpy.copy(grayscale_image[y:y+height, x:x+width])
                tail_roi[numpy.where(tail_mask == 0)] = 0
                
                # Tail Attributes            
                tail_area = comet_area - head_area
                tail_length = max(comet_length - head_length, 0)
                coordinates = numpy.where(tail_mask != 0)
                tail_dna_content = numpy.sum(tail_roi[coordinates])
                tail_average_intensity = tail_dna_content / nonzero
                tail_dna_percentage = 1. - head_dna_percentage
                tail_moment = tail_length * tail_dna_percentage

                try:
                    tail_centroid_x = utils.get_contour_centroid(tail_roi, True)[0]
                except Exception as err:
                    print(err)
                    print("Unable to get Tail contour centroid. Aborting.")
                    return
                
                try:
                    head_centroid_x = utils.get_contour_centroid(head_roi, True)[0]
                except:
                    print(err)
                    print("Unable to get Head contour centroid. Aborting.")
                    return
                
                olive_moment = tail_dna_percentage * numpy.absolute(
                                   tail_centroid_x - head_centroid_x)

        # Set parameters
        self.__parameters.set_comet_area(comet_area)
        self.__parameters.set_comet_length(comet_length)
        self.__parameters.set_comet_dna_content(comet_dna_content)   
        self.__parameters.set_comet_average_intensity(comet_average_intensity)    
        self.__parameters.set_head_area(head_area)    
        self.__parameters.set_head_length(head_length)
        self.__parameters.set_head_dna_content(head_dna_content)
        self.__parameters.set_head_average_intensity(head_average_intensity)
        self.__parameters.set_head_dna_percentage(head_dna_percentage)
        if self.__tail_contour is not None:
            self.__parameters.set_tail_area(tail_area)
            self.__parameters.set_tail_length(tail_length)
            self.__parameters.set_tail_dna_content(tail_dna_content)
            self.__parameters.set_tail_average_intensity(tail_average_intensity)    
            self.__parameters.set_tail_dna_percentage(tail_dna_percentage)
            self.__parameters.set_tail_moment(tail_moment)
            self.__parameters.set_olive_moment(olive_moment)
            
        # Comet parameters are updated
        self.__updated = True

    ''' Updates the comet contours. '''
    def update_contours(self, tail_contour, head_contour):

        self.__tail_contour = tail_contour
        self.__head_contour = head_contour
        self.__updated = False

    ''' Removes the comet tail. '''
    def remove_tail(self):

        tail_contour_copy = self.__tail_contour.copy()
        self.__tail_contour = None
        self.__updated = False
        return tail_contour_copy

    ''' Adds tail to the comet. '''
    def add_tail(self, tail_contour):

        self.__tail_contour = tail_contour.copy()
        self.__updated = False

    ''' Horizontally flips the comet contours. '''
    def flip(self):

        width = self.__sample.get_image().shape[1]

        if self.__tail_contour is not None:
            self.__tail_contour = utils.flip_contour(
                self.__tail_contour, width)

        self.__head_contour = utils.flip_contour(
            self.__head_contour, width)


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

    def get_id(self):
        return self.__id

    def get_tail_contour(self):
        return self.__tail_contour

    def set_tail_contour(self, tail_contour):
        self.__tail_contour = tail_contour

    def get_head_contour(self):
        return self.__head_contour

    def set_head_contour(self, head_contour):
        self.__head_contour = head_contour

    def get_updated(self):
        return self.__updated

    def set_updated(self, updated):
        self.__updated = updated

    def get_parameters(self):

        if not self.__updated:
            self.build_parameters()
        return self.__parameters

    def set_parameters(self, parameters):
        self.__parameters = parameters 


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	CometParameters                                                           #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class CometParameters(object):

    '''
        The CometParameters class.
    '''

    ''' Initialization method. '''
    def __init__(self):

        self.initialize()

    ''' Atributes initialization. '''
    def initialize(self):
        
        # Number of pixels in the comet.
        self.__comet_area = 0.
        # Length of the comet region in pixels.	                 
        self.__comet_length = 0.
        # Sum of pixel intensities inside the comet.	                 
        self.__comet_dna_content = 0. 
        # Comet DNA content divided by comet size.            
        self.__comet_average_intensity = 0.
        # Number of pixels inside the head.	     
        self.__head_area = 0.
        # Length of the head in pixels.                 
        self.__head_length = 0.
        # Sum of pixel intensities inside the head.
        self.__head_dna_content = 0.
        # Head DNA content divided by head size. 	         
        self.__head_average_intensity = 0.
        # Head DNA content as a percentage of Comet DNA content.        
        self.__head_dna_percentage = 0.
        # Number of pixels in the tail.         
        self.__tail_area = 0.
        # Length of the tail in pixels.                 
        self.__tail_length = 0.
         # Sum of pixel intensities inside the tail.                
        self.__tail_dna_content = 0.
        # Tail DNA content divided by tail size.	        
        self.__tail_average_intensity = 0.
        # Tail DNA content as a percentage of Comet DNA content.  	     
        self.__tail_dna_percentage = 0.
        # Tail length times Tail DNA %.  	     
        self.__tail_moment = 0.
        # Tail DNA % times the distance between the intensity-weighted
        # centroids of head and tail.  	             
        self.__olive_moment = 0. 	              
                                                 

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_comet_area(self):
        return self.__comet_area    

    def set_comet_area(self, area):
        self.__comet_area = area

    def get_comet_length(self):
        return self.__comet_length    

    def set_comet_length(self, length):
        self.__comet_length = length

    def get_comet_dna_content(self):
        return self.__comet_dna_content    

    def set_comet_dna_content(self, dna_content):
        self.__comet_dna_content = dna_content

    def get_comet_average_intensity(self):
        return self.__comet_average_intensity    

    def set_comet_average_intensity(self, average_intensity):
        self.__comet_average_intensity = average_intensity 

    def get_head_area(self):
        return self.__head_area    

    def set_head_area(self, area):
        self.__head_area = area

    def get_head_length(self):
        return self.__head_length

    def set_head_length(self, length):
        self.__head_length = length

    def get_head_dna_content(self):
        return self.__head_dna_content    

    def set_head_dna_content(self, dna_content):
        self.__head_dna_content = dna_content 

    def get_head_average_intensity(self):
        return self.__head_average_intensity    

    def set_head_average_intensity(self, average_intensity):
        self.__head_average_intensity = average_intensity 

    def get_head_dna_percentage(self):
        return self.__head_dna_percentage    

    def set_head_dna_percentage(self, dna_percentage):
        self.__head_dna_percentage = dna_percentage

    def get_tail_area(self):
        return self.__tail_area    

    def set_tail_area(self, area):
        self.__tail_area = area

    def get_tail_length(self):
        return self.__tail_length

    def set_tail_length(self, length):
        self.__tail_length = length

    def get_tail_dna_content(self):
        return self.__tail_dna_content    

    def set_tail_dna_content(self, dna_content):
        self.__tail_dna_content = dna_content 

    def get_tail_average_intensity(self):
        return self.__tail_average_intensity    

    def set_tail_average_intensity(self, average_intensity):
        self.__tail_average_intensity = average_intensity 

    def get_tail_dna_percentage(self):
        return self.__tail_dna_percentage    

    def set_tail_dna_percentage(self, dna_percentage):
        self.__tail_dna_percentage = dna_percentage

    def get_tail_moment(self):
        return self.__tail_moment

    def set_tail_moment(self, tail_moment):
        self.__tail_moment = tail_moment

    def get_olive_moment(self):
        return self.__olive_moment

    def set_olive_moment(self, olive_moment):
        self.__olive_moment = olive_moment