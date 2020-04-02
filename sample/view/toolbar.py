# -*- encoding: utf-8 -*-

'''
    The toolbar module.
'''

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	ToolBar                                                                   #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class ToolBar(object):

    '''
        The ToolBar class. The application's toolbar.
    '''

    ''' Initialization method. '''
    def __init__(self, gtk_builder):

        self.__new_button = gtk_builder.get_object("toolbar-new")
        self.__open_button = gtk_builder.get_object("toolbar-open")
        self.__save_button = gtk_builder.get_object("toolbar-save")
        self.__undo_button = gtk_builder.get_object("toolbar-undo")
        self.__redo_button = gtk_builder.get_object("toolbar-redo")
        self.__fullscreen_button = gtk_builder.get_object("toolbar-fullscreen")

        self.__undo_button.set_sensitive(False)
        self.__redo_button.set_sensitive(False)


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

    def get_new_button(self):
        return self.__new_button

    def set_new_button(self, new_button):
        self.__new_button = new_button

    def get_open_button(self):
        return self.__open_button

    def set_open_button(self, open_button):
        self.__open_button = open_button

    def get_save_button(self):
        return self.__save_button

    def set_save_button(self, save_button):
        self.__save_button = save_button

    def get_undo_button(self):
        return self.__undo_button

    def set_undo_button(self, undo_button):
        self.__undo_button = undo_button

    def get_redo_button(self):
        return self.__redo_button

    def set_redo_button(self, redo_button):
        self.__redo_button = redo_button

    def get_fullscreen_button(self):
        return self.__fullscreen_button

    def set_fullscreen_button(self, fullscreen_button):
        self.__fullscreen_button = fullscreen_button

