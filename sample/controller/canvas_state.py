# -*- encoding: utf-8 -*-

'''
    The canvas_state module.
'''

import itertools
import cairo
import math

# PyGObject imports
import gi
import cairo
gi.require_version('Gtk', '3.0')
gi.require_foreign("cairo")
from gi.repository import Gdk
from gi.repository import Gtk

# Custom imports
import model.utils as utils
from singleton import Singleton
from controller.buttons import MouseButtons
from model.canvas_model import CanvasModel, DelimiterPointType, DelimiterPointSelection, \
    SelectionArea, DelimiterPoint, CanvasContour, SelectedDelimiterPoint, RequestedDelimiterPoint, \
    TailContourBuilder, HeadContourBuilder, union, see_anchoring_with_delimiter_point_list




# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	State                                                                     #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class State(metaclass=Singleton):

    '''
        The State class.
    '''

    ''' Initialization method. '''
    def __init__(self, context):
    
        self._context = context



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	CanvasState                                                               #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class CanvasState(State):

    '''
        The CanvasState abstract class. Extends from State.
    '''

    ''' Initialization method. '''
    def __init__(self, context):

        super().__init__(context)

    ''' Mouse entrance behaviour. '''
    def on_mouse_enter(self, *args):
        self._context.get_view().get_main_window().get_canvas().set_cursor("default")

    ''' Mouse exit behaviour. '''
    def on_mouse_leave(self, *args):
        self._context.get_view().get_main_window().get_canvas().set_mouse_coordinates(None)

    ''' Mouse motion behaviour. '''
    def on_mouse_motion(self, *args):
        raise NotImplementedError("Method must be implemented.")

    ''' Mouse clicking behaviour. '''
    def on_mouse_click(self, *args):
        raise NotImplementedError("Method must be implemented.")

    ''' Mouse release behaviour. '''
    def on_mouse_release(self, *args):
        raise NotImplementedError("Method must be implemented.")

    ''' Key press behaviour. '''
    def on_key_press_event(self, *args):
        raise NotImplementedError("Method must be implemented.")

    ''' Drawing behaviour. '''
    def draw(self, *args):
        raise NotImplementedError("Method must be implemented.")

    ''' Get editing behaviour. '''
    def get_editing(self, *args):
        pass 

    ''' Restart behaviour. '''
    def reset_parameters(self, *args):
        pass

    ''' Update buttons sensitivity behaviour. '''
    def update_buttons_sensitivity(self, *args):
        pass

    ''' Transition to EditingSelectionState behaviour. '''
    def transition_to_editing_selection_state(self, *args):
        pass

    ''' Transition to EditingBuildingState behaviour. '''
    def transition_to_editing_building_state(self, *args):
        pass

    ''' Transition to BuildingTailContourState behaviour. '''
    def transition_to_building_tail_contour_state(self, *args):
        pass

    ''' Transition to BuildingHeadContourState behaviour. '''
    def transition_to_building_head_contour_state(self, *args):
        pass        



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	ActionState                                                               #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class ActionState(CanvasState):

    '''
        The ActionState class. Extends from CanvasState.
    '''

    ''' Initialization method. '''
    def __init__(self, context):
        super().__init__(context)

    ''' Returns the anchored DelimiterPoint. '''
    def get_anchored_delimiter_point(self):        
        return CanvasModel.get_instance().get_anchored_delimiter_point()

    ''' Sets the anchored DelimiterPoint. '''
    def set_anchored_delimiter_point(self, anchored_delimiter_point):
        CanvasModel.get_instance().set_anchored_delimiter_point(
            anchored_delimiter_point)

    ''' Returns a list with all active Sample DelimiterPoints. '''
    def get_all_points(self):

        if CanvasEditingState.get_instance() is not None:

            return CanvasEditingState.get_instance().get_all_points()

    ''' Draws a DelimiterPoint. '''
    def draw_delimiter_point(self, cairo_context, delimiter_point):
        CanvasEditingState.get_instance().draw_delimiter_point(
            cairo_context, delimiter_point)

    ''' 
        Returns all the active Sample DelimiterPoints that belong to the 
        tail contour.
    '''
    def get_all_tail_points(self):
        return CanvasEditingState.get_instance().get_all_tail_points()

    ''' 
        Returns all the active Sample DelimiterPoints that belong to the 
        head contour.
    '''
    def get_all_head_points(self):
        return CanvasEditingState.get_instance().get_all_head_points()



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	CanvasSelectionState                                                      #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class CanvasSelectionState(CanvasState):

    '''
        The CanvasSelectionState class. Implements State and Observer
        patterns.
    '''

    ''' Initialization method. '''
    def __init__(self, context):

        super().__init__(context)

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
# 	                      CanvasState Implementation                          #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

    ''' CanvasState.on_mouse_click() implementation method. '''
    def on_mouse_click(self, event):
        
        # Selection and scrollbars movement
        if event.button == MouseButtons.LEFT_BUTTON:

            # Select comet
            self.__check_comet_selection((int(event.x), int(event.y)))

            # Scrollbars movement
            self._context.get_view().get_main_window().get_canvas().set_move_reference_point(
                (int(event.x_root), int(event.y_root)))

        # Pop up CanvasSelectionState context menu
        elif event.button == MouseButtons.RIGHT_BUTTON:                
            self._context.get_view().get_main_window().get_canvas().\
                pop_up_canvas_selection_state_menu(event)

    ''' CanvasState.on_mouse_release() implementation method. '''
    def on_mouse_release(self, event):

        # Change to 'default' cursor
        self._context.get_view().get_main_window().get_canvas().set_cursor("default")

    ''' CanvasState.on_mouse_motion() implementation method. '''
    def on_mouse_motion(self, event):

        # Holding left button -> move scrollbars
        if event.state & Gdk.EventMask.BUTTON_PRESS_MASK:

            # Change to 'move' cursor
            self._context.get_view().get_main_window().get_canvas().set_cursor("move")
           
            # Get movement direction of mouse
            mouse_point = int(event.x_root), int(event.y_root)
            axis_direction = self.__get_direction(
                mouse_point, self._context.get_view().get_main_window().get_canvas().get_move_reference_point())
            self._context.get_view().get_main_window().get_canvas().move_scrollbars(axis_direction)
            # Update reference point with current mouse location
            self._context.get_view().get_main_window().get_canvas().set_move_reference_point(mouse_point)

    ''' CanvasState.on_key_press_event() implementation method. '''
    def on_key_press_event(self, event):

        keyval = event.keyval
        keyval_name = Gdk.keyval_name(keyval)

        # Supr -> delete selected comet
        if keyval_name == "Delete":
            self._context.delete_selected_comet()

    ''' CanvasState.draw() implementation method. '''
    def draw(self, cairo_context):

        # Draw comet selection rect
        self.__draw_comet_selection(cairo_context)

    ''' CanvasState.get_editing() implementation method. '''
    def get_editing(self):
        return False

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
# 	                                Methods                                   #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Draws a rectangle around the selected comet contour. '''
    def __draw_comet_selection(self, cairo_context):

        selected_comet_view = self._context.\
                                  get_active_sample_selected_comet_view()
        # A comet must be selected
        if selected_comet_view is not None:

            # Set Brush properties
            brush = self._context.get_brush()
            brush.set_width(CanvasModel.get_instance().get_selection_width())
            brush.set_color(CanvasModel.get_instance().get_selection_color())

            contour = selected_comet_view.get_scaled_tail_contour()
            if contour is None:
                contour = selected_comet_view.get_scaled_head_contour()

            # Draw
            selection_line = utils.contour_to_list(
                       utils.get_contour_rect_contour(contour))
            brush.draw_line(cairo_context, selection_line, close=True)

    ''' Returns the mouse pointer's movement direction. '''
    def __get_direction(self, point, reference_point):

        x_axis = reference_point[0] - point[0]
        y_axis = reference_point[1] - point[1]
        return x_axis, y_axis

    ''' If clicked point belongs to a comet contour, comet is selected. '''
    def __check_comet_selection(self, point):

        for comet_view in self._context.get_view().get_active_sample_comet_view_list():
        
            comet_contour = comet_view.get_scaled_tail_contour()
            if comet_contour is None:
                comet_contour = comet_view.get_scaled_head_contour()
                
            # Select comet if point is inside the comet    
            if utils.is_point_inside_contour(comet_contour, point):
            
                self._context.select_comet(
                    self._context.get_active_sample_id(), 
                    comet_view.get_id()
                )

 
 
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	CanvasEditingState                                                        #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class CanvasEditingState(CanvasState):

    '''
        The CanvasEditingState class.
    '''

    ''' Initialization method. '''
    def __init__(self, context):

        # CanvasState constructor
        super().__init__(context)

        # State
        if context.get_view().get_main_window().get_canvas().get_editing_selection_button().get_active():
            self.__state = EditingSelectionState(context)
            
        elif context.get_view().get_main_window().get_canvas().get_building_button().get_active():
            self.__state = EditingBuildingState(context)

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
# 	                               Methods                                    #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Restart behaviour. '''
    def restart(self):
    
        CanvasModel.get_instance().set_anchored_delimiter_point(None)
        CanvasModel.get_instance().set_requested_delimiter_point(None)
        self.__state.restart()

    ''' Update buttons sensitivity behaviour. '''
    def update_buttons_sensitivity(self):
        self.__state.update_buttons_sensitivity()

    ''' State transition to EditingSelectionState. '''
    def transition_to_editing_selection_state(self, context):
        self.__state = EditingSelectionState(context)

    ''' State transition to EditingBuildingState. '''
    def transition_to_editing_building_state(self, context):
        self.__state = EditingBuildingState(context)

    ''' State's state transition to BuildingTailContourState. '''
    def transition_to_building_tail_contour_state(self, context):
        self.__state.transition_to_building_tail_contour_state(context)

    ''' State's state transition to BuildingHeadContourState. '''
    def transition_to_building_head_contour_state(self, context):
        self.__state.transition_to_building_head_contour_state(context)

    ''' 
        Tells the context to pop up the EditingSelectionState context
        menu1.
     '''
    def pop_up_editing_selection_menu1(self, event):
        self._context.get_view().get_main_window().get_canvas().pop_up_editing_selection_menu1(event)

    ''' 
        Tells the context to pop up the EditingSelectionState context
        menu2.
    '''
    def pop_up_editing_selection_menu2(self, event):
        self._context.get_view().get_main_window().get_canvas().pop_up_editing_selection_menu2(event)
    

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
# 	                      CanvasState Implementation                          #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' CanvasState.on_mouse_click() implementation method. '''
    def on_mouse_click(self, event):
        self.__state.on_mouse_click(event)

    ''' CanvasState.on_mouse_release() implementation method. '''
    def on_mouse_release(self, event):
        self.__state.on_mouse_release(event)

    ''' CanvasState.on_mouse_motion() implementation method. '''
    def on_mouse_motion(self, event):
        self.__state.on_mouse_motion(event)

    ''' CanvasState.on_key_press_event() implementation method. '''
    def on_key_press_event(self, event):
        self.__state.on_key_press_event(event)

    ''' CanvasState.draw() implementation method. '''
    def draw(self, cairo_context):

        # Draw edges         
        self.__draw_edges(cairo_context)
 
        # Draw DelimiterPoints
        self.__draw_delimiter_points(cairo_context)

        # State drawing
        self.__state.draw(cairo_context)
        
    ''' Draws the edges of the comets being built. '''
    def __draw_edges(self, cairo_context):

        # Set Brush properties
        brush = self._context.get_brush()
        brush.set_width(CanvasModel.get_instance().get_edge_width())
        brush.set_line_type(CanvasModel.get_instance().get_edge_line_type())

        brush.set_color(self._context.get_tail_color())
        # Draw tail contours edges
        for (_, tail_contour) in CanvasModel.get_instance().get_tail_contour_dict().items():
            self.__draw_edge_lines(
                cairo_context, tail_contour.get_delimiter_point_list())

        brush.set_color(self._context.get_head_color())
        # Draw head contour edges            
        for (_, head_contour) in CanvasModel.get_instance().get_head_contour_dict().items():
            self.__draw_edge_lines(
                cairo_context, head_contour.get_delimiter_point_list())

    ''' 
        Draws the edge lines between the DelimiterPoints in the given list.
    '''
    def __draw_edge_lines(self, cairo_context, delimiter_point_list):

        # Draw contour edges
        for delimiter_point in delimiter_point_list:

            line = []

            # Draw line to neighbor DelimiterPoint
            for neighbor in delimiter_point.get_neighbors():

                line = [delimiter_point.get_coordinates(),
                        neighbor.get_coordinates()]

                cairo_context.new_sub_path()
                self._context.get_brush().draw_line( 
                    cairo_context, line, close=False)

    ''' 
        Draws the DelimiterPoints, the points that connect the contours
        edges.
    '''
    def __draw_delimiter_points(self, cairo_context):

        self._context.get_brush().set_color(
            self._context.get_tail_color())
        # Draw Comet delimiter points           
        for (_, tail_contour) in CanvasModel.get_instance().get_tail_contour_dict().items():
            for delimiter_point in tail_contour.get_delimiter_point_list():
                self.draw_delimiter_point(cairo_context, delimiter_point)              

        self._context.get_brush().set_color(
            self._context.get_head_color())
        # Draw Head delimiter points           
        for (_, head_contour) in CanvasModel.get_instance().get_head_contour_dict().items():
            for delimiter_point in head_contour.get_delimiter_point_list():
                self.draw_delimiter_point(cairo_context, delimiter_point) 

    ''' Draws a given DelimiterPoint. '''
    def draw_delimiter_point(self, cairo_context, delimiter_point):

        if delimiter_point.get_roommate() is None:

            self._context.get_brush().draw_delimiter_point(
                cairo_context,
                delimiter_point.get_coordinates(),
                CanvasModel.DELIMITER_POINT_SIZE
            )

        else:

            self._context.get_brush().draw_round_delimiter_point(
                cairo_context,
                delimiter_point.get_coordinates(),
                CanvasModel.DELIMITER_POINT_SIZE
            )

    ''' CanvasState.get_editing() implementation method. '''
    def get_editing(self):
        return True

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
# 	                                Methods                                   #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Returns all the DelimiterPoints. '''
    def get_all_points(self):
        return CanvasModel.get_instance().get_all_delimiter_points()

    ''' Returns all the tail contours DelimiterPoints. '''
    def get_all_tail_points(self):
        return CanvasModel.get_instance().get_all_tail_points()

    ''' Returns all the Head contours DelimiterPoints. '''
    def get_all_head_points(self):
        return CanvasModel.get_instance().get_all_head_points()
 
    ''' Deletes the DelimiterPoints that belong to the given list. '''
    def delete_delimiter_points(self, delimiter_point_id_list):
    
        CanvasModel.get_instance().delete_delimiter_points(
            delimiter_point_id_list)
            
        if self._context.get_active_sample_comet_being_edited_id() is not None:    
            self._context.set_comet_being_edited_has_changed(True)
            self._context.update_save_button_sensitivity() 
    


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	EditingSelectionState                                                     #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class EditingSelectionState(ActionState):

    '''
        The EditingSelectionState class.
    '''

    ''' Initialization method. '''
    def __init__(self, context):

        # State constructor
        super().__init__(context)
        
        self.initialize()
            
    def initialize(self):
      
        CanvasModel.get_instance().set_anchored_delimiter_point(None)
        CanvasModel.get_instance().set_selection_area(None)
        CanvasModel.get_instance().set_selected_pivot_delimiter_point(None)
        CanvasModel.get_instance().set_delimiter_point_selection(
            DelimiterPointSelection())
        self._context.get_view().get_main_window().get_canvas().\
            set_build_contour_buttons_sensitivity(False)


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
# 	                      CanvasState Implementation                          #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Mouse motion behaviour. '''
    def on_mouse_motion(self, event):
        
        # Holding left mouse button
        if event.state & Gdk.EventMask.BUTTON_PRESS_MASK:

            if CanvasModel.get_instance().get_selection_area() is None:

                # Set selectedDelimiterPoints origin coordinates
                if not CanvasModel.get_instance().get_delimiter_point_selection().get_moved():

                    for (_, selected_point) in CanvasModel.get_instance().get_delimiter_point_selection().\
                                                      get_dict().items():
            
                        # Get DelimiterPoint
                        delimiter_point = get_delimiter_point(
                            selected_point.get_id())
                        # Set origin coordinates
                        selected_point.set_origin(
                            delimiter_point.get_coordinates())

                    CanvasModel.get_instance().get_delimiter_point_selection().set_moved(True)
     
                # Move selected DelimiterPoints
                self.move_selected_delimiter_points(
                    (int(event.x), int(event.y)))

            else:
                # Update the SelectionArea ending point
                CanvasModel.get_instance().get_selection_area().set_ending_point(
                    (int(event.x), int(event.y)))

    ''' Mouse clicking behaviour. '''
    def on_mouse_click(self, event):
        
        mouse_coordinates = (int(event.x), int(event.y))
        # See if the 'click' was above a DelimiterPoint
        (value, delimiter_point) = self.click_on_delimiter_point(
                                       mouse_coordinates)

        # Click was on a DelimiterPoint
        if value:

            accel_mask = Gtk.accelerator_get_default_mod_mask()
            # Ctrl + click
            if event.state & accel_mask == Gdk.ModifierType.CONTROL_MASK:
                # Toggle DelimiterPoint selection                 
                self.toggle_delimiter_point_selection(delimiter_point)

            # Ctrl is not pressed
            else:

                # Right click
                if event.button == MouseButtons.RIGHT_BUTTON:
                    self._context.get_view().get_main_window().get_canvas().pop_up_editing_selection_menu1(event)

                # If it is not already selected, it is selected as an individual 
                if (delimiter_point.get_id() not in 
                    CanvasModel.get_instance().get_delimiter_point_selection().get_dict().keys()):

                    CanvasModel.get_instance().get_delimiter_point_selection().get_dict().clear()
                    CanvasModel.get_instance().get_delimiter_point_selection().get_dict()[
                        delimiter_point.get_id()] = SelectedDelimiterPoint(
                        delimiter_point.get_id())                       

        # Click wasn't on a DelimiterPoint          
        else:

            # Right click
            if event.button == MouseButtons.RIGHT_BUTTON:
            
                candidate = self.right_click_on_edge(mouse_coordinates)
                if candidate is not None:
                
                    CanvasModel.get_instance().set_requested_delimiter_point(
                        RequestedDelimiterPoint(mouse_coordinates, candidate[0])
                    )
                    self._context.get_view().get_main_window().get_canvas().pop_up_editing_selection_menu2(event)

            # Left click
            else:
      
                CanvasModel.get_instance().get_delimiter_point_selection().get_dict().clear()
                CanvasModel.get_instance().set_selection_area(SelectionArea(mouse_coordinates))

    ''' Mouse release behaviour. '''
    def on_mouse_release(self, event):
        
        if CanvasModel.get_instance().get_selection_area() is not None:
            self.select_delimiter_points_inside_selection_area()

        if CanvasModel.get_instance().get_selected_pivot_delimiter_point() is not None:

            if CanvasModel.get_instance().get_anchored_delimiter_point() is not None:

                CanvasModel.get_instance().get_anchored_delimiter_point().set_roommate(
                    CanvasModel.get_instance().get_selected_pivot_delimiter_point())
                CanvasModel.get_instance().get_selected_pivot_delimiter_point().set_roommate(
                    CanvasModel.get_instance().get_anchored_delimiter_point())

            if CanvasModel.get_instance().get_delimiter_point_selection().get_moved():

                if self._context.get_active_sample_comet_being_edited_id() is not None:
                    
                    self._context.update_save_button_sensitivity()
                    self._context.set_comet_being_edited_has_changed(True)

                CanvasModel.get_instance().get_delimiter_point_selection().set_moved(False)

        CanvasModel.get_instance().set_anchored_delimiter_point(None)
        CanvasModel.get_instance().set_selected_pivot_delimiter_point(None)            
        CanvasModel.get_instance().set_selection_area(None)

    ''' Key press behaviour. '''
    def on_key_press_event(self, event):

        keyval = event.keyval
        keyval_name = Gdk.keyval_name(keyval)

        # Supr -> delete selected DelimiterPoints
        if keyval_name == "Delete":

            if len(CanvasModel.get_instance().get_delimiter_point_selection().get_dict()) == 0:
                return True

            self.delete_selected_delimiter_points()

    ''' Drawing behaviour. '''
    def draw(self, cairo_context):
        
        self.draw_selected_delimiter_points(cairo_context)
        self.draw_selection_area(cairo_context)


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
# 	                               Methods                                    #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #  

    def reset_parameters(self):
        self.initialize()

    def update_buttons_sensitivity(self):
        self._context.get_build_tail_contour_button().set_sensitive(
            False)
        self._context.get_build_head_contour_button().set_sensitive(
            False)          

    ''' Toggles the selection of a given DelimiterPoint. '''  
    def toggle_delimiter_point_selection(self, delimiter_point):

        if delimiter_point.get_id() not in \
                       CanvasModel.get_instance().get_delimiter_point_selection().get_dict().keys():
            CanvasModel.get_instance().get_delimiter_point_selection().get_dict()[delimiter_point.\
                get_id()] = SelectedDelimiterPoint(delimiter_point.get_id())
        else:
            del CanvasModel.get_instance().get_delimiter_point_selection().get_dict()[
                delimiter_point.get_id()]

    ''' Draws the selected DelimiterPoints. '''
    def draw_selected_delimiter_points(self, cairo_context):
    
        # These DelimiterPoints have a different color
        self._context.get_brush().set_color(
            CanvasModel.get_instance().get_delimiter_point_selection_color()
        )

        for (_, selected_point) in CanvasModel.get_instance().get_delimiter_point_selection().get_dict().items():
           
            # Draw selected DelimiterPoint
            delimiter_point = get_delimiter_point(
                selected_point.get_id())
            if delimiter_point is not None:
                self.draw_delimiter_point(cairo_context, delimiter_point)
   
    ''' Draws the selection area. '''
    def draw_selection_area(self, cairo_context):

        if CanvasModel.get_instance().get_selection_area() is not None:

            (rect_x, rect_y, width, height) = CanvasModel.get_instance().get_selection_area().get_rect()
            
            # Set Brush properties
            self._context.get_brush().set_color(
                CanvasModel.get_instance().get_selection_area_color())
            self._context.get_brush().set_width(
                CanvasModel.get_instance().get_free_selection_area_width()
            )

            # Draw selection area
            self._context.get_brush().draw_selection_area(
                cairo_context, (rect_x, rect_y, width, height))

            # Draw DelimiterPoints inside the selection area as if they were
            # selected
            for delimiter_point in self.get_all_points():

                (point_x, point_y) = delimiter_point.get_coordinates()
                if ( (point_x >= rect_x and point_x <= rect_x + width) and
                     (point_y >= rect_y and point_y <= rect_y + height) ):

                    # Draw DelimiterPoint
                    self.draw_delimiter_point(cairo_context, delimiter_point)


    ''' Selects the DelimiterPoints inside the selection area. '''
    def select_delimiter_points_inside_selection_area(self):

        (rect_x, rect_y, width, height) = CanvasModel.get_instance().get_selection_area().get_rect()
        for delimiter_point in self.get_all_points():

            (point_x, point_y) = delimiter_point.get_coordinates()
            if ( (point_x >= rect_x and point_x <= rect_x + width) and
                 (point_y >= rect_y and point_y <= rect_y + height) ):

                CanvasModel.get_instance().get_delimiter_point_selection().get_dict()[
                    delimiter_point.get_id()] = SelectedDelimiterPoint(
                                                     delimiter_point.get_id())

    ''' Moves the selected DelimiterPoints. '''
    def move_selected_delimiter_points(self, mouse_coordinates):

        roommate = CanvasModel.get_instance().get_selected_pivot_delimiter_point().get_roommate()
        if roommate is not None:

            if (roommate.get_id() not in 
                CanvasModel.get_instance().get_delimiter_point_selection().get_dict().keys()):

                roommate.set_roommate(None)
                CanvasModel.get_instance().get_selected_pivot_delimiter_point().set_roommate(None)

        dst_coordinates = self.__selection_anchoring(mouse_coordinates)
        if dst_coordinates is None:
            return

        pivot_point_coordinates = \
            CanvasModel.get_instance().get_selected_pivot_delimiter_point().get_coordinates()
        x_offset = dst_coordinates[0] - pivot_point_coordinates[0]
        y_offset = dst_coordinates[1] - pivot_point_coordinates[1]
     
        for (_, selected_point) in CanvasModel.get_instance().get_delimiter_point_selection().\
                                                    get_dict().items():

            delimiter_point = get_delimiter_point(selected_point.get_id())                    
            x = delimiter_point.get_coordinates()[0] + x_offset
            y = delimiter_point.get_coordinates()[1] + y_offset
            delimiter_point.set_coordinates((x, y))

    def __selection_anchoring(self, mouse_coordinates):

        # No anchoring if pivot point is selected with its roommate
        roommate = CanvasModel.get_instance().get_selected_pivot_delimiter_point().get_roommate() 
        if (roommate is not None and roommate.get_id() in 
            CanvasModel.get_instance().get_delimiter_point_selection().get_dict().keys()):
            return mouse_coordinates

        pivot_point_coordinates = \
                CanvasModel.get_instance().get_selected_pivot_delimiter_point().get_coordinates()

        # See if mouse pointer is close to a DelimiterPoint different of
        # selected pivot DelimiterPoint's type.
        if CanvasModel.get_instance().get_selected_pivot_delimiter_point().get_type() == \
                                                DelimiterPointType.HEAD:
            delimiter_point_list = self.get_all_tail_points()
        else:
            delimiter_point_list = self.get_all_head_points()

        # The forbidden id list
        points_with_roommate = [point.get_id() for point in delimiter_point_list if 
                                point.get_roommate() is not None]
        forbidden_id_list = union(CanvasModel.get_instance().get_delimiter_point_selection().\
                                get_dict().keys(), points_with_roommate)

        # Search for candidate
        candidate = see_anchoring_with_delimiter_point_list(
            delimiter_point_list, forbidden_id_list, mouse_coordinates)

        # We are anchoring the selected pivot DelimiterPoint and the 
        # candidate DelimiterPoint
        if candidate is not None:
            
            # If the candidate is already the anchored DelimiterPoint
            if (CanvasModel.get_instance().get_anchored_delimiter_point() is not None and
                CanvasModel.get_instance().get_anchored_delimiter_point().get_id() ==
                candidate[0].get_id()):
                return None

            # The pivot DelimiterPoint isn't anchored and is close to a
            # DelimiterPoint of different type
            else:
                CanvasModel.get_instance().set_anchored_delimiter_point(candidate[0])
                return candidate[0].get_coordinates()

        else:
            CanvasModel.get_instance().set_anchored_delimiter_point(None)
            return mouse_coordinates

    ''' Sees if given coordinates belong to a DelimiterPoint. '''
    def click_on_delimiter_point(self, mouse_coordinates):

        # See if the click is above a DelimiterPoint
        for delimiter_point in self.get_all_points():

            euclidean_distance = utils.euclidean_distance(
                                    delimiter_point.get_coordinates(),
                                    mouse_coordinates)

            # The click is above a DelimiterPoint
            if euclidean_distance <= CanvasModel.get_instance().get_selection_distance():
                CanvasModel.get_instance().set_selected_pivot_delimiter_point(delimiter_point)
                return (True, delimiter_point)

        return (False, None)

    ''' Returns the existing edges, defined by two DelimiterPoints. '''
    def get_edges(self):

        edges = []
        aux_dic = {}

        for delimiter_point in self.get_all_points():

            if delimiter_point.get_id() not in aux_dic:
                aux_dic[delimiter_point.get_id()] = []

            for neighbor in delimiter_point.get_neighbors():

                if neighbor.get_id() not in aux_dic:
                    aux_dic[neighbor.get_id()] = []

                if neighbor.get_id() not in aux_dic[delimiter_point.get_id()]:

                    # Append points to edges
                    edges.append((delimiter_point, neighbor))

                    aux_dic[delimiter_point.get_id()].append(neighbor.get_id())
                    aux_dic[neighbor.get_id()].append(delimiter_point.get_id())

        return edges            

    ''' 
        Sees if given right click coordinates belong to a edge between
        two DelimiterPoints.
    '''
    def right_click_on_edge(self, mouse_coordinates):

        candidate = None

        for edge in self.get_edges():

            # Calculate distance
            distance = self.get_distance_point_to_segment(
                           mouse_coordinates, edge)           

            if distance <= CanvasModel.get_instance().get_edge_selection_distance():
            
                if candidate is None:
                    candidate = (edge, distance)

                elif distance < candidate[1]:
                    candidate = (edge, distance)
                    
        return candidate 

    ''' Returns the distance from point 'point' to line 'line'. '''
    def get_distance_point_to_segment(self, point0, line):   

        point1 = line[0].get_coordinates()
        point2 = line[1].get_coordinates() 

        x0, y0 = float(point0[0]), float(point0[1])
        x1, y1, x2, y2 = (float(point1[0]), float(point1[1]), 
                          float(point2[0]), float(point2[1]))

        A = x0 - x1
        B = y0 - y1
        C = x2 - x1
        D = y2 - y1

        dot = A * C + B * D
        len_sq = C * C + D * D
        param = -1

        if len_sq != 0:
            param = dot / len_sq

        if param < 0:
            xx = x1
            yy = y1

        elif param > 1:
            xx = x2
            yy = y2
 
        else:
            xx = x1 + param * C
            yy = y1 + param * D

        dx = x0 - xx
        dy = y0 - yy
        return math.sqrt(dx * dx + dy * dy)

    ''' Deletes the selected DelimiterPoints. '''
    def delete_selected_delimiter_points(self):

        # Selected points IDs
        selected_points_id_list = CanvasModel.get_instance().get_delimiter_point_selection().\
                                      get_dict().keys() 

        # Deletes the selected DelimiterPoints
        CanvasEditingState.get_instance().delete_delimiter_points(
            selected_points_id_list)

        # No selected points
        CanvasModel.get_instance().get_delimiter_point_selection().get_dict().clear()



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	EditingBuildingState                                                      #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class EditingBuildingState(ActionState):

    '''
        The EditingBuildingState class.
    '''

    ''' Initialization method. '''
    def __init__(self, context):

        # State constructor
        super().__init__(context)
        
        self.__initialize()

    ''' Initialization behaviour. '''
    def __initialize(self):

        # EditingBuildingState state
        if self._context.get_build_tail_contour_button().get_active():
            self.__state = BuildingTailContourState(self._context)
        elif self._context.get_build_head_contour_button().get_active():
            self.__state = BuildingHeadContourState(self._context)
    
        # Update buttons sensitivity
        self.update_buttons_sensitivity()
        
    ''' Restart behaviour. '''    
    def restart(self):
        self.__initialize()
        self.__state.restart()
        

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
# 	                      CanvasState Implementation                          #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Mouse motion behaviour. '''
    def on_mouse_motion(self, event):
        self.__state.on_mouse_motion(event)

    ''' Mouse clicking behaviour. '''
    def on_mouse_click(self, event):

        # Left click
        if event.button == MouseButtons.LEFT_BUTTON:
            self.__state.left_mouse_button_click(event)

        # Right click
        elif event.button == MouseButtons.RIGHT_BUTTON:
            self.__state.right_mouse_button_click(event)

    ''' Mouse release behaviour. '''
    def on_mouse_release(self, event):
        pass

    ''' Key press behaviour. '''
    def on_key_press_event(self, event):
        pass

    ''' Drawing behaviour. '''
    def draw(self, cairo_context):
    
        self.__draw_building_trail_line(cairo_context)
        self.__draw_mouse_pointer_delimiter_point(cairo_context)
            
    ''' 
        Draws the trail between the root and mouse pointer 
        DelimiterPoints.
    '''
    def __draw_building_trail_line(self, cairo_context):
            
        if CanvasModel.get_instance().get_root_delimiter_point() is not None:

            mouse_coordinates = self._context.get_view().get_main_window().get_canvas().get_mouse_coordinates()
            if mouse_coordinates is not None:
    
                # Set building trail line color
                self._context.get_brush().set_color(
                    self.__state.get_color())
  
                # Draw trail line
                self._context.get_brush().draw_line(
                    cairo_context, self.__get_trail_line())

                # Draw root DelimiterPoint
                self.draw_delimiter_point(
                    cairo_context, CanvasModel.get_instance().get_root_delimiter_point())

    ''' Builds and returns the trail line to be drawn. '''
    def __get_trail_line(self):

        line = []
        # First point is root DelimiterPoint coordinates 
        line.append(CanvasModel.get_instance().get_root_delimiter_point().get_coordinates())

        if CanvasModel.get_instance().get_anchored_delimiter_point() is not None:               
            line.append(
                CanvasModel.get_instance().get_anchored_delimiter_point().get_coordinates())
        else:  
            line.append(self._context.get_view().get_main_window().get_canvas().get_mouse_coordinates())

        return line
        
    ''' Draws the DelimiterPoint at mouse location. '''
    def __draw_mouse_pointer_delimiter_point(self, cairo_context):

        # Mouse is inside the DrawingArea
        if self._context.get_view().get_main_window().get_canvas().get_mouse_coordinates() is not None:

            # No anchored DelimiterPoint
            if CanvasModel.get_instance().get_anchored_delimiter_point() is None:
                    
                coordinates = self._context.get_view().get_main_window().get_canvas().get_mouse_coordinates()
                self._context.get_brush().set_color(
                    self.__state.get_color())

            # A DelimiterPoint is anchored
            else:

                coordinates = self.get_anchored_delimiter_point().\
                                  get_coordinates()
                self._context.get_brush().set_color(
                    CanvasModel.get_instance().get_anchored_delimiter_point_color())

            # Draw mouse pointer DelimiterPoint
            self._context.get_brush().draw_delimiter_point(
                cairo_context, coordinates,
                CanvasModel.DELIMITER_POINT_SIZE)

 
        
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
# 	                                Methods                                   #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' State transition to BuildingTailContourState. '''
    def transition_to_building_tail_contour_state(self, context):
        self.__state = BuildingTailContourState(context)

    ''' State transition to BuildingHeadContourState. '''
    def transition_to_building_head_contour_state(self, context):
        self.__state = BuildingHeadContourState(context)

    ''' Makes the Building buttons sensitive. '''
    def update_buttons_sensitivity(self):
        self._context.get_build_tail_contour_button().set_sensitive(True)
        self._context.get_build_head_contour_button().set_sensitive(True)   
        
        

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	BuildingContourState                                                      #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class BuildingContourState(ActionState):

    '''
        The BuildingContourState class.
    '''

    ''' Initialization method. '''
    def __init__(self, context):

        # Parent constructor
        super().__init__(context)
        
        self.__initialize()

    ''' Initialization behaviour. '''
    def __initialize(self):
        
        CanvasModel.get_instance().set_root_delimiter_point(None)
        CanvasModel.get_instance().set_anchored_delimiter_point(None)
      
    ''' Restart behaviour. '''
    def restart(self):
        self.__initialize()
        
    ''' Returns the color for drawing. '''    
    def get_color(self):
        return self.BUILDER.get_color()
 

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
# 	                          ActionState Methods                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' On mouse motion behaviour. '''
    def on_mouse_motion(self, event):

        # See if a DelimiterPoint should be anchored
        self.BUILDER.set_anchored_delimiter_point_method(event)
        
    ''' Left mouse button click behaviour. '''
    def left_mouse_button_click(self, event):

        mouse_coordinates = (int(event.x), int(event.y))

        # A DelimiterPoint is root
        if CanvasModel.get_instance().get_root_delimiter_point() is not None:

            # Mouse is anchored to a DelimiterPoint
            if CanvasModel.get_instance().get_anchored_delimiter_point() is not None:  
          
                self.click_on_anchored_point_with_root()

            # Mouse pointer is free 
            else:
                self.free_click_with_root(mouse_coordinates)

        # No root DelimiterPoint
        else:

            # Mouse is anchored to a DelimiterPoint
            if CanvasModel.get_instance().get_anchored_delimiter_point() is not None:

                self.click_on_anchored_point_with_no_root() 
         
            # Mouse pointer is free 
            else:
                self.free_click_with_no_root(mouse_coordinates)

        if self._context.get_active_sample_comet_being_edited_id() is not None:
            
            self._context.update_save_button_sensitivity()
            self._context.set_comet_being_edited_has_changed(True)

    ''' Right mouse button click behaviour. '''
    def right_mouse_button_click(self, event):
        self.__initialize()

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
# 	                                Methods                                   #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #     
        
    ''' 
        Left mouse button click behaviour when a DelimiterPoint is root and a
        DelimiterPoint is anchored.
    '''
    def click_on_anchored_point_with_root(self):

        # Anchored DelimiterPoint is of same type
        if CanvasModel.get_instance().get_anchored_delimiter_point().get_type() == \
                                                              self.BUILDER.POINT_TYPE:

            self.anchored_point_with_root_is_same_type()
              
        # Anchored DelimiterPoint is of different type
        else:
                
            self.anchored_point_with_root_is_different_type()    
        
    ''' 
        Behaviour when root and anchored points are from the same type.
    '''
    def anchored_point_with_root_is_same_type(self):

        # Connect points
        self.BUILDER.connect_points(
           CanvasModel.get_instance().get_root_delimiter_point(), 
            CanvasModel.get_instance().get_anchored_delimiter_point()
        )

        # See if the contour is closed
        contour = self.BUILDER.get_contour_dict()[
            CanvasModel.get_instance().get_root_delimiter_point().get_contour_id()]
        delimiter_point_id_list = check_contour_is_closed(contour,
                                      CanvasModel.get_instance().get_root_delimiter_point())

        if contour.get_closed():     
            self.on_closed_contour_created(contour, delimiter_point_id_list)

    ''' 
        Behaviour when root and anchored points are from a different type.
    '''
    def anchored_point_with_root_is_different_type(self):

        # Create a new DelimiterPoint on anchored DelimiterPoint
        # coordinates and connect with the root
        delimiter_point = self.BUILDER.create_and_connect_points(
            CanvasModel.get_instance().get_anchored_delimiter_point().get_coordinates(),
            CanvasModel.get_instance().get_root_delimiter_point()
        )

        # Make roommates
        make_roommates(CanvasModel.get_instance().get_anchored_delimiter_point(),
            delimiter_point)
            
    '''
        Left mouse button click behaviour when there isn't a root
        DelimiterPoint and a DelimiterPoint is anchored.
    '''       
    def click_on_anchored_point_with_no_root(self):
          
        # The DelimiterPoint is of same type
        if CanvasModel.get_instance().get_anchored_delimiter_point().get_type() == \
                                                      self.BUILDER.POINT_TYPE:    
                  
            self.anchored_point_with_no_root_is_same_type()
                        
        # The DelimiterPoint is of different type
        else:

            self.anchored_point_with_no_root_is_different_type()

    ''' 
        Behaviour when the anchored point is from the same type.
    '''
    def anchored_point_with_no_root_is_same_type(self):
        # Select anchored DelimiterPoint        
        self.BUILDER.select_anchored_delimiter_point()

    ''' 
        Behaviour when the anchored point is from a different type.
    '''
    def anchored_point_with_no_root_is_different_type(self):

        # Create a new DelimiterPoint on anchored DelimiterPoint coordinates
        delimiter_point = self.BUILDER.create_delimiter_point(
            CanvasModel.get_instance().get_anchored_delimiter_point().get_coordinates()
        )

        # Make roommates
        make_roommates(CanvasModel.get_instance().get_anchored_delimiter_point(),
            delimiter_point)

        # New DelimiterPoint is root           
        CanvasModel.get_instance().set_root_delimiter_point(delimiter_point)
        # No anchored delimiter point anymore
        CanvasModel.get_instance().set_anchored_delimiter_point(None)

    ''' Behaviour when a point is root and there is no anchored points. '''
    def free_click_with_root(self, mouse_coordinates):

        # Create a new DelimiterPoint on mouse location and connect 
        # with the root
        delimiter_point = self.BUILDER.create_and_connect_points(
            mouse_coordinates,
            CanvasModel.get_instance().get_root_delimiter_point()
        )

    ''' Behaviour when there is neither root point nor anchored point. '''
    def free_click_with_no_root(self, mouse_coordinates):

        # Create a new DelimiterPoint
        delimiter_point = self.BUILDER.create_delimiter_point(mouse_coordinates)            
        # New delimiter point is now the root
        CanvasModel.get_instance().set_root_delimiter_point(delimiter_point)
        
        
    ''' Behaviour when a comet has been successfully built. '''
    def on_comet_built(self, head_contour, tail_contour=None):

        # Send signal to upper context
        self._context.on_add_comet(tail_contour, head_contour)
        # Clear the Comet points that belong to the comet contour
        if tail_contour is not None:
            del CanvasModel.get_instance().get_tail_contour_dict()\
                [tail_contour.get_id()]
        # Clear all Head contour points
        del CanvasModel.get_instance().get_head_contour_dict()\
                [head_contour.get_id()]

        CanvasModel.get_instance().set_root_delimiter_point(None)

    ''' Behaviour by default when a contour is closed. '''
    def on_closed_contour_created(self, contour, valid_points_id_list):
                
        valid_points = [point for point in contour.get_delimiter_point_list()
                        if point.get_id() in valid_points_id_list]

        # Contour has now only the DelimiterPoints that close the contour
        contour.set_delimiter_point_list(valid_points)

        # The rest of points are removed from the neighbors pointers
        for delimiter_point in valid_points:
            for neighbor in delimiter_point.get_neighbors():
                if neighbor.get_id() not in valid_points_id_list:
                    delimiter_point.get_neighbors().remove(neighbor)

        CanvasModel.get_instance().set_root_delimiter_point(None)
        CanvasModel.get_instance().set_anchored_delimiter_point(None)

        return valid_points


        
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	BuildingTailContourState                                                  #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class BuildingTailContourState(BuildingContourState):

    '''
        The BuildingTailContourState class.
    '''

    ''' Initialization method. '''
    def __init__(self, context):

        # State constructor
        super().__init__(context)
        
        # Constants
        self.BUILDER = TailContourBuilder.get_instance()
       
       

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	BuildingHeadContourState                                                  #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class BuildingHeadContourState(BuildingContourState):

    '''
        The BuildingHeadContourState class.
    '''

    ''' Initialization method. '''
    def __init__(self, context):

        # State constructor
        super().__init__(context)
        
        # Constants
        self.BUILDER = HeadContourBuilder.get_instance()


    ''' Behaviour when a Head Contour is closed. '''
    def on_closed_contour_created(self, head_contour, valid_points_id_list):
        
        if self._context.get_sample_comet_being_edited_id(
            self._context.get_active_sample_id()) is not None:
            return

        valid_points = super().on_closed_contour_created(
                           head_contour, valid_points_id_list)

        closed_tail_contour_list = [contour for (_, contour) in CanvasModel.\
                                     get_instance().get_tail_contour_dict().items()
                                     if contour.get_closed()]

        # If the Head contour is nested to a closed Comet contour, both are
        # used to build the comet.
        for tail_contour in closed_tail_contour_list:

            comet_coordinates_list = [point.get_coordinates() for point in
                                      tail_contour.get_delimiter_point_list()]
            cv2_tail_contour = utils.list_to_contour(comet_coordinates_list)
                    
            is_inside = False
            index = 0
            while (index < len(valid_points) and not is_inside):
 
                is_inside = utils.is_point_inside_contour(
                    cv2_tail_contour, valid_points[index].get_coordinates())
                
                if is_inside:
                    self.on_comet_built(head_contour, tail_contour)
                    return

                index += 1

        # Otherwise, the comet is built just with the Head contour
        self.on_comet_built(head_contour)



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                            Auxiliary Methods                                #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

''' Returns the DelimiterPoint identifier. '''
def get_delimiter_point(delimiter_point_id):

    tail_contour_dict = CanvasModel.get_instance().get_tail_contour_dict()
    head_contour_dict = CanvasModel.get_instance().get_head_contour_dict()

    for (_, contour) in tail_contour_dict.items():
        for delimiter_point in contour.get_delimiter_point_list():
            if delimiter_point.get_id() == delimiter_point_id:
                return delimiter_point

    for (_, contour) in head_contour_dict.items():
        for delimiter_point in contour.get_delimiter_point_list():
            if delimiter_point.get_id() == delimiter_point_id:
                return delimiter_point

''' Makes two DelimiterPoints 'roommates'. '''
def make_roommates(delimiter_point1, delimiter_point2):

    delimiter_point1.set_roommate(delimiter_point2)
    delimiter_point2.set_roommate(delimiter_point1)

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

















     
