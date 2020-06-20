# -*- encoding: utf-8 -*-

'''
    The singleton module.
'''


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	Singleton                                                                 #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class Singleton(type):

    '''
        The Singleton metaclass.
    '''

    __instances = {}

    ''' 
        Executed when the constructor of a class that implements Singleton is
        called.
    '''
    def __call__(cls, *args, **kwargs):
    
        if cls not in cls.__instances:
            cls.__instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            cls.__instances[cls].__init__(*args, **kwargs)

        return cls.__instances[cls]

    ''' Returns the instantiated objet of the given class or None. '''
    def get_instance(cls):

        # Not instantiated
        if cls not in cls.__instances:
            return None

        return cls.__instances[cls]
