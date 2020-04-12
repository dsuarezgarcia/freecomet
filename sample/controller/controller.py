# -*- encoding: utf-8 -*-

'''
    The controller module.
'''

# General imports
import os
import sys
import copy
import ntpath


# PyGObject imports
import gi
from gi.repository import GLib


# Custom imports
from pathvalidate import ValidationError, validate_filename
from dialog_response import DialogResponse
from singleton import Singleton

from view.view_store import CometView, SampleParameters

from controller.algorithm_settings_dto import AlgorithmSettingsDto
from controller.canvas_state import CanvasSelectionState, CanvasEditingState, \
    EditingSelectionState, BuildingTailContourState, BuildingHeadContourState
from controller.threads import ThreadWithException
import controller.commands as commands

import model.utils as utils
from model.model import Model
from model.sample import Sample
from model.comet import Comet
from model.canvas_model import CanvasModel, DelimiterPointType, \
    contours_are_nested, check_contour_is_closed, make_roommates




# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#  Controller                                                                 #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class Controller(object):

    ''' 
        The Controller class. 
    '''

    ''' Initialization method. '''
    def __init__(self, model, view, strings):
    
        # Active Sample ID
        self.__active_sample_id = None
        
        # Undo & Redo stacks
        self.__undo_stack = []
        self.__redo_stack = []

        # Strings
        self.__strings = strings

        # Flags
        self.__flag_unsaved_changes = False
        self.__flag_project_is_new = True

        # Constants
        self.__SEPARATOR = " - "
        self.__UNSAVED_CHANGES_SYMBOL = "*"

        # Model & View
        self.__model = model
        self.__view = view
        
        # Canvas state
        self.__canvas_state = CanvasSelectionState(self)

        # Start UI
        self.__view.connect(self)
        self.__view.set_application_window_title(
            self.__build_application_window_title())        
        self.__view.set_strings(strings)
        self.__view.start()


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                  Use Cases                                  #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' 'Exit' use case. '''
    def exit_use_case(self):
     
        # If there are unsaved changes in the current project
        if self.__flag_unsaved_changes:   
            self.__ask_user_to_save_before_action(self.__view.exit)

        # Otherwise, proceed to exit
        else:
            self.__view.exit()

    ''' 'New project' use case. '''
    def new_project_use_case(self):

        # If there are unsaved changes
        if self.__flag_unsaved_changes:
            self.__ask_user_to_save_before_action(self.__new_project)

        # Otherwise proceed to create a new project
        else:
            self.__new_project()

    ''' 'Open project' use case '''
    def open_project_use_case(self):

        # If there are unsaved changes
        if self.__flag_unsaved_changes:
            self.__ask_user_to_save_before_action(self.__open_project)

        # Otherwise proceed to open an existent project
        else:
            self.__open_project()

    ''' Opens a project. '''
    def __open_project(self):

        # Run OpenProjectDialog
        (response_id, project_path) = self.__view.run_open_project_dialog()
        if response_id != DialogResponse.ACCEPT:
            return

        # Open project
        self.__model.open_project(project_path)
    
        # Update View
        view_store = []
        for (sample_id, sample) in self.__model.get_store().items():

            comet_view_list = self.comet_list_to_comet_view_list(
                sample.get_comet_list())
            view_store.append(
                (sample_id, 
                 sample.get_name(), 
                 utils.image_to_pixbuf(sample.get_image()),
                 comet_view_list
                )
            ) 
       
        # Restart View
        self.__view.restart()
        # Update View MainWindow title with openned project's name
        self.__view.get_main_window().set_title(
            self.__build_application_window_title())       
        # Add new Samples on View
        for (sample_id, sample_name, pixbuf, 
             comet_view_list) in view_store:
             
             self.__add_sample_view(sample_id, sample_name, 
                SampleParameters(pixbuf, comet_view_list), None)

        # Current project is not a 'new project'
        self.__flag_project_is_new = False
        # Update state and clear command stacks
        self.__update(False)
        self.__clear_command_stacks()

    ''' 'Save project' use case. '''
    def save_project_use_case(self):

        # If current project is a 'new project', 'Save project' works as
        # 'Save project as'.
        if self.__flag_project_is_new:           
            return self.save_project_as_use_case()
        self.__save_project()

    ''' 'Save project as' use case. '''
    def save_project_as_use_case(self):

        # Run SaveProjectAsDialog
        (response_id, path) = self.__view.run_save_project_as_dialog(
                                  self.__get_project_name())

        if response_id == DialogResponse.ACCEPT:

            # Validate filename
            filename = ntpath.basename(path)      
            _, extension = os.path.splitext(filename)
            if extension != '.fc':
                index = len(path) - len(filename)
                filename += Model.FILE_EXTENSION            
                path = path[:index] + filename

            # Save project at path
            return self.__save_project(path)

        return False

    ''' Saves project. '''
    def __save_project(self, path=None):

        # Save project
        self.__model.save_project(path)

        self.__command_stacks_on_project_saved()
        self.__update(False)
        self.__flag_project_is_new = False

    ''' 'Add samples' use case. '''
    def add_new_samples_use_case(self):

        # Run AddSamplesDialog
        (response_id, filenames) = self.__view.run_add_new_samples_dialog()

        if response_id == DialogResponse.ACCEPT:

            # Run LoadSamplesWindow
            self.__view.run_load_samples_window()

            # Run thread to add the Samples and update the LoadSamplesWindow
            self.__thread = ThreadWithException(self.__add_new_samples,
                                                [filenames])
            self.__thread.daemon = True
            self.__thread.start()

    ''' 'Rename sample' functioanlity. '''
    def rename_sample_use_case(self, sample_id, text):

        # Prepare the RenameSampleCommand
        command = commands.RenameSampleCommand(self)
        command.set_string(self.__strings.RENAME_SAMPLE_COMMAND_STRING)

        # Only valid characters for a filename
        try:
            validate_filename(text)
        except ValidationError as e:
            print("{}\n".format(e), file=sys.stderr)
            return       
        # Name must be valid
        sample_name = get_valid_name(text, self.__model.get_store())

        # Rename sample
        previous_name = self.rename_sample(sample_id, sample_name)

        # Add RenameSampleCommand to the undo stack
        command.set_data((sample_id, previous_name))               
        self.__add_command(command)

    ''' 'Delete sample' use case. '''
    def delete_sample_use_case(self, sample_id):

        # Prepare the DeleteSampleCommand
        command = commands.DeleteSampleCommand(self)
        command.set_string(self.__strings.DELETE_SAMPLE_COMMAND_STRING)

        # Delete sample
        (sample_copy, sample_parameters, pos) = self.delete_sample(sample_id)

        # Add DeleteSampleCommand to the undo stack              
        command.set_data((sample_copy, sample_parameters, pos))  
        self.__add_command(command)

    ''' 'Analyze samples' use case. '''
    def analyze_samples_use_case(self, samples_id_list, algorithm_settings=None):

        if algorithm_settings is None:
            algorithm_settings = self.__model.get_algorithm_settings()

        # Run AnalyzeSamplesLoadingWindow
        self.__view.run_analyze_samples_loading_window()

        # Run thread to analyze the Samples and update the
        # AnalyzeSamplesLoadingWindow
        self.__thread = ThreadWithException(
                            self.__analyze_samples,
                            [samples_id_list, algorithm_settings])
        self.__thread.daemon = True
        self.__thread.start()
 
    ''' 'Add new comet' use case. '''
    def add_new_comet_use_case(self, sample_id, tail_contour, head_contour):
        
        # Add comet
        return self.add_new_comet(sample_id, tail_contour, head_contour)

    ''' 'Delete comet' use case. '''
    def delete_comet_use_case(self, sample_id, comet_id):

        # Prepare the DeleteCometCommand
        command = commands.DeleteCometCommand(self)
        command.set_string(self.__strings.DELETE_COMET_COMMAND_STRING)

        # Delete comet
        (comet_copy, pos) = self.delete_comet(sample_id, comet_id)

        # Add DeleteCometCommand to the stack
        command.set_data((sample_id, comet_copy, pos))
        self.__add_command(command)
        
    ''' 'Edit comet contours' use case. ''' 
    def edit_comet_contours_use_case(self, sample_id, comet_id):
    
        # Prepare the EditCometContoursCommand
        command = commands.EditCometContoursCommand(self)
        command.set_string(self.__strings.EDIT_COMET_CONTOURS_COMMAND_STRING)

        # Start Comet being edited
        self.start_comet_being_edited(sample_id, comet_id)

        # Add EditCometContoursCommand to the undo stack
        data = (sample_id, comet_id,
                copy.deepcopy(CanvasModel.get_instance().get_tail_contour_dict()),
                copy.deepcopy(CanvasModel.get_instance().get_head_contour_dict()),
                self.get_sample_zoom_value(sample_id)
               )               
        command.set_data(data)                      
        self.__add_command(command)

    ''' 'Cancel edit comet contours' use case. '''
    def cancel_edit_comet_contours_use_case(self):
    
        # Prepare the CancelEditCometContoursCommand
        command = commands.CancelEditCometContoursCommand(self)
        command.set_string(self.__strings.CANCEL_EDIT_COMET_CONTOURS_COMMAND_STRING)
       
        # CanvasContours are parsed to ratio 1.
        scale_ratio = 1. / self.get_sample_zoom_value(self.__active_sample_id)
        
        tail_contour_dict = copy.deepcopy(CanvasModel.get_instance().get_tail_contour_dict())
        head_contour_dict = copy.deepcopy(CanvasModel.get_instance().get_head_contour_dict())    
        utils.scale_canvas_contour_dict(tail_contour_dict, scale_ratio)
        utils.scale_canvas_contour_dict(head_contour_dict, scale_ratio)
       
        comet_id = self.__model.get_sample(self.__active_sample_id).get_comet_being_edited_id()
        data = (
            self.__active_sample_id, 
            comet_id,
            tail_contour_dict,
            head_contour_dict
        )
        command.set_data(data)
      
        # Quit Comet being edited
        self.quit_comet_being_edited()
        
        # Add CancelEditCometContoursCommand to the undo stack                    
        self.__add_command(command)

    ''' 'Update comet contour' use case. '''
    def update_comet_contours_use_case(self, sample_id, comet_id, tail_contour, head_contour):
    
        # Prepare the UpdateCometContoursCommand
        command = commands.UpdateCometContoursCommand(self)
        command.set_string(self.__strings.UPDATE_COMET_CONTOURS_COMMAND_STRING)

        (_, old_tail_contour, old_head_contour) = self.update_comet_contours(
            sample_id, comet_id, tail_contour, head_contour)

        data = (sample_id, comet_id, old_tail_contour, old_head_contour,
                copy.deepcopy(CanvasModel.get_instance().get_tail_contour_dict()),
                copy.deepcopy(CanvasModel.get_instance().get_head_contour_dict())
               )
        # Add UpdateCometContoursCommand to the undo stack
        command.set_data(data)                      
        self.__add_command(command)
        
    ''' 'Remove comet tail' use case. '''
    def remove_comet_tail_use_case(self, sample_id, comet_id):

        # Prepare the RemoveCometTailCommand
        command = commands.RemoveCometTailCommand(self)
        command.set_string(self.__strings.REMOVE_COMET_TAIL_COMMAND_STRING)

        # Remove comet tail
        tail_contour = self.remove_comet_tail(sample_id, comet_id)

        # Add RemoveCometTailCommand to the stack
        command.set_data((sample_id, comet_id, tail_contour))
        self.__add_command(command)
 
    ''' 'About' use case. '''
    def about_use_case(self):      
        self.__view.run_about_dialog()

    ''' 'Undo' use case. '''
    def undo_use_case(self):
    
        unsaved_changes_value = self.__flag_unsaved_changes

        command = self.__undo_stack.pop()
        self.__update(command.get_flag_unsaved_changes())
        command.undo()
        command.set_flag_unsaved_changes(unsaved_changes_value)
        self.__redo_stack.append(command)

        if len(self.__undo_stack) == 0:
            self.__view.set_undo_button_sensitivity(False)
        self.__view.set_redo_button_sensitivity(True)
        
        self.__view.update_undo_and_redo_buttons_tooltips()

    ''' 'Redo' use case. '''
    def redo_use_case(self):

        unsaved_changes_value = self.__flag_unsaved_changes

        command = self.__redo_stack.pop()
        self.__update(command.get_flag_unsaved_changes())
        command.execute()
        command.set_flag_unsaved_changes(unsaved_changes_value)
        self.__undo_stack.append(command)

        if len(self.__redo_stack) == 0:
            self.__view.set_redo_button_sensitivity(False)
        self.__view.set_undo_button_sensitivity(True)
        
        self.__view.update_undo_and_redo_buttons_tooltips()

    ''' 'Generate excel file' use case. '''
    def generate_excel_file_use_case(self):

        # Run GenerateExcelFileDialog
        (response_id, filename) = self.__view.run_generate_excel_file_dialog(
            self.__get_project_name())

        if response_id == DialogResponse.ACCEPT:
            self.__model.generate_excel_file(filename)

    ''' 'See comet parameters' use case. '''
    def see_comet_parameters_use_case(self, sample_id, comet_id):
        
        sample_name = self.__model.get_sample(sample_id).get_name()
        comet_number = self.__model.get_comet_number(sample_id, comet_id)
        comet_parameters = self.__model.get_sample(sample_id).get_comet(
                               comet_id).get_parameters()

        self.__view.see_comet_parameters(
            sample_name, comet_number, comet_parameters)

    ''' 'Flip sample image' use case. '''
    def flip_sample_image_use_case(self, sample_id):

        # Prepare the FlipSampleImageCommand
        command = commands.FlipSampleImageCommand(self)
        command.set_string(self.__strings.FLIP_SAMPLE_IMAGE_COMMAND_STRING)

        self.flip_sample_image(sample_id)

        # Add FlipSampleImageCommand to the stack
        command.set_data((sample_id))
        self.__add_command(command)

    ''' 'Invert sample image' use case. '''
    def invert_sample_image_use_case(self, sample_id):
        
        # Prepare the InvertSampleImageCommand
        command = commands.InvertSampleImageCommand(self)
        command.set_string(self.__strings.INVERT_SAMPLE_IMAGE_COMMAND_STRINGA)

        self.invert_sample_image(sample_id)

        # Add InvertSampleImageCommand to the stack
        command.set_data(sample_id)
        self.__add_command(command)
        
    ''' 'Add new zoom value' use case. '''    
    def add_new_zoom_value_use_case(self, sample_id, zoom_level):
        return self.__model.add_new_zoom_value(sample_id, zoom_level)
  
    ''' 'Set tail color' use case. '''    
    def set_tail_color_use_case(self, tail_color):       
        CanvasModel.get_instance().set_tail_color(tail_color)
  
    ''' 'Set head color' use case. '''    
    def set_head_color_use_case(self, head_color):       
        CanvasModel.get_instance().set_head_color(head_color)
     
    ''' 'Create DelimiterPoint' use case. '''
    def create_delimiter_point_use_case(self, builder, coordinates,
            make_roommate=False):
    
        # Prepare the CreateDelimiterPointCommand command
        command = commands.CreateDelimiterPointCommand(self)
        command.set_string(self.__strings.CREATE_DELIMITER_POINT_COMMAND_STRING)
    
        # Create DelimiterPoint
        delimiter_point = self.create_delimiter_point(
                              builder, coordinates)
          
        # Make roommates if requested  
        if make_roommate:
            
            make_roommates(
                CanvasModel.get_instance().get_anchored_delimiter_point(),
                delimiter_point
            )
       
        # Add CreateDelimiterPointCommand to the stack
        data = commands.CreateDelimiterPointCommandData(
            self.__active_sample_id,
            delimiter_point.get_id(),
            delimiter_point.get_type(),
            delimiter_point.get_contour_id(),
            delimiter_point.get_roommate(),
            coordinates,
            builder,
            self.get_sample_zoom_value(self.__active_sample_id)
        )   
        command.set_data(data)
        self.__add_command(command)
        
        return delimiter_point
        
    ''' 
        Creates a new DelimiterPoint with given creation method and given
        coordinates. 
    '''    
    def create_delimiter_point(self, builder, coordinates, 
                               delimiter_point_id=None, canvas_contour_id=None,
                               roommate=None):
                       
        return builder.create_delimiter_point(
            coordinates, delimiter_point_id, canvas_contour_id, roommate)
       

    ''' 'Create and connect DelimiterPoint' use case. ''' 
    def create_and_connect_delimiter_point_use_case(self, builder,
            root_delimiter_point, coordinates, make_roommate=False):

        # Prepare the CreateDelimiterPointCommand command
        command = commands.CreateDelimiterPointCommand(self)
        command.set_string(self.__strings.CREATE_DELIMITER_POINT_COMMAND_STRING)
        
        # Create and connect
        delimiter_point = self.create_and_connect_delimiter_point(
            builder, root_delimiter_point, coordinates)
        
        # Make roommates if requested  
        if make_roommate:
            
            make_roommates(
                CanvasModel.get_instance().get_anchored_delimiter_point(),
                delimiter_point
            )
        
        # Add command to the stack
        data = commands.CreateDelimiterPointCommandData(
            self.__active_sample_id,
            delimiter_point.get_id(),
            delimiter_point.get_type(),
            delimiter_point.get_contour_id(),
            delimiter_point.get_roommate(),
            coordinates,
            builder,
            self.get_sample_zoom_value(self.__active_sample_id)
        )         
        data.set_root_delimiter_point_id(root_delimiter_point.get_id())
        command.set_data(data)
        self.__add_command(command)
        
        return delimiter_point
    
    ''' 
        Creates a new DelimiterPoint with given creation method and given
        coordinates and connects it to the root DelimiterPoint. 
    ''' 
    def create_and_connect_delimiter_point(self, builder, root_delimiter_point,
            coordinates, delimiter_point_id=None, roommate=None):
     
        return builder.create_and_connect_points(root_delimiter_point,
                   coordinates, delimiter_point_id, roommate)  

    ''' 'Connect DelimiterPoints' use case. '''
    def connect_delimiter_points_use_case(self, builder, src_delimiter_point,
            dst_delimiter_point): 

        #CanvasModel.get_instance().debug()

        # Previous CanvasContours IDs of both points
        previous_src_delimiter_point_canvas_contour_id = src_delimiter_point.\
            get_contour_id()
        previous_dst_delimiter_point_canvas_contour_id = dst_delimiter_point.\
            get_contour_id()

        if src_delimiter_point.get_contour_id() == dst_delimiter_point.get_contour_id():
            # Previous state of the CanvasContour's DelimiterPoint dict
            previous_canvas_contour = copy.deepcopy(builder.get_contour_dict()[
                src_delimiter_point.get_contour_id()])

        # Connect both points
        self.connect_delimiter_points(builder, src_delimiter_point, dst_delimiter_point)
        
        # See if the contour is closed
        canvas_contour = builder.get_contour_dict()[src_delimiter_point.get_contour_id()]
        delimiter_point_id_list = check_contour_is_closed(
            canvas_contour, src_delimiter_point)

        # If the CanvasContour has been closed
        if canvas_contour.get_closed(): 

            # If it is a Tail contour
            if builder.POINT_TYPE == DelimiterPointType.TAIL:
            
                # Prepare CanvasContourClosedCommand command
                command = commands.CanvasContourClosedCommand(self)
                command.set_string(self.__strings.CONNECT_DELIMITER_POINTS_COMMAND_STRING)
                command.set_data((self.__active_sample_id, builder, previous_canvas_contour))
                
                # Behaviour when a Tail CanvasContour is closed
                self.on_tail_closed_contour_created(
                    canvas_contour, delimiter_point_id_list)
                    
                # Add CanvasContourClosedCommand to the stack               
                self.__add_command(command)
                
            # If it is a Head contour
            else:
            
                # If a comet is being edited
                if self.get_sample_comet_being_edited_id(
                        self.get_active_sample_id()) is not None:
                        
                    # Add ConnectDelimiterPointsCommand to the stack
                    command = commands.ConnectDelimiterPointsCommand(self)
                    command.set_string(self.__strings.CONNECT_DELIMITER_POINTS_COMMAND_STRING)
                    command.set_data(
                    commands.ConnectDelimiterPointsCommandData(
                        self.__active_sample_id, builder,
                        src_delimiter_point_id, dst_delimiter_point_id,
                        previous_src_delimiter_point_canvas_contour_id,
                        previous_dst_delimiter_point_canvas_contour_id,
                        canvas_contour.get_id()
                        )
                    )      
                    self.__add_command(command) 
                   
                # If happened on 'free editing' mode
                else:    
            
                    # Behaviour when a Head CanvasContour is closed
                    (closed_head_canvas_contour, closed_tail_canvas_contour) = \
                        self.on_head_closed_contour_created(
                            canvas_contour,
                            delimiter_point_id_list
                        )

                    # Prepare and add the new built comet
                    comet_id = self.on_comet_built(
                        closed_head_canvas_contour, closed_tail_canvas_contour)
                    
                    # Prepare the AddCometCommand
                    command = commands.AddCometCommand(self)
                    command.set_string(self.__strings.ADD_COMET_COMMAND_STRING)
        
                    # Add AddCometCommand to the stack
                    command.set_data(commands.AddCometCommandData
                        (self.__active_sample_id, comet_id, 
                         self.__model.get_sample(self.__active_sample_id).get_analyzed(),
                         copy.deepcopy(closed_tail_canvas_contour),
                         previous_canvas_contour,
                         self.get_sample_zoom_value(self.__active_sample_id)                       
                        )
                     )
                    self.__add_command(command)
         
        # If the CanvasContour is not closed
        else:    
           
            # Add ConnectDelimiterPointsCommand to the stack
            command = commands.ConnectDelimiterPointsCommand(self)
            command.set_string(self.__strings.CONNECT_DELIMITER_POINTS_COMMAND_STRING)
            command.set_data(
                commands.ConnectDelimiterPointsCommandData(
                    self.__active_sample_id, builder,
                    src_delimiter_point.get_id(), dst_delimiter_point.get_id(),
                    previous_src_delimiter_point_canvas_contour_id,
                    previous_dst_delimiter_point_canvas_contour_id,
                    canvas_contour.get_id()
                )
            )      
            self.__add_command(command)        

    ''' Behaviour by default when a CanvasContour is closed. '''
    def __on_closed_contour_created(self, contour, valid_points_id_list):
                
        valid_points = [p for p in contour.get_delimiter_point_dict().values()
                        if p.get_id() in valid_points_id_list]

        # Contour has now only the DelimiterPoints that close the contour
        contour.set_delimiter_point_dict(
            {p.get_id():p for p in valid_points})

        # The rest of points are removed from the neighbors pointers
        for delimiter_point in valid_points:
            for neighbor in delimiter_point.get_neighbors():
                if neighbor.get_id() not in valid_points_id_list:
                    delimiter_point.get_neighbors().remove(neighbor)

        CanvasModel.get_instance().set_root_delimiter_point(None)
        CanvasModel.get_instance().set_anchored_delimiter_point(None)

        return valid_points

    ''' Behaviour when a Tail CanvasContour is closed. '''
    def on_tail_closed_contour_created(self, contour,
            valid_delimiter_point_id_list):
            
        self.__on_closed_contour_created(
            contour, valid_delimiter_point_id_list)
                
    ''' Behaviour when a Head CanvasContour is closed. '''
    def on_head_closed_contour_created(self, head_contour, valid_points_id_list):
        
        valid_points = self.__on_closed_contour_created(
                           head_contour, valid_points_id_list)

        closed_tail_contour_list = [contour for (_, contour) in CanvasModel.\
                                     get_instance().get_tail_contour_dict().items()
                                     if contour.get_closed()]

        # If the Head contour is nested to a closed Tail contour, both are
        # used to build the comet.
        for tail_contour in closed_tail_contour_list:

            tail_coordinates_list = [p.get_coordinates() for p in
                                     tail_contour.get_delimiter_point_dict().values()]
            cv2_tail_contour = utils.list_to_contour(tail_coordinates_list)
                    
            is_inside = False
            index = 0
            while (index < len(valid_points) and not is_inside):
 
                is_inside = utils.is_point_inside_contour(
                    cv2_tail_contour, valid_points[index].get_coordinates())
                
                if is_inside:
                    return (head_contour, tail_contour)

                index += 1

        # Otherwise, the comet is built just with the Head contour
        return (head_contour, None)
          
    ''' 
        Connects 2 given DelimiterPoints.
    '''    
    def connect_delimiter_points(self, builder, src_delimiter_point,
            dst_delimiter_point, canvas_contour_id=None):
            
        builder.connect_points(src_delimiter_point, dst_delimiter_point,
            canvas_contour_id)
      
    ''' 
        Disconnects 2 given DelimiterPoints.
    '''
    def disconnect_delimiter_points(self, builder, src_delimiter_point, 
            dst_delimiter_point, previous_src_delimiter_point_canvas_contour_id,
            previous_dst_delimiter_point_canvas_contour_id):
        
        builder.disconnect_points(src_delimiter_point, dst_delimiter_point,
            previous_src_delimiter_point_canvas_contour_id,
            previous_dst_delimiter_point_canvas_contour_id
        )
        
    ''' Behaviour when a comet has been successfully built. '''
    def on_comet_built(self, head_contour, tail_contour=None):

        # Create and add the new Comet to the Model
        comet_id = self.on_add_comet(tail_contour, head_contour)
        # Clear the Tail points that belong to the tail contour
        if tail_contour is not None:
            del CanvasModel.get_instance().get_tail_contour_dict()\
                [tail_contour.get_id()]
        # Clear all Head contour points
        del CanvasModel.get_instance().get_head_contour_dict()\
                [head_contour.get_id()]

        CanvasModel.get_instance().set_root_delimiter_point(None)

        return comet_id
  
    ''' 'Move DelimiterPoints' use case. '''
    def move_delimiter_points_use_case(self, delimiter_point_selection):
   
        # The DelimiterPoints have been already moved. This method creates and 
        # adds the command to the stack so it can be undone/redone.
   
        # Prepare the MoveDelimiterPointsCommand command
        command = commands.MoveDelimiterPointsCommand(self)
        command.set_string(self.__strings.MOVE_DELIMITER_POINTS_COMMAND_STRING)
        
        # Set data
        command.set_data(
            (self.__active_sample_id,
            copy.deepcopy(delimiter_point_selection),
            self.get_sample_zoom_value(self.__active_sample_id))
        )
        # Add MoveDelimiterPointsCommand to the stack
        self.__add_command(command)
        
    '''
        Moves the given DelimiterPoints from the DelimiterPointSelection 
        from its current position to their origin.
    '''    
    def move_delimiter_points_to_origin(self, delimiter_point_selection, scale_ratio):

        # Get scale_ratio to scale DelimiterPoints coordinates if needed
        current_scale_ratio = self.get_sample_zoom_value(self.__active_sample_id)
        scale_flag = (scale_ratio != current_scale_ratio)
        if scale_flag:
            new_scale_ratio = current_scale_ratio / scale_ratio

        for (_, selected_delimiter_point) in delimiter_point_selection.get_dict().items():

            # Get DelimiterPoint
            delimiter_point = CanvasModel.get_instance().get_delimiter_point(
                selected_delimiter_point.get_id(),
                selected_delimiter_point.get_type(),
                selected_delimiter_point.get_canvas_contour_id()
            )
            
            # Current coordinates will be the new origin ones
            new_origin = delimiter_point.get_coordinates()
                       
            # Set origin as new coordinates
            origin = delimiter_point_selection.get_dict()[delimiter_point.get_id()].get_origin()
            if scale_flag:
                origin = utils.scale_point(origin, new_scale_ratio)          
            delimiter_point.set_coordinates(origin)
            
            # Set new origin 
            delimiter_point_selection.get_dict()[delimiter_point.get_id()].\
                set_origin(new_origin)
        
        # Update Canvas
        self.__view.get_main_window().get_canvas().update()
        
        return current_scale_ratio
        
    ''' 'Delete DelimiterPoints' use case. '''    
    def delete_delimiter_points_use_case(self, selected_delimiter_point_list):    
        
        #CanvasModel.get_instance().debug()
        
        # Prepare the DeleteDelimiterPointsCommand command
        command = commands.DeleteDelimiterPointsCommand(self)
        command.set_string(self.__strings.DELETE_DELIMITER_POINTS_COMMAND_STRING)
        
        # Take the selected DelimiterPoints for removal
        if len(selected_delimiter_point_list) == 0:
            selected_delimiter_point_list = CanvasModel.get_instance().\
                get_delimiter_point_selection().get_dict().copy().values()
               
        deleted_delimiter_point_data_dict = {}
        for selected_delimiter_point in selected_delimiter_point_list:
        
            delimiter_point = CanvasModel.get_instance().get_delimiter_point(
                selected_delimiter_point.get_id(),
                selected_delimiter_point.get_type(),
                selected_delimiter_point.get_canvas_contour_id()
            )
        
            if delimiter_point.get_contour_id() not in deleted_delimiter_point_data_dict.keys():
                deleted_delimiter_point_data_dict[delimiter_point.get_contour_id()] = \
                    ([], CanvasModel.get_instance().get_canvas_contour(
                        delimiter_point.get_type(), delimiter_point.get_contour_id()).get_closed())
        
            deleted_delimiter_point_data_dict[delimiter_point.get_contour_id()][0].append(
                commands.DeletedDelimiterPointData(
                    delimiter_point.get_id(),
                    delimiter_point.get_coordinates(),
                    [n.get_id() for n in delimiter_point.get_neighbors()],
                    delimiter_point.get_roommate(),
                    CanvasModel.get_instance().get_contour_builder(delimiter_point.get_type())
                )
            )  
        
        # Delete DelimiterPoints
        self.delete_delimiter_points(selected_delimiter_point_list)
           
        # Set data
        command.set_data(
            commands.DeleteDelimiterPointsCommandData(
                self.__active_sample_id,
                deleted_delimiter_point_data_dict,
                self.get_sample_zoom_value(self.__active_sample_id)
            )
        )
        # Add DeleteDelimiterPointsCommand to the stack
        self.__add_command(command)
        
        
    ''' Deletes the DelimiterPoints with given IDs. '''
    def delete_delimiter_points(self, selected_delimiter_point_list):
                          
        # Delete DelimiterPoints
        CanvasModel.get_instance().delete_delimiter_points(
            selected_delimiter_point_list)
    
        # If a Comet is being edited, update the 'Save' Button sensitivity
        if self.get_active_sample_comet_being_edited_id() is not None:    
            self.set_comet_being_edited_has_changed(True)
            self.update_save_button_sensitivity()
    
        # Update Canvas
        self.__view.get_main_window().get_canvas().update()
    
    
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                   Methods                                   # 
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
    
    ''' Returns the string that will be used for the Undo Button tooltip. '''
    def get_undo_button_tooltip(self):
    
        if len(self.__undo_stack) == 0:
            string = self.__strings.LAST_ACTION_LABEL
        else:
            string = self.__undo_stack[-1].get_string()
        
        return self.__strings.UNDO_TOOLBAR_BUTTON_TOOLTIP.format(string) 
        
    ''' Returns the string that will be used for the Redo Button tooltip. '''
    def get_redo_button_tooltip(self):
    
        if len(self.__redo_stack) == 0:
            string = self.__strings.LAST_ACTION_LABEL
        else:
            string = self.__redo_stack[-1].get_string()
        
        return self.__strings.REDO_TOOLBAR_BUTTON_TOOLTIP.format(string)     

    ''' 
        Removes the tail of the comet with given ID that belongs to the sample
        with given ID.
    '''
    def remove_comet_tail(self, sample_id, comet_id):

        # Model
        tail_contour = self.__remove_comet_tail_model(sample_id, comet_id) 
        # View
        self.__remove_comet_tail_view(sample_id, comet_id)
        return tail_contour
        
    ''' 'remove_comet_tail' Model behaviour. '''    
    def __remove_comet_tail_model(self, sample_id, comet_id):
    
        return self.__model.get_sample(sample_id).\
                   get_comet(comet_id).remove_tail()
    
    ''' 'remove_comet_tail' View behaviour. '''
    def __remove_comet_tail_view(self, sample_id, comet_id):
            
        comet_view = self.__view.get_view_store().get_comet_view(sample_id, comet_id)
        comet_view.set_scaled_tail_contour(None)
        self.__view.get_main_window().get_canvas().update()
        self.__view.get_main_window().get_selection_window().update()

    ''' Updates the Save Button sensitivity. '''
    def update_save_button_sensitivity(self):

        tail_contour_dict = CanvasModel.get_instance().\
                                 get_tail_contour_dict()
        head_contour_dict = CanvasModel.get_instance().\
                                 get_head_contour_dict()

        comet_is_valid = False
        # If there are no Tail contours, with a closed Head contour
        # is enough
        if len(tail_contour_dict) == 0:

            if len(head_contour_dict) == 0:
            
                comet_is_valid = True

            elif len(head_contour_dict) == 1:

                for (_, head_contour) in head_contour_dict.items():

                    comet_is_valid = head_contour.get_closed()
   
        else:

            # If there is a Tail contour, both Tail and Head contours
            # must be closed, and also touching themselves
            if len(tail_contour_dict) == 1:
            
                for (_, tail_contour) in tail_contour_dict.items():

                    if tail_contour.get_closed():

                        for (_, head_contour) in head_contour_dict.items():

                            comet_is_valid = (
                                head_contour.get_closed() and 
                                contours_are_nested(
                                    head_contour, tail_contour,))
                

        self.__view.get_main_window().get_selection_window().\
            get_save_button().set_sensitive(comet_is_valid)

    ''' Translates the app to Spanish language. '''
    def translate_app_to_spanish(self):
    
        self.__strings.translate_to_spanish()
        self.__view.set_strings(self.__strings)
        self.__view.set_application_window_title(
            self.__build_application_window_title())

    ''' Translates the app to English language. '''
    def translate_app_to_english(self):

        self.__strings.translate_to_english()
        self.__view.set_strings(self.__strings)
        self.__view.set_application_window_title(
            self.__build_application_window_title())     

    ''' Stops the Analyze Samples thread. '''
    def stop_analyze_samples_thread(self):
        self.__thread.raise_exception()

    ''' Analyze samples behaviour. '''
    def __analyze_samples(self, samples_id_list, algorithm_settings):

        try:

            # Prepare the AnalyzeSamples command
            command = commands.AnalyzeSamplesCommand(self)
            command.set_string(self.__strings.ANALYZE_SAMPLES_COMMAND_STRING)

            samples_comet_lists = []
            i = 0
            # Process each sample
            while (i < len(samples_id_list) and not 
                   self.__view.get_analyze_samples_loading_window().\
                        get_cancelled()):

                # Retrieve Sample from model
                sample = self.__model.get_sample(samples_id_list[i])
                # Update AnalyzeSamplesLoadingWindow
                GLib.idle_add(self.__view.update_analyze_samples_loading_window,
                    self.__strings.ANALYZING_SAMPLES_WINDOW_LABEL.format(
                        i+1, len(samples_id_list)), sample.get_name())
     
                # Sample analyzed flag value previous to analysis
                analyzed_flag = sample.get_analyzed()

                comet_list = self.__model.analyze_sample(sample, algorithm_settings)
                samples_comet_lists.append((samples_id_list[i], comet_list, True))
                i += 1

            # Operation cannot be cancelled anymore
            GLib.idle_add(self.__view.get_analyze_samples_loading_window().\
                get_cancel_button().hide)

            # Only save if not cancelled
            if not self.__view.get_analyze_samples_loading_window().get_cancelled():

                # Replace in Model
                data = self.__model.update_samples_comet_list(samples_comet_lists)

                samples_comet_view_lists = []
                for (sample_id, comet_list, _) in samples_comet_lists:
                    samples_comet_view_lists.append(
                        (sample_id, self.comet_list_to_comet_view_list(comet_list)))
                # Replace in View
                GLib.idle_add(self.replace_samples_comet_view_list,
                    samples_comet_view_lists)

                # Add AnalyzeSamples command to the stack
                command.set_data(data)
                self.__add_command(command)

        finally:

            GLib.idle_add(self.__view.close_analyze_samples_loading_window)
            
    ''' Sets the given comet list for the sample with given ID. '''
    def replace_samples_comet_view_list(self, samples_comet_view_lists):

        for (sample_id, comet_view_list) in samples_comet_view_lists:    

            sample_parameters = self.__view.get_view_store().get_store()[sample_id]
            # Set new list
            sample_parameters.set_comet_view_list(comet_view_list)
            # Set number of comets in sample
            self.__view.get_main_window().get_samples_view().\
                set_sample_number_of_comets(sample_id, len(comet_view_list), 
                    self.__model.get_sample(sample_id).get_analyzed()
            )       
                        
        
        # Scale CometView objects to current Sample scale ratio
        scale_ratio = self.get_sample_zoom_value(
                        self.__active_sample_id)
        self.scale_sample_comet_contours(
            self.__active_sample_id, scale_ratio) 

        # Update
        self.__view.get_main_window().get_canvas().update()
        self.__view.get_main_window().get_selection_window().update()

    ''' 
        Sets the comet contours with given ID that belongs to the sample with
        given ID.
    '''
    def set_comet_contours(self, sample_id, comet_id, tail_contour, head_contour):

        comet = self.__model.get_sample(sample_id).get_comet(
            comet_id)

        old_tail_contour = comet.get_tail_contour()
        old_head_contour = comet.get_head_contour()
        comet.update_contours(tail_contour, head_contour)
        
        return (old_tail_contour, old_head_contour)


    ''' Returns the Comet tail contour with given identifier. '''
    def get_tail_contour(self, sample_id, comet_id):
        return self.__model.get_sample(sample_id).get_comet(
            comet_id).get_tail_contour()

    ''' Returns the Comet 'head contour' with given identifier. '''
    def get_head_contour(self, sample_id, comet_id):
        return self.__model.get_sample(sample_id).get_comet(
            comet_id).get_head_contour()

    ''' Flips the sample's image with given ID. '''
    def flip_sample_image(self, sample_id):

        # Update Model
        self.__model.flip_sample_image(sample_id)
        
        # Update View
        sample_parameters = self.__view.get_view_store().get_store()[sample_id]
        # Flip Pixbufs
        sample_parameters.set_original_pixbuf(
            sample_parameters.get_original_pixbuf().flip(True))
        sample_parameters.set_displayed_pixbuf(
            sample_parameters.get_displayed_pixbuf().flip(True))
            
        width = sample_parameters.get_displayed_pixbuf().get_width()
        # Flip ScaledContours
        for comet_view in sample_parameters.get_comet_view_list():

            if comet_view.get_scaled_tail_contour() is not None:
                comet_view.set_scaled_tail_contour(
                    utils.flip_contour(
                        comet_view.get_scaled_tail_contour(), width))                
            comet_view.set_scaled_head_contour(
                utils.flip_contour(
                    comet_view.get_scaled_head_contour(), width))
        
        # Flip DelimiterPoints
        for (_, contour) in self.__model.get_sample(sample_id).get_tail_contour_dict().items():
            for delimiter_point in contour.get_delimiter_point_dict().values():
                coordinates = delimiter_point.get_coordinates()
                delimiter_point.set_coordinates((width-1-coordinates[0], coordinates[1]))
        for (_, contour) in self.__model.get_sample(sample_id).get_head_contour_dict().items():
            for delimiter_point in contour.get_delimiter_point_dict().values():
                coordinates = delimiter_point.get_coordinates()
                delimiter_point.set_coordinates((width-1-coordinates[0], coordinates[1]))

        # Delete Sample's cache of zoomed images
        if sample_id in self.__view.get_main_window().get_zoom_tool().get_cache().keys(): 
            del self.__view.get_main_window().get_zoom_tool().get_cache()[sample_id]

        # Update Canvas
        self.__view.get_main_window().get_canvas().update()

    ''' Inverts the sample's image with given ID. '''
    def invert_sample_image(self, sample_id):

        # Update Model
        self.__model.invert_sample_image(sample_id)
        
        # Update View
        sample_parameters = self.__view.get_view_store().get_store()[sample_id]
        image = self.__model.get_sample(sample_id).get_image()       
        scale_ratio = self.get_sample_zoom_value(sample_id)

        # Set inverted pixbufs
        pixbuf = utils.image_to_pixbuf(image)          
        sample_parameters.set_original_pixbuf(pixbuf)
        scaled_pixbuf = pixbuf.scale_simple(
                            pixbuf.get_width() * scale_ratio, 
                            pixbuf.get_height() * scale_ratio,
                            2
                        )
        sample_parameters.set_displayed_pixbuf(scaled_pixbuf)

        # Delete Sample's cache of zoomed images
        if sample_id in self.__view.get_main_window().get_zoom_tool().get_cache().keys(): 
            del self.__view.get_main_window().get_zoom_tool().get_cache()[sample_id]

        # Update Canvas
        self.__view.get_main_window().get_canvas().update()

    '''
        In the Model, the sample is added with the given ID. In the View,
        the name is needed for the SamplesView (Gtk.Treeview) and the
        parameters are added to the ViewStore. Both have the associated ID and
        the item is added in the SamplesView at given position.
    '''
    def add_sample(self, sample, sample_parameters, pos=None):

        # Model
        self.__model.add_sample(sample)
        # View
        self.__add_sample_view(
            sample.get_id(), sample.get_name(), sample_parameters, pos)
            
    ''' 'add_sample' View behaviour. '''        
    def __add_sample_view(self, sample_id, sample_name, sample_parameters, pos):

        # Add to MainWindow's SamplesView   
        self.__view.get_main_window().get_samples_view().add_sample(
            sample_id, sample_name, pos)
        # Add to ViewStore
        self.__view.get_view_store().add(sample_id, sample_parameters)
        # Update SamplesView
        self.__view.get_main_window().get_samples_view().set_sample_number_of_comets(
                sample_id, len(self.__model.get_sample(sample_id).get_comet_list()), 
                self.__model.get_sample(sample_id).get_analyzed()
        )

    ''' Renames the sample with given ID with given name. '''
    def rename_sample(self, sample_id, sample_name):

        name = self.__model.get_store()[sample_id].get_name()
        
        # Model
        self.__model.rename_sample(sample_id, sample_name)
        # View
        self.__view.get_main_window().get_samples_view().rename_sample(
            sample_id, sample_name)

        return name

    ''' Deletes the sample with given ID. '''
    def delete_sample(self, sample_id):
    
        # Delete from Model
        sample_copy = self.__model.delete_sample(sample_id)
        # Delete from View
        (sample_parameters, pos) = self.__view.delete_sample(sample_id)
        
        if len(self.__model.get_store()) == 0:     
            self.__active_sample_id = None
        
        return (sample_copy, sample_parameters, pos)

    '''
        Creates and adds a new Comet with given contours to the Sample with
        given ID. 
    '''
    def add_new_comet(self, sample_id, tail_contour, head_contour):

        # Create new Comet
        comet = Comet(
                    self.__model.get_sample(sample_id), 
                    tail_contour, 
                    head_contour
                )
        # Add Comet
        self.add_comet(sample_id, comet)
        # Return its ID
        return comet.get_id()

    '''
        Adds given Comet to the Sample with given ID at the given position. 
    '''
    def add_comet(self, sample_id, comet, pos=None):

        # Model
        self.__model.get_sample(sample_id).add_comet(comet, pos)
        # View
        self.__add_comet_view(sample_id, comet.get_id(),
            comet.get_tail_contour(), comet.get_head_contour(), pos)
            
    ''' 'add_comet' View behaviour. '''        
    def __add_comet_view(self, sample_id, comet_id, tail_contour, head_contour, pos):        

        scale_value = self.get_sample_zoom_value(sample_id)
        
        # Scale tail contour
        scaled_tail_contour = None
        if tail_contour is not None:           
            scaled_tail_contour = utils.scale_contour(tail_contour, scale_value)
        # Scale head contour
        scaled_head_contour = utils.scale_contour(head_contour, scale_value)

        # Create and add CometView
        comet_view = CometView(comet_id, scaled_tail_contour, scaled_head_contour)
        sample_parameters = self.__view.get_view_store().get_store()[sample_id]
        sample_parameters.add_comet(comet_view, pos)

        # Update SamplesView
        self.__view.get_main_window().get_samples_view().set_sample_number_of_comets(
            sample_id, len(sample_parameters.get_comet_view_list()),
            self.__model.get_sample(sample_id).get_analyzed()
        ) 
        # Update Canvas
        self.__view.get_main_window().get_canvas().update()

    '''
        Deletes the comet with given ID that belongs to the sample with given
        ID.
    '''
    def delete_comet(self, sample_id, comet_id):

        # Model
        (comet_copy, pos) = self.__model.delete_comet(sample_id, comet_id)
        # View
        self.__delete_comet_view(sample_id, comet_id)
        return (comet_copy, pos)
        
    ''' 'delete_comet' View behaviour. '''   
    def __delete_comet_view(self, sample_id, comet_id):

        # Delete comet
        self.__view.get_view_store().get_store()[sample_id].delete_comet(comet_id)  
        # Update SamplesView
        self.__view.get_main_window().get_samples_view().set_sample_number_of_comets(
            sample_id, len(self.__model.get_sample(sample_id).get_comet_list()),
            self.__model.get_sample(sample_id).get_analyzed()
        )
        # Update Canvas
        self.__view.get_main_window().get_canvas().update()
        # Update SelectionWindow
        self.__view.get_main_window().get_selection_window().update()     

    '''
        Adds the tail contour to the Comet with given ID that belongs to the
        Sample with given ID.
    '''
    def add_comet_tail(self, sample_id, comet_id, tail_contour):
    
        # Model
        self.__add_comet_tail_model(sample_id, comet_id, tail_contour)
        # View
        self.__add_comet_tail_view(sample_id, comet_id, tail_contour)
        
    ''' 'add_comet_tail' Model behaviour. '''    
    def __add_comet_tail_model(self, sample_id, comet_id, tail_contour):    
        self.__model.get_sample(sample_id).get_comet(comet_id).\
            add_tail(tail_contour)
           
    ''' 'add_comet_tail' View behaviour. '''       
    def __add_comet_tail_view(self, sample_id, comet_id, tail_contour):        

        scale_value = self.get_sample_zoom_value(sample_id)

        comet_view = self.__view.get_view_store().get_comet_view(sample_id, comet_id)
        comet_view.set_scaled_tail_contour(
            utils.scale_contour(tail_contour, scale_value)
        )
                
        self.__view.get_main_window().get_canvas().update()
        self.__view.get_main_window().get_selection_window().update()
 
    '''
        Replaces the comet list of the given samples with the given comet
        lists.
    '''
    def update_samples_comet_list(self, samples_comet_lists):
            
        # Model
        data = self.__model.update_samples_comet_list(samples_comet_lists)
        # View
        self.__update_samples_comet_list_view(samples_comet_lists)
        return data
     
    ''' Updates the Comets of the Samples. '''
    def __update_samples_comet_list_view(self, samples_comet_lists):
    
        samples_comet_view_lists = []
        
        for (sample_id, comet_list, _) in samples_comet_lists:
            samples_comet_view_lists.append((
                sample_id,
                self.comet_list_to_comet_view_list(comet_list)
            ))
       
        for (sample_id, comet_view_list) in samples_comet_view_lists:    

            # Set new CometView list
            self.__view.get_view_store().get_store()[sample_id].set_comet_view_list(
                comet_view_list)
            # Set number of comets in SamplesView
            self.__view.get_main_window().get_samples_view().\
                set_sample_number_of_comets(sample_id, len(comet_view_list), 
                    self.__model.get_sample(sample_id).get_analyzed()
            )       
                        
        # Scale Comet contours according to Sample scale value activated
        scale_value = self.get_sample_zoom_value(self.__active_sample_id)
        self.scale_sample_comet_contours(self.__active_sample_id, scale_value)
        
        # Update View
        self.__view.get_main_window().get_canvas().update()
        self.__view.get_main_window().get_selection_window().update()

    ''' Returns the project filename. '''
    def get_project_filename(self):
        return self.__get_project_name()

    ''' Clear Undo & Redo stacks. '''
    def __clear_command_stacks(self):

        self.__undo_stack.clear()
        self.__redo_stack.clear()
        self.__view.set_undo_button_sensitivity(False)
        self.__view.set_redo_button_sensitivity(False)
        self.__update_undo_and_redo_buttons_tooltips()

    ''' Adds a command to the undo stack. '''
    def __add_command(self, command):

        # Add command        
        self.__undo_stack.append(command)
        # Reset redo stack
        self.__redo_stack.clear()
        # Set buttons sensitivity
        self.__view.set_undo_button_sensitivity(True)
        self.__view.set_redo_button_sensitivity(False)
        # Update tooltips
        self.__update_undo_and_redo_buttons_tooltips()
        # Update -> there are unsaved changes
        self.__update(True)
        
    ''' Updates Undo and Redo Buttons tooltips. '''    
    def __update_undo_and_redo_buttons_tooltips(self):
        self.__view.update_undo_and_redo_buttons_tooltips()

    ''' Updates the state and the main application window's title. '''
    def __update(self, value):
        self.__flag_unsaved_changes = value
        self.__view.set_application_window_title(
            self.__build_application_window_title())

    ''' Asks user to save changes before doing an specific action. '''
    def __ask_user_to_save_before_action(self, function):

        label = self.__strings.DIALOG_SAVE_BEFORE_ACTION_LABEL.format(
            self.__get_project_name())

        response_id = self.__view.run_save_before_action_dialog(
                          label)

        # User chose to save the project first
        if response_id == DialogResponse.ACCEPT:
            # If project is finally saved -> proceed to do action
            if self.save_project():                                          
                function()
        # User chose to discard the project -> proceed to action
        elif response_id == DialogResponse.DISCARD:
            function()

    ''' Builds and returns main application window title. '''
    def __build_application_window_title(self):
        title = ""
        if self.__flag_unsaved_changes:
            title += self.__UNSAVED_CHANGES_SYMBOL
        title += self.__get_project_name()
        title += self.__SEPARATOR + Model.APP_NAME

        return title

    ''' Creates a new project. '''
    def __new_project(self):
       
        self.__active_sample_id = None
       
        # New project
        self.__model.new_project()
        # Restart View
        self.__view.restart()
        # Current project is a 'new project'
        self.__flag_project_is_new = True
        # Update state & clear command stacks
        self.__update(False)
        self.__clear_command_stacks()   

    ''' Add new samples. '''
    def __add_new_samples(self, filepaths):

        # Prepare command
        command = commands.AddSamplesCommand(self)
        command.set_string(self.__strings.ADD_SAMPLES_COMMAND_STRING)
 
        # Add samples
        added_samples_ids = []
        i = 0
        while i < len(filepaths):

            # Get filename from full path
            filename = ntpath.basename(filepaths[i])

            # Update LoadSamplesWindow
            GLib.idle_add(self.__view.update_load_samples_window, filename,
                self.__strings.LOAD_SAMPLES_WINDOW_LABEL.format(i+1, len(filepaths)),
                i+1, len(filepaths))

            sample_name = get_valid_name(filename, self.__model.get_store())
            
            try:
            
                sample_image = utils.read_image(filepaths[i])[1]                    
                sample = Sample(sample_name, sample_image)
                sample_parameters = SampleParameters(utils.image_to_pixbuf(sample_image))
                GLib.idle_add(self.add_sample, sample, sample_parameters)
                added_samples_ids.append(sample.get_id())
                
            except Exception as err:
                print(err)
                print("ERROR: image " + filename + " couldn't be added.")
                
            i += 1
            
        if len(added_samples_ids) > 0:    
        
            # Add AddSamples command to the stack
            command.set_data(added_samples_ids)               
            self.__add_command(command)

        # Close LoadSamplesWindow
        GLib.idle_add(self.__view.close_load_samples_window)

    ''' Behaviour on the command stacks when project is saved. '''
    def __command_stacks_on_project_saved(self):

        for command in self.__undo_stack:
            command.set_flag_unsaved_changes(True)
        for command in self.__redo_stack:
            command.set_flag_unsaved_changes(True)

    ''' Parses a Comet list to a CometView list. '''
    def comet_list_to_comet_view_list(self, comet_list):

        comet_view_list = []
        for comet in comet_list:
            comet_view_list.append(self.__comet_to_comet_view(comet))
        return comet_view_list
        
    ''' Parses a Comet to a CometView '''
    def __comet_to_comet_view(self, comet):

        return CometView(comet.get_id(), comet.get_tail_contour(),
            comet.get_head_contour())    

    ''' Sets the analyzed flag value of the Sample with given ID. '''
    def set_sample_analyzed_flag(self, sample_id, analyzed):
        self.__model.get_sample(sample_id).set_analyzed(analyzed)
     
    ''' Returns the project name. '''
    def __get_project_name(self): 

        if self.__model.get_project_name() is None:
            return self.__strings.DEFAULT_PROJECT_NAME
        return self.__model.get_project_name()

    ''' Updates the comet that was being edited contours. '''
    def save_comet_being_edited_changes(self):
    
        # Only update contours if they are different from the original
        if CanvasModel.get_instance().get_comet_being_edited_has_changed():
        
            comet_id = self.__model.get_sample(
                self.__active_sample_id).get_comet_being_edited_id()
                
            tail_contour_dict = CanvasModel.get_instance().get_tail_contour_dict()
            head_contour_dict = CanvasModel.get_instance().get_head_contour_dict()

            # Remove comet if both contours are empty
            if len(tail_contour_dict) == 0 and len(head_contour_dict) == 0:           
                self.delete_comet_use_case(self.__active_sample_id, comet_id)          

            else:
                
                # The scale ratio
                scale_ratio = 1. / self.get_sample_zoom_value(self.__active_sample_id)
                
                # Build tail contour
                tail_contour = None
                for (_, canvas_contour) in tail_contour_dict.items():

                    # Scale the DelimiterPoint list to ratio 1. to save in the Model as about_use_case
                    # OpenCV contour
                    utils.scale_delimiter_point_list(
                        canvas_contour.get_delimiter_point_dict().values(), scale_ratio)
                    tail_contour = utils.list_to_contour(
                        [p.get_coordinates() for p in canvas_contour.get_delimiter_point_dict().values()]
                    )
                    
                # Build head contour
                head_contour = None
                for (_, canvas_contour) in head_contour_dict.items():

                    # Scale the DelimiterPoint list to ratio 1. to save in the Model as about_use_case
                    # OpenCV contour
                    utils.scale_delimiter_point_list(
                        canvas_contour.get_delimiter_point_dict().values(), scale_ratio)
                    head_contour = utils.list_to_contour(
                        [p.get_coordinates() for p in canvas_contour.get_delimiter_point_dict().values()]
                    )    
                
                # Update comet contours
                self.update_comet_contours_use_case(
                    self.__active_sample_id,
                    comet_id,
                    tail_contour,
                    head_contour
                )
            
        # No editing mode anymore
        self.quit_comet_being_edited()
        self.__view.get_main_window().get_canvas().update()

    ''' Updates the Comet contours with given contours. '''
    def update_comet_contours(self, sample_id, comet_id, tail_contour, head_contour):

        # Update contours in Model
        (old_tail_contour, old_head_contour) = self.set_comet_contours(
            sample_id, comet_id, tail_contour, head_contour)
           
        scale_ratio = self.get_sample_zoom_value(self.__active_sample_id)
        # Update contours in View
        scaled_tail_contour = None
        if tail_contour is not None:
            scaled_tail_contour = utils.scale_contour(tail_contour, scale_ratio)
        scaled_head_contour = utils.scale_contour(head_contour, scale_ratio)
        self.__view.get_view_store().set_comet_scaled_contours(
            sample_id, comet_id, scaled_tail_contour, scaled_head_contour)

        return (comet_id, old_tail_contour, old_head_contour)

    ''' Returns wether the comet being edited has changed or not. '''
    def get_comet_being_edited_has_changed(self):
        CanvasModel.get_instance().get_comet_being_edited_has_changed()

    ''' Sets wheter the comet being edited has changed or not. '''
    def set_comet_being_edited_has_changed(self, comet_being_edited_has_changed):
        CanvasModel.get_instance().\
            set_comet_being_edited_has_changed(comet_being_edited_has_changed)
        
    ''' Returns sample's tail contour dictionary with given ID. '''
    def get_sample_tail_contour_dict(self, sample_id=None):
    
        if sample_id is None:
            sample_id = self.__active_sample_id
        return self.__model.get_sample(sample_id).get_tail_contour_dict()
    
    ''' Returns sample's head contour dictionary with given ID. '''
    def get_sample_head_contour_dict(self, sample_id=None):
    
        if sample_id is None:
            sample_id = self.__active_sample_id
        return self.__model.get_sample(sample_id).get_head_contour_dict()

    ''' Returns sample's zoom model with given ID. '''
    def get_sample_zoom_model(self, sample_id):
        return self.__model.get_sample(sample_id).get_zoom_model()

    ''' Returns sample's zoom active index with given ID. '''
    def get_sample_zoom_index(self, sample_id):
        return self.__model.get_sample(sample_id).get_zoom_index()

    ''' Sets sample's zoom active index with given ID. '''
    def set_sample_zoom_index(self, sample_id, zoom_index):
        self.__model.get_sample(sample_id).set_zoom_index(zoom_index)
       
    ''' 
        Returns the AlgorithmSettings as a AlgorithmSettingsDto to the View.
    '''
    def get_algorithm_settings(self):
        return self.__algorithm_settings_to_algorithm_settings_dto(
            self.__model.get_algorithm_settings())
            
    '''
        Sets the Model AlgorithmSettings with given AlgorithmSettingsDto
        object.
    '''
    def set_algorithm_settings(self, algorithm_settings_dto):
    
        self.__model.get_algorithm_settings().set_algorithm_id(
            algorithm_settings_dto.get_algorithm_id())
        self.__model.get_algorithm_settings().set_fit_tail(
            algorithm_settings_dto.get_fit_tail())
        self.__model.get_algorithm_settings().set_fit_head(
            algorithm_settings_dto.get_fit_head())

    ''' Parses Model AlgorithmSettings to AlgorithmSettingsDto. '''
    def __algorithm_settings_to_algorithm_settings_dto(self, algorithm_settings):
        
        return AlgorithmSettingsDto(
                   algorithm_settings.get_algorithm_id(), 
                   algorithm_settings.get_fit_tail(),
                   algorithm_settings.get_fit_head()
               )
       
    ''' Activates Sample with given ID. '''   
    def activate_sample(self, sample_id=None):

        # If no sample_id is given, the sample_id used is the one that belongs
        # to the selected row from the SamplesView TreeView
        if sample_id is None:
            sample_id = self.__view.get_main_window().get_samples_view().get_sample_id(
                self.__view.get_main_window().get_samples_view().get_selected_sample_row())

        # Change the active sample 
        self.__active_sample_id = sample_id
        # Update CanvasModel contour dicts
        self.update_canvas_model_contours_dicts()
        # View behaviour on sample activated
        self.__view.on_sample_activated(sample_id)

    ''' 
        Scales the active Sample Comet contours and CanvasContours 
        DelimiterPoints.
    '''
    def scale_active_sample_comets(self, requested_scale_value):
        self.scale_sample_comets(self.__active_sample_id, requested_scale_value)
        
    ''' Scales the Comet contours and CanvasContours DelimiterPoints of Sample
        with given ID.
    '''    
    def scale_sample_comets(self, sample_id, requested_scale_ratio):    
    
        ''' TODO: escalar los cometas del modelo y sustituirlos en la Vista. '''
    
        # Scale Comets
        self.scale_sample_comet_contours(sample_id, requested_scale_ratio)
        
        # Scale 'Free Editing' and 'Comet being edited' CanvasContours
        self.scale_sample_canvas_contours(sample_id, requested_scale_ratio)
       
    ''' 
        Scales all Comet contours of Sample with given ID and creates
        their corresponding CometView objects.
    '''
    def scale_sample_comet_contours(self, sample_id, scale_ratio):
          
        sample = self.__model.get_sample(sample_id)

        comet_view_list = self.comet_list_to_comet_view_list(
                              sample.get_comet_list())
        
        # Scale Comets contours
        for comet_view in comet_view_list:

            # Scale the Comet tail contour
            if comet_view.get_scaled_tail_contour() is not None:
                tail_contour = comet_view.get_scaled_tail_contour()
                comet_view.set_scaled_tail_contour(
                    utils.scale_contour(
                        tail_contour,
                        scale_ratio
                    )
                )
                
            # Scale the head contour
            head_contour = comet_view.get_scaled_head_contour()
            comet_view.set_scaled_head_contour(              
                utils.scale_contour(
                    head_contour,
                    scale_ratio
                )
            )
            
        # Set new CometView list
        self.__view.get_view_store().get_store()[sample_id].set_comet_view_list(
            comet_view_list)
        
    ''' Scales all DelimiterPoints of Sample with given ID. '''
    def scale_sample_canvas_contours(self, sample_id, requested_scale_ratio):

        current_scale_ratio = self.get_sample_zoom_value(sample_id)
        final_scale_ratio = requested_scale_ratio / current_scale_ratio
        sample = self.__model.get_sample(sample_id)
                                
        # Scale 'Free editing' CanvasContours 
        utils.scale_canvas_contour_dict(
            sample.get_tail_contour_dict(),
            final_scale_ratio
        )
        utils.scale_canvas_contour_dict(
            sample.get_head_contour_dict(),
            final_scale_ratio
        )
        # Scale 'Comet being edited' CanvasContours
        utils.scale_canvas_contour_dict(
            sample.get_comet_being_edited_tail_contour_dict(),
            final_scale_ratio
        )
        utils.scale_canvas_contour_dict(
            sample.get_comet_being_edited_head_contour_dict(),
            final_scale_ratio
        )


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                               Canvas Methods                                #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #           
    
    ''' Adds the requested DelimiterPoint by the user. '''
    def add_requested_delimiter_point(self):
        CanvasModel.get_instance().add_requested_delimiter_point()
                         
    ''' Returns the Canvas 'editing' value. '''
    def get_editing(self):
        return self.__canvas_state.get_editing() 

    ''' Returns the active sample selected comet view. '''
    def get_active_sample_selected_comet_view(self):
    
        comet_id = self.get_active_sample_selected_comet_id()
        if comet_id is not None:
            return self.__get_sample_selected_comet_view(
                self.__active_sample_id, comet_id)
            
    ''' Returns the active sample selected comet identifier. '''
    def get_active_sample_selected_comet_id(self):
    
        if self.__active_sample_id is not None:
    
            return self.__model.get_sample(
                self.__active_sample_id).get_selected_comet_id()
     
    ''' Returns the active sample comet being edited identifier. '''
    def get_active_sample_comet_being_edited_id(self):

        if self.__active_sample_id is not None:
    
            return self.__model.get_sample(
                self.__active_sample_id).get_comet_being_edited_id()
                
    ''' Returns the active Sample tail_contour_dict. '''          
    def get_active_sample_tail_contour_dict(self):

        if self.__active_sample_id is not None:
            
            return self.__model.get_sample(
                self.__active_sample_id).get_tail_contour_dict()
         
    ''' Returns the active Sample head_contour_dict. '''      
    def get_active_sample_head_contour_dict(self):

        if self.__active_sample_id is not None:
            
            return self.__model.get_sample(
                self.__active_sample_id).get_head_contour_dict()           
            
    ''' Returns the Brush object. '''
    def get_brush(self):
        return self.__view.get_main_window().get_canvas().get_brush()

    ''' Returns the color for drawing Tail contours. '''
    def get_tail_color(self):
        return CanvasModel.get_instance().get_tail_color()
        
    ''' Returns the color for drawing Head contours. '''  
    def get_head_color(self):
        return CanvasModel.get_instance().get_head_color()
        
    ''' Returns the 'build tail contour' Button. '''    
    def get_build_tail_contour_button(self):
        return self.__view.get_main_window().get_canvas().get_build_tail_contour_button()
        
    ''' Returns the 'build head contour' Button. '''     
    def get_build_head_contour_button(self):
        return self.__view.get_main_window().get_canvas().get_build_head_contour_button()
     
    ''' Returns the sample's comet being edited identifier with given ID. ''' 
    def get_sample_comet_being_edited_id(self, sample_id):
        return self.__model.get_sample(sample_id).get_comet_being_edited_id()    
        
    ''' Behaviour when the user builds a valid comet. '''
    def on_add_comet(self, tail_contour, head_contour):

        # Contours are parsed to ratio 1.
        scale_ratio = 1. / self.get_sample_zoom_value(self.__active_sample_id)

        # [1] Build Tail contour
        if tail_contour is not None:

            # Parse to opencv contour
            coordinates_list = [point.get_coordinates() for point in
                                tail_contour.get_delimiter_point_dict().values()]
            tail_contour = utils.scale_contour(
                               utils.list_to_contour(coordinates_list),
                               scale_ratio
                           )

        # [2] Build Head contour                
        # Parse to opencv contour
        coordinates_list = [point.get_coordinates() for point in
                            head_contour.get_delimiter_point_dict().values()]           
        head_contour = utils.scale_contour(
                           utils.list_to_contour(coordinates_list),
                           scale_ratio
                       )
                           
        # Merge contours
        if tail_contour is not None:
            tail_contour = utils.merge_contours(tail_contour, head_contour) 

        return self.add_new_comet_use_case(
            self.__active_sample_id, tail_contour, head_contour)
            
                
    ''' Selects comet from Sample with given ID. '''
    def select_comet(self, sample_id, comet_id):  

        # Select comet
        self.__model.select_comet(sample_id, comet_id)
        # Update View
        self.__view.get_main_window().get_canvas().update()
        self.__view.get_main_window().get_selection_window().update()
        
    ''' 
        Returns the Comet's number of Comet with given ID of Sample with given ID.
    '''
    def get_comet_number(self, sample_id, comet_id):
        return self.__model.get_comet_number(sample_id, comet_id)
  
    '''
        Prepares the Canvas configuration so the user can edit an existent
        Comet manually.
    '''            
    def start_comet_being_edited(self, sample_id, comet_id, tail_canvas_contour_dict=None, head_canvas_contour_dict=None):

        # Preamble
        if not BuildingTailContourState.get_instance():
            BuildingTailContourState(self)
        if not BuildingHeadContourState.get_instance():
            BuildingHeadContourState(self)

        # Set Sample comet_being_edited_id
        self.__model.get_sample(sample_id).set_comet_being_edited_id(comet_id)

        # If no CanvasContours dictionaries are provided, use OpenCV contours instead
        if tail_canvas_contour_dict is None and head_canvas_contour_dict is None:

            # Get the original contours
            comet = self.__model.get_sample(sample_id).get_comet(comet_id)
            # Load the OpenCV contours into CanvasModel        
            CanvasModel.get_instance().prepare_comet_for_editing(
                comet.get_tail_contour(), comet.get_head_contour())
                  
            # Scale the CanvasContours
            utils.scale_canvas_contour_dict(
                CanvasModel.get_instance().get_tail_contour_dict(),
                self.get_sample_zoom_value(sample_id)
            )
            utils.scale_canvas_contour_dict(
                CanvasModel.get_instance().get_head_contour_dict(),
                self.get_sample_zoom_value(sample_id)
            )    
         
        # If CanvasContours dictionaries are provided, use them directly
        else:
        
            CanvasModel.get_instance().set_tail_contour_dict(
                tail_canvas_contour_dict)
            CanvasModel.get_instance().set_head_contour_dict(
                head_canvas_contour_dict)
                
        # Activate Editing state with 'Edit contours' mode.   
        self.__view.get_main_window().get_canvas().get_editing_button().set_active(True)
        self.__view.get_main_window().get_canvas().get_editing_selection_button().set_active(True)
            
        # Make SelectionWindow 'Save' button active
        self.__view.get_main_window().get_selection_window().get_save_button()\
            .set_sensitive(True)
            
        self.__model.get_sample(sample_id).set_comet_being_edited_tail_contour_dict(
            CanvasModel.get_instance().get_tail_contour_dict())
        self.__model.get_sample(sample_id).set_comet_being_edited_head_contour_dict(
            CanvasModel.get_instance().get_head_contour_dict())
                   
    ''' Returns the Sample zoom value with given ID. '''
    def get_sample_zoom_value(self, sample_id):  
    
        return self.get_sample_zoom_model(sample_id)[
            self.get_sample_zoom_index(sample_id)]

    ''' Returns the selected CometView of Sample with given ID. '''
    def __get_sample_selected_comet_view(self, sample_id, comet_id):
        return self.__view.get_view_store().get_comet_view(sample_id, comet_id)            
            
    ''' Behaviour for a Comet to stop being edited. '''        
    def quit_comet_being_edited(self):
    
        # Start SelectionState
        self.__view.get_main_window().get_canvas().get_selection_button().set_active(True)
        
        sample = self.__model.get_sample(self.__active_sample_id)
        # Set to None the Sample's Comet ID being edited
        sample.set_comet_being_edited_id(None)       
        # Activate on CanvasModel Sample's 'free editing' contours dicts
        CanvasModel.get_instance().set_tail_contour_dict(
            sample.get_tail_contour_dict())
        CanvasModel.get_instance().set_head_contour_dict(
            sample.get_head_contour_dict())
        
    ''' Deletes selected comet. '''    
    def delete_selected_comet(self):

        comet_id = self.__model.get_sample(
            self.__active_sample_id).get_selected_comet_id()
        
        self.delete_comet_use_case(self.__active_sample_id, comet_id)
        
    ''' Updates the CanvasModel contours dictionaries. '''   
    def update_canvas_model_contours_dicts(self):
    
        sample = self.__model.get_sample(self.__active_sample_id)
    
        # If a comet is being edited     
        if sample.get_comet_being_edited_id() is not None:
        
            tail_contour_dict = sample.\
                                    get_comet_being_edited_tail_contour_dict()
            head_contour_dict = sample.\
                                    get_comet_being_edited_head_contour_dict()
            
        # Free editing
        else:

            tail_contour_dict = sample.get_tail_contour_dict()
            head_contour_dict = sample.get_head_contour_dict()

        # Set CanvasModel contour dicts
        CanvasModel.get_instance().set_tail_contour_dict(tail_contour_dict)
        CanvasModel.get_instance().set_head_contour_dict(head_contour_dict)
   


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              Canvas Callbacks                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' On Canvas key press event method. '''
    def on_canvas_key_press_event(self, event):
        self.__canvas_state.on_key_press_event(event)

    ''' On Canvas mouse enter callback method. '''
    def on_canvas_mouse_enter(self):
        self.__canvas_state.on_mouse_enter()

    ''' On Canvas mouse leave callback method. '''
    def on_canvas_mouse_leave(self):
        self.__canvas_state.on_mouse_leave()

    ''' On Canvas mouse release callback method. '''
    def on_canvas_mouse_release(self, event):
        self.__canvas_state.on_mouse_release(event)      

    ''' On Canvas mouse click callback method. '''
    def on_canvas_mouse_click(self, event):      
        self.__canvas_state.on_mouse_click(event)

    ''' On Canvas mouse motion callback method. '''
    def on_canvas_mouse_motion(self, event):
        self.__canvas_state.on_mouse_motion(event)
       
    ''' On Canvas draw callback method. '''
    def draw(self, cairo_context):
        self.__canvas_state.draw(cairo_context)
        
        
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                           Canvas Transition methods                         #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
        
    ''' Canvas state transition to CanvasSelectionState. '''
    def canvas_transition_to_selection_state(self):
    
        canvas = self.__view.get_main_window().get_canvas()
        canvas.get_selection_button().set_active(True)
        canvas.hide_editing_buttons()
        self.__canvas_state = CanvasSelectionState(self) 
        canvas.update()
        self.__view.get_main_window().get_selection_window().update()
        

    ''' Canvas state transition to CanvasEditingState. '''
    def canvas_transition_to_editing_state(self):
    
        canvas = self.__view.get_main_window().get_canvas()
        canvas.get_editing_button().set_active(True)
        canvas.show_editing_buttons()    
        self.__canvas_state = CanvasEditingState(self)
        canvas.update()
        self.__view.get_main_window().get_selection_window().update()
        
    ''' Canvas EditingState state transition to EditingSelectionState. '''
    def canvas_transition_to_editing_selection_state(self):

        self.__canvas_state.transition_to_editing_selection_state(self)
        canvas = self.__view.get_main_window().get_canvas()
        canvas.set_build_contour_buttons_sensitivity(False)
        canvas.update()

    ''' Canvas EditingState state transition to EditingBuildingState. '''
    def canvas_transition_to_editing_building_state(self):
    
        self.__canvas_state.transition_to_editing_building_state(self)
        canvas = self.__view.get_main_window().get_canvas()
        canvas.set_build_contour_buttons_sensitivity(True)
        canvas.update()

    ''' Canvas EditingBuildingState state transition to BuildingTailContourState. '''
    def canvas_transition_to_building_tail_contour_state(self):
        self.__canvas_state.transition_to_building_tail_contour_state(self)
        self.__view.get_main_window().get_canvas().update()

    ''' Canvas EditingBuildingState state transition to BuildingHeadContourState. '''
    def canvas_transition_to_building_head_contour_state(self):
        self.__canvas_state.transition_to_building_head_contour_state(self)
        self.__view.get_main_window().get_canvas().update()


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              Getters & Setters                              #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_active_sample_id(self):
        return self.__active_sample_id
        
    def set_active_sample_id(self, active_sample_id):
        self.__active_sample_id = active_sample_id

    def get_strings(self):
        return self.__strings
       
    def set_strings(self, strings):
        self.__strings = strings

    def get_flag_unsaved_changes(self):
        return self.__flag_unsaved_changes

    def set_flag_unsaved_changes(self, flag_unsaved_changes):
        self.__flag_unsaved_changes = flag_unsaved_changes

    def get_flag_project_is_new(self):
        return self.__flag_project_is_new

    def set_flag_project_is_new(self, flag_project_is_new):
        self.__flag_project_is_new = flag_project_is_new

    def get_view(self):
        return self.__view
        
    def set_view(self, view):
        self.__view = view

    def get_model(self):
        return self.__model
        
    def set_model(self, model):
        self.__model = model
        
    def get_canvas_state(self):
        return self.__canvas_state
        
    def set_canvas_state(self, canvas_state):
        self.__canvas_state = canvas_state
        
        

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
# ~                         Module Auxiliar Methods                         ~ # 
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

''' If name already exists in the Model, another name is created. '''
def get_valid_name(text, store):

    name = text
    n = 1
    while __is_name_in_use(name, store):
        name = text + "(" + str(n) + ")"
        n += 1

    return name

''' Returns whether a name is already in use by an existent Sample
    in the Model.    
''' 
def __is_name_in_use(name, store):
     
    for sample in store.values():
        if sample.get_name() == name:
            return True
    return False 


