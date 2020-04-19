# -*- encoding: utf-8 -*-

'''
    The commands module.
'''

# General imports
import copy

# Custom imports
import sample.model.utils as utils
from sample.model.canvas_model import CanvasModel, SelectedDelimiterPoint



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
        The AddSamplesCommand class. Extends Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):
      
        new_data = []
        # Redo execution
        while len(self._data) > 0:

            (sample, parameters) = self._data.pop()
            # Add sample
            self._controller.add_sample(sample, parameters)
            new_data.append(sample.get_id())

        # Save data        
        self._data = new_data

    ''' Command.undo() behaviour. '''
    def undo(self):

        new_data = []
        # Undo execution
        for sample_id in self._data:

            # Delete sample
            (sample_copy, parameters, _) = self._controller.\
                                               delete_sample(sample_id)
            new_data.append((sample_copy, parameters))
            
        new_data.reverse()
          
        # Save data       
        self._data = new_data



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   DeleteSampleCommand                                                       #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
   
class DeleteSampleCommand(Command):

    '''
        The DeleteSample class. Extends Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):

        # Retrieve data
        sample_id = self._data
        
        # Delete sample
        (sample_copy, parameters, pos) = self._controller.delete_sample(
                                             sample_id)
        
        # Save data
        self._data = (sample_copy, parameters, pos)

    ''' Command.undo() behaviour. '''
    def undo(self):

        # Retrieve data
        (sample, parameters, pos) = self._data
        
        # Add sample
        self._controller.add_sample(sample, parameters, pos)
        
        # Save data
        self._data = sample.get_id()
    


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   RenameSampleCommand                                                       #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
  
class RenameSampleCommand(Command):

    '''
        The RenameSampleCommand class. Extends Command.
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
        (sample_id, sample_name) = self._data
        
        # Rename Sample
        previous_name = self._controller.rename_sample(
                            sample_id, sample_name)
                            
        # Save data
        self._data = (sample_id, previous_name)



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   AddCometCommand                                                           #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class AddCometCommand(Command):

    '''
        The AddCometCommand class. Extends Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):
        
        # Activate Sample
        if self._controller.get_active_sample_id() != self._data.get_sample_id():
            self._controller.activate_sample(self._data.get_sample_id())
        
        # Transition to CanvasSelectionState       
        self._controller.canvas_transition_to_selection_state() 
        
        # Add comet
        self._controller.add_comet(
            self._data.get_sample_id(),
            self._data.get_comet_copy(),
            self._data.get_pos()
        )
        
        # Remove the Tail CanvasContour from the CanvasContour dictionary
        if self._data.get_tail_canvas_contour() is not None:
            del CanvasModel.get_instance().get_tail_contour_dict()[
                self._data.get_tail_canvas_contour().get_id()]      
          
        # Remove the Head CanvasContour from the CanvasContour dictionary
        del CanvasModel.get_instance().get_head_contour_dict()[
            self._data.get_head_canvas_contour().get_id()]

    ''' Command.undo() behaviour. '''
    def undo(self):

        # Delete Comet
        (comet_copy, pos) = self._controller.delete_comet(
                                self._data.get_sample_id(), 
                                self._data.get_comet_id()
                            )

        # Activate Sample
        if self._controller.get_active_sample_id() != self._data.get_sample_id():
            self._controller.activate_sample(self._data.get_sample_id())
            
        # Transition to CanvasEditingState       
        self._controller.canvas_transition_to_editing_state()    
                              
        # Set analyzed flag
        self._controller.set_sample_analyzed_flag(
            self._data.get_sample_id(), self._data.get_analyzed_flag())
         
        current_scale_ratio = self._controller.get_sample_zoom_value(
            self._data.get_sample_id())
        scale = self._data.get_scale_ratio() != current_scale_ratio
                             
        # Add the previous Tail CanvasContour (before the comet was built)
        if self._data.get_tail_canvas_contour() is not None:
        
            # If scaling is needed
            if scale:
                      
                utils.scale_canvas_contour(
                    self._data.get_tail_canvas_contour(),
                    current_scale_ratio / self._data.get_scale_ratio()
                )
        
            CanvasModel.get_instance().get_tail_contour_dict()[
                self._data.get_tail_canvas_contour().get_id()] = \
                    copy.deepcopy(self._data.get_tail_canvas_contour())     
          
        # If scaling is needed
        if scale:
                  
            utils.scale_canvas_contour(
                self._data.get_head_canvas_contour(),
                current_scale_ratio / self._data.get_scale_ratio()
            )  
          
        # Add the previous Head CanvasContour (before the comet was built)  
        CanvasModel.get_instance().get_head_contour_dict()[
            self._data.get_head_canvas_contour().get_id()] = \
                copy.deepcopy(self._data.get_head_canvas_contour())
                   
        # Save data
        self._data.set_comet_copy(comet_copy)
        self._data.set_pos(pos)
        self._data.set_scale_ratio(current_scale_ratio)
        


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   AddCometCommandData                                                       #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class AddCometCommandData(object):

    '''
        The AddCometCommandData class.
    '''

    ''' Initialization method. '''
    def __init__(self, sample_id, comet_id, analyzed_flag,
            tail_canvas_contour, head_canvas_contour, scale_ratio):
            
        self.__sample_id = sample_id
        self.__comet_id = comet_id
        self.__comet_copy = None
        self.__pos = None
        self.__analyzed_flag = analyzed_flag
        self.__tail_canvas_contour = tail_canvas_contour
        self.__head_canvas_contour = head_canvas_contour
        self.__scale_ratio = scale_ratio
        
        
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #   
   
    def get_sample_id(self):
        return self.__sample_id
        
    def set_sample_id(self, sample_id):
        self.__sample_id = sample_id
        
    def get_comet_id(self):
        return self.__comet_id
        
    def set_comet_id(self, comet_id):
        self.__comet_id = comet_id

    def get_comet_copy(self):
        return self.__comet_copy
        
    def set_comet_copy(self, comet_copy):
        self.__comet_copy = comet_copy
        
    def get_pos(self):
        return self.__pos
        
    def set_pos(self, pos):
        self.__pos = pos
        
    def get_analyzed_flag(self):
        return self.__analyzed_flag
        
    def set_analyzed_flag(self, analyzed_flag):
        self.__analyzed_flag = analyzed_flag
        
    def get_tail_canvas_contour(self):
        return self.__tail_canvas_contour
        
    def set_tail_canvas_contour(self, tail_canvas_contour):
        self.__tail_canvas_contour = tail_canvas_contour
        
    def get_head_canvas_contour(self):
        return self.__head_canvas_contour
        
    def set_head_canvas_contour(self, head_canvas_contour):
        self.__head_canvas_contour = head_canvas_contour
        
    def get_scale_ratio(self):
        return self.__scale_ratio
        
    def set_scale_ratio(self, scale_ratio):
        self.__scale_ratio = scale_ratio



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   DeleteCometCommand                                                        #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class DeleteCometCommand(Command):

    '''
        The DeleteCometCommand class. Extends Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):

        # Retrieve data
        (sample_id, comet_id) = self._data
        
        # Activate Sample
        if self._controller.get_active_sample_id() != sample_id:
            self._controller.activate_sample(sample_id)
        
        # Transition to CanvasSelectionState       
        self._controller.canvas_transition_to_selection_state()
        
        # Delete comet
        (comet_copy, pos) = self._controller.delete_comet(
                                sample_id, comet_id)
                    
        # Save data
        self._data = (sample_id, comet_copy, pos)

    ''' Command.undo() behaviour. '''
    def undo(self):

        # Retrieve data
        (sample_id, comet, pos) = self._data
        
        # Activate Sample
        if self._controller.get_active_sample_id() != sample_id:
            self._controller.activate_sample(sample_id)
        
        # Transition to CanvasSelectionState       
        self._controller.canvas_transition_to_selection_state()
        
        # Add comet
        self._controller.add_comet(sample_id, comet, pos)        

        # Select comet
        self._controller.select_comet(sample_id, comet.get_id())
        
        # Save data
        self._data = (sample_id, comet.get_id())



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   RemoveCometTailCommand                                                    #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class RemoveCometTailCommand(Command):

    '''
        The RemoveCometTailCommand class. Extends Command. 
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):

        # Retrieve data
        (sample_id, comet_id) = self._data
        
        # Activate Sample
        if self._controller.get_active_sample_id() != sample_id:
            self._controller.activate_sample(sample_id)
            
        # Transition to CanvasSelectionState       
        self._controller.canvas_transition_to_selection_state()    
        
        # Remove comet tail
        comet_contour = self._controller.remove_comet_tail(
                            sample_id, comet_id)                           
                
        # Select comet
        self._controller.select_comet(sample_id, comet_id)                    
                            
        # Save data
        self._data = (sample_id, comet_id, comet_contour)

    ''' Command.undo() behaviour. '''
    def undo(self):

        # Retrieve data
        (sample_id, comet_id, comet_contour) = self._data
        
        # Activate Sample
        if self._controller.get_active_sample_id() != sample_id:
            self._controller.activate_sample(sample_id)
            
        # Transition to CanvasSelectionState       
        self._controller.canvas_transition_to_selection_state()    
        
        # Add comet tail
        self._controller.add_comet_tail(
            sample_id, comet_id, comet_contour)
                
        # Select comet
        self._controller.select_comet(sample_id, comet_id)
        
        # Save data
        self._data = (sample_id, comet_id)



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   AnalyzeSamplesCommand                                                     #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class AnalyzeSamplesCommand(Command):

    '''
        The AnalyzeSamplesCommand class. Extends Command.
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

        # Replace sample's comet lists
        self._data = self._controller.update_samples_comet_list(self._data)



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   FlipSampleImageCommand                                                    #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class FlipSampleImageCommand(Command):

    '''
        The FlipSampleImageCommand class. Extends Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)
    
    ''' Command.execute() behaviour. '''
    def execute(self):
        self.__flip_sample_image()
        
    ''' Command.undo() behaviour. '''    
    def undo(self):
        self.__flip_sample_image()
        
    ''' Flips the Sample's image with given ID. '''    
    def __flip_sample_image(self):

        # Retrieve data
        sample_id = self._data

        # Activate Sample
        if self._controller.get_active_sample_id() != sample_id:
            self._controller.activate_sample(sample_id)
            
        # Transition to CanvasSelectionState       
        self._controller.canvas_transition_to_selection_state()
        
        # Flip Sample's image
        self._controller.flip_sample_image(sample_id)



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   InvertSampleImageCommand                                                  #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class InvertSampleImageCommand(Command):

    '''
        The InvertSampleImage class. Extends Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)
    
    ''' Command.execute() behaviour. '''
    def execute(self):
        self.__invert_sample_image()
        
    ''' Command.undo() behaviour. '''    
    def undo(self):
        self.__invert_sample_image()
        
    ''' Inverts the Sample's image with given ID. '''    
    def __invert_sample_image(self):

        # Retrieve data
        sample_id = self._data

        # Activate Sample
        if self._controller.get_active_sample_id() != sample_id:
            self._controller.activate_sample(sample_id)
            
        # Transition to CanvasSelectionState       
        self._controller.canvas_transition_to_selection_state()
        
        # Invert Sample's image
        self._controller.invert_sample_image(sample_id)



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   EditCometContoursCommand                                                  #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class EditCometContoursCommand(Command):

    '''
        The EditCometContoursCommand class. Extends Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):
        
        # Activate Sample if needed
        if self._controller.get_active_sample_id() != self._data.get_sample_id():
            self._controller.activate_sample(self._data.get_sample_id())
        
        # Select Comet
        self._controller.select_comet(
            self._data.get_sample_id(), self._data.get_comet_id())
        
        # Scale the CanvasContours dicts if needed
        current_scale_ratio = self._controller.get_sample_zoom_value(
            self._data.get_sample_id())
        if self._data.get_scale_ratio() != current_scale_ratio:
        
            utils.scale_canvas_contour_dict(
                self._data.get_tail_canvas_contour_dict(),
                current_scale_ratio / self._data.get_scale_ratio()
            )
                
            utils.scale_canvas_contour_dict(
                self._data.get_head_canvas_contour_dict(),
                current_scale_ratio / self._data.get_scale_ratio()
            )
            
            self._data.set_scale_ratio(current_scale_ratio)
                     
        # Set the Comet as being edited
        self._controller.start_comet_being_edited(
            self._data.get_sample_id(), self._data.get_comet_id(),
            copy.deepcopy(self._data.get_tail_canvas_contour_dict()),
            copy.deepcopy(self._data.get_head_canvas_contour_dict())
        )
        
    ''' Command.undo() behaviour. '''
    def undo(self):
        
        # Activate Sample if needed
        if self._controller.get_active_sample_id() != self._data.get_sample_id():
            self._controller.activate_sample(self._data.get_sample_id())
        
        # Set Comet as not being edited
        self._controller.quit_comet_being_edited()
        
        # Select Comet
        self._controller.select_comet(
            self._data.get_sample_id(), self._data.get_comet_id())
        


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   EditCometContoursCommandData                                              #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class EditCometContoursCommandData(object):

    '''
        The EditCometContoursCommandData class.
    '''

    ''' Initialization method. '''
    def __init__(self, sample_id, comet_id, tail_canvas_contour_dict,
            head_canvas_contour_dict, scale_ratio):
        
        self.__sample_id = sample_id
        self.__comet_id = comet_id
        self.__tail_canvas_contour_dict = tail_canvas_contour_dict
        self.__head_canvas_contour_dict = head_canvas_contour_dict
        self.__scale_ratio = scale_ratio


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #   
   
    def get_sample_id(self):
        return self.__sample_id
        
    def set_sample_id(self, sample_id):
        self.__sample_id = sample_id
        
    def get_comet_id(self):
        return self.__comet_id
        
    def set_comet_id(self, comet_id):
        self.__comet_id = comet_id

    def get_tail_canvas_contour_dict(self):
        return self.__tail_canvas_contour_dict
        
    def set_tail_canvas_contour_dict(self, tail_canvas_contour_dict):
        self.__tail_canvas_contour_dict = tail_canvas_contour_dict
        
    def get_head_canvas_contour_dict(self):
        return self.__head_canvas_contour_dict
        
    def set_head_canvas_contour_dict(self, head_canvas_contour_dict):
        self.__head_canvas_contour_dict = head_canvas_contour_dict

    def get_scale_ratio(self):
        return self.__scale_ratio
        
    def set_scale_ratio(self, scale_ratio):
        self.__scale_ratio = scale_ratio
 
 
 
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   CancelEditCometContoursCommand                                            #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class CancelEditCometContoursCommand(Command):

    '''
        The CancelEditCometContoursCommand class. Extends Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):
    
        # Activate Sample if needed
        if self._controller.get_active_sample_id() != self._data.get_sample_id():
            self._controller.activate_sample(self._data.get_sample_id())
        
        # Quit Comet being edited
        self._controller.quit_comet_being_edited()

    ''' Command.undo() behaviour. '''
    def undo(self):
                   
        # Activate Sample if needed
        if self._controller.get_active_sample_id() != self._data.get_sample_id():
            self._controller.activate_sample(self._data.get_sample_id())

        current_scale_ratio = self._controller.get_sample_zoom_value(
            self._data.get_sample_id())
        # Scale the CanvasContour dictionaries if needed
        if self._data.get_scale_ratio() != current_scale_ratio:
        
            utils.scale_canvas_contour_dict(
                self._data.get_tail_canvas_contour_dict(),
                current_scale_ratio / self._data.get_scale_ratio()
            )
            
            utils.scale_canvas_contour_dict(
                self._data.get_head_canvas_contour_dict(),
                current_scale_ratio / self._data.get_scale_ratio()
            )
        
            # Update the scale_ratio attribute
            self._data.set_scale_ratio(current_scale_ratio)
            
        # Start Comet being edited  
        self._controller.start_comet_being_edited(
            self._data.get_sample_id(), self._data.get_comet_id(),
            copy.deepcopy(self._data.get_tail_canvas_contour_dict()),
            copy.deepcopy(self._data.get_head_canvas_contour_dict())
        )
        


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   CancelEditCometContoursCommandData                                        #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class CancelEditCometContoursCommandData(object):

    '''
        The CancelEditCometContoursCommandData class.
    '''

    ''' Initialization method. '''
    def __init__(self, sample_id, comet_id, tail_canvas_contour_dict,
            head_canvas_contour_dict, scale_ratio):
        
        self.__sample_id = sample_id
        self.__comet_id = comet_id
        self.__tail_canvas_contour_dict = tail_canvas_contour_dict
        self.__head_canvas_contour_dict = head_canvas_contour_dict
        self.__scale_ratio = scale_ratio


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #   
   
    def get_sample_id(self):
        return self.__sample_id
        
    def set_sample_id(self, sample_id):
        self.__sample_id = sample_id
        
    def get_comet_id(self):
        return self.__comet_id
        
    def set_comet_id(self, comet_id):
        self.__comet_id = comet_id

    def get_tail_canvas_contour_dict(self):
        return self.__tail_canvas_contour_dict
        
    def set_tail_canvas_contour_dict(self, tail_canvas_contour_dict):
        self.__tail_canvas_contour_dict = tail_canvas_contour_dict
        
    def get_head_canvas_contour_dict(self):
        return self.__head_canvas_contour_dict
        
    def set_head_canvas_contour_dict(self, head_canvas_contour_dict):
        self.__head_canvas_contour_dict = head_canvas_contour_dict

    def get_scale_ratio(self):
        return self.__scale_ratio
        
    def set_scale_ratio(self, scale_ratio):
        self.__scale_ratio = scale_ratio



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   UpdateCometContoursCommand                                                #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class UpdateCometContoursCommand(Command):

    '''
        The UpdateCometContoursCommand class. Extends Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() implementation method. '''
    def execute(self):                          
        
        # Activate Sample if needed
        if (self._controller.get_active_sample_id() != self._data.
                get_sample_id()):
            self._controller.activate_sample(self._data.get_sample_id())
         
        # Quit Comet being edited
        self._controller.quit_comet_being_edited()

        # Update Comet contours
        self._controller.update_comet_contours(
            self._data.get_sample_id(), self._data.get_comet_id(),
            self._data.get_opencv_tail_contour(),
            self._data.get_opencv_head_contour()
        )

    ''' Command.undo() implementation method. '''
    def undo(self):
         
        # Activate Sample if needed
        if (self._controller.get_active_sample_id() != self._data.
                get_sample_id()):
            self._controller.activate_sample(self._data.get_sample_id()) 
         
        
        current_scale_ratio = self._controller.get_sample_zoom_value(
            self._data.get_sample_id())
        # Scale the CanvasContour dictionaries if needed
        if self._data.get_scale_ratio() != current_scale_ratio:
        
            utils.scale_canvas_contour_dict(
                self._data.get_tail_canvas_contour_dict(),
                current_scale_ratio / self._data.get_scale_ratio()
            )
            
            utils.scale_canvas_contour_dict(
                self._data.get_head_canvas_contour_dict(),
                current_scale_ratio / self._data.get_scale_ratio()
            )
        
            # Update the scale_ratio attribute
            self._data.set_scale_ratio(current_scale_ratio)
         
        # Start Comet being edited  
        self._controller.start_comet_being_edited(
            self._data.get_sample_id(), self._data.get_comet_id(),
            copy.deepcopy(self._data.get_tail_canvas_contour_dict()),
            copy.deepcopy(self._data.get_head_canvas_contour_dict())
        )
        
        # Update Comet contours
        self._controller.update_comet_contours(
            self._data.get_sample_id(), self._data.get_comet_id(),
            self._data.get_opencv_tail_contour(),
            self._data.get_opencv_head_contour()
        )
        

 
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   UpdateCometContoursCommandData                                            #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class UpdateCometContoursCommandData(object):

    '''
        The UpdateCometContoursCommandData class.
    '''

    ''' Initialization method. '''
    def __init__(self, sample_id, comet_id, opencv_tail_contour,
            opencv_head_contour, tail_canvas_contour_dict,
            head_canvas_contour_dict, scale_ratio):
        
        self.__sample_id = sample_id
        self.__comet_id = comet_id
        self.__opencv_tail_contour = opencv_tail_contour
        self.__opencv_head_contour = opencv_head_contour
        self.__tail_canvas_contour_dict = tail_canvas_contour_dict
        self.__head_canvas_contour_dict = head_canvas_contour_dict
        self.__scale_ratio = scale_ratio


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #   
   
    def get_sample_id(self):
        return self.__sample_id
        
    def set_sample_id(self, sample_id):
        self.__sample_id = sample_id
        
    def get_comet_id(self):
        return self.__comet_id
        
    def set_comet_id(self, comet_id):
        self.__comet_id = comet_id
        
    def get_opencv_tail_contour(self):
        return self.__opencv_tail_contour
        
    def set_opencv_tail_contour(self, opencv_tail_contour):
        self.__opencv_tail_contour = opencv_tail_contour
        
    def get_opencv_head_contour(self):
        return self.__opencv_head_contour
        
    def set_opencv_head_contour(self, opencv_head_contour):
        self.__opencv_head_contour = opencv_head_contour

    def get_tail_canvas_contour_dict(self):
        return self.__tail_canvas_contour_dict
        
    def set_tail_canvas_contour_dict(self, tail_canvas_contour_dict):
        self.__tail_canvas_contour_dict = tail_canvas_contour_dict
        
    def get_head_canvas_contour_dict(self):
        return self.__head_canvas_contour_dict
        
    def set_head_canvas_contour_dict(self, head_canvas_contour_dict):
        self.__head_canvas_contour_dict = head_canvas_contour_dict

    def get_scale_ratio(self):
        return self.__scale_ratio
        
    def set_scale_ratio(self, scale_ratio):
        self.__scale_ratio = scale_ratio
        

   
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   CreateDelimiterPointCommand                                               #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class CreateDelimiterPointCommand(Command):

    '''
        The CreateDelimiterPointCommand class. Extends Command.
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

        # Recalculate DelimiterPoint coordinates based on previous and
        # current zoom values
        current_scale_ratio = self._controller.get_sample_zoom_value(
            self._data.get_sample_id())
        if self._data.get_scale_ratio() != current_scale_ratio:
        
            # Scale and set coordinates
            self._data.set_coordinates(
                utils.scale_point(
                    self._data.get_coordinates(),
                    current_scale_ratio / self._data.get_scale_ratio()
                )
            )
            self._data.set_scale_ratio(current_scale_ratio)
           
        # 'Create DelimiterPoint' use case 
        if self._data.get_root_delimiter_point_id() is None:     
             
            # Create DelimiterPoint
            delimiter_point = self._controller.create_delimiter_point(
                self._data.get_builder(),
                self._data.get_coordinates(),
                self._data.get_delimiter_point_id(),
                self._data.get_canvas_contour_id(),
                self._data.get_roommate().get_delimiter_point()
            ) 
          
        # 'Create and connect DelimiterPoint' use case
        else:
        
            root_delimiter_point = CanvasModel.get_instance().get_delimiter_point(
                self._data.get_root_delimiter_point_id(),
                self._data.get_delimiter_point_type(),
                self._data.get_canvas_contour_id()
            )
            
            # Create and connect DelimiterPoint
            delimiter_point = self._controller.create_and_connect_delimiter_point(
                self._data.get_builder(),
                root_delimiter_point,
                self._data.get_coordinates(),
                self._data.get_delimiter_point_id(),
                self._data.get_roommate().get_delimiter_point()
            ) 
                    
        # Update Canvas
        self._controller.get_view().get_main_window().get_canvas().update()
        
        if self._data.get_comet_being_edited_has_changed() is not None:    
            self._controller.set_comet_being_edited_has_changed(True)
  
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
        
        if self._data.get_comet_being_edited_has_changed() is not None:    
            self._controller.set_comet_being_edited_has_changed(
                self._data.get_comet_being_edited_has_changed())
        
        
        
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
            canvas_contour_id, roommate, coordinates, builder, scale_ratio):
        
        self.__sample_id = sample_id
        self.__delimiter_point_id = delimiter_point_id
        self.__delimiter_point_type = delimiter_point_type
        self.__canvas_contour_id = canvas_contour_id
        self.__roommate = roommate
        self.__coordinates = coordinates      
        self.__builder = builder
        self.__scale_ratio = scale_ratio
        self.__root_delimiter_point_id = None
        self.__comet_being_edited_has_changed = None
        

        
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
        
    def get_builder(self):
        return self.__builder
        
    def set_builder(self, builder):
        self.__builder = builder
        
    def get_scale_ratio(self):
        return self.__scale_ratio
        
    def set_scale_ratio(self, scale_ratio):
        self.__scale_ratio = scale_ratio
        
    def get_root_delimiter_point_id(self):
        return self.__root_delimiter_point_id
        
    def set_root_delimiter_point_id(self, root_delimiter_point_id):
        self.__root_delimiter_point_id = root_delimiter_point_id
        
    def get_roommate(self):
        return self.__roommate
        
    def set_roommate(self, roommate):
        self.__roommate = roommate
        
    def get_comet_being_edited_has_changed(self):
        return self.__comet_being_edited_has_changed
        
    def set_comet_being_edited_has_changed(self, comet_being_edited_has_changed):
        self.__comet_being_edited_has_changed = comet_being_edited_has_changed



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   DeleteDelimiterPointsCommand                                              #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class DeleteDelimiterPointsCommand(Command):

    '''
        The DeleteDelimiterPointsCommand command. Extends Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)

    ''' Command.execute() behaviour. '''
    def execute(self):
        
        # Activate Sample if needed
        if self._controller.get_active_sample_id() != self._data.get_sample_id():
            self._controller.activate_sample(self._data.get_sample_id())

        # Transition to EditingSelectionState       
        self._controller.canvas_transition_to_editing_selection_state()
        
        # Prepare the list of SelectedDelimiterPoints
        selected_delimiter_point_list = []
        for (canvas_contour_id, (deleted_delimiter_point_data_list, _)) in self._data.get_deleted_delimiter_point_data_dict().items():
              
            for deleted_delimiter_point_data in deleted_delimiter_point_data_list:
              
                selected_delimiter_point_list.append(
                    SelectedDelimiterPoint(
                        deleted_delimiter_point_data.get_delimiter_point_id(),
                        deleted_delimiter_point_data.get_builder().POINT_TYPE,
                        canvas_contour_id
                    )
                )
                
        # Delete the DelimiterPoints   
        self._controller.delete_delimiter_points(selected_delimiter_point_list)
        
        if self._data.get_comet_being_edited_has_changed() is not None:    
            self._controller.set_comet_being_edited_has_changed(True)
    
    ''' Command.undo() behaviour. '''
    def undo(self):
        
        # Activate Sample if needed
        if self._controller.get_active_sample_id() != self._data.get_sample_id():
            self._controller.activate_sample(self._data.get_sample_id())

        # Transition to EditingSelectionState       
        self._controller.canvas_transition_to_editing_selection_state()
        
        # Recalculate DelimiterPoint coordinates based on previous and
        # current zoom values
        current_scale_ratio = self._controller.get_sample_zoom_value(
            self._data.get_sample_id())
        recalculate_coordinates = self._data.get_scale_ratio() != current_scale_ratio
        
        # Add the DelimiterPoints that were removed
        for (canvas_contour_id, (deleted_delimiter_point_data_list, closed)) in self._data.get_deleted_delimiter_point_data_dict().items():
    
            for deleted_delimiter_point_data in deleted_delimiter_point_data_list:
            
                if recalculate_coordinates:
        
                    # Scale and set coordinates
                    deleted_delimiter_point_data.set_coordinates(
                        utils.scale_point(
                            deleted_delimiter_point_data.get_coordinates(),
                            current_scale_ratio / self._data.get_scale_ratio()
                        )
                    )
           
                # Add DelimiterPoint
                self._controller.create_delimiter_point(
                    deleted_delimiter_point_data.get_builder(),
                    deleted_delimiter_point_data.get_coordinates(),
                    deleted_delimiter_point_data.get_delimiter_point_id(),
                    canvas_contour_id,
                    deleted_delimiter_point_data.get_roommate().get_delimiter_point()
                )
                
            # Set the CanvasContour 'closed' value
            CanvasModel.get_instance().get_canvas_contour(
                deleted_delimiter_point_data.get_builder().POINT_TYPE, 
                canvas_contour_id
            ).set_closed(closed)    
                
        # Connect the DelimiterPoints as they were connected before
        for (canvas_contour_id, (deleted_delimiter_point_data_list, _)) in self._data.get_deleted_delimiter_point_data_dict().items():

            for deleted_delimiter_point_data in deleted_delimiter_point_data_list:
            
                # Source DelimiterPoint
                src_delimiter_point = CanvasModel.get_instance().get_delimiter_point(
                    deleted_delimiter_point_data.get_delimiter_point_id(),
                    deleted_delimiter_point_data.get_builder().POINT_TYPE,
                    canvas_contour_id
                )
                               
                for neighbor_id in deleted_delimiter_point_data.get_neighbor_id_list():

                    # Destination DelimiterPoint
                    dst_delimiter_point = CanvasModel.get_instance().get_delimiter_point(
                        neighbor_id,
                        deleted_delimiter_point_data.get_builder().POINT_TYPE,
                        canvas_contour_id
                    )
                    
                    if src_delimiter_point is not None and dst_delimiter_point is not None:
                  
                        # Connect DelimiterPoints
                        self._controller.connect_delimiter_points(
                            deleted_delimiter_point_data.get_builder(),
                            src_delimiter_point,
                            dst_delimiter_point,
                            canvas_contour_id
                        )
                        
        if recalculate_coordinates: 
            self._data.set_scale_ratio(current_scale_ratio)
            
        if self._data.get_comet_being_edited_has_changed() is not None:    
            self._controller.set_comet_being_edited_has_changed(
                self._data.get_comet_being_edited_has_changed())

        

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   DeleteDelimiterPointsCommandData                                          #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class DeleteDelimiterPointsCommandData(object):  

    '''
        The DeleteDelimiterPointsCommandData class.
    '''

    ''' Initialization method. '''
    def __init__(self, sample_id, deleted_delimiter_point_data_dict,
            scale_ratio): 

        self.__sample_id = sample_id
        self.__deleted_delimiter_point_data_dict = deleted_delimiter_point_data_dict
        self.__scale_ratio = scale_ratio
        self.__comet_being_edited_has_changed = None
        

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
        
    def get_sample_id(self):
        return self.__sample_id
        
    def set_sample_id(self, sample_id):
        self.__sample_id = sample_id
        
    def get_deleted_delimiter_point_data_dict(self):
        return self.__deleted_delimiter_point_data_dict
        
    def set_deleted_delimiter_point_data_dict(self,
            deleted_delimiter_point_data_dict):
        self.__deleted_delimiter_point_data_dict = \
            deleted_delimiter_point_data_dict
            
    def get_scale_ratio(self):  
        return self.__scale_ratio
        
    def set_scale_ratio(self, scale_ratio):
        self.__scale_ratio = scale_ratio
        
    def get_comet_being_edited_has_changed(self):
        return self.__comet_being_edited_has_changed 

    def set_comet_being_edited_has_changed(self, comet_being_edited_has_changed):
        self.__comet_being_edited_has_changed = comet_being_edited_has_changed        



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   DeletedDelimiterPointData                                                 #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class DeletedDelimiterPointData(object):

    '''
        The DeletedDelimiterPointData class.
    '''

    ''' Initialization method. '''
    def __init__(self, delimiter_point_id, coordinates, neighbor_id_list,
            roommate, builder): 

        self.__delimiter_point_id = delimiter_point_id
        self.__coordinates = coordinates
        self.__neighbor_id_list = neighbor_id_list
        self.__roommate = roommate
        self.__builder = builder
        
        
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_delimiter_point_id(self):
        return self.__delimiter_point_id
        
    def set_delimiter_point_id(self, delimiter_point_id):
        self.__delimiter_point_id = delimiter_point_id
        
    def get_coordinates(self):
        return self.__coordinates
        
    def set_coordinates(self, coordinates):
        self.__coordinates = coordinates
        
    def get_neighbor_id_list(self):
        return self.__neighbor_id_list
        
    def set_neighbor_id_list(self, neighbor_id_list):
        self.__neighbor_id_list = neighbor_id_list
        
    def get_roommate(self):
        return self.__roommate
        
    def set_roommate(self, roommate):
        self.__roommate = roommate
        
    def get_builder(self):
        return self.__builder
        
    def set_builder(self, builder):
        self.__builder = builder
        
        

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   ConnectDelimiterPointsCommand                                             #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class ConnectDelimiterPointsCommand(Command):

    '''
        The ConnectDelimiterPointsCommand command. Extends Command.
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
       
        src_delimiter_point = CanvasModel.get_instance().get_delimiter_point(
            self._data.get_src_delimiter_point_id(),
            self._data.get_builder().POINT_TYPE,
            self._data.get_previous_src_delimiter_point_canvas_contour_id()
        )
        dst_delimiter_point = CanvasModel.get_instance().get_delimiter_point(
            self._data.get_dst_delimiter_point_id(),
            self._data.get_builder().POINT_TYPE,
            self._data.get_previous_dst_delimiter_point_canvas_contour_id()
        )
       
        # Connect DelimiterPoints
        self._controller.connect_delimiter_points(
            self._data.get_builder(),
            src_delimiter_point, dst_delimiter_point,
            self._data.get_new_canvas_contour_id()
        )
        
        if self._data.get_comet_being_edited_has_changed() is not None:    
            self._controller.set_comet_being_edited_has_changed(True)
        
    ''' Command.undo() behaviour. '''
    def undo(self):
    
        # Activate Sample if needed
        if self._controller.get_active_sample_id() != self._data.get_sample_id():
            self._controller.activate_sample(self._data.get_sample_id())

        # Transition to CanvasEditingState       
        self._controller.canvas_transition_to_editing_state()
    
        src_delimiter_point = CanvasModel.get_instance().get_delimiter_point(
            self._data.get_src_delimiter_point_id(),
            self._data.get_builder().POINT_TYPE,
            self._data.get_new_canvas_contour_id()
        )
        dst_delimiter_point = CanvasModel.get_instance().get_delimiter_point(
            self._data.get_dst_delimiter_point_id(),
            self._data.get_builder().POINT_TYPE,
            self._data.get_new_canvas_contour_id()
        ) 
        
        # Disconnect DelimiterPoints
        self._controller.disconnect_delimiter_points(
            self._data.get_builder(),
            src_delimiter_point, dst_delimiter_point,
            self._data.get_previous_src_delimiter_point_canvas_contour_id(),
            self._data.get_previous_dst_delimiter_point_canvas_contour_id() 
        )

        if self._data.get_comet_being_edited_has_changed() is not None:    
            self._controller.set_comet_being_edited_has_changed(
                self._data.get_comet_being_edited_has_changed())



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   ConnectDelimiterPointsCommandData                                         #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class ConnectDelimiterPointsCommandData(object):

    '''
        The ConnectDelimiterPointsCommandData class.
    '''

    ''' Initialization method. '''
    def __init__(self, sample_id, builder, src_delimiter_point_id,
            dst_delimiter_point_id, previous_src_delimiter_point_canvas_contour_id,
            previous_dst_delimiter_point_canvas_contour_id, new_canvas_contour_id):
        
        self.__sample_id = sample_id
        self.__builder = builder       
        self.__src_delimiter_point_id = src_delimiter_point_id
        self.__dst_delimiter_point_id = dst_delimiter_point_id
        self.__previous_src_delimiter_point_canvas_contour_id = \
            previous_src_delimiter_point_canvas_contour_id
        self.__previous_dst_delimiter_point_canvas_contour_id = \
            previous_dst_delimiter_point_canvas_contour_id
        self.__new_canvas_contour_id = new_canvas_contour_id
        self.__comet_being_edited_has_changed = None
        
      
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #   
   
    def get_sample_id(self):
        return self.__sample_id
        
    def set_sample_id(self, sample_id):
        self.__sample_id = sample_id
        
    def get_builder(self):
        return self.__builder
        
    def set_builder(self, builder):
        self.__builder = builder    
        
    def get_src_delimiter_point_id(self):
        return self.__src_delimiter_point_id
        
    def set_src_delimiter_point_id(self, src_delimiter_point_id):
        self.__src_delimiter_point_id = src_delimiter_point_id
        
    def get_dst_delimiter_point_id(self):
        return self.__dst_delimiter_point_id
        
    def set_dst_delimiter_point_id(self, dst_delimiter_point_id):
        self.__dst_delimiter_point_id = dst_delimiter_point_id
        
    def get_previous_src_delimiter_point_canvas_contour_id(self):
        return self.__previous_src_delimiter_point_canvas_contour_id
      
    def set_previous_src_delimiter_point_canvas_contour_id(self,
            previous_src_delimiter_point_canvas_contour_id):
        self.__previous_src_delimiter_point_canvas_contour_id = \
            previous_src_delimiter_point_canvas_contour_id
      
    def get_previous_dst_delimiter_point_canvas_contour_id(self):
        return self.__previous_dst_delimiter_point_canvas_contour_id
        
    def set_previous_dst_delimiter_point_canvas_contour_id(self,
            previous_dst_delimiter_point_canvas_contour_id):
        self.__previous_dst_delimiter_point_canvas_contour_id = \
            previous_dst_delimiter_point_canvas_contour_id

    def get_new_canvas_contour_id(self):
        return self.__new_canvas_contour_id
        
    def set_new_canvas_contour_id(self, new_canvas_contour_id):
        self.__new_canvas_contour_id = new_canvas_contour_id
     
    def get_comet_being_edited_has_changed(self):
        return self.__comet_being_edited_has_changed
        
    def set_comet_being_edited_has_changed(self, comet_being_edited_has_changed):
        self.__comet_being_edited_has_changed = comet_being_edited_has_changed
        
        

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   CloseCanvasContourCommand                                                 #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class CloseCanvasContourCommand(Command):

    '''
        CloseCanvasContourCommand command. Extends Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)
        
    ''' Command.execute() behaviour. '''
    def execute(self):
    
        self.__replace_delimiter_point_dict(True)
         
    ''' Command.undo() behaviour. '''
    def undo(self):
    
        self.__replace_delimiter_point_dict(
            self._data.get_comet_being_edited_has_changed())
        
    ''' 
        Replaces the DelimiterPoint dict of the CanvasContour with given ID. 
    '''
    def __replace_delimiter_point_dict(self, has_changed):
            
        # Activate Sample if needed
        if self._controller.get_active_sample_id() != self._data.get_sample_id():
            self._controller.activate_sample(self._data.get_sample_id())
            
        # Transition to CanvasEditingState       
        self._controller.canvas_transition_to_editing_state()
        
        # Scale CanvasContour if needed
        current_scale_ratio = self._controller.get_sample_zoom_value(
            self._data.get_sample_id())
            
        if self._data.get_scale_ratio() != current_scale_ratio:
            utils.scale_canvas_contour(
                self._data.get_canvas_contour(),
                current_scale_ratio/self._data.get_scale_ratio()
            )
                                
        canvas_contour_copy = self._data.get_builder().get_contour_dict()[
            self._data.get_canvas_contour().get_id()]
            
        self._data.get_builder().get_contour_dict()[
            self._data.get_canvas_contour().get_id()] = \
                copy.deepcopy(self._data.get_canvas_contour())
            
        self._data.set_scale_ratio(current_scale_ratio)
        self._data.set_canvas_contour(canvas_contour_copy)

        if self._data.get_comet_being_edited_has_changed() is not None:    
            self._controller.set_comet_being_edited_has_changed(
                has_changed)



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   CloseCanvasContourCommandData                                             #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class CloseCanvasContourCommandData(object):

    '''
        The CloseCanvasContourCommandData class.
    '''

    ''' Initialization method. '''
    def __init__(self, sample_id, builder, canvas_contour, scale_ratio):

        self.__sample_id = sample_id
        self.__builder = builder
        self.__canvas_contour = canvas_contour
        self.__scale_ratio = scale_ratio
        self.__comet_being_edited_has_changed = None


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_sample_id(self):
        return self.__sample_id
        
    def set_sample_id(self, sample_id):
        self.__sample_id = sample_id
        
    def get_builder(self):
        return self.__builder
        
    def set_builder(self, builder):
        self.__builder = builder
        
    def get_canvas_contour(self):
        return self.__canvas_contour
        
    def set_canvas_contour(self, canvas_contour):
        self.__canvas_contour = canvas_contour
        
    def get_scale_ratio(self):
        return self.__scale_ratio
        
    def set_scale_ratio(self, scale_ratio):
        self.__scale_ratio = scale_ratio
        
    def get_comet_being_edited_has_changed(self):
        return self.__comet_being_edited_has_changed
        
    def set_comet_being_edited_has_changed(self, comet_being_edited_has_changed):
        self.__comet_being_edited_has_changed = comet_being_edited_has_changed



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   MoveDelimiterPointsCommand                                                #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 
        
