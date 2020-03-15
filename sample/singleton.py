# -*- encoding: utf-8 -*-

'''
    The Singleton module.
'''

class Singleton(type):

    '''
        The Singleton class.
    '''

    __instances = {}

    def __call__(cls, *args, **kwargs):
    
        if cls not in cls.__instances:
            cls.__instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            cls.__instances[cls].__init__(*args, **kwargs)

        return cls.__instances[cls]

    def get_instance(cls):

        # Not instantiated
        if cls not in cls.__instances:
            return None

        return cls.__instances[cls]
