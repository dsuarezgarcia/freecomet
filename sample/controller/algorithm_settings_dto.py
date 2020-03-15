# -*- encoding: utf-8 -*-

'''
    The algorithm_settings_dto module.
'''

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	AlgorithmSettingsDto                                                      #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class AlgorithmSettingsDto(object):

    '''
        The AlgorithmSettingsDto class.
    '''
    
    FREECOMET = 0
    OPENCOMET = 1

    ''' Iitialization method. '''
    def __init__(self, id, fit_tail, fit_head):
        
        self.__algorithm_id = id
        self.__fit_tail = fit_tail
        self.__fit_head = fit_head


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                            Getters & Setters                                #
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

