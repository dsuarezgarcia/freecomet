# -*- encoding: utf-8 -*-

'''
    The algorithm_settings module.
'''

# Custom imports
from sample.singleton import Singleton



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	AlgorithmSettings                                                         #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class AlgorithmSettings(metaclass=Singleton):

    '''
        The AlgorithmSettings class. Extends from Singleton.
    '''

    FREECOMET = 0
    OPENCOMET = 1

    ''' Iitialization method. '''
    def __init__(self):
        
        self.__algorithm_id = AlgorithmSettings.FREECOMET
        self.__fit_tail = False
        self.__fit_head = False


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_algorithm_id(self):
        return self.__algorithm_id

    def set_algorithm_id(self, algorithm_id):
        self.__algorithm_id = algorithm_id

    def get_fit_tail(self):
        return self.__fit_tail

    def set_fit_tail(self, fit_tail):
        self.__fit_tail = fit_tail

    def get_fit_head(self):
        return self.__fit_head

    def set_fit_head(self, fit_head):
        self.__fit_head = fit_head
        
        