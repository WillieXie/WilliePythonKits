#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Willie
# Created Date: 2020-12-25
# =============================================================================

"""
Create AprilTags of family Tag36h11 and render together.

This script is based on
`Github kalibr createTargetPDF.py <https://github.com/ethz-asl/kalibr/blob/master/aslam_cv/aslam_cameras_april/src/createTargetPDF.py>`_

The difference is that `createTargetPDF.py` uses Python2, And the 1st tag
render at left bottom, 36th tag render at right top.

The result will show on window and save to png file.

Note that another AprilTags project `Github apriltag-generation <https://github.com/AprilRobotics/apriltag-generation>`_
will generate another format of family Tag36h11

For example, rendering 36 AprilTags of family Tag36h11, each tag
has 120 pixels, interval between tags is 30 pixels, also render 100 pixels arrow

    python3 AprilTagsGenerator.py -x 6 -y 6 -s 120 -i 0.25 -a 100

Version: 1.0 2020-12-31 Finish rendering AprilTags of family Tag36h11.


"""

import math
import optparse
import tkinter as tk
from tkinter import Canvas
from tkinter.tix import Tk

from copy import deepcopy

from PIL import Image

# =============================================================================
# Imports
# =============================================================================
from cv_kits.april_tags.families.Tag36h11 import Tag36h11


def render_april_board(_canvas, _num_x, _num_y, _tag_size,
                       _tag_interval_ratio, _tag_family, _lt_x=0, _lt_y=0):
    """
    generate multi tags and render to canvas

    :param _canvas: target canvas
    :param _num_x: num of tags every row
    :param _num_y: num of tags every column
    :param _tag_size: every tag size in pixels
    :param _tag_interval_ratio: interval between tags in pixels
    :param _tag_family: every tag's shape is decided by tag_family
    :param _lt_x:
    :param _lt_y:
    :return:
    """
    _interval_size = _tag_interval_ratio * _tag_size
    for idx_y in range(_num_y):
        for idx_x in range(_num_x):
            _tag_id = idx_y * _num_x + idx_x
            _start_x = _lt_x + _interval_size + idx_x * (
                    1 + _tag_interval_ratio) * _tag_size
            _start_y = _lt_y + _interval_size + idx_y * (
                    1 + _tag_interval_ratio) * _tag_size
            render_single_april_tag(_canvas, _start_x, _start_y, _tag_size,
                                    _tag_interval_ratio, _tag_id, _tag_family)


def render_tag_border(_canvas, _start_x, _start_y, _tag_size, _border_size,
                      _type=0):
    """
    Render border of tag by `_type`
    `_type` decide outer half and inner half border color:

        0 - outer and inner both black
        1 - outer white, inner black
        2 - outer black, inner white

    :param _canvas:
    :param _start_x: left top x
    :param _start_y: left top y
    :param _tag_size: full tag size in pixels
    :param _border_size: border tag size in pixels
    :param _type: border type.
    :return:
    """
    _half_border_size = _border_size // 2
    _outer_color = 'black'
    _inner_color = 'black'
    if 1 == _type:  # classic layout
        _outer_color = 'white'
    elif 2 == _type:  # standard layout
        _inner_color = 'white'

    # Draw top border
    _lt_x = _start_x
    _lt_y = _start_y
    _rb_x = _lt_x + _tag_size
    _rb_y = _lt_y + _half_border_size
    _canvas.create_rectangle(_lt_x, _lt_y, _rb_x, _rb_y, fill=_outer_color,
                             outline="")
    _lt_x = _start_x + _half_border_size
    _lt_y = _start_y + _half_border_size
    _rb_x = _lt_x + _tag_size - _border_size
    _rb_y = _lt_y + _half_border_size
    _canvas.create_rectangle(_lt_x, _lt_y, _rb_x, _rb_y, fill=_inner_color,
                             outline="")

    # Draw bottom border
    _lt_x = _start_x
    _lt_y = _start_y + _tag_size - _half_border_size
    _rb_x = _lt_x + _tag_size
    _rb_y = _lt_y + _half_border_size
    _canvas.create_rectangle(_lt_x, _lt_y, _rb_x, _rb_y, fill=_outer_color,
                             outline="")
    _lt_x = _start_x + _half_border_size
    _lt_y = _start_y + _tag_size - _border_size
    _rb_x = _lt_x + _tag_size - _border_size
    _rb_y = _lt_y + _half_border_size
    _canvas.create_rectangle(_lt_x, _lt_y, _rb_x, _rb_y, fill=_inner_color,
                             outline="")

    # Draw left border
    _lt_x = _start_x
    _lt_y = _start_y
    _rb_x = _lt_x + _half_border_size
    _rb_y = _lt_y + _tag_size
    _canvas.create_rectangle(_lt_x, _lt_y, _rb_x, _rb_y, fill=_outer_color,
                             outline="")
    _lt_x = _start_x + _half_border_size
    _lt_y = _start_y + _half_border_size
    _rb_x = _lt_x + _half_border_size
    _rb_y = _lt_y + _tag_size - _border_size
    _canvas.create_rectangle(_lt_x, _lt_y, _rb_x, _rb_y, fill=_inner_color,
                             outline="")

    # Draw right border
    _lt_x = _start_x + _tag_size - _half_border_size
    _lt_y = _start_y
    _rb_x = _lt_x + _half_border_size
    _rb_y = _lt_y + _tag_size
    _canvas.create_rectangle(_lt_x, _lt_y, _rb_x, _rb_y, fill=_outer_color,
                             outline="")
    _lt_x = _start_x + _tag_size - _border_size
    _lt_y = _start_y + _half_border_size
    _rb_x = _lt_x + _half_border_size
    _rb_y = _lt_y + _tag_size - _border_size
    _canvas.create_rectangle(_lt_x, _lt_y, _rb_x, _rb_y, fill=_inner_color,
                             outline="")


