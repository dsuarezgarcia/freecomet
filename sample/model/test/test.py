# -*- encoding: utf-8 -*-

'''
    The test module. Uses IOU metric.
'''


import os
import sys
import cv2
import numpy
import shutil
import matplotlib.pyplot as plt

import model.algorithms
import constants
import model.utils
import model.model
from model import Sample

numpy.seterr(divide='ignore', invalid='ignore')

# Paths
WORK_PATH = os.path.dirname(os.path.abspath(__file__)) 
INPUT_IMAGES_PATH = os.path.join(WORK_PATH, "data/input")
OUTPUT_HEADS_PATH = os.path.join(WORK_PATH, "data/output/heads")
OUTPUT_COMETS_PATH = os.path.join(WORK_PATH, "data/output/comets")

# Options
DEBUG = True


def run_test(input_images, value=None):

    # Initialize Test Debugger
    if DEBUG:        
        if os.path.exists(constants.TEST_DEBUG_PATH):
            shutil.rmtree(constants.TEST_DEBUG_PATH)            
        os.mkdir(constants.TEST_DEBUG_PATH)

    # If test program was run with no arguments, each image inside
    # 'input' folder is tested
    if input_images == []:
        input_images = os.listdir(INPUT_IMAGES_PATH)

    # Choose algorithm
    algorithm = algorithms.FreeComet(False, False)
    #algorithm = algorithms.OpenComet()

    comet_statistics_list = []
    head_statistics_list = []
    for image_name in input_images:
   
        print("Input Image: " + image_name + "\n")

        # [1] Get input image
        input_image_path = os.path.join(INPUT_IMAGES_PATH, image_name)
        grayscale_input_image, original_input_image = utils.read_image(input_image_path, True)
        
        if DEBUG:
            path = __create_debug_path(image_name)
            utils.save_image(original_input_image, path)

        # [2] Execute algorithm. Returns a list of lists of contours
        sample = Sample(image_name, original_input_image)
        comets_contours_list = algorithm.execute(sample, value)
        # Build Comet objects
        comet_list = __build_comets(comets_contours_list, sample)

        # [3] Get algorithm execution output masks
        heads_output_mask = numpy.zeros(shape=(grayscale_input_image.shape), dtype=numpy.uint8)
        comets_output_mask = numpy.zeros(shape=(grayscale_input_image.shape), dtype=numpy.uint8)
        for comet in comet_list: 
            if comet._get_comet_contour() is not None:
                utils.draw_contours(comets_output_mask, [comet._get_comet_contour()])
            else:
                utils.draw_contours(comets_output_mask, [comet._get_head_contour()])
            utils.draw_contours(heads_output_mask, [comet._get_head_contour()])

        utils.save_image(comets_output_mask, "1.png")
        utils.save_image(heads_output_mask, "2.png")

        # [4] Get expected output masks (input image has to be previously manually segmented)
        # Expected output heads mask 
        _, expected_heads_image = utils.read_image(os.path.join(OUTPUT_HEADS_PATH, image_name), True)
        expected_heads_mask = utils.get_red_from_image(expected_heads_image)
        expected_heads_mask = utils.to_binary_image(utils.to_gray_image(expected_heads_mask), 1)
        # Expected output comets mask
        _, expected_comets_image = utils.read_image(os.path.join(OUTPUT_COMETS_PATH, image_name), True)
        expected_comets_mask = utils.get_red_from_image(expected_comets_image)
        expected_comets_mask = utils.to_binary_image(utils.to_gray_image(expected_comets_mask), 1)

        # [5] Input image test results
        comet_statistics = __intersection_over_union(comets_output_mask, expected_comets_mask, original_input_image,
                                                     "COMETS TEST", "Comets", image_name)
        comet_statistics_list.append(comet_statistics)               
        head_statistics = __intersection_over_union(heads_output_mask, expected_heads_mask, original_input_image,
                                                    "HEADS TEST", "Heads", image_name)
        head_statistics_list.append(head_statistics)

    # Final average test results
    return __test_results(comet_statistics_list, head_statistics_list)   

