# -*- encoding: utf-8 -*-

'''
    The commands module.
'''


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
        self.controller = controller
        self.sample_to_activate_id = controller.get_active_sample_id()
        self.comet_to_select_id = None
        self.comet_to_select_id = \
            controller.get_active_sample_selected_comet_id()
        self.comet_being_edited_has_changed_to_set = controller.\
            get_comet_being_edited_has_changed()
        self.__flag_unsaved_changes = controller.get_flag_unsaved_changes()
        self.__data = None


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
# ~                                 Methods                                 ~ #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Execute Command method. '''
    def execute(self, *args):
        raise NotImplementedError("This method must be implemented.")

    ''' Undo Command method. '''
    def undo(self, *args):
        raise NotImplementedError("This method must be implemented.")

    ''' Retrieves the needed data before execution. '''
    def retrieve_data(self):
        self.comet_being_edited_has_changed = \
            self.controller.get_comet_being_edited_has_changed()
        self.active_sample_id = self.controller.get_active_sample_id()
        self.selected_comet_id = None
        self.selected_comet_id = \
            self.controller.get_active_sample_selected_comet_id()
        return self.__data

    ''' Saves the needed data for the next execution. '''
    def save_data(self, data):

        # Activate previously active sample
        if self.sample_to_activate_id is not None:
            self.controller.activate_sample(self.sample_to_activate_id)
            
        # Select previously selected comet
        if self.comet_to_select_id is not None:
            self.controller.select_comet(
                self.controller.get_active_sample_id(),
                self.comet_to_select_id
            )
            
        self.controller.set_comet_being_edited_has_changed(
            self.comet_being_edited_has_changed_to_set)
        # Set values for next execution
        self.sample_to_activate_id = self.active_sample_id
        self.comet_to_select_id = self.selected_comet_id
        # Store data
        self.__data = data


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_flag_unsaved_changes(self):
        return self.__flag_unsaved_changes

    def set_flag_unsaved_changes(self, flag_unsaved_changes):
        self.__flag_unsaved_changes = flag_unsaved_changes

    def get_data(self):
        return self.__data

    def set_data(self, data):
        self.__data = data

    

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   AddSamplesCommand                                                         #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
   
class AddSamplesCommand(Command):

    '''
        The AddSamplesCommand class. Extends from Command.
    '''

    def __init__(self, controller):
        super().__init__(controller)

    ''' Adds new samples. '''
    def execute(self):

        # Retrieve data
        data = self.retrieve_data()
      
        new_data = []
        # Redo execution
        while len(data) > 0:

            (sample, parameters) = data.pop()
            # Add sample
            self.controller.add_sample(sample, parameters)
            new_data.append(sample.get_id())

        # Save data        
        self.save_data(new_data)

    ''' Deletes the added samples. '''
    def undo(self):

        # Retrieve data
        data = self.retrieve_data()

        new_data = []
        # Undo execution
        for sample_id in data:

            # Delete sample
            (sample_copy, parameters, _) = self.controller.\
                                               delete_sample(sample_id)
            new_data.append((sample_copy, parameters))

        # Save data
        new_data.reverse()
        self.save_data(new_data)



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#   DeleteSampleCommand                                                       #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
   
class DeleteSampleCommand(Command):

    '''
        The DeleteSample class. Extends from Command.
    '''

    def __init__(self, controller):
        super().__init__(controller)

    def execute(self):

        # Retrieve data
        sample_id = self.retrieve_data()
        # Delete sample
        (sample_copy, parameters, pos) = self.controller.delete_sample(sample_id)
        # Save data
        self.save_data((sample_copy, parameters, pos))

    def undo(self):

        # Retrieve data
        (sample, parameters, pos) = self.retrieve_data()
        # Add sample
        self.controller.add_sample(sample, parameters, pos)
        # Save data
        self.save_data(sample.get_id())



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

    def execute(self):
        self.__rename()

    def undo(self):
        self.__rename()

    def __rename(self):

        # Retrieve data   
        (sample_id, sample_name) = self.retrieve_data()
        # Rename Sample
        previous_name = self.controller.rename_sample(
                            sample_id, sample_name)
        # Save data
        self.save_data((sample_id, previous_name))



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

    def execute(self):

        # Retrieve data
        (sample_id, comet, pos) = self.retrieve_data()         
        # Add comet
        self.controller.add_comet(sample_id, comet, pos)            
        # Save data
        self.save_data((sample_id, comet.get_id(), 
            self.controller.get_model().get_sample(sample_id).get_analyzed()))

    def undo(self):

        # Retrieve data
        (sample_id, comet_id, analyzed_flag) = self.retrieve_data()        
        # Delete comet
        (comet_copy, pos) = self.controller.delete_comet(
                                sample_id, comet_id)
        # Set analyzed flag
        self.controller.set_sample_analyzed_flag(
            sample_id, analyzed_flag)
        # Save data
        self.save_data((sample_id, comet_copy, pos))



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

    def execute(self):

        # Retrieve data
        (sample_id, comet_id) = self.retrieve_data()
        # Delete comet
        (comet_copy, pos) = self.controller.delete_comet(
                                sample_id, comet_id)
        # Save data
        self.save_data((sample_id, comet_copy, pos))

    def undo(self):

        # Retrieve data
        (sample_id, comet, pos) = self.retrieve_data()         
        # Add comet
        self.controller.add_comet(sample_id, comet, pos)
        # Save data
        self.save_data((sample_id, comet.get_id()))



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

    def execute(self):

        # Retrieve data
        (sample_id, comet_id) = self.retrieve_data()
        # Remove comet tail
        comet_contour = self.controller.remove_comet_tail(
                            sample_id, comet_id)
        # Save data
        self.save_data((sample_id, comet_id, comet_contour))

    def undo(self):

        # Retrieve data
        (sample_id, comet_id, comet_contour) = self.retrieve_data()
        # Add comet tail
        self.controller.add_comet_tail(
            sample_id, comet_id, comet_contour)
        # Save data
        self.save_data((sample_id, comet_id))



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

    def execute(self):
        self.__update_samples_comet_list()
        
    def undo(self):
        self.__update_samples_comet_list()

    def __update_samples_comet_list(self):

        # Retrieve data
        data = self.retrieve_data()
        # Replace sample's comet lists
        new_data = self.controller.update_samples_comet_list(data)
        # Save data
        self.save_data(new_data)



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
    
    def execute(self):
        self.controller.flip_sample_image(self.get_data())
        
    def undo(self):
        self.controller.flip_sample_image(self.get_data())



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
    
    def execute(self):
        self.controller.invert_sample_image(self.get_data())
        
    def undo(self):
        self.controller.invert_sample_image(self.get_data())



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

    def execute(self):
                  
        self.__update_comet_contours()

        '''
        canvas = self.controller.get_view().get_main_window().\
            get_canvas()
        canvas.get_selection_button().set_active(True)
        '''

    def undo(self):

        self.__update_comet_contours()
        
        '''
        (sample_id, data) = self.retrieve_data()
        self.controller.get_view().edit_comet_contour(
            sample_id, *data)
        '''

    def __update_comet_contours(self):

        # Retrieve data
        (sample_id, data) = self.retrieve_data()

        new_data = self.controller.update_comet_contours(sample_id, *data)

        # Save data
        self.save_data((sample_id, new_data))

