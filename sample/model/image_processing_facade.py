# -*- encoding: utf-8 -*-

'''
    The ImageProcessingFacade module. Facade module that uses OpenCV, 
    Scikit-image and Numpy to process images.
'''

# General imports
import os
import cv2
import numpy
import skimage.draw
import skimage.filters
import skimage.morphology

# Custom imports
import sample.model.constants as constants
import sample.model.utils as utils


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                               Histogram Methods                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

def get_histogram(image, mask=None):

    hist = cv2.calcHist([utils.renormalize_image(image)], [0], mask, 
                        [constants.LEVELS], [0, constants.LEVELS])
    # [ [x], [y], [z], ... ] -> [x, y, z, ...]
    return numpy.array([b[0] for b in hist])

def adjust_intensity(image, in_range, out_range):

    # Read parameters
    if in_range == []:
        imin, imax = image.min(), image.max()
    else:
        imin, imax = in_range[0], in_range[1]
    imin_norm, imax_norm = out_range[0], out_range[1]

    height, width = image.shape
    new_image = numpy.zeros(shape=(height, width)).astype(numpy.float32)

    row = 0
    while row < height:
        column = 0
        while column < width:
            numerator = (imax_norm - imin_norm) * (image[row][column] - imin)
            denominator = imax - imin
            new_image[row][column] = imin_norm + (numerator / denominator)
            column += 1
        row += 1

    return new_image


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                          Morphological & Filtering                          #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

def circular_median(image, radius=None):

    kernel = __get_circular_kernel(radius)
    return utils.normalize_image(skimage.filters.median(
               utils.renormalize_image(image), kernel))

def dilate(image, radius=None):

    kernel = __get_circular_kernel(radius)
    return cv2.dilate(image, kernel, iterations = 1)

def erode(image, radius=None):

    kernel = __get_circular_kernel(radius)  
    return cv2.erode(image, kernel, iterations = 1)

def elliptical_openning(image, radius_y, radius_x):

    kernel = __get_elliptical_kernel(radius_y, radius_x)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

def closing(image, radius=None):

    kernel = __get_circular_kernel(radius)
    return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)

def __get_circular_kernel(radius=None):
  
    if radius is None:
        radius = 5
    return skimage.morphology.disk(radius) 

def __get_elliptical_kernel(radius_y, radius_x):

    rr, cc = skimage.draw.ellipse(radius_y, radius_x, radius_y, radius_x)
    kernel = numpy.zeros((radius_y*2, radius_x*2), dtype=numpy.uint8)
    kernel[rr, cc] = constants.MAX_VALUE
    return kernel


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                 Thresholding                                #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

def otsu_threshold(image, mask=None):

    # https://docs.opencv.org/3.4.0/d7/d4d/tutorial_py_thresholding.html

    # Histogram retrieval
    histogram = get_histogram(image, mask)
           
    # Histogram is normalized as a probability distribution
    histogram_normalized = histogram / histogram.max()
    Q = histogram_normalized.cumsum()

    bins = numpy.arange(constants.LEVELS)
    fn_min = numpy.inf
    threshold = -1
    index = 1
    while index < constants.LEVELS:
        # Probabilities
        p1, p2 = numpy.hsplit(histogram_normalized, [index])
        # Cum sum of 'background' and 'object' classes 
        q1, q2 = Q[index], Q[constants.MAX_VALUE] - Q[index]
        # Weights
        b1, b2 = numpy.hsplit(bins, [index])
        # Finding means and variances
        if q1 > 0. and q2 > 0.:
            m1, m2 = numpy.sum(p1 * b1) / q1, numpy.sum(p2 * b2) / q2
            v1, v2 = ( numpy.sum(((b1 - m1) * (b1 - m1)) * p1) / 
                       q1, numpy.sum(((b2 - m2) * (b2 - m2)) * p2) / q2 )
            # Calculates the minimization function
            fn = v1*q1 + v2*q2
            if fn < fn_min:
                fn_min = fn
                threshold = index
        index += 1

    return threshold

def huang_threshold(image):
    
    '''
        Implements Huang's fuzzy thresholding method. Uses Shannon's entropy
        function (one can also use Yager's entropy function). 
        Huang L.-K. and Wang M.-J.J. (1995) "Image Thresholding by Minimizing  
        the Measures of Fuzziness" Pattern Recognition, 28(1): 41-51
    '''

    histogram = get_histogram(image)
        
    threshold = -1
    threshold_two = -1

    first_bin = 0
    while first_bin < len(histogram) and histogram[first_bin] == 0:
        first_bin += 1
 
    last_bin = constants.MAX_VALUE-1
    while last_bin > 0 and histogram[last_bin] == 0:
        last_bin -= 1

    term = 1.0 / (last_bin - first_bin)
    
    mu_0 = numpy.zeros(shape=(254, 1))
    num_pix = 0.0
    sum_pix = 0.0
    for ih in range(first_bin, 254):
        sum_pix = sum_pix + (ih * histogram[ih])
        num_pix = num_pix + histogram[ih]
        mu_0[ih] = sum_pix / num_pix # NUM_PIX cannot be zero !

    mu_1 = numpy.zeros(shape=(254, 1))
    num_pix = 0.0
    sum_pix = 0.0
    for ih in range(last_bin, 1, -1 ):
        sum_pix = sum_pix + (ih * histogram[ih])
        num_pix = num_pix + histogram[ih]

        mu_1[ih-1] = sum_pix / num_pix # NUM_PIX cannot be zero !

    min_ent = float("inf")
    min_ent_two = float("inf")
    for it in range(254): 
        ent = 0.0
        for ih in range(it):
            # Equation (4) in Reference
            mu_x = 1.0 / ( 1.0 + term * numpy.fabs( ih - mu_0[it]))
            if ( not ((mu_x  < 1e-06 ) or (mu_x > 0.999999))):

                # Equation (6) & (8) in Reference
                ent = ( ent + histogram[ih] * (-mu_x * numpy.log(mu_x) - 
                        (1.0 - mu_x) * numpy.log(1.0 - mu_x) ) )
          
        for ih in range(it + 1, 254):
            # Equation (4) in Ref. 1 */
            mu_x = 1.0 / (1.0 + term * numpy.fabs( ih - mu_1[it]))
            if ( not((mu_x  < 1e-06 ) or ( mu_x > 0.999999))):
                # Equation (6) & (8) i Reference
                ent = ( ent + histogram[ih] * (-mu_x * numpy.log(mu_x) - 
                        (1.0 - mu_x) * numpy.log(1.0 - mu_x) ) )             
 
        if (ent < min_ent):
            previous = min_ent
            previous_threshold = threshold
            min_ent = ent
            threshold = it
            if (previous < min_ent_two):
                min_ent_two = previous
                threshold_two = previous_threshold
        elif (ent < min_ent_two):
            min_ent_two = ent
            threshold_two = it

    if threshold == 0:
        return threshold_two
    return threshold

def triangle_threshold(image):
    
    flags = cv2.THRESH_BINARY | cv2.THRESH_TRIANGLE
    return cv2.threshold(utils.renormalize_image(image),
                         0,
                         constants.MAX_VALUE,
                         flags)