def __intersection_over_union(mask, expected_mask, original_image, title, objects_name, image_name):

    # [1] Masks
    union_mask = cv2.bitwise_or(expected_mask, mask)
    inverse_mask = (constants.MAX_VALUE) - mask
    inverse_expected_mask = (constants.MAX_VALUE) - expected_mask
    true_positives_mask = cv2.bitwise_and(mask, expected_mask)
    true_negatives_mask = cv2.bitwise_and(inverse_mask, inverse_expected_mask) 
    false_positives_mask = union_mask - expected_mask
    false_negatives_mask = union_mask - mask
 
    # [2] Statistics creation
    found_objects = len(utils.find_contours(true_positives_mask))
    real_objects_number = len(utils.find_contours(expected_mask))

    # [2.1] Intersection-Over-Union on image objects
    iou_list = []
    youden_index_list = []
    for contour in utils.find_contours(union_mask):

        x, y, width, height = utils.create_enclosing_rectangle(contour)
        true_positives = numpy.count_nonzero(true_positives_mask[y:y+height, x:x+width])
        true_negatives = numpy.count_nonzero(true_negatives_mask[y:y+height, x:x+width])
        false_positives = numpy.count_nonzero(false_positives_mask[y:y+height, x:x+width])
        false_negatives = numpy.count_nonzero(false_negatives_mask[y:y+height, x:x+width])
        contour_iou = true_positives / numpy.count_nonzero(union_mask[y:y+height, x:x+width])
        iou_list.append(contour_iou)
        

    iou = numpy.sum(iou_list) / len(iou_list)

    # [2.2] Global image Sensitivity & Specificity
    global_true_positives = numpy.count_nonzero(true_positives_mask)
    global_true_negatives = numpy.count_nonzero(true_negatives_mask)
    global_false_positives = numpy.count_nonzero(false_positives_mask)
    global_false_negatives = numpy.count_nonzero(false_negatives_mask)
    sensitivity = global_true_positives / (global_true_positives + global_false_negatives)
    specificity = global_true_negatives / (global_true_negatives + global_false_positives)       

    # [3] Test output image creation
    if DEBUG:        
        debug_image = numpy.copy(original_image)        
        # True positives coordinates
        coordinates = numpy.where(true_positives_mask != 0)
        debug_image[coordinates] = constants.GREEN
        # False positives coordinates
        coordinates = numpy.where(false_positives_mask != 0)
        debug_image[coordinates] = constants.BLUE
        # False negatives coordinates
        coordinates = numpy.where(false_negatives_mask != 0)
        debug_image[coordinates] = constants.RED
        path = __create_debug_path(image_name + "_" + objects_name)
        utils.save_image(debug_image, path)   

    '''
    # Statistics output
    print(title)
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print("Intersection Over Union = " + str(iou))
    print("Sensitivity = " + str(sensitivity))
    print("1 - specificity = " + str(1-specificity))
    print(objects_name + " found: " + str(found_objects) + "/" + str(real_objects_number))
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print("")
    '''
    return (iou, sensitivity, specificity, found_objects, real_objects_number,
            global_true_positives, global_true_negatives, global_false_positives, global_false_negatives)

def __test_results(comet_statistics_list, head_statistics_list):

    comet_avg_statistics = __average_of_statistics(comet_statistics_list, "COMETS STATISTICS", "Comets")
    head_avg_statistics = __average_of_statistics(head_statistics_list, "HEADS STATISTICS", "Heads")
    return (comet_avg_statistics, head_avg_statistics)


