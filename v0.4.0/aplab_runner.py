#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Version: 0.4.0-alpha

Written by Lars Frogner
'''

import tkinter as tk
import numpy as np
import aplab_common as apc
from aplab_common import C, ErrorWindow, Catcher
from aplab_tool_manager import ToolManager

tk.CallWrapper = Catcher

startup_success = True # Set to false if an error occurs while reading camera data
startup_error = ''     # Error message to show
no_cdefault = False    # Set to true if there is no default camera
no_tdefault = False    # Set to true if there is no default telescope

# Try to read camera data and store in lists

try:
    file1 = open('cameradata.txt', 'r')
    
except IOError:

    startup_success = False
    startup_error = 'Could not find "cameradata.txt".'
    
try:
    file2 = open('telescopedata.txt', 'r')
    
except IOError:

    startup_success = False
    startup_error = 'Could not find "telescopedata.txt".'

if startup_success:
    
    lines1 = file1.read().split('\n')
    file1.close()
    
    lines2 = file2.read().split('\n')
    file2.close()

    for line in lines1[1:-1]:

        line = line.split(',')
        
        try:
        
            C.CNAME.append(line[0])
            C.TYPE.append(line[1])
            
            if not (line[1] == 'DSLR' or line[1] == 'CCD'):
            
                startup_success = False
                startup_error = 'Invalid camera type for camera model:\n"{}". '.format(C.CNAME[-1]) \
                                + 'Must be "DSLR" or "CCD".'
                break
                
            if len(line) != (12 if line[1] == "DSLR" else 11): raise IndexError
            
            C.GAIN.append(apc.itpData(line[2], 'float'))
            C.RN.append(apc.itpData(line[3], 'float'))
            C.SAT_CAP.append(apc.itpData(line[4], 'int'))
            C.BLACK_LEVEL.append(apc.itpData(line[5], 'int'))
            C.WHITE_LEVEL.append(apc.itpData(line[6], 'int'))
            C.QE.append([('NA' if line[7] == 'NA' else float(line[7].split('*')[0])),
                        (1 if '*' in line[7] else 0)])
            C.PIXEL_SIZE.append([float(line[8].split('*')[0]), (1 if '*' in line[8] else 0)])
            C.RES_X.append([int(line[9].split('*')[0]), (1 if '*' in line[9] else 0)])
            C.RES_Y.append([int(line[10].split('*')[0]), (1 if '*' in line[10] else 0)])
            C.ISO.append(np.array(line[11].split('-')).astype(int) if line[1] == 'DSLR' else [0])
            
            if line[1] == 'DSLR':
            
                if len(C.GAIN[-1][0]) != len(C.ISO[-1]):
                
                    startup_success = False
                    startup_error = 'Non-matching number of gain and C.ISO values\nfor ' \
                                    + 'camera model: "{}".'.format(C.CNAME[-1])
                    break
                    
                elif len(C.RN[-1][0]) != len(C.ISO[-1]):
                
                    startup_success = False
                    startup_error = 'Non-matching number of read noise and C.ISO values\nfor ' \
                                    + 'camera model: "{}".'.format(C.CNAME[-1])
                    break
                    
            if len(C.SAT_CAP[-1][0]) != len(C.GAIN[-1][0]):
            
                startup_success = False
                startup_error = 'Non-matching number of saturation capacity and\ngain values for ' \
                                + 'camera model: "{}".'.format(C.CNAME[-1])
                break
                
            if len(C.WHITE_LEVEL[-1][0]) != len(C.GAIN[-1][0]):
            
                startup_success = False
                startup_error = 'Non-matching number of white level and gain\nvalues for ' \
                                + 'camera model: "{}".'.format(C.CNAME[-1])
                break
            
        except IndexError:
        
            startup_success = False
            startup_error = 'Invalid data configuration in\nline %d in "cameradata.txt".' \
                            .format(len(C.CNAME) + 1)
            break
            
        except (TypeError, ValueError):
        
            startup_success = False
            startup_error = 'Invalid data type detected for camera model:\n"{}".'.format(C.CNAME[-1])
            break
            
    for line in lines2[1:-1]:
    
        line = line.split(',')
        
        try:
            C.TNAME.append(line[0])
            
            if len(line) != 3: raise IndexError
            
            C.FOCAL_LENGTH.append([float(line[1].split('*')[0]), (1 if '*' in line[1] else 0)])
            C.APERTURE.append([float(line[2].split('*')[0]), (1 if '*' in line[2] else 0)])
            
        except IndexError:
        
            startup_success = False
            startup_error = 'Invalid data configuration in\nline %d in "telescopedata.txt".' \
                            % (len(C.TNAME) + 1)
            break
            
        except (TypeError, ValueError):
        
            startup_success = False
            startup_error = 'Invalid data type detected for telescope model:\n"{}".'.format(C.TNAME[-1])
            break
         
# Get name of default camera model and default tooltip state
            
if startup_success:
    
    try:
        definfo = (lines1[-1].split('Camera: ')[1]).split(', Tooltips: ')
        definfo2 = definfo[1].split(', Fontsize: ')
        
        CDEFAULT = definfo[0]
        C.TT_STATE = definfo2[0]
        FS = definfo2[1]
        if FS != 'auto': FS = int(FS)
        
        if CDEFAULT == 'none':
        
            no_cdefault = True
        
        elif not CDEFAULT in C.CNAME:
        
            startup_success = False
            startup_error = 'Invalid default camera name. Must\nbe the name of a camera in the list.'
            
        if not (C.TT_STATE == 'on' or C.TT_STATE == 'off'):
            
            startup_success = False
            startup_error = 'Invalid default tooltip state.\nMust be "on" or "off".'
            
    except IndexError:
    
        startup_success = False
        startup_error = 'Invalid last line in "cameradata.txt". Must be\n"Camera: <camera name>, ' \
                        + 'Tooltips: <on/off>, Fontsize: <integer>".'
        
    except ValueError:
    
        startup_success = False
        startup_error = 'Invalid font size. Must be an integer.'
   
# Get name of default telescope model
   
if startup_success:
    
    try:
        TDEFAULT = lines2[-1].split('Telescope: ')[1]
        
        if TDEFAULT == 'none':
        
            no_tdefault = True
        
        elif not TDEFAULT in C.TNAME:
        
            startup_success = False
            startup_error = 'Invalid default telescope name. Must\nbe the name of a telescope in the list.'
            
    except IndexError:
    
        startup_success = False
        startup_error = 'Invalid last line in "telescope.txt". Must be\n"Telescope: <telescope name>".'
    
# Run application, or show error message if an error occurred
    
if startup_success:
    app = ToolManager(None if no_cdefault else C.CNAME.index(CDEFAULT),
                      None if no_tdefault else C.TNAME.index(TDEFAULT), FS)
    app.mainloop()
else:
    error = ErrorWindow(startup_error)
    error.mainloop()