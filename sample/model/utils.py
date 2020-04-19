# -*- encoding: utf-8 -*-

'''
    The utils module.
'''

# PyObject imports
import gi
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf

# General imports
import os
import cv2
import numpy

# Custom imports
import sample.model.constants as constants



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                 I/O Methods                                 #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

def read_image(image_path: str, test_mode=False):

    if test_mode:
        image_path = os.path.join(constants.TEST_IMAGES_FOLDER_PATH, image_path)
    
    grayscale_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    original_image = cv2.imread(image_path, cv2.IMREAD_COLOR)    

    if grayscale_image is None or original_image is None:
        raise ValueError("ERROR: unable to read image " + image_path)

    return normalize_image(grayscale_image), original_image 

def display_image(image, window_name=None):
  
    if window_name is None:
        window_name = "template"

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1024, 1280)

    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def save_image(image, path):
    return cv2.imwrite(path, image)
    
    
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                   Images                                    #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

def normalize_image(image):
    return (image / (constants.MAX_VALUE)).astype(numpy.float64)

def renormalize_image(image):
    return (image * (constants.MAX_VALUE)).astype(numpy.uint8)
    
def flip_image_horizontally(image):
    return numpy.fliplr(image)

def invert_image(image):
    return (constants.MAX_VALUE) - image     

def to_binary_image(image, threshold):

    return cv2.threshold(renormalize_image(image),
                         threshold, 
                         constants.MAX_VALUE,
                         cv2.THRESH_BINARY
           )[1]
           
