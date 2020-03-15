# -*- encoding: utf-8 -*-

'''
    The Model constants module.
'''


import os


# Paths
TEST_PATH =  os.path.join(os.path.dirname(os.path.abspath(__file__)), "model/test/")
TEST_IMAGES_FOLDER_PATH = os.path.join(TEST_PATH, "images/")
DEBUG_PATH = os.path.join(TEST_PATH, "debug/")
ALGORITHM_DEBUG_PATH = os.path.join(DEBUG_PATH, "algorithm/")
SCORE_DEBUG_PATH =  os.path.join(DEBUG_PATH, "score/")

# Intensity levels
LEVELS = 256
MAX_VALUE = LEVELS - 1

# BGR Values
WHITE = (MAX_VALUE, MAX_VALUE, MAX_VALUE)
YELLOW = (0, MAX_VALUE, MAX_VALUE)
BLUE = (MAX_VALUE, 0, 0)
GREEN = (0, MAX_VALUE, 0)
RED = (0, 0, MAX_VALUE)
BLACK = (0, 0, 0)
