# -*- encoding: utf-8 -*-

'''
    The strings module.
'''

import gettext

es_lang = gettext.translation('base', localedir='locales', languages=['es'])
en_lang = gettext.translation('base', localedir='locales', languages=['en'])


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	Strings                                                                   #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class Strings(object):

    '''
        The Strings class.
    '''

    ''' Translates with given translator. '''
    def translate(self, _):

        self.DEFAULT_PROJECT_NAME = _("Sin titulo")

        # MenuBar
        self.MENUBAR_FILE_BUTTON_LABEL = _("Archivo")
        self.MENUBAR_PREFERENCES_BUTTON_LABEL = _("Preferencias")
        self.MENUBAR_HELP_BUTTON_LABEL = _("Ayuda")
        self.FILE_MENU_NEW_PROJECT_BUTTON_LABEL = _("Nuevo")
        self.FILE_MENU_OPEN_PROJECT_BUTTON_LABEL = _("Abrir")
        self.FILE_MENU_SAVE_PROJECT_BUTTON_LABEL = _("Guardar")
        self.FILE_MENU_SAVE_PROJECT_AS_BUTTON_LABEL = _("Guardar como")
        self.FILE_MENU_EXIT_BUTTON_LABEL = _("Salir")
        self.PREFERENCES_MENU_LANGUAGE_BUTTON_LABEL = _("Idioma")
        self.PREFERENCES_MENU_LANGUAGE_SPANISH_LANGUAGE_BUTTON_LABEL = _("Español")
        self.PREFERENCES_MENU_LANGUAGE_ENGLISH_LANGUAGE_BUTTON_LABEL = _("Inglés")
        self.HELP_MENU_ABOUT_BUTTON_LABEL = _("Acerca de")

        # ToolBar
        self.CREATE_NEW_PROJECT_TOOLBAR_BUTTON_LABEL = _("Nuevo")
        self.CREATE_NEW_PROJECT_TOOLBAR_BUTTON_TOOLTIP = _("Crear un proyecto nuevo (Ctrl+N)")
        self.SAVE_PROJECT_TOOLBAR_BUTTON_LABEL = _("Guardar")
        self.SAVE_PROJECT_TOOLBAR_BUTTON_TOOLTIP = _("Guardar proyecto (Ctrl+S)")
        self.OPEN_PROJECT_TOOLBAR_BUTTON_LABEL = _("Abrir")
        self.OPEN_PROJECT_TOOLBAR_BUTTON_TOOLTIP = _("Abrir un proyecto existente (Ctrl+O)")
        self.UNDO_TOOLBAR_BUTTON_LABEL = _("Deshacer")
        self.UNDO_TOOLBAR_BUTTON_TOOLTIP = _("Deshacer {} (Ctrl+Z)")
        self.REDO_TOOLBAR_BUTTON_LABEL = _("Rehacer")
        self.REDO_TOOLBAR_BUTTON_TOOLTIP = _("Rehacer {} (Ctrl+Y)")
        self.FULLSCREEN_TOOLBAR_BUTTON_LABEL = _("Pantalla completa")
        self.FULLSCREEN_TOOLBAR_BUTTON_TOOLTIP = _("Modo pantalla completa (F12)")

        # SamplesView   
        self.SAMPLES_VIEW_COLUMN_LABEL = _("Muestras")     
        self.ADD_SAMPLES_BUTTON_TOOLTIP = _("Añadir muestras (Ctrl+A)")
        self.SAMPLES_VIEW_CONTEXT_MENU_ADD_BUTTON_LABEL = _("Añadir...")

        # Canvas
        self.ANALYZE_SAMPLES_BUTTON_TOOLTIP = _("Analizar muestras... (Ctrl+R)")
        self.QUICK_ANALYZE_BUTTON_TOOLTIP = _("Análisis rápido (Shift+Ctrl+R)")
        self.PARAMETERS_BUTTON_TOOLTIP = _("Parámetros... (Ctrl+P)")
        self.GENERATE_EXCEL_FILE_BUTTON_TOOLTIP = _("Generar archivo excel... (Ctrl+E)")
        self.SELECTION_MODE_BUTTON_TOOLTIP = _("Modo selección")
        self.EDITING_MODE_BUTTON_TOOLTIP = _("Modo edición")
        self.EDITING_SELECTION_MODE_BUTTON_TOOLTIP = _("Editar contornos")
        self.EDITING_BUILDING_MODE_BUTTON_TOOLTIP = _("Construir contornos")
        self.BUILDING_TAIL_CONTOUR_MODE_BUTTON_TOOLTIP = _("Contorno del cometa")
        self.BUILDING_HEAD_CONTOUR_MODE_BUTTON_TOOLTIP = _("Contorno de la cabeza")
        self.ADD_DELIMITER_POINT_BUTTON_LABEL = _("Añadir punto")
        self.DELETE_DELIMITER_POINTS_BUTTON_LABEL = _("Eliminar punto/s")

        # ZoomTool
        self.ZOOM_COMBOBOX_ICON_TOOLTIP = _("Vaciar")
        self.ZOOM_COMBOBOX_TOOLTIP = _("Ampliación")
        self.ZOOM_IN_BUTTON_LABEL = _("Ampliar")
        self.ZOOM_IN_BUTTON_TOOLTIP = _("Ampliar imagen")
        self.ZOOM_OUT_BUTTON_LABEL = _("Reducir")
        self.ZOOM_OUT_BUTTON_TOOLTIP = _("Reducir imagen")

        # AnalyzeSamplesWindow
        self.SAMPLE_LABEL = _("Muestra")
        self.ALGORITHM_LABEL = _("Algoritmo de segmentación:")
        self.FIT_TAIL_LABEL = _("Contorno de la cola elíptico:")
        self.FIT_HEAD_LABEL = _("Contorno de la cabeza elíptico:")
        self.TAIL_CONTOUR_COLOR_LABEL = _("Color del perímetro del cometa")
        self.HEAD_CONTOUR_COLOR_LABEL = _("Color del perímetro de la cabeza")
        self.ANALYZING_SAMPLES_WINDOW_LABEL = _("Analizando muestra {}/{}")
        self.ANALYZE_SAMPLES_SELECTION_WINDOW_TITLE = _("Análisis de {}")
        self.ANALYZE_SAMPLES_WINDOW_TITLE = _("Analizar muestras")
        
        # Info labels
        self.INFO_LABEL_ON_EMPTY_STORE = _("Añade tus muestras para comenzar!")
        self.INFO_LABEL_ON_NOT_EMPTY_STORE = _("{} imágenes cargadas.")
        
        # LoadSamplesWindow
        self.LOAD_SAMPLES_WINDOW_LABEL = _("Cargando muestra {}/{} ...")

        # SettingsWindow
        self.SETTINGS_WINDOW_TITLE = _("Configuración")
        
        # SelectionWindow
        self.SELECTION_WINDOW_TITLE = _("Ventana de selección")      
        self.SELECTION_WINDOW_SELECTION_LABEL = _("Cometa nº {}") 
        self.SELECTION_WINDOW_COMET_BEING_EDITED_LABEL = \
            _("La edición del cometa nº {} está en curso.\n" +
              "Seleccione una de las acciones de abajo para terminar.")
        self.SELECTION_WINDOW_DELETE_COMET_BUTTON_LABEL = _("Eliminar cometa")
        self.SELECTION_WINDOW_REMOVE_TAIL_BUTTON_LABEL = _("Eliminar cola")
        self.SELECTION_WINDOW_EDIT_CONTOUR_BUTTON_LABEL = _("Editar contorno")
        self.SELECTION_WINDOW_SEE_PARAMETERS_BUTTON_LABEL = _("Ver parámetros")

        # CometParametersWindow
        self.COMET_PARAMETERS_WINDOW_TITLE = _("Parámetros")
        self.COMET_PARAMETERS_WINDOW_COMET_NUMBER_TOOLTIP = _(
            "Número del cometa")
        self.COMET_PARAMETERS_WINDOW_COMET_AREA_TOOLTIP = _(
            "Área del cometa")
        self.COMET_PARAMETERS_WINDOW_COMET_INTENSITY_TOOLTIP = _(
            "Valor de intensidad promedio de los píxeles dentro del cometa")
        self.COMET_PARAMETERS_WINDOW_COMET_LENGTH_TOOLTIP = _(
            "Longitud del cometa")
        self.COMET_PARAMETERS_WINDOW_COMET_DNA_TOOLTIP = _(
            "Suma de los valores de intensidad de los píxeles dentro del cometa")
        self.COMET_PARAMETERS_WINDOW_HEAD_AREA_TOOLTIP = _(
            "Área de la cabeza")
        self.COMET_PARAMETERS_WINDOW_HEAD_INTENSITY_TOOLTIP = _(
            "Valor de intensidad promedio de los píxeles dentro de la cabeza")
        self.COMET_PARAMETERS_WINDOW_HEAD_LENGTH_TOOLTIP = _(
            "Longitud de la cabeza")
        self.COMET_PARAMETERS_WINDOW_HEAD_DNA_TOOLTIP = _(
            "Suma de los valores de intensidad de los píxeles dentro de la cabeza")
        self.COMET_PARAMETERS_WINDOW_HEAD_DNA_PERCENTAGE_TOOLTIP = _(
            "Porcentaje de DNA del cometa perteneciente a la cabeza")
        self.COMET_PARAMETERS_WINDOW_TAIL_AREA_TOOLTIP = _(
            "Área de la cola")
        self.COMET_PARAMETERS_WINDOW_TAIL_INTENSITY_TOOLTIP = _(
            "Valor de intensidad promedio de los píxeles dentro de la cola")
        self.COMET_PARAMETERS_WINDOW_TAIL_LENGTH_TOOLTIP = _(
            "Longitud de la cola")
        self.COMET_PARAMETERS_WINDOW_TAIL_DNA_TOOLTIP = _(
            "Suma de los valores de intensidad de los píxeles dentro de la cola")
        self.COMET_PARAMETERS_WINDOW_TAIL_DNA_PERCENTAGE_TOOLTIP = _(
            "Porcentaje de DNA del cometa perteneciente a la cola")
        self.COMET_PARAMETERS_WINDOW_TAIL_MOMENT_TOOLTIP = _(
            "Momento de torsión de la cola")
        self.COMET_PARAMETERS_WINDOW_OLIVE_MOMENT_TOOLTIP = _(
            "Momento de torsión de Olive de la cola")
        
        # Misc
        self.SAVE_BUTTON_LABEL = _("Guardar")
        self.CANCEL_BUTTON_LABEL = _("Cancelar")
        self.DISCARD_BUTTON_LABEL = _("Descartar")
        self.NEXT_BUTTON_LABEL = _("Siguiente")
        self.BACK_BUTTON_LABEL = _("Atrás")
        self.ADD_BUTTON_LABEL = _("Añadir")
        self.OPEN_BUTTON_LABEL = _("Abrir")
        self.EXECUTE_BUTTON_LABEL = _("Ejecutar")
        self.ANALYZE_BUTTON_LABEL = _("Analizar")
        self.RENAME_BUTTON_LABEL = _("Cambiar nombre")
        self.DELETE_BUTTON_LABEL = _("Eliminar")
        self.FLIP_BUTTON_LABEL = _("Voltear horizontalmente")
        self.INVERT_BUTTON_LABEL = _("Invertir color")
        self.LAST_ACTION_LABEL = _("última acción")
        
        # Dialogs
        self.DIALOG_SAVE_BEFORE_ACTION_LABEL = _(
            "Hay cambios en {} sin guardar.\n¿Desea guardar antes de continuar?")
        self.DIALOG_ABOUT_COMMENTS = _(
            "Originalmente creada como un Trabajo de Fin de Grado, FreeComet es una aplicación gratuita y de código abierto para trabajar con imágenes del ensayo del cometa.")
        self.DIALOG_OPEN_PROJECT_TITLE = _("Abrir proyecto")
        self.DIALOG_ADD_SAMPLES_TITLE = _("Añadir muestras")
        self.DIALOG_SAVE_PROJECT_AS_TITLE = _("Guardar proyecto")
        self.DIALOG_SAVE_BEFORE_ACTION_TITLE = _("Advertencia - FreeComet")
        
        # Commands
        self.ADD_SAMPLES_COMMAND_STRING = _("'Añadir Imágenes'")
        self.DELETE_SAMPLE_COMMAND_STRING = _("'Eliminar Imagen'")
        self.RENAME_SAMPLE_COMMAND_STRING = _("'Renombrar Imagen'")
        self.ADD_COMET_COMMAND_STRING = _("'Añadir Cometa'")
        self.DELETE_COMET_COMMAND_STRING = _("'Eliminar Cometa'")
        self.REMOVE_COMET_TAIL_COMMAND_STRING = _("'Eliminar Cola de Cometa'")
        self.ANALYZE_SAMPLES_COMMAND_STRING = _("'Analizar Imágenes'")
        self.FLIP_SAMPLE_IMAGE_COMMAND_STRING = _("'Voltear Imagen'")
        self.INVERT_SAMPLE_IMAGE_COMMAND_STRING = _("'Invertir Imagen'")
        self.EDIT_COMET_CONTOURS_COMMAND_STRING = _("'Comenzar Edición de Cometa'")
        self.CANCEL_EDIT_COMET_CONTOURS_COMMAND_STRING = _("'Cancelar Edición de Cometa'")
        self.UPDATE_COMET_CONTOURS_COMMAND_STRING = _("'Finalizar Edición de Cometa'")
        self.MOVE_DELIMITER_POINTS_COMMAND_STRING = _("'Mover Punto/s Delimitador/es'")
        

    ''' Translates the strings to spanish. '''
    def translate_to_spanish(self):
        self.translate(es_lang.gettext)

    ''' Translates the strings to english. '''
    def translate_to_english(self):
        self.translate(en_lang.gettext)


        


