#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# usage: ./postparser.py "input"
# 
# if input has a recognized command and enough parameters it will lauch a shell script
# see command_switch for more details
#
# suikale 021121

import sys
import os
import re
import math

spi_send = "/usr/local/bin/spi_send " 
nums = []

# control wireless plugs, see spi_send for more info
def socket ():
    if len(nums) > 0:
        state = nums.pop()
        cli_cmd = spi_send + str(state)
        if len(nums) > 0:
            id = nums.pop()
            cli_cmd = cli_cmd + str(id)
        if len(nums) > 0:
            group = nums.pop()
            cli_cmd = cli_cmd + str(group)        
        os.system(cli_cmd)
def sockets():
    if len(nums) > 0:
        state = nums.pop()
        state = state + 2
        cli_cmd = spi_send + str(state)
        os.system(cli_cmd)
def ceiling_light():
    nums.insert(0, 0)
    socket()
def shelf_light():
    nums.insert(0, 1)
    socket()

# turn off tv display panel led
def tv():
    if len(nums) > 0:
        state = nums.pop()
        if state == 0:
            io = "Off"
        if state == 1:
            io = "On"
        cli_cmd = "ssh tv luna-send -n 1 luna://com.webos.service.tvpower/power/turn" + io + "Screen '{}'"
        os.system(cli_cmd)

# executes a function based on input
# keywords act as regular expressions
command_switch = {
# 'keyword' : function,
    'katto' : ceiling_light,
    'kasvi' : shelf_light,
    'kaikki': sockets,
    'lamput': sockets,
    'valot' : sockets,
    '^s$'     : socket,
    'valo'  : socket,
    'lamppu': socket,
    'tv'    : tv,
    'tele'  : tv,
}

# contains regular expressions for numbers 0 to 9. 
# change num_count if the comments are moved
# may break if (len(numlist) % num_count) != 0 
num_count = 4                                  
num_list = [ '0',     '1',    '2',    '3',      # '4',      '5',    '6',    '7',      '8',     '9', 
             'noll',  'yks',  'kaks', 'kolm',   # 'nelj',   'viis', 'kuus', 'seitse', 'kahde', 'yhdek',
             'yhtää', 'eka',  'toka', 'kolom',  # 'nelij',  'viie', 'kuue', 'seisk',  'kasi',  'ysi',
             'nada',  'ykkö', 'toin', 'kolkku'] # 'nelkku', 'vito', 'kuto', 'seitte', 'kahek', 'yheks', ] 

# contains words for states off/on
state_list = [ 'kiinni', 'päälle', 
               'pois',   'auki', 
               'off',    'on' ]

# contains words for recognized commands
word_list = list(command_switch.keys())

# checks if word matches a regular expression from a given list
# if mod > 0 returns int(index of the keyword % mod)
# else returns the keyword as string
def check_match(word, lst, empty, mod):
    for i in lst:
        r = re.compile('(?i)' + i)
        if r.match(word):
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
    # input sanitization must be handled by php
    input = sys.argv[1]
    input_words = input.split()

    # adds support for controlling sockets with s[command][id][group], eq. "s100" or "s1"
    if len(input_words) == 1 and input_words[0].startswith('s'):
        if re.match("(?i)^s[0-9]?[0-9]?[0-9]?$", input_words[0]):
            input_words = input_words[0]

    # parses the input
    # command -> cmd, numeric values and states -> nums
    hax = True
    cmd = ""
    for iw in input_words:
        c = check_match(iw, word_list, "", -1)
        if (len(c) > 0):
            cmd = c
            continue

        num = check_match(iw, num_list, -1, num_count)
        if (num >= 0):
            nums.append(num)
            continue
        
        state = check_match(iw, state_list, -1, 2)
        if (state >= 0):
            hax = False # fix for finnish grammar, "toinen valo päälle" etc
            nums.append(state)
            continue
    
    if hax: 
        nums.reverse() # fixes pop()
    if len(cmd) > 0:
        cmd = command_switch.get(cmd)
        cmd()