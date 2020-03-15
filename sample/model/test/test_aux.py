# -*- encoding: utf-8 -*-

'''
    Auxiliar module to fill manually segmented contours.
'''

# General imports
import numpy
import cv2
import os

# Custom imports
import image_processing_facade as utils
import constants

# Module constants
INPUT_IMAGES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "data/test_image_contours/comets")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "data/output/temp_output")

''' Fills the passed images contours with color. '''
def run_test_image_filler():

    input_images = os.listdir(INPUT_IMAGES_PATH)

    for image_name in input_images:

        input_image_path = os.path.join(INPUT_IMAGES_PATH, image_name)
        _, original_image = utils.read_image(
            input_image_path, True)
        contours_red_mask = utils.get_red_from_image(
            original_image)
        contours_binary_mask = utils.to_binary(
            utils.to_gray_image(contours_red_mask), 1)

        binary_mask = numpy.zeros(shape=(contours_binary_mask.shape))
        for contour in utils.find_contours(contours_binary_mask):
            utils.draw_contours(binary_mask, [contour])

        filled_image = numpy.copy(original_image)
        coordinates = numpy.where(binary_mask != 0)
        filled_image[coordinates] = constants.RED
        
        path = os.path.join(OUTPUT_PATH, image_name)
        utils.save_image(filled_image, path)


if __name__ == "__main__":

    run_test_image_filler()

