# -*- encoding: utf-8 -*-

'''
    The canvas module.
'''

# Generic imports
import math

# PyGObject imports
import gi
import cairo
gi.require_version('Gtk', '3.0')
gi.require_foreign("cairo")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

# Custom imports
import sample.model.utils as utils
from sample.view.color_tool import ColorTool



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	Canvas                                                                    #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class Canvas(object):

    '''
        the Canvas class.
    '''

    DEFAULT_SCROLLBAR_X_POSITION = 0
    DEFAULT_SCROLLBAR_Y_POSITION = 0

    ''' Initialization method. '''
    def __init__(self, view, gtk_builder):

        # The View
        self.__view = view

        # Initialize
        self.__initialize()

        # Gtk Components
        self.__scrolledwindow = gtk_builder.get_object("drawing-area-scrolledwindow") 
        self.__viewport = gtk_builder.get_object("drawing-area-viewport")
        self.__drawing_area = gtk_builder.get_object("drawing-area")
        self.__drawing_area.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
        self.__label = gtk_builder.get_object("drawing-area-label")

        self.__analyze_button = gtk_builder.get_object(
            "drawing-area-toolbar-analyze")
        self.__analyze_all_button = gtk_builder.get_object(
            "drawing-area-toolbar-analyze-all")
        self.__settings_button = gtk_builder.get_object(
            "drawing-area-toolbar-settings")
        self.__generate_output_file_button = gtk_builder.get_object(
            "drawing-area-toolbar-generate-output-file") 
        self.__selection_button = gtk_builder.get_object(
            "drawing-area-toolbar-selection")
        self.__editing_button = gtk_builder.get_object(
            "drawing-area-toolbar-editing")
        self.__editing_selection_button = gtk_builder.get_object(
            "drawing-area-toolbar-editing-selection")
        self.__building_button = gtk_builder.get_object(
            "drawing-area-toolbar-building")
        self.__build_tail_contour_button = gtk_builder.get_object(
            "drawing-area-toolbar-build-comet-contour-button")
        self.__build_head_contour_button = gtk_builder.get_object(
            "drawing-area-toolbar-build-head-contour-button")

        self.__color_tool = ColorTool(gtk_builder, view)

        # Context menus
        self.__selection_context_menu = gtk_builder.get_object(
            "canvas-selection-state-context-menu")
        self.__selection_context_menu_flip_button = gtk_builder.\
            get_object("canvas-selection-state-context-menu-flip")
        self.__selection_context_menu_invert_button = gtk_builder.\
            get_object("canvas-selection-state-context-menu-invert")
        self.__editing_selection_context_menu1 = gtk_builder.get_object(
            "canvas-editing-selection-state-context-menu1")
        self.__delete_delimiter_point_button = gtk_builder.\
            get_object("canvas-editing-selection-state-context-menu1-delete")
        self.__editing_selection_context_menu2 = gtk_builder.get_object(
            "canvas-editing-selection-state-context-menu2")
        self.__add_delimiter_point_button = gtk_builder.\
            get_object("canvas-editing-selection-state-context-menu2-add")

    
    ''' Attributes initialization. '''
    def __initialize(self):

        self.__scroll_speed = 5.       
        self.__mouse_coordinates = None
        self.__move_reference_point = None

        self.__brush = Brush()
        self.__contours_width = 1
        self.__contours_line_type = cairo.LINE_CAP_ROUND     

    ''' Restart. '''
    def restart(self):

        self.__initialize()
        self.__build_tail_contour_button.set_active(True)
        self.__editing_selection_button.set_active(True)
        self.__selection_button.set_active(True)
        self.switch_off()
        
        
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              Context menus                                  #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Pops up the CanvasSelectionState menu. '''
    def pop_up_canvas_selection_state_menu(self, event):
        self.__selection_context_menu.popup(
            None, None, None, None, event.button, event.time)

    ''' Pops up the CanvasEditingSelectionState menu1. '''
    def pop_up_editing_selection_menu1(self, event):
        self.__editing_selection_context_menu1.popup(
            None, None, None, None, event.button, event.time)

    ''' Pops up the CanvasEditingSelectionState menu2. '''
    def pop_up_editing_selection_menu2(self, event):
        self.__editing_selection_context_menu2.popup(
            None, None, None, None, event.button, event.time)


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              State Methods                                  #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' On key press event method. '''
    def on_key_press_event(self, event):
        self.__view.get_controller().on_canvas_key_press_event(event)
        self.update()

    ''' On mouse enter callback method. '''
    def on_mouse_enter(self):
        self.__view.get_controller().on_canvas_mouse_enter()
        self.update()

    ''' On mouse leave callback method. '''
    def on_mouse_leave(self):
        self.__view.get_controller().on_canvas_mouse_leave()
        self.update()

    ''' On mouse release callback method. '''
    def on_mouse_release(self, event):
        self.__view.get_controller().on_canvas_mouse_release(event)      
        self.update()

    ''' On mouse click callback method. '''
    def on_mouse_click(self, event):
        self.__drawing_area.grab_focus()        
        self.__view.get_controller().on_canvas_mouse_click(event)
        self.update()

    ''' On mouse motion callback method. '''
    def on_mouse_motion(self, event, pixbuf):

        self.__mouse_coordinates = int(event.x), int(event.y)
        if not self.__is_mouse_pointer_inside_visible_area():
            return True

        self.__view.get_controller().on_canvas_mouse_motion(event)
        self.update()

    ''' Returns whether the mouse pointer is inside the DrawingArea's visible area or not. '''
    def __is_mouse_pointer_inside_visible_area(self):

        mouse_x = self.__mouse_coordinates[0]
        mouse_y = self.__mouse_coordinates[1]

        x_offset = self.__viewport.get_hadjustment().get_value()
        y_offset = self.__viewport.get_vadjustment().get_value()
        x_margin = ( self.__viewport.get_margin_left() +
                     self.__viewport.get_margin_right() ) 
        y_margin = ( self.__viewport.get_margin_top() +
                     self.__viewport.get_margin_bottom() ) 

        visible_area_width = self.__viewport.get_allocated_size()[0].width - x_margin
        visible_area_height = self.__viewport.get_allocated_size()[0].height - y_margin

        return ( (mouse_x >= x_offset and mouse_x < x_offset + visible_area_width) and
                 (mouse_y >= y_offset and mouse_y < y_offset + visible_area_height) )

    ''' Draw method. '''
    def draw(self, cairo_context, pixbuf, comet_view_list):

        # Set drawing area size
        self.__drawing_area.get_window().resize(pixbuf.get_width(), pixbuf.get_height())
        self.__drawing_area.set_size_request(pixbuf.get_width(), pixbuf.get_height())

        # (x, y) offsets
        pixbuf_x = int(self.__viewport.get_hadjustment().get_value())
        pixbuf_y = int(self.__viewport.get_vadjustment().get_value())

        # Width and height of the image's clip
        width = self.__viewport.get_allocation().width
        height = self.__viewport.get_allocation().height
        if pixbuf_x + width > pixbuf.get_width():                            
            width = pixbuf.get_width() - pixbuf_x
        if pixbuf_y + height > pixbuf.get_height():
            height = pixbuf.get_height() - pixbuf_y

        if width > 0 and height > 0: 

            # Create the area of the image that will be displayed in the
            # specific position
            image = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB,
                        pixbuf.get_has_alpha(), 8, width, height)
            pixbuf.copy_area(pixbuf_x, pixbuf_y, width, height, image, 0, 0)

            # Draw created area of Sample's Pixbuf
            Gdk.cairo_set_source_pixbuf(
                cairo_context, image, pixbuf_x, pixbuf_y)
            cairo_context.paint()

            # Draw samples comets   
            self.__draw_sample_comets(cairo_context, comet_view_list)

            # Canvas state specific drawing
            self.__view.get_controller().draw(cairo_context)
            
    ''' Draws the contours of the Sample's comets. '''
    def __draw_sample_comets(self, cairo_context, comet_view_list):

        if comet_view_list is not None and len(comet_view_list) > 0:  

            # Set few Brush properties
            self.__brush.set_width(self.__contours_width)
            self.__brush.set_line_type(self.__contours_line_type)

            # Initialize path
            cairo_context.new_path()

            for comet_view in comet_view_list:
            
                # Do not draw comet if it's currently being edited
                if (self.__view.get_controller().get_active_sample_comet_being_edited_id() is not None and
                        self.__view.get_controller().get_active_sample_comet_being_edited_id() == comet_view.get_id() and
                        self.__view.get_controller().get_editing()):
                    continue

                self.__draw_comet(cairo_context, comet_view)

    ''' Draws the contours of a comet. '''
    def __draw_comet(self, cairo_context, comet_view):

        # Set Brush color to Tail Color
        self.__brush.set_color(self.__view.get_controller().get_tail_color())

        # Draw comet tail contour
        if comet_view.get_scaled_tail_contour() is not None:
            tail_contour = utils.contour_to_list(
                comet_view.get_scaled_tail_contour())
            self.__brush.draw_line(
                cairo_context, tail_contour, close=True)

        cairo_context.new_sub_path()

        # Set Brush color to Head color
        self.__brush.set_color(self.__view.get_controller().get_head_color())            

        # Draw comet head contour
        head_contour = utils.contour_to_list(
                           comet_view.get_scaled_head_contour())
        self.__brush.draw_line(
            cairo_context, head_contour, close=True)


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                 Methods                                     #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Redraw Canvas. '''
    def update(self, rect=None):

        # Draw
        if rect is None:
            self.__drawing_area.queue_draw()
        else:
            self.__drawing_area.queue_draw_area(*rect)

    ''' Sets the Building buttons sensitivity. '''
    def set_build_contour_buttons_sensitivity(self, sensitivity):
        self.__build_tail_contour_button.set_sensitive(sensitivity)
        self.__build_head_contour_button.set_sensitive(sensitivity)

    ''' Sets cursor. '''
    def set_cursor(self, cursor_name):
        self.__drawing_area.get_window().set_cursor(
            Gdk.Cursor.new_from_name(Gdk.Display.get_default(), cursor_name))

    ''' Move scrollbars. '''
    def move_scrollbars(self, axis):

        x_pos = int(self.__scrolledwindow.get_hadjustment().get_value())
        y_pos = int(self.__scrolledwindow.get_vadjustment().get_value())
        x_value = axis[0] * self.__scroll_speed
        y_value = axis[1] * self.__scroll_speed
        self.__scrolledwindow.get_hadjustment().set_value(x_pos + x_value)
        self.__scrolledwindow.get_vadjustment().set_value(y_pos + y_value)

    ''' Switch Canvas On. '''
    def switch_on(self):

        self.__update_buttons_sensitivity(True)
        self.__view.get_controller().get_canvas_state().update_buttons_sensitivity()
        self.__label.show_all()
        self.__drawing_area.show_all()      

    ''' Switch Canvas Off. '''
    def switch_off(self):

        self.__update_buttons_sensitivity(False)
        self.__drawing_area.hide()       
        self.__label.set_label("")
        
    ''' Sets the scrolledwindow scroll position. '''
    def set_scroll_position(self, x, y):
    
        self.__scrolledwindow.get_hadjustment().set_value(x)
        self.__scrolledwindow.get_vadjustment().set_value(y)

    ''' Gets the scrolledwindow scroll position. '''
    def get_scroll_position(self):
    
        x = self.__scrolledwindow.get_hadjustment().get_value()
        y = self.__scrolledwindow.get_vadjustment().get_value()
        return (x, y)

    ''' Update buttons sensitivity. '''
    def __update_buttons_sensitivity(self, value):
    
        self.__analyze_button.set_sensitive(value)
        self.__analyze_all_button.set_sensitive(value)
        self.__generate_output_file_button.set_sensitive(value)
        self.__selection_button.set_sensitive(value)
        self.__editing_button.set_sensitive(value)
        self.__editing_selection_button.set_sensitive(value)
        self.__building_button.set_sensitive(value)
        self.__build_tail_contour_button.set_sensitive(value)
        self.__build_head_contour_button.set_sensitive(value)

    ''' Hides editing state buttons. '''
    def hide_editing_buttons(self):
    
        self.__editing_selection_button.hide()
        self.__building_button.hide()
        self.__build_tail_contour_button.hide()
        self.__build_head_contour_button.hide()

    ''' Shows editing state buttons. '''
    def show_editing_buttons(self):
    
        self.__editing_selection_button.show_all()
        self.__building_button.show_all()
        self.__build_tail_contour_button.show_all()
        self.__build_head_contour_button.show_all()
        

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              Getters & Setters                              #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

    def get_scroll_speed(self):
        return self.__scroll_speed

    def set_scroll_speed(self, scroll_speed):
        self.__scroll_speed = scroll_speed

    def get_mouse_coordinates(self):
        return self.__mouse_coordinates

    def set_mouse_coordinates(self, location):
        self.__mouse_coordinates = location

    def set_move_reference_point(self, move_reference_point):
        self.__move_reference_point = move_reference_point

    def get_move_reference_point(self):
        return self.__move_reference_point

    def get_scrolledwindow(self):
        return self.__scrolledwindow

    def set_scrolledwindow(self, scrolledwindow):
        self.__scrolledwindow = scrolledwindow

    def get_drawing_area(self):
        return self.__drawing_area

    def set_drawing_area(self, drawing_area):
        self.__drawing_area = drawing_area

    def get_viewport(self):
        return self.__viewport

    def set_viewport(self, viewport):
        self.__viewport = viewport

    def get_brush(self):
        return self.__brush

    def set_brush(self, brush):
        self.__brush = brush

    def get_analyze_button(self):
        return self.__analyze_button

    def set_analyze_button(self, analyze_button):
        self.__analyze_button = analyze_button

    def get_analyze_all_button(self):
        return self.__analyze_all_button

    def set_analyze_all_button(self, analyze_all_button):
        self.__analyze_all_button = analyze_all_button

    def get_settings_button(self):
        return self.__settings_button

    def set_settings_button(self, settings_button):
        self.__settings_button = settings_button

    def get_generate_output_file_button(self):
        return self.__generate_output_file_button

    def set_generate_output_file_button(self, generate_output_file_button):
        self.__generate_output_file_button = generate_output_file_button
    
    def get_selection_button(self):
        return self.__selection_button

    def set_selection_button(self, selection_button):
        self.__tolbar_selection_button = selection_button

    def get_editing_button(self):
        return self.__editing_button

    def set_editing_button(self, editing_button):
        self.__editing_button = editing_button

    def get_editing_selection_button(self):
        return self.__editing_selection_button

    def set_editing_selection_button(self, editing_selection_button):
        self.__editing_selection_button = editing_selection_button

    def get_building_button(self):
        return self.__building_button

    def set_building_button(self, building_button):
        self.__building_button = building_button

    def get_build_tail_contour_button(self):
        return self.__build_tail_contour_button

    def set_build_tail_contour_button(self, build_tail_contour_button):
        self.__build_tail_contour_button = build_tail_contour_button

    def get_build_head_contour_button(self):
        return self.__build_head_contour_button

    def set_build_head_contour_button(self, build_head_contour_button):
        self.__build_head_contour_button = build_head_contour_button

    def get_color_tool(self):
        return self.__color_tool

    def set_color_tool(self, color_tool):
        self.__color_tool = color_tool

    def get_selection_context_menu_flip_button(self):
        return self.__selection_context_menu_flip_button

    def set_selection_context_menu_flip_button(self, flip_button):
        self.__selection_context_menu_flip_button = flip_button

    def get_selection_context_menu_invert_button(self):
        return self.__selection_context_menu_invert_button

    def set_selection_context_menu_invert_button(self, invert_button):
        self.__selection_context_menu_invert_button = invert_button

    def get_delete_delimiter_point_button(self):
        return self.__delete_delimiter_point_button

    def set_delete_delimiter_point_button(self, delete_button):
        self.__delete_delimiter_point_button = delete_button

    def get_add_delimiter_point_button(self):
        return self.__add_delimiter_point_button

    def set_add_delimiter_point_button(self, add_delimiter_point_button):
        self.__add_delimiter_point_button = add_delimiter_point_button

    def get_label(self):
        return self.__label

    def set_label(self, label):
        self.__label = label



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	Brush                                                                     #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class Brush(object):

    '''
        The Brush class.
    '''

    ''' Initialization method. '''
    def __init__(self):

        self.__width = 1
        self.__color = (0, 0, 0, 1)
        self.__line_type = None


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                 Methods                                     #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Draws a line. '''
    def draw_line(self, cairo_context, line, close=False):
      
        self.set_properties(cairo_context)

        # Move to first point
        cairo_context.move_to(line[0][0], line[0][1])
        # Make line to next coordinate. Repeat until no more points.
        for point in line:        
            cairo_context.line_to(point[0], point[1])

        # Close line connecting last and first points
        if close:       
            cairo_context.line_to(line[0][0], line[0][1])
        
        # Stroke
        cairo_context.stroke()

    ''' Draws a DelimiterPoint. '''
    def draw_delimiter_point(self, cairo_context, point, size):

        self.set_properties(cairo_context)
            
        # Draw rectangle
        cairo_context.rectangle(
            point[0]-(size // 2), point[1]-(size // 2), size, size)
        # Fill rectangle
        cairo_context.fill()
        cairo_context.stroke()

    ''' Draws a round DelimiterPoint. '''
    def draw_round_delimiter_point(self, cairo_context, point, size):

        self.set_properties(cairo_context)
            
        # Draw circle
        cairo_context.arc(
            point[0], point[1], size/2, 0., 2. * math.pi)
        # Fill circle
        cairo_context.fill()
        cairo_context.stroke()

    ''' Draws a non filled rectangle. '''
    def draw_selection_area(self, cairo_context, rect):

        self.set_properties(cairo_context)

        # Draw selection area
        cairo_context.rectangle(rect[0], rect[1], rect[2], rect[3])
        cairo_context.stroke()

    ''' Sets the Cairo.context properties. '''
    def set_properties(self, cairo_context):

        cairo_context.set_line_width(self.__width)          
        cairo_context.set_source_rgba(*self.__color)
        cairo_context.set_line_cap(self.__line_type)


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

    def get_width(self):
        return self.__width

    def set_width(self, width):
        self.__width = width

    def get_color(self):
        return self.__color

    def set_color(self, color):
        self.__color = color

    def get_line_type(self):
        return self.__line_type

    def set_line_type(self, line_type):
        self.__line_type = line_type




