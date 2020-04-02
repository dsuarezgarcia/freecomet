# -*- encoding: utf-8 -*-

'''
    The windows module.
'''


# Custom imports
from view.menubar import MenuBar
from view.toolbar import ToolBar
from view.listview import SamplesView, AnalyzeSamplesView
from view.canvas import Canvas
from view.zoom_tool import ZoomTool
from controller.algorithm_settings_dto import AlgorithmSettingsDto


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	MyWindow                                                                  #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class MyWindow(object):

    '''
        The MyWindow class. The class that windows inherit from.
    '''

    ''' Initialization method. '''
    def __init__(self, window):
        self.__window = window


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                  Methods                                    #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Shows the window. '''
    def show(self):
        self.__window.show_all()

    ''' Hides the window. '''
    def hide(self):
        self.__window.hide()

    ''' Sets the window title. '''
    def set_title(self, title):
        self.__window.set_title(title)


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #   

    def get_window(self):
        return self.__window

    def set_window(self, window):
        self.__window = window



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	MainWindow                                                                #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class MainWindow(MyWindow):

    '''
        The MainWindow class. The application's main window.
    '''

    ''' Initialization method. '''
    def __init__(self, view, gtk_builder):

        # The window
        super().__init__(gtk_builder.get_object("main-window"))
        self.get_window().set_default_size(850, 600)

        # The components
        self.__menubar = MenuBar(gtk_builder)      
        self.__toolbar = ToolBar(gtk_builder)
        self.__samples_view = SamplesView(gtk_builder)
        self.__canvas = Canvas(view, gtk_builder)
        self.__zoom_tool = ZoomTool(view, gtk_builder)
        self.__color_tool = self.__canvas.get_color_tool()
        self.__selection_window = SelectionWindow(view, gtk_builder)
        self.__info_label = gtk_builder.get_object("info-label")


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                 Methods                                     #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Restart behaviour. '''
    def restart(self):
        
        self.__samples_view.restart()
        self.__canvas.restart()
        self.__zoom_tool.restart()
        #self.__color_tool.restart()
        self.__selection_window.restart()

    ''' Activates fullscreen mode. '''
    def fullscreen(self):
        self.get_window().fullscreen()

    ''' Deactivates fullscreen mode. '''
    def unfullscreen(self):
        self.get_window().unfullscreen()

    ''' Sets the info label text. '''
    def set_info_label_text(self, text):
        self.__info_label.set_label(text)


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              Getters & Setters                              #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_menubar(self):
        return self.__menubar

    def set_menubar(self, menubar):
        self.__menubar = menubar

    def get_toolbar(self):
        return self.__toolbar

    def set_toolbar(self, toolbar):
        self.__toolbar = toolbar

    def get_zoom_tool(self):
        return self.__zoom_tool

    def set_zoom_tool(self, zoom_tool):
        self.__zoom_tool = zoom_tool

    def get_color_tool(self):
        return self.__color_tool

    def set_color_tool(self, color_tool):
        self.__color_tool = color_tool

    def get_samples_view(self):
        return self.__samples_view

    def set_samples_view(self, samples_view):
        self.__samples_view = samples_view

    def get_canvas(self):
        return self.__canvas

    def set_canvas(self, canvas):
        self.__canvas = canvas

    def get_selection_window(self):
        return self.__selection_window

    def set_selection_window(self, selection_window):
        self.__selection_window = selection_window

    def get_info_label(self):
        return self.__info_label

    def set_info_label(self, info_label):
        self.__info_label = info_label



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	SettingsWindow                                                            #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class SettingsWindow(MyWindow):

    '''
        The SettingsWindow class.
    '''

    ''' Initialization method. '''
    def __init__(self, window):

        super().__init__(window)

        self.__initialize()

        self.__algorithm_label = None
        self.__algorithm_combobox = None
        self.__fit_tail_label = None
        self.__fit_tail_switch = None
        self.__fit_head_label = None
        self.__fit_head_switch = None
        
    ''' Initialization behaviour. '''    
    def __initialize(self):
        self.__ask_for_settings = True
        
    ''' Restart behaviour. '''    
    def restart(self):
        self.__initialize()


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                 Methods                                     #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Sets the components visibility. '''
    def set_components_visibility(self, visible):

        self.__fit_tail_label.set_visible(visible)
        self.__fit_tail_switch.set_visible(visible)
        self.__fit_head_label.set_visible(visible)
        self.__fit_head_switch.set_visible(visible)

    ''' Shows components.'''
    def show_components(self, algorithm_settings_dto):

        if algorithm_settings_dto is not None:

            self.__ask_for_settings = False

            self.__algorithm_combobox.set_active(
                algorithm_settings_dto.get_algorithm_id())

            if (algorithm_settings_dto.get_algorithm_id() == 
                AlgorithmSettingsDto.OPENCOMET):

                visibility = False

            elif (algorithm_settings_dto.get_algorithm_id() ==
                  AlgorithmSettingsDto.FREECOMET):

                self.__fit_tail_switch.set_active(
                    algorithm_settings_dto.get_fit_tail())
                self.__fit_head_switch.set_active(
                    algorithm_settings_dto.get_fit_head())
                visibility = True

            self.set_components_visibility(visibility)
            
    ''' Returns a AlgorithmSettingsDto object. '''
    def get_algorithm_settings(self):
    
        return AlgorithmSettingsDto(
            self.get_algorithm_combobox().get_active(),
            self.get_fit_tail_switch().get_active(),
            self.get_fit_head_switch().get_active()
        )

    ''' Overrides MyWindow.hide() method. '''
    def hide(self):

        self.__ask_for_settings = True
        super().hide()



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_ask_for_settings(self):
        return self.__ask_for_settings

    def set_ask_for_settings(self, ask_for_settings):
        self.__ask_for_settings = ask_for_settings

    def get_algorithm_label(self):
        return self.__algorithm_label

    def set_algorithm_label(self, algorithm_label):
        self.__algorithm_label = algorithm_label

    def get_algorithm_combobox(self):
        return self.__algorithm_combobox

    def set_algorithm_combobox(self, algorithm_combobox):
        self.__algorithm_combobox = algorithm_combobox

    def get_fit_tail_label(self):
        return self.__fit_tail_label

    def set_fit_tail_label(self, fit_tail_label):
        self.__fit_tail_label = fit_tail_label

    def get_fit_tail_switch(self):
        return self.__fit_tail_switch

    def set_fit_tail_switch(self, fit_tail_switch):
        self.__fit_tail_switch = fit_tail_switch

    def get_fit_head_label(self):
        return self.__fit_head_label

    def set_fit_head_label(self, fit_head_label):
        self.__fit_head_label = fit_head_label

    def get_fit_head_switch(self):
        return self.__fit_head_switch

    def set_fit_head_switch(self, fit_head_switch):
        self.__fit_head_switch = fit_head_switch

 

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	AnalyzeSamplesWindow                                                      #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class AnalyzeSamplesWindow(SettingsWindow):

    '''
        The AnalyzeSamplesWindow class.
    '''

    STACK_SAMPLES_SELECTION = "page0"
    STACK_PARAMETERS_SELECTION = "page1"


    ''' Initialization method. '''
    def __init__(self, view, gtk_builder):

        super().__init__(gtk_builder.get_object("analyze-samples-window"))

        self.get_window().set_default_size(200, 400)

        self.__view = view

        # Initialize attributes
        self.__initialize()

        # Samples selection page components (page 0)
        self.__stack = gtk_builder.get_object("analyze-samples-window-stack")
        self.__samples_view = AnalyzeSamplesView(gtk_builder, self)
        self.__cancel_button = gtk_builder.get_object(
            "analyze-samples-cancel")
        self.__cancel_button_image = gtk_builder.get_object(
            "analyze-samples-window-cancel-image1")
        self.__next_button = gtk_builder.get_object(
            "analyze-samples-next")

        # Parameters selection page components (page 1)

        # SettingsWindow widgets
        self.set_algorithm_label(gtk_builder.get_object(
            "analyze-samples-window-algorithm-label"))
        self.set_algorithm_combobox(gtk_builder.get_object(
            "analyze-samples-window-algorithm-combobox"))
        self.get_algorithm_combobox().append("0", "FreeComet")
        self.get_algorithm_combobox().append("1", "OpenComet")
        self.set_fit_tail_label(gtk_builder.get_object(
            "analyze-samples-window-fit-tail-label"))
        self.set_fit_tail_switch(gtk_builder.get_object(
            "analyze-samples-window-fit-tail-switch"))
        self.set_fit_head_label(gtk_builder.get_object(
            "analyze-samples-window-fit-head-label"))
        self.set_fit_head_switch(gtk_builder.get_object(
            "analyze-samples-window-fit-head-switch"))
        # Buttons
        self.__back_button = gtk_builder.get_object(
            "analyze-samples-window-back")
        self.__back_button_image = gtk_builder.get_object(
            "analyze-samples-window-back-image")
        self.__execute_button = gtk_builder.get_object(
            "analyze-samples-window-execute")

    ''' Initialization behaviour. '''
    def __initialize(self):

        self.__sample_id_list = []
        self.__single_analysis_flag = False

    ''' Restart behaviour. '''
    def restart(self):
        self.__initialize()


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                 Methods                                     #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
   
    ''' MyWindow.hide() implementation. '''
    def hide(self):

        super().hide()
        self.__stack.set_visible_child_name(self.STACK_SAMPLES_SELECTION)
        self.__sample_id_list = []

    ''' MyWindow.show() implementation. '''
    def show(self):

        if self.__single_analysis_flag:
            self.__back_button.set_label(
                self.__view.get_controller().get_strings().CANCEL_BUTTON_LABEL)
            self.__back_button.set_image(self.__cancel_button_image)
        else:
            self.set_title(
                self.__view.get_controller().get_strings().ANALYZE_SAMPLES_WINDOW_TITLE)
            self.__back_button.set_label(
                self.__view.get_controller().get_strings().BACK_BUTTON_LABEL)
            self.__back_button.set_image(self.__back_button_image)

        MyWindow.show(self)

    ''' Transition to parameters window. '''
    def transition_to_parameters_window(self, algorithm_settings_dto):

        # Configure page 1
        self.__configure_parameters_window(algorithm_settings_dto)
        
        self.get_window().resize(200, 250)

        # Show page 1
        self.__stack.set_visible_child_name(self.STACK_PARAMETERS_SELECTION)

    ''' Transition to samples selection window. '''
    def transition_to_samples_selection_window(self):

        self.get_window().resize(200, 450)

        # Show page 0
        self.__stack.set_visible_child_name(self.STACK_SAMPLES_SELECTION) 

    ''' 
        Configures parameters window with given AlgorithmSettingsDto object.
    ''' 
    def __configure_parameters_window(self, algorithm_settings_dto):

        self.show_components(algorithm_settings_dto)

       
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                            Getters & Setters                                #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_single_analysis_flag(self):
        return self.__single_analysis_flag

    def set_single_analysis_flag(self, single_analysis_flag):
        self.__single_analysis_flag = single_analysis_flag

    def get_sample_id_list(self):
        return self.__sample_id_list

    def set_sample_id_list(self, sample_id_list):
        self.__sample_id_list = sample_id_list

    def get_stack(self):
        return self.__stack

    def set_stack(self, stack):
        self.__stack = stack

    def get_samples_view(self):
        return self.__samples_view

    def set_samples_view(self, samples_view):
        self.__samples_view = samples_view

    def get_cancel_button(self):
        return self.__cancel_button

    def set_cancel_button(self, cancel_button):
        self.__cancel_button = cancel_button

    def get_next_button(self):
        return self.__next_button

    def set_next_button(self, next_button):
        self.__start_buton = next_button

    def get_back_button(self):
        return self.__back_button

    def set_back_button(self, back_button):
        self.__back_button = back_button

    def get_execute_button(self):
        return self.__execute_button

    def set_execute_button(self, execute_button):
        self.__execute_button = execute_button

        

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	LoadSamplesWindow                                                         #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class LoadSamplesWindow(MyWindow):

    '''
        The LoadSamplesWindow class. The window that shows the user the files 
        loading progress when adding new samples.
    '''

    ''' Initialization method. '''
    def __init__(self, gtk_builder):

        # The window
        MyWindow.__init__(
            self, gtk_builder.get_object("load-samples-window"))
        self.get_window().set_default_size(440, 240)

        # The components
        self.__top_label = gtk_builder.get_object(
            "load-samples-top-label")
        self.__bottom_label = gtk_builder.get_object(
            "load-samples-bottom-label")
        self.__progress_bar = gtk_builder.get_object(
            "load-samples-progress-bar")


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_top_label(self):
        return self.__top_label

    def set_top_label(self, top_label):
        self.__top_label = top_label

    def get_bottom_label(self):
        return self.__bottom_label

    def set_bottom_label(self, bottom_label):
        self.__bottom_label = bottom_label

    def get_progress_bar(self):
        return self.__progress_bar

    def set_progress_bar(self, progress_bar):
        self.__progress_bar = progress_bar



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	SelectionWindow                                                           #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class SelectionWindow(MyWindow):

    '''
        The SelectionWindow class.
    '''

    COMET_SELECTION = "page0"
    COMET_BEING_EDITED = "page1"

    ''' Initialization method. '''
    def __init__(self, view, gtk_builder):

        MyWindow.__init__(self, gtk_builder.get_object("selection-window"))

        # Components
        self.__stack = gtk_builder.get_object("selection-window-stack")
        self.__title_label = gtk_builder.get_object(
            "selection-window-title-label")

        # Page0
        self.__selection_label = gtk_builder.get_object(
            "selection-window-selection-label")
        self.__delete_comet_button = gtk_builder.get_object(
            "selection-window-delete-comet")
        self.__remove_tail_button = gtk_builder.get_object(
            "selection-window-delete-tail")
        self.__edit_contour_button = gtk_builder.get_object(
            "selection-window-edit-contour")
        self.__focus_on_image_button = gtk_builder.get_object(
            "selection-window-focus-on-image")
        self.__see_parameters_button = gtk_builder.get_object(
            "selection-window-see-parameters")

        # Page1
        self.__editing_label = gtk_builder.get_object(
            "selection-window-editing-label")
        self.__editing_label.set_line_wrap(True)
        self.__cancel_button = gtk_builder.get_object(
            "selection-window-cancel")
        self.__save_button = gtk_builder.get_object(
            "selection-window-save")

        # Attributes
        self.__view = view

        self.transition_to_comet_selection()
 
    ''' Restart behaviour. '''        
    def restart(self):
        self.switch_off()


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                  Methods                                    #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Transition to 'comet selection' page. '''
    def transition_to_comet_selection(self):

        # Show page 0
        self.__stack.set_visible_child_name(SelectionWindow.COMET_SELECTION)

    ''' Transition to 'comet being edited' page. '''
    def transition_to_comet_being_edited(self):

        # Show page 1
        self.__stack.set_visible_child_name(SelectionWindow.COMET_BEING_EDITED)
                
        comet_number = self.__view.get_active_sample_comet_number(
            self.__view.get_controller().get_active_sample_comet_being_edited_id())
        self.__editing_label.set_label(
            self.__view.get_controller().get_strings().SELECTION_WINDOW_COMET_BEING_EDITED_LABEL.format(
                comet_number))

    ''' Switches on the SelectionWindow. '''
    def switch_on(self):
        self.show() 

    ''' Switches off the SelectionWindow. '''
    def switch_off(self):
        self.hide()

    ''' Updates the SelectionWindow configuration. '''
    def update(self):
       
        self.switch_on()

        # Editing Mode
        if self.__view.get_controller().get_editing():

            if self.__view.get_controller().get_active_sample_comet_being_edited_id() is not None:
                self.transition_to_comet_being_edited()
                
                return

            self.switch_off()

        else:
        
            self.transition_to_comet_selection()

            comet_view = self.__view.get_controller().get_active_sample_selected_comet_view()
            # A comet is selected
            if comet_view is not None:

                self.switch_on()

                comet_number = self.__view.get_active_sample_comet_number(
                    comet_view.get_id())            
                self.__selection_label.set_label(
                    self.__view.get_controller().get_strings().SELECTION_WINDOW_SELECTION_LABEL.format(
                        comet_number))

                self.__remove_tail_button.set_sensitive(
                    comet_view.get_scaled_tail_contour() is not None)

            # No comets selected
            else:
                self.switch_off()


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_title_label(self):
        return self.__title_label

    def set_tittle_label(self, title_label):
        self.__title_label = title_label

    def get_selection_label(self):
        return self.__selection_label

    def set_selection_label(self, selection_label):
        self.__selection_label = selection_label

    def get_delete_comet_button(self):
        return self.__delete_comet_button

    def set_delete_comet_button(self, delete_comet_button):
        self.__delete_comet_button = delete_comet_button

    def get_remove_tail_button(self):
        return self.__remove_tail_button

    def set_remove_tail_button(self, remove_tail_button):
        self.__remove_tail_button = remove_tail_button

    def get_edit_contour_button(self):
        return self.__edit_contour_button

    def set_edit_contour_button(self, edit_contour_button):
        self.__edit_contour_button = edit_contour_button

    def get_see_parameters_button(self):
        return self.__see_parameters_button

    def set_see_parameters_button(self, see_parameters_button):
        self.__see_parameters_button = see_parameters_button

    def get_cancel_button(self):
        return self.__cancel_button

    def set_cancel_button(self, cancel_button):
        self.__cancel_button = cancel_button

    def get_save_button(self):
        return self.__save_button

    def set_save_button(self, save_button):
        self.__save_button = save_button

    def get_stack(self):
        return self.__stack

    def set_stack(self, stack):
        self.__stack = stack

    def get_editing_label(self):
        return self.__editing_label



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	MainSettingsWindow                                                        #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class MainSettingsWindow(SettingsWindow):

    '''
        The MainSettingsWindow class.
    '''

    ''' Initialization method. '''
    def __init__(self, gtk_builder):

        # The window
        super().__init__(gtk_builder.get_object("settings-window"))
        self.get_window().set_default_size(440, 240) 

        # SettingsWindow widgets
        self.set_algorithm_label(gtk_builder.get_object("algorithm-label"))
        self.set_algorithm_combobox(gtk_builder.get_object(
            "algorithm-combobox"))
        self.get_algorithm_combobox().append("0", "FreeComet")
        self.get_algorithm_combobox().append("1", "OpenComet")  
        self.set_fit_tail_label(gtk_builder.get_object("fit-tail-label"))
        self.set_fit_tail_switch(gtk_builder.get_object("fit-tail-switch"))
        self.set_fit_head_label(gtk_builder.get_object("fit-head-label"))
        self.set_fit_head_switch(gtk_builder.get_object("fit-head-switch"))
            
        # Buttons
        self.__cancel_button = gtk_builder.get_object(
            "settings-window-cancel")
        self.__save_button = gtk_builder.get_object(
            "settings-window-save") 
  

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_cancel_button(self):
        return self.__cancel_button

    def set_cancel_button(self, cancel_button):
        self.__cancel_button = cancel_button

    def get_save_button(self):
        return self.__save_button

    def set_save_button(self, save_button):
        self.__save_button = save_button



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	CometParametersWindow                                                     #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class CometParametersWindow(MyWindow):

    '''
        The CometParametersWindow class.
    '''

    ''' Initialization method. '''
    def __init__(self, gtk_builder):

        # The window
        MyWindow.__init__(
            self, gtk_builder.get_object("comet-parameters-window"))

        # The components
        self.__sample_name_label = gtk_builder.get_object(
            "comet-parameters-window-sample-name-label")
        self.__comet_number_label = gtk_builder.get_object(
            "comet-parameters-window-comet-number-label")
        self.__comet_number_value_label = gtk_builder.get_object(
            "comet-parameters-window-comet-number-value-label")
        self.__comet_area_label = gtk_builder.get_object(
            "comet-parameters-window-comet-area-label")
        self.__comet_area_value_label = gtk_builder.get_object(
            "comet-parameters-window-comet-area-value-label")
        self.__comet_intensity_label = gtk_builder.get_object(
            "comet-parameters-window-comet-intensity-label")
        self.__comet_intensity_value_label = gtk_builder.get_object(
            "comet-parameters-window-comet-intensity-value-label")
        self.__comet_length_label = gtk_builder.get_object(
            "comet-parameters-window-comet-length-label")
        self.__comet_length_value_label = gtk_builder.get_object(
            "comet-parameters-window-comet-length-value-label")
        self.__comet_dna_label = gtk_builder.get_object(
            "comet-parameters-window-comet-dna-label")
        self.__comet_dna_value_label = gtk_builder.get_object(
            "comet-parameters-window-comet-dna-value-label")
        self.__head_area_label = gtk_builder.get_object(
            "comet-parameters-window-head-area-label")
        self.__head_area_value_label = gtk_builder.get_object(
            "comet-parameters-window-head-area-value-label")
        self.__head_intensity_label = gtk_builder.get_object(
            "comet-parameters-window-head-intensity-label")
        self.__head_intensity_value_label = gtk_builder.get_object(
            "comet-parameters-window-head-intensity-value-label")
        self.__head_length_label = gtk_builder.get_object(
            "comet-parameters-window-head-length-label")
        self.__head_length_value_label = gtk_builder.get_object(
            "comet-parameters-window-head-length-value-label")
        self.__head_dna_label = gtk_builder.get_object(
            "comet-parameters-window-head-dna-label")
        self.__head_dna_value_label = gtk_builder.get_object(
            "comet-parameters-window-head-dna-value-label")
        self.__head_dna_percentage_label = gtk_builder.get_object(
            "comet-parameters-window-head-dna-percentage-label")
        self.__head_dna_percentage_value_label = gtk_builder.get_object(
            "comet-parameters-window-head-dna-percentage-value-label")
        self.__tail_area_label = gtk_builder.get_object(
            "comet-parameters-window-tail-area-label")
        self.__tail_area_value_label = gtk_builder.get_object(
            "comet-parameters-window-tail-area-value-label")
        self.__tail_intensity_label = gtk_builder.get_object(
            "comet-parameters-window-tail-intensity-label")
        self.__tail_intensity_value_label = gtk_builder.get_object(
            "comet-parameters-window-tail-intensity-value-label")
        self.__tail_length_label = gtk_builder.get_object(
            "comet-parameters-window-tail-length-label")
        self.__tail_length_value_label = gtk_builder.get_object(
            "comet-parameters-window-tail-length-value-label")
        self.__tail_dna_label = gtk_builder.get_object(
            "comet-parameters-window-tail-dna-label")
        self.__tail_dna_value_label = gtk_builder.get_object(
            "comet-parameters-window-tail-dna-value-label")
        self.__tail_dna_percentage_label = gtk_builder.get_object(
            "comet-parameters-window-tail-dna-percentage-label")
        self.__tail_dna_percentage_value_label = gtk_builder.get_object(
            "comet-parameters-window-tail-dna-percentage-value-label")
        self.__tail_moment_label = gtk_builder.get_object(
            "comet-parameters-window-tail-moment-label")
        self.__tail_moment_value_label = gtk_builder.get_object(
            "comet-parameters-window-tail-moment-value-label")
        self.__olive_moment_label = gtk_builder.get_object(
            "comet-parameters-window-olive-moment-label")
        self.__olive_moment_value_label = gtk_builder.get_object(
            "comet-parameters-window-olive-moment-value-label")


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                            Getters & Setters                                #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #  

    def get_sample_name_label(self):
        return self.__sample_name_label

    def get_sample_name_value_label(self):
        return self.__sample_name_value_label

    def get_comet_number_label(self):
        return self.__comet_number_label

    def get_comet_number_value_label(self):
        return self.__comet_number_value_label

    def get_comet_area_label(self):
        return self.__comet_area_label

    def get_comet_area_value_label(self):
        return self.__comet_area_value_label

    def get_comet_intensity_label(self):
        return self.__comet_intensity_label

    def get_comet_intensity_value_label(self):
        return self.__comet_intensity_value_label

    def get_comet_length_label(self):
        return self.__comet_length_label

    def get_comet_length_value_label(self):
        return self.__comet_length_value_label

    def get_comet_dna_label(self):
        return self.__comet_dna_label

    def get_comet_dna_value_label(self):
        return self.__comet_dna_value_label

    def get_head_area_label(self):
        return self.__head_area_label

    def get_head_area_value_label(self):
        return self.__head_area_value_label

    def get_head_intensity_label(self):
        return self.__head_intensity_label

    def get_head_intensity_value_label(self):
        return self.__head_intensity_value_label

    def get_head_length_label(self):
        return self.__head_length_label

    def get_head_length_value_label(self):
        return self.__head_length_value_label

    def get_head_dna_label(self):
        return self.__head_dna_label

    def get_head_dna_value_label(self):
        return self.__head_dna_value_label

    def get_head_dna_percentage_label(self):
        return self.__head_dna_percentage_label

    def get_head_dna_percentage_value_label(self):
        return self.__head_dna_percentage_value_label

    def get_tail_area_label(self):
        return self.__tail_area_label

    def get_tail_area_value_label(self):
        return self.__tail_area_value_label

    def get_tail_intensity_label(self):
        return self.__tail_intensity_label

    def get_tail_intensity_value_label(self):
        return self.__tail_intensity_value_label

    def get_tail_length_label(self):
        return self.__tail_length_label

    def get_tail_length_value_label(self):
        return self.__tail_length_value_label

    def get_tail_dna_label(self):
        return self.__tail_dna_label

    def get_tail_dna_value_label(self):
        return self.__tail_dna_value_label  

    def get_tail_dna_percentage_label(self):
        return self.__tail_dna_percentage_label

    def get_tail_dna_percentage_value_label(self):
        return self.__tail_dna_percentage_value_label

    def get_tail_moment_label(self):
        return self.__tail_moment_label

    def get_tail_moment_value_label(self):
        return self.__tail_moment_value_label

    def get_olive_moment_label(self):
        return self.__olive_moment_label

    def get_olive_moment_value_label(self):
        return self.__olive_moment_value_label



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
#  AnalyzeSamplesLoadingWindow                                                #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class AnalyzeSamplesLoadingWindow(MyWindow):

    '''
        The AnalyzeSamplesLoadingWindow class. The window that shows the user 
        which selected samples are being analyzed. 
    '''

    ''' Initialization method. '''
    def __init__(self, gtk_builder):

        # The window
        MyWindow.__init__(
            self, gtk_builder.get_object("analyze-samples-loading-window"))
        self.get_window().set_default_size(440, 240)

        # The components
        self.__top_label = gtk_builder.get_object(
            "analyze-samples-loading-window-top-label")
        self.__bottom_label = gtk_builder.get_object(
            "analyze-samples-loading-window-bottom-label")
        self.__spinner = gtk_builder.get_object(
            "analyze-samples-loading-window-spinner")
        self.__cancel_button = gtk_builder.get_object(
            "analyze-samples-loading-window-cancel")
        self.__initialize()

    ''' Initialization behaviour. '''
    def __initialize(self):
        self.__cancelled = False

    ''' Restart behaviour. '''
    def restart(self):
        self.__initialize()


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                  Methods                                    #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' MyWindow.show() implementation. '''
    def show(self):

        super().show()
        self.__spinner.start()

    ''' MyWindow.hide() implementation. '''
    def hide(self):

        self.__spinner.stop()
        self.__cancel_button.set_sensitive(True)
        self.__cancelled = False
        super().hide()


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              Getters & Setters                              #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_top_label(self):
        return self.__top_label

    def set_top_label(self, top_label):
        self.__top_label = top_label

    def get_bottom_label(self):
        return self.__bottom_label

    def set_bottom_label(self, bottom_label):
        self.__bottom_label = bottom_label

    def get_spinner(self):
        return self.__spinner

    def set_spinner(self, spinner):
        self.__spinner = spinner

    def get_cancel_button(self):
        return self.__cancel_button

    def set_cancel_button(self, cancel_button):
        self.__cancel_button = cancel_button

    def get_cancelled(self):
        return self.__cancelled

    def set_cancelled(self, cancelled):
        self.__cancelled = cancelled

