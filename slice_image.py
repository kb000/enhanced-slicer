"""
Extracts image regions.
"""

import os
import argparse
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

class Rect:
    """ Encapsulates the four coordinates that define a rectangle """
    def __init__(self, p1, p2, p3, p4):
        c_top = min(p1, p3)
        c_bot = max(p1, p3)
        c_left = min(p2, p4)
        c_right = max(p2, p4)
        self._coords = (c_top, c_left, c_bot, c_right)

    @property
    def coords(self):
        """ The coordinate tuple. """
        return self._coords

GREYLEVELS = 255

def enhanced_greyscale(img):
    """ Performs an ehhanced greyscale operation, using a regularized background. """
    # Use a background removal technique from
    #  http://stackoverflow.com/questions/4632174/what-processing-steps-should-i-use-to-clean-photos-of-line-drawings/4632685#4632685
    white = img.filter(ImageFilter.BLUR).filter(ImageFilter.MaxFilter(15))
    imgpix = np.array(img)
    whitepix = np.array(white)
    greypix = GREYLEVELS * np.max(imgpix / whitepix, axis=2)
    greyimg = Image.fromarray(greypix)
    return greyimg

def slice_image(csv_filename, image_filename, out_dir, out_height, out_width):
    """ Extracts segments from an image using coordinates from a csv. """
    image_filename = image_filename or os.path.splitext(csv_filename)[0]
    img_base, _ = os.path.splitext(image_filename)
    img_dir, img_base = os.path.split(img_base)
    out_dir = out_dir or img_dir
    with Image.open(image_filename) as img:
        greyimg = enhanced_greyscale(img)
        csv = np.genfromtxt(csv_filename, delimiter=",")
        for i in range(csv.shape[0]):
            if len(csv[i]) != 4:
                print("Error on line {}. Expected 4 points, got {}"
                      .format(i, len(csv[i])))
                continue
            rect = Rect(*csv[i])
            cropped = greyimg.crop(rect.coords)
            if (out_height is None) and (out_width is None):
                scaled = cropped
            else:
                out_height = out_height or cropped.height
                out_width = out_width or cropped.width
                scaled = cropped.resize((out_height, out_width), Image.LANCZOS)
            scaled.save(os.path.join(out_dir, "slice_{0}_{1:03d}{2}".format(img_base, i, ".gif")))


def arg_parser():
    """ Builds argument parser. """
    parser = argparse.ArgumentParser(description='Slice an image from points in a csv.')
    parser.add_argument('--slice-csv', dest='slice_csv',
                        help='Path to csv file.')
    parser.add_argument('--image', dest='image', default=None,
                        help='Path to image to slice. ' +
                        'Default will try to find a file from csv name.')
    parser.add_argument('--out-dir', dest='out_dir', default=None,
                        help='Path to output directory. ' +
                        'Defaults to image directory.')
    parser.add_argument('--out-height', dest='out_height', default=None, type=int,
                        help='Height to scale all output images. ' +
                        'Defaults to no scaling.')
    parser.add_argument('--out-width', dest='out_width', default=None, type=int,
                        help='Width to scale all output images. ' +
                        'Defaults to no scaling.')
    return parser

def main(FLAGS=None): # pylint: disable=invalid-name
    """ Main entry point for image slicer """
    assert FLAGS.slice_csv != None
    slice_image(FLAGS.slice_csv, FLAGS.image,
                FLAGS.out_dir, FLAGS.out_height, FLAGS.out_width)

#If you also want to do some basic processing like increasing the contrast,
# see the other functions in the ImageOps module, like autocontrast. They're all pretty easy to use,
# but if you get stuck, you can always ask a new question. For more complex enhancements, look around
# the rest of PIL. ImageEnhance can be used to sharpen an image, ImageFilter can do edge detection and
# unsharp masking; etc. You may also want to change the format to greyscale (L8), or even black and white
# (L1); that's all in the Image.convert method.


if __name__ == "__main__":
    main(arg_parser().parse_args())