def render_tag_data(_canvas, _start_x, _start_y, _tag_bits, _pixels_per_bit,
                    _tag_code):
    """
    Render tag by `_tag_code`

    Note:
    Rotate operation can be done with numpy:

        code_matrix = np.zeros((_tag_bits, _tag_bits))
        for i in range(0, _tag_bits):
            for j in range(0, _tag_bits):
                if not _tag_code & (1 << _tag_bits * i + j):
                    code_matrix[i, j] = 1
        # rotate matrix twice
        code_matrix = np.rot90(code_matrix, 2)

    :param _canvas:
    :param _start_x:
    :param _start_y:
    :param _tag_bits:
    :param _pixels_per_bit:
    :param _tag_code:
    :return:
    """
    _curr_array = [[0 for col in range(_tag_bits)] for row in range(_tag_bits)]
    for i in range(0, _tag_bits):
        for j in range(0, _tag_bits):
            if _tag_code & (1 << _tag_bits * i + j):
                _curr_array[i][j] = 1
    rotate_90(_curr_array, _tag_bits, _tag_bits)
    rotate_90(_curr_array, _tag_bits, _tag_bits)

    for i in range(0, _tag_bits):
        for j in range(0, _tag_bits):
            _lt_x = _start_x + j * _pixels_per_bit
            _lt_y = _start_y + i * _pixels_per_bit
            _rb_x = _lt_x + _pixels_per_bit
            _rb_y = _lt_y + _pixels_per_bit
            if _curr_array[i][j]:
                _canvas.create_rectangle(_lt_x, _lt_y, _rb_x, _rb_y,
                                         fill='white', outline="")
            else:
                _canvas.create_rectangle(_lt_x, _lt_y, _rb_x, _rb_y,
                                         fill='black', outline="")


def rotate_90(_data_array, _width, _height):
    """
    Rotate 2d array 90 on z axis (right hand)
    :param _data_array:
    :param _width:
    :param _height:
    :return:
    """
    _ori_array = deepcopy(_data_array)
    for rIdx in range(_height):
        for cIdx in range(_width):
            _data_array[_width - 1 - cIdx][rIdx] = _ori_array[rIdx][cIdx]


def render_single_april_tag(_canvas, _start_x, _start_y, _tag_size,
                            _tag_interval_ratio,
                            _tag_id, _tag_family, _symmetric_corners=True,
                            _tag_border_bits=2, _type=0):
    """
    Render single april tag with border

    :param _canvas:
    :param _start_x:
    :param _start_y:
    :param _tag_size:
    :param _tag_interval_ratio:
    :param _tag_id:
    :param _tag_family:
    :param _symmetric_corners:
    :param _tag_border_bits:
    :param _type: border type
    :return: None
    """
    _tag_code = _tag_family.tagCodes[_tag_id]
    _tag_bits = math.sqrt(_tag_family.area)
    _pixels_per_bit = _tag_size / (_tag_bits + _tag_border_bits * 2)
    _pixels_per_bit = int(_pixels_per_bit)
    _tag_bits = int(_tag_bits)
    _border_size = _tag_border_bits * _pixels_per_bit

    render_tag_border(_canvas, _start_x, _start_y, _tag_size, _border_size,
                      _type)
    render_tag_data(_canvas, _start_x + _border_size, _start_y + _border_size,
                    _tag_bits, _pixels_per_bit, _tag_code)

    if _symmetric_corners:
        corner_size = _tag_interval_ratio * _tag_size
        # Draw left top corner
        _lt_x = _start_x - corner_size
        _lt_y = _start_y - corner_size
        _rb_x = _lt_x + corner_size
        _rb_y = _lt_y + corner_size
        _canvas.create_rectangle(_lt_x, _lt_y, _rb_x, _rb_y, fill='black')
        # Draw left bottom corner
        _lt_x = _start_x - corner_size
        _lt_y = _start_y + _tag_size
        _rb_x = _lt_x + corner_size
        _rb_y = _lt_y + corner_size
        _canvas.create_rectangle(_lt_x, _lt_y, _rb_x, _rb_y, fill='black')
        # Draw right top corner
        _lt_x = _start_x + _tag_size
        _lt_y = _start_y - corner_size
        _rb_x = _lt_x + corner_size
        _rb_y = _lt_y + corner_size
        _canvas.create_rectangle(_lt_x, _lt_y, _rb_x, _rb_y, fill='black')
        # Draw right bottom corner
        _lt_x = _start_x + _tag_size
        _lt_y = _start_y + _tag_size
        _rb_x = _lt_x + corner_size
        _rb_y = _lt_y + corner_size
        _canvas.create_rectangle(_lt_x, _lt_y, _rb_x, _rb_y, fill='black')


