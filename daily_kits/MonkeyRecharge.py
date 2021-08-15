#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Willie
# Created Date: 2021-8-14
# =============================================================================
"""
Recharge multi times with this script by mock click and input event with
`pyautogui <https://github.com/asweigart/pyautogui>`_

Note that while script running, browser and your webpage must at foreground

There are two modes:
1. Collect mode. Gather the following coordinates:
      a. `python3 MonkeyRecharge -b`:
         browser's back button

      b. `python3 MonkeyRecharge -a':
         Amount input box

      c. `python3 MonkeyRecharge -c':
         Confirm button

   The result is saved in coordinates.txt

2. Recharge mode. Recharge steps are:
      a. Input recharge amount.
      b. Input password.
      c. Click recharge button.
      d. Click browser back button after recharge is complete and jumped into next page.

   Must input password. Recharge amount and times are optional.

   Command is:

      python3 MonkeyRecharge -p xxxxxx

Use:

   `python3 MonkeyRecharge -h`

   to learn other commands

"""
import sys
import time
import optparse
import os
import pyautogui
import random

# Sampling coordinates delay
global_sampling_delay = 5
global_commit_wait = 8
global_back_wait = 3

global_coordinates_file_name = 'coordinates.txt'
global_type_amount = 'amount'
global_type_back = 'back'
global_type_confirm = 'confirm'
global_coordinates_x_dict = {}
global_coordinates_y_dict = {}
global_payment_password = ''
global_recharge_amount = '0.1'
global_recharge_times = 2

global_options = optparse.OptionParser(
    usage="MonkeyRecharge COMMAND [ARGS]"
    , version="%prog 1.0")
global_options.add_option('-a', '--amount', action='store_true', dest='record_amount_xy', default=False,
                          help='record input amount xy')
global_options.add_option('-b', '--back', action='store_true', dest='record_go_back_xy', default=False,
                          help='record browser go back button xy')
global_options.add_option('-c', '--confirm', action='store_true', dest='record_confirm_xy', default=False,
                          help='record confirm button xy')
global_options.add_option('-d', '--delete', action='store_true', dest='delete_coordinates', default=False,
                          help=f'Delete file {global_coordinates_file_name}')
global_options.add_option('-p', '--password', action='store', type='string',
                          dest='payment_password', default='',
                          help='Payment password. **MUST Input everytime**')
global_options.add_option('-m', '--money', action='store', type='string',
                          dest='recharge_amount', default=global_recharge_amount,
                          help=f"Largest recharge amount. Really recharge amount is a random number under it. Default is {global_recharge_amount}")
global_options.add_option('-t', '--times', action='store', type='string',
                          dest='recharge_times', default=str(global_recharge_times),
                          help=f'Recharge times. Default is {global_recharge_times}')
global_options.add_option('-w', '--wait', action='store', type='string',
                          dest='wait_seconds', default=str(global_commit_wait),
                          help=f'Waiting seconds after click confirm button. Default is {global_commit_wait}')


def record_coordinates_to_file(x, y, typename, mode):
    """
    Record button coordinates into file {global_coordinates_file_name}.
    every line's format is:
    type x y

    :param x: x coordinate
    :param y: y coordinate
    :param typename: coordinate type name
    :param mode: "a" is append, "w" is write over
    :return: None
    """
    with open(global_coordinates_file_name, mode) as fp:
        fp.write(f'{typename} {x} {y}\n')


def load_coordinates_from_file():
    """
    Load button coordinates on browser from file {global_coordinates_file_name}
    :return: 0 if no error
    """
    if not os.path.isfile(global_coordinates_file_name):
        print(f'Failed for {global_coordinates_file_name} not exist. Create it firstly.\n\nExit...')
        sys.exit(1)

    print(f"{global_coordinates_file_name}'s content:\n")
    with open(global_coordinates_file_name, "r") as fp:
        lines = fp.readlines()
        for line in lines:
            line = line.strip()
            if line:
                data_array = line.split(' ')
                global_coordinates_x_dict[data_array[0]] = int(data_array[1])
                global_coordinates_y_dict[data_array[0]] = int(data_array[2])
                print(f'    {data_array[0]} = [{data_array[1]}, {data_array[2]}]')
        return 0
    return 1