class MoveDelimiterPointsCommand(Command):

    '''
        The MoveDelimiterPointsCommand class. Extends Command.
    '''

    ''' Initialization method. '''
    def __init__(self, controller):
        super().__init__(controller)
    
    ''' Command.execute() behaviour. '''
    def execute(self):    
        self.__move_delimiter_points(True)
               
    ''' Command.undo() behaviour. '''
    def undo(self):   
        self.__move_delimiter_points(
            self._data.get_comet_being_edited_has_changed())

    ''' Moves the DelimiterPoints to its origin. '''    
    def __move_delimiter_points(self, has_changed): 
        
        # Activate Sample if needed
        if self._controller.get_active_sample_id() != self._data.get_sample_id():
            self._controller.activate_sample(self._data.get_sample_id())
            
        # Transition to CanvasEditingState       
        self._controller.canvas_transition_to_editing_state()
        
        # Move points to origin coordinates
        self._controller.move_delimiter_points_to_origin(
            self._data.get_delimiter_point_selection(),
            self._data.get_scale_ratio()
        )
        
        # Set new scale ratio
        self._data.set_scale_ratio(self._controller.
            get_sample_zoom_value(self._data.get_sample_id()))
            
        if self._data.get_comet_being_edited_has_changed() is not None:    
            self._controller.set_comet_being_edited_has_changed(
                has_changed)
  

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   MoveDelimiterPointsCommandData                                            #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class MoveDelimiterPointsCommandData(object):

    '''
        The MoveDelimiterPointsCommandData class. Extends 
        CometBeingEditedData.
    '''

    ''' Initialization method. '''
    def __init__(self, sample_id, delimiter_point_selection, scale_ratio):

        self.__sample_id = sample_id
        self.__delimiter_point_selection = delimiter_point_selection
        self.__scale_ratio = scale_ratio
        self.__comet_being_edited_has_changed = None


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_sample_id(self):
        return self.__sample_id
        
    def set_sample_id(self, sample_id):
        self.__sample_id = sample_id

    def get_delimiter_point_selection(self):
        return self.__delimiter_point_selection
        
    def set_delimiter_point_selection(self, delimiter_point_selection):
        self.__delimiter_point_selection = delimiter_point_selection
        
    def get_scale_ratio(self):
        return self.__scale_ratio
        
    def set_scale_ratio(self, scale_ratio):
        self.__scale_ratio = scale_ratio
        
    def get_comet_being_edited_has_changed(self):
        return self.__comet_being_edited_has_changed 

    def set_comet_being_edited_has_changed(self, comet_being_edited_has_changed):
        self.__comet_being_edited_has_changed = comet_being_edited_has_changed
        
        