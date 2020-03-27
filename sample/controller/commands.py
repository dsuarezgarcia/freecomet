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
        self.__flag_unsaved_changes = controller.get_flag_unsaved_changes()
        self.__data = None
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
        return self.__data

    def set_data(self, data):
        self.__data = data
           
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
            self.controller.add_sample(sample, parameters)
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
            (sample_copy, parameters, _) = self.controller.\
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
        (sample_copy, parameters, pos) = self.controller.delete_sample(sample_id)
        
        # Save data
        self.set_data((sample_copy, parameters, pos))

    ''' Command.undo() behaviour. '''
    def undo(self):

        # Retrieve data
        (sample, parameters, pos) = self.get_data()
        
        # Add sample
        self.controller.add_sample(sample, parameters, pos)
        
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
        previous_name = self.controller.rename_sample(
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
        self.controller.add_comet(sample_id, comet, pos)
        # Activate Sample
        if self.controller.get_active_sample_id() != sample_id:
            self.controller.activate_sample(sample_id)
            
        # Save data
        self.set_data((sample_id, comet.get_id(), 
            self.controller.get_model().get_sample(sample_id).get_analyzed()))

    ''' Command.undo() behaviour. '''
    def undo(self):

        # Retrieve data
        (sample_id, comet_id, analyzed_flag) = self.get_data()  
        
        # Delete comet
        (comet_copy, pos) = self.controller.delete_comet(
                                sample_id, comet_id)
        # Activate Sample
        if self.controller.get_active_sample_id() != sample_id:
            self.controller.activate_sample(sample_id)                        
        # Set analyzed flag
        self.controller.set_sample_analyzed_flag(
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
        (comet_copy, pos) = self.controller.delete_comet(
                                sample_id, comet_id)
        # Activate Sample
        if self.controller.get_active_sample_id() != sample_id:
            self.controller.activate_sample(sample_id)
            
        # Save data
        self.set_data((sample_id, comet_copy, pos))

    ''' Command.undo() behaviour. '''
    def undo(self):

        # Retrieve data
        (sample_id, comet, pos) = self.get_data()
        
        # Add comet
        self.controller.add_comet(sample_id, comet, pos)        
        # Activate Sample
        if self.controller.get_active_sample_id() != sample_id:
            self.controller.activate_sample(sample_id)
        # Select comet
        self.controller.select_comet(sample_id, comet.get_id())
        
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
        comet_contour = self.controller.remove_comet_tail(
                            sample_id, comet_id)                           
        # Activate Sample
        if self.controller.get_active_sample_id() != sample_id:
            self.controller.activate_sample(sample_id)        
        # Select comet
        self.controller.select_comet(sample_id, comet_id)                    
                            
        # Save data
        self.set_data((sample_id, comet_id, comet_contour))

    ''' Command.undo() behaviour. '''
    def undo(self):

        # Retrieve data
        (sample_id, comet_id, comet_contour) = self.get_data()
        # Add comet tail
        self.controller.add_comet_tail(
            sample_id, comet_id, comet_contour)

        # Activate Sample
        if self.controller.get_active_sample_id() != sample_id:
            self.controller.activate_sample(sample_id)        
        # Select comet
        self.controller.select_comet(sample_id, comet_id)
        
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
        new_data = self.controller.update_samples_comet_list(data)
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
        self.controller.flip_sample_image(self.get_data())
        
    ''' Command.undo() behaviour. '''    
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
    
    ''' Command.execute() behaviour. '''
    def execute(self):
        self.controller.invert_sample_image(self.get_data())
        
    ''' Command.undo() behaviour. '''    
    def undo(self):
        self.controller.invert_sample_image(self.get_data())



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
    
        # Activate Sample
        self.controller.activate_sample(self.get_data()[0])
        
        # Update Comet as being edited
        self.controller.start_comet_being_edited(*self.get_data())

    ''' Command.undo() behaviour. '''
    def undo(self):

        # Retrieve data
        (sample_id, comet_id, _, _) = self.get_data()
        
        # Activate Sample
        self.controller.activate_sample(sample_id)
        # Select Comet
        self.controller.select_comet(sample_id, comet_id)
        # Update Comet as not being edited
        self.controller.quit_comet_being_edited()

 
 
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
        data = self.get_data()      
        # Activate Sample
        self.controller.activate_sample(data[0])
        # Quit Comet being edited
        self.controller.quit_comet_being_edited()

    ''' Command.undo() behaviour. '''
    def undo(self):
          
        # Retrieve data  
        data = self.get_data()  
        # Activate Sample
        self.controller.activate_sample(data[0])  
        # Start Comet being edited  
        self.controller.start_comet_being_edited(*data)
        


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
        self.__update_comet_contours()

    ''' Command.undo() behaviour. '''
    def undo(self):
        self.__update_comet_contours()
      
    ''' Updates the Comet's contours. '''
    def __update_comet_contours(self):

        # Retrieve data
        (sample_id, data) = self.get_data()

        new_data = self.controller.update_comet_contours(sample_id, *data)

        # Save data
        self.set_data((sample_id, new_data))



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
    
        # Retrieve data
        (sample_id, data) = self.get_data()
                  
        new_data = self.controller.create_delimiter_point(sample_id, *data)

        # Save data
        self.set_data((sample_id, new_data))

    ''' Command.undo() behaviour. '''
    def undo(self):

        # Retrieve data
        (sample_id, data) = self.get_data()
                  
        new_data = self.controller.delete_delimiter_point(sample_id, *data)

        # Save data
        self.set_data((sample_id, new_data))
 


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
        if self.controller.get_active_sample_id() != sample_id:
            self.controller.activate_sample(sample_id)
        
        # Move points to origin coordinates
        new_scale_ratio = self.controller.move_delimiter_points_to_origin(
            delimiter_point_selection, scale_ratio)
            
        # Save data
        self.set_data((sample_id, delimiter_point_selection, new_scale_ratio))