if __name__ == '__main__':
    print('Mission Start\n')
    (options, args) = global_options.parse_args()
    if options.delete_coordinates:  # Record coordinates of recharge amount and verify by click
        print(f"delete {global_coordinates_file_name}")
        if os.path.isfile(global_coordinates_file_name):
            os.remove(global_coordinates_file_name)
            print(f'delete {global_coordinates_file_name} done')
        else:
            print(f'file {global_coordinates_file_name} not exist')
        sys.exit(0)

    if options.record_amount_xy:  # Record coordinates of recharge amount and verify by click
        print(f"Now record input amount coordinates in {global_sampling_delay} seconds")
        time.sleep(global_sampling_delay)
        mouse_x, mouse_y = pyautogui.position()
        print(f"Record input amount button done: [{mouse_x}, {mouse_y}]. Saved into {global_coordinates_file_name}")
        record_coordinates_to_file(mouse_x, mouse_y, global_type_amount, 'a')
        print('Now test this coordinate by click')
        pyautogui.click(mouse_x, mouse_y)
        print('Capture done')
        sys.exit(0)
    if options.record_go_back_xy:  # Record coordinates of browser's back button and verify by click
        print(f"Now record browser's back button coordinates in {global_sampling_delay} seconds")
        time.sleep(global_sampling_delay)
        mouse_x, mouse_y = pyautogui.position()
        print(f"Record browser's back button done: [{mouse_x}, {mouse_y}]. Saved into {global_coordinates_file_name}")
        record_coordinates_to_file(mouse_x, mouse_y, global_type_back, 'a')
        print('Now test this coordinate by click')
        pyautogui.click(mouse_x, mouse_y)
        sys.exit(0)
    if options.record_confirm_xy:  # Record coordinates of confirm button and verify by click
        print(f"Now record confirm button coordinates in {global_sampling_delay} seconds")
        time.sleep(global_sampling_delay)
        mouse_x, mouse_y = pyautogui.position()
        print(f"Record confirm button done: [{mouse_x}, {mouse_y}]. Saved into {global_coordinates_file_name}")
        record_coordinates_to_file(mouse_x, mouse_y, global_type_confirm, 'a')
        print('Now test this coordinate by click')
        pyautogui.click(mouse_x, mouse_y)
        print('Capture done')
        sys.exit(0)

    load_coordinates_from_file()

    if (options.payment_password is None) or (options.payment_password == ""):
        print(f'Failed for not setting password. Input with `-p xxx`.\n\nExit...')
        sys.exit(1)
    else:
        global_payment_password = options.payment_password

    global_recharge_amount = options.recharge_amount
    global_recharge_times = int(options.recharge_times)
    global_commit_wait = int(options.wait_seconds)
    global_back_wait = int(global_commit_wait * 0.4)
    print(
        f'\nRecharge max amount={global_recharge_amount}; Total recharge times={global_recharge_times}; Wait seconds=({global_commit_wait}/{global_back_wait})\n\nStart recharge')
    max_random_amount = int(float(global_recharge_amount) / 0.01)
    str_amount = global_recharge_amount
    random_amount = 0.01

    total_recharge = 0
    input_amount_x = global_coordinates_x_dict[global_type_amount]
    input_amount_y = global_coordinates_y_dict[global_type_amount]
    go_back_x = global_coordinates_x_dict[global_type_back]
    go_back_y = global_coordinates_y_dict[global_type_back]
    confirm_x = global_coordinates_x_dict[global_type_confirm]
    confirm_y = global_coordinates_y_dict[global_type_confirm]
    tic = time.perf_counter()
    for idx in range(global_recharge_times):
        random_amount = random.randint(1, max_random_amount) * 0.01
        str_amount = str(random_amount)

        if idx % 10 == 9:
            toc = time.perf_counter()
            print(f"\nProgram has been running for {toc - tic:0.4f} seconds\n")

        print(f'({idx + 1}/{global_recharge_times}) recharge start, amount={str_amount}')
        pyautogui.click(input_amount_x, input_amount_y)
        # Use Ctrl+A & Delete to clear amount
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('delete')
        pyautogui.write(str_amount, interval=0.05)
        pyautogui.press('tab')
        pyautogui.write(global_payment_password, interval=0.05)
        pyautogui.click(confirm_x, confirm_y)
        time.sleep(global_commit_wait)
        pyautogui.click(go_back_x, go_back_y)
        total_recharge += random_amount
        print(f'({idx + 1}/{global_recharge_times}) recharge done. Total recharged: {total_recharge:.2f}')
        time.sleep(global_back_wait)

    toc = time.perf_counter()
    print(f'\nMission Complete. Total elapsed {toc - tic:0.4f} seconds')
    sys.exit(0)
