#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# usage: ./main.py "input"
# 
# if input has a recognized command and enough parameters it will lauch a shell script
# see command_switch for more details
#
# suikale 021121

import sys
import os
import re
nums = []

### user defined functions
spi_send = "/usr/local/bin/spi_send "

# control wireless plugs, see spi_send for details
def socket():
    if len(nums) > 0:
        state = nums.pop()
        cli_cmd = spi_send + str(state)
        if len(nums) > 0:
            id = nums.pop()
            cli_cmd = cli_cmd + str(id)
        if len(nums) > 0:
            group = nums.pop()
            cli_cmd = cli_cmd + str(group)        
        print(cli_cmd)
        #os.system(cli_cmd)
def sockets():
    if len(nums) > 0:
        state = nums.pop()
        state = int(state) + 2
        if 2 <= state and state <= 3:
            nums.insert(3, state)
            socket()
def set_socket(id, group):
    if len(nums) > 0:
        state = nums.pop()
        if 0 <= state and state <= 1:
            nums.insert(0, group)
            nums.insert(1, id)
            nums.insert(2, state)
            socket()
def ceiling_light():
    set_socket(0, 0)
def shelf_light():
    set_socket(1, 0)
def coffee():
    set_socket(2, 0)

# turn off tv display panel led
# TODO: add ssh keys to host
def tv():
    if len(nums) > 0:
        state = nums.pop()
        if state < 0 or 3 < state:
            return
        if state == 0 or state == 2:
            io = "Off"
        if state == 1 or state == 3:
            io = "On"
        cli_cmd = "ssh tv luna-send -n 1 luna://com.webos.service.tvpower/power/turn" + io + "Screen '{}'"
        print(cli_cmd)
        #os.system(cli_cmd)

# executes a function based on input
# keywords act as regular expressions
command_switch = {
# 'keyword' : function,
    '^s[0-9]?[0-9]?[0-9]?$' : socket,
    'tel[e]?([k]{2}|vis){1}' : tv,
    'kah[a]?vi' : coffee,
    'katto' : ceiling_light,
    'kasvi' : shelf_light,
    'kaikki': sockets,
    'valot' : sockets,
    'lamput': sockets,
    'valo'  : socket,
    'lamppu': socket,
    'tv'    : tv,
}

# contains regular expressions for numbers 0 to 9. 
# change num_count if the comments are moved
# may break if (len(numlist) % num_count) != 0 
num_count = 4                                   # expendable to reassonable limits as long as all fields have a unique value
num_list = [ '0',     '1',    '2',    '3',      # '4',      '5',    '6',    '7',      '8',     '9', 
             'noll',  'yks',  'kaks', 'kolm',   # 'nelj',   'viis', 'kuus', 'seitse', 'kahde', 'yhdek',
             'yhtää', 'eka',  'toka', 'kolom',  # 'nelij',  'viie', 'kuue', 'seisk',  'kasi',  'ysi',
             'nada',  'ykkö', 'toin', 'kolkku'] # 'nelkku', 'vito', 'kuto', 'seitte', 'kahek', 'yheks', ] 

# contains words for states off/on
state_count = 2
state_list = [ 'kiinni', 'päälle', 
               'pois',   'auki', 
               'off',    'on' ]

# contains words for recognized commands
word_list = list(command_switch.keys())

# checks if word matches a regular expression from a given list
# if mod > 0 returns int(index of the keyword % mod)
# else returns the keyword as string
def check_match(word, lst, empty, mod = 0):
    for i in lst:
        if re.compile('(?i)' + i).match(word):
            if (mod > 0):
                return lst.index(i) % mod
            else: 
                return i
    return empty

if __name__ == '__main__':
    if len(sys.argv) < 2:
        # no input
        exit()

    # php calls for ./main.py "input"
    # so only argv[1] matters    
    # input sanitization must be done by php
    input = sys.argv[1]
    input_words = input.split()

    # adds support for controlling sockets with s[command][id][group], eq. "s100" or "s1"
    if len(input_words) == 1 and input_words[0].startswith('s'):
        if re.match("(?i)^s[0-9]?[0-9]?[0-9]?$", input_words[0]):
            input_words = input_words[0]

    # parses the input
    # command -> cmd, numeric values -> nums, state -> state
    cmd = ""
    state = ""
    for iw in input_words:
        c = check_match(iw, word_list, "")
        if (len(c) > 0):
            cmd = c
            continue

        num = check_match(iw, num_list, -1, num_count)
        if (num >= 0):
            nums.append(num)
            continue
        
        st = check_match(iw, state_list, -1, state_count)
        if (st >= 0):
            state = st
            continue
    
    if len(cmd) > 0:
        nums.reverse() # fixes pop()
        if len(str(state)) > 0:
            nums.append(state)
        command_switch.get(cmd)()