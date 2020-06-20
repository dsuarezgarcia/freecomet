# -*- encoding: utf-8 -*-

'''
    The observer module.
'''


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	Observer                                                                  #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class Observer(object):

    '''
        The Observer abstract class.
    '''

    ''' Update method. '''
    def update(self, *args):
        raise NotImplementedError("Method must be implemented.")



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	Observable                                                                #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class Observable(object):

    '''
        The Observable abstract class.
    '''

    ''' Initialization method. '''
    def __init__(self, observable_state):

        self.__observers = set()
        self.__observable_state = observable_state

    ''' Registers a new observer. '''
    def register(self, observer):
    
        self.__observers.add(observer)
        observer.update(self.__observable_state)

    ''' Unregisters given observer. '''
    def unregister(self, observer):
        self.__observers.discard(observer)

    ''' Notifies all observers the state has changed. '''
    def notify(self):

        for observer in self.__observers:
            observer.update(self.__observable_state)


        

