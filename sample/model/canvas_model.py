# -*- encoding: utf-8 -*-

'''
    The canvas_model module.
'''

# General imports
import itertools
import cairo
import copy

# Custom imports
from singleton import Singleton
import model.utils as utils


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	Colors                                                                    #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class Colors(object):

    '''
        The Colors class.
    '''

    YELLOW = (1., 1., 0., 1.)
    GREEN = (0., 1., 0., 1.)
    RED = (1., 0., 0., 1.)


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	CanvasModel                                                               #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class CanvasModel(metaclass=Singleton):

    '''
        The CanvasModel class.
    '''
    
    ANCHORING_DISTANCE = 10
    DELIMITER_POINT_SIZE = 5

    ''' Initialization method. '''
    def __init__(self):
        
        self.__tail_color = Colors.RED
        self.__head_color = Colors.GREEN
        
        # CanvasSelectionState parameters
        self.__selection_color = Colors.YELLOW
        self.__selection_width = 0.5
        
        # CanvasEditingState parameters
        self.__tail_contour_dict = {}
        self.__head_contour_dict = {}
        self.__edge_width = 1
        self.__edge_line_type = cairo.LINE_CAP_ROUND    
        self.__anchored_delimiter_point = None
        self.__anchored_delimiter_point_color = Colors.YELLOW
        
        # EditingSelectionState parameters
        self.__selection_area_color = Colors.YELLOW   
        self.__selection_distance = CanvasModel.DELIMITER_POINT_SIZE
        self.__requested_delimiter_point = None
        self.__delimiter_point_selection = DelimiterPointSelection()        
        self.__delimiter_point_selection_color = Colors.YELLOW         
        self.__free_selection_area_width = 0.5
        self.__edge_selection_distance = 5
        self.__selection_area = None
        self.__selected_pivot_delimiter_point = None
        
        # BuildingContourState parameters
        self.__root_delimiter_point = None
        
        # So we don't save anything if the comet contours remained the same.
        self.__comet_being_edited_has_changed = False
        
        TailContourBuilder()
        HeadContourBuilder()
        

   
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                   Methods                                   #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #        
    
    def debug(self):
    
        print("***************************TAIL*******************************")
        for canvas_contour in self.__tail_contour_dict.values():
            for delimiter_point in canvas_contour.get_delimiter_point_dict().values():
                print(delimiter_point.to_string())
        print("***************************HEAD******************************")
        for canvas_contour in self.__head_contour_dict.values():
            for delimiter_point in canvas_contour.get_delimiter_point_dict().values():
                print(delimiter_point.to_string())
        
    
    ''' Behaviour when a Comet is requested to be edited. '''
    def prepare_comet_for_editing(self, opencv_tail_contour, opencv_head_contour):
    
        self.__tail_contour_dict = {}
        self.__head_contour_dict = {}

        # Load Comet contour
        if opencv_tail_contour is not None:
        
            self.load_opencv_contour(
                opencv_tail_contour,
                TailContourBuilder.get_instance()
            )
            self.__root_delimiter_point = None

        # Load Head contour
        self.load_opencv_contour(
            opencv_head_contour,
            HeadContourBuilder.get_instance()
        )           
        self.__root_delimiter_point = None
    
    ''' Loads an OpenCV contour into the contour dictionary. '''
    def load_opencv_contour(self, opencv_contour, building_instance):

        # Create first point
        previous_point = building_instance.create_delimiter_point(
            (opencv_contour[0][0][0], opencv_contour[0][0][1]))
        first_point = previous_point

        # Create and connect the rest
        for point in opencv_contour[1:]:
            coordinates = (point[0][0], point[0][1])
            previous_point = building_instance.create_and_connect_points(
                previous_point, coordinates)

        # Connect last and first points
        building_instance.connect_points(first_point, previous_point)

        for (_, contour) in building_instance.get_contour_dict().items():
            contour.set_closed(True)
            
    ''' Adds the requested_delimiter_point by the user. '''        
    def add_requested_delimiter_point(self):

        (neighbor1, neighbor2) = self.__requested_delimiter_point.\
                                     get_edge()

        builder = self.get_contour_builder(neighbor1.get_type())
        # Add requested DelimiterPoint
        new_point1 = self.__add_requested_delimiter_point(
            self.__requested_delimiter_point.get_coordinates(),
            (neighbor1, neighbor2), builder
        )

        # If the edge belongs to both Comet and Head contour
        if (neighbor1.get_roommate() is not None and
            neighbor2.get_roommate() is not None):

            neighbor1_roommate_neighbors_id_list = \
                [point.get_id() for point in 
                 neighbor1.get_roommate().get_delimiter_point().get_neighbors()]

            neighbor2_roommate_neighbors_id_list = \
                [point.get_id() for point in
                 neighbor2.get_roommate().get_delimiter_point().get_neighbors()]

            if (neighbor1.get_roommate().get_delimiter_point_id() in 
                neighbor2_roommate_neighbors_id_list and
                neighbor2.get_roommate().get_delimiter_point_id() in
                neighbor1_roommate_neighbors_id_list):

                builder = self.get_contour_builder(
                    neighbor1.get_roommate().get_delimiter_point_type())

                new_point2 = self.__add_requested_delimiter_point(
                    self.__requested_delimiter_point.get_coordinates(),
                    (neighbor1.get_roommate().get_delimiter_point(), 
                     neighbor2.get_roommate().get_delimiter_point()),
                    builder
                )

            make_roommates(new_point1, new_point2)


    ''' 
        Returns the BuildingContourState instance depending on given
        DelimiterPointType.
    '''
    def get_contour_builder(self, contour_type):

        if contour_type == DelimiterPointType.TAIL:
            return TailContourBuilder.get_instance()
        return HeadContourBuilder.get_instance()

    ''' Returns all the DelimiterPoints. '''
    def get_all_points(self):
    
        delimiter_point_list = []

        # Add Head points
        delimiter_point_list += CanvasModel.get_instance().get_all_head_points()
        # Add Comet points
        delimiter_point_list += CanvasModel.get_instance().get_all_tail_points()

        return delimiter_point_list
        
    ''' Returns all the tail contours DelimiterPoints. '''
    def get_all_tail_points(self):
        return self.__get_points(self.__tail_contour_dict)

    ''' Returns all the Head contours DelimiterPoints. '''
    def get_all_head_points(self):
        return self.__get_points(self.__head_contour_dict)
        
    ''' Returns the DelimiterPoints from the given contour dictionary. '''
    def __get_points(self, contour_dict):

        delimiter_point_list = []
        for (_, contour) in contour_dict.items():
            delimiter_point_list += [p for (_, p) in contour.get_delimiter_point_dict().items()]

        return delimiter_point_list 
        
    ''' 
        Deletes the DelimiterPoints with given IDs on given list. If the list
        is empty, the requested points to be deleted are the selected ones.
    '''    
    def delete_delimiter_points(self, selected_delimiter_point_list):
            
        # For each requested DelimiterPoint to be deleted
        for selected_delimiter_point in selected_delimiter_point_list:
        
            if selected_delimiter_point.get_type() == DelimiterPointType.TAIL:
                canvas_contour_dict = self.__tail_contour_dict
            else:
                canvas_contour_dict = self.__head_contour_dict
                              
            canvas_contour = canvas_contour_dict[
                selected_delimiter_point.get_canvas_contour_id()]     
            delimiter_point = canvas_contour.get_delimiter_point_dict()[
                selected_delimiter_point.get_id()]
            
            # Remove itself from its local neighborhood
            for neighbor in delimiter_point.get_neighbors():                                             
                neighbor.get_neighbors().remove(delimiter_point)
                
            # Remove from the CanvasContour it belongs to
            del canvas_contour.get_delimiter_point_dict()[delimiter_point.get_id()]
                    
            # Contour is no longer closed
            canvas_contour.set_closed(False)        
            
            # Remove Contour object from the dictionary if has no points
            if len(canvas_contour.get_delimiter_point_dict()) == 0:
                del canvas_contour_dict[canvas_contour.get_id()]
                
            # If DelimiterPoint has roommate, its roommate has no
            # longer a roommate
            if delimiter_point.get_roommate() is not None:
                delimiter_point.get_roommate().get_delimiter_point().\
                    set_roommate(None) 

            # Remove from the DelimiterPointSelection
            if delimiter_point.get_id() in self.__delimiter_point_selection.get_dict().keys():
                del self.__delimiter_point_selection.get_dict()[delimiter_point.get_id()]

    ''' Returns the CanvasContour with given ID. '''
    def get_canvas_contour(self, delimiter_point_type, canvas_contour_id):
    
        if delimiter_point_type == DelimiterPointType.TAIL:
            canvas_contour_dict = self.__tail_contour_dict
        else:
            canvas_contour_dict = self.__head_contour_dict
            
        return canvas_contour_dict[canvas_contour_id]

    ''' Returns the DelimiterPoint with given ID. '''
    def get_delimiter_point(self, delimiter_point_id, delimiter_point_type, canvas_contour_id):
    
        if delimiter_point_type == DelimiterPointType.TAIL:
            canvas_contour_dict = self.__tail_contour_dict
        else:
            canvas_contour_dict = self.__head_contour_dict
                   
        try:
            return canvas_contour_dict[canvas_contour_id].\
                   get_delimiter_point_dict()[delimiter_point_id]
        except:
            return None
    
        
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                               Private Methods                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #            
        
    ''' Adds the requested DelimiterPoint. '''
    def __add_requested_delimiter_point(
                         self, coordinates, neighbors, builder):

        # Neighbor1 is no longer local neighbor with neighbor2 and
        # viceversa
        neighbors[0].get_neighbors().remove(neighbors[1])
        neighbors[1].get_neighbors().remove(neighbors[0]) 

        # Create new point                 
        new_delimiter_point = builder.create_delimiter_point(
            coordinates, contour_id=neighbors[0].get_contour_id())

        make_neighbors(neighbors[0], new_delimiter_point)
        make_neighbors(neighbors[1], new_delimiter_point)

        return new_delimiter_point
        
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              Getters & Setters                              #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #    
    
    def get_tail_color(self):
        return self.__tail_color

    def set_tail_color(self, tail_color):
        self.__tail_color = tail_color

    def get_head_color(self):
        return self.__head_color

    def set_head_color(self, head_color):
        self.__head_color = head_color
    
    def get_selection_color(self):
        return self.__selection_color
        
    def set_selection_color(self, selection_color):
        self.__selection_color = selection_color    
        
    def get_selection_width(self):
        return self.__selection_width
        
    def set_selection_width(self, selection_width):
        self.__selection_width = selection_width
       
    def get_tail_contour_dict(self):
        return self.__tail_contour_dict
        
    def set_tail_contour_dict(self, tail_contour_dict):
        self.__tail_contour_dict = tail_contour_dict

    def get_head_contour_dict(self):
        return self.__head_contour_dict

    def set_head_contour_dict(self, head_contour_dict):
        self.__head_contour_dict = head_contour_dict
        
    def get_edge_width(self):
        return self.__edge_width
        
    def set_edge_width(self, edge_width):
        self.__edge_width = edge_width
        
    def get_edge_line_type(self):
        return self.__edge_line_type
        
    def set_edge_line_type(self, edge_line_type):
        self.__edge_line_type = edge_line_type
        
    def get_anchored_delimiter_point(self):
        return self.__anchored_delimiter_point
        
    def set_anchored_delimiter_point(self, anchored_delimiter_point):
        self.__anchored_delimiter_point = anchored_delimiter_point

    def get_requested_delimiter_point(self,):
        return self.__requested_delimiter_point
        
    def set_requested_delimiter_point(self, requested_delimiter_point):
        self.__requested_delimiter_point = requested_delimiter_point

    def get_selection_area_color(self):
        return self.__selection_area_color
        
    def set_selection_area_color(self, selection_area_color):
        self.__selection_area_color = selection_area_color
        
    def get_selection_distance(self):
        return self.__selection_distance
        
    def set_selection_distance(self, selection_distance):
        self.__selection_distance = selection_distance

    def get_delimiter_point_selection_color(self):
        return self.__delimiter_point_selection_color
        
    def set_delimiter_point_selection_color(self, delimiter_point_selection_color):
        self.__delimiter_point_selection_color = delimiter_point_selection_color
        
    def get_delimiter_point_selection(self):
        return self.__delimiter_point_selection
        
    def set_delimiter_point_selection(self, delimiter_point_selection):
        self.__delimiter_point_selection = delimiter_point_selection

    def get_free_selection_area_width(self):
        return self.__free_selection_area_width
        
    def set_free_selection_area_width(self, free_selection_area_width):
        self.__free_selection_area_width = free_selection_area_width
        
    def get_edge_selection_distance(self):
        return self.__edge_selection_distance
        
    def set_edge_selection_distance(self, edge_selection_distance):
        self.__edge_selection_distance = edge_selection_distance
        
    def get_selection_area(self):
        return self.__selection_area
        
    def set_selection_area(self, selection_area):
        self.__selection_area = selection_area
        
    def get_selected_pivot_delimiter_point(self):
        return self.__selected_pivot_delimiter_point
        
    def set_selected_pivot_delimiter_point(self, selected_pivot_delimiter_point):
        self.__selected_pivot_delimiter_point = selected_pivot_delimiter_point
        
    def get_root_delimiter_point(self):
        return self.__root_delimiter_point
        
    def set_root_delimiter_point(self, root_delimiter_point):
        self.__root_delimiter_point = root_delimiter_point
        
    def get_anchored_delimiter_point(self):
        return self.__anchored_delimiter_point
        
    def set_anchored_delimiter_point(self, anchored_delimiter_point):
        self.__anchored_delimiter_point = anchored_delimiter_point
        
    def get_anchored_delimiter_point_color(self):
        return self.__anchored_delimiter_point_color
        
    def set_anchored_delimiter_point_color(self, anchored_delimiter_point_color):
        self.__anchored_delimiter_point_color = anchored_delimiter_point_color
        
    def get_comet_being_edited_has_changed(self):
        return self.__comet_being_edited_has_changed

    def set_comet_being_edited_has_changed(self, comet_being_edited_has_changed):
        self.__comet_being_edited_has_changed = comet_being_edited_has_changed


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	SelectionArea                                                             #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class SelectionArea(metaclass=Singleton):

    '''
        The SelectionArea class. Implements Singleton pattern.
    '''

    def __init__(self, starting_point, ending_point=None):

        self.__starting_point = starting_point
        self.__ending_point = ending_point
        if ending_point is None:
            self.__ending_point = starting_point

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                  Methods                                    #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Returns the SelectionArea rect. '''
    def get_rect(self):

        x = min(self.__starting_point[0], self.__ending_point[0])
        y = min(self.__starting_point[1], self.__ending_point[1])
        width = abs(self.__starting_point[0] - self.__ending_point[0])
        height = abs(self.__starting_point[1] - self.__ending_point[1])
        return (x, y, width, height)

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              Getters & Setters                              #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_starting_point(self):
        return self.__starting_point

    def set_starting_point(self, starting_point):
        self.__starting_point = starting_point

    def get_ending_point(self):
        return self.__ending_point

    def set_ending_point(self, ending_point):
        self.__ending_point = ending_point



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	DelimiterPointSelection                                                   #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class DelimiterPointSelection(object):

    '''
        The DelimiterPointSelection class.
    '''

    ''' Initialization method. '''
    def __init__(self):

        self.__dict = {}
        self.__moved = False

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_dict(self):
        return self.__dict

    def set_dict(self, dict):
        self.__dict = dict

    def get_moved(self):
        return self.__moved

    def set_moved(self, moved):
        self.__moved = moved



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	SelectedDelimiterPoint                                                    #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class SelectedDelimiterPoint(object):

    '''
        The SelectedDelimiterPoint class.
    '''

    ''' Initialization method. '''
    def __init__(self, id, type, canvas_contour_id):

        self.__id = id
        self.__origin = None
        self.__type = type
        self.__canvas_contour_id = canvas_contour_id


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_id(self):
        return self.__id
        
    def set_id(self, id):
        self.__id = id

    def get_origin(self):
        return self.__origin

    def set_origin(self, origin):
        self.__origin = origin
        
    def get_type(self):
        return self.__type
        
    def set_type(self, type):
        self.__type = type
        
    def get_canvas_contour_id(self):
        return self.__canvas_contour_id
        
    def set_canvas_contour_id(self, canvas_contour_id):
        self.__canvas_contour_id = canvas_contour_id


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	RequestedDelimiterPoint                                                   #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class RequestedDelimiterPoint(metaclass=Singleton):

    '''
        The RequestedDelimiterPoint class. Implements Singleton pattern.
    '''

    ''' Initialization method. '''
    def __init__(self, coordinates, edge):

        self.__coordinates = coordinates
        self.__edge = edge


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_coordinates(self):
        return self.__coordinates

    def set_coordinates(self, coordinates):
        self.__coordinates = coordinates

    def get_edge(self):
        return self.__edge

    def set_edge(self, edge):
        self.__edge = edge



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	CanvasContour                                                             #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class CanvasContour(object):

    '''
        The CanvasContour class.
    '''

    # The ID Generator
    new_id = itertools.count()

    ''' Initialization method. '''
    def __init__(self, id=None):
    
        if id is None:
            self.__id = next(CanvasContour.new_id)
        else:
            self.__id = id
        self.__delimiter_point_dict = {}
        self.__closed = False


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              Getters & Setters                              #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_id(self):
        return self.__id

    def set_id(self, id):
        self.__id = id

    def get_delimiter_point_dict(self):
        return self.__delimiter_point_dict

    def set_delimiter_point_dict(self, delimiter_point_dict):
        self.__delimiter_point_dict = delimiter_point_dict

    def get_closed(self):
        return self.__closed

    def set_closed(self, closed):
        self.__closed = closed



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	DelimiterPointType                                                        #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class DelimiterPointType(object):

    '''
        The DelimiterPointType class.
    '''

    TAIL = 0
    HEAD = 1

   
   
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	DelimiterPoint                                                            #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class DelimiterPoint(object):

    '''
        The DelimiterPoint class.
    '''

    # The ID Generator
    new_id = itertools.count()

    ''' Initialization method. '''
    def __init__(self, coordinates, type, id):

        if id is None:
            self.__id = next(DelimiterPoint.new_id)
        else:
            self.__id = id
        self.__contour_id = None
        self.__coordinates = coordinates
        self.__neighbors = []
        self.__roommate = None
        self.__type = type  

    def to_string(self):

        string = "ID=" + str(self.__id) + "\n"
        string += "ContourID=" + str(self.__contour_id) + "\n"
        string += "Neighbors = " + str([point.get_id() for point in self.__neighbors])
        return string   

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              Getters & Setters                              #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_id(self):
        return self.__id

    def get_contour_id(self):
        return self.__contour_id

    def set_contour_id(self, contour_id):
        self.__contour_id = contour_id

    def get_coordinates(self):
        return self.__coordinates

    def set_coordinates(self, coordinates):
        self.__coordinates = coordinates

    def get_neighbors(self):
        return self.__neighbors

    def set_neighbors(self, neighbors):
        self.__neighbors = neighbors

    def get_roommate(self):
        return self.__roommate

    def set_roommate(self, roommate):
        self.__roommate = roommate

    def get_type(self):
        return self.__type

    def set_type(self, type):
        self.__type = type
               


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	Roommate                                                                  #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
        