def __average_of_statistics(statistics, title, objects):

    n = len(statistics)

    avg_statistics = []
    # If there are statistics
    if n > 0:

        avg_iou = 0.
        avg_sensitivity = 0.
        avg_specificity = 0.
        objects_found = 0
        total_objects = 0
        youden_index = 0
        avg_true_positives = 0
        avg_true_negatives = 0
        avg_false_positives = 0
        avg_false_negatives = 0
        for x in statistics:
            avg_iou += x[0]
            avg_sensitivity += x[1]
            avg_specificity += x[2]
            objects_found += x[3]
            total_objects += x[4]
            avg_true_positives += x[5]
            avg_true_negatives += x[6]
            avg_false_positives += x[7]
            avg_false_negatives += x[8]

        avg_iou /= n
        avg_sensitivity /= n
        avg_specificity /= n
        avg_true_positives /= n
        avg_true_negatives /= n
        avg_false_positives /= n
        avg_false_negatives /= n
        avg_statistics = [avg_iou, avg_sensitivity, avg_specificity, objects_found, total_objects,
                          avg_true_positives, avg_true_negatives, avg_false_positives, avg_false_negatives]

        # Statistics Output
        print(title)
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print("AVG Intersection Over Union = " + str(round(avg_iou*100, 2)) + "%")
        print("AVG Sensitivity = " + str(avg_sensitivity))
        print("1 - specificity = " + str(1-avg_specificity))
        print(objects + " found: " + str(round(objects_found/total_objects*100, 2)) + "%")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

    return avg_statistics


def __create_debug_path(image_name):
    return constants.TEST_DEBUG_PATH + "/" + image_name + ".png" 

def __build_comets(comet_contours_list, sample):

    comet_list = []
    for (comet_contour, head_contour) in comet_contours_list:

        # Build Comet
        comet = model.Comet(comet_contour, head_contour, sample)
        comet_list.append(comet)

    return comet_list

def get_youden_index(true_positives, true_negatives, false_positives, false_negatives):

    return (true_positives / (true_positives + false_negatives)) + (true_negatives / (true_negatives + false_positives)) - 1

def __print_usage_and_exit():
    print("main.py <image_name>")
    sys.exit()

if __name__ == "__main__":

    run_test(sys.argv[1:])

    '''
    tail_score_array = ([], [])
    head_score_array = ([], [])
    tail_youden_index_array = []
    head_youden_index_array = []
    values = []

    index = 0
    value = 3
    while index < 7:
        
        values.append(value)
        (tail_avg_metrics, head_avg_metrics) = run_test(sys.argv[1:], value)
        tail_score_array[0].append(1-tail_avg_metrics[2])
        tail_score_array[1].append(tail_avg_metrics[1])
        tail_youden_index_array.append(get_youden_index(
            tail_avg_metrics[5], tail_avg_metrics[6], tail_avg_metrics[7], tail_avg_metrics[8]))
        head_score_array[0].append(1-head_avg_metrics[2])
        head_score_array[1].append(head_avg_metrics[1])
        head_youden_index_array.append(get_youden_index(
            head_avg_metrics[5], head_avg_metrics[6], head_avg_metrics[7], head_avg_metrics[8]))
        value += 2
        index += 1

    # Best Tail Value
    index = tail_youden_index_array.index(max(tail_youden_index_array))
    print("Best Tail value: " + str(values[index]))
    print("Best Tail Youden Index: " + str(tail_youden_index_array[index]))
    
    plt.plot(*tail_score_array)
    plt.plot(*tail_score_array, 'ro')
    plt.plot([tail_score_array[0][index]], [tail_score_array[1][index]],'yo')
    plt.title('Tamaño del filtro de mediana - COLA')
    plt.ylabel('Sensibilidad')
    plt.xlabel('1 - Especificidad')
    plt.autoscale(True)
    plt.ylim(top=1)
    plt.xlim(left=0)
    plt.show()

    # Best Head Value
    index = head_youden_index_array.index(max(head_youden_index_array))
    print("Best Head value: " + str(values[index]))
    print("Best Head Youden Index: " + str(head_youden_index_array[index]))
    

    plt.plot(*head_score_array)
    plt.plot(*head_score_array, 'ro')
    plt.plot([head_score_array[0][index]], [head_score_array[1][index]],'yo')
    plt.title('Tamaño del filtro de mediana - CABEZA')
    plt.ylabel('Sensibilidad')
    plt.xlabel('1 - Especificidad')
    plt.autoscale(True)
    plt.show()
    '''


