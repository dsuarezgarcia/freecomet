# -*- encoding: utf-8 -*-

'''
    The menubar module.
'''

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	MenuBar                                                                   #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class MenuBar(object):

    '''
        The MenuBar class. The application's menubar.
    '''

    ''' Initialization method. '''
    def __init__(self, gtk_builder):

        # File tab
        self.__menu_file = gtk_builder.get_object("menubar-file")
        self.__new_button = gtk_builder.get_object("menubar-new")
        self.__open_button = gtk_builder.get_object("menubar-open")
        self.__save_button = gtk_builder.get_object("menubar-save")
        self.__save_as_button = gtk_builder.get_object("menubar-save-as")
        self.__exit_button = gtk_builder.get_object("menubar-exit")

        # Preferences tab
        self.__menu_preferences = gtk_builder.get_object(
            "menubar-preferences")
        self.__menu_language = gtk_builder.get_object(
            "menubar-preferences-language")
        self.__spanish_language_button = gtk_builder.get_object(
            "spanish-language")
        self.__english_language_button = gtk_builder.get_object(
            "english-language")

        self.__spanish_language_button.set_active(True)

        # Help tab
        self.__menu_help = gtk_builder.get_object("menubar-help")
        self.__about_button = gtk_builder.get_object("menubar-about")


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

    def get_menu_file(self):
        return self.__menu_file

    def set_menu_file(self, menu_file):
        self.__menu_file = menu_file

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

    def get_save_as_button(self):
        return self.__save_as_button

    def set_save_as_button(self, save_as_button):
        self.__save_as_button = save_as_button

    def get_exit_button(self):
        return self.__exit_button

    def set_exit_button(self, exit_button):
        self.__exit_button = exit_button

    def get_menu_preferences(self):
        return self.__menu_preferences

    def set_menu_preferences(self, menu_preferences):
        self.__menu_preferences = menu_preferences

    def get_menu_language(self):
        return self.__menu_language

    def set_menu_language(self, menu_language):
        self.__menu_language = menu_language

    def get_spanish_language_button(self):
        return self.__spanish_language_button

    def set_spanish_language_button(self, spanish_language_button):
        self.__spanish_language_button = spanish_language_button

    def get_english_language_button(self):
        return self.__english_language_button

    def set_english_language_button(self, english_language_button):
        self.__english_language_button = english_language_button

    def get_menu_help(self):
        return self.__menu_help

    def set_menu_help(self, menu_help):
        self.__menu_help = menu_help

    def get_about_button(self):
        return self.__about_button

    def set_about_button(self, about_button):
        self.__about_button = about_button

