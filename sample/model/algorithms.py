# -*- encoding: utf-8 -*-

'''
    The algorithms module.
'''

# General imports

#from cv2_rolling_ball import subtract_background_rolling_ball
from matplotlib import pyplot
import shutil
import numpy
import math
import cv2
import sys
import os


# Custom imports
import sample.model.image_processing_facade as facade
import sample.model.utils as utils
import sample.model.constants as constants
from sample.singleton import Singleton
from sample.model.classifier import DecisionTree



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	Algorithm                                                                 #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class Algorithm(metaclass=Singleton):

    '''
        The Algorithm abstract class. Extends from Singleton.
    '''

    def __init__(self):

        # Debugging attributes
        self.DEBUG = False                       # Debugging flag
        self.debug_folder_path = None            # Path to save the debugging images
        self.debug_counter = 0                   # Counter to chronologically save the debugging images
        self.original_image = None               # The original image
        self.image_name = None                   # The image name

    def execute(self, *args):
        raise NotImplementedError("Method must be implemented.")


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Debugging Methods                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #        

    def initialize_debugger(self, original_image, image_name):

        self.original_image = original_image
        self.image_name = image_name

        self.debug_folder_path = constants.ALGORITHM_DEBUG_PATH + image_name.split('.')[0]
        if os.path.exists(self.debug_folder_path):
            shutil.rmtree(self.debug_folder_path)            
        os.mkdir(self.debug_folder_path)
        path = self.create_debug_path("Input image")          
        utils.save_image(original_image, path)
    
    def create_debug_image(self, binary_image):
      
        debug_image = numpy.copy(self.original_image)
        utils.draw_contours(debug_image, utils.find_contours(binary_image), constants.GREEN, 2)
        return debug_image

    def create_debug_path(self, image_description):

        path = self.debug_folder_path + "/" + str(self.debug_counter) + "_" + image_description + ".png" 
        self.debug_counter += 1
        return path

    '''
    def _save_comets_attributes(self, comet_list):

        f = open(os.path.join(constants.DEBUG_PATH, self.WRITE_FILENAME), "a+")

        for comet in comet_list:

            # Desired attributes are saved to train a classifier.
            head_to_comet_ratio = comet.get_head_area() / comet.get_comet_area()
            head_avg_intensity = comet.get_head_average_intensity()
            tail_avg_intensity = comet.get_tail_average_intensity() 
            comet_contour = comet.get_comet_contour()
            head_contour = comet.get_head_contour()
            left_length = (utils.get_contour_leftmost_point(head_contour)[0] -
                           utils.get_contour_leftmost_point(comet_contour)[0])
            right_length = (utils.get_contour_rightmost_point(comet_contour)[0] -
                           utils.get_contour_rightmost_point(head_contour)[0])
            length_difference = right_length - left_length
           
           
            line = ("[" + str(head_to_comet_ratio) + ", " 
                        + str(head_avg_intensity) + ", "
                        + str(tail_avg_intensity) + ", " 
                        + str(length_difference) + "], ")
            f.write(line + "\n")

        f.write("\n")
        f.close()
    '''



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	FreeComet                                                                 #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class FreeComet(Algorithm):

    '''
        The FreeComet class. Extends from Algorithm.
    '''

    ''' Initialization method. '''
    def __init__(self, fit_head_flag, fit_tail_flag):

        # Algorithm class initialization
        super().__init__()

        # Settings
        self.__fit_head_flag = fit_head_flag
        self.__fit_tail_flag = fit_tail_flag

        # Classifier
        self.WRITE = False
        self.WRITE_FILENAME = "samples.txt"
        self.classifier = DecisionTree()

        # Algorithm default parameters
        self.WINDOW_EXPAND_OFFSET = 5
        self.N_MAX_SEGMENTATION_TIMES = 2

        self.PREPROCESSING_MEDIAN_RADIUS = 6   # 6
        self.PREPROCESSING_CLOSING_RADIUS = 5            
        self.COMET_PROCESSING_MEDIAN_RADIUS = 5 
        self.COMET_FILTERING_CLOSING_RADIUS = 5             
        self.COMET_PROCESSING_DILATION_RADIUS = 5
        self.COMET_MAXIMUM_HEIGHT_WIDTH_RATIO = 1.2
        self.COMET_MAXIMUM_WIDTH_HEIGHT_RATIO = 1.4
        self.COMET_IMPROVING_ELLIPTICAL_OPENNING_RADIUS = 20
        self.HEAD_MINIMUM_CONVEXITY = 0.85
        self.HEAD_MINIMUM_CIRCULARITY = 0.8
        self.MAXIMUM_HEAD_COMET_PROPORTION = 0.26

    ''' Algorithm.execute() implementation method. '''
    def execute(self, sample, value=None):

        original_image = sample.get_image()
        gs_image = utils.normalize_image(utils.to_gray_image(original_image))
        image_name = sample.get_name()

        # Update algorithm parameters
        self.__update_algorithm_parameters(gs_image, value)

        if self.DEBUG:
            self.initialize_debugger(original_image, image_name)

        # [0] Display input image histogram.
        #histogram = cv2.calcHist([utils.renormalize_image(gs_image)], 
        #                 [0], None, [constants.LEVELS], [0, constants.LEVELS])
        #pyplot.plot(histogram)
        #pyplot.show()
       
        # [1] IMAGE PREPROCESSING
        smoothed_gs_image = self.__preprocessing(gs_image)
        # [2] COMET FINDING
        comets_binary_mask = self.__comet_finding(smoothed_gs_image)
        # [3] HEAD SEGMENTATION
        comets_contours_list = self.__head_segmentation(comets_binary_mask, gs_image)
        # [4] TAIL SEGMENTATION
        comets_contours_list = self.__tail_segmentation(comets_contours_list, gs_image)
        # [5] COMET FILTERING
        comets_contours_list = self.__comet_filtering(comets_contours_list, gs_image)
               
        '''
        # Save in a file the desired attributes of the found comets
        if self.WRITE:            
            self._save_comets_attributes(comets_contours_list)
        '''

        return comets_contours_list

    ''' Update algorithm parameters. '''
    def __update_algorithm_parameters(self, image, value):

        # Initialize debug counter
        self.debug_counter = 0
        # Update parameters      
        self.HEAD_MINIMUM_SIZE = image.size * 0.0002
        self.COMET_MINIMUM_SIZE = (image.size * 0.001) + self.HEAD_MINIMUM_SIZE
        #self.PREPROCESSING_MEDIAN_RADIUS = value
            

    ''' Comet filtering. '''
    def __comet_filtering(self, comet_contours, gs_image):

        new_comet_contours = []
        for comet_contour in comet_contours:

            if self.__is_valid_comet(comet_contour, gs_image):
                new_comet_contours.append(comet_contour)

        if self.DEBUG:

            debug_image = numpy.copy(self.original_image)
            for comet in new_comet_contours:
                if comet[0] is not None:
                    utils.draw_contours(debug_image, [comet[0]], constants.RED, 2)
                utils.draw_contours(debug_image, [comet[1]], constants.GREEN, 2)
            path = self.create_debug_path("Comet Filtering")           
            utils.save_image(debug_image, path)

        return new_comet_contours

    def __is_valid_comet(self, comet, gs_image):

        comet_contour = comet[0]
        head_contour = comet[1]

        if comet_contour is None:
            comet_contour = head_contour

        # [1] Comets touching the edge of the image are filtered out
        if utils.is_contour_on_border(gs_image, comet_contour):
            return False
        # [2] Head is in the correct place
        if (comet[0] is not None) and (not self.__is_head_in_correct_place(comet_contour, head_contour)):
            return False
        # [3] Comet orientation and size isn't abnormal
        (x, y), (ma, MA), angle = cv2.fitEllipse(comet_contour)      
        # 90º = horizontal
        if angle < 75. or angle > 105:
            # Height-Width ratio
            if (ma / MA) > self.COMET_MAXIMUM_HEIGHT_WIDTH_RATIO:
                return False
            # Width-Height ratio
            if (MA / ma) > self.COMET_MAXIMUM_WIDTH_HEIGHT_RATIO:
                return False               

        return True

    def __is_head_in_correct_place(self, comet_contour, head_contour):

        (x, y, comet_width, comet_height) = utils.create_enclosing_rectangle(comet_contour)        
        (head_x, head_y) = utils.get_contour_centroid(head_contour)

        # [1] Head is on the left (default) side of the comet
        if head_x > (x + (comet_width / 2)):
            return False       

        # [2] Head is in the middle of the comet       
        comet_height_third = comet_height / 3
        return (head_y > y+(comet_height_third)) and (head_y < y+(2*comet_height_third)) 
       

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                               Preprocessing                                 #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

    ''' Preprocessing. '''
    def __preprocessing(self, gs_image):

        height, width = gs_image.shape
          
        # [1] Circular closing filter
        gs_image = facade.closing(gs_image, self.PREPROCESSING_CLOSING_RADIUS)

        if self.DEBUG:
            path = self.create_debug_path("Closing filter radius " + str(self.PREPROCESSING_CLOSING_RADIUS))          
            utils.save_image(utils.renormalize_image(gs_image), path)

        # [2] Circular median filter
        gs_image = facade.circular_median(gs_image, self.PREPROCESSING_MEDIAN_RADIUS)

        if self.DEBUG:
            path = self.create_debug_path("Median filter radius " + str(self.PREPROCESSING_MEDIAN_RADIUS))          
            utils.save_image(utils.renormalize_image(gs_image), path)
        
        return gs_image


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                              Comet finding                                  #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

    ''' Comet finding. '''
    def __comet_finding(self, gs_image):

        # [1] Objects are retrieved from the background
        binary_image = self.__separate_objects_from_background(gs_image)

        # [2] Comet size filtering
        return self.__comet_size_filtering(binary_image)

    ''' Separate objects from background. '''
    def __separate_objects_from_background(self, gs_image):
        
        # Global Triangle thresholding method
        threshold, _ = facade.triangle_threshold(gs_image)
        binary_image = utils.to_binary_image(gs_image, threshold)

        # Debug
        if self.DEBUG:
            path = self.create_debug_path("Objects  Threshold: " + str(threshold))          
            utils.save_image(binary_image, path)
            debug_image = self.create_debug_image(binary_image)
            path = self.create_debug_path("Objects contours  Threshold: " + str(threshold))   
            utils.save_image(debug_image, path)

        return binary_image

    ''' Comet size filtering. '''
    def __comet_size_filtering(self, binary_image):
       

        new_binary_image = numpy.zeros(shape=(binary_image.shape))
        for contour in utils.find_contours(binary_image):
            
            # [1] If contour is too small it's wiped out
            if utils.get_contour_area(contour) < self.COMET_MINIMUM_SIZE:
                x, y, width, height = utils.create_enclosing_rectangle(contour)            
                temp_binary_image = utils.create_contour_mask(contour, binary_image, (x, y, width, height))
                contour_pixels = numpy.where(temp_binary_image != 0) 
                contour_pixels = (contour_pixels[0] + y, contour_pixels[1] + x)
                binary_image[contour_pixels] = 0
            # [2] Closing filter to reduce holes and irregular shapes occurences
            else:     
                temp_mask, rec = utils.create_expanded_contour_mask(contour, binary_image, self.WINDOW_EXPAND_OFFSET*2)      
                temp_mask = facade.closing(temp_mask, self.COMET_FILTERING_CLOSING_RADIUS)
                mask_contour = utils.find_contours(temp_mask)[0]
                mask_contour += (rec[0], rec[1])
                utils.draw_contours(new_binary_image, [mask_contour])

        # Debug
        if self.DEBUG:

            debug_image = numpy.copy(self.original_image)
            for contour in utils.find_contours(new_binary_image):
                utils.draw_contours(debug_image, [contour], constants.GREEN, 2)
            path = self.create_debug_path("Comet filtering")             
            utils.save_image(debug_image, path)
            
        return new_binary_image


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Head segmentation                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

    ''' Head segmentation. '''
    def __head_segmentation(self, binary_image, gs_image):

        # First phase: head finding
        comet_list, processed_image = self.__find_heads(binary_image, gs_image)

        # Debug
        if self.DEBUG:
            debug_image = numpy.copy(self.original_image)
            for comet in comet_list:
                utils.draw_contours(debug_image, [comet[0]], constants.RED, 2)
            path = self.create_debug_path("Comet contours")
            utils.save_image(debug_image, path)
            for comet in comet_list:
                for head in comet[1]:
                    utils.draw_contours(debug_image, [head], constants.GREEN, 2)
            path = self.create_debug_path("Head Segmentation  Phase 1  All Contours")
            utils.save_image(debug_image, path)
            path = self.create_debug_path("Head Segmentation  Phase 1  Processed Image")
            utils.save_image(utils.renormalize_image(processed_image), path)
            
        # Second phase: head segmentation
        comet_list = self.__segment_heads(comet_list, binary_image, gs_image, processed_image)  

        # Debug
        if self.DEBUG:
            debug_image = numpy.copy(self.original_image)
            for comet in comet_list:
                utils.draw_contours(debug_image, [comet[0]], constants.RED, 2)
                for head in comet[1]:
                    utils.draw_contours(debug_image, [head], constants.GREEN, 2)
            path = self.create_debug_path("Head Segmentation  Phase 2  Contours")
            utils.save_image(debug_image, path)

        # Head filtering
        return self.__head_filtering(gs_image, comet_list)
  
    def __find_heads(self, binary_image, gs_image):

        image_height, image_width = binary_image.shape
        processed_image = numpy.copy(gs_image)

        comet_list = []
        # Each comet is processed and its head location searched
        for comet_contour in utils.find_contours(binary_image):

            # [1.] PREAMBLE

            # Expanded Comet Mask
            comet_mask, rec = utils.create_expanded_contour_mask(comet_contour, binary_image, self.WINDOW_EXPAND_OFFSET)
            # Comet Mask Dilation radius n
            comet_mask = facade.dilate(comet_mask, self.WINDOW_EXPAND_OFFSET)            
            # Comet ROI
            roi = numpy.copy(gs_image[rec[1]:rec[1]+rec[3], rec[0]:rec[0]+rec[2]])

            # [2.] COMET REGION PROCESSING
            # Dilation
            processed_roi = facade.dilate(roi, self.COMET_PROCESSING_DILATION_RADIUS)
            # Median
            processed_roi = facade.circular_median(processed_roi, self.COMET_PROCESSING_MEDIAN_RADIUS)
            # Dilation
            processed_roi = facade.dilate(processed_roi, self.COMET_PROCESSING_DILATION_RADIUS)
            # Median
            processed_roi = facade.circular_median(processed_roi, self.COMET_PROCESSING_MEDIAN_RADIUS)

            # [3.] UPDATE IMAGE WITH PROCESSED COMETS           
            # Apply comet mask to ROIs
            coordinates = numpy.where(comet_mask == 0)
            roi[coordinates] = 0
            processed_roi[coordinates] = 0
            coordinates = numpy.where(comet_mask != 0)
            processed_image_coordinates = (coordinates[0] + rec[1], coordinates[1] + rec[0])
            processed_image[processed_image_coordinates] = processed_roi[coordinates] 

            if self.DEBUG:
                path = self.create_debug_path("Phase 1  Original Comet before Otsu")          
                utils.save_image(utils.renormalize_image(roi), path)
                path = self.create_debug_path("Phase 1  Processed Comet before Otsu")           
                utils.save_image(utils.renormalize_image(processed_roi), path)
 
            # [4.] OTSU THRESHOLD
            heads_binary_image = utils.to_binary_image(processed_roi, facade.otsu_threshold(processed_roi, comet_mask))

            if self.DEBUG:
                coordinates = numpy.where(heads_binary_image == 0)
                roi[coordinates] = 0
                processed_roi[coordinates] = 0
                path = self.create_debug_path("Phase 1  Original Comet after Otsu")           
                utils.save_image(utils.renormalize_image(roi), path)
                path = self.create_debug_path("Phase 1  Processed Comet after Otsu")           
                utils.save_image(utils.renormalize_image(processed_roi), path)

            # [5.] ADD COMET AND HEAD BOUNDARIES MASKS TO COMET LIST 
            comet_contour = utils.find_contours(comet_mask)[0]
            comet_contour += (rec[0], rec[1])
            new_head_contours = []
            for head_contour in utils.find_contours(heads_binary_image):
                head_contour += (rec[0], rec[1]) 
                new_head_contours.append(head_contour)                                                        
                
            comet_list.append((comet_contour, new_head_contours))
           
        return comet_list, processed_image

    def __segment_heads(self, comet_list, binary_image, gs_image, processed_image):

        # Potential heads are segmented
        i = 0
        while i < len(comet_list):
            comet_list[i] = self.__segment_head(comet_list[i], binary_image, gs_image, processed_image)
            i += 1

        return comet_list

    def __segment_head(self, comet, binary_image, gs_image, processed_image):
           
        comet_contour = comet[0]
        x, y, width, height = utils.create_enclosing_rectangle(comet_contour)
        new_head_mask = numpy.zeros(binary_image.shape, dtype=numpy.uint8)
        new_head_mask = new_head_mask[y:y+height, x:x+width]

        for head_contour in comet[1]:
                    
            # [1] PREAMBLE

            # Processed Head Mask
            head_mask = utils.create_contour_mask(head_contour, binary_image, (x, y, width, height)) 
            # Processed Head Grayscale ROI            
            processed_head = numpy.copy(processed_image[y:y+height, x:x+width])
            coordinates = numpy.where(head_mask == 0)
            processed_head[coordinates] = 0                 
            
            if self.DEBUG:
                original_head = numpy.copy(gs_image[y:y+height, x:x+width])               
                original_head[coordinates] = 0 
                path = self.create_debug_path("Phase 2  Original Head")           
                utils.save_image(utils.renormalize_image(original_head), path)
                path = self.create_debug_path("Phase 2  Processed Head")           
                utils.save_image(utils.renormalize_image(processed_head), path)
                head_contour = utils.find_contours(head_mask)[0]
                convexity = utils.get_contour_convexity(head_contour)
                circularity = utils.get_contour_circularity(head_contour)
                area = utils.get_contour_area(head_contour)
                proportion = utils.get_contour_area(head_contour) / utils.get_contour_area(comet_contour)
                path = self.create_debug_path("Convexity: " + str(convexity) + " Circularity: " + str(circularity) +
                                               " Area: " + str(area) + "  Proportion " + str(proportion))
                utils.save_image(head_mask, path)
           
            # [3.] Process head until its segmentation is valid or it's been segmentated 
            # self.N_MAX_SEGMENTATION_TIMES times.
            segmentation_counter = 0
            while (segmentation_counter < self.N_MAX_SEGMENTATION_TIMES and 
                   not self.__is_head_too_small(head_mask) and 
                   not self.__is_valid_head_segmentation(head_mask, comet_contour)):

                # [3.1] Otsu threshold
                head_mask = utils.to_binary_image(processed_head, facade.otsu_threshold(processed_head, head_mask))           

                # [3.2] Update head after threshold
                coordinates = numpy.where(head_mask == 0)
                processed_head[coordinates] = 0

                if self.DEBUG:
                    head_roi = numpy.copy(gs_image[y:y+height, x:x+width])               
                    head_roi[coordinates] = 0 
                    head_contour = utils.find_contours(head_mask)[0] 
                    path = self.create_debug_path("Phase 2  Original Head " + str(segmentation_counter))           
                    utils.save_image(utils.renormalize_image(head_roi), path)
                    path = self.create_debug_path("Phase 2  Processed Head " + str(segmentation_counter))           
                    utils.save_image(utils.renormalize_image(processed_head), path)
                    head_contour = utils.find_contours(head_mask)[0]
                    convexity = utils.get_contour_convexity(head_contour)
                    circularity = utils.get_contour_circularity(head_contour)
                    area = utils.get_contour_area(head_contour)
                    proportion = utils.get_contour_area(head_contour) / utils.get_contour_area(comet_contour)
                    path = self.create_debug_path("Convexity: " + str(convexity) + " Circularity: " + str(circularity) +
                                               " Area: " + str(area) + "  Proportion " + str(proportion))
                    utils.save_image(head_mask, path)

                segmentation_counter += 1

            new_head_mask |= head_mask

        head_contours = []       
        for head_contour in utils.find_contours(new_head_mask):
            head_contour += (x, y)
            head_contours.append(head_contour)
                                
        return (comet_contour, head_contours)                                                           

    def __is_valid_head_segmentation(self, head_mask, comet_contour):
        
        head_contour = utils.find_contours(head_mask)[0]

        proportion = utils.get_contour_area(head_contour) / utils.get_contour_area(comet_contour)
        # Segment more for more accurate results
        if proportion > self.MAXIMUM_HEAD_COMET_PROPORTION:
            return False
        # Segmentation should be convex
        if utils.get_contour_convexity(head_contour) < self.HEAD_MINIMUM_CONVEXITY:
            return False
        # Segmentation should be circular
        if utils.get_contour_circularity(head_contour) < self.HEAD_MINIMUM_CIRCULARITY:
            return False

        return True   
                       
    def __head_filtering(self, gs_image, comet_list):

        new_comet_list = []

        if self.DEBUG:
            height, width = gs_image.shape
            debug_image = numpy.zeros((height, width, 3), numpy.uint8)

        i = 0
        while i < len(comet_list):

            comet_contour = comet_list[i][0]

            # [1] Validate head contours          
            new_head_contours = []
            for head_contour in comet_list[i][1]:                
                if self.__is_valid_head(gs_image, head_contour):
                    new_head_contours.append(head_contour)
                    if self.DEBUG:
                        utils.draw_contours(debug_image, [head_contour], constants.GREEN)                    
                else:
                    if self.DEBUG:
                        utils.draw_contours(debug_image, [head_contour], constants.RED)
           
            if self.DEBUG:
                utils.draw_contours(debug_image, comet_contour)           
                path = self.create_debug_path("Head Filtering : GREEN=Valid  RED=Not_Valid")
                utils.save_image(debug_image, path)

            # [2] Otsu algorithm might bring more than 1 potential heads. Best candidate is chosen.
            if len(new_head_contours) > 1:
                new_head_contours = self.__choose_comet_head(gs_image, comet_contour, new_head_contours)

            # [3] Comet regions without valid head contours are ignored.
            if len(new_head_contours) == 1:
                new_comet_list.append((comet_contour, new_head_contours[0]))

            i += 1

        return new_comet_list
        
    def __is_valid_head(self, image, head_contour):
           
        # Heads are not too small
        if utils.get_contour_area(head_contour) < self.HEAD_MINIMUM_SIZE:          
            return False        
        # Heads touching the edge of the original image are filtered out
        if utils.is_contour_on_border(image, head_contour):
            return False
        # Heads are convex
        if utils.get_contour_convexity(head_contour) < self.HEAD_MINIMUM_CONVEXITY:
            return False
        # Heads are circular
        if utils.get_contour_circularity(head_contour) < self.HEAD_MINIMUM_CIRCULARITY:
            return False

        return True

    def __is_head_too_small(self, head_mask):       
        head_contour = utils.find_contours(head_mask)[0]
        return utils.get_contour_area(head_contour) < self.HEAD_MINIMUM_SIZE

    def __choose_comet_head(self, gs_image, comet_contour, head_contours):

        # [1] Comet Y centroid
        _, y = utils.get_contour_centroid(comet_contour, True)

        # [2] Pivot point
        x, _, width, _ = utils.create_enclosing_rectangle(comet_contour)
        pivot_point = (y, x + width*0.1)

        # [3] Closest head contour to pivot point is chosen as comet's head
        if self.DEBUG:
            height, width = gs_image.shape
            debug_image = numpy.zeros((height, width, 3), numpy.uint8)
            utils.draw_contours(debug_image, [comet_contour])

        min_distance = sys.maxsize
        head = None
        head_x = None
        head_y = None
        for head_contour in head_contours:

            x, y = utils.get_contour_centroid(head_contour, True)
            distance = utils.euclidean_distance(pivot_point, (y, x))
            if distance < min_distance:
                min_distance = distance
                head = head_contour
                head_x = x
                head_y = y

            if self.DEBUG:          
                utils.draw_contours(debug_image, [head_contour], constants.RED)
                debug_image[y][x] = constants.BLUE
                
        if self.DEBUG:           
            utils.draw_contours(debug_image, [head], constants.GREEN)
            debug_image[head_y][head_x] = constants.BLUE
            debug_image[int(pivot_point[0])][int(pivot_point[1])] = constants.BLUE   
            path = self.create_debug_path("Green: Choosen head  Blue: Pivot Point")
            utils.save_image(debug_image, path)
    
        return [head]


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Tail segmentation                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

    def __tail_segmentation(self, comet_list, gs_image):

        i = 0
        while i < len(comet_list):
               
            # [1] Tail Segmentation        
            comet_list[i] = self.__segment_tail(comet_list[i], gs_image)

            # [2] Healthy comets should not have tail
            comet_contour = comet_list[i][0]
            head_contour = comet_list[i][1]
            healthy_comet = self.__is_healthy_comet(comet_contour, head_contour, gs_image)
            if healthy_comet is not None:
                if healthy_comet: 
                    comet_contour = None
                # [3] Fitting Options
                else:
                    # [3.1] Tail fitting
                    if self.__fit_tail_flag:
                        comet_contour = self.__fit_tail(comet_contour, head_contour, gs_image)
                    # [3.2] Head fitting
                    if self.__fit_head_flag:
                        head_contour = self.__fit_head(comet_contour, head_contour, gs_image)

                comet_list[i] = (comet_contour, head_contour)
            i += 1

        if self.DEBUG:
            debug_image = numpy.copy(self.original_image)
            for comet in comet_list:
                if comet[0] is not None:
                    utils.draw_contours(debug_image, [comet[0]], constants.RED, 2)
                utils.draw_contours(debug_image, [comet[1]], constants.GREEN, 2)
            path = self.create_debug_path("Tail segmentation")           
            utils.save_image(debug_image, path)

        return comet_list 

    def __segment_tail(self, comet, gs_image):

        comet_contour, head_contour = comet[0], comet[1]
        x, y, width, height = utils.create_enclosing_rectangle(comet_contour) 
        
        # [1] Comet & Head masks creation
        comet_mask = utils.create_contour_mask(comet_contour, gs_image, (x, y, width, height))
        head_mask = utils.create_contour_mask(head_contour, gs_image, (x, y, width, height))

        if self.DEBUG:
            path = self.create_debug_path("Phase 2  Comet before improving")           
            utils.save_image(comet_mask, path)

        # [2] Improve comet figure 
        # [2.1] Elliptical Opening Filter         
        improved_comet_mask = facade.elliptical_openning(comet_mask, height//4, width//4)
        if self.DEBUG:
            path = self.create_debug_path("Phase 2  Comet after elliptical openning radius_x: "
                                             + str(width//4) + " radius_y: " + str(height//4))        
            utils.save_image(improved_comet_mask, path)
        
        # [2.2] Head must not be affected when applying these filters
        and_mask = cv2.bitwise_and(improved_comet_mask, head_mask)
        if numpy.count_nonzero(and_mask) == numpy.count_nonzero(head_mask):
            comet_contour = utils.find_contours(improved_comet_mask)[0]
            comet_contour += (x, y)

        comet_contour = utils.get_contour_convex_hull(comet_contour)
        if self.DEBUG:
            debug_mask = utils.create_contour_mask(comet_contour, gs_image, (x, y, width, height))
            path = self.create_debug_path("Phase 2  Convex hull")           
            utils.save_image(debug_mask, path)

        return (comet_contour, head_contour)

    def __is_healthy_comet(self, comet_contour, head_contour, gs_image):

        classifier_sample = []

        # [1] Head Area to Comet Area proportion
        comet_area = utils.get_contour_area(comet_contour)
        if comet_area == 0:
            return None
        classifier_sample.append(utils.get_contour_area(head_contour) / comet_area)

        # [2] Head average intensity
        (x, y, width, height) = utils.create_enclosing_rectangle(comet_contour)
        head_mask = utils.create_contour_mask(head_contour, gs_image, (x, y, width, height))
        head_roi = numpy.copy(gs_image[y:y+height, x:x+width])
        coordinates = numpy.where(head_mask != 0)
        if len(coordinates[0]) == 0 or len(coordinates[1]) == 0:
            return None
        classifier_sample.append(numpy.sum(head_roi[coordinates]) / len(coordinates[0]))

        # [3] Tail average intensity
        comet_mask = utils.create_contour_mask(comet_contour, gs_image, (x, y, width, height))
        tail_mask =  comet_mask - head_mask
        tail_roi = numpy.copy(gs_image[y:y+height, x:x+width])
        coordinates = numpy.where(tail_mask != 0)
        if len(coordinates[0]) == 0 or len(coordinates[1]) == 0:
            return None
        classifier_sample.append(numpy.sum(tail_roi[coordinates]) / len(coordinates[0]))

        # [4] Sides length differences
        left_length = (utils.get_contour_leftmost_point(head_contour)[0] -
                       utils.get_contour_leftmost_point(comet_contour)[0])
        right_length = (utils.get_contour_rightmost_point(comet_contour)[0] -
                       utils.get_contour_rightmost_point(head_contour)[0])
        classifier_sample.append(right_length - left_length)

        if (math.isnan(classifier_sample[0]) or math.isnan(classifier_sample[1]) or
                math.isnan(classifier_sample[2]) or math.isnan(classifier_sample[3])):
            return None

        return (self.classifier.predict([classifier_sample]) == 1)

    def __fit_tail(self, comet_contour, head_contour, gs_image):

        # [1] Get Ellipse That Fits The Comet Contour        
        (x, y), (ma, MA), angle = cv2.fitEllipse(comet_contour)
        comet_mask = numpy.zeros(shape=(gs_image.shape))
        utils.draw_contours(comet_mask, [head_contour])
        # [2] Get New Comet Contour (head and comet contours union)      
        utils.draw_ellipse(comet_mask, (int(x), int(y)), (int(ma/2), int(MA/2)), angle, constants.WHITE, -1, False)          
        new_comet_contour = utils.find_contours(comet_mask)[0]

        return new_comet_contour

    def __fit_head(self, comet_contour, head_contour, gs_image):

        # [1] Get Ellipse That Fits The Head Contour        
        (x, y), (ma, MA), angle = cv2.fitEllipse(head_contour)
        head_mask = numpy.zeros(shape=(gs_image.shape))     
        utils.draw_ellipse(head_mask, (int(x), int(y)), (int(ma/2), int(MA/2)), angle, constants.WHITE, -1, False)          
        new_head_contour = utils.find_contours(head_mask)[0]

        return new_head_contour



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	OpenComet                                                                 #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class OpenComet(Algorithm):

    '''
        The OpenComet class. Extends from Algorithm. Implements Singleton 
        pattern. Implements main steps from the original algorithm.
    '''

    ''' Initialization method. '''
    def __init__(self):
        
        # Parent initialization
        super().__init__()

        # Algorithm Parameters
        self.NOISE_FILTER_RADIUS = 10
        self.COMET_MORPH_RADIUS = 3
        self.COMET_MINIMUM_SIZE = 1000
        self.COMET_MINIMUM_CONVEXITY_RATIO = 0.85
        self.COMET_MAXIMUM_HEAD_DISPLACEMENT_RATIO = 0.2
        self.COMET_MAXIMUM_HEIGHT_WIDTH_RATIO = 1.05
        self.COMET_MAXIMUM_SYMMETRY_RATIO = 0.5
        self.BRIGHTEST_REGION_CLOSING_RADIUS = 5

    ''' Algorithm.execute() implementation. '''
    def execute(self, sample, value=None):

        original_image = sample.get_image()
        gs_image = utils.normalize_image(utils.to_gray_image(original_image))
        image_name = sample.get_name()

        # [0] Debugging initialization
        if self.DEBUG:
            self.initialize_debugger(original_image, image_name)

        # [1] Comet Finding
        comet_contours = self.__comet_finding(gs_image)

        if self.DEBUG:
            debug_image = numpy.copy(self.original_image)
            for comet in comet_contours:
                utils.draw_contours(debug_image, [comet], constants.GREEN, 2)
            path = self.create_debug_path("Comet Finding")          
            utils.save_image(debug_image, path)

        # [2] Head Finding
        comets_contours_list = self.__head_segmentation(comet_contours, gs_image)

        if self.DEBUG:
            debug_image = numpy.copy(self.original_image)
            for comet_contour in comets_contours_list:               
                utils.draw_contours(debug_image, [comet_contour[0]], constants.RED, 2)
                utils.draw_contours(debug_image, [comet_contour[1]], constants.GREEN, 2)
            path = self.create_debug_path("Final Result")          
            utils.save_image(debug_image, path)

        return comets_contours_list           
        
    def __comet_finding(self, image):

        # [1] Noise filter
        image = self.__noise_filter(image)
        # [2] Global background correction
        #image = self.__global_background_correction(image)
        # [3] Adaptive thresholding     
        image = self.__adaptive_thresholding(image)
        # [4] Morphological filter       
        image = self.__morphological_filter(image, 3)
        # [5] Comet region finding       
        comet_contours = self.__comet_region_finding(image)
        # [6] Region shape filter
        comet_contours = self.__comet_shape_filter(comet_contours, image)

        return comet_contours


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                Comet finding                                #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

    def __noise_filter(self, image):

        # Circular median filter
        image = facade.circular_median(image, self.NOISE_FILTER_RADIUS)

        if self.DEBUG:
            path = self.create_debug_path("Circular median radius " + str(self.NOISE_FILTER_RADIUS))          
            utils.save_image(utils.renormalize_image(image), path)   

        return image     

    '''
    def __global_background_correction(self, image):
    
        height, width = image.shape 
        # Rolling ball background subtractor algorithm 
        radius = int(numpy.minimum(height, width) * 0.3)
        image, _ = subtract_background_rolling_ball(utils.renormalize_image(image), radius, False, False, True)
        
        if self.DEBUG:
            path = self.create_debug_path("Substract background rolling ball radius " + str(radius))          
            utils.save_image(image, path)

        return utils.normalize_image(image)
    '''

    def __adaptive_thresholding(self, image):
        
        # In the docs, they say they apply the threshold method adaptively but does not 
        # make much sense after subtracting the background, plus in the code they use
        # it as a global method.

        # Huang's thresholding method
        threshold = facade.huang_threshold(image)
        image = utils.to_binary_image(image, threshold)

        if self.DEBUG:
            path = self.create_debug_path("Huang threshold " + str(threshold))          
            utils.save_image(image, path)

        return image

    def __morphological_filter(self, image, iterations):
  
        # n dilations 
        i = 0
        while i < iterations:
            image = facade.dilate(image, self.COMET_MORPH_RADIUS)
            i += 1

        if self.DEBUG:
            path = self.create_debug_path(str(iterations) + " dilations")          
            utils.save_image(image, path)

        # n erodes
        i = 0
        while i < iterations:
            image = facade.erode(image, self.COMET_MORPH_RADIUS)
            i += 1

        if self.DEBUG:
            path = self.create_debug_path(str(iterations) + " erosions")          
            utils.save_image(image, path)

        return image

    def __comet_region_finding(self, image):
        return utils.find_contours(image)

    def __comet_shape_filter(self, contours, image):
        
        filtered_contours = []       
        for contour in contours:

            rect = utils.create_enclosing_rectangle(contour)
            comet_mask = utils.create_contour_mask(contour, image, rect)
            if self.__validate_comet(image, comet_mask, contour):
                # Contour's hulls to increase convexity
                filtered_contours.append(utils.get_contour_convex_hull(contour))

        if self.DEBUG:
            debug_image = numpy.zeros(image.shape)
            for contour in filtered_contours:
                utils.draw_contours(debug_image, [contour])                
            path = self.create_debug_path("Comet shape filter")          
            utils.save_image(debug_image, path)

        return filtered_contours

    def __validate_comet(self, image, mask, contour):

        height, width = mask.shape
           
        # Comets are not partially small
        if utils.get_contour_area(contour) < self.COMET_MINIMUM_SIZE:          
            return False

        # Comets should be convex
        if utils.get_contour_convexity(contour) < self.COMET_MINIMUM_CONVEXITY_RATIO:
            return False

        # Comets shouldn't be higher than wider        
        if (height / width) > self.COMET_MAXIMUM_HEIGHT_WIDTH_RATIO:
            return False

        # Comets touching the edge of the image are filtered out
        if utils.is_contour_on_border(image, contour):
            return False

        # Head should be as centered as possible on the roi
        y_front_centroid = self.__get_front_centroid(mask)
        if self.__get_head_displacement_ratio(mask, y_front_centroid) > self.COMET_MAXIMUM_HEAD_DISPLACEMENT_RATIO:
            return False
 
        # Commets are kinda symmetric
        if self.__y_comet_symmetry(mask, y_front_centroid) > self.COMET_MAXIMUM_SYMMETRY_RATIO:
            return False

        return True

    def __get_head_displacement_ratio(self, mask, y_front_centroid):
        
        height, _ = mask.shape
        
        return numpy.abs(y_front_centroid - (height // 2)) / height

    def __get_front_centroid(self, mask):

        height, width = mask.shape 
       
        y_front_centroid = 0
        count = 0
        max_column = int(width * 0.1) + 1 

        row = 0
        while row < height:
            column = 0
            while column < max_column:
                if mask[row][column] != 0:
                    y_front_centroid += row
                    count += 1
                column += 1
            row += 1

        return y_front_centroid // count

    def __y_comet_symmetry(self, mask, y_front_centroid):

        height, width = mask.shape
        sum1, sum2 = 0, 0
        count = 0

        row = 0
        while row < height:
            column = 0
            while column < width:
                if mask[row][column] != 0:
                    if row < y_front_centroid: 
                        sum1 += 1
                    else:
                        sum2 += 1
                    count += 1
                column += 1
            row += 1

        return numpy.abs(sum2-sum1) / count


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Head segmentation                             ~ #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 


    def __head_segmentation(self, comet_contours, gs_image):

        comet_list = []
        # For each comet its head is segmented
        for comet_contour in comet_contours:

            # Initial status
            head_is_valid = True

            # Comet Mask & ROI
            comet_rect = utils.create_enclosing_rectangle(comet_contour)
            comet_mask = utils.create_contour_mask(comet_contour, gs_image, comet_rect)
            comet_roi = numpy.copy(gs_image[comet_rect[1]:comet_rect[1]+comet_rect[3], 
                                            comet_rect[0]:comet_rect[0]+comet_rect[2]])
            coordinates = numpy.where(comet_mask == 0)
            comet_roi[coordinates] = 0

            if self.DEBUG:
                path = self.create_debug_path("Head Segmentation  Comet Roi")          
                utils.save_image(utils.renormalize_image(comet_roi), path)
       
            # [1.1] First stage: comet brightest region         
            head_mask = self.__brightest_region_finding(comet_roi, comet_contour)
            head_mask = facade.closing(head_mask, self.BRIGHTEST_REGION_CLOSING_RADIUS)
            head_contours = utils.find_contours(head_mask)

            # [1.2] Find subwindow of brightest area
            boxes = []
            for contour in head_contours:
                (x, y, w, h) = utils.create_enclosing_rectangle(contour)
                boxes.append([x, y, x+w, y+h])

            boxes = numpy.asarray(boxes)
            left = numpy.min(boxes[:,0])
            top = numpy.min(boxes[:,1])
            head_width = numpy.max(boxes[:,2])
            head_height = numpy.max(boxes[:,3])
           
            if ((utils.get_contour_circularity(comet_contour) < 0.9) and
               (head_width > head_height*2)):
                    # head is too long: invalid
                    head_is_valid = False

            # [1.3] Head center of mass & radius        
            head_xc, _ = utils.get_contour_centroid(head_mask, True)
            head_yc = self.__get_front_centroid(comet_roi)
            head_radius = self.__get_head_height(head_mask, head_xc)

            # [1.4] Head gap
            head_gap = head_xc - head_radius
            if head_gap > 0:
                # head is at wrong place: invalid
                head_is_valid = False

            if self.DEBUG:
                debug_image = numpy.copy(self.original_image[comet_rect[1]:comet_rect[1]+comet_rect[3], 
                                                             comet_rect[0]:comet_rect[0]+comet_rect[2]])
                brightest_pixels = numpy.where(head_mask != 0)
                debug_image[brightest_pixels] = constants.GREEN
                debug_image[head_yc][head_xc] = constants.BLUE
                cv2.rectangle(debug_image, (left, top), (head_width, head_height), constants.YELLOW, 2)
                path = self.create_debug_path("Brightest Region  BLUE=Center of Mass  " + 
                                               "GREEN=Brightest pixels  YELLOW=Head Rect  " +
                                               "Head Gap=" + str(head_gap) + "  Status=" + str(head_is_valid))          
                utils.save_image(debug_image, path)
                
            # [2] Second stage: Intensity Profile
            # Ran if first approach is not viable
            if not head_is_valid:

                # [2.1] Get comet intensity profile               
                comet_profile = self.__intensity_profile(comet_roi)

                # [2.2] Head-Tail edge
                head_edge = self.__get_head_edge(comet_profile)

                if self.DEBUG:                   
                    # Comet profile
                    pyplot.plot(comet_profile)
                    pyplot.plot([head_edge, head_edge], [0, numpy.max(comet_profile)])
                    pyplot.ylabel("Avg Intensity") 
                    pyplot.savefig(self.create_debug_path("Comet Intensity Profile"))
                    pyplot.clf()
                    # Comet image
                    debug_image = numpy.copy(comet_roi)
                    debug_image[:, head_edge] = 1.
                    path = self.create_debug_path("Intensity Profile  Head-Comet Edge")          
                    utils.save_image(utils.renormalize_image(debug_image), path)
                
                head_radius = head_edge // 2
                head_xc = head_radius
                           
            # Prepare contours           
            head_mask = numpy.zeros(comet_mask.shape, dtype=numpy.uint8)
            utils.draw_circle(head_mask, (head_xc, head_yc), head_radius) 
            head_mask = cv2.bitwise_and(comet_mask, head_mask)
            head_contour = utils.find_contours(head_mask)[0] + (comet_rect[0], comet_rect[1])
            # Add comet to list
            comet_list.append((comet_contour, head_contour))
             
        return comet_list

    def __brightest_region_finding(self, roi, contour):

        n = utils.get_contour_area(contour) * 0.05
        threshold = 254
        binary_image = utils.to_binary_image(roi, threshold)
        # Umbralization is applied until 5% of the pixels which
        # intensity is greater than the threshold are found
        n_brightest = numpy.count_nonzero(binary_image)
        while threshold > 0 and n_brightest < n:
            binary_image = utils.to_binary_image(roi, threshold)                        
            n_brightest = numpy.count_nonzero(binary_image)
            threshold -= 1

        return binary_image
        
    def __get_head_height(self, head_mask, x_center):

        height, _ = head_mask.shape

        head_height = 0
        row = 0
        while row < height:
            if head_mask[row][x_center] > 0:
                head_height += 1
            row += 1

        return head_height
    
    def __intensity_profile(self, comet_roi):

        # Renormalize intensities values
        comet_roi = utils.renormalize_image(comet_roi)
        
        height, width = comet_roi.shape
        profile = numpy.zeros(width)

        x = 0
        while x < width:
            intensity_sum = 0
            count = 0
            y = 0
            while y < height:
                if comet_roi[y][x] != 0:
                    intensity_sum += comet_roi[y][x]
                    count += 1
                y += 1
            profile[x] = intensity_sum / count
            x += 1  

        return profile

    def __get_head_edge(self, comet_profile):

        # Kernels
        kernel_width = len(comet_profile) // 10
        smooth_kernel = numpy.ones(kernel_width)
        smooth_kernel /= kernel_width
        differential_kernel = numpy.array([-1., 1.])

        # Smooth comet profile
        y1 = cv2.filter2D(comet_profile, -1, smooth_kernel)
        # Differentiate comet profile
        y2 = cv2.filter2D(y1, -1, differential_kernel)
        # Smooth differential
        y3 = cv2.filter2D(y2, -1, smooth_kernel)
        # Differentiate again
        y4 = cv2.filter2D(y3, -1, differential_kernel)
        # Smooth again
        dd_comet_profile = cv2.filter2D(y4, -1, smooth_kernel)

        # Head-tail transition point
        transition_point = 0
        i = 0
        while (i < len(comet_profile)-1) and transition_point == 0:
            if (dd_comet_profile[i+1] > 0) and (dd_comet_profile[i] < 0):
                transition_point = i
            i += 1

        # Best transition point
        dd_max = 0
        i = transition_point
        while (i < len(comet_profile)-1) and dd_max == 0:
            if dd_comet_profile[i+1] <= dd_comet_profile[i] and dd_comet_profile[i-1] <= dd_comet_profile[i]:
                dd_max = i
            i += 1

        if dd_max == 0:
            dd_max = width

        return dd_max 


        
