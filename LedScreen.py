#!/usr/bin/python3

import numpy as np
from PIL import Image


def image_import(path, background_color=(255, 255, 255), height=16):
    """ Import an image from the given path and remove the ALPHA channel
    by using a static color background instead"""
    img = Image.open(path)
    img.load()  # required for png.split()

    # resize image
    width = int(float(img.size[0]) * height / float(img.size[1]))
    img = img.resize((width, height), Image.ANTIALIAS)

    if img.mode == "RGBA":
        # replace alpha channel with background color
        # in the case of (255, 255, 255) the leds will be shining bright,
        # if the leds should stay of use (0,0,0) as backgroundColor
        background = Image.new("RGB", img.size, background_color)
        background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
        return np.array(background)
    elif img.mode == "RGB":
        return np.array(img)
    else:
        img.convert("RGB")
        return np.array(img)


class LedScreen:
    def __init__(self, image_path, background=(255, 255, 255)):  # Parameter for function
        """ Create a LED screen from an image path.
        The image is created and transformed to the right size with the ImageImport class."""
        self.image_path = image_path
        self.background = np.asarray(background, dtype=np.uint8)
        self.image = image_import(image_path, background)  # get image (4x16)x16 wide
        self.image_height = len(self.image)
        self.image_width = len(self.image[0])
        # stack picture side by side to allow easier handling for get_image_part Function
        self.image = np.hstack([self.image, self.image])

    def get_image_part(self, offset):
        """ Gets the image to show the right part (right side from the picture) according to the offset """
        start = offset % self.image_width  # start position is offset modulo image width
        return self.image[:, start:start + 16]  # return every row, but only the columns between start and start+16

    def get(self, offset):
        """ Returns a list of LED screens according to the offset """
        result = list()
        result.append(self.get_image_part(offset))
        return result
