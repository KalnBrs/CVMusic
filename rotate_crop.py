from image import Image
from functions import *
from statistics import median
from math import inf
from typing import Tuple, List, Optional, Dict, Any
import numpy as np
import cv2

def rotate_neck_picture(image):
    """
    Rotating the picture so that the neck of the guitar is horizontal. We use Hough transform to detect lines
    and calculating the slopes of all lines, we rotate it according to the median slope.
    Hopefully, most lines detected will be strings or neck lines so the median slope is the slope of the neck
    An image with lots of noise and different lines will result in poor results.
    :param image: an Image object
    :return rotated_neck_picture: an Image object rotated according to the angle of the median slope detected in param image
    """
    image_to_rotate = image.image

    edges = image.edges_sobely()
    edges = threshold(edges, 127)

    lines = image.lines_hough_transform(edges, 50, 50)  # TODO: Calibrate params automatically
    slopes = []
    
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                if x2 != x1:
                    slopes.append(abs((y2 - y1) / (x2 - x1)))

    angle = 0
    if slopes:
        median_slope = median(slopes)
        angle = median_slope * 45

    return Image(img=rotate(image_to_rotate, -angle))


def crop_neck_picture(image):
    """
    Cropping the picture so we only work on the region of interest (i.e. the neck)
    We're looking for a very dense region where we detect horizontal line
    Currently, we identify it by looking at parts where there are more than two lines at the same y (height)
    :param image: an Image object of the neck (rotated horizontally if necessary)
    :return cropped_neck_picture: an Image object cropped around the neck
    """
    image_to_crop = image.image

    edges = image.edges_sobely()
    edges = threshold(edges, 127)

    lines = image.lines_hough_transform(edges, 50, 50)  # TODO: Calibrate params automatically
    y = []

    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                y.append(y1)
                y.append(y2)

    if not y:
        return Image(img=image_to_crop)

    y_sort = list(sorted(y))
    y_differences = [0]

    first_y = 0
    last_y = inf

    for i in range(len(y_sort) - 1):
        y_differences.append(y_sort[i + 1] - y_sort[i])
    for i in range(len(y_differences) - 1):
        if y_differences[i] == 0:
            last_y = y_sort[i]
            if i > 3 and first_y == 0:
                first_y = y_sort[i]

    if last_y == inf:
        last_y = len(image_to_crop)
    
    # Safety checks
    top = max(0, first_y - 10)
    bottom = min(len(image_to_crop), last_y + 10)
    if bottom <= top:
        top = 0
        bottom = len(image_to_crop)
        
    return Image(img=image_to_crop[top:bottom])


def crop_neck_with_offset(rotated_image: Image) -> Tuple[np.ndarray, Tuple[int, int]]:
    """
    Crop neck region similar to crop_neck_picture but also return offset relative to rotated image.
    """
    image_to_crop = rotated_image.image
    height = len(image_to_crop)
    if height == 0:
        return image_to_crop, (0, 0)

    edges = rotated_image.edges_sobely()
    edges = threshold(edges, 127)

    lines = rotated_image.lines_hough_transform(edges, 50, 50)
    if lines is None:
        return image_to_crop, (0, 0)

    y_coords = []
    for line in lines:
        for _x1, y1, _x2, y2 in line:
            y_coords.append(y1)
            y_coords.append(y2)

    if not y_coords:
        return image_to_crop, (0, 0)

    y_sort = sorted(y_coords)
    y_diff = [0]
    first_y = 0
    last_y = height - 1

    for i in range(len(y_sort) - 1):
        y_diff.append(y_sort[i + 1] - y_sort[i])

    for i in range(len(y_diff) - 1):
        if y_diff[i] == 0:
            last_y = y_sort[i]
            if i > 3 and first_y == 0:
                first_y = y_sort[i]

    top = max(0, first_y - 10)
    bottom = min(height, last_y + 10)
    if bottom <= top:
        top = 0
        bottom = height

    cropped = image_to_crop[top:bottom].copy()
    return cropped, (0, top)


def resize_image(img):
    """
    Recursive function to resize image if definition is too elevated
    :param img: an image as defined in OpenCV
    :return: an image as defined in OpenCV
    """
    height = len(img)
    width = len(img[0])
    if height >= 1080 or width >= 1920:
        resized_image = cv2.resize(img, (int(width * 0.8), int(height * 0.8)))
        return resize_image(resized_image)
    else:
        return img


if __name__ == "__main__":
    print("Run rotate_crop_tests.py to have a look at results!")
