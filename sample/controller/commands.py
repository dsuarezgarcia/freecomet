# -*- encoding: utf-8 -*-

'''
    The commands module.
'''

# General Imports
import model.utils as utils

from model.canvas_model import CanvasModel, SelectedDelimiterPoint



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	Command                                                                   #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class Command(object):

    '''
        The Command abstract class. Specific Commands inherit from this class.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
    
        # Protected Attributes
        self._controller = controller
        self._data = None 

        # Private Attributes
        self.__flag_unsaved_changes = controller.get_flag_unsaved_changes()
        self.__string = ""


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                   Methods                                   #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Execute Command method. '''
    def execute(self, *args):
        raise NotImplementedError("This method must be implemented.")

    ''' Undo Command method. '''
    def undo(self, *args):
        raise NotImplementedError("This method must be implemented.")
        

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_flag_unsaved_changes(self):
        return self.__flag_unsaved_changes

    def set_flag_unsaved_changes(self, flag_unsaved_changes):
        self.__flag_unsaved_changes = flag_unsaved_changes

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data
           
    def get_string(self):
        return self.__string
        
    def set_string(self, string):
        self.__string = string

    

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   AddSamplesCommand                                                         #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
   
class AddSamplesCommand(Command):

    '''
        The AddSamplesCommand class. Extends from Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):

        # Retrieve data
        data = self.get_data()
      
        new_data = []
        # Redo execution
        while len(data) > 0:

            (sample, parameters) = data.pop()
            # Add sample
            self._controller.add_sample(sample, parameters)
            new_data.append(sample.get_id())

        # Save data        
        self.set_data(new_data)

    ''' Command.undo() behaviour. '''
    def undo(self):

        # Retrieve data
        data = self.get_data()

        new_data = []
        # Undo execution
        for sample_id in data:

            # Delete sample
            (sample_copy, parameters, _) = self._controller.\
                                               delete_sample(sample_id)
            new_data.append((sample_copy, parameters))
            
        new_data.reverse()

        # Save data       
        self.set_data(new_data)



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   DeleteSampleCommand                                                       #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
   
class DeleteSampleCommand(Command):

    '''
        The DeleteSample class. Extends from Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):

        # Retrieve data
        sample_id = self.get_data()
        
        # Delete sample
        (sample_copy, parameters, pos) = self._controller.delete_sample(sample_id)
        
        # Save data
        self.set_data((sample_copy, parameters, pos))

    ''' Command.undo() behaviour. '''
    def undo(self):

        # Retrieve data
        (sample, parameters, pos) = self.get_data()
        
        # Add sample
        self._controller.add_sample(sample, parameters, pos)
        
        # Save data
        self.set_data(sample.get_id())
    


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   RenameSampleCommand                                                       #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
  