def to_gray_image(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 

def get_red_from_image(image):

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    left_lower_red = numpy.array([0, 100, 30])
    left_upper_red = numpy.array([10, 255, 255])
    right_lower_red = numpy.array([170, 100, 30])
    right_upper_red = numpy.array([180, 255, 255])

    left_mask = cv2.inRange(hsv_image, left_lower_red, left_upper_red)
    right_mask = cv2.inRange(hsv_image, right_lower_red, right_upper_red)
    mask = cv2.bitwise_or(left_mask, right_mask)
    return cv2.bitwise_and(image, image, mask=mask)

def image_to_pixbuf(image):

    image = image[...,[2, 1, 0]]
    height, width, channels = image.shape
    # Returning a copy is a must ... believe me
    return GdkPixbuf.Pixbuf.new_from_data(image.tostring(),
        GdkPixbuf.Colorspace.RGB, False, 8, width, height, width*channels).copy()

def compress_image(image):
    return cv2.imencode('.png', image)[1].tostring()

def decompress_image(data):
    return cv2.imdecode(numpy.fromstring(data, numpy.uint8), cv2.IMREAD_COLOR)

   
   
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                               Contours & Points                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

def find_contours(binary_image, retrieval_mode=None, aproximation_method=None):

    if retrieval_mode is None:
        retrieval_mode = cv2.RETR_TREE
    if aproximation_method is None:
        aproximation_method = cv2.CHAIN_APPROX_SIMPLE 

    # !! depending on the version, 2 or 3 arguments are returned.
    return cv2.findContours(renormalize_image(binary_image),
                            retrieval_mode,
                            aproximation_method
           )[0]

def draw_contours(image, contours, color=None, thickness=None):

    if color is None:
        color = constants.WHITE
    if thickness is None:
        thickness = cv2.FILLED

    cv2.drawContours(image, contours, -1, color, thickness)

def draw_circle(image, center, radius, color=None, thickness=None):

    if color is None:
        color = constants.WHITE
    if thickness is None:
        thickness = -1

    cv2.circle(image, center, radius, color, thickness)

def draw_ellipse(image, center, axes, angle, color=None, thickness=None, half=False):

    if color is None:
        color = constants.YELLOW
    if thickness is None:
        thickness = 1

    start_angle = 0
    if half:
        start_angle = 180

    cv2.ellipse(image, center, axes, angle, start_angle, 360, color, thickness)

def get_contour_area(contour):
    return cv2.contourArea(contour)

def get_contour_convexity(contour):

    try:
        return (get_contour_area(contour) / 
                get_contour_area(get_contour_convex_hull(contour)))
    except:
        return None
        
def get_contour_circularity(contour):

        contour_perimeter = get_contour_perimeter(contour)
        try:
            return (4.0 * numpy.pi * get_contour_area(contour) / 
                    contour_perimeter * contour_perimeter)
        except:
            return None

def get_contour_perimeter(contour):
        return cv2.arcLength(contour, True)

def get_contour_convex_hull(contour):
    return cv2.convexHull(contour, False)
    
def get_contour_rect_contour(contour):

    x, y, width, height = create_enclosing_rectangle(contour)
    p1, p2, p3, p4 = (x, y), (x, y + height), (x+width, y+height), (x+width, y)
    return numpy.array([[p1], [p2], [p3], [p4]])  

def get_contour_centroid(contour, binary=False):

    m = cv2.moments(contour, binaryImage=binary)
    x = int(m["m10"] / m["m00"])
    y = int(m["m01"] / m["m00"])   
    return (x, y)

def get_contour_leftmost_point(contour):
    return tuple(contour[contour[: ,: ,0].argmin()][0])

def get_contour_rightmost_point(contour):
    return tuple(contour[contour[:, :, 0].argmax()][0])

def get_contour_topmost_point(contour):
    return tuple(contour[contour[:, :, 1].argmin()][0])

def get_contour_bottonmost_point(contour):
    return tuple(contour[contour[:, :, 1].argmax()][0])    

def is_point_inside_contour(contour, point):
    # cv2.pointPolygonTest > 0 (inside), < 0 (outside), == 0 (on an edge)
    return (cv2.pointPolygonTest(contour, point, False) >= 0)

def is_contour_on_border(image, contour):

    height, width = image.shape
    for point in contour:
        if point[0][0] in (0, width-1) or point[0][1] in (0, height-1): 
            return True

def create_enclosing_rectangle(contour):
    return cv2.boundingRect(contour)

def create_contour_mask(contour, image, rec=None):

    if rec is None:
        x, y, width, height = create_enclosing_rectangle(contour)
    else:
        x, y, width, height = rec
    mask = numpy.zeros(image.shape, dtype=numpy.uint8)
    draw_contours(mask, [contour])
    return mask[y:y+height, x:x+width]

def create_expanded_contour_mask(contour, image, offset):

    image_height, image_width = image.shape
    x, y, width, height = create_enclosing_rectangle(contour)
            
    # Contour window boundaries are expanded
    y_offset = y-offset if y-offset >= 0 else y
    x_offset = x-offset if x-offset >= 0 else x
    expanded_height = height + (offset*2)
    expanded_height = expanded_height if expanded_height < image_height else height
    expanded_width = width + (offset*2)
    expanded_width = expanded_width if expanded_width < image_width else width
    rec = (x_offset, y_offset, expanded_width, expanded_height)
    return create_contour_mask(contour, image, rec), rec

def scale_canvas_contour_dict(canvas_contour_dict, scale_ratio):

    for (_, canvas_contour) in canvas_contour_dict.items():
        scale_canvas_contour(canvas_contour, scale_ratio)
            
def scale_canvas_contour(canvas_contour, scale_ratio):

    scale_delimiter_point_list(
        canvas_contour.get_delimiter_point_dict().values(),
        scale_ratio
    )        
        
def scale_delimiter_point_list(delimiter_point_list, scale_ratio):

    for delimiter_point in delimiter_point_list:
        delimiter_point.set_coordinates(
            scale_point(delimiter_point.get_coordinates(), scale_ratio))

def scale_point(coordinates, scale_ratio):
    return (coordinates[0] * scale_ratio,
            coordinates[1] * scale_ratio)

def scale_contour(contour, scale_ratio):

    new_coordinates = []

    coordinates = contour_to_list(contour)

    index = 0
    while index < len(coordinates):

        new_coordinates.append((coordinates[index][0] * scale_ratio,
                                coordinates[index][1] * scale_ratio)
                              )
        index += 1

    return list_to_contour(new_coordinates)

def contour_to_list(contour):

    list = []

    for point in contour:
        list.append([point[0][0], point[0][1]])

    return list

def list_to_contour(list):

    new_list = []
    for item in list:
        new_list.append([item])
    return get_contour_convex_hull(
               numpy.array(new_list, dtype=numpy.int32))

def flip_contour(contour, width):

    flipped_coordinates = []
    for coordinates in contour_to_list(contour):
        new_x = width-1-coordinates[0]
        flipped_coordinates.append((new_x, coordinates[1]))
    return list_to_contour(flipped_coordinates)

def merge_contours(contour1, contour2):
 
    return get_contour_convex_hull(
        list_to_contour(contour_to_list(contour1) + 
                        contour_to_list(contour2))
    )

def are_same_contours(image, contour1, contour2):

    x1, y1, width1, height1 = create_enclosing_rectangle(contour1)
    x2, y2, width2, height2 = create_enclosing_rectangle(contour2)
    
    if (x1 != x2) or (y1 != y2) or (width1 != width2) or (height1 != height2):
        return False
        
    mask_image = numpy.zeros(shape=(image.shape[:-1]))  
    mask_rect_image1 = numpy.copy(mask_image[y1:y1+height1, x1:x1+width1])
    mask_rect_image2 = numpy.copy(mask_image[y1:y1+height1, x1:x1+width1])
    
    draw_contours(mask_rect_image1, [contour1])
    draw_contours(mask_rect_image2, [contour2])
    
    if numpy.count_nonzero(mask_rect_image1) != numpy.count_nonzero(mask_rect_image2):
        return False
    
    # Pixel count == 0 -> True
    return (numpy.count_nonzero(mask_rect_image1 - mask_rect_image2) == 0)    
    
  

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                   Geometry                                  #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

def euclidean_distance(point1, point2):
    return numpy.sqrt(((point1[0]-point2[0]) * (point1[0]-point2[0])) + 
                      ((point1[1]-point2[1]) * (point1[1]-point2[1])))