class Roommate(object):

    '''
        The Roommate class.
    '''
    
    def __init__(self, delimiter_point_type, canvas_contour_id, 
            delimiter_point_id):
            
        self.__delimiter_point_type = delimiter_point_type
        self.__canvas_contour_id = canvas_contour_id
        self.__delimiter_point_id = delimiter_point_id
        
 
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                   Methods                                   #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
 
    ''' Returns the DelimiterPoint associated to this object. '''
    def get_delimiter_point(self):

        return CanvasModel.get_instance().get_delimiter_point(
            self.__delimiter_point_id,
            self.__delimiter_point_type,
            self.__canvas_contour_id
        )
       
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              Getters & Setters                              #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_delimiter_point_type(self):
        return self.__delimiter_point_type
        
    def set_delimiter_point_type(self, delimiter_point_type):
        self.__delimiter_point_type = delimiter_point_type
        
    def get_canvas_contour_id(self):
        return self.__canvas_contour_id
        
    def set_canvas_contour_id(self, canvas_contour_id):
        self.__canvas_contour_id = canvas_contour_id
        
    def get_delimiter_point_id(self):
        return self.__delimiter_point_id
        
    def set_delimiter_point_id(self, delimiter_point_id):
        self.__delimiter_point_id



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	CometContourBuilder                                                       #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class CometContourBuilder(metaclass=Singleton):

    '''
        The CometContourBuilder abstract class.
    '''

    POINT_TYPE = None
     
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
# 	                                Methods                                   #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #        
 
    ''' Behaviour creating a new DelimiterPoint. '''
    def create_delimiter_point(self, coordinates, id=None, contour_id=None,
            roommate=None):
                 
        delimiter_point = DelimiterPoint(coordinates, self.POINT_TYPE, id)
        
        # If a CanvasContour ID is NOT given
        if contour_id is None:
        
            # Create a new CanvasContour
            canvas_contour = CanvasContour()
            # Add the contour to the contour dict
            self.get_contour_dict()[canvas_contour.get_id()] = canvas_contour
                
        # If a CanvasContour ID is given
        else:
        
            # Use existent CanvasContour 
            if contour_id in self.get_contour_dict().keys():
                canvas_contour = self.get_contour_dict()[contour_id]
                
            # Otherwise create new CanvasContour with given ID
            else:
                canvas_contour = CanvasContour(contour_id)
                self.get_contour_dict()[canvas_contour.get_id()] = canvas_contour
        
        # Add the new DelimiterPoint to the Contour DelimiterPoint dict
        delimiter_point.set_contour_id(canvas_contour.get_id())
        canvas_contour.get_delimiter_point_dict()[
            delimiter_point.get_id()] = delimiter_point  
            
        if roommate is not None and roommate.get_delimiter_point() is not None: 
            make_roommates(
                delimiter_point,
                roommate.get_delimiter_point()
            )

        return delimiter_point

    ''' Behaviour connecting two DelimiterPoints. '''
    def connect_points(self, src_point, dst_point, canvas_contour_id=None):
        
        src_contour_id = src_point.get_contour_id()
        dst_contour_id = dst_point.get_contour_id()

        # They are now local neighbors
        make_neighbors(src_point, dst_point)

        # They belong to different contours
        if src_point.get_contour_id() != dst_point.get_contour_id():

            # Make a new CanvasContour with the union
            new_contour = CanvasContour(canvas_contour_id)
            new_contour.get_delimiter_point_dict().update(
                self.get_contour_dict()[src_contour_id].get_delimiter_point_dict())
            new_contour.get_delimiter_point_dict().update(
                self.get_contour_dict()[dst_contour_id].get_delimiter_point_dict())
            
            # The points belong to the new Contour
            for (_, delimiter_point) in new_contour.get_delimiter_point_dict().items():
                delimiter_point.set_contour_id(new_contour.get_id())

            # Add the new CanvasContour to the CanvasContour dictionary
            self.get_contour_dict()[new_contour.get_id()] = new_contour
            # Remove the src and dst old contours
            del self.get_contour_dict()[src_contour_id]
            del self.get_contour_dict()[dst_contour_id] 

    ''' Behaviour disconnecting two DelimiterPoints. '''
    def disconnect_points(self, src_point, dst_point,
            src_point_previous_contour_id, dst_point_previous_contour_id):
    
        # They are no longer local neighbors
        unmake_neighbors(src_point, dst_point)
        
        # If they belonged to different CanvasContours before the connection
        if src_point_previous_contour_id != dst_point_previous_contour_id:
        
            # Remove the current CanvasContour from the CanvasContour dict
            del self.get_contour_dict()[src_point.get_contour_id()]       
            # Split it into 2 new CanvasContours
            canvas_contour1 = CanvasContour(src_point_previous_contour_id)
            canvas_contour2 = CanvasContour(dst_point_previous_contour_id)
            
            # Add the corresponding DelimiterPoints to the new CanvasContours
            delimiter_point_list = get_local_neighbors(src_point)
            for delimiter_point in delimiter_point_list:
                delimiter_point.set_contour_id(canvas_contour1.get_id())
            canvas_contour1.set_delimiter_point_dict(
                {p.get_id():p for p in delimiter_point_list}) 
            
            delimiter_point_list = get_local_neighbors(dst_point)
            for delimiter_point in delimiter_point_list:
                delimiter_point.set_contour_id(canvas_contour2.get_id())
            canvas_contour2.set_delimiter_point_dict(
                {p.get_id():p for p in delimiter_point_list})
            
            # Add both contours to the CanvasContour dict
            self.get_contour_dict()[canvas_contour1.get_id()] = canvas_contour1
            self.get_contour_dict()[canvas_contour2.get_id()] = canvas_contour2
         
        # If they were part of the same CanvasContour before the connection
        else:
            # The CanvasContour is no longer 'closed'
            self.get_contour_dict()[src_point.get_contour_id()].\
                set_closed(False)

    ''' Sets the anchored DelimiterPoint. '''
    def set_anchored_delimiter_point_method(self, event):

        # When a DelimiterPoint is root
        if CanvasModel.get_instance().get_root_delimiter_point() is not None:

            anchored_point = self.set_anchored_delimiter_point_with_root(
                                 (int(event.x), int(event.y)))

        # When a there isn't a root DelimiterPoint
        else:

            anchored_point = self.set_anchored_delimiter_point_with_no_root(
                                 (int(event.x), int(event.y)))

        # Set anchored DelimiterPoint
        CanvasModel.get_instance().set_anchored_delimiter_point(anchored_point)

    ''' Setting the anchored DelimiterPoint when a point is root. '''
    def set_anchored_delimiter_point_with_root(self, mouse_coordinates):

        # DelimiterPoints that cannot be anchored
        forbidden_id_list = self.get_forbidden_id_list(
                                CanvasModel.get_instance().get_root_delimiter_point())

        (comet_candidate, head_candidate) = \
            self.get_anchoring_candidates(forbidden_id_list,
                mouse_coordinates)

        return self.choose_anchored_delimiter_point(
            comet_candidate, head_candidate)

    ''' Setting the anchored DelimiterPoint when no point is root. '''
    def set_anchored_delimiter_point_with_no_root(self, mouse_coordinates):

        forbidden_id_list = get_delimiter_points_ids_from_closed_contours(
                                self.get_contour_dict())

        (comet_candidate, head_candidate) = \
            self.get_anchoring_candidates(
                forbidden_id_list, mouse_coordinates)

        return self.choose_anchored_delimiter_point(
            comet_candidate, head_candidate)

    ''' 
        Returns the Comet contour DelimiterPoint and Head contour
        DelimiterPoint candidates for anchoring.
    '''
    def get_anchoring_candidates(self, forbidden_id_list, mouse_coordinates):

        # First candidate comes from the comet contour DelimiterPoints
        candidate1 = see_anchoring_with_delimiter_point_list(
                        CanvasModel.get_instance().get_all_tail_points(),
                        forbidden_id_list, mouse_coordinates)

        # Second candidate comes from the head contour DelimiterPoints
        candidate2 = see_anchoring_with_delimiter_point_list(
                        CanvasModel.get_instance().get_all_head_points(),
                        forbidden_id_list, mouse_coordinates)

        return (candidate1, candidate2)

    ''' 
        Returns the ID list of DelimiterPoints that cannot be
        anchored when given DelimiterPoint is root.
    '''
    def get_forbidden_id_list(self, delimiter_point):

        # Points that belong to a closed Contour cannot be anchored
        points_from_closed_contours = \
            get_delimiter_points_ids_from_closed_contours(
                self.get_contour_dict())
        

        # Own root cannot be anchored
        forbidden_id_list = union(points_from_closed_contours, 
                                [delimiter_point.get_id()])

        # Neighbors cannot be anchored
        forbidden_id_list = union(forbidden_id_list,
            [neighbor.get_id() for neighbor
             in delimiter_point.get_neighbors()])

        return forbidden_id_list

    '''
        The anchored DelimiterPoint is now the root.
    '''
    def select_anchored_delimiter_point(self):
        CanvasModel.get_instance().set_root_delimiter_point(
            CanvasModel.get_instance().get_anchored_delimiter_point())
        CanvasModel.get_instance().set_anchored_delimiter_point(None)

    ''' 
        Creates a new DelimiterPoint and connects this new point and the source
        given one.
    '''
    def create_and_connect_points(self, src_point, coordinates,
            delimiter_point_id=None, roommate=None):

        # Create the new point
        delimiter_point = self.create_delimiter_point(
                              coordinates, delimiter_point_id,
                              src_point.get_contour_id(),
                              roommate)

        # Connect the source and the new created point
        self.connect_points(src_point, delimiter_point)

        return delimiter_point



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	TailContourBuilder                                                        #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class TailContourBuilder(CometContourBuilder):

    '''
        The TailContourBuilder class.
    '''
      
    POINT_TYPE = DelimiterPointType.TAIL
      
    ''' Initialization method. '''
    def __init__(self):

        # Parent constructor
        super().__init__()
        
    ''' Returns the contour dictionary the class works with. '''
    def get_contour_dict(self):            
        return CanvasModel.get_instance().get_tail_contour_dict()

    ''' Choosing anchored DelimiterPoint behaviour. '''
    def choose_anchored_delimiter_point(self, comet_candidate, head_candidate):

        if comet_candidate is not None:

            if head_candidate is None:

                return comet_candidate[0]

            else:

                if comet_candidate[1] <= head_candidate[1]:
                    return comet_candidate[0]
                else:
                    return head_candidate[0]
        else:

            if head_candidate is not None:
                return head_candidate[0]
     
    ''' Returns the color for drawing. '''     
    def get_color(self):
        return CanvasModel.get_instance().get_tail_color()
      
      
      
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	HeadContourBuilder                                                        #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class HeadContourBuilder(CometContourBuilder):

    '''
        The HeadContourBuilder class.
    '''
       
    POINT_TYPE = DelimiterPointType.HEAD  
       
    ''' Initialization method. '''
    def __init__(self):

        # Parent constructor
        super().__init__()
        
  
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                  Methods                                    #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #  
  
    ''' Returns the contour dictionary that the class works with. '''
    def get_contour_dict(self):            
        return CanvasModel.get_instance().get_head_contour_dict()
        
    ''' Choosing anchored DelimiterPoint behaviour. '''
    def choose_anchored_delimiter_point(self, comet_candidate, head_candidate):

        if comet_candidate is not None:

            if head_candidate is None:

                return comet_candidate[0]

            else:

                if head_candidate[1] <= comet_candidate[1]:
                    return head_candidate[0]
                else:
                    return comet_candidate[0]
        else:

            if head_candidate is not None:
                return head_candidate[0]

    ''' Returns the color for drawing. '''
    def get_color(self):
        return CanvasModel.get_instance().get_head_color()
        
        
        
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                            Auxiliary Methods                                #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

