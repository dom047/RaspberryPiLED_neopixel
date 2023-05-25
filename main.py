#!/usr/bin/env python3

# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
# Source: https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage

# Imports as described in the source
import time
import board
import neopixel
import numpy as np

# Specific imports
import LedScreen

# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18

# The number of NeoPixels for one display
num_pixels = (16 * 16)
# For four displays

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB


def transform_to_strip_layout(arr, has_dead_pixels=False):
    """Convert to pixels array to the layout of the strip"""
    # array([[ 1,  2,  3,  4],
    #        [ 5,  6,  7,  8],
    #        [ 9, 10, 11, 12],
    #        [13, 14, 15, 16]])

    # rotate array by 90 degrees
    arr = np.rot90(arr, 1, (1, 0))

    # array([[13,  9,  5,  1],
    #        [14, 10,  6,  2],
    #        [15, 11,  7,  3],
    #        [16, 12,  8,  4]])

    # flip left to right if start is not from left
    arr = np.fliplr(arr)

    # array([[ 1,  5,  9, 13],
    #        [ 2,  6, 10, 14],
    #        [ 3,  7, 11, 15],
    #        [ 4,  8, 12, 16]])

    # flip every second row
    flipped = np.fliplr(arr)  # copy array, but in reverse order

    # flipped: array([[13,  9,  5,  1],
    #                 [14, 10,  6,  2],
    #                 [15, 11,  7,  3],
    #                 [16, 12,  8,  4]])

    arr[::2] = flipped[::2]  # every second row is the second row of the flipped array

    # array([[13,  9,  5,  1],
    #        [ 2,  6, 10, 14],
    #        [15, 11,  7,  3],
    #        [ 4,  8, 12, 16]])

    # add inactive leds
    if has_dead_pixels:
        # add 0 pixels to rows (axis 0), 1 before and after on columns (axis 1), and 0 colors values (axis 3)
        arr = np.pad(arr, ((0, 0), (1, 1), (0, 0)), mode='constant', constant_values=0)

    return arr


def set_color(pixels, color, wait_ms=50):
    """Set color across display at once or the pixels will be the same color"""
    for i in range(len(pixels)):
        pixels[i] = color
    pixels.show()
    time.sleep(wait_ms / 1000.0)


def loop_logo(pixels, screen_leds, duration, offset_change=8, wait_ms=50):
    """ 
    The image circles the cube.
    Duration: How long the animation runs
    Offset_change: By how many pixels should the image move on each iteration
    Wait_ms: Time between the leds refreshes (e.g. refresh rate)
    """
    offset = 0  # position of the image
    start_time = time.time()  # number in seconds
    while duration > time.time() - start_time:  # loops until the duration elapsed
        write_to_strip(pixels, screen_leds, offset)
        offset = offset + offset_change  # every loop offset is increased by 8
        time.sleep(wait_ms / 1000.0)  # waits 50ms, /1000 converts to seconds


def pulsate_logo(pixels, screen_leds, duration, wait_ms=50, brightness_change=10, offset=0):
    """ 
    The image pulsates (increases and decreases brightness)
    Duration: How long the animation runs
    Wait_ms: Time between the leds refreshes (e.g. refresh rate)
    Brightness_change: Change of brightness per tick
    Offset: The left start position of the picture
    """
    brightness = 255  # start with max brightness
    direction = -1  # therefore, we want to decrease the brightness. Minus = direction
    start_time = time.time()
    while duration > time.time() - start_time:
        brightness = brightness + brightness_change * direction  # direction: brightness_change will be changes to minus
        if brightness > 255:  # checks for cases when brightness exceeds max value and reverses direction
            brightness = 255
            direction = -1
        if brightness < 0:  # checks for cases when brightness exceeds min value and reverses direction
            brightness = 0
            direction = 1

        write_to_strip(pixels, screen_leds, offset)
        time.sleep(wait_ms / 1000.0)


def write_to_strip(pixels, screen_leds, offset=0):
    # Get the screens from the leds module
    leds = screen_leds.get(offset)

    # First screen 16x18
    screen_pixels = transform_to_strip_layout(leds[0], True)  # True adds the two dead screen_pixels
    for i, row in screen_pixels:  # rows
        for j, pixel in row:  # columns
            # get the position of the LED, by calculating with the current row and column indexes
            position = i * len(row) + j
            # get the color by saved values from the array
            color = (pixel[0], pixel[1], pixel[2])
            pixels[position] = color


# Main program logic follows:
# Start the program /main program
if __name__ == '__main__':
    # Create NeoPixel object with appropriate configuration. / copied from source
    strip = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1, auto_write=False, pixel_order=ORDER)

    # Inform the user: To quit the program in cmd
    print('Press Ctrl-C to quit.')
    # Errors occurs: reacts to keyboard interrupt
    try:
        # Read logos from files, must be in same directory as python file
        loopLogoLeds = LedScreen.LedScreen("steelseries.jpg")
        pulsateLogoLeds = LedScreen.LedScreen("SOLA-logo.png")

        # Endless loop, needs keyboard interrupt. Prints to cmd
        while True:
            print('Loop logo for 20 seconds.')
            loop_logo(strip, loopLogoLeds, duration=20)
            set_color(strip, (0, 0, 0), 250)  # turn off leds between transitions

            print('Pulsate logo for 10 seconds.')
            pulsate_logo(strip, pulsateLogoLeds, duration=10, wait_ms=10, brightness_change=10)
            set_color(strip, (0, 0, 0), 250)  # turn off leds between transitions

    #  If a keyboard interrupt is being input the following will be executed. The strip will be turned off.
    except KeyboardInterrupt:
        set_color(strip, (0, 0, 0), 10)
