# -*- encoding: utf-8 -*-

'''
    The view module.
'''

# PyGObject imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

# Custom imports
from sample.dialog_response import DialogResponse
from sample.view.windows import CometParametersWindow, MainSettingsWindow, SelectionWindow, \
                    LoadSamplesWindow, AnalyzeSamplesWindow, MainWindow, \
                    AnalyzeSamplesLoadingWindow
from sample.view.view_store import ViewStore, SampleParameters
from sample.view.zoom_tool import ZoomTool
from sample.controller.algorithm_settings_dto import AlgorithmSettingsDto
from sample.observer import Observer
from sample.i18n.language import Language

import sample.config as config



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	View                                                                      #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class View(Observer):

    '''
        The View class. Implements Observer.
    '''
 
    ''' The class initialization. '''
    def __init__(self):
        
        self.__controller = None

        # Initialization
        self.__init_view()
        self.__init_store()
        
        # Style classes
        self.__dialog_add_new_samples_add_button.get_style_context().add_class(
            Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        self.__dialog_open_project_open_button.get_style_context().add_class(
            Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        self.__dialog_save_project_save_button.get_style_context().add_class(
            Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        self.__main_settings_window.get_save_button().get_style_context().\
            add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        self.__dialog_save_before_action_save_button.get_style_context().\
            add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        self.__dialog_generate_output_file_save_button.get_style_context().\
            add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        self.__analyze_samples_window.get_next_button().get_style_context().\
            add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        self.__analyze_samples_window.get_execute_button().get_style_context().\
            add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)

    ''' The GUI components initialization. '''
    def __init_view(self):

        # [1] Load .ui file
        gtk_builder = Gtk.Builder()
        try:
            gtk_builder.add_from_file(config.UI_FILE)
        except:
            print("ERROR: " + config.UI_FILE + " not found")
            self.exit()

        # [2] Initialize GUI components

        # Windows. Each window class initializes its components.
        self.__main_window = MainWindow(self, gtk_builder)
        self.__analyze_samples_window = AnalyzeSamplesWindow(
            self, gtk_builder)
        self.__analyze_samples_loading_window = AnalyzeSamplesLoadingWindow(
            gtk_builder)
        self.__load_samples_window = LoadSamplesWindow(gtk_builder)
        self.__main_settings_window = MainSettingsWindow(gtk_builder)
        self.__comet_parameters_window = CometParametersWindow(gtk_builder)

        # Context menus
        self.__context_menu1 = gtk_builder.get_object(
            "context-menu1")
        self.__context_menu1_analyze_button = gtk_builder.get_object(
            "context-menu1-analyze")
        self.__context_menu1_rename_button = gtk_builder.get_object(
            "context-menu1-rename")
        self.__context_menu1_delete_button = gtk_builder.get_object(
            "context-menu1-delete")       
        self.__context_menu2 = gtk_builder.get_object(
            "context-menu2")
        self.__context_menu2_add_button = gtk_builder.get_object(
            "context-menu2-add")

        # Dialogs
        self.__dialog_add_new_samples = gtk_builder.get_object(
             "dialog-add-samples")
        self.__dialog_add_new_samples_cancel_button = gtk_builder.get_object(
            "dialog-add-samples-cancel")
        self.__dialog_add_new_samples_add_button = gtk_builder.get_object(
            "dialog-add-samples-add")
        self.__dialog_save_project_as = gtk_builder.get_object(
            "dialog-save-project-as")
        self.__dialog_save_project_cancel_button = gtk_builder.get_object(
            "dialog-save-project-cancel")
        self.__dialog_save_project_save_button = gtk_builder.get_object(
            "dialog-save-project-save")
        self.__dialog_open_project = gtk_builder.get_object(
            "dialog-open-project")
        self.__dialog_open_project_cancel_button = gtk_builder.get_object(
            "dialog-open-project-cancel")
        self.__dialog_open_project_open_button = gtk_builder.get_object(
            "dialog-open-project-open")
        self.__dialog_save_before_action = gtk_builder.get_object(
            "dialog-save-before-action")
        self.__dialog_save_before_action_label = gtk_builder.get_object(
            "dialog-save-before-action-label")
        self.__dialog_save_before_action_cancel_button = gtk_builder.get_object(
            "dialog-save-before-action-cancel")
        self.__dialog_save_before_action_discard_button = gtk_builder.get_object(
            "dialog-save-before-action-discard")
        self.__dialog_save_before_action_save_button = gtk_builder.get_object(
            "dialog-save-before-action-save")
        self.__dialog_about = gtk_builder.get_object("dialog-about")
        self.__dialog_generate_output_file = gtk_builder.get_object(
            "dialog-generate-output-file")
        self.__dialog_generate_output_file_cancel_button = gtk_builder.get_object(
            "dialog-generate-output-file-cancel")
        self.__dialog_generate_output_file_save_button = gtk_builder.get_object(
            "dialog-generate-output-file-save")
        self.__dialog_comet_color_chooser = gtk_builder.get_object(
            "dialog-comet-color-chooser")
        self.__dialog_head_color_chooser = gtk_builder.get_object(
            "dialog-head-color-chooser")

    ''' The ViewStore initialization. '''
    def __init_store(self):
        self.__view_store = ViewStore()
        self.__view_store.register(self)

    ''' Connect Controller with View; signals and their callbacks. '''
    def connect(self, controller):

        # The Controller
        self.__controller = controller

        # MainWindow
        self.__main_window.get_window().connect(
            "delete-event", self.__on_main_window_delete_event)
        self.__main_window.get_window().connect(
            "configure-event", self.__on_main_window_configure_event)

        # MenuBar
        menubar = self.__main_window.get_menubar()
        menubar.get_new_button().connect(
            "activate", self.__on_menubar_new_button_activated)
        menubar.get_open_button().connect(
            "activate", self.__on_menubar_open_button_activated)
        menubar.get_save_button().connect(
            "activate", self.__on_menubar_save_button_activated)
        menubar.get_save_as_button().connect(
            "activate", self.__on_menubar_save_as_button_activated)
        menubar.get_exit_button().connect(
            "activate", self.__on_menubar_exit_button_activated)
        menubar.get_spanish_language_button().connect(
            "activate", self.__on_menubar_spanish_language_button_activated)
        menubar.get_english_language_button().connect(
            "activate", self.__on_menubar_english_language_button_activated)
        menubar.get_theme_clear_button().connect(
            "activate", self.__on_menubar_theme_clear_button_activated)
        menubar.get_theme_dark_button().connect(
            "activate", self.__on_menubar_theme_dark_button_activated)
        menubar.get_about_button().connect(
            "activate", self.__on_menubar_about_button_activated)
            
        if controller.get_i18n().get_language() == Language.SPANISH:
            menubar.get_spanish_language_button().set_active(True)
        else:
            menubar.get_english_language_button().set_active(True)

        # ToolBar
        self.__main_window.get_toolbar().get_new_button().connect(
            "clicked", self.__on_toolbar_new_button_clicked)
        self.__main_window.get_toolbar().get_open_button().connect(
            "clicked", self.__on_toolbar_open_button_clicked)
        self.__main_window.get_toolbar().get_save_button().connect(
            "clicked", self.__on_toolbar_save_button_clicked)
        self.__main_window.get_toolbar().get_undo_button().connect(
            "clicked", self.__on_toolbar_undo_button_clicked)
        self.__main_window.get_toolbar().get_redo_button().connect(
            "clicked", self.__on_toolbar_redo_button_clicked)
        self.__main_window.get_toolbar().get_fullscreen_button().connect(
            "clicked", self.__on_toolbar_fullscreen_button_clicked)

        # SamplesView
        self.__main_window.get_samples_view().get_add_samples_button().connect(
            "clicked", self.__on_samples_view_add_samples_button_clicked)
        self.__main_window.get_samples_view().get_treeview().connect(
            "row-activated", self.__on_samples_view_treeview_row_activated)
        self.__main_window.get_samples_view().get_treeview().connect(
            "button-press-event", self.__on_samples_view_treeview_button_press_event)
        self.__main_window.get_samples_view().get_treeview().connect(
            "key-press-event", self.__on_samples_view_treeview_row_key_press_event)
        self.__main_window.get_samples_view().get_treeview().connect(
            "query-tooltip", self.__on_samples_view_treeview_row_query_tooltip)
        self.__main_window.get_samples_view().get_treeview_renderer_text().connect(
            "edited", self.__on_samples_view_treeview_row_edited)
        self.__main_window.get_samples_view().get_column_event_box().connect(
            "button-press-event", self.__on_samples_view_column_label_button_press_event)
        self.__main_window.get_samples_view().get_treeview().connect(
            "focus-out-event", self.__on_samples_view_focus_out_event)

        # Canvas
        self.__main_window.get_canvas().get_viewport().connect(
            "scroll-event", self.__on_canvas_scroll_event)
        self.__main_window.get_canvas().get_viewport().connect(
            "size-allocate", self.__on_viewport_size_allocate)
        self.__main_window.get_canvas().get_drawing_area().connect(
            "enter-notify-event", self.__on_canvas_mouse_enter)
        self.__main_window.get_canvas().get_drawing_area().connect(
            "leave-notify-event", self.__on_canvas_mouse_leave)
        self.__main_window.get_canvas().get_drawing_area().connect(
            "motion-notify-event", self.__on_canvas_mouse_motion)        
        self.__main_window.get_canvas().get_drawing_area().connect(
            "button-press-event", self.__on_canvas_button_press_event)
        self.__main_window.get_canvas().get_drawing_area().connect(
            "button-release-event", self.__on_canvas_button_release_event)
        self.__main_window.get_canvas().get_drawing_area().connect(
            "draw", self.__on_canvas_draw)
        self.__main_window.get_canvas().get_drawing_area().connect(
            "key-press-event", self.__on_canvas_key_press_event)
        self.__main_window.get_canvas().get_drawing_area().connect(
            "size-allocate", self.__on_canvas_size_allocate)
        self.__main_window.get_canvas().get_analyze_button().connect(
            "clicked", self.__on_canvas_analyze_button_clicked)
        self.__main_window.get_canvas().get_analyze_all_button().connect(
            "clicked", self.__on_canvas_analyze_all_button_clicked)
        self.__main_window.get_canvas().get_selection_button().connect(
            "clicked", self.__on_canvas_selection_button_clicked)
        self.__main_window.get_canvas().get_editing_button().connect(
            "clicked", self.__on_canvas_editing_button_clicked)
        self.__main_window.get_canvas().get_editing_selection_button().connect(
            "clicked", self.__on_canvas_editing_selection_button_clicked)
        self.__main_window.get_canvas().get_building_button().connect(
            "clicked", self.__on_canvas_editing_building_button_clicked)
        self.__main_window.get_canvas().get_build_tail_contour_button().connect(
            "clicked", self.__on_canvas_build_tail_contour_button_clicked)
        self.__main_window.get_canvas().get_build_head_contour_button().connect(
            "clicked", self.__on_canvas_build_head_contour_button_clicked)
        self.__main_window.get_canvas().get_settings_button().connect(
            "clicked", self.__on_canvas_settings_button_clicked)
        self.__main_window.get_canvas().get_generate_output_file_button().connect(
            "clicked", self.__on_canvas_generate_output_file_button_clicked)
        self.__main_window.get_canvas().get_scrolledwindow().get_hscrollbar().connect(
            "value-changed", self.__on_canvas_horizontal_scrollbar_value_changed)
        self.__main_window.get_canvas().get_scrolledwindow().get_vscrollbar().connect(
            "value-changed", self.__on_canvas_vertical_scrollbar_value_changed)
        self.__main_window.get_canvas().get_delete_delimiter_point_button().connect(
            "activate", self.__on_canvas_delete_delimiter_point_button_activated)
        self.__main_window.get_canvas().get_add_delimiter_point_button().connect(
            "activate", self.__on_canvas_add_delimiter_point_button_activated)

        # ColorTool
        self.__main_window.get_color_tool().get_tail_color_button_image().connect(
            "size-allocate", self.__on_canvas_tail_color_button_image_size_allocated)
        self.__main_window.get_color_tool().get_head_color_button_image().connect(
            "size-allocate", self.__on_canvas_head_color_button_image_size_allocated)
        self.__main_window.get_color_tool().get_tail_color_button().connect(
            "clicked", self.__on_canvas_tail_color_button_clicked)
        self.__main_window.get_color_tool().get_head_color_button().connect(
            "clicked", self.__on_canvas_head_color_button_clicked)

        # ZoomTool
        self.__main_window.get_zoom_tool().get_combobox().connect(
            "changed", self.__on_zoom_combobox_changed)
        self.__main_window.get_zoom_tool().get_zoom_out_button().connect(
            "clicked", self.__on_zoom_out_button_clicked)
        self.__main_window.get_zoom_tool().get_zoom_in_button().connect(
            "clicked", self.__on_zoom_in_button_clicked)
        self.__main_window.get_zoom_tool().get_entry().connect(
            "activate", self.__on_zoom_tool_entry_activated)
        self.__main_window.get_zoom_tool().get_entry().connect(
            "focus-in-event", self.__on_zoom_tool_entry_focus_in_event) 
        self.__main_window.get_zoom_tool().get_entry().connect(
            "focus-out-event", self.__on_zoom_tool_entry_focus_out_event)
        self.__main_window.get_zoom_tool().get_entry().connect(
            "icon-press", self.__on_zoom_tool_entry_icon_press)

        # ContextMenus
        self.__context_menu1_analyze_button.connect(
            "activate", self.__on_context_menu1_analyze_sample)
        self.__context_menu1_rename_button.connect(
            "activate", self.__on_context_menu1_rename)
        self.__context_menu1_delete_button.connect(
            "activate", self.__on_context_menu1_delete)
        self.__context_menu2_add_button.connect(
            "activate", self.__on_context_menu2_add)
        self.__main_window.get_canvas().get_selection_context_menu_flip_button().connect(
            "activate", self.__on_canvas_context_menu_flip)
        self.__main_window.get_canvas().get_selection_context_menu_invert_button().connect(
            "activate", self.__on_canvas_context_menu_invert)

        # AnalyzeSamplesWindow
        self.__analyze_samples_window.get_window().connect(
            "delete-event", self.__on_analyze_samples_window_delete_event)
        self.__analyze_samples_window.get_samples_view().get_treeview_renderer_toggle().connect(
            "toggled", self.__on_analyze_samples_view_row_toggled)
        self.__analyze_samples_window.get_cancel_button().connect(
            "clicked", self.__on_analyze_samples_samples_selection_window_cancel_button_clicked)
        self.__analyze_samples_window.get_next_button().connect(
            "clicked", self.__on_analyze_samples_samples_selection_window_next_button_clicked)
        self.__analyze_samples_window.get_samples_view().get_samples_column_toggle().connect(
            "clicked", self.__on_samples_column_toggle_clicked)
        self.__analyze_samples_window.get_back_button().connect(
            "clicked", self.__on_analyze_samples_parameters_window_back_button_clicked)
        self.__analyze_samples_window.get_execute_button().connect(
            "clicked", self.__on_analyze_samples_parameters_window_execute_button_clicked)
        self.__analyze_samples_window.get_algorithm_combobox().connect(
            "changed", self.__on_settings_window_algorithm_combobox_changed,
            self.__analyze_samples_window)

        # AnalyzeSamplesLoadingWindow
        self.__analyze_samples_loading_window.get_cancel_button().connect(
            "clicked", self.__on_analyze_samples_loading_window_cancel_button_clicked)

        # MainSettingsWindow
        self.__main_settings_window.get_window().connect(
            "delete-event", self.__on_settings_window_delete_event)
        self.__main_settings_window.get_cancel_button().connect(
            "clicked", self.__on_settings_window_cancel_button_clicked)
        self.__main_settings_window.get_save_button().connect(
            "clicked", self.__on_settings_window_save_button_clicked)
        self.__main_settings_window.get_algorithm_combobox().connect(
            "changed", self.__on_settings_window_algorithm_combobox_changed,
            self.__main_settings_window)

        # SelectionWindow
        self.__main_window.get_selection_window().get_delete_comet_button().\
            connect("clicked", self.__on_delete_comet_button_clicked)
        self.__main_window.get_selection_window().get_remove_tail_button().\
            connect("clicked", self.__on_remove_tail_button_clicked)
        self.__main_window.get_selection_window().get_edit_contour_button().\
            connect("clicked", self.__on_edit_comet_contours_button_clicked)
        self.__main_window.get_selection_window().\
            get_see_parameters_button().connect(
                "clicked", self.__on_see_parameters_button_clicked)
        self.__main_window.get_selection_window().get_cancel_button().connect(
            "clicked", self.__on_editing_comet_cancel_button_clicked)
        self.__main_window.get_selection_window().get_save_button().connect(
            "clicked", self.__on_editing_comet_save_button_clicked)

        # CometParametersWindow
        self.__comet_parameters_window.get_window().\
            connect("delete-event",
                self.__on_comet_parameters_window_delete_event)

    ''' Sets the translatable strings of the application. '''
    def set_strings(self, strings):

        # MainWindow
        self.__set_info_label_text(
            len(self.__view_store.get_store()))

        menubar = self.__main_window.get_menubar()
        # MenuBar
        menubar.get_menu_file().set_label(
            strings.MENUBAR_FILE_BUTTON_LABEL)
        menubar.get_new_button().set_label(
            strings.FILE_MENU_NEW_PROJECT_BUTTON_LABEL)
        menubar.get_open_button().set_label(
            strings.FILE_MENU_OPEN_PROJECT_BUTTON_LABEL)
        menubar.get_save_button().set_label(
            strings.FILE_MENU_SAVE_PROJECT_BUTTON_LABEL)
        menubar.get_save_as_button().set_label(
            strings.FILE_MENU_SAVE_PROJECT_AS_BUTTON_LABEL)
        menubar.get_exit_button().set_label(
            strings.FILE_MENU_EXIT_BUTTON_LABEL)
        menubar.get_menu_preferences().set_label(
            strings.MENUBAR_PREFERENCES_BUTTON_LABEL)
        menubar.get_menu_language().set_label(
            strings.PREFERENCES_MENU_LANGUAGE_BUTTON_LABEL)
        menubar.get_spanish_language_button().set_label(
            strings.PREFERENCES_MENU_LANGUAGE_SPANISH_LANGUAGE_BUTTON_LABEL)
        menubar.get_english_language_button().set_label(
            strings.PREFERENCES_MENU_LANGUAGE_ENGLISH_LANGUAGE_BUTTON_LABEL)
        menubar.get_menu_help().set_label(
            strings.MENUBAR_HELP_BUTTON_LABEL)
        menubar.get_menu_theme().set_label(
            strings.PREFERENCES_MENU_THEME_BUTTON_LABEL)
        menubar.get_theme_clear_button().set_label(
            strings.PREFERENCES_MENU_THEME_CLEAR_BUTTON_LABEL)
        menubar.get_theme_dark_button().set_label(
            strings.PREFERENCES_MENU_THEME_DARK_BUTTON_LABEL)
        menubar.get_about_button().set_label(
            strings.HELP_MENU_ABOUT_BUTTON_LABEL)

        toolbar = self.__main_window.get_toolbar()
        # ToolBar
        toolbar.get_new_button().set_label(
            strings.CREATE_NEW_PROJECT_TOOLBAR_BUTTON_LABEL)
        toolbar.get_new_button().set_tooltip_text(
            strings.CREATE_NEW_PROJECT_TOOLBAR_BUTTON_TOOLTIP)
        toolbar.get_open_button().set_label(
            strings.OPEN_PROJECT_TOOLBAR_BUTTON_LABEL)
        toolbar.get_open_button().set_tooltip_text(
            strings.OPEN_PROJECT_TOOLBAR_BUTTON_TOOLTIP)
        toolbar.get_save_button().set_label(
            strings.SAVE_PROJECT_TOOLBAR_BUTTON_LABEL)
        toolbar.get_save_button().set_tooltip_text(
            strings.SAVE_PROJECT_TOOLBAR_BUTTON_TOOLTIP)
        toolbar.get_undo_button().set_label(
            strings.UNDO_TOOLBAR_BUTTON_LABEL)
        toolbar.get_undo_button().set_tooltip_text(
            self.__controller.get_undo_button_tooltip())
        toolbar.get_redo_button().set_label(
            strings.REDO_TOOLBAR_BUTTON_LABEL)
        toolbar.get_redo_button().set_tooltip_text(
            self.__controller.get_redo_button_tooltip())
        toolbar.get_fullscreen_button().set_label(
            strings.FULLSCREEN_TOOLBAR_BUTTON_LABEL)
        toolbar.get_fullscreen_button().set_tooltip_text(
            strings.FULLSCREEN_TOOLBAR_BUTTON_TOOLTIP)

        zoom_tool = self.__main_window.get_zoom_tool()
        # ZoomTool
        zoom_tool.get_combobox().set_tooltip_text(
            strings.ZOOM_COMBOBOX_TOOLTIP)      
        zoom_tool.get_zoom_out_button().set_tooltip_text(
            strings.ZOOM_OUT_BUTTON_TOOLTIP)
        zoom_tool.get_zoom_in_button().set_tooltip_text(
            strings.ZOOM_IN_BUTTON_TOOLTIP)
        zoom_tool.get_entry().set_icon_tooltip_text(
            ZoomTool.SECONDARY_POSITION,
            strings.ZOOM_COMBOBOX_ICON_TOOLTIP)
        zoom_tool.get_zoom_in_button().set_label(
            strings.ZOOM_IN_BUTTON_LABEL)
        zoom_tool.get_zoom_out_button().set_label(
            strings.ZOOM_OUT_BUTTON_LABEL)

        canvas = self.__main_window.get_canvas()
        # Canvas
        canvas.get_analyze_button().set_tooltip_text(
            strings.ANALYZE_SAMPLES_BUTTON_TOOLTIP)
        canvas.get_analyze_all_button().set_tooltip_text(
            strings.QUICK_ANALYZE_BUTTON_TOOLTIP)
        canvas.get_settings_button().set_tooltip_text(
            strings.PARAMETERS_BUTTON_TOOLTIP)
        canvas.get_generate_output_file_button().set_tooltip_text(
            strings.GENERATE_OUTPUT_FILE_BUTTON_TOOLTIP)
        canvas.get_selection_button().set_tooltip_text(
            strings.SELECTION_MODE_BUTTON_TOOLTIP)
        canvas.get_editing_button().set_tooltip_text(
            strings.EDITING_MODE_BUTTON_TOOLTIP)
        canvas.get_editing_selection_button().set_tooltip_text(
            strings.EDITING_SELECTION_MODE_BUTTON_TOOLTIP)
        canvas.get_building_button().set_tooltip_text(
            strings.EDITING_BUILDING_MODE_BUTTON_TOOLTIP)
        canvas.get_build_tail_contour_button().set_tooltip_text(
            strings.BUILDING_TAIL_CONTOUR_MODE_BUTTON_TOOLTIP)
        canvas.get_build_head_contour_button().set_tooltip_text(
            strings.BUILDING_HEAD_CONTOUR_MODE_BUTTON_TOOLTIP)
        canvas.get_add_delimiter_point_button().set_label(
            strings.ADD_DELIMITER_POINT_BUTTON_LABEL)
        canvas.get_delete_delimiter_point_button().set_label(
            strings.DELETE_DELIMITER_POINTS_BUTTON_LABEL)
        self.__main_window.get_color_tool().get_tail_color_button().\
            set_tooltip_text(strings.TAIL_CONTOUR_COLOR_LABEL)
        self.__main_window.get_color_tool().get_head_color_button().\
            set_tooltip_text(strings.HEAD_CONTOUR_COLOR_LABEL)

        samples_view = self.__main_window.get_samples_view()
        # SamplesView
        samples_view.get_treeview().props.has_tooltip = True
        samples_view.get_add_samples_button().set_tooltip_text(
            strings.ADD_SAMPLES_BUTTON_TOOLTIP)
        samples_view.get_column_label().set_label(
            strings.SAMPLES_VIEW_COLUMN_LABEL)
        
        # MainSettingsWindow
        self.__main_settings_window.get_algorithm_label().set_label(
            strings.ALGORITHM_LABEL)
        self.__main_settings_window.get_fit_tail_label().set_label(
            strings.FIT_TAIL_LABEL)
        self.__main_settings_window.get_fit_head_label().set_label(
            strings.FIT_HEAD_LABEL)
        self.__main_settings_window.set_title(
            strings.SETTINGS_WINDOW_TITLE)
        self.__main_settings_window.get_cancel_button()\
            .set_label(strings.CANCEL_BUTTON_LABEL)
        self.__main_settings_window.get_save_button()\
            .set_label(strings.SAVE_BUTTON_LABEL)

        # AnalyzeSamplesWindow
        self.__analyze_samples_window.get_algorithm_label().set_label(
            strings.ALGORITHM_LABEL)
        self.__analyze_samples_window.get_fit_tail_label().set_label(
            strings.FIT_TAIL_LABEL)
        self.__analyze_samples_window.get_fit_head_label().set_label(
            strings.FIT_HEAD_LABEL)       
        self.__analyze_samples_window.get_cancel_button().set_label(
            strings.CANCEL_BUTTON_LABEL)
        self.__analyze_samples_window.get_next_button().set_label(
            strings.NEXT_BUTTON_LABEL)
        self.__analyze_samples_window.get_execute_button().set_label(
            strings.EXECUTE_BUTTON_LABEL)
        self.__analyze_samples_window.get_samples_view().\
            get_samples_column_name().set_title(strings.SAMPLE_LABEL)

        # ContextMenus
        self.__context_menu1_analyze_button.set_label(
            strings.ANALYZE_BUTTON_LABEL)
        self.__context_menu1_rename_button.set_label(
            strings.RENAME_BUTTON_LABEL)
        self.__context_menu1_delete_button.set_label(
            strings.DELETE_BUTTON_LABEL)   
        self.__context_menu2_add_button.set_label(
            strings.SAMPLES_VIEW_CONTEXT_MENU_ADD_BUTTON_LABEL)
        canvas.get_selection_context_menu_flip_button().\
            set_label(strings.FLIP_BUTTON_LABEL)
        canvas.get_selection_context_menu_invert_button().\
            set_label(strings.INVERT_BUTTON_LABEL)
        
        # Dialogs      
        self.__dialog_about.set_comments(strings.DIALOG_ABOUT_COMMENTS)       
        self.__dialog_add_new_samples.set_title(
            strings.DIALOG_ADD_SAMPLES_TITLE)
        self.__dialog_add_new_samples_cancel_button.set_label(
            strings.CANCEL_BUTTON_LABEL)
        self.__dialog_add_new_samples_add_button.set_label(
            strings.ADD_BUTTON_LABEL)
        self.__dialog_open_project.set_title(
            strings.DIALOG_OPEN_PROJECT_TITLE)
        self.__dialog_open_project_cancel_button.set_label(
            strings.CANCEL_BUTTON_LABEL)
        self.__dialog_open_project_open_button.set_label(
            strings.OPEN_BUTTON_LABEL)
        self.__dialog_save_project_as.set_title(
            strings.DIALOG_SAVE_PROJECT_AS_TITLE)
        self.__dialog_save_project_cancel_button.set_label(
            strings.CANCEL_BUTTON_LABEL)
        self.__dialog_save_project_save_button.set_label(
            strings.SAVE_BUTTON_LABEL)
        self.__dialog_save_before_action.set_title(
            strings.DIALOG_SAVE_BEFORE_ACTION_TITLE)
        self.__dialog_save_before_action_cancel_button.set_label(
            strings.CANCEL_BUTTON_LABEL)
        self.__dialog_save_before_action_discard_button.set_label(
            strings.DISCARD_BUTTON_LABEL)
        self.__dialog_save_before_action_save_button.set_label(
            strings.SAVE_BUTTON_LABEL)
        self.__dialog_generate_output_file_cancel_button.set_label(
            strings.CANCEL_BUTTON_LABEL)
        self.__dialog_generate_output_file_save_button.set_label(
            strings.SAVE_BUTTON_LABEL)

        # AnalyzeSamplesLoadingWindow
        self.__analyze_samples_loading_window.get_cancel_button().set_label(
            strings.CANCEL_BUTTON_LABEL)

        selection_window = self.__main_window.get_selection_window()
        # SelectionWindow
        selection_window.get_title_label().set_label(
            strings.SELECTION_WINDOW_TITLE)
        selection_window.get_delete_comet_button().set_label(
            strings.SELECTION_WINDOW_DELETE_COMET_BUTTON_LABEL)
        selection_window.get_remove_tail_button().set_label(
            strings.SELECTION_WINDOW_REMOVE_TAIL_BUTTON_LABEL)
        selection_window.get_edit_contour_button().set_label(
            strings.SELECTION_WINDOW_EDIT_CONTOUR_BUTTON_LABEL)
        selection_window.get_see_parameters_button().set_label(
            strings.SELECTION_WINDOW_SEE_PARAMETERS_BUTTON_LABEL)
        selection_window.get_cancel_button().set_label(
            strings.CANCEL_BUTTON_LABEL)
        selection_window.get_save_button().set_label(
            strings.SAVE_BUTTON_LABEL)

        if self.__controller.get_active_sample_id() is not None:
        
            comet_number = self.__controller.get_comet_number(
                               self.__controller.get_active_sample_id(),
                               self.__controller.get_sample_comet_being_edited_id(
                                   self.__controller.get_active_sample_id()
                               )
                           )    

            selection_window.get_editing_label().set_label(
                strings.SELECTION_WINDOW_COMET_BEING_EDITED_LABEL.format(
                    comet_number))

        # CometParametersWindow
        self.__comet_parameters_window.set_title(
            strings.COMET_PARAMETERS_WINDOW_TITLE)
        self.__comet_parameters_window.get_comet_number_label().set_tooltip_text(
            strings.COMET_PARAMETERS_WINDOW_COMET_NUMBER_TOOLTIP)
        self.__comet_parameters_window.get_comet_area_label().set_tooltip_text(
            strings.COMET_PARAMETERS_WINDOW_COMET_AREA_TOOLTIP)
        self.__comet_parameters_window.get_comet_intensity_label().set_tooltip_text(
            strings.COMET_PARAMETERS_WINDOW_COMET_INTENSITY_TOOLTIP)
        self.__comet_parameters_window.get_comet_length_label().set_tooltip_text(
            strings.COMET_PARAMETERS_WINDOW_COMET_LENGTH_TOOLTIP)
        self.__comet_parameters_window.get_comet_dna_label().set_tooltip_text(
            strings.COMET_PARAMETERS_WINDOW_COMET_DNA_TOOLTIP)
        self.__comet_parameters_window.get_head_area_label().set_tooltip_text(
            strings.COMET_PARAMETERS_WINDOW_HEAD_AREA_TOOLTIP)
        self.__comet_parameters_window.get_head_intensity_label().set_tooltip_text(
            strings.COMET_PARAMETERS_WINDOW_HEAD_INTENSITY_TOOLTIP)
        self.__comet_parameters_window.get_head_length_label().set_tooltip_text(
            strings.COMET_PARAMETERS_WINDOW_HEAD_LENGTH_TOOLTIP)
        self.__comet_parameters_window.get_head_dna_label().set_tooltip_text(
            strings.COMET_PARAMETERS_WINDOW_HEAD_DNA_TOOLTIP)
        self.__comet_parameters_window.get_head_dna_percentage_label().set_tooltip_text(
            strings.COMET_PARAMETERS_WINDOW_HEAD_DNA_PERCENTAGE_TOOLTIP)
        self.__comet_parameters_window.get_tail_area_label().set_tooltip_text(
            strings.COMET_PARAMETERS_WINDOW_TAIL_AREA_TOOLTIP)
        self.__comet_parameters_window.get_tail_intensity_label().set_tooltip_text(
            strings.COMET_PARAMETERS_WINDOW_TAIL_INTENSITY_TOOLTIP)
        self.__comet_parameters_window.get_tail_length_label().set_tooltip_text(
            strings.COMET_PARAMETERS_WINDOW_TAIL_LENGTH_TOOLTIP)
        self.__comet_parameters_window.get_tail_dna_label().set_tooltip_text(
            strings.COMET_PARAMETERS_WINDOW_TAIL_DNA_TOOLTIP)
        self.__comet_parameters_window.get_tail_dna_percentage_label().set_tooltip_text(
            strings.COMET_PARAMETERS_WINDOW_TAIL_DNA_PERCENTAGE_TOOLTIP)
        self.__comet_parameters_window.get_tail_moment_label().set_tooltip_text(
            strings.COMET_PARAMETERS_WINDOW_TAIL_MOMENT_TOOLTIP)
        self.__comet_parameters_window.get_olive_moment_label().set_tooltip_text(
            strings.COMET_PARAMETERS_WINDOW_OLIVE_MOMENT_TOOLTIP)


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                  Dialogs                                    #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Run AddSamplesDialog. '''
    def run_add_new_samples_dialog(self):

        # Show dialog and wait for user response
        response_id = self.__dialog_add_new_samples.run()          
        # Hide dialog
        self.__dialog_add_new_samples.hide()
        # Return response ID and filenames
        return (response_id, self.__dialog_add_new_samples.get_filenames())

    ''' Run OpenProjectDialog. '''
    def run_open_project_dialog(self):

        # Show dialog and wait for user response
        response_id = self.__dialog_open_project.run()
        # Hide dialog
        self.__dialog_open_project.hide()
        # Return response ID and filename
        return (response_id, self.__dialog_open_project.get_filename())

    ''' Run SaveProjectAsDialog. '''
    def run_save_project_as_dialog(self, project_name):

        # Set name by default
        self.__dialog_save_project_as.set_current_name(project_name)
        # Show dialog and wait for user response
        response_id = self.__dialog_save_project_as.run()
        # Hide dialog
        self.__dialog_save_project_as.hide()
        # Return response ID and filename
        return (response_id, self.__dialog_save_project_as.get_filename())

    ''' Runs SaveBeforeActionDialog. '''
    def run_save_before_action_dialog(self, label):

        # Set label
        self.__dialog_save_before_action_label.set_label(label)
        # Show dialog and wait for user response
        response_id = self.__dialog_save_before_action.run()
        # Hide dialog
        self.__dialog_save_before_action.hide()
        # Return response ID
        return response_id

    ''' Runs AboutDialog. '''
    def run_about_dialog(self):

        # Show dialog
        self.__dialog_about.run()
        # Hide dialog
        self.__dialog_about.hide()

    ''' Runs GenerateOutputFileDialog. '''
    def run_generate_output_file_dialog(self, filename):

        # Set default name
        self.__dialog_generate_output_file.set_current_name(filename)
        # Show dialog and wait for user response
        response_id = self.__dialog_generate_output_file.run()
        # Hide dialog
        self.__dialog_generate_output_file.hide()
        # Return response ID and filename
        return (response_id, self.__dialog_generate_output_file.get_filename())

    ''' Runs ColorChooserDialog. '''
    def run_color_chooser_dialog(self, color_chooser_dialog):

        # Show dialog and wait for user response
        response_id = color_chooser_dialog.run()
        # Hide dialog
        color_chooser_dialog.hide()
        # Return response ID and filename
        return (response_id, color_chooser_dialog.get_rgba())


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                           Signals Callbacks                                 #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

    #                                              #
    # #     #     MainWindow callbacks     #     # #
    #                                              #

    ''' Main Window 'delete-event' signal callback. '''
    def __on_main_window_delete_event(self, window, event):
        self.__controller.exit_use_case()
        return True   

    ''' Main Window 'configure-event' callback. '''
    def __on_main_window_configure_event(self, viewport, event):
        if self.__controller.get_active_sample_id() is not None:
            self.__main_window.get_canvas().update()

    ''' MenuBar 'New' tab 'activate' signal callback. '''
    def __on_menubar_new_button_activated(self, menuitem):
        self.__controller.new_project_use_case() 

    ''' MenuBar 'Open' tab 'activate' signal callback. '''
    def __on_menubar_open_button_activated(self, menuitem):
        self.__controller.open_project_use_case()

    ''' MenuBar 'Save' tab 'activate' signal callback. '''
    def __on_menubar_save_button_activated(self, menuitem):
        self.__controller.save_project_use_case()

    ''' MenuBar 'Save as' tab 'activate' signal callback. '''
    def __on_menubar_save_as_button_activated(self, menuitem):
        self.__controller.save_project_as_use_case()

    ''' MenuBar 'Exit' tab 'activate' signal callback. '''
    def __on_menubar_exit_button_activated(self, menuitem):
        self.__controller.exit_use_case()

    ''' MenuBar 'Spanish' tab 'activate' signall callback. '''
    def __on_menubar_spanish_language_button_activated(self, radio_button):

        if radio_button.get_active():
            self.__controller.translate_app_to_spanish()

    ''' MenuBar 'English' tab 'activate' signall callback. '''
    def __on_menubar_english_language_button_activated(self, radio_button):

        if radio_button.get_active():
            self.__controller.translate_app_to_english()
      
    ''' MenuBar 'Clear' tab 'activate' signall callback. '''      
    def __on_menubar_theme_clear_button_activated(self, radio_button):
    
        if radio_button.get_active():
            self.__controller.set_application_clear_theme_use_case()
     
    ''' MenuBar 'Dark' tab 'activate' signall callback. '''     
    def __on_menubar_theme_dark_button_activated(self, radio_button):
    
        if radio_button.get_active():
            self.__controller.set_application_dark_theme_use_case()             

    ''' MenuBar 'About' tab 'activate' signal callback. '''
    def __on_menubar_about_button_activated(self, menuitem):
        self.__controller.about_use_case()

    ''' ToolBar 'New' Button 'clicked' signal callback. '''
    def __on_toolbar_new_button_clicked(self, toolbutton):
        self.__controller.new_project_use_case()

    ''' ToolBar 'Open' Button 'clicked' signal callback. '''
    def __on_toolbar_open_button_clicked(self, toolbutton):
        self.__controller.open_project_use_case()

    ''' ToolBar 'Save' Button 'clicked' signal callback. '''
    def __on_toolbar_save_button_clicked(self, toolbutton):
        self.__controller.save_project_use_case()

    ''' ToolBar 'Undo' Button 'clicked' signal callback. '''
    def __on_toolbar_undo_button_clicked(self, toolbutton):
        self.__controller.undo_use_case()

    ''' ToolBar 'Redo' Button 'clicked' signal callback. '''
    def __on_toolbar_redo_button_clicked(self, toolbutton):
        self.__controller.redo_use_case()

    ''' ToolBar 'Fullscreen' Button 'clicked' signal callback. '''
    def __on_toolbar_fullscreen_button_clicked(self, toolbutton):
        self.fullscreen(toolbutton)

    ''' SamplesView 'Add Samples' Button 'clicked' signal callback. '''
    def __on_samples_view_add_samples_button_clicked(self, button):
        self.__controller.add_new_samples_use_case()

    ''' SamplesView Treeview row 'row-activated' signal callback. '''
    def __on_samples_view_treeview_row_activated(self, treeview, path, columnw):
        sample_id = treeview.get_model()[path][0]
        self.__controller.activate_sample(sample_id)

    ''' SamplesView Treeview 'button-press-event' signal callback. '''
    def __on_samples_view_treeview_button_press_event(self, treeview, event):

        # Mouse Right Click -> open context menu
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:

            path = treeview.get_path_at_pos(int(event.x), int(event.y))
            # If a row has been right-clicked            
            if path is not None: 
                self.show_context_menu1(event)
            # If the background has been right-clicked
            else:
                self.show_context_menu2(event)

    ''' SamplesView Treeview row 'key-press-event' signal callback. '''
    def __on_samples_view_treeview_row_key_press_event(self, treeview, event):

        keyval_name = Gdk.keyval_name(event.keyval)
        # Supr -> delete selected row
        if len(treeview.get_model()) > 0 and keyval_name == "Delete":
            model, treeiter = treeview.get_selection().get_selected()
            if treeiter is not None:
                # Delete Sample by ID
                self.__controller.delete_sample_use_case(model[treeiter][0])

    ''' SamplesView Treeview row 'query-tooltip' signal callback. '''
    def __on_samples_view_treeview_row_query_tooltip(
                                self, treeview, x, y, keyboard_mode, tooltip):

        bin_x, bin_y = treeview.convert_widget_to_bin_window_coords(x, y)
        fullpath = treeview.get_path_at_pos(bin_x, bin_y)
        if fullpath is None:
            return False

        path, column, _, _ = fullpath
        # Row Sample's name is displayed in the tooltip
        tooltip.set_text(treeview.get_model()[path][1] )
        treeview.set_tooltip_cell(tooltip, path, column, None)
        
        return True

    ''' SamplesView Treeview row 'edited' signall callback. '''
    def __on_samples_view_treeview_row_edited(
                                        self, cell_renderer_text, path, text):

        # If name hasn't changed
        if self.__main_window.get_samples_view().get_sample_name(path) == text:      
            return True

        # Otherwise, rename
        sample_id = self.__main_window.get_samples_view().get_sample_id(path)
        self.__controller.rename_sample_use_case(sample_id, text)

    ''' SamplesView column label 'button-press-event' callback. '''
    def __on_samples_view_column_label_button_press_event(self, widget, event):
        self.__main_window.get_samples_view().sort_list()

    ''' SamplesView TreeView 'focus-out-event' callback. '''
    def __on_samples_view_focus_out_event(self, treeview, event):
        treeview.get_selection().unselect_all()
        return True

    ''' Canvas 'scroll-event' callback. '''
    def __on_canvas_scroll_event(self, viewport, event):

        if self.__controller.get_active_sample_id() is not None:
        
            # Handles zoom in / zoom out on Ctrl+mouse wheel
            accel_mask = Gtk.accelerator_get_default_mod_mask()
            if (event.state & accel_mask == Gdk.ModifierType.CONTROL_MASK):

                zoom_tool = self.__main_window.get_zoom_tool()
                direction = event.get_scroll_deltas()[2]           
                index = zoom_tool.get_active()
                # Scrolling down -> Zoom out
                if direction > 0 and index > 0:
                    self.zoom_out()
                # Scrolling up -> Zoom in
                elif direction < 0 and index < len(zoom_tool.get_model())-1:
                    self.zoom_in()

        # Update mouse coordinates
        self.__main_window.get_canvas().set_mouse_coordinates(
            (int(event.x), int(event.y)))

        
    def __on_viewport_size_allocate(self, viewport, allocation):
        if self.__controller.get_active_sample_id() is not None:
            self.__main_window.get_canvas().update()

    ''' Canvas 'enter-notify-event' callback. '''
    def __on_canvas_mouse_enter(self, drawing_area, event):
        if self.__controller.get_active_sample_id() is not None: 
            self.__main_window.get_canvas().on_mouse_enter()
        
    ''' Canvas 'leave-notify-event' callback. '''          
    def __on_canvas_mouse_leave(self, drawing_area, event):
        if self.__controller.get_active_sample_id() is not None:
            self.__main_window.get_canvas().on_mouse_leave()

    ''' Canvas 'motion-notify-event' callback. '''
    def __on_canvas_mouse_motion(self, drawing_area, event):

        if self.__controller.get_active_sample_id() is not None:           
            pixbuf = self.__view_store.get_store()[self.__controller.get_active_sample_id()].\
                get_displayed_pixbuf()       
            self.__main_window.get_canvas().on_mouse_motion(event, pixbuf)

    ''' Canvas 'button-press-event' callback. '''
    def __on_canvas_button_press_event(self, drawing_area, event):
        if self.__controller.get_active_sample_id() is not None:
            self.__main_window.get_canvas().on_mouse_click(event)

    ''' Canvas 'button-release-event' callback. '''
    def __on_canvas_button_release_event(self, drawing_area, event):    
        if self.__controller.get_active_sample_id() is not None: 
            self.__main_window.get_canvas().on_mouse_release(event)

    ''' Canvas 'draw' callback. '''
    def __on_canvas_draw(self, drawing_area, cairo_context):
        
        if self.__controller.get_active_sample_id() is not None:

            # Get displayed pixbuf
            pixbuf = self.__view_store.get_store()[self.__controller.get_active_sample_id()].\
                get_displayed_pixbuf()
            # Get comet view list
            comet_view_list = self.__view_store.\
                get_store()[self.__controller.get_active_sample_id()].get_comet_view_list()                
            # Draw
            self.__main_window.get_canvas().draw(
                cairo_context, pixbuf, comet_view_list)

    ''' Canvas Horizontal Scrollbar 'changed-value' callback. '''
    def __on_canvas_horizontal_scrollbar_value_changed(self, scrollbar):
    
        if self.__controller.get_active_sample_id() is not None:

            # Update sample 'scroll_x_position' parameter
            self.__view_store.get_store()[self.__controller.get_active_sample_id()].\
                set_scroll_x_position(scrollbar.get_value())
            # Update canvas      
            self.__main_window.get_canvas().update()
   
    ''' Canvas Vertical Scrollbar 'value-changed' callback. '''
    def __on_canvas_vertical_scrollbar_value_changed(self, scrollbar):

        if self.__controller.get_active_sample_id() is not None:

            # Update sample 'scroll_y_position' parameter
            self.__view_store.get_store()[self.__controller.get_active_sample_id()].\
                set_scroll_y_position(scrollbar.get_value())
            # Update canvas
            self.__main_window.get_canvas().update()

    ''' Canvas 'key-press-event' signal callback. '''
    def __on_canvas_key_press_event(self, drawing_area, event):
        self.__main_window.get_canvas().on_key_press_event(event)

    ''' 'Analyze' Treeview Context Menu1 tab 'activate' signal callback. '''
    def __on_context_menu1_analyze_sample(self, menu_item):

        samples_view = self.__main_window.get_samples_view()
        
        sample_id = samples_view.get_sample_id(
            samples_view.get_selected_sample_row())
        sample_name = samples_view.get_sample_name(
            samples_view.get_selected_sample_row())
        
        # Single sample analysis (do not show samples selection window)
        self.__analyze_samples_window.set_single_analysis_flag(True)
        # Set window title
        self.__analyze_samples_window.get_window().set_title(
            self.__controller.get_i18n().get_strings().ANALYZE_SAMPLES_SELECTION_WINDOW_TITLE.format(sample_name))
        # Set the samples IDs to analyze        
        self.__analyze_samples_window.set_sample_id_list([sample_id])

        # Set window page 1
        self.__analyze_samples_window.transition_to_parameters_window(
            self.__controller.get_algorithm_settings())

        # Show AnalyzeSamplesWindow window
        self.__analyze_samples_window.show() 
       
    ''' 'Rename' Treeview Context Menu1 tab 'activate' signal callback. '''
    def __on_context_menu1_rename(self, menu_item):
        self.__main_window.get_samples_view().prepare_row_for_rename()
        
    ''' 'Delete' Treeview Context Menu1 tab 'activate' signal callback. '''
    def __on_context_menu1_delete(self, menu_item):
    
        row = self.__main_window.get_samples_view().get_selected_sample_row()
        self.__controller.delete_sample_use_case(
            self.__main_window.get_samples_view().get_sample_id(row))

    ''' 'Add' Treeview Context Menu2 tab 'activate' signal callback. '''
    def __on_context_menu2_add(self, menu_item):
        self.__controller.add_new_samples_use_case() 

    ''' 'Flip' Canvas Context Menu tab 'activate' signal callback. '''
    def __on_canvas_context_menu_flip(self, menu_item):
        self.__controller.flip_sample_image_use_case(
            self.__controller.get_active_sample_id())

    ''' 'Invert' Canvas Context Menu tab 'activate' signal callback. '''
    def __on_canvas_context_menu_invert(self, menu_item):
        self.__controller.invert_sample_image_use_case(
            self.__controller.get_active_sample_id())

    ''' ZoomTool Combobox and Combobox Entry 'changed' callback. '''
    def __on_zoom_combobox_changed(self, combobox):

        if self.__controller.get_active_sample_id() is not None:

            zoom_tool = self.__main_window.get_zoom_tool()
            canvas = self.__main_window.get_canvas()
            sample_parameters = self.__view_store.get_store()[
                                    self.__controller.get_active_sample_id()]

            treeiter = combobox.get_active_iter()
            # The Combobox selection has changed 
            if treeiter is not None:

                # Combobox Entry unlimited length
                combobox.get_child().set_max_length(ZoomTool.UNLIMITED)

                # Scale image
                pixbuf = sample_parameters.get_original_pixbuf()
                scaled_pixbuf = zoom_tool.apply_zoom(
                    self.__controller.get_active_sample_id(), pixbuf)
                    
                # Scale Active Sample Comets    
                requested_scale_ratio = self.__main_window.get_zoom_tool()\
                                            .get_active_scale_ratio()
                self.__controller.scale_active_sample_comets(
                    requested_scale_ratio)

                # Update Active Sample Parameters
                current_scale_ratio = self.__controller.get_sample_zoom_value(
                                          self.__controller.get_active_sample_id())
                scale_ratio = requested_scale_ratio / current_scale_ratio
                sample_parameters.set_displayed_pixbuf(scaled_pixbuf)
                self.__controller.set_sample_zoom_index(
                    self.__controller.get_active_sample_id(), zoom_tool.get_active())
                x_pos = sample_parameters.get_scroll_x_position()
                y_pos = sample_parameters.get_scroll_y_position()
                sample_parameters.set_scroll_x_position(x_pos * scale_ratio)
                sample_parameters.set_scroll_y_position(y_pos * scale_ratio)

                # Update canvas
                self.__main_window.get_canvas().update()


            # The internal Gtk.Entry text has changed
            else:

                text = zoom_tool.validate_entry_text()
                combobox.get_child().set_text(text)

                # Set icon
                icon_name = ZoomTool.CLEAR_ICON
                if not text:
                    icon_name = ZoomTool.NO_ICON
                zoom_tool.set_entry_icon(icon_name)

    ''' ZoomTool Zoom-Out Button 'clicked' callback. '''
    def __on_zoom_out_button_clicked(self, button):
        self.zoom_out()

    ''' ZoomTool Zoom-In Button 'clicked' callback. '''
    def __on_zoom_in_button_clicked(self, button):
        self.zoom_in()

    ''' ZoomTool Entry 'activate' callback. '''
    def __on_zoom_tool_entry_activated(self, entry):
      
        # Entry is activated with empty text
        if not entry.get_text():
            return
            
        # Add zoom value to Model
        (zoom_value, index) = self.__controller.add_new_zoom_value_use_case(
            self.__controller.get_active_sample_id(), entry.get_text())
 
        # Add zoom value to ZoomTool
        self.__main_window.get_zoom_tool().add_new_zoom_value(
            zoom_value, index)
         
        # Make the active Sample SamplesView row grab the focus
        samples_view = self.__main_window.get_samples_view()
        row = samples_view.get_sample_row(self.__controller.get_active_sample_id())
        samples_view.focus_row(row)

    ''' ZoomTool Combobox Entry 'focus-in-event' callback. '''
    def __on_zoom_tool_entry_focus_in_event(self, entry, event):
    
        entry.set_text(entry.get_text()[:-1])
        zoom_tool = self.__main_window.get_zoom_tool() 
        entry.set_max_length(ZoomTool.MAX_LENGTH)
        zoom_tool.set_entry_icon(ZoomTool.CLEAR_ICON)

    ''' ZoomTool Combobox Entry 'focus-out-event' callback. '''
    def __on_zoom_tool_entry_focus_out_event(self, entry, event):
    
        zoom_tool = self.__main_window.get_zoom_tool()        
        entry.set_max_length(ZoomTool.UNLIMITED)
        zoom_tool.set_entry_icon(ZoomTool.NO_ICON)
        zoom_tool.set_active(self.__controller.get_sample_zoom_index(
            self.__controller.get_active_sample_id()))

    ''' ZoomTool Combobox Entry 'icon-press' callback. '''
    def __on_zoom_tool_entry_icon_press(self, entry, icon_pos, event):
    
        entry.set_text("")
        zoom_tool = self.__main_window.get_zoom_tool()
        zoom_tool.set_entry_icon(ZoomTool.NO_ICON)
        
    ''' Canvas 'Analyze' Button 'clicked' callback. '''
    def __on_canvas_analyze_button_clicked(self, button):
    
        model = self.__main_window.get_samples_view().get_model()
        self.__analyze_samples_window.get_samples_view().clear_model()
        self.__analyze_samples_window.get_samples_view().set_model(model)
        self.__analyze_samples_window.set_single_analysis_flag(False)
        self.__analyze_samples_window.show()

    ''' Canvas 'Analyze all' Button 'clicked' callback. '''
    def __on_canvas_analyze_all_button_clicked(self, button):
    
        model = self.__main_window.get_samples_view().get_model()
        samples_id_list = [sample[0] for sample in model]
        self.__controller.analyze_samples_use_case(samples_id_list)

    ''' Canvas 'Settings' Button 'clicked' callback. '''
    def __on_canvas_settings_button_clicked(self, button):

        self.__main_settings_window.show()

        algorithm_settings = None
        if self.__main_settings_window.get_ask_for_settings():
            algorithm_settings = self.__controller.get_algorithm_settings()
        
        self.__main_settings_window.show_components(
            algorithm_settings)

    ''' Canvas 'Generate output file' Button 'clicked' signal callback. '''
    def __on_canvas_generate_output_file_button_clicked(self, button):
        self.__controller.generate_output_file_use_case()

    ''' Canvas 'Selection Mode' Button 'clicked' callback. '''
    def __on_canvas_selection_button_clicked(self, button):
        if button.get_active():
            self.__controller.canvas_transition_to_selection_state()

    ''' Canvas 'Editing Mode' Button 'clicked' callback. '''
    def __on_canvas_editing_button_clicked(self, button):
        if button.get_active():         
            self.__controller.canvas_transition_to_editing_state()
            
    ''' Canvas 'Editing Selection' Button 'clicked' callback. '''
    def __on_canvas_editing_selection_button_clicked(self, button):
        if button.get_active():       
            self.__controller.canvas_transition_to_editing_selection_state()

    ''' Canvas 'Building' Button 'clicked' callback. '''
    def __on_canvas_editing_building_button_clicked(self, button):      
        if button.get_active():     
            self.__controller.canvas_transition_to_editing_building_state()

    ''' Canvas 'Build comet contour' Button 'clicked' callback. '''
    def __on_canvas_build_tail_contour_button_clicked(self, button):
        if button.get_active():       
            self.__controller.canvas_transition_to_building_tail_contour_state()
            
    ''' Canvas 'Build head contour' Button 'clicked' callback. '''
    def __on_canvas_build_head_contour_button_clicked(self, button):
        if button.get_active():           
            self.__controller.canvas_transition_to_building_head_contour_state()

    ''' Set the Canvas scrolls position. '''
    def __on_canvas_size_allocate(self, drawing_area, allocation):

        if self.__controller.get_active_sample_id() is not None:

            sample_parameters = self.__view_store.get_store()[
                                    self.__controller.get_active_sample_id()]

            # Set scrolls position
            self.__main_window.get_canvas().set_scroll_position(
                sample_parameters.get_scroll_x_position(),
                sample_parameters.get_scroll_y_position()
            )
    
        self.__main_window.get_canvas().update()

    ''' 
        Canvas 'Delete DelimiterPoint' context menu Button 'activate' 
        callback.
    '''
    def __on_canvas_delete_delimiter_point_button_activated(self, menu_item):
        self.__controller.delete_delimiter_points_use_case([])

    '''
        Canvas 'Add delimiter point.' context menu Button 'activate'
        callback. 
    '''
    def __on_canvas_add_delimiter_point_button_activated(self, menu_item):
        self.__controller.add_requested_delimiter_point()

    ''' Canvas 'Tail color' Button image 'size-allocate' callback. '''
    def __on_canvas_tail_color_button_image_size_allocated(self, image, allocation):

        self.__main_window.get_color_tool().set_tail_button_image_pixbuf(
            GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8,
                                 allocation.width, allocation.height))

    ''' Canvas 'Head color' Button image 'size-allocate' callback. '''
    def __on_canvas_head_color_button_image_size_allocated(self, image, allocation):

        self.__main_window.get_color_tool().set_head_button_image_pixbuf(
            GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8,
                                 allocation.width, allocation.height))

    ''' Canvas 'Comet color' Button 'clicked' callback. '''
    def __on_canvas_tail_color_button_clicked(self, button):

        # Run ColorChooserDialog
        (response_id, gdk_rgba) = self.run_color_chooser_dialog(
            self.__dialog_comet_color_chooser)

        if response_id == DialogResponse.ACCEPT:
            self.__main_window.get_color_tool().set_tail_color(gdk_rgba)

        return True            

    ''' Canvas 'Head color' Button 'clicked' callback. '''
    def __on_canvas_head_color_button_clicked(self, button):
        
        # Run ColorChooserDialog
        (response_id, gdk_rgba) = self.run_color_chooser_dialog(
            self.__dialog_head_color_chooser)

        if response_id == DialogResponse.ACCEPT:
            self.__main_window.get_color_tool().set_head_color(gdk_rgba)

        return True

    #                                                             #
    # #     #    AnalyzeSamplesLoadingWindow callbacks    #     # #
    #                                                             #

    ''' AnalyzeSamplesLoadingWindow 'Cancel' Button 'clicked' callback. '''
    def __on_analyze_samples_loading_window_cancel_button_clicked(self, button):
    
        button.set_sensitive(False)
        self.__analyze_samples_loading_window.set_cancelled(True)
        self.__controller.stop_analyze_samples_thread()

    #                                            #
    # #     #       SettingsWindow      #      # #
    #                                            #

    ''' SettingsWindow 'Algorithm' Combobox 'changed' callback. '''
    def __on_settings_window_algorithm_combobox_changed(
                                            self, combobox, settings_window):

        if combobox.get_active() == AlgorithmSettingsDto.FREECOMET:
            visibility = True
        elif combobox.get_active() == AlgorithmSettingsDto.OPENCOMET:
            visibility = False
                
        settings_window.set_components_visibility(visibility)

    #                                                      #
    # #     #     AnalyzeSamplesWindow callbacks   #     # #
    #                                                      #

    ''' AnalyzeSamplesWindow window 'delete-event' callback. '''
    def __on_analyze_samples_window_delete_event(self, window, event):
    
        self.__analyze_samples_window.get_samples_view().clear_model()
        self.__analyze_samples_window.hide()
        return True

    ''' AnalyzeSamplesView row 'toggled' callback. ''' 
    def __on_analyze_samples_view_row_toggled(self, cell_renderer, path):
        analyze_samples_view = self.__analyze_samples_window.get_samples_view()
        analyze_samples_view.toggle_row(path)

    ''' AnalyzeSamplesWindow page0 'Cancel' Button 'clicked' callback. '''
    def __on_analyze_samples_samples_selection_window_cancel_button_clicked(self, button):
        self.__analyze_samples_window.hide()
        return True  

    ''' AnalyzeSamplesWindow page0 'Next' Button 'clicked' callback. '''
    def __on_analyze_samples_samples_selection_window_next_button_clicked(self, button):

        # Set Sample id list
        sample_id_list = self.__analyze_samples_window.\
                          get_samples_view().get_requested_samples()       
        self.__analyze_samples_window.set_sample_id_list(sample_id_list)

        # Transition to SettingsWindow
        algorithm_settings = None
        if self.__analyze_samples_window.get_ask_for_settings():
            algorithm_settings = self.__controller.get_algorithm_settings()
        self.__analyze_samples_window.transition_to_parameters_window(
            algorithm_settings)

    ''' AnalyzeSamplesView toggle column 'clicked' callback. '''
    def __on_samples_column_toggle_clicked(self, checkbox):
        self.__analyze_samples_window.get_samples_view().toggle_all()

    ''' AnalyzeSamplesWindow page1 'Back' Button 'clicked' callback. '''
    def __on_analyze_samples_parameters_window_back_button_clicked(self, button):

        if self.__analyze_samples_window.get_single_analysis_flag():
            self.__analyze_samples_window.hide()
        else:
            self.__analyze_samples_window.transition_to_samples_selection_window()

    ''' AnalyzeSamplesWindow page1 'Execute' Button 'clicked' callback. '''
    def __on_analyze_samples_parameters_window_execute_button_clicked(self, button):

        # Analyze samples
        self.__controller.analyze_samples_use_case(
            self.__analyze_samples_window.get_sample_id_list(),
            self.__analyze_samples_window.get_algorithm_settings())
                      
        # Hide AnalyzeSamplesWindow
        self.__analyze_samples_window.hide() 
        

    #                                                        #
    # #     #      MainSettingsWindow callbacks      #     # #
    #                                                        #

    ''' MainSettingsWindow 'delete-event' callback. '''
    def __on_settings_window_delete_event(self, window, event):
        self.__main_settings_window.hide()
        return True

    ''' MainSettingsWindow 'Cancel' Button 'clicked' callback. '''
    def __on_settings_window_cancel_button_clicked(self, button):
        self.__main_settings_window.hide()
        return True

    ''' MainSettingsWindow 'Save' Button 'clicked' callback. '''
    def __on_settings_window_save_button_clicked(self, button):
    
        self.__controller.set_algorithm_settings(
            self.__main_settings_window.get_algorithm_settings())        
        self.__main_settings_window.hide()
        return True


    #                                                     #
    # #     #      SelectionWindow callbacks      #     # #
    #                                                     #

    ''' SelectionWindow 'delete comet' Button 'clicked' callback. '''
    def __on_delete_comet_button_clicked(self, button):   

        self.__controller.delete_comet_use_case(
            self.__controller.get_active_sample_id(),
            self.__controller.get_active_sample_selected_comet_id()
        )

    ''' SelectionWindow 'remove tail' Button 'clicked' callback. '''
    def __on_remove_tail_button_clicked(self, button):
    
        self.__controller.remove_comet_tail_use_case(
            self.__controller.get_active_sample_id(),
            self.__controller.get_active_sample_selected_comet_id()
        )

    ''' SelectionWindow 'Edit contour' Button 'clicked' callback. '''
    def __on_edit_comet_contours_button_clicked(self, button):

        self.__controller.edit_comet_contours_use_case(
            self.__controller.get_active_sample_id(),
            self.__controller.get_active_sample_selected_comet_id()
        )

    ''' SelectionWindow 'Cancel' Button 'clicked' callback. '''
    def __on_editing_comet_cancel_button_clicked(self, button):  
        self.__controller.cancel_edit_comet_contours_use_case()    

    ''' SelectionWindow 'See parameters' Button 'clicked' callback. '''
    def __on_see_parameters_button_clicked(self, button): 

        self.__controller.see_comet_parameters_use_case(
            self.__controller.get_active_sample_id(),
            self.__controller.get_active_sample_selected_comet_id()
        )

    ''' SelectionWindow 'Save' Button 'clicked' callback. '''
    def __on_editing_comet_save_button_clicked(self, button):
        self.__controller.save_comet_being_edited()


    #                                                           #
    # #     #      CometParametersWindow callbacks      #     # #
    #                                                           #

    ''' CometParametersWindow window 'delete-event' signall callback. '''
    def __on_comet_parameters_window_delete_event(self, window, event):
        window.hide()
        return True



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                  Methods                                    #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Start the GUI. '''
    def start(self):

        self.__main_window.show()
        self.__main_window.get_selection_window().hide()
        self.__main_window.get_samples_view().get_sorting_arrow_icon().\
            set_visible(False)   
        self.__controller.canvas_transition_to_selection_state()
        self.__main_window.get_canvas().hide_editing_buttons()
        self.__main_window.get_menubar().get_theme_clear_button().\
            set_active(True)
        
    ''' Restarts components parameters. '''
    def restart(self):
    
        self.__view_store.restart()
        self.__analyze_samples_window.restart()
        self.__main_settings_window.restart()
        self.__main_window.restart()
        self.__analyze_samples_loading_window.restart()

    ''' Observer.update() implementation method. '''
    def update(self, store):

        if len(store) == 0:
            self.on_empty_store()
        else:
            self.on_store_not_empty(self.__controller.get_active_sample_id())

        self.__set_info_label_text(len(store))
        
    ''' 'Delete sample' behaviour. '''
    def delete_sample(self, sample_id):

        # Retrieve sample parameters before removal
        parameters = self.__view_store.get_sample_parameters(sample_id)
        # Remove from the SamplesView
        pos = self.__main_window.get_samples_view().delete_sample(sample_id)
        # Delete from the ViewStore
        self.__view_store.remove(sample_id)
       
        # If the deleted sample was the 'active sample', the sample that takes 
        # its position in the list is activated   
        if ( (len(self.__view_store.get_store())) > 0 and
             (sample_id == self.__controller.get_active_sample_id()) ):
            self.__controller.activate_sample()
        # Return sample's parameters
        return (parameters, pos)

    ''' Builds the CometParametersWindow and shows it. ''' 
    def see_comet_parameters(self, sample_name, comet_number, 
                              comet_parameters):

        self.__comet_parameters_window.get_sample_name_label().set_label(
            sample_name)
        self.__comet_parameters_window.get_comet_number_value_label().set_label(
            str(comet_number))
        self.__comet_parameters_window.get_comet_area_value_label().set_label(
            str(comet_parameters.get_comet_area()))
        self.__comet_parameters_window.get_comet_intensity_value_label().set_label(
            str(comet_parameters.get_comet_average_intensity()))
        self.__comet_parameters_window.get_comet_length_value_label().set_label(
            str(comet_parameters.get_comet_length()))
        self.__comet_parameters_window.get_comet_dna_value_label().set_label(
            str(comet_parameters.get_comet_dna_content()))
        self.__comet_parameters_window.get_head_area_value_label().set_label(
            str(comet_parameters.get_head_area()))
        self.__comet_parameters_window.get_head_intensity_value_label().set_label(
            str(comet_parameters.get_head_average_intensity()))
        self.__comet_parameters_window.get_head_length_value_label().set_label(
            str(comet_parameters.get_head_length()))
        self.__comet_parameters_window.get_head_dna_value_label().set_label(
            str(comet_parameters.get_head_dna_content()))
        self.__comet_parameters_window.get_head_dna_percentage_value_label().set_label(
            str(comet_parameters.get_head_dna_percentage()*100))  
        self.__comet_parameters_window.get_tail_area_value_label().set_label(
            str(comet_parameters.get_tail_area()))
        self.__comet_parameters_window.get_tail_intensity_value_label().set_label(
            str(comet_parameters.get_tail_average_intensity()))
        self.__comet_parameters_window.get_tail_length_value_label().set_label(
            str(comet_parameters.get_tail_length()))
        self.__comet_parameters_window.get_tail_dna_value_label().set_label(
            str(comet_parameters.get_tail_dna_content()))
        self.__comet_parameters_window.get_tail_dna_percentage_value_label().set_label(
            str(comet_parameters.get_tail_dna_percentage()*100))
        self.__comet_parameters_window.get_tail_moment_value_label().set_label(
            str(comet_parameters.get_tail_moment()))
        self.__comet_parameters_window.get_olive_moment_value_label().set_label(
            str(comet_parameters.get_olive_moment()))
     
        self.__comet_parameters_window.show()

    ''' Sets Undo Button sensitivity. ''' 
    def set_undo_button_sensitivity(self, value):
        self.__main_window.get_toolbar().get_undo_button().set_sensitive(
                                                                 value)
    ''' Sets Redo Button sensitivity. '''
    def set_redo_button_sensitivity(self, value):
        self.__main_window.get_toolbar().get_redo_button().set_sensitive(
                                                                 value)
    ''' Zoom out the active sample image. '''
    def zoom_out(self):

        # Make the active Sample grab the focus
        samples_view = self.__main_window.get_samples_view()
        row = samples_view.get_sample_row(self.__controller.get_active_sample_id())
        samples_view.focus_row(row)
        # Zoom Out
        self.__main_window.get_zoom_tool().zoom_out()
        # Save current active sample 'zoom_index' parameter
        self.__controller.set_sample_zoom_index(self.__controller.get_active_sample_id(), 
            self.__main_window.get_zoom_tool().get_active())

    ''' Zoom in the active sample image. '''
    def zoom_in(self):

        # Make the active Sample grab the focus
        samples_view = self.__main_window.get_samples_view()
        row = samples_view.get_sample_row(self.__controller.get_active_sample_id())
        samples_view.focus_row(row)
        # Zoom In
        self.__main_window.get_zoom_tool().zoom_in()
        # Save current active sample 'zoom_index' parameter
        self.__controller.set_sample_zoom_index(self.__controller.get_active_sample_id(), 
            self.__main_window.get_zoom_tool().get_active())

    ''' Application window fullscreen mode. '''
    def fullscreen(self, fullscreen_button):

        # check if the state is the same as Gdk.WindowState.FULLSCREEN, which
        # is a bit flag
        is_fullscreen = self.__main_window.get_window().get_window().get_state(
        ) & Gdk.WindowState.FULLSCREEN != 0
        if not is_fullscreen:
            fullscreen_button.set_stock_id(Gtk.STOCK_LEAVE_FULLSCREEN)
            self.__main_window.fullscreen()
        else:
            fullscreen_button.set_stock_id(Gtk.STOCK_FULLSCREEN)
            self.__main_window.unfullscreen()

    ''' Sets the main application window title. '''
    def set_application_window_title(self, title):
        self.__main_window.set_title(title)

    ''' Pops up ContextMenu1. '''
    def show_context_menu1(self, event):
        self.__context_menu1.popup(
            None, None, None, None, event.button, event.time)

    ''' Pops up ContextMenu2. '''
    def show_context_menu2(self, event):
        self.__context_menu2.popup(
            None, None, None, None, event.button, event.time)

    ''' Pops up CanvasContextMenu. '''
    def show_canvas_context_menu(self, event):
        self.__canvas_context_menu.popup(
            None, None, None, None, event.button, event.time)

    ''' Runs LoadSamplesWindow. '''
    def run_load_samples_window(self):
        self.__load_samples_window.show()

    ''' Runs AnalyzeSamplesLoadingWindow. '''
    def run_analyze_samples_loading_window(self):
        self.__analyze_samples_loading_window.show()

    ''' Closes LoadSamplesWindow. '''
    def close_load_samples_window(self):
        self.__load_samples_window.hide()

    ''' Closes AnalyzeSamplesLoadingWindow. '''
    def close_analyze_samples_loading_window(self):
        self.__analyze_samples_loading_window.hide()

    ''' 
        Threading Synchronous method to update the configuration of
        LoadSamplesWindow.
    '''
    def update_load_samples_window(self, bottom_label, top_label, n, n_total):

        self.__load_samples_window.get_top_label().set_label(top_label)
        self.__load_samples_window.get_bottom_label().set_label(bottom_label)
        self.__load_samples_window.get_progress_bar().set_fraction(n/n_total)

    ''' 
        Threading Synchronous method to update the configuration of
        AnalyzeSamplesLoadingWindow.
    '''
    def update_analyze_samples_loading_window(
                                    self, top_label, bottom_label):

        self.__analyze_samples_loading_window.get_top_label().set_label(
            top_label)            
        self.__analyze_samples_loading_window.get_bottom_label().set_label(
            bottom_label)

    ''' Behaviour when the ViewStore goes empty. '''
    def on_empty_store(self):

        # Disable widgets that need samples to be available for
        self.__switch_off_tools()

    ''' Behaviour when the ViewStore goes from empty to no longer empty. '''
    def on_store_not_empty(self, sample_id=None):

        # Sample in first row is activated
        if sample_id is None:
            self.__switch_on_tools()
            self.__controller.activate_sample(
                self.__main_window.get_samples_view().get_sample_id(0))

        elif sample_id != self.__controller.get_active_sample_id():
            self.__controller.activate_sample(sample_id)

    ''' On sample activated behaviour. '''
    def on_sample_activated(self, sample_id):

        samples_view = self.__main_window.get_samples_view()
        # Focus the active Sample's row on the SamplesView TreeView
        samples_view.focus_row(samples_view.get_sample_row(sample_id))
        # Update components configuration with active Sample parameters 
        self.__update_components_parameters()

    ''' Returns the active sample's comet view list. '''
    def get_active_sample_comet_view_list(self):

        if self.__controller.get_active_sample_id() is not None:
            return self.__view_store.get_store()[self.__controller.get_active_sample_id()].\
                get_comet_view_list()

    ''' Returns the active sample's comet number. '''
    def get_active_sample_comet_number(self, comet_id):

        if self.__controller.get_active_sample_id() is not None:
            return self.__view_store.get_comet_number(
                self.__controller.get_active_sample_id(), comet_id)
            
    ''' Updates Undo and Redo Buttons tooltips. '''        
    def update_undo_and_redo_buttons_tooltips(self):  

        self.__main_window.get_toolbar().get_undo_button().set_tooltip_text(
            self.__controller.get_undo_button_tooltip())
        self.__main_window.get_toolbar().get_redo_button().set_tooltip_text(
            self.__controller.get_redo_button_tooltip())

    ''' Sets the info label text. '''
    def __set_info_label_text(self, n_samples):

        if self.__controller is not None:

            if n_samples == 0:
                self.__main_window.set_info_label_text(
                    self.__controller.get_i18n().get_strings().INFO_LABEL_ON_EMPTY_STORE)

            else:
                self.__main_window.set_info_label_text(self.__controller.\
                    get_i18n().get_strings().INFO_LABEL_ON_NOT_EMPTY_STORE.format(
                        n_samples))

    ''' Updates the components with active sample's parameters '''
    def __update_components_parameters(self):
  
        sample_parameters = self.__view_store.\
                                get_store()[self.__controller.get_active_sample_id()]

        # # # # # ZoomTool
        self.__main_window.get_zoom_tool().update(
            self.__controller.get_active_sample_id())

        # # # # # Canvas
        canvas = self.__main_window.get_canvas() 
        #canvas.reset_parameters()
       
        # Set scrolls position (only if available space)
        if (sample_parameters.get_scroll_x_position() <=         
            canvas.get_scrolledwindow().get_hadjustment().get_upper() and
            sample_parameters.get_scroll_y_position() <= 
            canvas.get_scrolledwindow().get_vadjustment().get_upper()):

            canvas.set_scroll_position(sample_parameters.get_scroll_x_position(),
                                       sample_parameters.get_scroll_y_position())

        # Set label text
        row = self.__main_window.get_samples_view().get_sample_row(
            self.__controller.get_active_sample_id())
        sample_name = self.__main_window.get_samples_view().get_sample_name(
            row)
        canvas.get_label().set_label(sample_name)
        self.__main_window.get_canvas().update()

        # # # # # SelectionWindow
        self.__main_window.get_selection_window().update()

    ''' Activate tools. '''
    def __switch_on_tools(self):

        # Activate Canvas
        self.__main_window.get_canvas().switch_on()
        # Activate Zoom Tool
        self.__main_window.get_zoom_tool().switch_on()      
        # Activate SelectionWindow
        self.__main_window.get_selection_window().switch_on()

    ''' Deactivate tools. '''
    def __switch_off_tools(self):
    
        # Deactivate Canvas
        self.__main_window.get_canvas().switch_off()
        # Deactivate ZoomTool
        self.__main_window.get_zoom_tool().switch_off()
        # Deactivate SelectionWindow
        self.__main_window.get_selection_window().switch_off()      
           
    
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_controller(self):
        return self.__controller

    def set_controller(self, controller):
        self.__controller = controller

    def get_main_window(self):
        return self.__main_window

    def set_main_window(self, main_window):
        self.__main_window = main_window

    def get_load_samples_window(self):
        return self.__load_samples_window

    def set_load_samples_window(self, load_samples_window):
        self.__load_samples_window = load_samples_window

    def get_analyze_samples_loading_window(self):
        return self.__analyze_samples_loading_window

    def set_analyze_samples_loading_window(self, analyze_samples_loading_window):
        self.__analyze_samples_loading_window = analyze_samples_loading_window

    def get_main_settings_window(self):
        return self.__main_settings_window

    def set_main_settings_window(self, main_settings_window):
        self.__main_settings_window = main_settings_window

    def get_view_store(self):
        return self.__view_store

    def set_view_store(self, view_store):
        self.__view_store = view_store