''' Union of two given lists. '''
def union(list1, list2):
    return list(set(list1) | set(list2))

''' Makes two DelimiterPoints 'neighbors'. '''
def make_neighbors(delimiter_point1, delimiter_point2):

    delimiter_point1.get_neighbors().append(delimiter_point2)
    delimiter_point2.get_neighbors().append(delimiter_point1)
  
''' Makes two DelimiterPoints not being neighbors anymore. '''  
def unmake_neighbors(delimiter_point1, delimiter_point2):

    delimiter_point1.get_neighbors().remove(delimiter_point2)
    delimiter_point2.get_neighbors().remove(delimiter_point1)
    
''' Makes two DelimiterPoints 'roommates'. '''
def make_roommates(delimiter_point1, delimiter_point2):

    delimiter_point1.set_roommate(
        Roommate(
            delimiter_point2.get_type(),
            delimiter_point2.get_contour_id(),
            delimiter_point2.get_id()            
        )
    )
    delimiter_point2.set_roommate(
        Roommate(
            delimiter_point1.get_type(),
            delimiter_point1.get_contour_id(),
            delimiter_point1.get_id()            
        )
    )    
    
''' 
    Returns a list with all the local neighbors from given DelimiterPoint.
    The contour the DelimiterPoint belongs to must not be closed. 
'''    
def get_local_neighbors(delimiter_point):

    local_neighbors = [delimiter_point]
    for neighbor in delimiter_point.get_neighbors():
        local_neighbors = union(
            local_neighbors,
            __get_local_neighbors(
                neighbor,
                delimiter_point.get_id(),
                []
            )
        )
            
    return local_neighbors        
   
