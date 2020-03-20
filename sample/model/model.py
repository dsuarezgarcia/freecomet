# -*- encoding: utf-8 -*-

'''
    The Model module.
'''

# General imports
import itertools
import ntpath
import numpy
import copy

# Custom imports
from singleton import Singleton

import model.utils as utils
from model.canvas_model import CanvasModel, TailContourBuilder, HeadContourBuilder
from model.parser import Parser
from model.algorithms import FreeComet, OpenComet


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	Model                                                                     #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
 
class Model(object):

    '''
        The Model class.
    '''

    APP_NAME = "FreeComet"
    FILE_EXTENSION = ".fc"

    MAX_ZOOM_VALUE = 8.
    MIN_ZOOM_VALUE = 0.1

    ''' Initialization method. '''
    def __init__(self):

        self.initialize()

    ''' Attributes initialization. '''
    def initialize(self):
        
        self.__project_path = None
        self.__store = {}
        self.__algorithm = None
        self.__algorithm_settings = AlgorithmSettings()
        
        # Initialize CanvasModel
        CanvasModel()
        TailContourBuilder()
        HeadContourBuilder()
        


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                  Methods                                    #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' 'New project' behaviour. '''
    def new_project(self):
        self.initialize()

    ''' 'Open project' behaviour. '''
    def open_project(self, project_path):

        # Retrieve data from file
        data = Parser.read(project_path)

        store = {}
        # Add to each of the stores the required information
        for sample in data['samples']:

            # Give new ID
            sample.set_id(next(Sample.new_id))
            # Set decompressed image
            sample.set_image(utils.decompress_image(sample.get_image()))           
            # Add to store           
            store[sample.get_id()] = sample

        # Update Model
        self.__store.clear()
        self.__store = store
        self.__project_path = project_path
        self.__algorithm_settings = data['settings'] 


    ''' 'Save project' behaviour. '''
    def save_project(self, path=None):

        if path is None:
            path = self.__project_path

        # Prepare data to be saved in memory       
        data = {}

        samples = []
        for (_, sample) in self.__store.items():

            sample_copy = copy.deepcopy(sample)
            # Compress image
            compressed_image = utils.compress_image(sample.get_image().copy())
            sample_copy.set_image(compressed_image)
            samples.append(sample_copy)

        data['samples'] = samples
        data['settings'] = self.__algorithm_settings

        # Save data
        try:
            Parser.write(data, path)
            if path is not None:
                self.__project_path = path
            return True

        except:                   
            return False

    ''' Adds given sample to the store. '''
    def add_sample(self, sample):
        self.__store[sample.get_id()] = sample
        
    ''' Deletes comet from sample with given IDs. '''    
    def delete_comet(self, sample_id, comet_id):

        # Delete comet from Sample
        (comet, pos) = self.__store[sample_id].delete_comet(comet_id)
        
        # See if deleted comet was the selected one and set to None
        if self.__store[sample_id].get_selected_comet_id() == comet_id:
            self.__store[sample_id].set_selected_comet_id(None)

        return (comet, pos)

    ''' Analyzes given sample. '''
    def analyze_sample(self, sample, algorithm_settings):

        if algorithm_settings is None:
            algorithm_settings = self.__algorithm_settings

        # FreeComet
        if (algorithm_settings.get_algorithm_id() == 
            AlgorithmSettings.FREECOMET):

            self.__algorithm = FreeComet(
                algorithm_settings.get_fit_head(),
                algorithm_settings.get_fit_tail()
            )

        # OpenComet
        elif (algorithm_settings.get_algorithm_id() == 
              AlgorithmSettings.OPENCOMET):

            self.__algorithm = OpenComet()

        # Execute algorithm
        comet_list_contours = self.__algorithm.execute(sample)
        # Build Comet objects
        return self.__build_comets(comet_list_contours, sample)

    ''' Deletes the sample with given ID from the store and returns a copy. '''
    def delete_sample(self, sample_id):

        sample_copy = self.__store[sample_id]
        del self.__store[sample_id]
        return sample_copy

    ''' Renames the sample with given ID with given name. '''
    def rename_sample(self, sample_id, name):
        self.__store[sample_id].set_name(name)

    ''' Generates an excel file with the segmented comet metrics. '''
    def generate_excel_file(self, filename):
        Parser.generate_excel_file(self.__store.values(), filename) 

    ''' Returns the current project name. '''
    def get_project_name(self):

        if self.__project_path is None:
            return None
        return ntpath.basename(self.__project_path)

    ''' Returns the sample with given ID. '''
    def get_sample(self, sample_id):
        return self.__store[sample_id]

    ''' Returns the comet number from the comet that matches given ID from the
        sample that matches given ID.
    '''
    def get_comet_number(self, sample_id, comet_id):        

        number = 1
        for comet in self.__store[sample_id].get_comet_list():
            if comet.get_id() == comet_id:
                return number
            number += 1

        return -1

    ''' Updates the comet lists of the samples with given IDs. ''' 
    def update_samples_comet_list(self, samples_comet_lists):

        data = []
        for (sample_id, comet_list, analyzed) in samples_comet_lists:

            # Keep data
            data.append((sample_id, 
                         self.__store[sample_id].get_comet_list().copy(),
                         self.__store[sample_id].get_analyzed()
                       ))  
            # Set comet list      
            self.__store[sample_id].set_comet_list(comet_list)
            # Set analyzed flag
            self.__store[sample_id].set_analyzed(analyzed)
            # No selected comet        
            self.__store[sample_id].set_selected_comet_id(None)
            # No comet being edited
            self.__store[sample_id].set_comet_being_edited_id(None)
            
        return data

    ''' Flips horizontally the image of the sample with given ID. '''
    def flip_sample_image(self, sample_id):
    
        # Flip the image horizontally
        flipped_image = utils.flip_image_horizontally(
                            self.__store[sample_id].get_image())
        self.__store[sample_id].set_image(flipped_image)

        # Flip the comet contours
        for comet in self.__store[sample_id].get_comet_list():
            comet.flip()

    ''' Inverts the image of the sample with given ID. '''
    def invert_sample_image(self, sample_id):

        # Invert the image
        inverted_image = utils.invert_image(
                             self.__store[sample_id].get_image())
        self.__store[sample_id].set_image(inverted_image)
        # Comet statistics must be recalculated
        for comet in self.__store[sample_id].get_comet_list():
            comet.set_updated(False)
            
    ''' Adds given zoom value to sample's zoom model with given ID. '''        
    def add_new_zoom_value(self, sample_id, zoom_text):
    
        zoom_value = int(zoom_text) / 100
        zoom_model = self.__store[sample_id].get_zoom_model()
        
        # Above maximum allowed zoom
        if zoom_value >= Model.MAX_ZOOM_VALUE:
        
            index = len(zoom_model) - 1        
            return (zoom_model[index], index)
            
        # Below minimum allowed zoom    
        if zoom_value <= Model.MIN_ZOOM_VALUE:
        
            return (zoom_model[0], 0)
            
        # Insert new zoom value   
        index = 0
        while index < len(zoom_model):
               
            # The zoom level is already in the sample's model
            if zoom_value == zoom_model[index]:
                self.__store[sample_id].set_zoom_index(index)
                return (zoom_value, index)
                
            # Add new zoom level
            elif zoom_value < zoom_model[index]:
                zoom_model.insert(index, zoom_value)
                self.__store[sample_id].set_zoom_index(index)
                return (zoom_value, index)
                
            index += 1 
            
    ''' Selects the sample's comet with given ID. '''
    def select_comet(self, sample_id, comet_id):
        self.get_sample(sample_id).set_selected_comet_id(comet_id)
         
    ''' Builds Comet objects with given contours. '''
    def __build_comets(self, comet_contours_list, sample):

        comet_list = []
        for (tail_contour, head_contour) in comet_contours_list:

            # Build Comet
            comet = Comet(sample, tail_contour, head_contour)
            comet_list.append(comet)

        return comet_list
        

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #    

    def get_project_path(self):
        return self.__project_path

    def set_project_path(self, project_path):
        self.__project_path = project_path

    def get_store(self):
        return self.__store

    def set_store(self, store):
        self.__store = store

    def get_algorithm_settings(self):
        return self.__algorithm_settings

    def set_algorithm_settings(self, algorithm_settings):
        self.__algorithm_settings = algorithm_settings

   

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

        if pos is None:
            self.__comet_list.append(comet)
        else:
            self.__comet_list.insert(pos, comet)
        # Update analyzed
        self.__analyzed = True
   
    ''' Deletes comet with given ID. '''
    def delete_comet(self, comet_id):

        pos = 0
        while pos < len(self.__comet_list):

            if self.__comet_list[pos].get_id() == comet_id:
                comet_copy = self.__comet_list[pos]
                del self.__comet_list[pos]

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
       
    def set_comet_being_edited_tail_contour_dictt(self, comet_being_edited_tail_contour_dict):
        self.__comet_being_edited_tail_contour_dict = comet_being_edited_tail_contour_dict
        
    def get_comet_being_edited_head_contour_dict(self):
        return self.__comet_being_edited_head_contour_dict
       
    def set_comet_being_edited_head_contour_dict(self, comet_being_edited_head_contour_dict):
        self.__comet_being_edited_head_contour_dict = comet_being_edited_head_contour_dict
    

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



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	AlgorithmSettings                                                         #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class AlgorithmSettings(metaclass=Singleton):

    '''
        The AlgorithmSettings class. Extends from Singleton.
    '''

    FREECOMET = 0
    OPENCOMET = 1

    ''' Iitialization method. '''
    def __init__(self):
        
        self.__algorithm_id = AlgorithmSettings.FREECOMET
        self.__fit_tail = False
        self.__fit_head = False


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                            Getters & Setters                                #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_algorithm_id(self):
        return self.__algorithm_id

    def set_algorithm_id(self, algorithm_id):
        self.__algorithm_id = algorithm_id

    def get_fit_tail(self):
        return self.__fit_tail

    def set_fit_tail(self, fit_tail):
        self.__fit_tail = fit_tail

    def get_fit_head(self):
        return self.__fit_head

    def set_fit_head(self, fit_head):
        self.__fit_head = fit_head
        
        