def render_axis(_canvas, _start_x, _start_y, axis_len):
    """
    Render x and y axis, which can note first and last tag

    :param _canvas:
    :param _start_x:
    :param _start_y:
    :param axis_len:
    :return:
    """
    # Draw x axis
    _canvas.create_line(_start_x, _start_y, _start_x + axis_len, _start_y,
                        arrow=tk.LAST, width=3, fill='red')
    # Draw y axis
    _canvas.create_line(_start_x, _start_y, _start_x, _start_y + axis_len,
                        arrow=tk.LAST, width=3, fill='green')

    _canvas.create_text(_start_x + axis_len, _start_y, fill="darkblue",
                        font="Consolas 20 bold",
                        text="x")
    _canvas.create_text(_start_x, _start_y + axis_len, fill="darkblue",
                        font="Consolas 20 bold",
                        text="y")


if __name__ == "__main__":
    global_options = optparse.OptionParser(
        usage="Generate a PDF with a calibration pattern."
        , version="%prog 1.0")
    global_options.add_option('-t', '--type', action='store', type='string',
                              dest='grid_type', default='april_tag',
                              help='Grid pattern type. (\'april_tag\''
                                   ' or \'checkerboard\')')
    global_options.add_option('-x', '--nx', action='store', type='int',
                              dest='num_x', default=6,
                              help='Number of tags in x direction')
    global_options.add_option('-y', '--ny', action='store', type='int',
                              dest='num_y', default=6,
                              help='Number of tags in y direction')
    global_options.add_option('-s', '--size', action='store', type='float',
                              dest='tag_size', default=120,
                              help='Tag size in pixels')
    global_options.add_option('-i', '--interval', action='store', type='float',
                              dest='tag_interval', default=0.25,
                              help='Ratio of tag interval relative to tag size')
    global_options.add_option('-a', '--axis', action='store', type='int',
                              dest='axis_len', default=100,
                              help='Axis length in pixels.'
                                   'if length=0, skip rendering axis')

    (options, args) = global_options.parse_args()

    # if draw axis, canvas's size is `N * tag_size + (N+3) * space_size)`
    # else canvas's size is `N * tag_size + (N+1) * space_size)`
    total_width = options.num_x * options.tag_size + (
            options.num_x + 1) * options.tag_interval * options.tag_size
    total_height = options.num_y * options.tag_size + (
            options.num_y + 1) * options.tag_interval * options.tag_size
    tag_border_lt_x = 0
    tag_border_lt_y = 0
    if not options.axis_len == 0:
        tag_border_lt_x = options.tag_interval * options.tag_size
        tag_border_lt_y = options.tag_interval * options.tag_size
        total_width = int(total_width + 2 * tag_border_lt_x)
        total_height = int(total_height + 2 * tag_border_lt_x)
    print('type={} num_x={} num_y={} size={} interval={} canvasWidth={} '
          'canvasHeight={} tag_border_lt_x={} tag_border_lt_y={}'
          .format(options.grid_type, options.num_x, options.num_y,
                  options.tag_size, options.tag_interval, total_width,
                  total_height, tag_border_lt_x, tag_border_lt_y))

    tk_instance = Tk()
    canvas = Canvas(tk_instance, bg="white", width=total_width,
                    height=total_height)

    render_april_board(canvas, options.num_x, options.num_y, options.tag_size,
                       options.tag_interval, Tag36h11(), 2 * tag_border_lt_x,
                       2 * tag_border_lt_y)
    if not options.axis_len == 0:
        render_axis(canvas, tag_border_lt_x, tag_border_lt_y,
                    options.axis_len)

    canvas.pack()

    file_name = f'output/Tag36h11_{options.num_y}_{options.num_x}'
    ps_file_name = f'{file_name}.eps'
    png_file_name = f'{file_name}.png'

    # Note:
    #   1. Must call `update()` before `postscript()`
    #   2. Canvas operation must before `Tk.mainloop()`
    #   3. Default postscript will scale canvas to (0.7496, 0.7496)
    #      To avoid this, set `pagewidth` and `pageheight`
    canvas.update()
    canvas.postscript(file=ps_file_name, pagewidth=total_width,
                      pageheight=total_height)

    img = Image.open(ps_file_name)  # use PIL to convert to PNG
    # print('img.size={}'.format(img.size))
    # foo = img.resize((total_width, total_height), Image.ANTIALIAS)
    img.save(png_file_name, 'png')

    tk_instance.mainloop()