''' 'get_local_neighbors' recursive auxiliary method. '''   
def __get_local_neighbors(delimiter_point, sender_id, local_neighbors):    
    
    for neighbor in delimiter_point.get_neighbors():
        if neighbor.get_id() != sender_id:
            local_neighbors = union(
                local_neighbors,
                __get_local_neighbors(
                    neighbor,
                    delimiter_point.get_id(),
                    []
                )
            )
                
    return union(local_neighbors, [delimiter_point])            
    
''' 
    Returns whether given first CanvasContour is nested to second
    CanvasContour.
'''
def contours_are_nested(canvas_contour1, canvas_contour2):

    point_list = [point.get_coordinates() for (_, point) in
                  canvas_contour2.get_delimiter_point_dict().items()]
    cv2_contour = utils.list_to_contour(point_list)        
         
    for (_, delimiter_point) in canvas_contour1.get_delimiter_point_dict().items():
        
        if (utils.is_point_inside_contour(
            cv2_contour, delimiter_point.get_coordinates())):
            return True

    return False 

''' 
    Returns a list with the DelimiterPoint identifiers that belong to a
    closed CanvasContour.
'''
def get_delimiter_points_ids_from_closed_contours(contour_dict):

    point_ids_list = []

    for (_, contour) in contour_dict.items():
        if contour.get_closed():
            point_ids_list += [point.get_id() for (_, point) in 
                               contour.get_delimiter_point_dict().items()]

    return point_ids_list
    