class RenameSampleCommand(Command):

    '''
        The RenameSampleCommand class. Extends from Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):
        self.__rename()

    ''' Command.undo() behaviour. '''
    def undo(self):
        self.__rename()

    ''' Renames Sample's name with given ID. '''
    def __rename(self):

        # Retrieve data   
        (sample_id, sample_name) = self.get_data()
        
        # Rename Sample
        previous_name = self._controller.rename_sample(
                            sample_id, sample_name)
                            
        # Save data
        self.set_data((sample_id, previous_name))



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   AddCometCommand                                                           #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class AddCometCommand(Command):

    '''
        The AddComet class. Extends from Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):

        # Retrieve data
        (sample_id, comet, pos) = self.get_data() 
        
        # Add comet
        self._controller.add_comet(sample_id, comet, pos)
        # Activate Sample
        if self._controller.get_active_sample_id() != sample_id:
            self._controller.activate_sample(sample_id)
            
        # Save data
        self.set_data((sample_id, comet.get_id(), 
            self._controller.get_model().get_sample(sample_id).get_analyzed()))

    ''' Command.undo() behaviour. '''
    def undo(self):

        # Retrieve data
        (sample_id, comet_id, analyzed_flag) = self.get_data()  
        
        # Delete comet
        (comet_copy, pos) = self._controller.delete_comet(
                                sample_id, comet_id)
        # Activate Sample
        if self._controller.get_active_sample_id() != sample_id:
            self._controller.activate_sample(sample_id)                        
        # Set analyzed flag
        self._controller.set_sample_analyzed_flag(
            sample_id, analyzed_flag)
            
        # Save data
        self.set_data((sample_id, comet_copy, pos))



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   DeleteCometCommand                                                        #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class DeleteCometCommand(Command):

    '''
        The DeleteCometCommand class. Extends from Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):

        # Retrieve data
        (sample_id, comet_id) = self.get_data()
        
        # Delete comet
        (comet_copy, pos) = self._controller.delete_comet(
                                sample_id, comet_id)
        # Activate Sample
        if self._controller.get_active_sample_id() != sample_id:
            self._controller.activate_sample(sample_id)
            
        # Save data
        self.set_data((sample_id, comet_copy, pos))

    ''' Command.undo() behaviour. '''
    def undo(self):

        # Retrieve data
        (sample_id, comet, pos) = self.get_data()
        
        # Add comet
        self._controller.add_comet(sample_id, comet, pos)        
        # Activate Sample
        if self._controller.get_active_sample_id() != sample_id:
            self._controller.activate_sample(sample_id)
        # Select comet
        self._controller.select_comet(sample_id, comet.get_id())
        
        # Save data
        self.set_data((sample_id, comet.get_id()))



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   RemoveCometTailCommand                                                    #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class RemoveCometTailCommand(Command):

    '''
        The RemoveCometTailCommand class. Extends from Command. 
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):

        # Retrieve data
        (sample_id, comet_id) = self.get_data()
        
        # Remove comet tail
        comet_contour = self._controller.remove_comet_tail(
                            sample_id, comet_id)                           
        # Activate Sample
        if self._controller.get_active_sample_id() != sample_id:
            self._controller.activate_sample(sample_id)        
        # Select comet
        self._controller.select_comet(sample_id, comet_id)                    
                            
        # Save data
        self.set_data((sample_id, comet_id, comet_contour))

    ''' Command.undo() behaviour. '''
    def undo(self):

        # Retrieve data
        (sample_id, comet_id, comet_contour) = self.get_data()
        # Add comet tail
        self._controller.add_comet_tail(
            sample_id, comet_id, comet_contour)

        # Activate Sample
        if self._controller.get_active_sample_id() != sample_id:
            self._controller.activate_sample(sample_id)        
        # Select comet
        self._controller.select_comet(sample_id, comet_id)
        
        # Save data
        self.set_data((sample_id, comet_id))



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   AnalyzeSamplesCommand                                                     #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class AnalyzeSamplesCommand(Command):

    '''
        The AnalyzeSamplesCommand class. Extends from Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)
   
    ''' Command.execute() behaviour. '''
    def execute(self):
        self.__update_samples_comet_list()
    
    ''' Command.undo() behaviour. '''
    def undo(self):
        self.__update_samples_comet_list()

    ''' Updates the Comets for a Sample. '''
    def __update_samples_comet_list(self):

        # Retrieve data
        data = self.get_data()
        # Replace sample's comet lists
        new_data = self._controller.update_samples_comet_list(data)
        # Save data
        self.set_data(new_data)



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   FlipSampleImageCommand                                                    #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class FlipSampleImageCommand(Command):

    '''
        The FlipSampleImageCommand class. Extends from Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)
    
    ''' Command.execute() behaviour. '''
    def execute(self):
        self._controller.flip_sample_image(self.get_data())
        
    ''' Command.undo() behaviour. '''    
    def undo(self):
        self._controller.flip_sample_image(self.get_data())



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   InvertSampleImageCommand                                                  #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class InvertSampleImageCommand(Command):

    '''
        The InvertSampleImage class. Extends from Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)
    
    ''' Command.execute() behaviour. '''
    def execute(self):
        self._controller.invert_sample_image(self.get_data())
        
    ''' Command.undo() behaviour. '''    
    def undo(self):
        self._controller.invert_sample_image(self.get_data())



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   EditCometContoursCommand                                                  #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class EditCometContoursCommand(Command):

    '''
        The EditCometContoursCommand class. Extends from Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):
    
        # Retrieve data
        (sample_id, comet_id, 
         tail_canvas_contour_dict,
         head_canvas_contour_dict) = self.get_data()
    
        # Activate Sample
        self._controller.activate_sample(sample_id)       
        # Select Comet
        self._controller.select_comet(sample_id, comet_id)
        
        # Update Comet as being edited
        self._controller.start_comet_being_edited(
            sample_id, comet_id,
            tail_canvas_contour_dict,
            head_canvas_contour_dict
        )

    ''' Command.undo() behaviour. '''
    def undo(self):

        # Retrieve data
        (sample_id, comet_id, _, _) = self.get_data()
        
        # Activate Sample
        self._controller.activate_sample(sample_id)
        # Select Comet
        self._controller.select_comet(sample_id, comet_id)
        
        # Update Comet as not being edited
        self._controller.quit_comet_being_edited()

 
 
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   CancelEditCometContoursCommand                                            #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class CancelEditCometContoursCommand(Command):

    '''
        The CancelEditCometContoursCommand class. Extends from Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):
    
        # Retrieve data
        sample_id = self.get_data()[0] 
        
        # Activate Sample
        if self._controller.get_active_sample_id() != sample_id:
            self._controller.activate_sample(sample_id)
        
        # Quit Comet being edited
        self._controller.quit_comet_being_edited()

    ''' Command.undo() behaviour. '''
    def undo(self):
          
        # Retrieve data
        (sample_id, comet_id, 
         tail_canvas_contour_dict,
         head_canvas_contour_dict) = self.get_data()
         
        # Activate Sample
        if self._controller.get_active_sample_id() != sample_id:
            self._controller.activate_sample(sample_id) 
        
        # Start Comet being edited  
        self._controller.start_comet_being_edited(
            sample_id, comet_id,
            tail_canvas_contour_dict,
            head_canvas_contour_dict
        )
        


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   UpdateCometContoursCommand                                                #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class UpdateCometContoursCommand(Command):

    '''
        The UpdateCometContoursCommand class. Extends from Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):                          
        
        # Retrieve data
        (sample_id, comet_id, tail_contour, head_contour,
         tail_canvas_contour_dict,
         head_canvas_contour_dict) = self.get_data()
        
        # Activate Sample
        if self._controller.get_active_sample_id() != sample_id:
            self._controller.activate_sample(sample_id)
         
        # Quit Comet being edited
        self._controller.quit_comet_being_edited()

        # Update Comet contours
        (_, 
         previous_tail_contour,
         previous_head_contour) = self._controller.update_comet_contours(
                                      sample_id, comet_id, tail_contour, head_contour)
        
        # Save data
        self.set_data(
            (sample_id, comet_id, previous_tail_contour, 
             previous_head_contour, tail_canvas_contour_dict,
             head_canvas_contour_dict)
        )
         

    ''' Command.undo() behaviour. '''
    def undo(self):
    
        # Retrieve data
        (sample_id, comet_id, tail_contour, head_contour,
         tail_canvas_contour_dict,
         head_canvas_contour_dict) = self.get_data()
         
        # Activate Sample
        if self._controller.get_active_sample_id() != sample_id:
            self._controller.activate_sample(sample_id) 
         
        # Start Comet being edited  
        self._controller.start_comet_being_edited(
            sample_id, comet_id,
            tail_canvas_contour_dict,
            head_canvas_contour_dict
        )
        
        # Update Comet contours
        (comet_id, 
         previous_tail_contour,
         previous_head_contour) = self._controller.update_comet_contours(
                                      sample_id, comet_id, tail_contour, head_contour)
        
        # Save data
        self.set_data(
            (sample_id, comet_id, previous_tail_contour, 
             previous_head_contour, tail_canvas_contour_dict,
             head_canvas_contour_dict)
        )

      

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   CreateDelimiterPointCommand                                               #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class CreateDelimiterPointCommand(Command):

    '''
        The CreateDelimiterPointCommand class. Extends from Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):
            
        # Activate Sample if needed
        if self._controller.get_active_sample_id() != self._data.get_sample_id():
            self._controller.activate_sample(self._data.get_sample_id())

        # Transition to CanvasEditingState       
        self._controller.canvas_transition_to_editing_state()

        # Scale DelimiterPoint coordfinates if needed
        current_scale_ratio = self._controller.get_sample_zoom_value(
            self._data.get_sample_id())
        if self._data.get_scale_ratio() != current_scale_ratio:
        
            # Scale and set coordinates
            self._data.set_coordinates(
                utils.scale_point(
                    self._data.get_coordinates(),
                    current_scale_ratio / scale_ratio
                )
            )
            self._data.set_scale_ratio(current_scale_ratio)
           
        # 'Create DelimiterPoint'   
        if self._data.get_root_delimiter_point_id() is None:     
             
            # Create DelimiterPoint
            delimiter_point = self._controller.create_delimiter_point(
                self._data.get_creation_method(),
                self._data.get_coordinates(),
                self._data.get_delimiter_point_id(),
                self._data.get_canvas_contour_id()
            ) 
          
        # 'Create and connect DelimiterPoint'
        else:
        
            root_delimiter_point = CanvasModel.get_instance().get_delimiter_point(
                self._data.get_root_delimiter_point_id(),
                self._data.get_delimiter_point_type(),
                self._data.get_canvas_contour_id()
            )
            
            # Create and connect DelimiterPoint
            delimiter_point = self._controller.create_and_connect_delimiter_point(
                self._data.get_creation_method(),
                root_delimiter_point,
                self._data.get_coordinates(),
                self._data.get_delimiter_point_id()
            ) 
                    
        # Update Canvas
        self._controller.get_view().get_main_window().get_canvas().update()
        
        #CanvasModel.get_instance().debug()
  
    ''' Command.undo() behaviour. '''
    def undo(self):

        # Activate Sample if needed
        if self._controller.get_active_sample_id() != self._data.get_sample_id():
            self._controller.activate_sample(self._data.get_sample_id())

        # Transition to CanvasEditingState       
        self._controller.canvas_transition_to_editing_state()
        
        # Delete DelimiterPoint
        selected_delimiter_point = SelectedDelimiterPoint(
            self._data.get_delimiter_point_id(),
            self._data.get_delimiter_point_type(),
            self._data.get_canvas_contour_id()
        )
        selected_delimiter_point.set_origin(self._data.get_coordinates())             
        self._controller.delete_delimiter_points([selected_delimiter_point])
       
        # Update Canvas
        self._controller.get_view().get_main_window().get_canvas().update()
        
        #CanvasModel.get_instance().debug()
        
        
        
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   CreateDelimiterPointCommandData                                           #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class CreateDelimiterPointCommandData(object):

    '''
        The CreateDelimiterPointCommandData class.
    '''

    ''' Initialization method. '''
    def __init__(self, sample_id, delimiter_point_id, delimiter_point_type,
            canvas_contour_id, coordinates, creation_method, scale_ratio):
        
        self.__sample_id = sample_id
        self.__delimiter_point_id = delimiter_point_id
        self.__delimiter_point_type = delimiter_point_type
        self.__canvas_contour_id = canvas_contour_id
        self.__coordinates = coordinates      
        self.__creation_method = creation_method
        self.__scale_ratio = scale_ratio
        self.__root_delimiter_point_id = None

        
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #   
   
    def get_sample_id(self):
        return self.__sample_id
        
    def set_sample_id(self, sample_id):
        self.__sample_id = sample_id
        
    def get_delimiter_point_id(self):
        return self.__delimiter_point_id
        
    def set_delimiter_point_id(self, delimiter_point_id):
        self.__delimiter_point_id = delimiter_point_id
        
    def get_delimiter_point_type(self):
        return self.__delimiter_point_type
        
    def set_delimiter_point_type(self, delimiter_point_type):
        self.__delimiter_point_type = delimiter_point_type
        
    def get_canvas_contour_id(self):
        return self.__canvas_contour_id
        
    def set_canvas_contour_id(self, canvas_contour_id):
        self.__canvas_contour_id = canvas_contour_id
        
    def get_coordinates(self):
        return self.__coordinates
        
    def set_coordinates(self, coordinates):
        self.__coordinates = coordinates
        
    def get_creation_method(self):
        return self.__creation_method
        
    def set_creation_method(self, creation_method):
        self.__creation_method = creation_method
        
    def get_scale_ratio(self):
        return self.__scale_ratio
        
    def set_scale_ratio(self, scale_ratio):
        self.__scale_ratio = scale_ratio
        
    def get_root_delimiter_point_id(self):
        return self.__root_delimiter_point_id
        
    def set_root_delimiter_point_id(self, root_delimiter_point_id):
        self.__root_delimiter_point_id = root_delimiter_point_id



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   MoveDelimiterPointsCommand                                                #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 
        
class MoveDelimiterPointsCommand(Command):

    '''
        The MoveDelimiterPointsCommand class. Extends from Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)
    
    ''' Command.execute() behaviour. '''
    def execute(self):
        self.__move_delimiter_points()
        
    ''' Command.undo() behaviour. '''
    def undo(self):
        self.__move_delimiter_points()
        
    ''' Moves the DelimiterPoints to its origin. '''    
    def __move_delimiter_points(self): 

        # Retrieve data
        (sample_id, delimiter_point_selection, scale_ratio) = self.get_data()
        
        # Activate Sample
        if self._controller.get_active_sample_id() != sample_id:
            self._controller.activate_sample(sample_id)
            
        # Transition to CanvasEditingState       
        self._controller.canvas_transition_to_editing_state()
        
        # Move points to origin coordinates
        new_scale_ratio = self._controller.move_delimiter_points_to_origin(
            delimiter_point_selection, scale_ratio)
            
        # Save data
        self.set_data((sample_id, delimiter_point_selection, new_scale_ratio))

