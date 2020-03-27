# -*- encoding: utf-8 -*-

'''
    The model module.
'''

# General imports
import ntpath
import copy

# Custom imports
import model.utils as utils
from model.canvas_model import CanvasModel
from model.parser import Parser
from model.algorithms import FreeComet, OpenComet
from model.algorithm_settings import AlgorithmSettings
from model.sample import Sample
from model.comet import Comet



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

   