''' Returns the candidate to be the anchored DelimiterPoint. '''
def see_anchoring_with_delimiter_point_list(delimiter_point_list,
                                forbidden_id_list, mouse_coordinates_point):

    # See anchoring with the DelimiterPoints except the ones that belongs
    # to the forbidden list
    candidate = None
    for delimiter_point in delimiter_point_list:

        if delimiter_point.get_id() not in forbidden_id_list:

            euclidean_distance = ( utils.euclidean_distance(
                                   delimiter_point.get_coordinates(), 
                                   mouse_coordinates_point)
                                  )
            if euclidean_distance < CanvasModel.ANCHORING_DISTANCE:

                if candidate is None:
                    candidate = (delimiter_point, euclidean_distance)
                else:
                    if euclidean_distance < candidate[1]:
                        candidate = (delimiter_point, euclidean_distance)

    return candidate
   

''' 
    Checks if a CanvasContour is closed. 
'''
def check_contour_is_closed(contour, root_point):
        
    delimiter_point_id_list = []

    for neighbor in root_point.get_neighbors():

        delimiter_point_id_list = union(
            delimiter_point_id_list,
            __check_contour_is_closed(
                neighbor,
                root_point.get_id(),
                root_point.get_id(),
                []
            ))

    contour.set_closed(root_point.get_id() in delimiter_point_id_list)
    return delimiter_point_id_list

''' 
    Recursive function that returns a list with the DelimiterPoints that
    closes the CanvasContour.
'''
def __check_contour_is_closed(delimiter_point, sender_id, root_id,
                                                     delimiter_point_id_list):

    if len(delimiter_point.get_neighbors()) < 2:
        return []

    # Point is root
    if delimiter_point.get_id() == root_id:
        return union(delimiter_point_id_list.copy(), [root_id])

    for neighbor in delimiter_point.get_neighbors():

        # Neighbor isn't sender
        if neighbor.get_id() != sender_id:

            delimiter_point_id_list = union(
                delimiter_point_id_list,
                __check_contour_is_closed(
                    neighbor,
                    delimiter_point.get_id(),
                    root_id,
                    []
                )
            )

    if len(delimiter_point_id_list) > 0:
        return union(delimiter_point_id_list, [delimiter_point.get_id()])

    return []   