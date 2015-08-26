'''
Version: 0.2.1-alpha

Written by Lars Frogner
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import packages
import Tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import ttk
import matplotlib
import FileDialog # Needed for matplotlib
import win32api
import tkFont
import tkFileDialog
from PIL import Image, ImageTk
import sys
import os
import subprocess
import pyfits
import re
import exifread
import traceback
import datetime
import textwrap

matplotlib.use("TkAgg") # Use TkAgg backend
matplotlib.rc('font', family='Tahoma') # Set plot font

class APLab(tk.Tk):

    def __init__(self, cnum, tnum, fs):
    
        '''Initialize application.'''
    
        tk.Tk.__init__(self) # Run parent constructor
        
        self.container = ttk.Frame(self) # Define main frame
        
        self.cnum = cnum # Index if camera in camera data lists. None if no camera is selected.
        self.tnum = tnum
        self.toolsConfigured = False # True if the non-"Image Analyser" classes are initialized
        
        self.title('Astrophotography Lab 0.2.1') # Set window title
        
        self.addIcon(self) # Add window icon if it exists
        
        if fs == 'auto':
        
            fs = 8 # Smallest font size

            # Adjust font size according to horizontal screen resolution
            if sw >= 1024:
                if sw >= 1280:
                    if sw >= 1440:
                        if sw >= 1920:
                            fs = 12
                        else:
                            fs = 11
                    else:
                        fs = 10
                else:
                    fs = 9
        
        # Set font sizes
        self.tt_fs = fs - 1
        self.small_fs = fs
        self.medium_fs = fs + 1
        self.large_fs = fs + 2

        # Define fonts
        self.small_font = tkFont.Font(root=self, family='Tahoma', size=self.small_fs)
        self.smallbold_font = tkFont.Font(root=self, family='Tahoma', size=self.small_fs, weight='bold')
        self.medium_font = tkFont.Font(root=self, family='Tahoma', size=self.medium_fs, weight='bold')
        self.large_font = tkFont.Font(root=self, family='Tahoma', size=self.large_fs, weight='bold')
        
        # Configure widget styles
        style = ttk.Style(None)
        style.configure('TLabel', font=self.small_font, background=DEFAULT_BG)
        style.configure('file.TLabel', font=self.small_font, background='white')
        style.configure('leftselectedfile.TLabel', font=self.small_font, background='royalblue')
        style.configure('rightselectedfile.TLabel', font=self.small_font, background='crimson')
        style.configure('leftrightselectedfile.TLabel', font=self.small_font, background='forestgreen')
        style.configure('TButton', font=self.small_font, background=DEFAULT_BG)
        style.configure('TFrame', background=DEFAULT_BG)
        style.configure('files.TFrame', background='white')
        style.configure('TMenubutton', font=self.small_font, background=DEFAULT_BG)
        style.configure('TRadiobutton', font=self.small_font, background=DEFAULT_BG)
        
        self.container.pack(side='top', fill='both', expand=True) # Pack main frame
        
        # Make rows and columns expand with window
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Define attributes to keep track of active page
        self.calMode = tk.IntVar()
        self.simMode = tk.IntVar()
        self.plMode = tk.IntVar()
        self.anMode = tk.IntVar()
        
        self.calMode.set(0)
        self.simMode.set(0)
        self.plMode.set(0)
        self.anMode.set(1)
        
        # Define attributes to keep track of camera end telescope name
        self.varCamName = tk.StringVar()
        self.varTelName = tk.StringVar()
        
        self.varFLMod = tk.StringVar() # Displayed focal length modifier string
        
        # Set default values
        self.varCamName.set('Camera:')
        self.varTelName.set('Telescope:')
        
        self.varFLMod.set('Focal length modifier: 1x')
        
        self.FLModVal = 1.0 # Focal length modifier value
        
        self.avgWL = 555.0 # Assumed average wavelength for electron flux-luminance conversion
        self.TLoss = 0.1   # Assumed transmission loss of optical train
        
        # Define attributes to keep track of current flux unit
        self.lumSignalType = tk.IntVar()
        self.electronSignalType = tk.IntVar()
        
        # Define attributes to keep track of current DR unit
        self.stopsDRUnit = tk.IntVar()
        self.dBDRUnit = tk.IntVar()
        
        # Define attributes to keep track of current angle unit
        self.degAngleUnit = tk.IntVar()
        self.dmsAngleUnit = tk.IntVar()
        
        # Set default angle unit
        self.dmsAngleUnit.set(1)
        self.degAngleUnit.set(0)
        
        # Define attributes to keep track of tooltip states
        self.tooltipsOn = tk.IntVar()
        self.tooltipsOn.set(1 if TT_STATE == 'on' else 0)
        
        self.defaultTTState = tk.IntVar()
        self.defaultTTState.set(1 if TT_STATE == 'on' else 0)
        
        # Setup window menu
        self.menubar = tk.Menu(self)
        
        # "Tool" menu
        menuTool = tk.Menu(self.menubar, tearoff=0)
        menuTool.add_checkbutton(label='Image Analyser', variable=self.anMode,
                                 command=self.enterAnFrame)
        menuTool.add_checkbutton(label='Image Calculator', variable=self.calMode,
                                 command=self.enterCalFrame)
        menuTool.add_checkbutton(label='Image Simulator', variable=self.simMode,
                                 command=self.enterSimFrame)
        menuTool.add_checkbutton(label='Plotting Tool', variable=self.plMode,
                                 command=self.enterPlotFrame)
        
        self.menubar.add_cascade(label='Tool', menu=menuTool)
        
        # "File" menu
        self.menuFile = tk.Menu(self.menubar, tearoff=0)
        self.menuFile.add_command(label='Save image data', command=self.saveData)
        self.menuFile.add_command(label='Load image data', command=self.loadData)
        self.menuFile.add_command(label='Manage image data', command=self.manageData)
        
        self.menubar.add_cascade(label='File', menu=self.menuFile)
        
        # "Settings" menu
        self.menuSettings = tk.Menu(self.menubar, tearoff=0)
        
        # "Camera" submenu of "Settings"
        self.menuCamera = tk.Menu(self.menubar, tearoff=0)
        self.menuCamera.add_command(label='Change camera', command=self.changeCamera)
        self.menuCamera.add_command(label='Modify camera parameters', command=self.modifyCamParams)
        
        self.menuSettings.add_cascade(label='Camera', menu=self.menuCamera)
        
        # "Telescope" submenu of "Settings"
        self.menuTelescope = tk.Menu(self.menubar, tearoff=0)
        self.menuTelescope.add_command(label='Change telescope', command=self.changeTelescope)
        self.menuTelescope.add_command(label='Modify telescope parameters', command=self.modifyTelParams)
        
        self.menuSettings.add_cascade(label='Telescope', menu=self.menuTelescope)
        
        # Add FL modifier command
        self.menuSettings.add_command(label='Change FL modifier', command=self.changeFLMod)
        
        self.menuSettings.add_separator()
        
        # "Signal quantity" submenu of "Settings"
        menuSignalType = tk.Menu(self.menubar, tearoff=0)
        menuSignalType.add_checkbutton(label='Luminance', variable=self.lumSignalType,
                                     command=self.setLumSignalType)
        menuSignalType.add_checkbutton(label='Electron flux', variable=self.electronSignalType,
                                     command=self.setElectronSignalType)
        
        self.menuSettings.add_cascade(label='Signal quantity', menu=menuSignalType)
        
        # "Dynamic range unit" submenu of "Settings"
        menuDRUnit = tk.Menu(self.menubar, tearoff=0)
        menuDRUnit.add_checkbutton(label='stops', variable=self.stopsDRUnit,
                                   command=self.setStopsDRUnit)
        menuDRUnit.add_checkbutton(label='dB', variable=self.dBDRUnit,
                                   command=self.setdBDRUnit)
        
        self.menuSettings.add_cascade(label='Dynamic range unit', menu=menuDRUnit)
        
        # "Angle unit" submenu of "Settings"
        menuAngleUnit = tk.Menu(self.menubar, tearoff=0)
        menuAngleUnit.add_checkbutton(label='deg/arcmin/arcsec', variable=self.dmsAngleUnit,
                                      command=self.setDMSAngleUnit)
        menuAngleUnit.add_checkbutton(label='degrees', variable=self.degAngleUnit,
                                      command=self.setDegAngleUnit)
        
        self.menuSettings.add_cascade(label='Angle unit', menu=menuAngleUnit)
        
        self.menuSettings.add_separator()
        
        # "Tooltips" submenu of "Settings"
        self.menuTT = tk.Menu(self.menubar, tearoff=0)
        self.menuTT.add_command(label='Toggle tooltips', command=self.toggleTooltips)
        if self.tooltipsOn.get():
            self.menuTT.add_command(label='Turn off as default', command=self.toogleDefaultTTState)
        else:
            self.menuTT.add_command(label='Turn on as default', command=self.toogleDefaultTTState)
            
        self.menuSettings.add_cascade(label='Tooltips', menu=self.menuTT)
        
        # Add font size command
        self.menuSettings.add_command(label='Change font size', command=self.changeFS)
        
        self.menubar.add_cascade(label='Settings', menu=self.menuSettings)
        
        # Show menubar
        self.config(menu=self.menubar)
        
        # Some menu items are disabled on startup
        self.menubar.entryconfig(2, state='disabled')
        
        # Dictionary to hold all frames
        self.frames = {}
        
        # Initialize Message Window class
        frameMsg = MessageWindow(self.container, self)
        self.frames[MessageWindow] = frameMsg
        frameMsg.grid(row=0, column=0, sticky='NSEW')
        
        # Initialize Image Analyser class
        frameAn = ImageAnalyser(self.container, self)
        self.frames[ImageAnalyser] = frameAn
        frameAn.grid(row=0, column=0, sticky='NSEW')
        
        # Resize and recenter window
        setupWindow(self, *AN_WINDOW_SIZE)
        
        # If no camera is active
        if self.cnum is None:
            
            # Run camera selection method
            if not self.changeCamera():
                self.destroy()
                return None
                
        else:
            self.isDSLR = TYPE[self.cnum] == 'DSLR'  # Set new camera type
            self.hasQE = QE[self.cnum][0] != 'NA'    # Set new QE state
            self.noData = GAIN[self.cnum][0][0] == 0 # Determine if camera data exists
            
            self.varCamName.set('Camera: ' + CNAME[self.cnum])
            
            # Show relevant camera type widgets
            if self.isDSLR:
                frameAn.radioCCDm.grid_forget()
                frameAn.radioCCDc.grid_forget()
                frameAn.labelDSLR.grid(row=0, column=0, columnspan=2, sticky='EW')
            else:
                frameAn.labelDSLR.grid_forget()
                frameAn.varCCDType.set('mono')
                frameAn.radioCCDm.grid(row=0, column=0)
                frameAn.radioCCDc.grid(row=0, column=1)
                
        # If no telescope is active
        if self.tnum is None:
            
            # Run camera selection method
            if not self.changeTelescope():
                self.destroy()
                return None
                
        else:
        
            self.varTelName.set('Telescope: ' + TNAME[self.tnum])
        
        # Image scale for the selected camera-telescope combination
        self.ISVal = np.arctan2(PIXEL_SIZE[self.cnum][0]*1e-3,
                                FOCAL_LENGTH[self.tnum][0]*self.FLModVal)*180*3600/np.pi
        
        # Set default flux unit
        self.lumSignalType.set(self.hasQE)
        self.electronSignalType.set(not self.hasQE)
        
        # Set default DR unit
        self.stopsDRUnit.set(1)
        self.dBDRUnit.set(0)
        
        # Setup frames and add to dictionary
        frameCal = ImageCalculator(self.container, self)
        frameSim = ImageSimulator(self.container, self)
        framePlot = PlottingTool(self.container, self)
        
        self.frames[ImageCalculator] = frameCal
        self.frames[ImageSimulator] = frameSim
        self.frames[PlottingTool] = framePlot
        
        frameCal.grid(row=0, column=0, sticky='NSEW')
        frameSim.grid(row=0, column=0, sticky='NSEW')
        framePlot.grid(row=0, column=0, sticky='NSEW')
        
        self.toolsConfigured = True
        
        # Show start page
        self.showFrame(ImageAnalyser)
        
        self.focus_force()
        
    def showFrame(self, page):
    
        '''Shows the given frame.'''
        
        self.frames[page].tkraise()
  
    def enterPlotFrame(self):
    
        '''Shows the Plotting Tool frame.'''
    
        # Do nothing if already in plotting frame
        if not self.calMode.get() and not self.simMode.get() and not self.anMode.get():
            self.plMode.set(1) # Keep state from changing
            return None
            
        if self.noData:
            self.frames[MessageWindow].varHeaderLabel.set('Plotting Tool')
            self.showFrame(MessageWindow)
        else:
            self.frames[PlottingTool].varMessageLabel.set('') # Clear message label
            self.showFrame(PlottingTool) # Show plot frame
        
        # Close simulation window if it is open
        try:
            self.frames[ImageSimulator].topCanvas.destroy()
        except:
            pass
        
        # Resize and recenter window
        setupWindow(self, *PLOT_WINDOW_SIZE)
        
        # Configure menu items
        self.menubar.entryconfig(2, state='normal')
        self.menuFile.entryconfig(0, state='disabled')
               
        self.plMode.set(1)
        self.calMode.set(0)
        self.simMode.set(0)
        self.anMode.set(0)
        
    def enterCalFrame(self):
    
        '''Shows the Image Calculator frame.'''
        
        # Do nothing if already in calculator frame
        if not self.simMode.get() and not self.plMode.get() and not self.anMode.get():
            self.calMode.set(1) # Keep state from changing
            return None
                
        if self.noData:
            self.frames[MessageWindow].varHeaderLabel.set('Image Calculator')
            self.showFrame(MessageWindow)
        else:
            self.frames[ImageCalculator].varMessageLabel.set('') # Clear message label
            self.showFrame(ImageCalculator) # Show calculator frame
        
        # Close simulation window if it is open
        try:
            self.frames[ImageSimulator].topCanvas.destroy()
        except:
            pass
        
        # Resize and recenter window
        setupWindow(self, *CAL_WINDOW_SIZE)
        
        # Configure menu items
        self.menubar.entryconfig(2, state='normal')
        self.menuFile.entryconfig(0, state='normal')
            
        self.calMode.set(1)
        self.simMode.set(0)
        self.plMode.set(0)
        self.anMode.set(0)
        
    def enterSimFrame(self):
    
        '''Shows the Image Simulator frame.'''
        
        # Do nothing if already in simulator frame
        if not self.calMode.get() and not self.plMode.get() and not self.anMode.get():
            self.simMode.set(1) # Keep state from changing
            return None
        
        if self.noData:
            self.frames[MessageWindow].varHeaderLabel.set('Image Simulator')
            self.showFrame(MessageWindow)
        else:
            self.frames[ImageSimulator].varMessageLabel.set('') # Clear message label
            self.showFrame(ImageSimulator) # Show simulator frame
        
        # Resize and recenter window
        setupWindow(self, *SIM_WINDOW_SIZE)
        
        # Configure menu items
        self.menubar.entryconfig(2, state='normal')
        self.menuFile.entryconfig(0, state='disabled')
            
        self.calMode.set(0)
        self.simMode.set(1)
        self.plMode.set(0)
        self.anMode.set(0)
    
    def enterAnFrame(self):
    
        '''Shows the Image Analyser frame.'''
    
        # Do nothing if already in Analyser frame
        if not self.calMode.get() and not self.simMode.get() and not self.plMode.get():
            self.anMode.set(1) # Keep state from changing
            return None
            
        self.frames[ImageAnalyser].varMessageLabel.set('') # Clear message label
        self.showFrame(ImageAnalyser)
        
        # Close simulation window if it is open
        try:
            self.frames[ImageSimulator].topCanvas.destroy()
        except:
            pass
        
        # Resize and recenter window
        setupWindow(self, *AN_WINDOW_SIZE)
        
        # Configure menu items
        self.menubar.entryconfig(2, state='disabled')
        
        self.calMode.set(0)
        self.simMode.set(0)
        self.plMode.set(0)
        self.anMode.set(1)
    
    def saveData(self):
    
        '''Creates window with options for saving image data.'''
    
        frame = self.frames[ImageCalculator]
        
        # Show error if no image data is calculated
        if not frame.dataCalculated:
        
            frame.varMessageLabel.set('Image data must be calculated before saving.')
            self.menubar.entryconfig(1, state='normal')
            self.menubar.entryconfig(2, state='normal')
            self.menubar.entryconfig(3, state='normal')
            self.menubar.entryconfig(4, state='normal')
            return None
            
        self.menubar.entryconfig(1, state='disabled')
        self.menubar.entryconfig(2, state='disabled')
        self.menubar.entryconfig(3, state='disabled')
        self.menubar.entryconfig(4, state='disabled')
    
        self.varKeywords = tk.StringVar()
        self.varSaveError = tk.StringVar()
    
        # Construct saving window on top
        self.topSave = tk.Toplevel()
        self.topSave.title('Save image data')
        self.addIcon(self.topSave)
        setupWindow(self.topSave, 300, 145)
        
        labelSave = tk.Label(self.topSave, text='Input image keywords\n(target, location, date etc.)',
                             font=self.small_font)
        entryKeywords = ttk.Entry(self.topSave, textvariable=self.varKeywords, font=self.small_font,
                                  background=DEFAULT_BG, width=35)
        buttonSave = ttk.Button(self.topSave, text='Save', command=self.executeSave)
        labelSaveError = ttk.Label(self.topSave, textvariable=self.varSaveError)
        
        labelSave.pack(side='top', pady=10*scsy, expand=True)
        entryKeywords.pack(side='top', pady=5*scsy, expand=True)
        buttonSave.pack(side='top', pady=6*scsy, expand=True)
        labelSaveError.pack(side='top', expand=True)
        
        entryKeywords.focus()
        
        self.wait_window(self.topSave)
        try:
            self.menubar.entryconfig(1, state='normal')
            self.menubar.entryconfig(2, state='normal')
            self.menubar.entryconfig(3, state='normal')
            self.menubar.entryconfig(4, state='normal')
        except:
            pass
        
    def executeSave(self):
    
        '''Saves image data to text file.'''
    
        keywords = self.varKeywords.get() # Get user inputted keyword string
        
        if not ',' in keywords and keywords != '':
        
            self.topSave.destroy() # Close window
            
            # Append image data to the text file
            
            file = open('imagedata.txt', 'a')
            
            frame = self.frames[ImageCalculator]
                
            file.write('%s,%s,%d,%d,%g,%d,%g,%g,%g,%g,%d,%.3f,%.3f,%.3f\n' % (CNAME[self.cnum],
                                                                              keywords,
                                                                              frame.gain_idx,
                                                                              frame.rn_idx,
                                                                              frame.exposure,
                                                                              frame.use_dark,
                                                                              frame.dark_input,
                                                                              frame.bgn,
                                                                              frame.bgl,
                                                                              frame.target,
                                                                              self.hasQE,
                                                                              frame.df,
                                             (convSig(frame.sf, True) if self.hasQE else frame.sf),
                                             (convSig(frame.tf, True) if self.hasQE else frame.tf)))
            
            file.close()
            
            frame.varMessageLabel.set('Image data saved.')
        
        # Show error message if the keyword contains a ","
        elif ',' in keywords:
        
            self.varSaveError.set('The keyword cannot contain a ",".')
        
        # Show error message if user hasn't inputted a save keyword
        else:
        
            self.varSaveError.set('Please insert a keyword.')
            
    def loadData(self):
    
        '''Creates a window with options for loading image data, and reads the image data file.'''
    
        self.varLoadData = tk.StringVar()
        frame = self.currentFrame()
    
        data = []     # Holds image data
        names = []    # Holds camera name
        keywords = [] # Holds save ID
    
        # Show error message if image data file doesn't exist
        try:
            file = open('imagedata.txt', 'r')
        except IOError:
            frame.varMessageLabel.set('No image data to load.')
            self.menubar.entryconfig(1, state='normal')
            self.menubar.entryconfig(2, state='normal')
            self.menubar.entryconfig(3, state='normal')
            self.menubar.entryconfig(4, state='normal')
            return None
            
        self.menubar.entryconfig(1, state='disabled')
        self.menubar.entryconfig(2, state='disabled')
        self.menubar.entryconfig(3, state='disabled')
        self.menubar.entryconfig(4, state='disabled')
        
        # Read file
        lines = file.read().split('\n')
        file.close()
        
        # Show error message if image data file is empty
        if len(lines) == 1:
            
            frame.varMessageLabel.set('No image data to load.')
            self.menubar.entryconfig(1, state='normal')
            self.menubar.entryconfig(2, state='normal')
            self.menubar.entryconfig(3, state='normal')
            self.menubar.entryconfig(4, state='normal')
            return None
        
        # Get image data from file and store in lists
        for line in lines[:-1]:
            
            elements = line.split(',')
            name = elements[0]
            keyword = elements[1]
            names.append(name)
            keywords.append(keyword + ' (' + name + ')')
            data.append(elements[2:])
    
        self.varLoadData.set(keywords[0])
        
        # Create loading window on top
        self.topLoad = tk.Toplevel()
        self.topLoad.title('Load image data')
        setupWindow(self.topLoad, 300, 135)
        self.addIcon(self.topLoad)
        self.topLoad.focus_force()
        
        labelLoad = ttk.Label(self.topLoad, text='Choose image data to load:', anchor='center')
        optionLoad = ttk.OptionMenu(self.topLoad, self.varLoadData, None, *keywords)
        buttonLoad = ttk.Button(self.topLoad, text='Load',
                                command=lambda: self.executeLoad(names, keywords, data))
        
        labelLoad.pack(side='top', pady=10*scsy, expand=True)
        optionLoad.pack(side='top', pady=6*scsy, expand=True)
        buttonLoad.pack(side='top', pady=14*scsy, expand=True)
        
        self.wait_window(self.topLoad)
        try:
            self.menubar.entryconfig(1, state='normal')
            self.menubar.entryconfig(2, state='normal')
            self.menubar.entryconfig(3, state='normal')
            self.menubar.entryconfig(4, state='normal')
        except:
            pass
        
    def executeLoad(self, names, keywords, datalist):
    
        '''Gets relevant loaded data and inserts to relevant widgets.'''
    
        frame = self.currentFrame()
    
        datanum = keywords.index(self.varLoadData.get()) # Index of data to load
        
        name = names[datanum]    # Camera name for selected save
        data = datalist[datanum] # Data from selected save
       
        # If image data is from the same camera model
        if name == CNAME[self.cnum]:
        
            # If Image Calculator is the active frame
            if self.calMode.get():
            
                # Set loaded data in calculator frame
                frame.gain_idx = int(data[0])
                frame.rn_idx = int(data[1])
                frame.varISO.set(ISO[self.cnum][frame.gain_idx])
                frame.varGain.set(GAIN[self.cnum][0][frame.gain_idx])
                frame.varRN.set(RN[self.cnum][0][frame.rn_idx])
                frame.varExp.set(data[2])
                frame.varUseDark.set(int(data[3]))
                frame.varDark.set(data[4] if int(data[3]) else '')
                frame.varBGN.set(data[5] if self.isDSLR else '')
                frame.varBGL.set(data[6])
                frame.varTarget.set(data[7] if float(data[7]) > 0 else '')
                
                frame.dataCalculated = False # Previously calculated data is no longer valid
                frame.toggleDarkInputMode() # Change to the dark input mode that was used for the data
                frame.updateSensorLabels() # Update sensor info labels in case the ISO has changed
                frame.emptyInfoLabels() # Clear other info labels
                frame.varMessageLabel.set('Image data loaded.')
        
            # If Image Simulator is the active frame
            elif self.simMode.get():
                
                # Set loaded data in simulator frame
                frame.gain_idx = int(data[0])
                frame.rn_idx = int(data[1])
                frame.varISO.set(ISO[self.cnum][frame.gain_idx])
                frame.varGain.set(GAIN[self.cnum][0][frame.gain_idx])
                frame.varRN.set(RN[self.cnum][0][frame.rn_idx])
                frame.varExp.set(data[2])
                frame.varDF.set(data[9] if float(data[9]) > 0 else 0)
                frame.varSF.set(data[10])
                frame.varTF.set(data[11] if float(data[11]) > 0 else 0)
                frame.varSubs.set(1)
            
                if int(data[8]):
                    self.setLumSignalType()
                else:
                    self.setElectronSignalType()
            
                frame.dataCalculated = False # Previously calculated data is no longer valid
                frame.updateSensorLabels() # Update sensor info labels in case the ISO has changed
                frame.emptyInfoLabels() # Clear other info labels
                frame.varMessageLabel.set('Image data loaded.' if int(data[3]) else \
                'Note: loaded signal data does not contain a separate value for dark current.')
            
            # If Plotting Tool is the active frame
            else:
                
                # Set loaded data in plot frame
                frame.gain_idx = int(data[0])
                frame.rn_idx = int(data[1])
                frame.varISO.set(ISO[self.cnum][frame.gain_idx])
                frame.varGain.set(GAIN[self.cnum][0][frame.gain_idx])
                frame.varRN.set(RN[self.cnum][0][frame.rn_idx])
                frame.varExp.set(data[2])
                frame.varDF.set(data[9] if float(data[9]) > 0 else 0)
                frame.varSF.set(data[10])
                frame.varTF.set(data[11] if float(data[11]) > 0 else 0)
            
                if int(data[8]):
                    self.setLumSignalType()
                else:
                    self.setElectronSignalType()
                
                frame.ax.cla() # Clear plot
                frame.varMessageLabel.set('Image data loaded.' if int(data[3]) else \
                'Note: loaded signal data does not contain a separate value for dark current.')
        
        # If image data is from another camera model:
        # If Image Simulator or Plotting Tool is the active frame
        elif (not self.calMode.get()) and int(data[8]) and self.hasQE:
        
            # Set signal data
            frame.varSF.set(data[10])
            frame.varTF.set(data[11])
            
            self.setLumSignalType()
        
            if self.simMode.get():
                frame.dataCalculated = False # Previously calculated data is no longer valid
                frame.emptyInfoLabels() # Clear info labels
            else:
                frame.ax.cla() # Clear plot
            frame.varMessageLabel.set('Signal data loaded.')
        
        # If Image Calculator is the active frame
        else:
            
            frame.varMessageLabel.set('Image data is from another camera model. No data loaded.')
            
        self.topLoad.destroy() # Close loading window
    
    def manageData(self):
    
        '''Creates a window with options for renaming saves or deleting saved data.'''
    
        self.varManageData = tk.StringVar()
        
        frame = self.currentFrame()
        
        data = []             # Holds image data
        names = []            # Holds camera name
        keywords = []         # Holds save keyword
        display_keywords = [] # Holds save name to display
    
        # Show error message if data file doesn't exist
        try:
            file = open('imagedata.txt', 'r')
        except IOError:
            frame.varMessageLabel.set('No image data to manage.')
            self.menubar.entryconfig(1, state='normal')
            self.menubar.entryconfig(2, state='normal')
            self.menubar.entryconfig(3, state='normal')
            self.menubar.entryconfig(4, state='normal')
            return None
        
        # Read data file
        lines = file.read().split('\n')
        file.close()
        
        # Show error message if data file is empty
        if len(lines) == 1:
            
            frame.varMessageLabel.set('No image data to manage.')
            self.menubar.entryconfig(1, state='normal')
            self.menubar.entryconfig(2, state='normal')
            self.menubar.entryconfig(3, state='normal')
            self.menubar.entryconfig(4, state='normal')
            return None
        
        # Get data from file and store in lists
        for line in lines[:-1]:
            
            elements = line.split(',')
            name = elements[0]
            keyword = elements[1]
            names.append(name)
            keywords.append(keyword)
            display_keywords.append(keyword + ' (' + name + ')')
            data.append(elements[2:])
    
        self.varManageData.set(display_keywords[0])
        
        self.menubar.entryconfig(1, state='disabled')
        self.menubar.entryconfig(2, state='disabled')
        self.menubar.entryconfig(3, state='disabled')
        self.menubar.entryconfig(4, state='disabled')
    
        # Setup managing window
        self.topManage = tk.Toplevel()
        self.topManage.title('Manage image data')
        self.addIcon(self.topManage)
        setupWindow(self.topManage, 300, 135)
        self.topManage.focus_force()
        
        labelManage = ttk.Label(self.topManage, text='Choose image data:',anchor='center')
        optionManage = ttk.OptionMenu(self.topManage, self.varManageData, None, *display_keywords)
        frameLow = ttk.Frame(self.topManage)
        
        labelManage.pack(side='top', pady=10*scsy, expand=True)
        optionManage.pack(side='top', pady=6*scsy, expand=True)
        frameLow.pack(side='top', pady=14*scsy, expand=True)
        
        buttonRename = ttk.Button(frameLow, text='Rename',
                                  command=lambda: self.executeManage(names,
                                                                     keywords,
                                                                     display_keywords,
                                                                     data,
                                                                     delete=False))
        buttonDelete = ttk.Button(frameLow, text='Delete',
                                  command=lambda: self.executeManage(names,
                                                                     keywords,
                                                                     display_keywords,
                                                                     data))
        
        buttonRename.grid(row=0, column=0, padx=5*scsx)
        buttonDelete.grid(row=0, column=1)
        
        self.wait_window(self.topManage)
        try:
            self.topRename.destroy()
        except:
            pass
        try:
            self.menubar.entryconfig(1, state='normal')
            self.menubar.entryconfig(2, state='normal')
            self.menubar.entryconfig(3, state='normal')
            self.menubar.entryconfig(4, state='normal')
        except:
            pass
    
    def executeManage(self, names, keywords, display_keywords, datafull, delete=True):
    
        '''Deletes selected data, or creates window for renaming selected save.'''
    
        linenum = display_keywords.index(self.varManageData.get()) # Index of relevant data
        
        if delete:
            
            file = open('imagedata.txt', 'w')
            
            # Rewrite the data file without the line containing the data selected for deleting
            
            for i in range(linenum):
            
                    file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
                               % tuple([names[i]] + [keywords[i]] + datafull[i]))
                
            if linenum < len(keywords):
                
                for i in range(linenum+1, len(keywords)):
                
                    file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
                               % tuple([names[i]] + [keywords[i]] + datafull[i]))
                      
                        
            file.close()
            
            # Go back to an updated managing window
            self.topManage.destroy()
            self.manageData()
            self.currentFrame().varMessageLabel.set('Image data deleted.')
            
        else:
        
            # Create window for inputting new save name
        
            self.varNewname = tk.StringVar()
            self.varNewnameError = tk.StringVar()
            
            self.varNewname.set(keywords[linenum])
            
            self.topRename = tk.Toplevel()
            self.topRename.title('Insert new name')
            self.addIcon(self.topRename)
            setupWindow(self.topRename, 300, 135)
            self.topRename.focus_force()
            
            labelRename = ttk.Label(self.topRename, text='Insert new name:', anchor='center')
            entryRename = ttk.Entry(self.topRename, textvariable=self.varNewname, font=self.small_font,
                                    background=DEFAULT_BG, width=35)
            buttonRename = ttk.Button(self.topRename, text='Rename',
                                      command=lambda: self.executeRename(names,
                                                                         keywords,
                                                                         datafull,
                                                                         linenum))
            labelRenameError = ttk.Label(self.topRename, textvariable=self.varNewnameError)
            
            labelRename.pack(side='top', pady=10*scsy, expand=True)
            entryRename.pack(side='top', pady=5*scsy, expand=True)
            buttonRename.pack(side='top', pady=6*scsy, expand=True)
            labelRenameError.pack(side='top', expand=True)
        
    def executeRename(self, names, keywords, datafull, linenum):
    
        '''Renames the selected data save.'''
    
        if self.varNewname.get() != '' and not ',' in self.varNewname.get():
        
            file = open('imagedata.txt', 'w')
            
            # Rewrites the data file, using the new keyword for the selected data save
            
            for i in range(linenum):
                
                file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
                           % tuple([names[i]] + [keywords[i]] + datafull[i]))

            file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
                       % tuple([names[linenum]] + [self.varNewname.get()] + datafull[linenum]))
            
            if linenum < len(keywords):
                
                for i in range(linenum+1, len(keywords)):

                    file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
                               % tuple([names[i]] + [keywords[i]] + datafull[i]))
                         
            file.close()
            
            # Go back to an updated managing window
            self.topRename.destroy()
            self.topManage.destroy()
            self.manageData()
            self.currentFrame().varMessageLabel.set('Image data renamed.')
        
        # Show an error message if the new name contains a ","
        elif ',' in self.varNewname.get():
        
            self.varNewnameError.set('The new name cannot contain a ",".')
        
        # Show an error message if the new name is an empty string
        else:
        
            self.varNewnameError.set('Please insert a new name.')
            return None

    def changeCamera(self, restrict='no'):
    
        '''Create window with list of camera models.'''
        
        self.menubar.entryconfig(1, state='disabled')
        self.menubar.entryconfig(2, state='disabled')
        self.menubar.entryconfig(3, state='disabled')
        self.menubar.entryconfig(4, state='disabled')
    
        # Setup window
        self.topCamera = tk.Toplevel()
        self.topCamera.title('Choose camera')
        self.addIcon(self.topCamera)
        setupWindow(self.topCamera, 300, 330)
        self.topCamera.focus_force()
        
        labelCamera = tk.Label(self.topCamera, text='Choose camera:', font=self.medium_font)
        frameSelection = ttk.Frame(self.topCamera)
        
        labelCamera.pack(side='top', pady=(18*scsy, 8*scsy), expand=True)
        frameSelection.pack(side='top', pady=10*scsy, expand=True)
        
        scrollbarCamera = ttk.Scrollbar(frameSelection)
        self.listboxCamera = tk.Listbox(frameSelection, height=8, width=28, font=self.small_font,
                                        selectmode='single', yscrollcommand=scrollbarCamera.set)
        
        scrollbarCamera.pack(side='right', fill='y')
        self.listboxCamera.pack(side='right', fill='both')
        
        self.listboxCamera.focus_force()
        
        # Insert camera names into listbox
        if restrict == 'no':
            for i in range(len(CNAME)):
                self.listboxCamera.insert(i, CNAME[i])
        elif restrict == 'DSLR':
            for i in range(len(CNAME)):
                if TYPE[i] == 'DSLR': self.listboxCamera.insert(i, CNAME[i])
        elif restrict == 'CCD':
            for i in range(len(CNAME)):
                if TYPE[i] == 'CCD': self.listboxCamera.insert(i, CNAME[i])
            
        scrollbarCamera.config(command=self.listboxCamera.yview) # Add scrollbar to listbox
        
        if self.cnum is not None: self.listboxCamera.activate(self.cnum)
        
        self.varSetDefaultC = tk.IntVar()
        
        frameDefault = ttk.Frame(self.topCamera)
        buttonChange = ttk.Button(self.topCamera, text='OK', command=self.executeCamChange)
        buttonAddNew = ttk.Button(self.topCamera, text='Add new camera', command=self.addNewCamera)
        
        frameDefault.pack(side='top', expand=True)
        buttonChange.pack(side='top', pady=(10*scsy, 5*scsy), expand=True)
        buttonAddNew.pack(side='top', pady=(0, 25*scsy), expand=True)
        
        labelDefault = ttk.Label(frameDefault, text='Use as default:')
        checkbuttonDefault = tk.Checkbutton(frameDefault, variable=self.varSetDefaultC)
        
        labelDefault.grid(row=0, column=0)
        checkbuttonDefault.grid(row=0, column=1)
        
        self.cancelled = True
        
        self.wait_window(self.topCamera)
        try:
            self.menubar.entryconfig(1, state='normal')
            if not self.anMode.get(): self.menubar.entryconfig(2, state='normal')
            self.menubar.entryconfig(3, state='normal')
            self.menubar.entryconfig(4, state='normal')
        except:
            pass
            
        # Return true if the window wasn't closed with the X
        return not self.cancelled
       
    def executeCamChange(self):
    
        '''Configures widgets according to the selected new camera.'''
        
        self.cancelled = False
    
        self.cnum = CNAME.index(self.listboxCamera.get('active')) # Get index of new camera
        
        # Calculate new image scale value if a telescope is selected
        if self.tnum is not None:
            self.ISVal = np.arctan2(PIXEL_SIZE[self.cnum][0]*1e-3,
                                    FOCAL_LENGTH[self.tnum][0]*self.FLModVal)*180*3600/np.pi
            
        # Sets the new camera name in bottom line in camera data file if "Set as default" is selected
        if self.varSetDefaultC.get():
            
            file = open('cameradata.txt', 'r')
            lines = file.read().split('\n')
            file.close()
            
            file = open('cameradata.txt', 'w')
            for line in lines[:-1]:
                file.write(line + '\n')
            file.write('Camera: ' + CNAME[self.cnum] + ',' + ','.join(lines[-1].split(',')[1:]))
            file.close()
            
        self.varCamName.set('Camera: ' + CNAME[self.cnum])
        
        anframe = self.frames[ImageAnalyser]
            
        self.isDSLR = TYPE[self.cnum] == 'DSLR' # Set new camera type
        self.hasQE = QE[self.cnum][0] != 'NA' # Set new QE state
        self.noData = GAIN[self.cnum][0][0] == 0
        
        if not self.hasQE: self.setElectronSignalType()
        
        if self.isDSLR:
            anframe.radioCCDm.grid_forget()
            anframe.radioCCDc.grid_forget()
            anframe.labelDSLR.grid(row=0, column=0, columnspan=2, sticky='EW')
        else:
            anframe.labelDSLR.grid_forget()
            anframe.varCCDType.set('mono')
            anframe.radioCCDm.grid(row=0, column=0)
            anframe.radioCCDc.grid(row=0, column=1)
            
        if not self.toolsConfigured:
            self.topCamera.destroy()
            anframe.varMessageLabel.set('Camera selected.')
            return None
        
        calframe = self.frames[ImageCalculator]
        simframe = self.frames[ImageSimulator]
        plotframe = self.frames[PlottingTool]
        
        # Reset frames to original states
        calframe.setDefaultValues()
        calframe.toggleDarkInputMode()
        if self.tooltipsOn.get():
            createToolTip(calframe.entryDark, TTDarkNoise if self.isDSLR else TTDarkLevel, self.tt_fs)
        
        simframe.setDefaultValues()
        
        plotframe.setDefaultValues()
        
        anframe.clearFiles()
        
        # Update widgets
        calframe.reconfigureNonstaticWidgets()
        simframe.reconfigureNonstaticWidgets()
        plotframe.reconfigureNonstaticWidgets()
        
        plotframe.toggleActiveWidgets(plotframe.plotList[0])
        
        if self.calMode.get():
            self.showFrame(MessageWindow if self.noData else ImageCalculator)
        elif self.simMode.get():
            self.showFrame(MessageWindow if self.noData else ImageSimulator)
        elif self.plMode.get():
            self.showFrame(MessageWindow if self.noData else PlottingTool)
        
        self.topCamera.destroy() # Close change camera window
        self.currentFrame().varMessageLabel.set('Camera changed.')

    def addNewCamera(self):
    
        '''Shows a window with options for adding a new camera.'''
    
        varCamName = tk.StringVar()
        varCamType = tk.StringVar()
        varPS = tk.StringVar()
        varMessageLabel = tk.StringVar()
        
        def executeAddNew():
        
            '''Adds the new camera to "cameradata.txt".'''
        
            # Get inputted name of new camera
            name = varCamName.get()
            type = varCamType.get()
            
            try:
                ps = float(varPS.get())
            except:
                varMessageLabel.set('Invalid pixel size input.')
                return None
                
            if name == '' or ',' in name:
                varMessageLabel.set('Invalid camera name input.')
                return None
                    
            if name in CNAME:
                varMessageLabel.set('This camera is already added.')
                return None
                
            # Read camera data file            
            file = open('cameradata.txt', 'r')
            lines = file.read().split('\n')
            file.close()
                
            file = open('cameradata.txt', 'w')
                
            file.write(lines[0])
            
            # Create new line in cameradata.txt
            file.write('\n' + '\n'.join(lines[1:-1]))
            file.write('\n%s,%s,0,0,0,0,0,NA,%g*' % (name, type, ps))
            if type == 'DSLR': file.write(',0')
            file.write('\n' + lines[-1])
            file.close()
            
            # Sort camera list
            idx = sortDataList(name, 'cameradata.txt')
            
            # Insert camera name and type to camera info lists
            CNAME.insert(idx, name)
            TYPE.insert(idx, type)
            GAIN.insert(idx, [np.array([0], dtype='float'), np.array([1])])
            RN.insert(idx, [np.array([0]), np.array([1])])
            SAT_CAP.insert(idx, [[0], [1]])
            BLACK_LEVEL.insert(idx, [[0], [1]])
            WHITE_LEVEL.insert(idx, [[0], [1]])
            QE.insert(idx, ['NA', 1])
            PIXEL_SIZE.insert(idx, [ps, 1])
            ISO.insert(idx, (np.array([0])))
            
            self.cancelled = False
            self.topAddNewCam.destroy()
            self.topCamera.destroy()
            self.changeCamera()
    
        # Setup window
        self.topAddNewCam = tk.Toplevel()
        self.topAddNewCam.title('Add new camera')
        self.addIcon(self.topAddNewCam)
        setupWindow(self.topAddNewCam, 300, 200)
        self.topAddNewCam.focus_force()
        
        varCamType.set('DSLR')
            
        ttk.Label(self.topAddNewCam, text='Please provide requested camera information:')\
                 .pack(side='top', pady=(15*scsy, 10*scsy), expand=True)
            
        frameInput = ttk.Frame(self.topAddNewCam)
        frameInput.pack(side='top', pady=(7*scsy, 10*scsy), expand=True)
                  
        ttk.Label(frameInput, text='Camera type: ').grid(row=0, column=0, sticky='W')
        ttk.OptionMenu(frameInput, varCamType, None, 'DSLR', 'CCD').grid(row=0, column=1)
            
        ttk.Label(frameInput, text='Camera name: ').grid(row=1, column=0, sticky='W')
        ttk.Entry(frameInput, textvariable=varCamName, font=self.small_font,
                  background=DEFAULT_BG, width=20).grid(row=1, column=1)
                  
        ttk.Label(frameInput, text=u'Pixel size (in \u03bcm): ').grid(row=2, column=0, sticky='W')
        ttk.Entry(frameInput, textvariable=varPS, font=self.small_font,
                  background=DEFAULT_BG, width=20).grid(row=2, column=1)
        
        ttk.Button(self.topAddNewCam, text='OK',
                   command=executeAddNew).pack(side='top', pady=(0, 10*scsy), expand=True)
        ttk.Label(self.topAddNewCam, textvariable=varMessageLabel, font=self.small_font,
                  background=DEFAULT_BG).pack(side='top', pady=(0, 10*scsy), expand=True)
        
    def changeTelescope(self):
    
        '''Create window with list of telescope models.'''
        
        self.menubar.entryconfig(1, state='disabled')
        self.menubar.entryconfig(2, state='disabled')
        self.menubar.entryconfig(3, state='disabled')
        self.menubar.entryconfig(4, state='disabled')
    
        # Setup window
        self.topTelescope = tk.Toplevel()
        self.topTelescope.title('Choose telescope or lens')
        self.addIcon(self.topTelescope)
        setupWindow(self.topTelescope, 320, 330)
        self.topTelescope.focus_force()
        
        labelTelescope = tk.Label(self.topTelescope, text='Choose telescope or lens:',
                                  font=self.medium_font)
        frameSelection = ttk.Frame(self.topTelescope)
        
        labelTelescope.pack(side='top', pady=(18*scsy, 8*scsy), expand=True)
        frameSelection.pack(side='top', pady=10*scsy, expand=True)
        
        scrollbarTelescope = ttk.Scrollbar(frameSelection)
        self.listboxTelescope = tk.Listbox(frameSelection, height=8, width=32, font=self.small_font,
                                           selectmode='single', yscrollcommand=scrollbarTelescope.set)
        
        scrollbarTelescope.pack(side='right', fill='y')
        self.listboxTelescope.pack(side='right', fill='both')
        
        self.listboxTelescope.focus_force()
        
        # Insert telescope names into listbox
        for i in range(len(TNAME)):
            self.listboxTelescope.insert(i, TNAME[i])
            
        scrollbarTelescope.config(command=self.listboxTelescope.yview) # Add scrollbar to listbox
        
        if self.tnum is not None: self.listboxTelescope.activate(self.tnum)
        
        self.varSetDefaultT = tk.IntVar()
        
        frameDefault = ttk.Frame(self.topTelescope)
        buttonChange = ttk.Button(self.topTelescope, text='OK', command=self.executeTelChange)
        buttonAddNew = ttk.Button(self.topTelescope, text='Add new telescope or lens',
                                  command=self.addNewTelescope)
        
        frameDefault.pack(side='top', expand=True)
        buttonChange.pack(side='top', pady=(10*scsy, 5*scsy), expand=True)
        buttonAddNew.pack(side='top', pady=(0, 25*scsy), expand=True)
        
        labelDefault = ttk.Label(frameDefault, text='Use as default:')
        checkbuttonDefault = tk.Checkbutton(frameDefault, variable=self.varSetDefaultT)
        
        labelDefault.grid(row=0, column=0)
        checkbuttonDefault.grid(row=0, column=1)
        
        self.cancelled = True
        
        self.wait_window(self.topTelescope)
        try:
            self.menubar.entryconfig(1, state='normal')
            if not self.anMode.get(): self.menubar.entryconfig(2, state='normal')
            self.menubar.entryconfig(3, state='normal')
            self.menubar.entryconfig(4, state='normal')
        except:
            pass
            
        return not self.cancelled
        
    def executeTelChange(self):
    
        '''Configures widgets according to the selected new telescope.'''
        
        self.cancelled = False
    
        self.tnum = TNAME.index(self.listboxTelescope.get('active')) # Get index of new telescope
        
        # Calculate new image scale value if a camera is selected
        if self.cnum is not None:
            self.ISVal = np.arctan2(PIXEL_SIZE[self.cnum][0]*1e-3,
                                    FOCAL_LENGTH[self.tnum][0]*self.FLModVal)*180*3600/np.pi
        
        # Sets the new telescope name in bottom line in telescope data file if "Set as default" is selected
        if self.varSetDefaultT.get():
            
            file = open('telescopedata.txt', 'r')
            lines = file.read().split('\n')
            file.close()
            
            file = open('telescopedata.txt', 'w')
            for line in lines[:-1]:
                file.write(line + '\n')
            file.write('Telescope: ' + TNAME[self.tnum])
            file.close()
            
        self.varTelName.set('Telescope: ' + TNAME[self.tnum])
            
        anframe = self.frames[ImageAnalyser]
            
        if not self.toolsConfigured:
            self.topTelescope.destroy()
            anframe.varMessageLabel.set('Telescope selected.')
            return None
        
        calframe = self.frames[ImageCalculator]
        simframe = self.frames[ImageSimulator]
        plotframe = self.frames[PlottingTool]
        
        calframe.setDefaultValues()
        simframe.setDefaultValues()
        plotframe.setDefaultValues()
        
        anframe.clearFiles()
        
        self.topTelescope.destroy() # Close change telescope window
        self.currentFrame().varMessageLabel.set('Telescope changed.')
        
    def addNewTelescope(self):
    
        '''Shows a window with options for adding a new telescope/lens.'''
    
        varTelName = tk.StringVar()
        varAp = tk.StringVar()
        varFL = tk.StringVar()
        varMessageLabel = tk.StringVar()
        
        def executeAddNew():
        
            '''Adds the new telescope to "telescopedata.txt".'''
        
            # Get inputted name of new camera
            name = varTelName.get()
            
            try:
                aperture = float(varAp.get())
            except:
                varMessageLabel.set('Invalid aperture input.')
                return None
            
            try:
                fl = float(varFL.get())
            except:
                varMessageLabel.set('Invalid focal length input.')
                return None
                
            if name == '' or ',' in name:
                varMessageLabel.set('Invalid telescope/lens name input.')
                return None
                    
            if name in TNAME:
                varMessageLabel.set('This telescope/lens is already added.')
                return None
                
            # Read telescope data file            
            file = open('telescopedata.txt', 'r')
            lines = file.read().split('\n')
            file.close()
                
            file = open('telescopedata.txt', 'w')
                
            file.write(lines[0])
            
            # Create new line in telescopedata.txt
            file.write('\n' + '\n'.join(lines[1:-1]))
            file.write('\n%s,%g*,%g*' % (name, fl, aperture))
            file.write('\n' + lines[-1])
            file.close()
            
            # Sort telescope list
            idx = sortDataList(name, 'telescopedata.txt')
            
            # Insert telescope name, aperture and focal length to telescope info lists
            TNAME.insert(idx, name)
            FOCAL_LENGTH.insert(idx, [fl, 1])
            APERTURE.insert(idx, [aperture, 1])
            
            self.cancelled = False
            self.topAddNewTel.destroy()
            self.topTelescope.destroy()
            self.changeTelescope()
    
        # Setup window
        self.topAddNewTel = tk.Toplevel()
        self.topAddNewTel.title('Add new telescope or lens')
        self.addIcon(self.topAddNewTel)
        setupWindow(self.topAddNewTel, 300, 220)
        self.topAddNewTel.focus_force()
            
        tk.Label(self.topAddNewTel, text='Please provide requested\ntelescope/lens information:',
                 font=self.small_font)\
                 .pack(side='top', pady=(15*scsy, 10*scsy), expand=True)
            
        frameInput = ttk.Frame(self.topAddNewTel)
        frameInput.pack(side='top', pady=(7*scsy, 10*scsy), expand=True)
            
        ttk.Label(frameInput, text='Name: ').grid(row=0, column=0, sticky='W')
        ttk.Entry(frameInput, textvariable=varTelName, font=self.small_font,
                  background=DEFAULT_BG, width=20).grid(row=0, column=1, columnspan=2)
                  
        ttk.Label(frameInput, text='Aperture: ').grid(row=1, column=0, sticky='W')
        ttk.Entry(frameInput, textvariable=varAp, font=self.small_font,
                  background=DEFAULT_BG, width=12).grid(row=1, column=1, sticky='W')
        tk.Label(frameInput, text='mm', font=self.small_font).grid(row=1, column=2, sticky='W')
                  
        ttk.Label(frameInput, text='Focal length: ').grid(row=2, column=0, sticky='W')
        ttk.Entry(frameInput, textvariable=varFL, font=self.small_font,
                  background=DEFAULT_BG, width=12).grid(row=2, column=1, sticky='W')
        tk.Label(frameInput, text='mm', font=self.small_font).grid(row=2, column=2, sticky='W')
        
        ttk.Button(self.topAddNewTel, text='OK',
                   command=executeAddNew).pack(side='top', pady=(0, 10*scsy), expand=True)
        ttk.Label(self.topAddNewTel, textvariable=varMessageLabel, font=self.small_font,
                  background=DEFAULT_BG).pack(side='top', pady=(0, 10*scsy), expand=True)
        
    def changeFLMod(self):
    
        '''Change focal length modifier.'''
        
        varFLMod = tk.StringVar()
        varMessageLabel = tk.StringVar()
        
        def ok():
        
            '''Set the new FL modifier value and update relevant widgets and parameters.'''
        
            try:
                FLModVal = float(varFLMod.get())
            except ValueError:
                varMessageLabel.set('Invalid input.')
                return None
                
            self.varFLMod.set('Focal length modifier: %gx' % FLModVal)
            self.FLModVal = FLModVal
            
            self.currentFrame().varMessageLabel.set('Focal length modifier changed.')
            
            self.ISVal = np.arctan2(PIXEL_SIZE[self.cnum][0]*1e-3,
                                    FOCAL_LENGTH[self.tnum][0]*self.FLModVal)*180*3600/np.pi
                                    
            self.frames[ImageCalculator].updateOpticsLabels()
            self.frames[ImageSimulator].updateOpticsLabels()
            self.frames[ImageAnalyser].updateAngle()
            
            topChangeFLMod.destroy()
        
        self.menubar.entryconfig(1, state='disabled')
        self.menubar.entryconfig(2, state='disabled')
        self.menubar.entryconfig(3, state='disabled')
        self.menubar.entryconfig(4, state='disabled')
    
        # Setup window
        topChangeFLMod = tk.Toplevel()
        topChangeFLMod.title('Change focal length modifier')
        setupWindow(topChangeFLMod, 220, 160)
        self.addIcon(topChangeFLMod)
        topChangeFLMod.focus_force()
        
        tk.Label(topChangeFLMod, text='Input the magnification factor of\nthe barlow or focal reducer:',
                 font=self.small_font).pack(side='top', pady=(12*scsy, 0), expand=True)
        entryFLMod = ttk.Entry(topChangeFLMod, textvariable=varFLMod, font=self.small_font,
                               background=DEFAULT_BG, width=10).pack(side='top', pady=12*scsy,
                                                                     expand=True)
        
        frameButtons = ttk.Frame(topChangeFLMod)
        frameButtons.pack(side='top', pady=(0, 12*scsy), expand=True)
        
        ttk.Button(frameButtons, text='OK', command=ok).grid(row=0, column=0)
        ttk.Button(frameButtons, text='Cancel',
                   command=lambda: topChangeFLMod.destroy()).grid(row=0, column=1)
                   
        ttk.Label(topChangeFLMod, textvariable=varMessageLabel,
                  anchor='center').pack(side='top', pady=(0, 3*scsy), expand=True)
        
        self.wait_window(topChangeFLMod)
        try:
            self.menubar.entryconfig(1, state='normal')
            if not self.anMode.get(): self.menubar.entryconfig(2, state='normal')
            self.menubar.entryconfig(3, state='normal')
            self.menubar.entryconfig(4, state='normal')
        except:
            pass
        
    def modifyCamParams(self):
    
        '''Creates window with options for modifying camera data.'''
    
        self.menubar.entryconfig(1, state='disabled')
        self.menubar.entryconfig(2, state='disabled')
        self.menubar.entryconfig(3, state='disabled')
        self.menubar.entryconfig(4, state='disabled')
    
        # Setup window
        self.topCModify = tk.Toplevel()
        self.topCModify.title('Modify parameters')
        self.addIcon(self.topCModify)
        setupWindow(self.topCModify, 280, 210)
        self.topCModify.focus_force()
        
        # Show a message if no camera data exists
        if self.noData:
        
            tk.Label(self.topCModify, text='No sensor data exists for\nthe currently active camera.\n\n' \
                                          + 'You can aquire sensor data\nwith the Image Analyser.',
                     font=self.small_font).pack(side='top', pady=20*scsy, expand=True)
            
            ttk.Button(self.topCModify, text='OK', command=lambda: self.topCModify.destroy())\
                .pack(side='top', pady=(0, 10*scsy), expand=True)
            
            self.wait_window(self.topCModify)
        
            try:
                self.menubar.entryconfig(1, state='normal')
                if not self.anMode.get(): self.menubar.entryconfig(2, state='normal')
                self.menubar.entryconfig(3, state='normal')
                self.menubar.entryconfig(4, state='normal')
            except:
                pass
            
            return None
    
        # Read camera data file
        file = open('cameradata.txt', 'r')
        self.lines = file.read().split('\n')
        file.close()
        
        # Store parameter values
        self.currentCValues = self.lines[self.cnum + 1].split(',')
        
        self.gain_idx = 0
        self.rn_idx = 0
    
        self.varCParam = tk.StringVar()
        self.varISO = tk.IntVar()
        self.varGain = tk.DoubleVar()
        self.varRN = tk.DoubleVar()
        
        self.varNewCParamVal = tk.StringVar()
        self.varCurrentCParamVal = tk.StringVar()
        self.varErrorModifyC = tk.StringVar()
        
        # List of modifyable parameters
        paramlist = ['Gain', 'Read noise', 'Sat. cap.', 'Black level', 'White level', 'QE',
                     'Pixel size']
        self.isolist = self.currentCValues[9].split('-') if self.isDSLR else ['0'] # List of ISO values
        self.gainlist = self.currentCValues[2].split('-')                          # List of gain values
        self.rnlist = self.currentCValues[3].split('-')     # List of read noise values
        self.satcaplist = self.currentCValues[4].split('-') # List of saturation capacity values
        self.bllist = self.currentCValues[5].split('-')     # List of black level values
        self.wllist = self.currentCValues[6].split('-')     # List of white level values
        
        self.varCParam.set(paramlist[0])
        self.varISO.set(self.isolist[0])
        self.varGain.set(self.gainlist[0])
        self.varRN.set(self.rnlist[0])
        
        self.varNewCParamVal.set('')
        self.varCurrentCParamVal.set('Current value: ' + self.gainlist[0].split('*')[0] + ' e-/ADU' \
                                     + (' (modified)' if '*' in self.gainlist[0] else ''))
        
        frameParam = ttk.Frame(self.topCModify)
        
        labelParam = ttk.Label(frameParam, text='Parameter:', anchor='center', width=11)
        optionParam = ttk.OptionMenu(frameParam, self.varCParam, None, *paramlist,
                                     command=self.updateCamParam)
                                     
        self.labelISO = ttk.Label(frameParam, text='ISO:', anchor='center', width=11)
        self.optionISO = ttk.OptionMenu(frameParam, self.varISO, None, *self.isolist,
                                        command=self.updateParamISO)
        
        self.labelGain = ttk.Label(frameParam, text='Gain:', anchor='center', width=11)
        self.optionGain = ttk.OptionMenu(frameParam, self.varGain, None, *self.gainlist,
                                         command=self.updateParamGain)
        
        self.labelRN = ttk.Label(frameParam, text='RN:', anchor='center', width=11)
        self.optionRN = ttk.OptionMenu(frameParam, self.varRN, None, *self.rnlist,
                                       command=self.updateParamRN)
        
        labelCurrent = ttk.Label(self.topCModify, textvariable=self.varCurrentCParamVal)
        
        labelSet = ttk.Label(self.topCModify, text='Input new value:', anchor='center')
        entryNewVal = ttk.Entry(self.topCModify, textvariable=self.varNewCParamVal,
                                font=self.small_font, background=DEFAULT_BG)
        
        buttonSet = ttk.Button(self.topCModify, text='Set value', command=self.setNewCamParamVal)
        
        errorModify = ttk.Label(self.topCModify, textvariable=self.varErrorModifyC, anchor='center')
        
        frameParam.pack(side='top', pady=(10*scsy, 0), expand=True)
        
        labelParam.grid(row=0, column=0)
        optionParam.grid(row=1, column=0)
        
        if self.isDSLR:
            self.labelISO.grid(row=0, column=1)
            self.optionISO.grid(row=1, column=1)
        elif len(self.gainlist) > 1:
            self.labelGain.grid(row=0, column=1)
            self.optionGain.grid(row=1, column=1)
        
        labelCurrent.pack(side='top', pady=10*scsy, expand=True)
        labelSet.pack(side='top', expand=True)
        entryNewVal.pack(side='top', pady=5*scsy, expand=True)
        buttonSet.pack(side='top', pady=5*scsy, expand=True)
        errorModify.pack(side='top', expand=True)
        
        self.currentFrame().varMessageLabel.set(\
        'Note: changing the value of a camera parameter will reset the application.')
        
        self.wait_window(self.topCModify)
        
        try:
            self.menubar.entryconfig(1, state='normal')
            if not self.anMode.get(): self.menubar.entryconfig(2, state='normal')
            self.menubar.entryconfig(3, state='normal')
            self.menubar.entryconfig(4, state='normal')
        except:
            pass

    def updateCamParam(self, selected_param):
    
        '''Displays the relevant parameter value when selected parameter in the optionmenu changes.'''
    
        self.labelISO.grid_forget()
        self.optionISO.grid_forget()
        self.labelGain.grid_forget()
        self.optionGain.grid_forget()
        self.labelRN.grid_forget()
        self.optionRN.grid_forget()
        
        self.varISO.set(self.isolist[0])
        self.varGain.set(self.gainlist[0])
        self.varRN.set(self.rnlist[0])
    
        if selected_param == 'Gain':
        
            if self.isDSLR:
                self.labelISO.grid(row=0, column=1)
                self.optionISO.grid(row=1, column=1)
            elif len(self.gainlist) > 1:
                self.labelGain.grid(row=0, column=1)
                self.optionGain.grid(row=1, column=1)
                
            self.varCurrentCParamVal.set('Current value: ' + self.gainlist[0].split('*')[0]  + ' e-/ADU' \
                                         + (' (modified)' if '*' in self.gainlist[0] else ''))
            
        elif selected_param == 'Read noise':
        
            if self.isDSLR:
                self.labelISO.grid(row=0, column=1)
                self.optionISO.grid(row=1, column=1)
            elif len(self.rnlist) > 1:
                self.labelRN.grid(row=0, column=1)
                self.optionRN.grid(row=1, column=1)
                
            self.varCurrentCParamVal.set('Current value: ' + self.rnlist[0].split('*')[0]  + ' e-' \
                                         + (' (modified)' if '*' in self.rnlist[0] else ''))
            
        elif selected_param == 'Sat. cap.':
        
            if self.isDSLR:
                self.labelISO.grid(row=0, column=1)
                self.optionISO.grid(row=1, column=1)
            elif len(self.gainlist) > 1:
                self.labelGain.grid(row=0, column=1)
                self.optionGain.grid(row=1, column=1)
        
            self.varCurrentCParamVal.set('Current value: ' + self.satcaplist[0].split('*')[0] + ' e-' \
                                         + (' (modified)' if '*' in self.satcaplist[0] else ''))
    
        elif selected_param == 'Black level':
        
            if self.isDSLR:
                self.labelISO.grid(row=0, column=1)
                self.optionISO.grid(row=1, column=1)
            elif len(self.gainlist) > 1:
                self.labelGain.grid(row=0, column=1)
                self.optionGain.grid(row=1, column=1)
                
            self.varCurrentCParamVal.set('Current value: ' + self.bllist[0].split('*')[0] + ' ADU' \
                                         + (' (modified)' if '*' in self.bllist[0] else ''))
        
        elif selected_param == 'White level':
        
            if self.isDSLR:
                self.labelISO.grid(row=0, column=1)
                self.optionISO.grid(row=1, column=1)
            elif len(self.gainlist) > 1:
                self.labelGain.grid(row=0, column=1)
                self.optionGain.grid(row=1, column=1)
        
            self.varCurrentCParamVal.set('Current value: ' + self.wllist[0].split('*')[0] + ' ADU' \
                                         + (' (modified)' if '*' in self.wllist[0] else ''))
            
        elif selected_param == 'QE':
        
            if self.hasQE:
                self.varCurrentCParamVal.set('Current value: ' + self.currentCValues[7].split('*')[0] \
                                             + (' (modified)' if '*' in self.currentCValues[7] else ''))
            else:
                self.varCurrentCParamVal.set('No value exists.')
            
        elif selected_param == 'Pixel size':
        
            self.varCurrentCParamVal.set('Current value: ' + self.currentCValues[8].split('*')[0] \
                                         + u' \u03bcm' \
                                         + (' (modified)' if '*' in self.currentCValues[8] else ''))
    
    def updateParamISO(self, selected_iso):
    
        '''Update the label showing the current gain or read noise value when a new ISO is selected.'''
    
        # Store index of selected iso
        self.gain_idx = self.isolist.index(selected_iso)
        self.rn_idx = self.gain_idx
        
        if self.varCParam.get() == 'Gain':
            self.varCurrentCParamVal.set('Current value: ' + self.gainlist[self.gain_idx].split('*')[0] \
                        + ' e-/ADU' + (' (modified)' if '*' in self.gainlist[self.gain_idx] else ''))
        elif self.varCParam.get() == 'Read noise':
            self.varCurrentCParamVal.set('Current value: ' + self.rnlist[self.rn_idx].split('*')[0] \
                                + ' e-' + (' (modified)' if '*' in self.rnlist[self.rn_idx] else ''))
        elif self.varCParam.get() == 'Sat. cap.':
            self.varCurrentCParamVal.set('Current value: ' + self.satcaplist[self.gain_idx].split('*')[0] \
                        + ' e-' + (' (modified)' if '*' in self.satcaplist[self.gain_idx] else ''))
        elif self.varCParam.get() == 'Black level':
            self.varCurrentCParamVal.set('Current value: ' + self.bllist[self.gain_idx].split('*')[0] \
                            + ' ADU' + (' (modified)' if '*' in self.bllist[self.gain_idx] else ''))
        elif self.varCParam.get() == 'White level':
            self.varCurrentCParamVal.set('Current value: ' + self.wllist[self.gain_idx].split('*')[0] \
                            + ' ADU' + (' (modified)' if '*' in self.wllist[self.gain_idx] else ''))
            
    def updateParamGain(self, selected_gain):
    
        '''Update the label showing the current gain value when a new gain is selected.'''
    
        self.gain_idx = self.gainlist.index(selected_gain) # Store index of selected gain
        
        if self.varCParam.get() == 'Gain':
            self.varCurrentCParamVal.set('Current value: ' + selected_gain.split('*')[0] + ' e-/ADU' \
                                         + (' (modified)' if '*' in selected_gain else ''))
        elif self.varCParam.get() == 'Sat. cap.':
            self.varCurrentCParamVal.set('Current value: ' + self.satcaplist[self.gain_idx].split('*')[0] \
                         + ' e-' + (' (modified)' if '*' in self.satcaplist[self.gain_idx] else ''))
        elif self.varCParam.get() == 'Black level':
            self.varCurrentCParamVal.set('Current value: ' + self.bllist[self.gain_idx].split('*')[0] \
                            + ' ADU' + (' (modified)' if '*' in self.bllist[self.gain_idx] else ''))
        elif self.varCParam.get() == 'White level':
            self.varCurrentCParamVal.set('Current value: ' + self.wllist[self.gain_idx].split('*')[0] \
                            + ' ADU' + (' (modified)' if '*' in self.wllist[self.gain_idx] else ''))
        
    def updateParamRN(self, selected_rn):
    
        '''Update the label showing the current read noise value when a new read noise is selected.'''
    
        self.rn_idx = self.rnlist.index(selected_rn) # Store index of selected read noise
        self.varCurrentCParamVal.set('Current value: ' + selected_rn.split('*')[0] + ' e-' \
                                     + (' (modified)' if '*' in selected_rn else ''))
    
    def setNewCamParamVal(self):
    
        '''Writes new camera data file with the new value of the selected parameter.'''
    
        calframe = self.frames[ImageCalculator]
        simframe = self.frames[ImageSimulator]
        plotframe = self.frames[PlottingTool]
        
        newval = self.varNewCParamVal.get()
        
        # Show error message if the new inputted value is not a number
        try:
            float(newval)
        except ValueError:
            self.varErrorModifyC.set('Invalid value. Please insert a number.')
            return None
    
        # Write new camera data file
        
        file = open('cameradata.txt', 'w')
        
        idx = self.cnum + 1
        
        file.write(self.lines[0])
        
        for i in range(1, idx):
            file.write('\n' + self.lines[i])
        
        if self.varCParam.get() == 'Gain':
        
            self.gainlist[self.gain_idx] = newval + '*'
            file.write('\n%s,%s,%s' % (','.join(self.currentCValues[:2]),
                                       '-'.join(self.gainlist),
                                       ','.join(self.currentCValues[3:])))
            GAIN[self.cnum][0][self.gain_idx] = float(newval)
            GAIN[self.cnum][1][self.gain_idx] = 1
            self.varCurrentCParamVal.set('Current value: ' + newval + ' e-/ADU (modified)')
            
        elif self.varCParam.get() == 'Read noise':
        
            self.rnlist[self.rn_idx] = newval + '*'
            file.write('\n%s,%s,%s' % (','.join(self.currentCValues[:3]),
                                       '-'.join(self.rnlist),
                                       ','.join(self.currentCValues[4:])))
            RN[self.cnum][0][self.rn_idx] = float(newval)
            RN[self.cnum][1][self.rn_idx] = 1
            self.varCurrentCParamVal.set('Current value: ' + newval + ' e- (modified)')
            
        elif self.varCParam.get() == 'Sat. cap.':
        
            self.satcaplist[self.gain_idx] = newval + '*'
            file.write('\n%s,%s,%s' % (','.join(self.currentCValues[:4]),
                                       '-'.join(self.satcaplist),
                                       ','.join(self.currentCValues[5:])))
            SAT_CAP[self.cnum][0][self.gain_idx] = int(newval)
            SAT_CAP[self.cnum][1][self.gain_idx] = 1
            self.varCurrentCParamVal.set('Current value: ' + newval + ' e- (modified)')
        
        elif self.varCParam.get() == 'Black level':
            self.bllist[self.gain_idx] = newval + '*'
            file.write('\n%s,%s,%s' % (','.join(self.currentCValues[:5]),
                                       '-'.join(self.bllist),
                                       ','.join(self.currentCValues[6:])))
            BLACK_LEVEL[self.cnum][0][self.gain_idx] = int(newval)
            BLACK_LEVEL[self.cnum][1][self.gain_idx] = 1
            self.varCurrentCParamVal.set('Current value: ' + newval + ' ADU (modified)')
            
        elif self.varCParam.get() == 'White level':
            
            self.wllist[self.gain_idx] = newval + '*'
            file.write('\n%s,%s,%s' % (','.join(self.currentCValues[:6]),
                                       '-'.join(self.wllist),
                                       ','.join(self.currentCValues[7:])))
            WHITE_LEVEL[self.cnum][0][self.gain_idx] = int(newval)
            WHITE_LEVEL[self.cnum][1][self.gain_idx] = 1
            self.varCurrentCParamVal.set('Current value: ' + newval + ' ADU (modified)')
            
        elif self.varCParam.get() == 'QE':
        
            file.write('\n%s,%s,%s' % (','.join(self.currentCValues[:7]),
                                       newval + '*',
                                       ','.join(self.currentCValues[8:])))
            QE[self.cnum][0] = float(newval)
            QE[self.cnum][1] = 1
            self.varCurrentCParamVal.set('Current value: ' + newval + ' (modified)')
            
        elif self.varCParam.get() == 'Pixel size':
        
            file.write('\n%s,%s' % (','.join(self.currentCValues[:8]), newval + '*'))
            if self.isDSLR: file.write(',%s' % (self.currentCValues[9]))
                
            PIXEL_SIZE[self.cnum][0] = float(newval)
            PIXEL_SIZE[self.cnum][1] = 1
            self.varCurrentCParamVal.set('Current value: ' + newval + u' \u03bcm (modified)')
        
        for i in range((idx + 1), len(self.lines)):
            file.write('\n' + self.lines[i])
            
        file.close()
        
        # Reset all frames in order for the parameter change to take effect

        self.hasQE = QE[self.cnum][0] != 'NA'
        
        calframe.setDefaultValues()
        simframe.setDefaultValues()
        plotframe.setDefaultValues()
        
        calframe.reconfigureNonstaticWidgets()
        simframe.reconfigureNonstaticWidgets()
        plotframe.reconfigureNonstaticWidgets()
        
        self.currentFrame().varMessageLabel.set('Camera parameter modified.')
        
        # Update widgets and attributes in the window with the new parameter value
        self.optionISO.set_menu(*([None] + self.isolist))
        self.optionGain.set_menu(*([None] + self.gainlist))
        self.optionRN.set_menu(*([None] + self.rnlist))
        
        if self.isDSLR: self.varISO.set(self.isolist[self.gain_idx])
        self.varGain.set(self.gainlist[self.gain_idx])
        self.varRN.set(self.rnlist[self.rn_idx])
        
        self.varNewCParamVal.set('')
        self.varErrorModifyC.set('')
        
        file = open('cameradata.txt', 'r')
        self.lines = file.read().split('\n')
        file.close()
        
        self.currentCValues = self.lines[self.cnum + 1].split(',')
        
    def modifyTelParams(self):
    
        '''Creates window with options for modifying telescope data.'''
    
        self.menubar.entryconfig(1, state='disabled')
        self.menubar.entryconfig(2, state='disabled')
        self.menubar.entryconfig(3, state='disabled')
        self.menubar.entryconfig(4, state='disabled')
    
        # Setup window
        self.topTModify = tk.Toplevel()
        self.topTModify.title('Modify parameters')
        self.addIcon(self.topTModify)
        setupWindow(self.topTModify, 280, 210)
        self.topTModify.focus_force()
    
        # Read telescope data file
        file = open('telescopedata.txt', 'r')
        self.lines = file.read().split('\n')
        file.close()
        
        # Store parameter values
        self.currentTValues = self.lines[self.tnum + 1].split(',')
    
        self.varTParam = tk.StringVar()
        
        self.varNewTParamVal = tk.StringVar()
        self.varCurrentTParamVal = tk.StringVar()
        self.varErrorModifyT = tk.StringVar()
        
        # List of modifyable parameters
        paramlist = ['Focal length', 'Aperture']
        
        self.varTParam.set(paramlist[0])
        
        self.varNewTParamVal.set('')
        self.varCurrentTParamVal.set('Current value: ' + self.currentTValues[1].split('*')[0] + ' mm' \
                                     + (' (modified)' if '*' in self.currentTValues[1] else ''))
        
        frameParam = ttk.Frame(self.topTModify)
        
        labelParam = ttk.Label(frameParam, text='Parameter:', anchor='center', width=11)
        optionParam = ttk.OptionMenu(frameParam, self.varTParam, None, *paramlist,
                                     command=self.updateTelParam)
        
        labelCurrent = ttk.Label(self.topTModify, textvariable=self.varCurrentTParamVal)
        
        labelSet = ttk.Label(self.topTModify, text='Input new value:', anchor='center')
        entryNewVal = ttk.Entry(self.topTModify, textvariable=self.varNewTParamVal,
                                font=self.small_font, background=DEFAULT_BG)
        
        buttonSet = ttk.Button(self.topTModify, text='Set value', command=self.setNewTelParamVal)
        
        errorModify = ttk.Label(self.topTModify, textvariable=self.varErrorModifyT, anchor='center')
        
        frameParam.pack(side='top', pady=(10*scsy, 0), expand=True)
        
        labelParam.grid(row=0, column=0)
        optionParam.grid(row=1, column=0)
        
        labelCurrent.pack(side='top', pady=10*scsy, expand=True)
        labelSet.pack(side='top', expand=True)
        entryNewVal.pack(side='top', pady=5*scsy, expand=True)
        buttonSet.pack(side='top', pady=5*scsy, expand=True)
        errorModify.pack(side='top', expand=True)
        
        self.currentFrame().varMessageLabel.set(\
        'Note: changing the value of a telescope/lens parameter will reset the application.')
        
        self.wait_window(self.topTModify)
        
        try:
            self.menubar.entryconfig(1, state='normal')
            if not self.anMode.get(): self.menubar.entryconfig(2, state='normal')
            self.menubar.entryconfig(3, state='normal')
            self.menubar.entryconfig(4, state='normal')
        except:
            pass
        
    def updateTelParam(self, selected_param):
    
        '''Displays the relevant parameter value when selected parameter in the optionmenu changes.'''
            
        if selected_param == 'Focal length':
        
            self.varCurrentTParamVal.set('Current value: ' + self.currentTValues[1].split('*')[0] + ' mm' \
                                         + (' (modified)' if '*' in self.currentTValues[1] else ''))
    
        elif selected_param == 'Aperture':
        
            self.varCurrentTParamVal.set('Current value: ' + self.currentTValues[2].split('*')[0] + ' mm' \
                                         + (' (modified)' if '*' in self.currentTValues[2] else ''))
        
    def setNewTelParamVal(self):
    
        '''Writes new telescope data file with the new value of the selected parameter.'''
    
        calframe = self.frames[ImageCalculator]
        simframe = self.frames[ImageSimulator]
        plotframe = self.frames[PlottingTool]
        
        newval = self.varNewTParamVal.get()
        
        # Show error message if the new inputted value is not a number
        try:
            float(newval)
        except ValueError:
            self.varErrorModifyT.set('Invalid value. Please insert a number.')
            return None
    
        # Write new camera data file
        
        file = open('telescopedata.txt', 'w')
        
        idx = self.tnum + 1
        
        file.write(self.lines[0])
        
        for i in range(1, idx):
            file.write('\n' + self.lines[i])
            
        if self.varTParam.get() == 'Focal length':
        
            file.write('\n%s,%s,%s' % (self.currentTValues[0], newval + '*', self.currentTValues[2]))
                
            FOCAL_LENGTH[self.tnum][0] = float(newval)
            FOCAL_LENGTH[self.tnum][1] = 1
            self.varCurrentTParamVal.set('Current value: ' + newval + ' mm (modified)')
        
        elif self.varTParam.get() == 'Aperture':
        
            file.write('\n%s,%s,%s' % (self.currentTValues[0], self.currentTValues[1], newval + '*'))
                
            APERTURE[self.tnum][0] = float(newval)
            APERTURE[self.tnum][1] = 1
            self.varCurrentTParamVal.set('Current value: ' + newval + ' mm (modified)')
        
        for i in range((idx + 1), len(self.lines)):
            file.write('\n' + self.lines[i])
            
        file.close()
        
        calframe.setDefaultValues()
        simframe.setDefaultValues()
        plotframe.setDefaultValues()
        
        self.currentFrame().varMessageLabel.set('Telescope parameter modified.')
        
        self.varNewTParamVal.set('')
        self.varErrorModifyT.set('')
        
        file = open('telescopedata.txt', 'r')
        self.lines = file.read().split('\n')
        file.close()
        
        self.currentTValues = self.lines[self.tnum + 1].split(',')
        
    def transferToSim(self):
    
        '''Transfer relevant inputted or calculated values to widgets in the Image Simulator frame.'''
    
        calframe = self.frames[ImageCalculator]
        simframe = self.frames[ImageSimulator]
        plotframe = self.frames[PlottingTool]
        
        # If Image Calculator is the active frame
        if self.calMode.get():
        
            # Show error message if flux data hasn't been calculated
            if not calframe.dataCalculated:
                calframe.varMessageLabel.set('Data must be calculated before transfering input.')
                return None
        
            # Set values
            simframe.gain_idx = calframe.gain_idx
            simframe.rn_idx = calframe.rn_idx
            simframe.varISO.set(ISO[self.cnum][calframe.gain_idx])
            simframe.varGain.set(GAIN[self.cnum][0][calframe.gain_idx])
            simframe.varRN.set(RN[self.cnum][0][calframe.rn_idx])
            simframe.varExp.set('%g' % calframe.exposure)
            simframe.varDF.set('%g' % calframe.df)
            simframe.varSF.set('%g' % (convSig(calframe.sf, True) if self.lumSignalType.get() \
                                                                    else calframe.sf))
            simframe.varTF.set(0 if calframe.tf == 0 \
                               else ('%g' % (convSig(calframe.tf, True) if self.lumSignalType.get() \
                                                                          else calframe.tf)))
            simframe.varSubs.set(1)
            
            simframe.dataCalculated = False # Previously calculated data is no longer valid
            simframe.updateSensorLabels() # Update sensor info labels in case the ISO has changed
            simframe.emptyInfoLabels() # Clear other info labels
            calframe.varMessageLabel.set('Input transfered to Image Simulator.' \
                                         if calframe.varUseDark.get() \
                                         else 'Input transfered. Note that transfered signal ' \
                                       + 'data does not contain a separate value for dark current.')
        
        # If Plotting Tool is the active frame
        elif self.plMode.get():
        
            simframe.setDefaultValues() # Reset Image Simulator frame
        
            # Set values that are not invalid
            
            simframe.gain_idx = plotframe.gain_idx
            simframe.rn_idx = plotframe.rn_idx
            simframe.varISO.set(ISO[self.cnum][plotframe.gain_idx])
            simframe.varGain.set(GAIN[self.cnum][0][plotframe.gain_idx])
            simframe.varRN.set(RN[self.cnum][0][plotframe.rn_idx])
            
            
            try:
                simframe.varExp.set('%g' % plotframe.varExp.get())
            except ValueError:
                pass
        
            try:
                simframe.varDF.set('%g' % plotframe.varDF.get())
            except ValueError:
                pass
        
            try:
                simframe.varSF.set('%g' % plotframe.varSF.get())
            except ValueError:
                pass
            
            try:
                simframe.varTF.set('%g' % plotframe.varTF.get())
            except ValueError:
                pass
            
            simframe.varSubs.set(1)
            
            simframe.updateSensorLabels() # Update sensor info labels in case the ISO has changed
            simframe.emptyInfoLabels() # Clear other info labels
            plotframe.varMessageLabel.set('Input transfered to Image Simulator.')
        
    def transferToPlot(self):
    
        '''Transfer relevant inputted or calculated values to widgets in the Plotting Tool frame.'''
    
        calframe = self.frames[ImageCalculator]
        simframe = self.frames[ImageSimulator]
        plotframe = self.frames[PlottingTool]
        
        # If Image Calculator is the active frame
        if self.calMode.get():
        
            # Show error message if flux data hasn't been calculated
            if not calframe.dataCalculated:
                calframe.varMessageLabel.set('Data must be calculated before transfering input.')
                return None
        
            # Set values
            plotframe.gain_idx = calframe.gain_idx
            plotframe.rn_idx = calframe.rn_idx
            plotframe.varISO.set(ISO[self.cnum][calframe.gain_idx])
            plotframe.varGain.set(GAIN[self.cnum][0][calframe.gain_idx])
            plotframe.varRN.set(RN[self.cnum][0][calframe.rn_idx])
            plotframe.varExp.set('%g' % calframe.exposure)
            plotframe.varDF.set('%g' % calframe.df)
            plotframe.varSF.set('%g' % (convSig(calframe.sf, True) if self.lumSignalType.get() \
                                                                     else calframe.sf))
            plotframe.varTF.set(0 if calframe.tf == 0 \
                                else ('%g' % (convSig(calframe.tf, True) if self.lumSignalType.get() \
                                                                          else calframe.tf)))
            
            plotframe.ax.cla() # Clear plot
            calframe.varMessageLabel.set('Input transfered to Plotting Tool.' \
                                         if calframe.varUseDark.get() \
                                         else 'Input transfered. Note that transfered signal data ' \
                                            + 'does not contain a separate value for dark current.')
        
        # If Plotting Tool is the active frame
        elif self.simMode.get():
        
            plotframe.setDefaultValues() # Reset Plotting Tool frame
        
            # Set values that are not invalid
        
            plotframe.gain_idx = simframe.gain_idx
            plotframe.rn_idx = simframe.rn_idx
            plotframe.varISO.set(ISO[self.cnum][simframe.gain_idx])
            plotframe.varGain.set(GAIN[self.cnum][0][simframe.gain_idx])
            plotframe.varRN.set(RN[self.cnum][0][simframe.rn_idx])
            
            try:
                plotframe.varExp.set('%g' % simframe.varExp.get())
            except ValueError:
                pass
        
            try:
                plotframe.varDF.set('%g' % simframe.varDF.get())
            except ValueError:
                pass
        
            try:
                plotframe.varSF.set('%g' % simframe.varSF.get())
            except ValueError:
                pass
            
            try:
                plotframe.varTF.set('%g' % simframe.varTF.get())
            except ValueError:
                pass
            
            plotframe.ax.cla() # Clear plot
            simframe.varMessageLabel.set('Input transfered to Plotting Tool.')
    
    def setElectronSignalType(self):
    
        '''Use electron flux as signal quantity.'''
    
        # Do nothing if electron flux is already used
        if not self.lumSignalType.get():
            self.electronSignalType.set(1)
            return None
            
        self.lumSignalType.set(0)
        self.electronSignalType.set(1)
    
        calframe = self.frames[ImageCalculator]
        simframe = self.frames[ImageSimulator]
        plotframe = self.frames[PlottingTool]
        
        # Change unit labels
        calframe.varSFLabel.set('e-/s')
        calframe.varTFLabel.set('e-/s')
        
        simframe.varSFLabel.set('e-/s')
        simframe.varTFLabel.set('e-/s')
        
        plotframe.varSFLabel.set('e-/s')
        plotframe.varTFLabel.set('e-/s')
        
        # Change tooltips
        if self.tooltipsOn.get():
            createToolTip(calframe.labelSF2, TTSFElectron if calframe.varUseDark.get() \
                                             or self.isDSLR else TTDSFElectron, self.tt_fs)
            createToolTip(calframe.labelTF2, TTTFElectron, self.tt_fs)
            createToolTip(simframe.entrySF, TTSFElectron, self.tt_fs)
            createToolTip(simframe.entryTF, TTTFElectron, self.tt_fs)
            createToolTip(plotframe.entrySF, TTSFElectron, self.tt_fs)
            createToolTip(plotframe.entryTF, TTTFElectron, self.tt_fs)
        
        # Change displayed flux values if they have been calculated
        if calframe.dataCalculated:
            calframe.varSFInfo.set('%.3g' % (calframe.sf)) 
            calframe.varTFInfo.set('-' if calframe.tf == 0 else '%.3g' % (calframe.tf))
            
            calframe.labelSF2.configure(background=DEFAULT_BG, foreground='black')
            calframe.labelTF2.configure(background=DEFAULT_BG, foreground='black')
            
        self.currentFrame().varMessageLabel.set('Using electron flux as signal quantity.')
            
    def setLumSignalType(self):
    
        '''Use luminance as signal quantity.'''
    
        # Do nothing if luminance is already used
        if not self.electronSignalType.get():
            self.lumSignalType.set(1)
            return None
            
        if not self.hasQE:
            self.lumSignalType.set(0)
            self.currentFrame().varMessageLabel\
                                .set('Camera doesn\'t have QE data. Cannot estimate luminance.')
            return None
            
        self.lumSignalType.set(1)
        self.electronSignalType.set(0)
    
        calframe = self.frames[ImageCalculator]
        simframe = self.frames[ImageSimulator]
        plotframe = self.frames[PlottingTool]
        
        # Change unit labels
        calframe.varSFLabel.set(u'mag/arcsec\u00B2')
        calframe.varTFLabel.set(u'mag/arcsec\u00B2')
        
        simframe.varSFLabel.set(u'mag/arcsec\u00B2')
        simframe.varTFLabel.set(u'mag/arcsec\u00B2')
        
        plotframe.varSFLabel.set(u'mag/arcsec\u00B2')
        plotframe.varTFLabel.set(u'mag/arcsec\u00B2')
        
        # Change tooltips
        if self.tooltipsOn.get():
            createToolTip(calframe.labelSF2, TTSFLum if calframe.varUseDark.get() \
                                             or self.isDSLR else TTDSFPhoton, self.tt_fs)
            createToolTip(calframe.labelTF2, TTTFLum, self.tt_fs)
            createToolTip(simframe.entrySF, TTSFLum, self.tt_fs)
            createToolTip(simframe.entryTF, TTTFLum, self.tt_fs)
            createToolTip(plotframe.entrySF, TTSFLum, self.tt_fs)
            createToolTip(plotframe.entryTF, TTTFLum, self.tt_fs)
        
        # Change displayed flux values if they have been calculated
        if calframe.dataCalculated:
        
            sf = convSig(calframe.sf, True)
            calframe.varSFInfo.set('%.4g' % sf)
            calframe.setLumColor(sf, calframe.labelSF2)
            
            if calframe.tf == 0:
                calframe.varTFInfo.set('-')
                calframe.labelTF2.configure(background=DEFAULT_BG, foreground='black')
            else:
                tf = convSig(calframe.tf, True)
                calframe.varTFInfo.set('%.4g' % tf)
                calframe.setLumColor(tf, calframe.labelTF2) 
            
        self.currentFrame().varMessageLabel.set('Using luminance as signal quantity.')

    def setdBDRUnit(self):
        
        '''Use [dB] as unit for dynamic range.'''
    
        # Do nothing if dB is already used
        if not self.stopsDRUnit.get():
            self.dBDRUnit.set(1)
            return None
    
        self.dBDRUnit.set(1)
        self.stopsDRUnit.set(0)
        
        calframe = self.frames[ImageCalculator]
        simframe = self.frames[ImageSimulator]
        
        calframe.varDRLabel.set('dB')
        simframe.varDRLabel.set('dB')
        
        # Convert existing DR values from stops to dB
        
        factor = 10*np.log(2.0)/np.log(10.0)
        
        if calframe.dataCalculated: calframe.varDRInfo.set('%.1f' % (calframe.dr*factor))
            
        if simframe.dataCalculated: simframe.varDRInfo.set('%.1f' % (simframe.dr*factor))
    
    def setStopsDRUnit(self):
        
        '''Use [stops] as unit for dynamic range.'''
    
        # Do nothing if stops is already used
        if not self.dBDRUnit.get():
            self.stopsDRUnit.set(1)
            return None
            
        self.dBDRUnit.set(0)
        self.stopsDRUnit.set(1)
        
        calframe = self.frames[ImageCalculator]
        simframe = self.frames[ImageSimulator]
        
        calframe.varDRLabel.set('stops')
        simframe.varDRLabel.set('stops')
        
        # Convert existing DR values from dB to stops
        
        if calframe.dataCalculated: calframe.varDRInfo.set('%.1f' % calframe.dr)
            
        if simframe.dataCalculated: simframe.varDRInfo.set('%.1f' % simframe.dr)
        
    def addIcon(self, window):
    
        '''Set icon if it exists.'''
    
        try:
            window.iconbitmap('aplab_icon.ico')
        except:
            pass
        
    def currentFrame(self):
    
        '''Returns the class corresponding to the currently active frame.'''
    
        if self.anMode.get():
            frame = self.frames[ImageAnalyser]
        elif self.calMode.get():
            frame = self.frames[ImageCalculator]
        elif self.simMode.get():
            frame = self.frames[ImageSimulator]
        else:
            frame = self.frames[PlottingTool]
    
        return frame

    def toggleTooltips(self):
    
        '''Turn tooltips on or off.'''
    
        if self.tooltipsOn.get():
        
            self.frames[ImageCalculator].deactivateTooltips()
            self.frames[ImageSimulator].deactivateTooltips()
            self.frames[PlottingTool].deactivateTooltips()
        
            self.tooltipsOn.set(0)
            
            self.currentFrame().varMessageLabel.set('Tooltips deactivated.')
            
        else:
                                       
            self.frames[ImageCalculator].activateTooltips()
            self.frames[ImageSimulator].activateTooltips()
            self.frames[PlottingTool].activateTooltips()
            
            self.tooltipsOn.set(1)
    
            self.currentFrame().varMessageLabel.set('Tooltips activated.')

    def toogleDefaultTTState(self):

        '''Toggle whether tooltips will be shown automatically on startup.'''
    
        self.menuTT.delete(1)
            
        file = open('cameradata.txt', 'r')
        lines = file.read().split('\n')
        file.close()
        
        file = open('cameradata.txt', 'w')
        
        for line in lines[:-1]:
            file.write(line + '\n')
        
        if self.defaultTTState.get():
        
            self.menuTT.insert_command(1, label='Turn on as default', command=self.toogleDefaultTTState)
            
            file.write(lines[-1].split(',')[0] + ', Tooltips: off,' + lines[-1].split(',')[2])
            
            self.defaultTTState.set(0)
            
            self.currentFrame().varMessageLabel.set('Default tooltip state: off')
            
        else:
        
            self.menuTT.insert_command(1, label='Turn off as default', command=self.toogleDefaultTTState)
            
            file.write(lines[-1].split(',')[0] + ', Tooltips: on,' + lines[-1].split(',')[2])
            
            self.defaultTTState.set(1)
            
            self.currentFrame().varMessageLabel.set('Default tooltip state: on')
            
        file.close()

    def changeFS(self):
    
        '''Change application font size.'''
    
        fs_vals = [7, 8, 9, 10, 11, 12, 13, 14, 15]
        
        varFS = tk.IntVar()
        varFS.set(self.small_fs)
        
        self.menubar.entryconfig(1, state='disabled')
        self.menubar.entryconfig(2, state='disabled')
        self.menubar.entryconfig(3, state='disabled')
        self.menubar.entryconfig(4, state='disabled')
    
        # Setup window
        topFS = tk.Toplevel()
        topFS.title('Change font size')
        setupWindow(topFS, 150, 130)
        self.addIcon(topFS)
        topFS.focus_force()
        
        labelFS = ttk.Label(topFS, text='Choose font size:', anchor='center')
        optionFS = ttk.OptionMenu(topFS, varFS, None, *fs_vals)
        buttonFS = ttk.Button(topFS, text='OK', command=lambda: setNewFS(self, self.cnum, self.tnum,
                              varFS.get()))
        
        labelFS.pack(side='top', pady=(12*scsy, 0), expand=True)
        optionFS.pack(side='top', pady=12*scsy, expand=True)
        buttonFS.pack(side='top', pady=(0, 12*scsy), expand=True)
    
        self.currentFrame().varMessageLabel.set('Warning: changing font size ' \
                                                + 'will restart the application.')
                                                            
        self.wait_window(topFS)
        try:
            self.menubar.entryconfig(1, state='normal')
            if not self.anMode.get(): self.menubar.entryconfig(2, state='normal')
            self.menubar.entryconfig(3, state='normal')
            self.menubar.entryconfig(4, state='normal')
        except:
            pass
    
    def clearInput(self):
    
        '''Reset input widgets in the active tool.'''
    
        frame = self.currentFrame()
        
        def ok():
        
            frame.setDefaultValues()
                
            if self.calMode.get():
                frame.toggleDarkInputMode()
            elif self.plMode.get():
                frame.toggleActiveWidgets(frame.plotList[0])
                
            topWarning.destroy()
                
        self.menubar.entryconfig(1, state='disabled')
        self.menubar.entryconfig(2, state='disabled')
        self.menubar.entryconfig(3, state='disabled')
        self.menubar.entryconfig(4, state='disabled')
    
        # Setup window
        topWarning = tk.Toplevel()
        topWarning.title('Warning')
        self.addIcon(topWarning)
        setupWindow(topWarning, 300, 145)
        topWarning.focus_force()
        
        tk.Label(topWarning, text='Are you sure you want to\nclear the inputted information?',
                 font=self.small_font).pack(side='top', pady=(20*scsy, 5*scsy), expand=True)
        
        frameButtons = ttk.Frame(topWarning)
        frameButtons.pack(side='top', expand=True, pady=(0, 10*scsy))
        ttk.Button(frameButtons, text='Yes', command=ok).grid(row=0, column=0)
        ttk.Button(frameButtons, text='Cancel',
                   command=lambda: topWarning.destroy()).grid(row=0, column=1)
        
        self.wait_window(topWarning)
        try:
            self.menubar.entryconfig(1, state='normal')
            self.menubar.entryconfig(2, state='normal')
            self.menubar.entryconfig(3, state='normal')
            self.menubar.entryconfig(4, state='normal')
        except:
            pass
    
    def setDMSAngleUnit(self):
    
        '''Use [deg/min/sex] as angle unit.'''
    
        # Do nothing if DMS is already used
        if not self.degAngleUnit.get():
            self.dmsAngleUnit.set(1)
            return None
        
        self.dmsAngleUnit.set(1)
        self.degAngleUnit.set(0)
        
        self.frames[ImageAnalyser].updateAngle()
    
    def setDegAngleUnit(self):
    
        '''Use [degree] as angle unit.'''
    
        # Do nothing if deg is already used
        if not self.dmsAngleUnit.get():
            self.degAngleUnit.set(1)
            return None
            
        self.dmsAngleUnit.set(0)
        self.degAngleUnit.set(1)
        
        self.frames[ImageAnalyser].updateAngle()
        
     
class ImageCalculator(ttk.Frame):
    
    def __init__(self, parent, controller):
    
        '''Initialize Image Calculator frame.'''
    
        ttk.Frame.__init__(self, parent)
        
        self.cont = controller
        small_font = self.cont.small_font
        medium_font = self.cont.medium_font
        large_font = self.cont.large_font
        
        # Define attributes
        
        self.varISO = tk.IntVar()
        self.varGain = tk.DoubleVar()
        self.varRN = tk.DoubleVar()
        self.varExp = tk.DoubleVar()
        self.varUseDark = tk.IntVar()
        self.varDark = tk.DoubleVar()
        self.varBGN = tk.DoubleVar()
        self.varBGL = tk.DoubleVar()
        self.varTarget = tk.DoubleVar()
        self.varStretch = tk.IntVar()
        
        self.varDarkLabel = tk.StringVar()
        self.varSNTypeLabel = tk.StringVar()
        self.varSFTypeLabel = tk.StringVar()
        self.varMessageLabel = tk.StringVar()
        
        self.varGainInfo = tk.StringVar()
        self.varSatCapInfo = tk.StringVar()
        self.varBLInfo = tk.StringVar()
        self.varWLInfo = tk.StringVar()
        self.varPSInfo = tk.StringVar()
        self.varQEInfo = tk.StringVar()
        
        self.varFLInfo = tk.StringVar()
        self.varEFLInfo = tk.StringVar()
        self.varAPInfo = tk.StringVar()
        self.varFRInfo = tk.StringVar()
        self.varISInfo = tk.StringVar()
        self.varRLInfo = tk.StringVar()
        
        self.varDFInfo = tk.StringVar()
        self.varSFInfo = tk.StringVar()
        self.varTFInfo = tk.StringVar()
        self.varSNRInfo = tk.StringVar()
        self.varDRInfo = tk.StringVar()
        
        self.varRNInfo = tk.StringVar()
        self.varSNInfo = tk.StringVar()
        self.varDNInfo = tk.StringVar()
        self.varTBGNInfo = tk.StringVar()
        
        self.varDRLabel = tk.StringVar()
        self.varRNLabel = tk.StringVar()
        self.varDNLabel = tk.StringVar()
        self.varSNLabel = tk.StringVar()
        self.varTBGNLabel = tk.StringVar()
        self.varSFLabel = tk.StringVar()
        self.varTFLabel = tk.StringVar()
        
        # Set default attribute values
        
        self.varDRLabel.set('stops')
        self.varRNLabel.set('e-')
        self.varDNLabel.set('e-')
        self.varSNLabel.set('e-')
        self.varTBGNLabel.set('e-')
        self.varSFLabel.set(u'mag/arcsec\u00B2' if self.cont.hasQE else 'e-/s')
        self.varTFLabel.set(u'mag/arcsec\u00B2' if self.cont.hasQE else 'e-/s')
        
        # Define frames
        
        frameHeader = ttk.Frame(self)
        
        frameContent = ttk.Frame(self)
        
        frameLeft = ttk.Frame(frameContent)
        frameMiddle = ttk.Frame(frameContent)
        frameRight = ttk.Frame(frameContent)
        
        frameUpMiddle = ttk.Frame(frameMiddle)
        frameLowMiddle = ttk.Frame(frameMiddle)
        
        frameSignal = ttk.Frame(frameRight, borderwidth=2, relief='groove')
        frameNoise = ttk.Frame(frameRight, borderwidth=2, relief='groove')
        
        frameOptics = ttk.Frame(frameLeft, borderwidth=2, relief='groove')
        frameSensor = ttk.Frame(frameLeft, borderwidth=2, relief='groove')
        
        frameMessage = ttk.Frame(self)
        
        # Place frames
        
        frameHeader.pack(side='top', fill='x')
        
        frameContent.pack(side='top', fill='both', expand=True)
        
        frameLeft.pack(side='left', padx=(30*scsx, 0), expand=True)
        frameMiddle.pack(side='left', expand=True)
        frameRight.pack(side='right', padx=(0, 30*scsx), expand=True)
        
        frameOptics.pack(side='top', pady=(25*scsy, 50*scsy), expand=True)
        ttk.Label(frameLeft, text='User modified camera/optics data is displayed in blue',
                  foreground='dimgray').pack(side='bottom', pady=(8*scsy, 25*scsy))
        frameSensor.pack(side='bottom', expand=True)
        
        frameUpMiddle.pack(side='top', pady=(25*scsy, 20*scsy), expand=True)
        frameLowMiddle.pack(side='bottom', pady=(0, 25*scsy), expand=True)
        
        frameSignal.pack(side='top', pady=(25*scsy, 50*scsy), expand=True)
        frameNoise.pack(side='bottom', pady=(0, 25*scsy), expand=True)
        
        frameMessage.pack(side='bottom', fill='x')
        
        # *** Header frame ***
        
        labelHeader = ttk.Label(frameHeader, text='Image Calculator', font=large_font, anchor='center')
        
        frameNames = ttk.Frame(frameHeader)
        labelCamName = ttk.Label(frameNames, textvariable=self.cont.varCamName, anchor='center')
        labelTelName = ttk.Label(frameNames, textvariable=self.cont.varTelName, anchor='center')
        labelFLMod = ttk.Label(frameNames, textvariable=self.cont.varFLMod, anchor='center')
        
        labelHeader.pack(side='top', pady=3*scsy)
        
        ttk.Separator(frameHeader, orient='horizontal').pack(side='top', fill='x')
        
        frameNames.pack(side='top', fill='x')
        labelCamName.pack(side='left', expand=True)
        labelTelName.pack(side='left', expand=True)
        labelFLMod.pack(side='right', expand=True)
        
        # *** Left frame ***
        
        # Define optics frame widgets
        
        labelOptics = ttk.Label(frameOptics, text='Optics', font=medium_font, anchor='center', width=28)
        labelOptics.grid(row=0, column=0, columnspan=3, pady=5*scsy)
        
        labelFL = ttk.Label(frameOptics, text='Focal length: ')
        self.labelFL2 = ttk.Label(frameOptics, textvariable=self.varFLInfo, anchor='center', width=7)
        labelFL3 = ttk.Label(frameOptics, text='mm')
        
        labelEFL = ttk.Label(frameOptics, text='Effective focal length: ')
        self.labelEFL2 = ttk.Label(frameOptics, textvariable=self.varEFLInfo, anchor='center', width=7)
        labelEFL3 = ttk.Label(frameOptics, text='mm')
        
        labelAP = ttk.Label(frameOptics, text='Aperture diameter: ')
        self.labelAP2 = ttk.Label(frameOptics, textvariable=self.varAPInfo, anchor='center', width=7)
        labelAP3 = ttk.Label(frameOptics, text='mm')
        
        labelFR = ttk.Label(frameOptics, text='Focal ratio: ')
        self.labelFR2 = ttk.Label(frameOptics, textvariable=self.varFRInfo, anchor='center', width=7)
        
        labelIS = ttk.Label(frameOptics, text='Image scale: ')
        self.labelIS2 = ttk.Label(frameOptics, textvariable=self.varISInfo, anchor='center', width=7)
        labelIS3 = ttk.Label(frameOptics, text='arcsec/pixel')
        
        labelRL = ttk.Label(frameOptics, text='Angular resolution limit: ')
        self.labelRL2 = ttk.Label(frameOptics, textvariable=self.varRLInfo, anchor='center', width=7)
        labelRL3 = ttk.Label(frameOptics, text='arcsec')
        
        # Define sensor frame widgets
        
        labelSensor = ttk.Label(frameSensor, text='Sensor', font=medium_font, anchor='center',
                                width=28)
        labelSensor.grid(row=0, column=0, columnspan=3, pady=5*scsy)
        
        labelGainI = ttk.Label(frameSensor, text='Gain: ')
        self.labelGainI2 = ttk.Label(frameSensor, textvariable=self.varGainInfo, anchor='center',
                                     width=7)
        labelGainI3 = ttk.Label(frameSensor, text='e-/ADU')
        
        labelSatCap = ttk.Label(frameSensor, text='Saturation capacity: ')
        self.labelSatCap2 = ttk.Label(frameSensor, textvariable=self.varSatCapInfo, anchor='center',
                                      width=7)
        labelSatCap3 = ttk.Label(frameSensor, text='e-')
        
        labelBL = ttk.Label(frameSensor, text='Black level: ')
        self.labelBL2 = ttk.Label(frameSensor, textvariable=self.varBLInfo, anchor='center', width=7)
        labelBL3 = ttk.Label(frameSensor, text='ADU')
        
        labelWL = ttk.Label(frameSensor, text='White level: ')
        self.labelWL2 = ttk.Label(frameSensor, textvariable=self.varWLInfo, anchor='center', width=7)
        labelWL3 = ttk.Label(frameSensor, text='ADU')
        
        labelPS = ttk.Label(frameSensor, text='Pixel size: ')
        self.labelPS2 = ttk.Label(frameSensor, textvariable=self.varPSInfo, anchor='center', width=7)
        labelPS3 = ttk.Label(frameSensor, text=u'\u03bcm')
        
        labelQE = ttk.Label(frameSensor, text='Quantum efficiency: ')
        self.labelQE2 = ttk.Label(frameSensor, textvariable=self.varQEInfo, anchor='center', width=7)
        labelQE3 = ttk.Label(frameSensor, text='%')
        
        # Place optics frame widgets
        
        labelFL.grid(row=1, column=0, sticky='W')
        self.labelFL2.grid(row=1, column=1)
        labelFL3.grid(row=1, column=2, sticky='W')
        
        labelEFL.grid(row=2, column=0, sticky='W')
        self.labelEFL2.grid(row=2, column=1)
        labelEFL3.grid(row=2, column=2, sticky='W')
        
        labelAP.grid(row=3, column=0, sticky='W')
        self.labelAP2.grid(row=3, column=1)
        labelAP3.grid(row=3, column=2, sticky='W')
        
        labelFR.grid(row=4, column=0, sticky='W')
        self.labelFR2.grid(row=4, column=1)
        
        labelIS.grid(row=5, column=0, sticky='W')
        self.labelIS2.grid(row=5, column=1)
        labelIS3.grid(row=5, column=2, sticky='W')
        
        labelRL.grid(row=6, column=0, sticky='W')
        self.labelRL2.grid(row=6, column=1)
        labelRL3.grid(row=6, column=2, sticky='W')
        
        # Place sensor frame widgets
        
        labelGainI.grid(row=1, column=0, sticky='W')
        self.labelGainI2.grid(row=1, column=1)
        labelGainI3.grid(row=1, column=2, sticky='W')
        
        labelSatCap.grid(row=2, column=0, sticky='W')
        self.labelSatCap2.grid(row=2, column=1)
        labelSatCap3.grid(row=2, column=2, sticky='W')
        
        labelBL.grid(row=3, column=0, sticky='W')
        self.labelBL2.grid(row=3, column=1)
        labelBL3.grid(row=3, column=2, sticky='W')
        
        labelWL.grid(row=4, column=0, sticky='W')
        self.labelWL2.grid(row=4, column=1)
        labelWL3.grid(row=4, column=2, sticky='W')
        
        ttk.Separator(frameSensor, orient='horizontal').grid(row=5, column=0, columnspan=3, sticky='EW')
        
        labelPS.grid(row=6, column=0, sticky='W')
        self.labelPS2.grid(row=6, column=1)
        labelPS3.grid(row=6, column=2, sticky='W')
        
        labelQE.grid(row=7, column=0, sticky='W')
        self.labelQE2.grid(row=7, column=1)
        labelQE3.grid(row=7, column=2, sticky='W')
        
        # *** Right frame ***
        
        # Define signal frame widgets
        
        labelSignal = ttk.Label(frameSignal, text='Signal', font=medium_font, anchor='center', width=28)
        labelSignal.grid(row=0, column=0, columnspan=3, pady=5*scsy)
        
        self.labelDF = ttk.Label(frameSignal, text='Dark current: ')
        self.labelDF2 = ttk.Label(frameSignal, textvariable=self.varDFInfo, anchor='center', width=7)
        self.labelDF3 = ttk.Label(frameSignal, text='e-/s')
        
        labelSF = ttk.Label(frameSignal, textvariable=self.varSFTypeLabel)
        self.labelSF2 = ttk.Label(frameSignal, textvariable=self.varSFInfo, anchor='center', width=7)
        labelSF3 = ttk.Label(frameSignal, textvariable=self.varSFLabel, font=small_font)
        
        labelTF = ttk.Label(frameSignal, text='Target signal: ')
        self.labelTF2 = ttk.Label(frameSignal, textvariable=self.varTFInfo, anchor='center', width=7)
        labelTF3 = ttk.Label(frameSignal, textvariable=self.varTFLabel)
        
        labelSNR = ttk.Label(frameSignal, text='Target SNR:')
        self.labelSNR2 = ttk.Label(frameSignal, textvariable=self.varSNRInfo, anchor='center', width=7)
        
        labelDR = ttk.Label(frameSignal, text='Dynamic range:')
        self.labelDR2 = ttk.Label(frameSignal, textvariable=self.varDRInfo, anchor='center', width=7)
        labelDR3 = ttk.Label(frameSignal, textvariable=self.varDRLabel)
        
        # Define noise frame widgets
        
        labelNoiseHeader = ttk.Label(frameNoise, text='Noise', font=medium_font, anchor='center',
                                     width=28)
        labelNoiseHeader.grid(row=0, column=0, columnspan=3, pady=5*scsy)
        
        labelRNI = ttk.Label(frameNoise, text='Read noise: ')
        self.labelRNI2 = ttk.Label(frameNoise, textvariable=self.varRNInfo, anchor='center', width=5)
        labelRNI3 = ttk.Label(frameNoise, textvariable=self.varRNLabel)
        
        self.labelDN = ttk.Label(frameNoise, text='Dark noise: ')
        self.labelDN2 = ttk.Label(frameNoise, textvariable=self.varDNInfo, anchor='center', width=5)
        self.labelDN3 = ttk.Label(frameNoise, textvariable=self.varDNLabel)
        
        labelSN = ttk.Label(frameNoise, textvariable=self.varSNTypeLabel)
        self.labelSN2 = ttk.Label(frameNoise, textvariable=self.varSNInfo, anchor='center', width=5)
        labelSN3 = ttk.Label(frameNoise, textvariable=self.varSNLabel)
        
        labelTBGN = ttk.Label(frameNoise, text='Total background noise: ')
        self.labelTBGN2 = ttk.Label(frameNoise, textvariable=self.varTBGNInfo, anchor='center', width=5)
        labelTBGN3 = ttk.Label(frameNoise, textvariable=self.varTBGNLabel)
        
        # Place signal frame widgets
        
        self.labelDF.grid(row=1, column=0, sticky='W')
        self.labelDF2.grid(row=1, column=1)
        self.labelDF3.grid(row=1, column=2, sticky='W')
        
        labelSF.grid(row=2, column=0, sticky='W')
        self.labelSF2.grid(row=2, column=1)
        labelSF3.grid(row=2, column=2, sticky='W')
        
        labelTF.grid(row=3, column=0, sticky='W')
        self.labelTF2.grid(row=3, column=1)
        labelTF3.grid(row=3, column=2, sticky='W')
        
        ttk.Separator(frameSignal, orient='horizontal').grid(row=4, column=0, columnspan=3,
                                                             sticky='EW')
        
        labelSNR.grid(row=5, column=0, sticky='W')
        self.labelSNR2.grid(row=5, column=1)
        
        labelDR.grid(row=6, column=0, sticky='W')
        self.labelDR2.grid(row=6, column=1)
        labelDR3.grid(row=6, column=2, sticky='W')
        
        # Place noise frame widgets
        
        labelRNI.grid(row=1, column=0, sticky='W')
        self.labelRNI2.grid(row=1, column=1)
        labelRNI3.grid(row=1, column=2, sticky='W')
        
        self.labelDN.grid(row=2, column=0, sticky='W')
        self.labelDN2.grid(row=2, column=1)
        self.labelDN3.grid(row=2, column=2, sticky='W')
        
        labelSN.grid(row=3, column=0, sticky='W')
        self.labelSN2.grid(row=3, column=1)
        labelSN3.grid(row=3, column=2, sticky='W')
        
        ttk.Separator(frameNoise, orient='horizontal').grid(row=4, column=0, columnspan=3, sticky='EW')
        
        labelTBGN.grid(row=5, column=0, sticky='W')
        self.labelTBGN2.grid(row=5, column=1)
        labelTBGN3.grid(row=5, column=2, sticky='W')
        
        # *** Middle frame ***
        
        # Define upper middle frame widgets
        
        labelInput = ttk.Label(frameUpMiddle, text='Image data', font=medium_font, anchor='center')
        
        self.labelISO = ttk.Label(frameUpMiddle, text='ISO:')
        self.optionISO = ttk.OptionMenu(frameUpMiddle, self.varISO, None, *ISO[self.cont.cnum],
                                        command=self.updateISO)
                                        
        self.labelGain = ttk.Label(frameUpMiddle, text='Gain:')
        self.optionGain = ttk.OptionMenu(frameUpMiddle, self.varGain, None, *GAIN[self.cont.cnum][0],
                                         command=self.updateGain)
        self.labelGain2 = ttk.Label(frameUpMiddle, text='e-/ADU')
        
        self.labelRN = ttk.Label(frameUpMiddle, text='Read noise:')
        self.optionRN = ttk.OptionMenu(frameUpMiddle, self.varRN, None, *RN[self.cont.cnum][0],
                                       command=self.updateRN)
        self.labelRN2 = ttk.Label(frameUpMiddle, text='e-')
        
        self.setDefaultValues()
        
        labelExp = ttk.Label(frameUpMiddle, text='Exposure time:')
        self.entryExp = ttk.Entry(frameUpMiddle, textvariable=self.varExp, width=9, font=small_font,
                                  background=DEFAULT_BG)
        labelExp2 = ttk.Label(frameUpMiddle, text='seconds')
        
        labelToggleDark = ttk.Label(frameUpMiddle, text='Use dark frame info:')
        self.checkbuttonToggleDark = tk.Checkbutton(frameUpMiddle, variable=self.varUseDark,
                                                    font=small_font, command=self.toggleDarkInputMode)
        labelToggleDark2 = ttk.Label(frameUpMiddle, text='', width=9)
        
        self.labelDark = ttk.Label(frameUpMiddle, textvariable=self.varDarkLabel)
        self.entryDark = ttk.Entry(frameUpMiddle, textvariable=self.varDark, font=small_font,
                                   background=DEFAULT_BG, width=9)
        self.labelDark2 = ttk.Label(frameUpMiddle, text='ADU')
        
        self.labelBGN = ttk.Label(frameUpMiddle, text='Background noise:')
        self.entryBGN = ttk.Entry(frameUpMiddle, textvariable=self.varBGN, font=small_font,
                                  background=DEFAULT_BG, width=9)
        self.labelBGN2 = ttk.Label(frameUpMiddle, text='ADU')
        
        labelBGL = ttk.Label(frameUpMiddle, text='Background level:')
        self.entryBGL = ttk.Entry(frameUpMiddle, textvariable=self.varBGL, font=small_font,
                                  background=DEFAULT_BG, width=9)
        labelBGL2 = ttk.Label(frameUpMiddle, text='ADU')
        
        labelTarget = ttk.Label(frameUpMiddle, text='Target level:')
        self.entryTarget = ttk.Entry(frameUpMiddle, textvariable=self.varTarget, font=small_font,
                                     background=DEFAULT_BG, width=9)
        labelTarget2 = ttk.Label(frameUpMiddle, text='ADU')
        
        # Define lower middle frame widgets
        
        buttonData = ttk.Button(frameLowMiddle, text='Calculate data', command=self.processInput,
                                width=14)
        buttonTransferSim = ttk.Button(frameLowMiddle, text='Transfer data to Image Simulator',
                                       command=self.cont.transferToSim, width=29)
        buttonTransferPlot = ttk.Button(frameLowMiddle, text='Transfer data to Plotting Tool',
                                        command=self.cont.transferToPlot, width=29)
        buttonClear = ttk.Button(frameLowMiddle, text='Clear input', command=self.cont.clearInput)                    
        
        # Place upper middle frame widgets
        
        labelInput.grid(row=0, column=0, columnspan=3, pady=(0, 10*scsy))
        
        labelExp.grid(row=3, column=0, sticky='W')
        self.entryExp.grid(row=3, column=1)
        labelExp2.grid(row=3, column=2, sticky='W')
        
        labelToggleDark.grid(row=4, column=0, sticky='W')
        self.checkbuttonToggleDark.grid(row=4, column=1)
        labelToggleDark2.grid(row=4, column=2, sticky='W')
        
        self.labelDark.grid(row=5, column=0, sticky='W')
        self.entryDark.grid(row=5, column=1)
        self.labelDark2.grid(row=5, column=2, sticky='W')
        
        labelBGL.grid(row=7, column=0, sticky='W')
        self.entryBGL.grid(row=7, column=1)
        labelBGL2.grid(row=7, column=2, sticky='W')
        
        labelTarget.grid(row=8, column=0, sticky='W')
        self.entryTarget.grid(row=8, column=1)
        labelTarget2.grid(row=8, column=2, sticky='W')
        
        # Place lower middle frame widgets
        
        buttonData.grid(row=0, column=0, pady=(0, 22*scsy))
        buttonTransferSim.grid(row=1, column=0)
        buttonTransferPlot.grid(row=2, column=0)
        buttonClear.grid(row=3, column=0, pady=(11*scsy, 0))
        
        # Place more widgets according to camera type
        self.reconfigureNonstaticWidgets()
        
        # *** Message frame ***
        
        labelMessage = ttk.Label(frameMessage, textvariable=self.varMessageLabel, anchor='center')
        ttk.Separator(frameMessage, orient='horizontal').pack(side='top', fill='x')
        labelMessage.pack(fill='x')
        
        if self.cont.tooltipsOn.get(): self.activateTooltips()

    def emptyInfoLabels(self):
    
        '''Clear labels showing calculated values.'''
    
        self.varSNRInfo.set('-')
        self.varDRInfo.set('-')
        self.varSNInfo.set('-')
        self.varDNInfo.set('-')
        self.varTBGNInfo.set('-')
        self.varDFInfo.set('-')
        try:
            self.labelSF2.configure(background=DEFAULT_BG, foreground='black')
            self.labelTF2.configure(background=DEFAULT_BG, foreground='black')
        except:
            pass
        self.varSFInfo.set('-')
        self.varTFInfo.set('-')
        
    def setDefaultValues(self):
    
        '''Set all relevant class attributes to their default values.'''
        
        # Variables to keep track of currently selected ISO, gain or read noise in the optionmenus
        self.gain_idx = 0
        self.rn_idx = 0
        
        self.dataCalculated = False # Used to indicate if calculated data exists
        
        # Default widget values
        
        self.varISO.set(ISO[self.cont.cnum][self.gain_idx])
        self.varGain.set(GAIN[self.cont.cnum][0][self.gain_idx])
        self.varRN.set(RN[self.cont.cnum][0][self.rn_idx])
        self.varExp.set('')
        self.varUseDark.set(1)
        self.varDark.set('')
        self.varBGN.set('')
        self.varBGL.set('')
        self.varTarget.set('')
        
        self.varDarkLabel.set('Dark frame noise:' if self.cont.isDSLR else 'Dark frame level:')
        self.varSNTypeLabel.set('Sky shot noise: ')
        self.varSFTypeLabel.set('Skyglow: ')
        self.varMessageLabel.set('')
        
        self.varGainInfo.set('%.3g' % GAIN[self.cont.cnum][0][self.gain_idx])
        self.varSatCapInfo.set('%d' % SAT_CAP[self.cont.cnum][0][self.gain_idx])
        self.varBLInfo.set('%d' % BLACK_LEVEL[self.cont.cnum][0][self.gain_idx])
        self.varWLInfo.set('%d' % WHITE_LEVEL[self.cont.cnum][0][self.gain_idx])
        self.varPSInfo.set('%g' % PIXEL_SIZE[self.cont.cnum][0])
        self.varQEInfo.set('-' if not self.cont.hasQE else ('%d' % (QE[self.cont.cnum][0]*100)))
        
        # Set text color according to whether the data is default or user added
        self.labelGainI2.configure(foreground=('black' \
                                   if GAIN[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelRNI2.configure(foreground=('black' \
                                 if RN[self.cont.cnum][1][self.rn_idx] == 0 else 'navy'))
        self.labelSatCap2.configure(foreground=('black' \
                                    if SAT_CAP[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelBL2.configure(foreground=('black' \
                                if BLACK_LEVEL[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelWL2.configure(foreground=('black' \
                                if WHITE_LEVEL[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelPS2.configure(foreground=('black' if PIXEL_SIZE[self.cont.cnum][1] == 0 else 'navy'))
        self.labelQE2.configure(foreground=('black' if QE[self.cont.cnum][1] == 0 else 'navy'))
        
        self.updateOpticsLabels()
        
        self.varRNInfo.set('%.1f' % RN[self.cont.cnum][0][self.rn_idx])
        
        self.emptyInfoLabels() # Clear labels
    
    def reconfigureNonstaticWidgets(self):
    
        '''Places widgets according to camera type.'''
    
        self.labelISO.grid_forget()
        self.optionISO.grid_forget()
                
        self.labelGain.grid_forget()
        self.optionGain.grid_forget()
        self.labelGain2.grid_forget()
            
        self.labelRN.grid_forget()
        self.optionRN.grid_forget()
        self.labelRN2.grid_forget()
        
        self.labelBGN.grid_forget()
        self.entryBGN.grid_forget()
        self.labelBGN2.grid_forget()
    
        # Set selectable values in the optionmenus according to camera model
        self.optionISO.set_menu(*([None] + list(ISO[self.cont.cnum])))
        self.optionGain.set_menu(*([None] + list(GAIN[self.cont.cnum][0])))
        self.optionRN.set_menu(*([None] + list(RN[self.cont.cnum][0])))
            
        if self.cont.isDSLR:
                
            # DSLRs use the ISO optionmenu and the background noise entry
                
            self.labelISO.grid(row=1, column=0, sticky='W')
            self.optionISO.grid(row=1, column=1)
            
            self.labelBGN.grid(row=6, column=0, sticky='W')
            self.entryBGN.grid(row=6, column=1)
            self.labelBGN2.grid(row=6, column=2, sticky='W')
                
        else:
                
            # CCDs use gain and/or read noise optionmenus if they have more than one value to use
                
            if len(GAIN[self.cont.cnum][0]) > 1:
                    
                self.labelGain.grid(row=1, column=0, sticky='W')
                self.optionGain.grid(row=1, column=1)
                self.labelGain2.grid(row=1, column=2, sticky='W')
                    
            if len(RN[self.cont.cnum][0]) > 1:
                    
                self.labelRN.grid(row=2, column=0, sticky='W')
                self.optionRN.grid(row=2, column=1)
                self.labelRN2.grid(row=2, column=2, sticky='W')

    def updateISO(self, selected_iso):
    
        '''Update index of selected ISO and update sensor labels.'''
        
        self.gain_idx = int(np.where(ISO[self.cont.cnum] == selected_iso)[0])
        self.rn_idx = self.gain_idx
        
        self.updateSensorLabels()
    
    def updateGain(self, selected_gain):
    
        '''Update index of selected gain and update sensor labels.'''
    
        self.gain_idx = int(np.where(GAIN[self.cont.cnum][0] == selected_gain)[0])
        
        self.updateSensorLabels()
    
    def updateRN(self, selected_rn):
            
        '''Update index of selected ISO and update sensor labels.'''
        
        self.rn_idx = int(np.where(RN[self.cont.cnum][0] == selected_rn)[0])
        
        self.updateSensorLabels()
    
    def updateSensorLabels(self):
    
        '''
        Update labels with the gain, read noise and saturation
        level values of currently selected ISO/gain/RN.
        '''
    
        self.varGainInfo.set('%.3g' % GAIN[self.cont.cnum][0][self.gain_idx])
        self.varRNInfo.set('%.1f' % RN[self.cont.cnum][0][self.rn_idx])
        self.varSatCapInfo.set('%d' % SAT_CAP[self.cont.cnum][0][self.gain_idx])
        self.varBLInfo.set('%d' % BLACK_LEVEL[self.cont.cnum][0][self.gain_idx])
        self.varWLInfo.set('%d' % WHITE_LEVEL[self.cont.cnum][0][self.gain_idx])
        
        # Set text color according to whether the data is default or user added
        self.labelGainI2.configure(foreground=('black' if GAIN[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelRNI2.configure(foreground=('black' if RN[self.cont.cnum][1][self.rn_idx] == 0 else 'navy'))
        self.labelSatCap2.configure(foreground=('black' if SAT_CAP[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelBL2.configure(foreground=('black' if BLACK_LEVEL[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelWL2.configure(foreground=('black' if WHITE_LEVEL[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
    
    def updateOpticsLabels(self):
    
        '''Update labels in the optics frame with the current values.'''
    
        self.varFLInfo.set('%g' % FOCAL_LENGTH[self.cont.tnum][0])
        self.varEFLInfo.set('%g' % (FOCAL_LENGTH[self.cont.tnum][0]*self.cont.FLModVal))
        self.varAPInfo.set('%g' % APERTURE[self.cont.tnum][0])
        self.varFRInfo.set(u'\u0192/%g' % round(FOCAL_LENGTH[self.cont.tnum][0]*self.cont.FLModVal\
                                                /APERTURE[self.cont.tnum][0], 1))
        self.varISInfo.set('%.3g' % (self.cont.ISVal))
        self.varRLInfo.set('%.2g' % (1.22*5.5e-4*180*3600/(APERTURE[self.cont.tnum][0]*np.pi)))
        
        # Set text color according to whether the data is default or user added
        self.labelFL2.configure(foreground=('black' if FOCAL_LENGTH[self.cont.tnum][1] == 0 else 'navy'))
        self.labelAP2.configure(foreground=('black' if APERTURE[self.cont.tnum][1] == 0 else 'navy'))
        
    def toggleDarkInputMode(self):
    
        '''Configure widets according to the state of the "Use dark input" checkbutton.'''
        
        self.labelDark.grid_forget()
        self.entryDark.grid_forget()
        self.labelDark2.grid_forget()
        
        self.labelDN.grid_forget()
        self.labelDN2.grid_forget()
        self.labelDN3.grid_forget()
        
        self.labelDF.grid_forget()
        self.labelDF2.grid_forget()
        self.labelDF3.grid_forget()
    
        if self.varUseDark.get() == 1:
        
            # Show dark input, noise and current widgets
            
            self.labelDark.grid(row=5, column=0, sticky='W')
            self.entryDark.grid(row=5, column=1)
            self.labelDark2.grid(row=5, column=2, sticky='W')
            
            self.labelDN.grid(row=2, column=0, sticky='W')
            self.labelDN2.grid(row=2, column=1)
            self.labelDN3.grid(row=2, column=2, sticky='W')
            
            self.labelDF.grid(row=1, column=0, sticky='W')
            self.labelDF2.grid(row=1, column=1)
            self.labelDF3.grid(row=1, column=2, sticky='W')
            
            # Change labels for skyglow noise/flux
            self.varSNTypeLabel.set('Sky shot noise: ')
            self.varSFTypeLabel.set('Skyglow: ')
            
            # Change tooltips
            if self.cont.tooltipsOn.get():
                createToolTip(self.labelSN2, TTSN, self.cont.tt_fs)
                createToolTip(self.labelSF2, TTSFLum if self.cont.lumSignalType.get() else TTSFElectron,
                              self.cont.tt_fs)
            
        else:
        
            # Dark input, noise and current widgets remain hidden
            
            # Change labels for skyglow noise/flux
            self.varSNTypeLabel.set('Sky and dark noise: ')
            
            if self.cont.tooltipsOn.get(): createToolTip(self.labelSN2, TTDSN, self.cont.tt_fs)
            
            if not self.cont.isDSLR:
            
                self.varSFTypeLabel.set('Background signal: ')
                
                if self.cont.tooltipsOn.get():
                    createToolTip(self.labelSF2, TTDSFPhoton if self.cont.lumSignalType.get() else TTDSFElectron,
                                  self.cont.tt_fs)
            
        self.emptyInfoLabels() # Clear labels
    
    def processInput(self):
    
        '''Check that the inputted values are valid, then run calculations method.'''
        
        try:
            self.exposure = self.varExp.get()
            
        except ValueError:
            self.varMessageLabel.set('Invalid input for exposure time.')
            self.emptyInfoLabels()
            return None
        
        self.use_dark = self.varUseDark.get()
        
        try:
            self.dark_input = self.varDark.get()
            
        except ValueError:
            if self.use_dark:
                self.varMessageLabel.set('Invalid input for dark frame noise.' \
                                         if self.cont.isDSLR else 'Invalid input for dark frame level.')
                self.emptyInfoLabels()
                return None
            else:
                self.dark_input = 0
        
        try:
            self.bgn = self.varBGN.get()
            
        except ValueError:
            if self.cont.isDSLR:
                self.varMessageLabel.set('Invalid input for background noise.')
                self.emptyInfoLabels()
                return None
            else:
                self.bgn = 0
        
        try:
            self.bgl = self.varBGL.get()
            
        except ValueError:
            self.varMessageLabel.set('Invalid input for background level.')
            self.emptyInfoLabels()
            return None
            
        try:
            self.target = self.varTarget.get()
            
        except ValueError:
            self.varTarget.set('')
            self.target = 0
        
        if self.cont.isDSLR:
        
            if self.bgl < BLACK_LEVEL[self.cont.cnum][0][self.gain_idx]:
                self.varMessageLabel.set('The background level cannot be lower than the black level.')
                self.emptyInfoLabels()
                return None
                
        elif self.use_dark:
        
            if self.dark_input < BLACK_LEVEL[self.cont.cnum][0][self.gain_idx]:
                self.varMessageLabel.set('The dark frame level cannot be lower than the black level.')
                self.emptyInfoLabels()
                return None
                
            if self.bgl < self.dark_input:
                self.varMessageLabel.set('The background level cannot be lower than the dark frame level.')
                self.emptyInfoLabels()
                return None
            
        if 0 < self.target < self.bgl:
            self.varMessageLabel.set('The target level cannot be lower than the background level.')
            self.emptyInfoLabels()
            return None
        
        if self.target > WHITE_LEVEL[self.cont.cnum][0][self.gain_idx]:
            self.varMessageLabel.set('The target level cannot be higher than the white level.')
            self.emptyInfoLabels()
            return None
        
        self.calculate()
    
    def calculate(self):
    
        '''Calculate SNR, dynamic range, noise and flux values and set to the corresponding labels.'''
        
        message = 'Image data calculated.'
        
        gain = GAIN[self.cont.cnum][0][self.gain_idx] # Gain [e-/ADU]
        rn = RN[self.cont.cnum][0][self.rn_idx]       # Read noise [e-]
        
        # For DSLRs
        if self.cont.isDSLR:
            
            if self.use_dark:
            
                dark_signal_e = (self.dark_input*gain)**2 - rn**2 # Signal from dark current [e-]
                
                # Show error if the provided dark frame noise (for DSLRs) is lower than the read noise
                if dark_signal_e < 0:
                    message = 'The dark frame noise cannot be lower than the read noise. Using ' \
                              + 'lowest possible value.'
                    self.varDark.set('%.3g' % (rn/gain))
                    dark_signal_e = 0
                    
            else:
                dark_signal_e = 0 # Set to 0 if dark frame noise is not provided
            
            # Signal from skyglow [e-]
            sky_signal_e = (self.bgl - BLACK_LEVEL[self.cont.cnum][0][self.gain_idx])*gain
            
            # Signal from target [e-]
            target_signal_e = 0 if self.target == 0 else (self.target - self.bgl)*gain
        
            sat_cap = SAT_CAP[self.cont.cnum][0][self.gain_idx] # Saturation capacity [e-]
                
            tbgn = self.bgn*gain # Total background noise [e-]
            
            if tbgn**2 < rn**2 + dark_signal_e:
                type = 'dark frame' if dark_signal_e > 0 else 'read'
                message = 'The background noise cannot be lower than the ' + type \
                          + ' noise. Using lowest possible value.'
                tbgn = np.sqrt(rn**2 + dark_signal_e)
                self.varBGN.set('%.3g' % (tbgn/gain))
                sky_signal_e = 0
            
            dn = np.sqrt(dark_signal_e)                   # Dark noise [e-]
            sn = np.sqrt(tbgn**2 - rn**2 - dark_signal_e) # Skyglow noise [e-]
     
            self.df = dark_signal_e/self.exposure   # Dark current [e-/s]
            self.sf = sky_signal_e/self.exposure    # Skyglow [e-/s]
            self.tf = target_signal_e/self.exposure # Target signal [e-/s]
        
        # For CCDs
        else:
            
            if self.use_dark:
                # Signal from dark current [e-]
                dark_signal_e = (self.dark_input - BLACK_LEVEL[self.cont.cnum][0][self.gain_idx])*gain
                sky_signal_e = (self.bgl - self.dark_input)*gain # Signal from skyglow [e-]
            else:
                dark_signal_e = 0 # Set to 0 if dark frame level is not provided
                sky_signal_e = (self.bgl - BLACK_LEVEL[self.cont.cnum][0][self.gain_idx])*gain
                
            # Signal from target [e-]
            target_signal_e = 0 if self.target == 0 else (self.target - self.bgl)*gain
                
            sat_cap = SAT_CAP[self.cont.cnum][0][self.gain_idx] # Saturation capacity [e-]
                
            dn = np.sqrt(dark_signal_e)                          # Dark noise [e-]
            sn = np.sqrt(sky_signal_e)                           # Skyglow noise [e-]
            tbgn = np.sqrt(rn**2 + dark_signal_e + sky_signal_e) # Total background noise [e-]
                
            self.df = dark_signal_e/self.exposure   # Dark current [e-/s]
            self.sf = sky_signal_e/self.exposure    # Skyglow [e-/s]
            self.tf = target_signal_e/self.exposure # Target signal [e-/s]
            
        # Signal to noise ratio
        snr = 0 if self.target == 0 else target_signal_e/np.sqrt(target_signal_e + tbgn**2)
        
        self.dr = np.log10(sat_cap/tbgn)/np.log10(2.0) # Dynamic range [stops]
        factor = 10*np.log(2.0)/np.log(10.0)
        
        # Update labels
        self.varSNRInfo.set('-' if self.target == 0 else '%.1f' % snr)
        self.varDRInfo.set('%.1f' % (self.dr if self.cont.stopsDRUnit.get() else self.dr*factor))
        self.varSNInfo.set('%.1f' % sn)
        self.varDNInfo.set('%.1f' % dn)
        self.varTBGNInfo.set('%.1f' % tbgn)
        self.varDFInfo.set('%.3g' % (self.df))
        
        if self.cont.lumSignalType.get():
        
            sf = convSig(self.sf, True)
            self.varSFInfo.set('%.4g' % sf)
            self.setLumColor(sf, self.labelSF2)
            
            if self.target != 0:
                tf = convSig(self.tf, True)
                self.varTFInfo.set('%.4g' % tf)
                self.setLumColor(tf, self.labelTF2)
            else:
                self.varTFInfo.set('-')
                self.labelTF2.configure(background=DEFAULT_BG, foreground='black')
        else:
            self.varSFInfo.set('%.3g' % (self.sf))
            
            self.varTFInfo.set('-' if self.target == 0 else '%.3g' % (self.tf))
            self.labelTF2.configure(background=DEFAULT_BG, foreground='black')
        
        self.dataCalculated = True
        
        self.varMessageLabel.set(message)
 
    def activateTooltips(self):
    
        '''Add tooltips to all relevant widgets.'''
        
        createToolTip(self.entryExp, TTExp, self.cont.tt_fs)
        createToolTip(self.checkbuttonToggleDark, TTUseDark, self.cont.tt_fs)
        createToolTip(self.entryDark, TTDarkNoise if self.cont.isDSLR else TTDarkLevel, self.cont.tt_fs)
        createToolTip(self.entryBGN, TTBGNoise, self.cont.tt_fs)
        createToolTip(self.entryBGL, TTBGLevel, self.cont.tt_fs)
        createToolTip(self.entryTarget, TTTarget, self.cont.tt_fs)
        createToolTip(self.labelSNR2, TTSNR, self.cont.tt_fs)
        createToolTip(self.labelDR2, TTDR, self.cont.tt_fs)
        createToolTip(self.labelFL2, TTFL, self.cont.tt_fs)
        createToolTip(self.labelEFL2, TTEFL, self.cont.tt_fs)
        createToolTip(self.labelAP2, TTAP, self.cont.tt_fs)
        createToolTip(self.labelFR2, TTFR, self.cont.tt_fs)
        createToolTip(self.labelIS2, TTIS, self.cont.tt_fs)
        createToolTip(self.labelRL2, TTRL, self.cont.tt_fs)
        createToolTip(self.labelGainI2, TTGain, self.cont.tt_fs)
        createToolTip(self.labelSatCap2, TTSatCap, self.cont.tt_fs)
        createToolTip(self.labelBL2, TTBL, self.cont.tt_fs)
        createToolTip(self.labelWL2, TTWL, self.cont.tt_fs)
        createToolTip(self.labelPS2, TTPS, self.cont.tt_fs)
        createToolTip(self.labelQE2, TTQE, self.cont.tt_fs)
        createToolTip(self.labelRNI2, TTRN, self.cont.tt_fs)
        createToolTip(self.labelDN2, TTDN, self.cont.tt_fs)
        createToolTip(self.labelSN2, TTSN, self.cont.tt_fs)
        createToolTip(self.labelTBGN2, TTTotN, self.cont.tt_fs)
        createToolTip(self.labelDF2, TTDF, self.cont.tt_fs)
        createToolTip(self.labelSF2, TTSFLum if self.cont.hasQE else TTSFElectron, self.cont.tt_fs)
        createToolTip(self.labelTF2, TTTFLum if self.cont.hasQE else TTTFElectron, self.cont.tt_fs)
 
    def deactivateTooltips(self):
    
        '''Remove tooltips from all widgets.'''
    
        for widget in [self.entryExp, self.checkbuttonToggleDark, self.entryDark, self.entryBGN,
                       self.entryBGL, self.entryTarget, self.labelSNR2, self.labelDR2,
                       self.labelFL2, self.labelEFL2, self.labelAP2, self.labelFR2, self.labelIS2, 
                       self.labelRL2, self.labelGainI2, self.labelSatCap2, self.labelBL2, self.labelWL2, 
                       self.labelPS2, self.labelQE2, self.labelRNI2, self.labelDN2, self.labelSN2,
                       self.labelTBGN2, self.labelDF2, self.labelSF2, self.labelTF2]:
                           
            widget.unbind('<Enter>')
            widget.unbind('<Motion>')
            widget.unbind('<Leave>')
              
    def setLumColor(self, sf, label):
    
        '''Set skyglow label background according to the luminance value.'''
    
        if sf > 21.8:
            label.configure(background=('#%02x%02x%02x' % (0, 0, 0)), foreground='white')
        elif 21.8 >= sf > 21.5:
            label.configure(background=('#%02x%02x%02x' % (11, 44, 111)), foreground='white')
        elif 21.5 >= sf > 21.2:
            label.configure(background=('#%02x%02x%02x' % (32, 153, 143)), foreground='white')
        elif 21.2 >= sf > 20.9:
            label.configure(background=('#%02x%02x%02x' % (0, 219, 0)), foreground='black')
        elif 20.9 >= sf > 20.4:
            label.configure(background=('#%02x%02x%02x' % (255, 255, 0)), foreground='black')
        elif 20.4 >= sf > 19.4:
            label.configure(background=('#%02x%02x%02x' % (237, 161, 19)), foreground='black')
        else:
            label.configure(background=('#%02x%02x%02x' % (194, 82, 60)), foreground='black')
    
    
class ImageSimulator(ttk.Frame):
    
    def __init__(self, parent, controller):
    
        '''Initialize Image Simulator frame.'''
    
        ttk.Frame.__init__(self, parent)
        
        self.cont = controller
        small_font = self.cont.small_font
        medium_font = self.cont.medium_font
        large_font = self.cont.large_font
        
        # Define attributes
        
        self.varISO = tk.IntVar()
        self.varGain = tk.DoubleVar()
        self.varRN = tk.DoubleVar()
        self.varExp = tk.DoubleVar()
        self.varDF = tk.DoubleVar()
        self.varSF = tk.DoubleVar()
        self.varTF = tk.DoubleVar()
        self.varSubs = tk.IntVar()
        self.varStretch = tk.IntVar()
        
        self.varMessageLabel = tk.StringVar()
        
        self.varSNRInfo = tk.StringVar()
        self.varStackSNRInfo = tk.StringVar()
        self.varDRInfo = tk.StringVar()
        self.varGainInfo = tk.StringVar()
        self.varSatCapInfo = tk.StringVar()
        self.varBLInfo = tk.StringVar()
        self.varWLInfo = tk.StringVar()
        self.varPSInfo = tk.StringVar()
        self.varQEInfo = tk.StringVar()
        self.varRNInfo = tk.StringVar()
        self.varSNInfo = tk.StringVar()
        self.varDNInfo = tk.StringVar()
        self.varTBGNInfo = tk.StringVar()
        self.varFLInfo = tk.StringVar()
        self.varEFLInfo = tk.StringVar()
        self.varAPInfo = tk.StringVar()
        self.varFRInfo = tk.StringVar()
        self.varISInfo = tk.StringVar()
        self.varRLInfo = tk.StringVar()
        
        self.varDRLabel = tk.StringVar()
        self.varRNLabel = tk.StringVar()
        self.varDNLabel = tk.StringVar()
        self.varSNLabel = tk.StringVar()
        self.varTBGNLabel = tk.StringVar()
        self.varSFLabel = tk.StringVar()
        self.varTFLabel = tk.StringVar()
        
        # Define frames
        
        frameHeader = ttk.Frame(self)
        
        frameContent = ttk.Frame(self)
        
        frameLeft = ttk.Frame(frameContent)
        frameMiddle = ttk.Frame(frameContent)
        frameRight = ttk.Frame(frameContent)
        
        frameUpMiddle = ttk.Frame(frameMiddle)
        frameLowMiddle = ttk.Frame(frameMiddle)
        
        frameSignal = ttk.Frame(frameRight, borderwidth=2, relief='groove')
        frameNoise = ttk.Frame(frameRight, borderwidth=2, relief='groove')
        
        frameOptics = ttk.Frame(frameLeft, borderwidth=2, relief='groove')
        frameSensor = ttk.Frame(frameLeft, borderwidth=2, relief='groove')
        
        frameMessage = ttk.Frame(self)
        
        # Setup canvas
        
        self.topCanvas = tk.Toplevel()
        self.topCanvas.destroy()
                     
            
        # Read demonstration image
        self.img_orig = matplotlib.image.imread('sim_orig_image.png')
        
        # Set default attribute values
        
        self.varDRLabel.set('stops')
        self.varRNLabel.set('e-')
        self.varDNLabel.set('e-')
        self.varSNLabel.set('e-')
        self.varTBGNLabel.set('e-')
        self.varSFLabel.set(u'mag/arcsec\u00B2' if self.cont.hasQE else 'e-/s')
        self.varTFLabel.set(u'mag/arcsec\u00B2' if self.cont.hasQE else 'e-/s')
        
        # Place frames
        
        frameHeader.pack(side='top', fill='x')
        
        frameContent.pack(side='top', fill='both', expand=True)
        
        frameLeft.pack(side='left', padx=(30*scsx, 0), expand=True)
        frameMiddle.pack(side='left', expand=True)
        frameRight.pack(side='right', padx=(0, 30*scsx), expand=True)
        
        frameOptics.pack(side='top', pady=(25*scsy, 50*scsy), expand=True)
        ttk.Label(frameLeft, text='User modified camera/optics data is displayed in blue',
                  foreground='dimgray').pack(side='bottom', pady=(8*scsy, 25*scsy))
        frameSensor.pack(side='bottom', expand=True)
        
        frameUpMiddle.pack(side='top', pady=(20*scsy, 40*scsy), expand=True)
        frameLowMiddle.pack(side='bottom', pady=(0, 25*scsy), expand=True)
        
        frameSignal.pack(side='top', pady=(25*scsy, 50*scsy), expand=True)
        frameNoise.pack(side='bottom', pady=(0, 25*scsy), expand=True)
        
        frameMessage.pack(side='bottom', fill='x')
        
        # *** Header frame ***
        
        labelHeader = ttk.Label(frameHeader, text='Image Simulator', font=large_font, anchor='center')
        
        frameNames = ttk.Frame(frameHeader)
        labelCamName = ttk.Label(frameNames, textvariable=self.cont.varCamName, anchor='center')
        labelTelName = ttk.Label(frameNames, textvariable=self.cont.varTelName, anchor='center')
        labelFLMod = ttk.Label(frameNames, textvariable=self.cont.varFLMod, anchor='center')
        
        labelHeader.pack(side='top', pady=3*scsy)
        
        ttk.Separator(frameHeader, orient='horizontal').pack(side='top', fill='x')
        
        frameNames.pack(side='top', fill='x')
        labelCamName.pack(side='left', expand=True)
        labelTelName.pack(side='left', expand=True)
        labelFLMod.pack(side='right', expand=True)
        
        # *** Left frame ***
        
        # Define optics frame widgets
        
        labelOptics = ttk.Label(frameOptics, text='Optics', font=medium_font, anchor='center', width=28)
        labelOptics.grid(row=0, column=0, columnspan=3, pady=5*scsy)
        
        labelFL = ttk.Label(frameOptics, text='Focal length: ')
        self.labelFL2 = ttk.Label(frameOptics, textvariable=self.varFLInfo, anchor='center', width=7)
        labelFL3 = ttk.Label(frameOptics, text='mm')
        
        labelEFL = ttk.Label(frameOptics, text='Effective focal length: ')
        self.labelEFL2 = ttk.Label(frameOptics, textvariable=self.varEFLInfo, anchor='center', width=7)
        labelEFL3 = ttk.Label(frameOptics, text='mm')
        
        labelAP = ttk.Label(frameOptics, text='Aperture diameter: ')
        self.labelAP2 = ttk.Label(frameOptics, textvariable=self.varAPInfo, anchor='center', width=7)
        labelAP3 = ttk.Label(frameOptics, text='mm')
        
        labelFR = ttk.Label(frameOptics, text='Focal ratio: ')
        self.labelFR2 = ttk.Label(frameOptics, textvariable=self.varFRInfo, anchor='center', width=7)
        
        labelIS = ttk.Label(frameOptics, text='Image scale: ')
        self.labelIS2 = ttk.Label(frameOptics, textvariable=self.varISInfo, anchor='center', width=7)
        labelIS3 = ttk.Label(frameOptics, text='arcsec/pixel')
        
        labelRL = ttk.Label(frameOptics, text='Angular resolution limit: ')
        self.labelRL2 = ttk.Label(frameOptics, textvariable=self.varRLInfo, anchor='center', width=7)
        labelRL3 = ttk.Label(frameOptics, text='arcsec')
        
        # Define sensor frame widgets
        
        labelSensor = ttk.Label(frameSensor, text='Sensor', font=medium_font, anchor='center',
                                width=28)
        labelSensor.grid(row=0, column=0, columnspan=3, pady=5*scsy)
        
        labelGainI = ttk.Label(frameSensor, text='Gain: ')
        self.labelGainI2 = ttk.Label(frameSensor, textvariable=self.varGainInfo, anchor='center',
                                     width=7)
        labelGainI3 = ttk.Label(frameSensor, text='e-/ADU')
        
        labelSatCap = ttk.Label(frameSensor, text='Saturation capacity: ')
        self.labelSatCap2 = ttk.Label(frameSensor, textvariable=self.varSatCapInfo, anchor='center',
                                      width=7)
        labelSatCap3 = ttk.Label(frameSensor, text='e-')
        
        labelBL = ttk.Label(frameSensor, text='Black level: ')
        self.labelBL2 = ttk.Label(frameSensor, textvariable=self.varBLInfo, anchor='center', width=7)
        labelBL3 = ttk.Label(frameSensor, text='ADU')
        
        labelWL = ttk.Label(frameSensor, text='White level: ')
        self.labelWL2 = ttk.Label(frameSensor, textvariable=self.varWLInfo, anchor='center', width=7)
        labelWL3 = ttk.Label(frameSensor, text='ADU')
        
        labelPS = ttk.Label(frameSensor, text='Pixel size: ')
        self.labelPS2 = ttk.Label(frameSensor, textvariable=self.varPSInfo, anchor='center', width=7)
        labelPS3 = ttk.Label(frameSensor, text=u'\u03bcm')
        
        labelQE = ttk.Label(frameSensor, text='Quantum efficiency: ')
        self.labelQE2 = ttk.Label(frameSensor, textvariable=self.varQEInfo, anchor='center', width=7)
        labelQE3 = ttk.Label(frameSensor, text='%')
        
        # Place optics frame widgets
        
        labelFL.grid(row=1, column=0, sticky='W')
        self.labelFL2.grid(row=1, column=1)
        labelFL3.grid(row=1, column=2, sticky='W')
        
        labelEFL.grid(row=2, column=0, sticky='W')
        self.labelEFL2.grid(row=2, column=1)
        labelEFL3.grid(row=2, column=2, sticky='W')
        
        labelAP.grid(row=3, column=0, sticky='W')
        self.labelAP2.grid(row=3, column=1)
        labelAP3.grid(row=3, column=2, sticky='W')
        
        labelFR.grid(row=4, column=0, sticky='W')
        self.labelFR2.grid(row=4, column=1)
        
        labelIS.grid(row=5, column=0, sticky='W')
        self.labelIS2.grid(row=5, column=1)
        labelIS3.grid(row=5, column=2, sticky='W')
        
        labelRL.grid(row=6, column=0, sticky='W')
        self.labelRL2.grid(row=6, column=1)
        labelRL3.grid(row=6, column=2, sticky='W')
        
        # Place sensor frame widgets
        
        labelGainI.grid(row=1, column=0, sticky='W')
        self.labelGainI2.grid(row=1, column=1)
        labelGainI3.grid(row=1, column=2, sticky='W')
        
        labelSatCap.grid(row=2, column=0, sticky='W')
        self.labelSatCap2.grid(row=2, column=1)
        labelSatCap3.grid(row=2, column=2, sticky='W')
        
        labelBL.grid(row=3, column=0, sticky='W')
        self.labelBL2.grid(row=3, column=1)
        labelBL3.grid(row=3, column=2, sticky='W')
        
        labelWL.grid(row=4, column=0, sticky='W')
        self.labelWL2.grid(row=4, column=1)
        labelWL3.grid(row=4, column=2, sticky='W')
        
        ttk.Separator(frameSensor, orient='horizontal').grid(row=5, column=0, columnspan=3, sticky='EW')
        
        labelPS.grid(row=6, column=0, sticky='W')
        self.labelPS2.grid(row=6, column=1)
        labelPS3.grid(row=6, column=2, sticky='W')
        
        labelQE.grid(row=7, column=0, sticky='W')
        self.labelQE2.grid(row=7, column=1)
        labelQE3.grid(row=7, column=2, sticky='W')
        
        # *** Right frame ***
        
        # Define signal frame widgets
        
        labelSignal = ttk.Label(frameSignal, text='Signal', font=medium_font, anchor='center', width=26)
        labelSignal.grid(row=0, column=0, columnspan=3, pady=5*scsy)
        
        labelSNR = ttk.Label(frameSignal, text='Target SNR:')
        self.labelSNR2 = ttk.Label(frameSignal, textvariable=self.varSNRInfo, anchor='center', width=5)
        
        labelStackSNR = ttk.Label(frameSignal, text='Stack SNR')
        self.labelStackSNR2 = ttk.Label(frameSignal, textvariable=self.varStackSNRInfo, anchor='center',
                                        width=5)
        
        labelDR = ttk.Label(frameSignal, text='Dynamic range:')
        self.labelDR2 = ttk.Label(frameSignal, textvariable=self.varDRInfo, anchor='center', width=5)
        labelDR3 = ttk.Label(frameSignal, textvariable=self.varDRLabel)
        
        # Define noise frame widgets
        
        labelNoise = ttk.Label(frameNoise, text='Noise', font=medium_font, anchor='center', width=26)
        labelNoise.grid(row=0, column=0, columnspan=3, pady=5*scsy)
        
        labelRNI = ttk.Label(frameNoise, text='Read noise: ')
        self.labelRNI2 = ttk.Label(frameNoise, textvariable=self.varRNInfo, anchor='center', width=5)
        labelRNI3 = ttk.Label(frameNoise, textvariable=self.varRNLabel)
        
        labelDN = ttk.Label(frameNoise, text='Dark noise: ')
        self.labelDN2 = ttk.Label(frameNoise, textvariable=self.varDNInfo, anchor='center', width=5)
        labelDN3 = ttk.Label(frameNoise, textvariable=self.varDNLabel)
        
        labelSN = ttk.Label(frameNoise, text='Sky shot noise: ')
        self.labelSN2 = ttk.Label(frameNoise, textvariable=self.varSNInfo, anchor='center', width=5)
        labelSN3 = ttk.Label(frameNoise, textvariable=self.varSNLabel)
        
        labelTBGN = ttk.Label(frameNoise, text='Total background noise: ')
        self.labelTBGN2 = ttk.Label(frameNoise, textvariable=self.varTBGNInfo, anchor='center', width=5)
        labelTBGN3 = ttk.Label(frameNoise, textvariable=self.varTBGNLabel)
        
        # Place signal frame widgets
        
        labelSNR.grid(row=1, column=0, sticky='W')
        self.labelSNR2.grid(row=1, column=1)
        
        labelStackSNR.grid(row=2, column=0, sticky='W')
        self.labelStackSNR2.grid(row=2, column=1)
        
        labelDR.grid(row=3, column=0, sticky='W')
        self.labelDR2.grid(row=3, column=1)
        labelDR3.grid(row=3, column=2, sticky='W')
        
        # Place noise frame widgets
        
        labelRNI.grid(row=1, column=0, sticky='W')
        self.labelRNI2.grid(row=1, column=1)
        labelRNI3.grid(row=1, column=2, sticky='W')
        
        labelDN.grid(row=2, column=0, sticky='W')
        self.labelDN2.grid(row=2, column=1)
        labelDN3.grid(row=2, column=2, sticky='W')
        
        labelSN.grid(row=3, column=0, sticky='W')
        self.labelSN2.grid(row=3, column=1)
        labelSN3.grid(row=3, column=2, sticky='W')
        
        ttk.Separator(frameNoise, orient='horizontal').grid(row=4, column=0, columnspan=3, sticky='EW')
        
        labelTBGN.grid(row=5, column=0, sticky='W')
        self.labelTBGN2.grid(row=5, column=1)
        labelTBGN3.grid(row=5, column=2, sticky='W')
        
        self.setDefaultValues()
        
        # *** Middle frame ***
        
        # Define upper middle frame widgets
        
        labelInput = ttk.Label(frameUpMiddle, text='Imaging parameters', font=medium_font, anchor='center')
        
        self.labelISO = ttk.Label(frameUpMiddle, text='ISO:')
        self.optionISO = ttk.OptionMenu(frameUpMiddle, self.varISO, None, *ISO[self.cont.cnum],
                                        command=self.updateISO)
        
        self.labelGain = ttk.Label(frameUpMiddle, text='Gain:')
        self.optionGain = ttk.OptionMenu(frameUpMiddle, self.varGain, None, *GAIN[self.cont.cnum][0],
                                         command=self.updateGain)
        self.labelGain2 = ttk.Label(frameUpMiddle, text='e-/ADU')
        
        self.labelRN = ttk.Label(frameUpMiddle, text='Read noise:')
        self.optionRN = ttk.OptionMenu(frameUpMiddle, self.varRN, None, *RN[self.cont.cnum][0],
                                       command=self.updateRN)
        self.labelRN2 = ttk.Label(frameUpMiddle, text='e-')
        
        labelExp = ttk.Label(frameUpMiddle, text='Exposure time:')
        self.entryExp = ttk.Entry(frameUpMiddle, textvariable=self.varExp, font=small_font,
                                  background=DEFAULT_BG, width=9)
        labelExp2 = ttk.Label(frameUpMiddle, text='seconds')
        
        labelDF = ttk.Label(frameUpMiddle, text='Dark current:')
        self.entryDF = ttk.Entry(frameUpMiddle, textvariable=self.varDF, font=small_font,
                                 background=DEFAULT_BG, width=9)
        labelDF2 = ttk.Label(frameUpMiddle, text='e-/s')
        
        labelSF = ttk.Label(frameUpMiddle, text='Skyglow:')
        self.entrySF = ttk.Entry(frameUpMiddle, textvariable=self.varSF, font=small_font,
                                 background=DEFAULT_BG, width=9)
        labelSF2 = ttk.Label(frameUpMiddle, textvariable=self.varSFLabel)
        
        labelTF = ttk.Label(frameUpMiddle, text='Target signal:')
        self.entryTF = ttk.Entry(frameUpMiddle, textvariable=self.varTF, font=small_font,
                                 background=DEFAULT_BG, width=9)
        labelTF2 = ttk.Label(frameUpMiddle, textvariable=self.varTFLabel)
        
        labelSubs = ttk.Label(frameUpMiddle, text='Number of subframes:')
        self.entrySubs = ttk.Entry(frameUpMiddle, textvariable=self.varSubs, font=small_font,
                                   background=DEFAULT_BG, width=9)
        labelSubs2 = ttk.Label(frameUpMiddle, text='', width=9)
        
        # Define lower middle frame widgets
        
        buttonData = ttk.Button(frameLowMiddle, text='Calculate data', command=self.processInput, width=14)
        buttonSim = ttk.Button(frameLowMiddle, text='Simulate image', command=self.simulateController, width=14)
        buttonTransferPlot = ttk.Button(frameLowMiddle, text='Transfer input to Plotting Tool',
                                        command=self.cont.transferToPlot, width=26)
        buttonClear = ttk.Button(frameLowMiddle, text='Clear input', command=self.cont.clearInput)
        
        # Place upper left frame widgets
        
        labelInput.grid(row=0, column=0, columnspan=3, pady=(0, 10*scsy))
        
        labelExp.grid(row=3, column=0, sticky='W')
        self.entryExp.grid(row=3, column=1)
        labelExp2.grid(row=3, column=2, sticky='W')
        
        labelDF.grid(row=4, column=0, sticky='W')
        self.entryDF.grid(row=4, column=1)
        labelDF2.grid(row=4, column=2, sticky='W')
        
        labelSF.grid(row=5, column=0, sticky='W')
        self.entrySF.grid(row=5, column=1)
        labelSF2.grid(row=5, column=2, sticky='W')
        
        labelTF.grid(row=6, column=0, sticky='W')
        self.entryTF.grid(row=6, column=1)
        labelTF2.grid(row=6, column=2, sticky='W')
        
        labelSubs.grid(row=7, column=0, sticky='W')
        self.entrySubs.grid(row=7, column=1)
        labelSubs2.grid(row=7, column=2)
        
        # Place lower middle frame widgets
        
        buttonData.grid(row=0, column=0)
        buttonSim.grid(row=1, column=0)
        buttonTransferPlot.grid(row=2, column=0, pady=(22*scsy, 11*scsy))
        buttonClear.grid(row=3, column=0)
        
        # Place more widgets according to camera type
        self.reconfigureNonstaticWidgets()
        
        # *** Message frame ***
        
        self.labelMessage = ttk.Label(frameMessage, textvariable=self.varMessageLabel, anchor='center')
        
        ttk.Separator(frameMessage, orient='horizontal').pack(side='top', fill='x')
        self.labelMessage.pack(fill='x')
        
        if self.cont.tooltipsOn.get(): self.activateTooltips()

    def emptyInfoLabels(self):
    
        '''Clear labels showing calculated values.'''
    
        self.varSNRInfo.set('-')
        self.varStackSNRInfo.set('-')
        self.varDRInfo.set('-')
        self.varSNInfo.set('-')
        self.varDNInfo.set('-')
        self.varTBGNInfo.set('-')
        
    def setDefaultValues(self):
    
        '''Set all relevant class attributes to their default values.'''
        
        # Variables to keep track of currently selected ISO, gain or read noise in the optionmenus
        self.gain_idx = 0
        self.rn_idx = 0
        
        self.dataCalculated = False # Used to indicate if calculated data exists
        self.noInvalidInput = True # Indicates if the processInput method has been run without errors
        
        self.varISO.set(ISO[self.cont.cnum][self.gain_idx])
        self.varGain.set(GAIN[self.cont.cnum][0][self.gain_idx])
        self.varRN.set(RN[self.cont.cnum][0][self.rn_idx])
        self.varExp.set('')
        self.varDF.set('')
        self.varSF.set('')
        self.varTF.set('')
        self.varSubs.set(1)
        self.varStretch.set(0)
        
        self.varGainInfo.set('%.3g' % GAIN[self.cont.cnum][0][self.gain_idx])
        self.varSatCapInfo.set('%d' % SAT_CAP[self.cont.cnum][0][self.gain_idx])
        self.varBLInfo.set('%d' % BLACK_LEVEL[self.cont.cnum][0][self.gain_idx])
        self.varWLInfo.set('%d' % WHITE_LEVEL[self.cont.cnum][0][self.gain_idx])
        self.varPSInfo.set('%g' % PIXEL_SIZE[self.cont.cnum][0])
        self.varQEInfo.set('-' if not self.cont.hasQE else ('%d' % (QE[self.cont.cnum][0]*100)))
        self.varRNInfo.set('%.1f' % (self.varRN.get()))
        
        # Set text color according to whether the data is default or user added
        self.labelGainI2.configure(foreground=('black' \
                                   if GAIN[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelRNI2.configure(foreground=('black' \
                                 if RN[self.cont.cnum][1][self.rn_idx] == 0 else 'navy'))
        self.labelSatCap2.configure(foreground=('black' \
                                    if SAT_CAP[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelBL2.configure(foreground=('black' \
                                if BLACK_LEVEL[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelWL2.configure(foreground=('black' \
                                if WHITE_LEVEL[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelPS2.configure(foreground=('black' if PIXEL_SIZE[self.cont.cnum][1] == 0 else 'navy'))
        self.labelQE2.configure(foreground=('black' if QE[self.cont.cnum][1] == 0 else 'navy'))
        
        self.updateOpticsLabels()
        
        self.varMessageLabel.set('')
        
        self.topCanvas.destroy()
        
        self.emptyInfoLabels() # Clear labels
    
    def reconfigureNonstaticWidgets(self):
    
        '''Places widgets according to camera type.'''
    
        self.labelISO.grid_forget()
        self.optionISO.grid_forget()
                
        self.labelGain.grid_forget()
        self.optionGain.grid_forget()
        self.labelGain2.grid_forget()
            
        self.labelRN.grid_forget()
        self.optionRN.grid_forget()
        self.labelRN2.grid_forget()
    
        # Set selectable values in the optionmenus according to camera model
        self.optionISO.set_menu(*([None] + list(ISO[self.cont.cnum])))
        self.optionGain.set_menu(*([None] + list(GAIN[self.cont.cnum][0])))
        self.optionRN.set_menu(*([None] + list(RN[self.cont.cnum][0])))
            
        if self.cont.isDSLR:
        
            # DSLRs use the ISO optionmenu
            self.labelISO.grid(row=1, column=0, sticky='W')
            self.optionISO.grid(row=1, column=1)
                
        else:
        
            # CCDs use gain and/or read noise optionmenus if they have more than one value to use
                
            if len(GAIN[self.cont.cnum][0]) > 1:
                    
                self.labelGain.grid(row=1, column=0, sticky='W')
                self.optionGain.grid(row=1, column=1)
                self.labelGain2.grid(row=1, column=2, sticky='W')
                    
            if len(RN[self.cont.cnum][0]) > 1:
                    
                self.labelRN.grid(row=2, column=0, sticky='W')
                self.optionRN.grid(row=2, column=1)
                self.labelRN2.grid(row=2, column=2, sticky='W')

    def updateISO(self, selected_iso):
    
        '''Update index of selected ISO and update sensor labels.'''
        
        self.gain_idx = int(np.where(ISO[self.cont.cnum] == selected_iso)[0])
        self.rn_idx = self.gain_idx
        
        self.updateSensorLabels()
    
    def updateGain(self, selected_gain):
    
        '''Update index of selected gain and update sensor labels.'''
    
        self.gain_idx = int(np.where(GAIN[self.cont.cnum][0] == selected_gain)[0])
        
        self.updateSensorLabels()
    
    def updateRN(self, selected_rn):
            
        '''Update index of selected ISO and update sensor labels.'''
            
        self.rn_idx = int(np.where(RN[self.cont.cnum][0] == selected_rn)[0])
        
        self.updateSensorLabels()
    
    def updateSensorLabels(self):
    
        '''
        Update labels with the gain, read noise and saturation
        level values of currently selected ISO/gain/RN.
        '''
    
        self.varGainInfo.set('%.3g' % GAIN[self.cont.cnum][0][self.gain_idx])
        self.varRNInfo.set('%.1f' % RN[self.cont.cnum][0][self.rn_idx])
        self.varSatCapInfo.set('%d' % SAT_CAP[self.cont.cnum][0][self.gain_idx])
        self.varBLInfo.set('%d' % BLACK_LEVEL[self.cont.cnum][0][self.gain_idx])
        self.varWLInfo.set('%d' % WHITE_LEVEL[self.cont.cnum][0][self.gain_idx])
        
        # Set text color according to whether the data is default or user added
        self.labelGainI2.configure(foreground=('black' if GAIN[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelRNI2.configure(foreground=('black' if RN[self.cont.cnum][1][self.rn_idx] == 0 else 'navy'))
        self.labelSatCap2.configure(foreground=('black' if SAT_CAP[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelBL2.configure(foreground=('black' if BLACK_LEVEL[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelWL2.configure(foreground=('black' if WHITE_LEVEL[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
    
    def updateOpticsLabels(self):
    
        '''Update labels in the optics frame with the current values.'''
    
        self.varFLInfo.set('%g' % FOCAL_LENGTH[self.cont.tnum][0])
        self.varEFLInfo.set('%g' % (FOCAL_LENGTH[self.cont.tnum][0]*self.cont.FLModVal))
        self.varAPInfo.set('%g' % APERTURE[self.cont.tnum][0])
        self.varFRInfo.set(u'\u0192/%g' % round(FOCAL_LENGTH[self.cont.tnum][0]*self.cont.FLModVal\
                                                /APERTURE[self.cont.tnum][0], 1))
        self.varISInfo.set('%.3g' % (self.cont.ISVal))
        self.varRLInfo.set('%.2g' % (1.22*5.5e-4*180*3600/(APERTURE[self.cont.tnum][0]*np.pi)))
        
        # Set text color according to whether the data is default or user added
        self.labelFL2.configure(foreground=('black' if FOCAL_LENGTH[self.cont.tnum][1] == 0 else 'navy'))
        self.labelAP2.configure(foreground=('black' if APERTURE[self.cont.tnum][1] == 0 else 'navy'))
    
    def processInput(self):
    
        '''Check that the inputted values are valid, then run calculations method.'''
        
        self.noInvalidInput = False
        
        try:
            self.exposure = self.varExp.get()
            
        except ValueError:
            self.varMessageLabel.set('Invalid input for exposure time.')
            self.emptyInfoLabels()
            return None
        
        try:
            self.df = self.varDF.get()
            
        except ValueError:
            self.varMessageLabel.set('Invalid input for dark current.')
            self.emptyInfoLabels()
            return None
        
        try:
            self.sf = (convSig(self.varSF.get(), False) if self.cont.lumSignalType.get() \
                                                        else self.varSF.get())
            
        except ValueError:
            self.varMessageLabel.set('Invalid input for skyglow.')
            self.emptyInfoLabels()
            return None
            
        try:
            self.tf = (convSig(self.varTF.get(), False) if self.cont.lumSignalType.get() \
                                                        else self.varTF.get())
            
        except ValueError:
            self.varMessageLabel.set('Invalid input for target signal.')
            self.emptyInfoLabels()
            return None
            
        try:
            self.subs = self.varSubs.get()
            
        except ValueError:
            self.varMessageLabel.set('Invalid input for number of subframes. Must be an integer.')
            self.emptyInfoLabels()
            return None
        
        self.noInvalidInput = True
        
        self.calculate()
    
    def calculate(self):
    
        '''Calculate SNR, dynamic range and noise values and set to the corresponding labels.'''
        
        gain = GAIN[self.cont.cnum][0][self.gain_idx] # Gain [e-/ADU]
        rn = RN[self.cont.cnum][0][self.rn_idx]       # Read noise [e-]
        
        dark_signal_e = self.df*self.exposure   # Signal from dark current [e-]
        sky_signal_e = self.sf*self.exposure    # Signal from skyglow [e-]
        target_signal_e = self.tf*self.exposure # Signal from target signal [e-]
        
        sat_cap = SAT_CAP[self.cont.cnum][0][self.gain_idx] # Saturation capacity [e-]
        
        dn = np.sqrt(dark_signal_e)                          # Dark noise [e-]
        sn = np.sqrt(sky_signal_e)                           # Skyglow noise [e-]
        tbgn = np.sqrt(rn**2 + dark_signal_e + sky_signal_e) # Total background noise [e-]
        
        snr = target_signal_e/np.sqrt(target_signal_e + tbgn**2) # Signal to noise ratio in subframe
        stack_snr = snr*np.sqrt(self.subs)        # Signal to noise ratio in stacked frame
        
        self.dr = np.log10(sat_cap/tbgn)/np.log10(2.0) # Dynamic range [stops]
        factor = 10*np.log(2.0)/np.log(10.0)
        
        # Update labels
        self.varSNRInfo.set('%.1f' % snr)
        self.varStackSNRInfo.set('%.1f' % stack_snr)
        self.varDRInfo.set('%.1f' % (self.dr if self.cont.stopsDRUnit.get() else self.dr*factor))
        self.varDNInfo.set('%.1f' % dn)
        self.varSNInfo.set('%.1f' % sn)
        self.varTBGNInfo.set('%.1f' % tbgn)
        
        self.dataCalculated = True
        
        self.varMessageLabel.set('SNR calculated.')
    
    def simulateController(self, fromCheckbutton=False):
    
        '''Changes the dispayed simulated image according to various conditions.'''
        
        # If the "Simulate image" button is pressed
        if not fromCheckbutton:
        
            # Calculate data and run simulation if all input is valid
        
            self.processInput()
        
            if self.noInvalidInput:
            
                # Show error message if the number of subframes is too high (to avoid memory error)
                if self.subs > 200:
                    self.varMessageLabel.set(\
                    'Please decrease number of subframes to 200 or less before simulating.')
                    return None
                
                self.showCanvasWindow()
                
                self.simulateImage()
        
        # If the "Stretch" checkbutton was pressed and calculated data exists
        elif self.dataCalculated:
        
            # Redraw the simulated image as stretched or unstretched depending on checkbutton state
            if self.varStretch.get():
        
                self.canvasSim.create_image(0, 0, image=self.photoim_str, anchor='nw')
                self.canvasSim.image = self.photoim_str
                
            else:
            
                self.canvasSim.create_image(0, 0, image=self.photoim, anchor='nw')
                self.canvasSim.image = self.photoim
            
    def simulateImage(self):
    
        '''Calculates an image from the inputted values.'''
    
        # Show "Working.." message while calculating
        self.varMessageLabel.set('Working..')
        self.labelMessage.update_idletasks()
    
        gain = float(GAIN[self.cont.cnum][0][self.gain_idx]) # Gain [e-/ADU]
        rn = RN[self.cont.cnum][0][self.rn_idx] # Read noise [e-]
    
        dark_signal_e = self.df*self.exposure # Mean dark current signal [e-]
        sky_signal_e = self.sf*self.exposure # Mean sky background signal [e-]
        target_signal_e = self.tf*self.exposure # Mean target signal [e-]

        imsize = (256, 256, self.subs) # Image dimensions (including stack size)
            
        map = np.where(self.img_orig > 0.0) # Locations of target pixels
        
        # Generate sky, target and dark images from poisson distributions
        dark = np.random.poisson(dark_signal_e, imsize)/gain
        sky = np.random.poisson(sky_signal_e, imsize)/gain
        target = np.random.poisson(target_signal_e, imsize)/gain
        
        # Generate bias images with correct amount of gaussian read noise
        bias = BLACK_LEVEL[self.cont.cnum][0][self.gain_idx] \
               + (np.random.normal(0, rn, imsize).astype(int))/gain
        
        # Combine signals to get final images
        img = bias + dark + sky
        for i in range(self.subs):
            img[:, :, i][map] += target[:, :, i][map]*self.img_orig[map]
        
        # Truncate invalid pixel values
        img[img < 0.0] = 0.0
        img[img > WHITE_LEVEL[self.cont.cnum][0][self.gain_idx]] \
                                                     = WHITE_LEVEL[self.cont.cnum][0][self.gain_idx]
        
        # Take mean of images to get a stacked image
        img = np.mean(img, axis=2)
        
        # Scale pixel values to be between 0 and 1, with 1 corresponding to the saturation capacity
        img = img/WHITE_LEVEL[self.cont.cnum][0][self.gain_idx]
        
        # Save linear and nonlinear version of the simulated image
        plt.imsave('sim.jpg', img, cmap=plt.get_cmap('gray'), vmin = 0.0, vmax = 1.0)
        plt.imsave('sim_str.jpg', autostretch(img), cmap=plt.get_cmap('gray'), vmin=0, vmax=65535)
        
        # Open as PIL images
        im = Image.open('sim.jpg')
        im_str = Image.open('sim_str.jpg')
        
        sidelength = int(self.canvasSim.winfo_width()) - 5 # Canvas size
        
        # Resize images to fit canvas
        im_res = im.resize((sidelength, sidelength), Image.ANTIALIAS)
        im_res_str = im_str.resize((sidelength, sidelength), Image.ANTIALIAS)
        
        # Convert to PhotoImage
        self.photoim = ImageTk.PhotoImage(im_res)
        self.photoim_str = ImageTk.PhotoImage(im_res_str)
        
        # Show relevant version in canvas
        if self.varStretch.get():
        
            self.canvasSim.create_image(0, 0, image=self.photoim_str, anchor='nw')
            self.canvasSim.image = self.photoim_str
            
        else:
        
            self.canvasSim.create_image(0, 0, image=self.photoim, anchor='nw')
            self.canvasSim.image = self.photoim
        
        self.varMessageLabel.set('Image simulated.')

    def activateTooltips(self):
    
        '''Add tooltips to all relevant widgets.'''
    
        createToolTip(self.entryExp, TTExp, self.cont.tt_fs)
        createToolTip(self.entryDF, TTDF, self.cont.tt_fs)
        createToolTip(self.entrySF, TTSFLum if self.cont.hasQE else TTSFElectron, self.cont.tt_fs)
        createToolTip(self.entryTF, TTTFLum if self.cont.hasQE else TTTFElectron, self.cont.tt_fs)
        createToolTip(self.entrySubs, TTSubs, self.cont.tt_fs)
        createToolTip(self.labelSNR2, TTSNR, self.cont.tt_fs)
        createToolTip(self.labelStackSNR2, TTStackSNR, self.cont.tt_fs)
        createToolTip(self.labelDR2, TTDR, self.cont.tt_fs)
        createToolTip(self.labelFL2, TTFL, self.cont.tt_fs)
        createToolTip(self.labelEFL2, TTEFL, self.cont.tt_fs)
        createToolTip(self.labelAP2, TTAP, self.cont.tt_fs)
        createToolTip(self.labelFR2, TTFR, self.cont.tt_fs)
        createToolTip(self.labelIS2, TTIS, self.cont.tt_fs)
        createToolTip(self.labelRL2, TTRL, self.cont.tt_fs)
        createToolTip(self.labelGainI2, TTGain, self.cont.tt_fs)
        createToolTip(self.labelSatCap2, TTSatCap, self.cont.tt_fs)
        createToolTip(self.labelBL2, TTBL, self.cont.tt_fs)
        createToolTip(self.labelWL2, TTWL, self.cont.tt_fs)
        createToolTip(self.labelPS2, TTPS, self.cont.tt_fs)
        createToolTip(self.labelQE2, TTQE, self.cont.tt_fs)
        createToolTip(self.labelRNI2, TTRN, self.cont.tt_fs)
        createToolTip(self.labelDN2, TTDN, self.cont.tt_fs)
        createToolTip(self.labelSN2, TTSN, self.cont.tt_fs)
        createToolTip(self.labelTBGN2, TTTotN, self.cont.tt_fs)
        
        if self.topCanvas.winfo_exists():
            
            createToolTip(self.checkbuttonStretch, TTStretch, self.cont.tt_fs)
        
    def deactivateTooltips(self):
    
        '''Remove tooltips from all widgets.'''
    
        for widget in [self.entryExp, self.entryDF, self.entrySF, self.entryTF, self.entrySubs,
                       self.labelSNR2, self.labelStackSNR2, self.labelDR2, self.labelFL2, 
                       self.labelEFL2, self.labelAP2, self.labelFR2, self.labelIS2, self.labelRL2, 
                       self.labelGainI2, self.labelSatCap2, self.labelBL2, self.labelWL2, self.labelPS2, 
                       self.labelQE2, self.labelRNI2, self.labelDN2, self.labelSN2, self.labelTBGN2]:
                           
            widget.unbind('<Enter>')
            widget.unbind('<Motion>')
            widget.unbind('<Leave>')
            
        if self.topCanvas.winfo_exists():
            
            self.checkbuttonStretch.unbind('<Enter>')
            self.checkbuttonStretch.unbind('<Motion>')
            self.checkbuttonStretch.unbind('<Leave>')
    
    def showCanvasWindow(self):
    
        '''Show window with the simulated image.'''

        # If the window isn't already created
        if not self.topCanvas.winfo_exists():
                
            # Setup window
            self.topCanvas = tk.Toplevel(bg=DEFAULT_BG)
            self.topCanvas.title('Simulated image')
            self.cont.addIcon(self.topCanvas)
            setupWindow(self.topCanvas, 330, 350)
            self.topCanvas.focus_force()
            self.topCanvas.wm_attributes('-topmost', 1)
                
            self.canvasSim = tk.Canvas(self.topCanvas, width=round(320*scsy),
                                       height=round(320*scsy), bg='white', bd=2,
                                       relief='groove')
                
            self.canvasSim.pack(side='top', expand=True)
        
            # Create stretch checkbutton
            frameStretch = ttk.Frame(self.topCanvas)
        
            labelStretch = ttk.Label(frameStretch, text='Stretch:')
            self.checkbuttonStretch = tk.Checkbutton(frameStretch, variable=self.varStretch,
                                      command=lambda: self.simulateController(fromCheckbutton=True))
            if self.cont.tooltipsOn.get():
                createToolTip(self.checkbuttonStretch, TTStretch, self.cont.tt_fs)
            
            frameStretch.pack(side='bottom', expand=True)
        
            labelStretch.pack(side='left')
            self.checkbuttonStretch.pack(side='left')
            
            self.topCanvas.update()
    
    
class PlottingTool(ttk.Frame):

    def __init__(self, parent, controller):
    
        '''Initialize Plotting Tool frame.'''
    
        ttk.Frame.__init__(self, parent)
        
        self.cont = controller
        small_font = self.cont.small_font
        medium_font = self.cont.medium_font
        large_font = self.cont.large_font
        small_fs = self.cont.small_fs
        medium_fs = self.cont.medium_fs
        
        # Define attributes
        
        self.varPlotType = tk.StringVar()
        
        self.varISO = tk.IntVar()
        self.varGain = tk.DoubleVar()
        self.varRN = tk.DoubleVar()
        self.varExp = tk.DoubleVar()
        self.varDF = tk.DoubleVar()
        self.varSF = tk.DoubleVar()
        self.varTF = tk.DoubleVar()
        self.varTotal = tk.DoubleVar()
        self.varMax = tk.DoubleVar()
        self.varMessageLabel = tk.StringVar()
        
        self.varSFLabel = tk.StringVar()
        self.varTFLabel = tk.StringVar()
        
        # Define frames
        
        frameHeader = ttk.Frame(self)
        
        frameContent = ttk.Frame(self)
        
        frameLeft = ttk.Frame(frameContent)
        
        frameUpLeft = ttk.Frame(frameLeft)
        frameLowLeft = ttk.Frame(frameLeft)
        frameButton = ttk.Frame(frameLeft)
        
        frameRight = ttk.Frame(frameContent)
        
        frameMessage = ttk.Frame(self)
        
        # Setup canvas
        
        f = matplotlib.figure.Figure(figsize=(6.5*scsx, 4.7*scsy), dpi=100, facecolor=DEFAULT_BG)
        self.ax = f.add_subplot(111)
        self.ax.tick_params(axis='both', which='major', labelsize=8)
        
        self.canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(f, frameRight)
        self.canvas._tkcanvas.config(highlightthickness=0)
        
        # Set dafault attribute values
        
        self.varSFLabel.set(u'mag/arcsec\u00B2' if self.cont.hasQE else 'e-/s')
        self.varTFLabel.set(u'mag/arcsec\u00B2' if self.cont.hasQE else 'e-/s')
        
        self.setDefaultValues()
        
        # Place frames
        
        frameHeader.pack(side='top', fill='x')
        
        frameContent.pack(side='top', fill='both', expand=True)
        
        frameLeft.pack(side='left', fill='both', padx=(50*scsx, 0), expand=True)
        
        frameUpLeft.pack(side='top', pady=(30*scsy, 0), expand=True)
        frameLowLeft.pack(side='top', pady=(0, 30*scsy), expand=True)
        frameButton.pack(side='bottom', pady=(0, 30*scsy), expand=True)
        
        frameRight.pack(side='right', expand=True)
        
        frameMessage.pack(side='bottom', fill='x')
        
        # *** Header frame ***
        
        labelHeader = ttk.Label(frameHeader, text='Plotting Tool', font=large_font, anchor='center')
        
        frameNames = ttk.Frame(frameHeader)
        labelCamName = ttk.Label(frameNames, textvariable=self.cont.varCamName, anchor='center')
        labelTelName = ttk.Label(frameNames, textvariable=self.cont.varTelName, anchor='center')
        labelFLMod = ttk.Label(frameNames, textvariable=self.cont.varFLMod, anchor='center')
        
        labelHeader.pack(side='top', pady=3*scsy)
        
        ttk.Separator(frameHeader, orient='horizontal').pack(side='top', fill='x')
        
        frameNames.pack(side='top', fill='x')
        labelCamName.pack(side='left', expand=True)
        labelTelName.pack(side='left', expand=True)
        labelFLMod.pack(side='right', expand=True)
        
        # *** Left frame ***
        
        # Define upper left frame widgets
        
        labelPlotType = ttk.Label(frameUpLeft, text='Choose plot type', font=medium_font,
                                  anchor='center', width=33)
        self.optionPlotType = ttk.OptionMenu(frameUpLeft, self.varPlotType, None, *self.plotList,
                                             command=self.toggleActiveWidgets)
        
        # Define lower left frame widgets
        
        labelInput = ttk.Label(frameLowLeft, text='Imaging parameters', font=medium_font,
                               anchor='center')
        
        self.labelISO = ttk.Label(frameLowLeft, text='ISO:')
        self.optionISO = ttk.OptionMenu(frameLowLeft, self.varISO, None, *ISO[self.cont.cnum],
                                        command=self.updateISO)
        
        self.labelGain = ttk.Label(frameLowLeft, text='Gain:')
        self.optionGain = ttk.OptionMenu(frameLowLeft, self.varGain, None, *GAIN[self.cont.cnum][0],
                                         command=self.updateGain)
        self.labelGain2 = ttk.Label(frameLowLeft, text='e-/ADU')
        
        self.labelRN = ttk.Label(frameLowLeft, text='Read noise:')
        self.optionRN = ttk.OptionMenu(frameLowLeft, self.varRN, None, *RN[self.cont.cnum][0],
                                       command=self.updateRN)
        self.labelRN2 = ttk.Label(frameLowLeft, text='e-')
        
        labelExp = ttk.Label(frameLowLeft, text='Exposure time:')
        self.entryExp = ttk.Entry(frameLowLeft, textvariable=self.varExp, font=small_font,
                                  background=DEFAULT_BG, width=9)
        labelExp2 = ttk.Label(frameLowLeft, text='seconds')
        
        labelDF = ttk.Label(frameLowLeft, text='Dark current:')
        self.entryDF = ttk.Entry(frameLowLeft, textvariable=self.varDF, font=small_font,
                                  background=DEFAULT_BG, width=9)
        labelDF2 = ttk.Label(frameLowLeft, text='e-/s')
        
        labelSF = ttk.Label(frameLowLeft, text='Skyglow:')
        self.entrySF = ttk.Entry(frameLowLeft, textvariable=self.varSF, font=small_font,
                                  background=DEFAULT_BG, width=9)
        labelSF2 = ttk.Label(frameLowLeft, textvariable=self.varSFLabel)
        
        labelTF = ttk.Label(frameLowLeft, text='Target signal:')
        self.entryTF = ttk.Entry(frameLowLeft, textvariable=self.varTF, font=small_font,
                                  background=DEFAULT_BG, width=9)
        labelTF2 = ttk.Label(frameLowLeft, textvariable=self.varTFLabel)
        
        labelTotal = ttk.Label(frameLowLeft, text='Total imaging time:')
        self.entryTotal = ttk.Entry(frameLowLeft, textvariable=self.varTotal, font=small_font,
                                  background=DEFAULT_BG, width=9)
        labelTotal2 = ttk.Label(frameLowLeft, text='hours')
        
        self.labelMax = ttk.Label(frameLowLeft, text='Max exposure time:')
        self.entryMax = ttk.Entry(frameLowLeft, textvariable=self.varMax, font=small_font,
                                  background=DEFAULT_BG, width=9)
        self.labelMax2 = ttk.Label(frameLowLeft, text='seconds')
        
        # Define button frame widgets
        
        buttonDraw = ttk.Button(frameButton, text='Draw graph', command=self.processInput)
        buttonTransferSim = ttk.Button(frameButton, text='Transfer input to Image Simulator',
                                        command=self.cont.transferToSim, width=29)
        buttonClear = ttk.Button(frameButton, text='Clear input', command=self.cont.clearInput)
        
        # Place upper left frame widgets
        
        labelPlotType.pack(side='top')
        self.optionPlotType.pack(side='top')
        
        # Place lower left frame widgets
        
        labelInput.grid(row=0, column=0, columnspan=3, pady=10*scsy)
        
        labelExp.grid(row=3, column=0, sticky='W')
        self.entryExp.grid(row=3, column=1)
        labelExp2.grid(row=3, column=2, sticky='W')
        
        labelDF.grid(row=4, column=0, sticky='W')
        self.entryDF.grid(row=4, column=1)
        labelDF2.grid(row=4, column=2, sticky='W')
        
        labelSF.grid(row=5, column=0, sticky='W')
        self.entrySF.grid(row=5, column=1)
        labelSF2.grid(row=5, column=2, sticky='W')
        
        labelTF.grid(row=6, column=0, sticky='W')
        self.entryTF.grid(row=6, column=1)
        labelTF2.grid(row=6, column=2, sticky='W')
            
        labelTotal.grid(row=7, column=0, sticky='W')
        self.entryTotal.grid(row=7, column=1)
        labelTotal2.grid(row=7, column=2, sticky='W')
        
        # Place more widgets according to camera type
        self.reconfigureNonstaticWidgets()
        
        # Place button frame widgets
        buttonDraw.grid(row=0, column=0)
        buttonTransferSim.grid(row=1, column=0, pady=(22*scsy, 11*scsy))
        buttonClear.grid(row=2, column=0)
        
        # *** Right frame (plot window) ***

        self.canvas.get_tk_widget().pack()
        
        # *** Message frame ***
        
        labelMessage = ttk.Label(frameMessage, textvariable=self.varMessageLabel, anchor='center')
        
        ttk.Separator(frameMessage, orient='horizontal').pack(side='top', fill='x')
        labelMessage.pack(fill='x')
        
        # Disable or enable widgets according to plot type
        self.toggleActiveWidgets(self.plotList[0])
        
        if self.cont.tooltipsOn.get(): self.activateTooltips()

    def setDefaultValues(self):
    
        '''Set all relevant class attributes to their default values.'''
        
        # Variables to keep track of currently selected ISO, gain or read noise in the optionmenus
        self.gain_idx = 0
        self.rn_idx = 0
        
        # Plot types
        self.p1 = 'Target SNR vs. sub exposure time'
        self.p7 = 'Target SNR vs. skyglow'
        self.p10 = 'Target SNR vs. target signal'
        self.p2 = 'Stack SNR vs. sub exposure time'
        self.p3 = 'Stack SNR vs. number of subframes'
        self.p4 = 'Stack SNR increase vs. number of subframes'
        self.p5 = 'Maximum stack SNR vs. ISO'
        self.p9 = 'Dynamic range vs. sub exposure time'
        self.p8 = 'Dynamic range vs. skyglow'
        self.p6 = 'Dynamic range vs. ISO'
        self.p11 = 'Saturation capacity vs. gain'
        
        # Set list of available plot types depending on camera type
        if self.cont.isDSLR:
            self.plotList = [self.p1, self.p7, self.p10, self.p2, self.p3,
                             self.p4, self.p5, self.p9, self.p8, self.p6, self.p11]
        else:
            self.plotList = [self.p1, self.p7, self.p10, self.p2, self.p3, self.p4, self.p9, self.p8]
        
        self.varPlotType.set(self.plotList[0])
        
        self.varISO.set(ISO[self.cont.cnum][self.gain_idx])
        self.varGain.set(GAIN[self.cont.cnum][0][self.gain_idx])
        self.varRN.set(RN[self.cont.cnum][0][self.rn_idx])
        self.varExp.set('')
        self.varDF.set('')
        self.varSF.set('')
        self.varTF.set('')
        self.varTotal.set('')
        self.varMax.set(600)
        
        # Clear plot
        self.ax.cla()
        self.canvas.show()
        
    def reconfigureNonstaticWidgets(self):
    
        '''Places widgets according to camera type.'''
    
        self.labelISO.grid_forget()
        self.optionISO.grid_forget()
                
        self.labelGain.grid_forget()
        self.optionGain.grid_forget()
        self.labelGain2.grid_forget()
            
        self.labelRN.grid_forget()
        self.optionRN.grid_forget()
        self.labelRN2.grid_forget()
            
        self.labelMax.grid_forget()
        self.entryMax.grid_forget()
        self.labelMax2.grid_forget()
        
        # Set selectable values in the optionmenus according to camera model
        
        self.optionPlotType.set_menu(*([None] + self.plotList))
        
        self.optionISO.set_menu(*([None] + list(ISO[self.cont.cnum])))
        self.optionGain.set_menu(*([None] + list(GAIN[self.cont.cnum][0])))
        self.optionRN.set_menu(*([None] + list(RN[self.cont.cnum][0])))
                
        if self.cont.isDSLR:
        
            # DSLRs use the ISO optionmenu and max exposure entry
            
            self.labelISO.grid(row=1, column=0, sticky='W')
            self.optionISO.grid(row=1, column=1)
            
            self.labelMax.grid(row=8, column=0, sticky='W')
            self.entryMax.grid(row=8, column=1)
            self.labelMax2.grid(row=8, column=2, sticky='W')
                
        else:
        
            # CCDs use gain and/or read noise optionmenus if they have more than one value to use
            
            if len(GAIN[self.cont.cnum][0]) > 1:
                
                self.labelGain.grid(row=1, column=0, sticky='W')
                self.optionGain.grid(row=1, column=1)
                self.labelGain2.grid(row=1, column=2, sticky='W')
                
            if len(RN[self.cont.cnum][0]) > 1:
                
                self.labelRN.grid(row=2, column=0, sticky='W')
                self.optionRN.grid(row=2, column=1)
                self.labelRN2.grid(row=2, column=2, sticky='W')
    
    def updateISO(self, selected_iso):
    
        '''Update index of selected ISO.'''
    
        self.gain_idx = int(np.where(ISO[self.cont.cnum] == selected_iso)[0])
        self.rn_idx = self.gain_idx
    
    def updateGain(self, selected_gain):
    
        '''Update index of selected gain.'''
    
        self.gain_idx = int(np.where(GAIN[self.cont.cnum][0] == selected_gain)[0])
    
    def updateRN(self, selected_rn):
    
        '''Update index of selected read noise.'''
    
        self.rn_idx = int(np.where(RN[self.cont.cnum][0] == selected_rn)[0])
    
    def toggleActiveWidgets(self, type):
    
        '''Activate or deactivate relevant widgets when changing plot type.'''
    
        if type == self.p1:
            
            self.useExp = False
            self.useTotal = False
            self.useMax = False
            self.useFlux = True
        
            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='disabled')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            
        elif type == self.p2:
        
            self.useExp = False
            self.useTotal = True
            self.useMax = False
            self.useFlux = True
            
            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='disabled')
            self.entryTotal.configure(state='normal')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            
        elif type == self.p3:
        
            self.useExp = True
            self.useTotal = False
            self.useMax = False
            self.useFlux = True
            
            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='normal')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            
        elif type == self.p4:
        
            self.useExp = True
            self.useTotal = False
            self.useMax = False
            self.useFlux = True
            
            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='normal')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            
        elif type == self.p5:
        
            self.useExp = False
            self.useTotal = True
            self.useMax = True
            self.useFlux = True
            
            self.optionISO.configure(state='disabled')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='disabled')
            self.entryTotal.configure(state='normal')
            self.entryMax.configure(state='normal')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            
        elif type == self.p6:
        
            self.useExp = True
            self.useTotal = False
            self.useMax = False
            self.useFlux = True
            
            self.optionISO.configure(state='disabled')
            self.optionGain.configure(state='normal')
            self.entryExp.configure(state='normal')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            
        elif type == self.p7:
        
            self.useExp = True
            self.useTotal = False
            self.useMax = False
            self.useFlux = True
            
            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='normal')
            self.entryExp.configure(state='normal')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            
        elif type == self.p8:
        
            self.useExp = True
            self.useTotal = False
            self.useMax = False
            self.useFlux = True
            
            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='normal')
            self.entryExp.configure(state='normal')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            
        elif type == self.p9:
        
            self.useExp = False
            self.useTotal = False
            self.useMax = False
            self.useFlux = True
            
            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='normal')
            self.entryExp.configure(state='disabled')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            
        elif type == self.p10:
        
            self.useExp = True
            self.useTotal = False
            self.useMax = False
            self.useFlux = True
            
            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='normal')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            
        elif type == self.p11:
        
            self.useExp = False
            self.useTotal = False
            self.useMax = False
            self.useFlux = False
            
            self.optionISO.configure(state='disabled')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='disabled')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='disabled')
            self.entrySF.configure(state='disabled')
            self.entryTF.configure(state='disabled')
    
    def processInput(self):
    
        '''Check that all inputted values are valid and run plot method.'''
        
        try:
            self.exposure = self.varExp.get()
            
        except ValueError:
            if self.useExp:
                self.varMessageLabel.set('Invalid input for exposure time.')
                return None
        
        try:
            if self.useFlux:
                self.df = self.varDF.get()
            
        except ValueError:
            self.varMessageLabel.set('Invalid input for dark current.')
            return None
        
        try:
            if self.useFlux:
                self.sf = (convSig(self.varSF.get(), False) if self.cont.lumSignalType.get() \
                                                            else self.varSF.get())
                
        except ValueError:
            self.varMessageLabel.set('Invalid input for skyglow.')
            return None
            
        try:
            if self.useFlux:
                self.tf = (convSig(self.varTF.get(), False) if self.cont.lumSignalType.get() \
                                                            else self.varTF.get())
            
        except ValueError:
            self.varMessageLabel.set('Invalid input for target signal.')
            return None
                
        try:
            self.total = self.varTotal.get()*3600
            
        except ValueError:
            if self.useTotal:
                self.varMessageLabel.set('Invalid input for total imaging time.')
                return None
                
        try:
            self.max = self.varMax.get()
            
        except ValueError:
            if self.useMax and self.cont.isDSLR:
                self.varMessageLabel.set('Invalid input for max exposure time.')
                return None
        
        self.plot()
    
    def plot(self):
    
        '''Calculate and plot data for relevant plot type.'''
    
        type = self.varPlotType.get()
        small_fs = self.cont.small_fs
        medium_fs = self.cont.medium_fs
    
        if type == self.p1:
        
            exposure = np.linspace(0, 900, 201)
            
            rn = RN[self.cont.cnum][0][self.rn_idx]
            
            snr = self.tf*exposure/np.sqrt(self.tf*exposure + self.sf*exposure \
                                           + self.df*exposure + rn**2)
            
            self.ax.cla()
            self.ax.plot(exposure, snr, '-', color='crimson')
            self.ax.set_title(self.p1, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Sub exposure time [s]', name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('Target SNR', name='Tahoma', fontsize=small_fs)
            self.canvas.draw()
            
        elif type == self.p2:
        
            exposure = np.linspace(1, 900, 200)
            
            subs = self.total/exposure
            
            rn = RN[self.cont.cnum][0][self.rn_idx]
            
            snr = self.tf*exposure/np.sqrt(self.tf*exposure + self.sf*exposure \
                                           + self.df*exposure + rn**2)
            stack_snr = snr*np.sqrt(subs)
            
            self.ax.cla()
            self.ax.plot(exposure, stack_snr, '-', color='forestgreen')
            self.ax.set_title(self.p2, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Sub exposure time [s]', name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('Stack SNR', name='Tahoma', fontsize=small_fs)
            self.canvas.draw()
            
        elif type == self.p3:
        
            subs = np.linspace(0, 200, 201)
            
            rn = RN[self.cont.cnum][0][self.rn_idx]
            
            snr = self.tf*self.exposure/np.sqrt(self.tf*self.exposure + self.sf*self.exposure \
                                                + self.df*self.exposure + rn**2)
            stack_snr = snr*np.sqrt(subs)
            
            self.ax.cla()
            self.ax.plot(subs, stack_snr, '-', color='forestgreen')
            self.ax.set_title(self.p3, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Number of subframes', name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('Stack SNR', name='Tahoma', fontsize=small_fs)
            self.canvas.draw()
            
        elif type == self.p4:
        
            subs = np.linspace(2, 201, 200)
            
            rn = RN[self.cont.cnum][0][self.rn_idx]
            
            snr = self.tf*self.exposure/np.sqrt(self.tf*self.exposure + self.sf*self.exposure \
                                                + self.df*self.exposure + rn**2)
            delta_snr = snr*(np.sqrt(subs[1:]) - np.sqrt(subs[:-1]))
            
            self.ax.cla()
            self.ax.plot(subs[:-1], delta_snr, '-', color='forestgreen')
            self.ax.set_title(self.p4, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Number of subframes', name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('Stack SNR increase with one additional frame', name='Tahoma',
                               fontsize=small_fs)
            self.canvas.draw()
            
        elif type == self.p5:
        
            iso = ISO[self.cont.cnum]
            
            if len(iso) < 2:
                self.varMessageLabel.set('At least two ISO values required.')
                return None
            
            sat_cap = SAT_CAP[self.cont.cnum][0]
            
            isTooLong = 0.3*sat_cap/self.sf > self.max
            
            exposure = 0.3*sat_cap/self.sf*np.invert(isTooLong) + self.max*isTooLong
            subs = self.total/exposure
            
            rn = RN[self.cont.cnum][0]
            
            snr = self.tf*exposure/np.sqrt(self.tf*exposure + self.sf*exposure \
                                           + self.df*exposure + rn**2)
            stack_snr = snr*np.sqrt(subs)
            
            self.ax.cla()
            self.ax.plot(iso, stack_snr, 'o-', color='forestgreen')
            
            for i in range(len(iso)):
                self.ax.annotate('%d x %d s' % (subs[i], np.ceil(exposure[i])), name='Tahoma',
                                 fontsize=self.cont.tt_fs, xy=(iso[i], stack_snr[i]),
                                 xytext=(8, -22), textcoords='offset points',
                                 arrowprops=dict(arrowstyle='->', facecolor='black'))
            self.ax.text(0.5, 0.05,
                         'Exposure time limited if the background\nlevel reaches 30% of the white level',
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes, name='Tahoma', fontsize=self.cont.tt_fs)
            
            self.ax.set_title(self.p5, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('ISO', name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('Maximum stack SNR', name='Tahoma', fontsize=small_fs)
            self.canvas.draw()
            
        elif type == self.p6:
        
            iso = ISO[self.cont.cnum]
            
            if len(iso) < 2:
                self.varMessageLabel.set('At least two ISO values required.')
                return None
            
            sat_cap = SAT_CAP[self.cont.cnum][0]
                
            rn = RN[self.cont.cnum][0]
            tbgn = np.sqrt(rn**2 + self.df*self.exposure + self.sf*self.exposure)
            
            dr = np.log10(sat_cap/tbgn)/np.log10(2)
            
            self.ax.cla()
            self.ax.plot(iso, dr, 'o-', color='navy')
            self.ax.set_title(self.p6, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('ISO', name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('Dynamic range [stops]', name='Tahoma', fontsize=small_fs)
            self.canvas.draw()
            
        elif type == self.p7:
        
            if self.cont.lumSignalType.get():
                sf = convSig(np.linspace(22, 19, 200), False)
            else:
                sf = np.linspace(0, 2*self.sf, 201)
            
            rn = RN[self.cont.cnum][0][self.rn_idx]
            
            snr = self.tf*self.exposure/np.sqrt(self.tf*self.exposure + sf*self.exposure \
                                                + self.df*self.exposure + rn**2)
            current_snr = self.tf*self.exposure/np.sqrt(self.tf*self.exposure + self.sf*self.exposure \
                                                        + self.df*self.exposure + rn**2)
            
            self.ax.cla()
            self.ax.plot((convSig(sf, True) if self.cont.lumSignalType.get() else sf), snr, '-',
                         color='crimson')
            p, = self.ax.plot((convSig(self.sf, True) if self.cont.lumSignalType.get() else self.sf),
                              current_snr, 'o', color='crimson', label='Current values')
            self.ax.legend(handles=[p], loc='best', numpoints=1, fontsize=small_fs)
            self.ax.set_title(self.p7, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Skyglow %s' % (u'[mag/arcsec\u00B2]' \
                                               if self.cont.lumSignalType.get() else '[e-/s]'),
                               name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('Target SNR', name='Tahoma', fontsize=small_fs)
            self.canvas.draw()

        elif type == self.p8:
           
            if self.cont.lumSignalType.get():
                sf = convSig(np.linspace(22, 19, 200), False)
            else:
                sf = np.linspace(0, 2*self.sf, 201)
        
            sat_cap = SAT_CAP[self.cont.cnum][0][self.gain_idx]
            
            rn = RN[self.cont.cnum][0][self.rn_idx]
            
            tbgn = np.sqrt(rn**2 + self.df*self.exposure + sf*self.exposure)
            current_tbgn = np.sqrt(rn**2 + self.df*self.exposure + self.sf*self.exposure)
            
            dr = np.log10(sat_cap/tbgn)/np.log10(2)
            current_dr = np.log10(sat_cap/current_tbgn)/np.log10(2)
            
            self.ax.cla()
            self.ax.plot((convSig(sf, True) if self.cont.lumSignalType.get() else sf), dr, '-',
                         color='navy')
            p, = self.ax.plot((convSig(self.sf, True) if self.cont.lumSignalType.get() else self.sf),
                              current_dr, 'o', color='navy', label='Current values')
            self.ax.legend(handles=[p], loc='best', numpoints=1, fontsize=small_fs)
            self.ax.set_title(self.p8, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Skyglow %s' % (u'[mag/arcsec\u00B2]' \
                                               if self.cont.lumSignalType.get() else '[e-/s]'),
                               name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('Dynamic range [stops]', name='Tahoma', fontsize=small_fs)
            self.canvas.draw()
            
        elif type == self.p9:
        
            exposure = np.linspace(1, 900, 200)
        
            sat_cap = SAT_CAP[self.cont.cnum][0][self.gain_idx]
            
            rn = RN[self.cont.cnum][0][self.rn_idx]
            
            tbgn = np.sqrt(rn**2 + self.df*exposure + self.sf*exposure)
            
            dr = np.log10(sat_cap/tbgn)/np.log10(2)
            
            self.ax.cla()
            self.ax.plot(exposure, dr, '-', color='navy')
            self.ax.set_title(self.p9, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Sub exposure time [s]', name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('Dynamic range [stops]', name='Tahoma', fontsize=small_fs)
            self.canvas.draw()
            
        elif type == self.p10:
        
            tf = np.linspace(0*self.tf, 2*self.tf, 201)
            
            rn = RN[self.cont.cnum][0][self.rn_idx]
            
            snr = tf*self.exposure/np.sqrt(tf*self.exposure + self.sf*self.exposure \
                                           + self.df*self.exposure + rn**2)
            current_snr = self.tf*self.exposure/np.sqrt(self.tf*self.exposure + self.sf*self.exposure \
                                                        + self.df*self.exposure + rn**2)
            
            self.ax.cla()
            self.ax.plot((convSig(tf, True) if self.cont.lumSignalType.get() else tf), snr, '-',
                         color='crimson')
            p, = self.ax.plot((convSig(self.tf, True) if self.cont.lumSignalType.get() else self.tf),
                              current_snr, 'o', color='crimson', label='Current values')
            self.ax.legend(handles=[p], loc='best', numpoints=1, fontsize=small_fs)
            self.ax.set_title(self.p10, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Target signal %s' % (u'[mag/arcsec\u00B2]' \
                                                     if self.cont.lumSignalType.get() else '[e-/s]'),
                               name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('Target SNR', name='Tahoma', fontsize=small_fs)
            self.canvas.draw()
            
        elif type == self.p11:
        
            gain = GAIN[self.cont.cnum][0]
            sat_cap = SAT_CAP[self.cont.cnum][0]
            
            if len(gain) < 2:
                self.varMessageLabel.set('At least two ISO values required.')
                return None
            
            self.ax.cla()
            self.ax.plot(np.log10(gain)/np.log10(2.0), np.log10(sat_cap)/np.log10(2.0), '-o',
                         color='darkviolet')
            self.ax.set_title(self.p11, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('log2(gain)', name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('log2(saturation capacity)', name='Tahoma', fontsize=small_fs)
            self.canvas.draw()
            
        self.varMessageLabel.set('Data plotted.')
            
    def activateTooltips(self):
    
        '''Add tooltips to all relevant widgets.'''
        
        createToolTip(self.entryExp, TTExp, self.cont.tt_fs)
        createToolTip(self.entryDF, TTDF, self.cont.tt_fs)
        createToolTip(self.entrySF, TTSFLum if self.cont.hasQE else TTSFElectron, self.cont.tt_fs)
        createToolTip(self.entryTF, TTTFLum if self.cont.hasQE else TTTFElectron, self.cont.tt_fs)
        createToolTip(self.entryTotal, TTTotal, self.cont.tt_fs)
        createToolTip(self.entryMax, TTMax, self.cont.tt_fs)
        
    def deactivateTooltips(self):
    
        '''Remove tooltips from all widgets.'''
    
        for widget in [self.entryExp, self.entryDF, self.entrySF, self.entryTF, self.entryTotal,
                       self.entryMax]:
                           
            widget.unbind('<Enter>')
            widget.unbind('<Motion>')
            widget.unbind('<Leave>')
    
    
class ImageAnalyser(ttk.Frame):

    def __init__(self, parent, controller):
    
        '''Initialize Image Analyser frame.'''
    
        ttk.Frame.__init__(self, parent)
        
        self.cont = controller
        
        # List of supported file formats
        self.supportedformats = [('DSLR RAW files', ('*.3fr', '*.R3D', '*.arw', '*.bay', '*.cap',
                                                     '*.cr2', '*.crw', '*.dcr', '*.dcs', '*.dng',
                                                     '*.drf', '*.eip', '*.erf', '*.fff', '*.iiq',
                                                     '*.k25', '*.kdc', '*.mdc', '*.mef', '*.mos',
                                                     '*.mrw', '*.nef', '*.nrw', '*.orf', '*.pef',
                                                     '*.ptx', '*.pxn', '*.raf', '*.raw', '*.rw2',
                                                     '*.rwl', '*.sr2', '*.srf', '*.srw', '*.x3f')),
                                 ('FITS and TIFF files', ('*.fit', '*.fits', '*.tif', '*.tiff'))]
        
        # List of image types that can be added
        self.imagetypes = ['Bias', 'Dark', 'Flat', 'Light', 'Saturated']
        
        self.mode = 'select'
        self.noInput = True # True if no files are added
        self.useGreen = None # Used to decide which CFA color to extract
        self.CFAPattern = None # Used to decide the CFA pattern of the color camera
        self.currentImage = None # ID for the currently showing canvas image
        self.selectionBox = None # ID for the canvas selection box
        self.measureLine = None # ID for the canvas measure line
        self.localSelection = False # True if a valid selection box is displayed
        self.menuActive = False # True when the right-click menu is showing
        self.previousPath = os.path.expanduser('~/Pictures') # Default file path
        self.busy = False # True when a topwindow is showing to disable use of other widgets
        self.currentCCDType = 'mono' # Camera type for the added images
        self.showResized = False # True when the displayed image is resized
        
        # Define values to keep track of number of added files
        self.displayed_bias = 0
        self.displayed_dark = 0
        self.displayed_flat = 0
        self.displayed_light = 0
        self.displayed_saturated = 0
        
        # Define widget variables
        
        self.varCCDType = tk.StringVar()
        
        self.varBiasHLabel = tk.StringVar()
        self.varDarkHLabel = tk.StringVar()
        self.varFlatHLabel = tk.StringVar()
        
        self.varBias1Label = tk.StringVar()
        self.varBias2Label = tk.StringVar()
        self.varDark1Label = tk.StringVar()
        self.varDark2Label = tk.StringVar()
        self.varFlat1Label = tk.StringVar()
        self.varFlat2Label = tk.StringVar()
        self.varLightLabel = tk.StringVar()
        self.varSaturatedLabel = tk.StringVar()
        
        self.varImType = tk.StringVar()
        self.varAddButtonLabel = tk.StringVar()
        
        self.varImInfo = tk.StringVar()
        self.varFOV = tk.StringVar()
        
        self.varMessageLabel = tk.StringVar()
        
        self.varCCDType.set('mono')
        self.varImType.set(self.imagetypes[0])
        self.varAddButtonLabel.set('Add bias frames')
        
        # Define frames
        
        frameHeader = ttk.Frame(self)
        
        frameContent = ttk.Frame(self)
        
        frameLeft = ttk.Frame(frameContent)
        frameRight = ttk.Frame(frameContent)
        
        frameMessage = ttk.Frame(self)
        
        # Place frames
        
        frameHeader.pack(side='top', fill='x')
        
        frameContent.pack(side='top', fill='both', expand=True)
        
        frameLeft.pack(side='left', fill='both', padx=(30*scsx, 0))
        frameRight.pack(side='right', fill='both', padx=(30*scsx, 0), expand=True)
        
        frameMessage.pack(side='bottom', fill='x')
        
        # *** Header frame ***
        
        labelHeader = ttk.Label(frameHeader, text='Image Analyser', font=self.cont.large_font,
                                anchor='center')
        
        frameNames = ttk.Frame(frameHeader)
        labelCamName = ttk.Label(frameNames, textvariable=self.cont.varCamName, anchor='center')
        labelTelName = ttk.Label(frameNames, textvariable=self.cont.varTelName, anchor='center')
        labelFLMod = ttk.Label(frameNames, textvariable=self.cont.varFLMod, anchor='center')
        
        labelHeader.pack(side='top', pady=3*scsy)
        
        ttk.Separator(frameHeader, orient='horizontal').pack(side='top', fill='x')
        
        frameNames.pack(side='top', fill='x')
        labelCamName.pack(side='left', expand=True)
        labelTelName.pack(side='left', expand=True)
        labelFLMod.pack(side='right', expand=True)
        
        # *** Left frame ***
        
        # Define left frame widgets
        
        labelType = ttk.Label(frameLeft, text='Camera type:', font=self.cont.smallbold_font,
                              anchor='center')
                              
        frameType = ttk.Frame(frameLeft)
        
        self.radioCCDm = ttk.Radiobutton(frameType, text='Mono CCD', variable=self.varCCDType,
                                         value='mono', command=self.changeCCDType)
        self.radioCCDc = ttk.Radiobutton(frameType, text='Color CCD', variable=self.varCCDType,
                                         value='color', command=self.changeCCDType)
        self.labelDSLR = ttk.Label(frameType, text='DSLR', font=self.cont.small_font,
                                   anchor='center')
        
        labelAdd = ttk.Label(frameLeft, text='Choose image type to add:',
                             font=self.cont.smallbold_font, anchor='center')
        self.optionAdd = ttk.OptionMenu(frameLeft, self.varImType, None, *self.imagetypes,
                                        command=self.updateFrameButtonText)
        self.buttonAdd = ttk.Button(frameLeft, textvariable=self.varAddButtonLabel,
                                    command=self.addImage)
        
        labelFiles = ttk.Label(frameLeft, text='Files', font=self.cont.smallbold_font,
                               anchor='center', width=22)
        self.frameFiles = ttk.Frame(frameLeft, style='files.TFrame', borderwidth=2, relief='groove',
                                    height=200*scsy)
        
        self.buttonClear = ttk.Button(frameLeft, text='Clear added files',
                                      command=lambda: self.showWarning('Warning',
                                      'Are you sure you want\nto remove all added files?',
                                                                       'Yes',
                                                                       'Cancel',
                                                                       self.clearFiles), width=19)
        
        self.buttonCompute = ttk.Button(frameLeft, text='Compute sensor data',
                                        command=self.computeSensorData, width=19)
        
        # Define file frame widgets
        
        self.frameBias = ttk.Frame(self.frameFiles, style='files.TFrame')
        self.frameDark = ttk.Frame(self.frameFiles, style='files.TFrame')
        self.frameFlat = ttk.Frame(self.frameFiles, style='files.TFrame')
        
        # Define bias frame widgets
        
        self.labelBiasH = ttk.Label(self.frameBias, textvariable=self.varBiasHLabel,
                                    style='file.TLabel', font=self.cont.smallbold_font, anchor='w')
        self.labelBias1 = ttk.Label(self.frameBias, textvariable=self.varBias1Label,
                                    style='file.TLabel', anchor='w')
        self.labelBias2 = ttk.Label(self.frameBias, textvariable=self.varBias2Label,
                                    style='file.TLabel', anchor='w')
        
        self.labelBias1.bind('<Button-1>', self.showImageEvent)
        self.labelBias2.bind('<Button-1>', self.showImageEvent)
        self.labelBias1.bind('<Button-3>', self.removeImageEvent)
        self.labelBias2.bind('<Button-3>', self.removeImageEvent)
        
        # Define dark frame widgets
        
        self.labelDarkH = ttk.Label(self.frameDark, textvariable=self.varDarkHLabel,
                                    style='file.TLabel', font=self.cont.smallbold_font, anchor='w')
        self.labelDark1 = ttk.Label(self.frameDark, textvariable=self.varDark1Label,
                                    style='file.TLabel', anchor='w')
        self.labelDark2 = ttk.Label(self.frameDark, textvariable=self.varDark2Label,
                                    style='file.TLabel', anchor='w')
        
        self.labelDark1.bind('<Button-1>', self.showImageEvent)
        self.labelDark2.bind('<Button-1>', self.showImageEvent)
        self.labelDark1.bind('<Button-3>', self.removeImageEvent)
        self.labelDark2.bind('<Button-3>', self.removeImageEvent)
        
        # Define flat frame widgets
        
        self.labelFlatH = ttk.Label(self.frameFlat, textvariable=self.varFlatHLabel,
                                    style='file.TLabel', font=self.cont.smallbold_font, anchor='w')
        self.labelFlat1 = ttk.Label(self.frameFlat, textvariable=self.varFlat1Label,
                                    style='file.TLabel', anchor='w')
        self.labelFlat2 = ttk.Label(self.frameFlat, textvariable=self.varFlat2Label,
                                    style='file.TLabel', anchor='w')
        
        self.labelFlat1.bind('<Button-1>', self.showImageEvent)
        self.labelFlat2.bind('<Button-1>', self.showImageEvent)
        self.labelFlat1.bind('<Button-3>', self.removeImageEvent)
        self.labelFlat2.bind('<Button-3>', self.removeImageEvent)
        
        # Define light frame widgets
        
        self.labelLightH = ttk.Label(self.frameFiles, text='Light frame', style='file.TLabel',
                                     font=self.cont.smallbold_font, anchor='w')
        self.labelLight = ttk.Label(self.frameFiles, textvariable=self.varLightLabel,
                                    style='file.TLabel', anchor='w')
        
        self.labelLight.bind('<Button-1>', self.showImageEvent)
        self.labelLight.bind('<Button-3>', self.removeImageEvent)
        
        # Define saturated frame widgets
        
        self.labelSaturatedH = ttk.Label(self.frameFiles, text='Saturated frame',style='file.TLabel',
                                         font=self.cont.smallbold_font, anchor='w')
        self.labelSaturated = ttk.Label(self.frameFiles, textvariable=self.varSaturatedLabel,
                                        style='file.TLabel', anchor='w')
        
        self.labelSaturated.bind('<Button-1>', self.showImageEvent)
        self.labelSaturated.bind('<Button-3>', self.removeImageEvent)
        
        # Place left frame widgets
        
        labelType.pack(side='top', pady=(10*scsy, 0))
        frameType.pack(side='top')
        
        labelAdd.pack(side='top', pady=(10*scsy, 0))
        self.optionAdd.pack(side='top', pady=(5*scsy, 5*scsy))
        self.buttonAdd.pack(side='top')
        
        labelFiles.pack(side='top', pady=(10*scsy, 5*scsy))
        self.frameFiles.pack(side='top', fill='both', expand=True)
        
        self.buttonClear.pack(side='top', pady=(10*scsy, 5*scsy))
        self.buttonCompute.pack(side='top', pady=(0, 10*scsy))
        
        # *** Right frame ***
        
        frameInfo = ttk.Frame(frameRight)
        labelImInfo = tk.Label(frameInfo, textvariable=self.varImInfo, font=self.cont.small_font)
        labelFOV = tk.Label(frameInfo, textvariable=self.varFOV, font=self.cont.small_font,
                            width=40, anchor='w')
        
        self.labelCanv = ttk.Label(frameRight, text='<Added images will be displayed here>',
                                   anchor='center')
        
        self.scrollbarCanvHor = ttk.Scrollbar(frameRight, orient='horizontal')
        self.scrollbarCanvVer = ttk.Scrollbar(frameRight, orient='vertical')
        self.canvasDisplay = tk.Canvas(frameRight, xscrollcommand=self.scrollbarCanvHor.set,
                                       yscrollcommand=self.scrollbarCanvVer.set, xscrollincrement='1',
                                       yscrollincrement='1')
        
        self.scrollbarCanvHor.config(command=self.canvasDisplay.xview)
        self.scrollbarCanvVer.config(command=self.canvasDisplay.yview)
        
        self.canvasDisplay.bind('<Button-1>', self.createSelectionBoxEvent)
        self.canvasDisplay.bind('<B1-Motion>', self.drawSelectionBoxEvent)
        self.canvasDisplay.bind('<ButtonRelease-1>', self.evaluateSelectionBoxEvent)
        self.canvasDisplay.bind('<Button-3>', self.showRCMenuEvent)
        
        frameInfo.pack(side='bottom', fill='x') 
        labelImInfo.pack(side='right', expand=True)
        labelFOV.pack(side='left', expand=True)
        self.labelCanv.pack(expand=True)
        
        # *** Message frame ***
        
        self.labelMessage = ttk.Label(frameMessage, textvariable=self.varMessageLabel)
        
        ttk.Separator(frameMessage, orient='horizontal').pack(side='top', fill='x')
        self.labelMessage.pack(anchor='w', padx=(5*scsx, 0))
        
        
        self.labelList = [self.labelBias1, self.labelBias2, self.labelDark1, self.labelDark2,
                          self.labelFlat1, self.labelFlat2, self.labelLight, self.labelSaturated]
                          
        # *** Right-click menu ***
        
        self.menuRC = tk.Menu(self.canvasDisplay, tearoff=0)
        self.menuRC.add_command(label='Show full image', command=self.useFullImage)
        self.menuRC.add_command(label='Fit to window', command=self.useResImage)
        self.menuRC.add_separator()
        self.menuRC.add_command(label='"Select" mode', command=self.useSelectMode)
        self.menuRC.add_command(label='"Measure" mode', command=self.useMeasureMode)
        self.menuRC.add_command(label='"Drag" mode', command=self.useDragMode)
        self.menuRC.add_separator()
        self.menuRC.add_command(label='Show histogram', command=self.showHistogram)
        self.menuRC.add_command(label='Show statistics', command=self.getStatistics)
        self.menuRC.add_command(label='Transfer data to Image Calculator', command=self.transferData)
        
        # Clear selection state of file labels
        for label in self.labelList:
            label.leftselected = False
            label.rightselected = False
            label.exposure = None
            label.iso = None
            label.photo_img_res = None
    
    def useFullImage(self):
    
        '''Show the displayed images at 100%.'''
        
        self.showResized = False
        
        if self.mode == 'select':
            self.useSelectMode()
        elif self.mode == 'drag':
            self.useDragMode()
        
        self.menuRC.entryconfig(3, state='normal')
        self.menuRC.entryconfig(5, state='normal')
        self.menuRC.entryconfig(8, state='normal')
        
        self.showImage(self.getSelectedLabel())
        
    def createResImage(self, label):
    
        '''Create an image resized to fit the window.'''
    
        w, h = label.pil_img.size
        
        f = np.min([(self.scrollbarCanvHor.winfo_width() - 17.0)/w,
                    self.scrollbarCanvVer.winfo_height()/float(h)])
                        
        label.photo_img_res = ImageTk.PhotoImage(label.pil_img.resize((int(round(f*w)),
                                                                       int(round(f*h))),
                                                                      Image.ANTIALIAS))
        
    def useResImage(self):
    
        '''Show a resized version of the image.'''
    
        self.showResized = True
        
        self.canvasDisplay.delete(self.selectionBox)
        self.localSelection = False
        
        if self.mode != 'measure':
            self.canvasDisplay.unbind('<Button-1>')
            self.canvasDisplay.unbind('<B1-Motion>')
            self.canvasDisplay.unbind('<ButtonRelease-1>')
        
        self.menuRC.entryconfig(3, state='disabled')
        self.menuRC.entryconfig(5, state='disabled')
        self.menuRC.entryconfig(8, state='disabled')
        
        label = self.getSelectedLabel()
        
        self.showImage(label)
    
    def forgetAttributes(self, label):
    
        '''Clear label attributes, including the images related to the label.'''
    
        label.raw_img = None
        label.stretched_img = None
        label.pil_img = None
        label.photo_img = None
        label.photo_img_res = None
        label.exposure = None
        label.iso = None
    
    def addImage(self):
    
        '''Add image file and show name in list.'''
        
        self.disableWidgets()
    
        type = self.varImType.get()
        
        supportedformats = [self.supportedformats[0]] if self.cont.isDSLR \
                                                      else [self.supportedformats[1]]
        
        if type == 'Bias':
        
            # Show error if two bias frames are already added
            if self.displayed_bias == 2:
                self.varMessageLabel.set('Cannot have more than 2 bias frames.')
                self.enableWidgets()
                return None
        
            # Show file selection menu and store selected files
            
            biasfiles = tkFileDialog.askopenfilenames(filetypes=supportedformats,
                                                      initialdir=self.previousPath)
            
            # Do nothing if no files were selected
            if biasfiles == '':
                self.enableWidgets()
                return None
            
            # Show error if too many files were selected
            if len(biasfiles) > 2 or (len(biasfiles) > 1 and self.displayed_bias == 1):
                self.varMessageLabel.set('Cannot have more than 2 bias frames.')
                self.enableWidgets()
                return None
                
            self.previousPath = '/'.join(biasfiles[-1].split('/')[:-1])
                
            # If one file was selected
            if len(biasfiles) == 1:
            
                # If no files are already added
                if self.displayed_bias == 0:
                
                    bias1path = biasfiles[0] # Store file path
                    
                    filename = bias1path.split('/')[-1] # Extract file name
                    
                    # Extract image data and store as attributes for bias 1 label
                    try:
                        self.getImage(self.labelBias1, bias1path, filename, 'bias')
                    except:
                        self.enableWidgets()
                        return None
                    
                    # Display header and file name
                    
                    self.varBias1Label.set(self.adjustName(self.labelBias1, filename))
                    self.varBiasHLabel.set('Bias frame')
                    
                    self.frameBias.pack(side='top', fill='x', anchor='w')
                    self.labelBiasH.pack(side='top', fill='x', anchor='w')
                    self.labelBias1.pack(side='top', fill='x', anchor='w')
                    
                    # Show canvas if this is the first added file
                    if self.noInput: self.showCanvas()
            
                    self.showImage(self.labelBias1)
                    
                    self.displayed_bias = 1
                    
                    self.varMessageLabel.set('Bias frame added.')
                
                # If one file is already added
                else:
                
                    bias2path = biasfiles[0]
                    
                    filename = bias2path.split('/')[-1]
                    
                    # Show error if the same file is already added
                    if filename == self.varBias1Label.get():
                        self.varMessageLabel.set('This bias frame is already added.')
                        self.enableWidgets()
                        return None
                    
                    # Extract image data and store as attributes for bias 2 label
                    try:
                        self.getImage(self.labelBias2, bias2path, filename, 'bias',
                                      compare=self.labelBias1)
                    except:
                        self.enableWidgets()
                        return None
                    
                    # Display file name after the existing one
                    
                    self.varBias2Label.set(self.adjustName(self.labelBias2, filename))
                    self.varBiasHLabel.set('Bias frames')
                    
                    self.labelBias2.pack(side='top', fill='x', anchor='w')
                    
                    self.showImage(self.labelBias2)
                    
                    self.displayed_bias = 2
                    
                    # Cycle image type optionmenu to flat frames
                    self.varImType.set('Flat')
                    self.updateFrameButtonText('Flat')
                    
                    self.varMessageLabel.set('Bias frame added.')
            
            # If two files were selected
            else:
            
                # Add paths for both files and show both file names
            
                bias1path = biasfiles[0]
                bias2path = biasfiles[1]
                
                filename1 = bias1path.split('/')[-1]
                filename2 = bias2path.split('/')[-1]
                
                # Extract image data and store as attributes for bias 1 and bias 2 labels
                try:
                    self.getImage(self.labelBias1, bias1path, filename1, 'bias')
                except:
                    self.enableWidgets()
                    return None
                    
                self.varBias1Label.set(self.adjustName(self.labelBias1, filename1))
                self.varBiasHLabel.set('Bias frames')
                
                self.frameBias.pack(side='top', fill='x', anchor='w')
                self.labelBiasH.pack(side='top', fill='x', anchor='w')
                self.labelBias1.pack(side='top', fill='x', anchor='w')
                
                if self.noInput: self.showCanvas()
                
                self.showImage(self.labelBias1)
                    
                self.update() # Update window to show changes
                
                try:
                    self.getImage(self.labelBias2, bias2path, filename2, 'bias',
                                  compare=self.labelBias1)
                except:
                    self.enableWidgets()
                    self.displayed_bias = 1
                    return None
                
                self.varBias2Label.set(self.adjustName(self.labelBias2, filename2))
                
                self.labelBias2.pack(side='top', fill='x', anchor='w')
                
                self.showImage(self.labelBias2)
                
                self.displayed_bias = 2
                
                self.varImType.set('Flat')
                self.updateFrameButtonText('Flat')
                
                self.varMessageLabel.set('Bias frames added.')
        
        elif type == 'Dark':
        
            if self.displayed_dark == 2:
                self.varMessageLabel.set('Cannot have more than 2 dark frames.')
                self.enableWidgets()
                return None
        
            darkfiles = tkFileDialog.askopenfilenames(filetypes=supportedformats,
                                                      initialdir=self.previousPath)
            
            if darkfiles == '':
                self.enableWidgets()
                return None
            
            if len(darkfiles) > 2 or (len(darkfiles) > 1 and self.displayed_dark == 1):
                self.varMessageLabel.set('Cannot have more than 2 dark frames.')
                self.enableWidgets()
                return None
                
            self.previousPath = '/'.join(darkfiles[-1].split('/')[:-1])
                
            if len(darkfiles) == 1:
            
                if self.displayed_dark == 0:
                
                    dark1path = darkfiles[0]
                    
                    filename = dark1path.split('/')[-1]
                    
                    try:
                        self.getImage(self.labelDark1, dark1path, filename, 'dark')
                    except:
                        self.enableWidgets()
                        return None
                    
                    self.varDark1Label.set(self.adjustName(self.labelDark1, filename))
                    self.varDarkHLabel.set('Dark frame')
                    
                    self.frameDark.pack(side='top', fill='x', anchor='w')
                    self.labelDarkH.pack(side='top', fill='x', anchor='w')
                    self.labelDark1.pack(side='top', fill='x', anchor='w')
                    
                    if self.noInput: self.showCanvas()
            
                    self.showImage(self.labelDark1)
                    
                    self.displayed_dark = 1
                    
                    self.varMessageLabel.set('Dark frame added.')
                
                else:
                
                    dark2path = darkfiles[0]
                    
                    filename = dark2path.split('/')[-1]
                    
                    if filename == self.varDark1Label.get():
                        self.varMessageLabel.set('This dark frame is already added.')
                        self.enableWidgets()
                        return None
                    
                    try:
                        self.getImage(self.labelDark2, dark2path, filename, 'dark',
                                      compare=self.labelDark1)
                    except:
                        self.enableWidgets()
                        return None
                    
                    self.varDark2Label.set(self.adjustName(self.labelDark2, filename))
                    self.varDarkHLabel.set('Dark frames')
                    
                    self.labelDark2.pack(side='top', fill='x', anchor='w')
                    
                    self.showImage(self.labelDark2)
                    
                    self.displayed_dark = 2
                    
                    self.varImType.set('Light')
                    self.updateFrameButtonText('Light')
                    
                    self.varMessageLabel.set('Dark frame added.')
            
            else:
            
                dark1path = darkfiles[0]
                dark2path = darkfiles[1]
                
                filename1 = dark1path.split('/')[-1]
                filename2 = dark2path.split('/')[-1]
                
                try:
                    self.getImage(self.labelDark1, dark1path, filename1, 'dark')
                except:
                    self.enableWidgets()
                    return None
                    
                self.varDark1Label.set(self.adjustName(self.labelDark1, filename1))
                self.varDarkHLabel.set('Dark frames')
                
                self.frameDark.pack(side='top', fill='x', anchor='w')
                self.labelDarkH.pack(side='top', fill='x', anchor='w')
                self.labelDark1.pack(side='top', fill='x', anchor='w')
                
                if self.noInput: self.showCanvas()
                
                self.showImage(self.labelDark1)
                
                self.update()
                    
                try:
                    self.getImage(self.labelDark2, dark2path, filename2, 'dark',
                                  compare=self.labelDark1)
                except:
                    self.enableWidgets()
                    self.displayed_dark = 1
                    return None
                
                self.varDark2Label.set(self.adjustName(self.labelDark2, filename2))
                
                self.labelDark2.pack(side='top', fill='x', anchor='w')
                
                self.showImage(self.labelDark2)
                
                self.displayed_dark = 2
                    
                self.varImType.set('Light')
                self.updateFrameButtonText('Light')
                
                self.varMessageLabel.set('Dark frames added.')
            
        elif type == 'Flat':
        
            if self.displayed_flat == 2:
                self.varMessageLabel.set('Cannot have more than 2 flat frames.')
                self.enableWidgets()
                return None
        
            flatfiles = tkFileDialog.askopenfilenames(filetypes=supportedformats,
                                                      initialdir=self.previousPath)
            
            if flatfiles == '':
                self.enableWidgets()
                return None
            
            if len(flatfiles) > 2 or (len(flatfiles) > 1 and self.displayed_flat == 1):
                self.varMessageLabel.set('Cannot have more than 2 flat frames.')
                self.enableWidgets()
                return None
                
            self.previousPath = '/'.join(flatfiles[-1].split('/')[:-1])
                
            if len(flatfiles) == 1:
            
                if self.displayed_flat == 0:
                
                    flat1path = flatfiles[0]
                    
                    filename = flat1path.split('/')[-1]
                    
                    try:
                        self.getImage(self.labelFlat1, flat1path, filename, 'flat',
                                      splitCFA=(self.cont.isDSLR or self.varCCDType.get() == 'color'))
                    except:
                        self.enableWidgets()
                        return None
                        
                    color = ' (green)' if self.useGreen == True \
                                       else (' (red)' if self.useGreen == False else '')
                    
                    self.varFlat1Label.set(self.adjustName(self.labelFlat1, filename + color))
                    self.varFlatHLabel.set('Flat frame')
                    
                    self.frameFlat.pack(side='top', fill='x', anchor='w')
                    self.labelFlatH.pack(side='top', fill='x', anchor='w')
                    self.labelFlat1.pack(side='top', fill='x', anchor='w')
                    
                    if self.noInput: self.showCanvas()
                    
                    self.showImage(self.labelFlat1)
                    
                    self.displayed_flat = 1
                    
                    self.varMessageLabel.set('Flat frame added.')
                
                else:
                
                    flat2path = flatfiles[0]
                    
                    filename = flat2path.split('/')[-1]
                    
                    if filename == self.varFlat1Label.get().split(' (')[0]:
                        self.varMessageLabel.set('This flat frame is already added.')
                        self.enableWidgets()
                        return None
                        
                    color = ' (green)' if self.useGreen == True \
                                       else (' (red)' if self.useGreen == False else '')
                    
                    try:
                        self.getImage(self.labelFlat2, flat2path, filename, 'flat',
                                      splitCFA=(self.cont.isDSLR or self.varCCDType.get() == 'color'),
                                      compare=self.labelFlat1)
                    except:
                        self.enableWidgets()
                        return None
                    
                    self.varFlat2Label.set(self.adjustName(self.labelFlat2, filename + color))
                    self.varFlatHLabel.set('Flat frames')
                    
                    self.labelFlat2.pack(side='top', fill='x', anchor='w')
                    
                    self.showImage(self.labelFlat2)
                    
                    self.displayed_flat = 2
                    
                    self.varImType.set('Saturated')
                    self.updateFrameButtonText('Saturated')
                    
                    self.varMessageLabel.set('Flat frame added.')
                    
            else:
            
                flat1path = flatfiles[0]
                flat2path = flatfiles[1]
                
                filename1 = flat1path.split('/')[-1]
                filename2 = flat2path.split('/')[-1]
                
                try:
                    self.getImage(self.labelFlat1, flat1path, filename1, 'flat',
                                  splitCFA=(self.cont.isDSLR or self.varCCDType.get() == 'color'))
                except:
                    self.enableWidgets()
                    return None
                    
                color = ' (green)' if self.useGreen == True \
                                   else (' (red)' if self.useGreen == False else '')
                    
                self.varFlat1Label.set(self.adjustName(self.labelFlat1, filename1 + color))
                self.varFlatHLabel.set('Flat frames')
                
                self.frameFlat.pack(side='top', fill='x', anchor='w')
                self.labelFlatH.pack(side='top', fill='x', anchor='w')
                self.labelFlat1.pack(side='top', fill='x', anchor='w')
                
                if self.noInput: self.showCanvas()
                
                self.showImage(self.labelFlat1)
                    
                self.update()
                    
                try:
                    self.getImage(self.labelFlat2, flat2path, filename2, 'flat',
                                  splitCFA=(self.cont.isDSLR or self.varCCDType.get() == 'color'),
                                  compare=self.labelFlat1)
                except:
                    self.enableWidgets()
                    self.displayed_flat = 1
                    return None
                
                self.varFlat2Label.set(self.adjustName(self.labelFlat2, filename2 + color))
                
                self.labelFlat2.pack(side='top', fill='x', anchor='w')
                
                self.showImage(self.labelFlat2)
                
                self.displayed_flat = 2
                    
                self.varImType.set('Saturated')
                self.updateFrameButtonText('Saturated')
                    
                self.varMessageLabel.set('Flat frames added.')
                
        elif type == 'Light':
        
            if self.displayed_light == 1:
                self.varMessageLabel.set('Cannot have more than 1 light frame.')
                self.enableWidgets()
                return None
        
            lightfiles = tkFileDialog.askopenfilenames(filetypes=supportedformats,
                                                       initialdir=self.previousPath)
            
            if lightfiles == '':
                self.enableWidgets()
                return None
            
            if len(lightfiles) > 1:
                self.varMessageLabel.set('Cannot have more than 1 light frame.')
                self.enableWidgets()
                return None
                
            self.previousPath = '/'.join(lightfiles[-1].split('/')[:-1])
                
            lightpath = lightfiles[0]
                    
            filename = lightpath.split('/')[-1]
                    
            try:
                self.getImage(self.labelLight, lightpath, filename, 'light',
                              splitCFA=(self.cont.isDSLR or self.varCCDType.get() == 'color'))
            except:
                self.enableWidgets()
                return None
                
            color = ' (green)' if self.useGreen == True \
                               else (' (red)' if self.useGreen == False else '')
                    
            self.varLightLabel.set(self.adjustName(self.labelLight, filename + color))
                    
            self.labelLightH.pack(side='top', fill='x', anchor='w')
            self.labelLight.pack(side='top', fill='x', anchor='w')
                    
            if self.noInput: self.showCanvas()
                    
            self.showImage(self.labelLight)
                    
            self.displayed_light = 1
                    
            self.varImType.set('Dark')
            self.updateFrameButtonText('Dark')
                    
            self.varMessageLabel.set('Light frame added.')
            
        elif type == 'Saturated':
        
            if self.displayed_saturated == 1:
                self.varMessageLabel.set('Cannot have more than 1 saturated frame.')
                self.enableWidgets()
                return None
        
            saturatedfiles = tkFileDialog.askopenfilenames(filetypes=supportedformats,
                                                           initialdir=self.previousPath)
            
            if saturatedfiles == '':
                self.enableWidgets()
                return None
            
            if len(saturatedfiles) > 1:
                self.varMessageLabel.set('Cannot have more than 1 saturated frame.')
                self.enableWidgets()
                return None
                
            self.previousPath = '/'.join(saturatedfiles[-1].split('/')[:-1])
                
            saturatedpath = saturatedfiles[0]
                    
            filename = saturatedpath.split('/')[-1]
                    
            try:
                self.getImage(self.labelSaturated, saturatedpath, filename, 'saturated')
            except:
                self.enableWidgets()
                return None
                    
            self.varSaturatedLabel.set(self.adjustName(self.labelSaturated, filename))
                    
            self.labelSaturatedH.pack(side='top', fill='x', anchor='w')
            self.labelSaturated.pack(side='top', fill='x', anchor='w')
                    
            if self.noInput: self.showCanvas()
                    
            self.showImage(self.labelSaturated)
                    
            self.displayed_saturated = 1
                    
            self.varImType.set('Bias')
            self.updateFrameButtonText('Bias')
                    
            self.varMessageLabel.set('Saturated frame added.')
            
        self.enableWidgets()
        self.noInput = False
    
    def showCanvas(self):
    
        '''Show canvas widget and scrollbars.'''
    
        self.labelCanv.pack_forget()
        self.scrollbarCanvHor.pack(side='bottom', fill='x')
        self.scrollbarCanvVer.pack(side='right', fill='y')
        self.canvasDisplay.pack(side='left', fill='both', expand=True)
    
    def disableWidgets(self):
    
        '''Disable widgets that can be interacted with.'''
    
        self.radioCCDm.configure(state='disabled')
        self.radioCCDc.configure(state='disabled')
        self.optionAdd.configure(state='disabled')
        self.buttonAdd.configure(state='disabled')
        self.buttonClear.configure(state='disabled')
        self.buttonCompute.configure(state='disabled')
        for label in self.labelList:
            label.configure(state='disabled')
        
    def enableWidgets(self):
    
        '''Enable widgets that can be interacted with.'''
    
        try:
            self.radioCCDm.configure(state='normal')
            self.radioCCDc.configure(state='normal')
            self.optionAdd.configure(state='normal')
            self.buttonAdd.configure(state='normal')
            self.buttonClear.configure(state='normal')
            self.buttonCompute.configure(state='normal')
            for label in self.labelList:
                label.configure(state='normal')
        except:
            pass
    
    def adjustName(self, label, name):
    
        '''Cut the filename if it reaches the end of the file frame.'''
    
        namewidth = self.cont.small_font.measure(name)
        framewidth = self.frameFiles.winfo_width()
    
        if namewidth > framewidth:
        
            createToolTip(label, name, self.cont.tt_fs)
            
            maxidx = int(np.floor(len(name)*framewidth/namewidth))
            name = name[:maxidx] + '..'
            
        else:
            
            label.unbind('<Enter>')
            label.unbind('<Motion>')
            label.unbind('<Leave>')
            
        return name
        
    def changeCCDType(self):
    
        '''Warn user that added data will be lost when changing camera type.'''
    
        # If files have been added
        if not self.noInput:
        
            def cmd():
                self.clearFiles()
                self.currentCCDType = self.varCCDType.get()
                self.varMessageLabel.set('CCD type changed to %s.' % (self.varCCDType.get()))
                
            self.showWarning('Warning', 'Changing CCD type will\nremove added files. Proceed?',
                             'Yes', 'Cancel', cmd)
                             
            # Change camera type back to previous state if the window was exited
            if self.varCCDType.get() != self.currentCCDType:
                self.varCCDType.set(self.currentCCDType)
            
        else:
            # Show message that the camera type was changed
            self.varMessageLabel.set('CCD type changed to %s.' % (self.varCCDType.get()))
            self.currentCCDType = self.varCCDType.get()
     
    def clearFiles(self):
    
        '''Reset attributes and clear added files.'''
        
        self.noInput = True
        
        self.useGreen = None
        self.CFAPattern = None
        self.currentImage = None
        
        self.displayed_bias = 0
        self.displayed_dark = 0
        self.displayed_flat = 0
        self.displayed_light = 0
        self.displayed_saturated = 0
        
        for label in self.labelList:
            self.forgetAttributes(label)
            label.leftselected = False
            label.rightselected = False
            label.pack_forget()
        
        self.varBias1Label.set('')
        self.varBias2Label.set('')
        self.varDark1Label.set('')
        self.varDark2Label.set('')
        self.varFlat1Label.set('')
        self.varFlat2Label.set('')
        self.varLightLabel.set('')
        self.varSaturatedLabel.set('')
        
        self.varImInfo.set('')
        self.varFOV.set('')
        
        self.frameBias.pack_forget()
        self.labelBiasH.pack_forget()
        self.frameDark.pack_forget()
        self.labelDarkH.pack_forget()
        self.frameFlat.pack_forget()
        self.labelFlatH.pack_forget()
        self.labelLightH.pack_forget()
        self.labelSaturatedH.pack_forget()
        
        self.canvasDisplay.delete(self.currentImage)
        self.canvasDisplay.delete(self.selectionBox)
        self.canvasDisplay.pack_forget()
        self.scrollbarCanvHor.pack_forget()
        self.scrollbarCanvVer.pack_forget()
        self.labelCanv.pack(expand=True)
        
    def getImage(self, label, filepath, filename, type, splitCFA=False, compare=False):
    
        '''Read image data and store as label attributes.'''
        
        self.varMessageLabel.set('%s - Loading file..' % filename)
        self.labelMessage.update_idletasks()
        
        # Create path string compatible with windows terminal
        norm_filepath = os.path.normpath('"' + filepath + '"')
            
        # Create path string compatible with python file opening methods
        py_filepath = '\\'.join(filepath.split('/'))
    
        # If image is a DSLR raw image
        if self.cont.isDSLR:
        
            self.varMessageLabel.set('%s - Converting to TIFF..' % filename)
            self.labelMessage.update_idletasks()
            
            # Create TIFF file from raw with dcraw
            subprocess.call('dcraw -4 -o 0 -D -t 0 -k 0 -H 1 -T -j -W %s' \
                            % norm_filepath.encode(sys.getfilesystemencoding()), shell=True)
            
            self.varMessageLabel.set('%s - Reading Exif metadata..' % filename)
            self.labelMessage.update_idletasks()
            
            tiff_filepath = '.'.join(py_filepath.split('.')[:-1]) + '.tiff'
            
            file = open(tiff_filepath, 'rb')
            tags = exifread.process_file(file)
            file.close()
            
            try:
                iso = int(str(tags['EXIF ISOSpeedRatings']))
                
            except (KeyError, ValueError):
                iso = None
                
            if iso is not None:
                
                isovals = []
                
                for otherlabel in self.labelList:
                
                    if label is not otherlabel and otherlabel.iso is not None:
                    
                        isovals.append(otherlabel.iso)
                
                if len(isovals) > 0 and isovals[1:] == isovals[:-1] and not iso in isovals:
                    
                    warning = 'This frame has ISO %d, whereas the\nother added frames have ISO %d.' \
                               % (iso, isovals[0]) + '\nStill proceed?' 
                    
                    if not self.showWarning('Warning', warning, 'Yes', 'Cancel', lambda: None):
                            
                        self.varMessageLabel.set('Cancelled.')
                        raise Exception
            
            label.exposure = self.checkExp(True, tags, compare, label, type)
            label.iso = iso
            
            self.varMessageLabel.set('%s - Extracting raw data..' % filename)
            self.labelMessage.update_idletasks()
            
            # Get array of image data
            img = plt.imread(tiff_filepath)
            
            self.varMessageLabel.set('%s - Deleting TIFF file..' % filename)
            self.labelMessage.update_idletasks()
            
            # Delete TIFF file created by dcraw
            subprocess.call('del /Q %s' \
                            % (os.path.normpath('"'  + '.'.join(filepath.split('.')[:-1]) + '.tiff"'))\
                              .encode(sys.getfilesystemencoding()),
                            shell=True)
            
            self.varMessageLabel.set('%s - Checking image dimensions..' % filename)
            self.labelMessage.update_idletasks()
            
            # Show error if the image size if different from the previously added image
            if compare and (img.shape != np.array(compare.raw_img.shape)*(2 if splitCFA else 1)).any():
                self.varMessageLabel.set('Error: The dimensions of "%s" does not match ' % filename \
                                             + 'those of the other added frame.')
                raise Exception
                
        # If image is a CCD raw image
        else:
            
            # If image is a TIFF file
            if filename.split('.')[1].lower() in ['tif', 'tiff']:
            
                self.varMessageLabel.set('%s - Reading TIFF file..' % filename)
                self.labelMessage.update_idletasks()
            
                # Get array of image data from TIFF file
                img = plt.imread(py_filepath)
                
                self.varMessageLabel.set('%s - Reading Exif metadata..' % filename)
                self.labelMessage.update_idletasks()
                
                file = open(py_filepath, 'rb')
                tags = exifread.process_file(file)
                file.close()
                
                label.exposure = self.checkExp(True, tags, compare, label, type)
                
            # If image is a FITS file
            elif filename.split('.')[1].lower() in ['fit', 'fits']:
                
                self.varMessageLabel.set('%s - Reading FITS file..' % filename)
                self.labelMessage.update_idletasks()
                
                # Get array of image data from FITS file
                hdulist = pyfits.open(py_filepath)
                
                img = hdulist[0].data
                header = hdulist[0].header
                
                hdulist.close()
                
                self.varMessageLabel.set('%s - Reading FITS header..' % filename)
                self.labelMessage.update_idletasks()
                
                label.exposure = self.checkExp(False, header, compare, label, type)
                
            if len(img.shape) != 2:
                self.varMessageLabel.set('Image file "%s" contains color channels.' \
                                         + 'Please use a non-debayered image.' % filename)
                raise Exception
                
        # If image has a CFA and a specific color needs to be extracted
        if splitCFA:
                
            self.varMessageLabel.set('%s - Detecting CFA pattern..' % filename)
            self.labelMessage.update_idletasks()
            
            # Get which color of pixels to extract from user if neccessary
            if self.useGreen is None:
                self.busy = True
                self.askColor()
                self.wait_window(self.topAskColor)
                self.busy = False
                self.useGreen = self.varUseGreen.get()
                
            # Abort if user cancels
            if self.cancelled:
                self.varMessageLabel.set('Cancelled.')
                raise Exception
            
            # If image is a DSLR raw image
            if self.cont.isDSLR:
                
                # Get string of raw file information
                metadata = subprocess.check_output('dcraw -i -v %s' \
                                    % norm_filepath.encode(sys.getfilesystemencoding()), shell=True)
                    
                # Extract string representing CFA pattern
                if self.CFAPattern is None:
                    for line in metadata.split('\n'):
                        
                        parts = line.split(': ')
                            
                        if parts[0] == 'Filter pattern': self.CFAPattern = parts[1].strip()
                
            # Ask user for CFA pattern if it wasn't detected or if camera is color CCD
            if self.CFAPattern is None:
                self.busy = True
                self.askCFAPattern()
                self.wait_window(self.topAskCFA)
                self.busy = False
                self.CFAPattern = self.varCFAPattern.get()
                
            # Abort if user cancels
            if self.cancelled:
                self.varMessageLabel.set('Cancelled.')
                raise Exception
                
            if not self.CFAPattern in ['RG/GB', 'BG/GR', 'GR/BG', 'GB/RG']:
                self.varMessageLabel.set('Error: CFA pattern %s not recognized.' % (self.CFAPattern))
                raise Exception
                
            self.varMessageLabel.set('%s - Extracting %s pixels..' \
                                     % (filename, ('green' if self.useGreen else 'red')))
            self.labelMessage.update_idletasks()
                
            # Extract green and red pixels as separate images
                
            h, w = img.shape
                
            if (self.CFAPattern == 'GB/RG' and self.useGreen) \
               or (self.CFAPattern == 'GR/BG' and self.useGreen) \
               or (self.CFAPattern == 'RG/GB' and not self.useGreen):
                new_img = img[0:(h-1):2, 0:(w-1):2] # Quadrant 1
            elif (self.CFAPattern == 'RG/GB' and self.useGreen) \
                 or (self.CFAPattern == 'BG/GR' and self.useGreen) \
                 or (self.CFAPattern == 'GR/BG' and not self.useGreen):
                new_img = img[0:(h-1):2, 1:w:2] # Quadrant 2
            elif self.CFAPattern == 'GB/RG' and not self.useGreen:
                new_img = img[1:h:2, 0:(w-1):2] # Quadrant 3
            elif self.CFAPattern == 'BG/GR' and not self.useGreen:
                new_img = img[1:h:2, 1:w:2] # Quadrant 4
                
            if type == 'light':
                self.labelLight.isSplitted = True
        
        # If image is mono or is to keep all pixels
        else:
            
            new_img = img
            
            if type == 'light':
                self.labelLight.isSplitted = False
        
        # Store raw image data as label attribute
        label.raw_img = new_img[:, :]
            
        self.varMessageLabel.set('%s - Applying screen stretch..' % filename)
        self.labelMessage.update_idletasks()
        
        label.stretched_img = autostretch(new_img)
        
        self.varMessageLabel.set('%s - Converting to JPEG..' % filename)
        self.labelMessage.update_idletasks()
        self.updateDisplayedImage(label, filename=filename)
                
    def checkExp(self, isTiff, metadata, compare, label, type):
    
        '''Find the exposure time of the added image, and compare to existing values.'''

        try:
            # Check image metadata for exposure time
            if isTiff:
                exposure_str = str(metadata['EXIF ExposureTime'])
            else:
                try:
                    exposure_str = str(metadata['EXPTIME'])
                except:
                    exposure_str = str(metadata['EXPOSURE'])
            
            # Calculate exposure in seconds if the quoted exposure time is a fraction
            if '/' in exposure_str:
                    
                fraction_parts = exposure_str.split('/')
                exposure_num = float(fraction_parts[0])/float(fraction_parts[1])
                        
            else:
                    
                exposure_num = float(exposure_str)
            
            # Show a warning of two frames of the same (relevant) type have very different exposures
            if compare and compare.exposure is not None:
                    
                exp1 = compare.exposure
                exp2 = exposure_num
                        
                if self.tooDiff(exp1, exp2):
                        
                    warning = 'The two %s frames have\nsignificantly different ' % type \
                               + 'exposure times.\n(%.4g s vs. %.4g s)\nStill proceed?' \
                               % (exp1, exp2)
                               
                    if not self.showWarning('Warning', warning, 'Yes', 'Cancel', lambda: None):
                            
                        self.varMessageLabel.set('Cancelled.')
                        raise Exception
            
        except (KeyError, ValueError):
            exposure_num = None
        
        warning = False
        
        # Compare light and dark exposure times and show a warning if they are very different
        if type == 'light' and exposure_num is not None:
        
            expvals = []
            
            for lab in [self.labelDark1, self.labelDark2]:
            
                if lab.exposure is not None:
                
                    expvals.append(lab.exposure)
                    
            if len(expvals) == 1 and self.tooDiff(exposure_num, expvals[0]):
            
                warning = 'This light frame and an added dark frame\nhave significantly ' \
                           + 'different exposure times.\n(%.4g s vs. %.4g s)\nStill proceed?' \
                           % (exposure_num, expvals[0])
                           
            elif len(expvals) == 2 and not self.tooDiff(*expvals) \
                                   and self.tooDiff(exposure_num, expvals[0]):
            
                warning = 'This light frame and the added dark frames\nhave significantly ' \
                          + 'different exposure times.\n(%.4g s vs. %.4g s)\nStill proceed?' \
                          % (exposure_num, expvals[0])
                          
        elif type == 'dark' and self.displayed_light == 1 and exposure_num is not None:
        
            if self.tooDiff(self.labelLight.exposure, exposure_num) \
                                and (label is self.labelDark1 or self.labelDark1.exposure is None):
                                
                warning = 'This dark frame and the added light frame\nhave significantly ' \
                          + 'different exposure times.\n(%.4g s vs. %.4g s)\nStill proceed?' \
                          % (exposure_num, self.labelLight.exposure)
        
        # Display the warning window
        if warning:
            if not self.showWarning('Warning', warning, 'Yes', 'Cancel', lambda: None):
                            
                self.varMessageLabel.set('Cancelled.')
                raise Exception
                
        return exposure_num
       
    def tooDiff(self, exp1, exp2):
    
        '''Return true if the exposure times differ by more than 10%.'''
        
        return np.abs(exp1 - exp2) >= 0.05*(exp1 + exp2)
       
    def askColor(self):
    
        '''Show window with options for choosing which CFA color to extract.'''
    
        def ok():
        
            '''Set confirmation that the window wasn't exited, and close window.'''
        
            self.cancelled = False
            self.topAskColor.destroy()
        
        # Setup window
        
        self.topAskColor = tk.Toplevel()
        self.topAskColor.title('Choose color')
        self.cont.addIcon(self.topAskColor)
        setupWindow(self.topAskColor, 300, 145)
        self.topAskColor.focus_force()
        
        self.cancelled = True
        self.varUseGreen = tk.IntVar()
        self.varUseGreen.set(1)
        
        tk.Label(self.topAskColor,
                  text='Choose which color of pixels to extract.\nGreen is recommended unless the '\
                       + 'image\nwas taken with a red narrowband filter.',
                  font=self.cont.small_font).pack(side='top', pady=(10*scsy, 5*scsy), expand=True)
        
        frameRadio = ttk.Frame(self.topAskColor)
        frameRadio.pack(side='top', expand=True, pady=(0, 10*scsy))
        ttk.Radiobutton(frameRadio, text='Green', variable=self.varUseGreen,
                        value=1).grid(row=0, column=0)
        ttk.Radiobutton(frameRadio, text='Red', variable=self.varUseGreen,
                        value=0).grid(row=0, column=1)
        
        ttk.Button(self.topAskColor, text='OK', command=ok).pack(side='top', expand=True,
                                                                 pady=(0, 10*scsy))
    
    def askCFAPattern(self):
    
        '''Show window with options for choosing which CFA pattern to use.'''
    
        def ok():
        
            '''Set confirmation that the window wasn't exited, and close window.'''
        
            self.cancelled = False
            self.topAskCFA.destroy()
            
        # Setup window
        
        self.topAskCFA = tk.Toplevel()
        self.topAskCFA.title('Choose filter pattern')
        self.cont.addIcon(self.topAskCFA)
        setupWindow(self.topAskCFA, 300, 145)
        self.topAskCFA.focus_force()
        
        self.cancelled = True
        CFAList = ['RG/GB', 'BG/GR', 'GR/BG', 'GB/RG']
        
        self.varCFAPattern = tk.StringVar()
        self.varCFAPattern.set(CFAList[0])
        
        ttk.Label(self.topAskCFA, text='Choose the color filter pattern of your camera.',
                  anchor='center').pack(side='top', pady=(10*scsy, 5*scsy), expand=True)
        
        ttk.OptionMenu(self.topAskCFA, self.varCFAPattern, None, *CFAList).pack(side='top',
                                                                                expand=True,
                                                                                pady=(0, 10*scsy))
        
        ttk.Button(self.topAskCFA, text='OK', command=ok).pack(side='top', expand=True,
                                                               pady=(0, 10*scsy))
    
    def showImageEvent(self, event):
    
        '''Only call the show image method when label is clicked if no topwindow is showing.'''
    
        if not self.busy: self.showImage(event.widget)
        
    def showImage(self, label):
    
        '''Change background of given label to blue and show the photoimage of the label.'''
        
        label.configure(style='leftselectedfile.TLabel')
        
        label.leftselected = True
        label.rightselected = False
        
        for other_label in self.labelList:
        
            other_label.rightselected = False
            
            if other_label is not label:
                other_label.leftselected = False
                other_label.configure(style='file.TLabel')
            
        # Create canvas image and store image dimensions
        self.canvasDisplay.delete(self.currentImage)
        self.canvasDisplay.delete(self.selectionBox)
        self.canvasDisplay.delete(self.measureLine)
        
        if self.showResized:
        
            # Show the resized version of the image
        
            # Create a resized image if none exist
            if label.photo_img_res is None:
                self.createResImage(label)
            
            w = label.photo_img_res.width()
            h = label.photo_img_res.height()
            cw = self.scrollbarCanvHor.winfo_width() - 17.0
            ch = self.scrollbarCanvVer.winfo_height()
            
            # Create new resized image if the window has changed enough
            if not (np.abs(cw - w) <= 0.01*(cw + w) or np.abs(ch - h) <= 0.01*(ch + h)):
                self.createResImage(label)
                
            self.imageSize = (w, h)
            
            self.currentImage = self.canvasDisplay.create_image(cw/2, ch/2,
                                                                image=label.photo_img_res,
                                                                anchor='center')
                                                                
            self.canvasDisplay.configure(scrollregion=(0, 0, 0, 0))
            
            # Display the FOV of the non-resized light frame
            if label is self.labelLight:
                self.setFOV(0, label.photo_img.width(), 0, label.photo_img.height(), False)
            else:
                self.varFOV.set('')
                                                                
        else:
        
            self.imageSize = (label.photo_img.width(), label.photo_img.height())
        
            self.currentImage = self.canvasDisplay.create_image(0, 0, image=label.photo_img,
                                                                anchor='nw')
        
            self.canvasDisplay.configure(scrollregion=(0, 0, self.imageSize[0], self.imageSize[1]))
            
            self.setFOV(0, self.imageSize[0], 0, self.imageSize[1], False)
        
        # Update ISO and exposure time labels
        
        if label.exposure is not None:
            self.varImInfo.set('Exposure time: %.4g s' % label.exposure)
        else:
            self.varImInfo.set('Exposure time: Not detected')
            
        if self.cont.isDSLR:
            if label.iso is not None:
                self.varImInfo.set('ISO: %d        %s' % (label.iso, self.varImInfo.get()))
            else:
                self.varImInfo.set('ISO: Not detected        %s' % (self.varImInfo.get()))
        
        # Disable image interaction for resized images, except for measuring in the light frame
        if label is self.labelLight:
            self.menuRC.entryconfig(4, state='normal')
        else:
            if self.mode == 'measure':
            
                self.useSelectMode()
                
                if self.showResized:
                    self.canvasDisplay.unbind('<Button-1>')
                    self.canvasDisplay.unbind('<B1-Motion>')
                    self.canvasDisplay.unbind('<ButtonRelease-1>')
                
            self.menuRC.entryconfig(4, state='disabled')
            
        self.menuActive = False
                
    def removeImageEvent(self, event):
    
        '''Mark rightclicked label with red, and remove marked labels if rightclicked again.'''
    
        if self.busy: return None
    
        if event.widget.rightselected:
            
            activateNew = False
            activelabel = None
            count = 0
            
            # Loop through all labels
            for label in self.labelList:
            
                if label.rightselected:
                
                    # Remove info for labels that have been right-clicked
                    
                    if label is self.labelBias1 or label is self.labelBias2:
                    
                        if self.displayed_bias == 1:
                        
                            self.forgetAttributes(self.labelBias1)
                            
                            self.labelBias1.pack_forget()
                            self.varBias1Label.set('')
                            self.frameBias.pack_forget()
                            self.labelBiasH.pack_forget()
                            
                            self.displayed_bias = 0
                            
                        elif self.displayed_bias == 2:
                        
                            # Shift info from label 2 to label 1 if label 2 is removed
                        
                            if label is self.labelBias1:
                                self.labelBias1.raw_img = self.labelBias2.raw_img[:, :]
                                self.labelBias1.stretched_img = self.labelBias2.stretched_img[:, :]
                                self.labelBias1.photo_img = self.labelBias2.photo_img
                                self.labelBias1.pil_img = self.labelBias2.pil_img
                                self.labelBias1.photo_img_res = self.labelBias2.photo_img_res
                                self.labelBias1.exposure = self.labelBias2.exposure
                                self.labelBias1.iso = self.labelBias2.iso
                                self.varBias1Label.set(self.varBias2Label.get())
                                if self.labelBias2.leftselected:
                                    self.showImage(self.labelBias1)
                            
                            self.forgetAttributes(self.labelBias2)
                            
                            self.labelBias2.pack_forget()
                            self.varBias2Label.set('')
                            self.varBiasHLabel.set('Bias frame')
                            
                            self.displayed_bias = 1
                        
                    elif label is self.labelDark1 or label is self.labelDark2:
                    
                        if self.displayed_dark == 1:
                        
                            self.forgetAttributes(self.labelDark1)
                            
                            self.labelDark1.pack_forget()
                            self.varDark1Label.set('')
                            self.frameDark.pack_forget()
                            self.labelDarkH.pack_forget()
                            
                            self.displayed_dark = 0
                            
                        elif self.displayed_dark == 2:
                        
                            if label is self.labelDark1:
                                self.labelDark1.raw_img = self.labelDark2.raw_img[:, :]
                                self.labelDark1.stretched_img = self.labelDark2.stretched_img[:, :]
                                self.labelDark1.photo_img = self.labelDark2.photo_img
                                self.labelDark1.pil_img = self.labelDark2.pil_img
                                self.labelDark1.photo_img_res = self.labelDark2.photo_img_res
                                self.labelDark1.exposure = self.labelDark2.exposure
                                self.labelDark1.iso = self.labelDark2.iso
                                self.varDark1Label.set(self.varDark2Label.get())
                                if self.labelDark2.leftselected:
                                    self.showImage(self.labelDark1)
                            
                            self.forgetAttributes(self.labelDark2)
                            
                            self.labelDark2.pack_forget()
                            self.varDark2Label.set('')
                            self.varDarkHLabel.set('Dark frame')
                            
                            self.displayed_dark = 1
                        
                    elif label is self.labelFlat1 or label is self.labelFlat2:
                    
                        if self.displayed_flat == 1:
                        
                            self.forgetAttributes(self.labelFlat1)
                            
                            self.labelFlat1.pack_forget()
                            self.varFlat1Label.set('')
                            self.frameFlat.pack_forget()
                            self.labelFlatH.pack_forget()
                            
                            self.displayed_flat = 0
                            
                        elif self.displayed_flat == 2:
                        
                            if label is self.labelFlat1:
                                self.labelFlat1.raw_img = self.labelFlat2.raw_img[:, :]
                                self.labelFlat1.stretched_img = self.labelFlat2.stretched_img[:, :]
                                self.labelFlat1.photo_img = self.labelFlat2.photo_img
                                self.labelFlat1.pil_img = self.labelFlat2.pil_img
                                self.labelFlat1.photo_img_res = self.labelFlat2.photo_img_res
                                self.labelFlat1.exposure = self.labelFlat2.exposure
                                self.labelFlat1.iso = self.labelFlat2.iso
                                self.varFlat1Label.set(self.varFlat2Label.get())
                                if self.labelFlat2.leftselected:
                                    self.showImage(self.labelFlat1)
                            
                            self.forgetAttributes(self.labelFlat2)
                            
                            self.labelFlat2.pack_forget()
                            self.varFlat2Label.set('')
                            self.varFlatHLabel.set('Flat frame')
                            
                            self.displayed_flat = 1
                        
                    elif label is self.labelLight:
                    
                        self.forgetAttributes(self.labelLight)
                        
                        self.labelLight.pack_forget()
                        self.varLightLabel.set('')
                        self.labelLightH.pack_forget()
                        self.displayed_light = 0
                        self.varFOV.set('')
                        
                    elif label is self.labelSaturated:
                    
                        self.forgetAttributes(self.labelSaturated)
                        
                        self.labelSaturated.pack_forget()
                        self.varSaturatedLabel.set('')
                        self.labelSaturatedH.pack_forget()
                        self.displayed_saturated = 0
        
                    label.configure(style='file.TLabel')
                    label.rightselected = False
                    
                    # Store left-clicked label if it exists
                    if label.leftselected:
                        activateNew = True
                        activelabel = label
        
                    count += 1
        
            # Move selection if the left-clicked label was removed
            if activateNew:
            
                if self.displayed_dark == 1 and (activelabel is self.labelDark1 \
                                                 or activelabel is self.labelDark2):
                    self.showImage(self.labelDark1)
                elif self.displayed_flat == 1 and (activelabel is self.labelFlat1 \
                                                   or activelabel is self.labelFlat2):
                    self.showImage(self.labelFlat1)
                elif self.displayed_bias >= 1:
                    self.showImage(self.labelBias1)
                elif self.displayed_dark >= 1:
                    self.showImage(self.labelDark1)
                elif self.displayed_flat >= 1:
                    self.showImage(self.labelFlat1)
                elif self.displayed_light == 1:
                    self.showImage(self.labelLight)
                elif self.displayed_saturated == 0:
                    self.useGreen = None
                    self.CFAPattern = None
                    self.currentImage = None
                    self.noInput = True
                    self.canvasDisplay.delete(self.currentImage)
                    self.canvasDisplay.pack_forget()
                    self.scrollbarCanvHor.pack_forget()
                    self.scrollbarCanvVer.pack_forget()
                    self.labelCanv.pack(expand=True)
                    self.varImInfo.set('')
                    self.varFOV.set('')
            else:
                self.getSelectedLabel().configure(style='leftselectedfile.TLabel')
        
            self.varMessageLabel.set('Frame removed.' if count == 1 else 'Frames removed.')
        
        # Change label background to red if it isn't already right-clicked
        else:
            if event.widget.leftselected:
                event.widget.configure(style='leftrightselectedfile.TLabel')
            else:
                event.widget.configure(style='rightselectedfile.TLabel')
            event.widget.rightselected = True
    
    def computeSensorData(self):
    
        '''Calculate sensor parameters from added files.'''
        
        # If not all required files have been added
        if not (self.displayed_bias == 2 and \
                self.displayed_flat == 2 and \
                self.displayed_saturated == 1):
            
            # Ask user to use light frame instead of saturated frame if added
            if self.displayed_light == 1:
            
                text='A frame containing saturated pixels is required\nto compute sensor data. ' \
                      + 'Does the added\nlight frame contain saturated pixels?'
                      
                if not self.showWarning('Note', text, 'Yes', 'No', lambda: None):
                    self.varMessageLabel.set('Cancelled. Please add a saturated ' \
                                             + 'frame to compute sensor data.')
                    self.menuActive = False
                    return False
                    
                # Use light frame as saturated frame
                saturated = self.labelLight.raw_img
                useLight = True
            
            # Show message if required files haven't been added
            else:
                self.varMessageLabel.set('Two bias frames, two flat frames and ' \
                             + 'one saturated (or light) frame is required to compute sensor data.')
                return None
        else:
        
            saturated = self.labelSaturated.raw_img
            useLight = False
            
        # Get raw image data
        bias1 = self.labelBias1.raw_img
        bias2 = self.labelBias2.raw_img
        flat1 = self.labelFlat1.raw_img
        flat2 = self.labelFlat2.raw_img
        
        # Define central crop area for flat frames
        h, w = flat1.shape
        a = int(0.25*h)
        b = int(0.75*h)
        c = int(0.25*w)
        d = int(0.75*w)
        
        # Crop flat frames
        flat1_crop = flat1[a:b, c:d]
        flat2_crop = flat2[a:b, c:d]
        
        self.white_level = np.max(saturated)
        
        self.black_level = 0.5*(np.median(bias1) + np.median(bias2))
        flat_level_ADU = 0.5*(np.median(flat1_crop) + np.median(flat2_crop))
        
        delta_bias = bias1 + 30000 - bias2
        delta_flat = flat1_crop + 30000 - flat2_crop
        
        read_noise_ADU = np.std(delta_bias)/np.sqrt(2)
        
        flat_noise_ADU = np.std(delta_flat)/np.sqrt(2)
        
        photon_noise_ADU_squared = flat_noise_ADU**2 - read_noise_ADU**2
        photon_level_ADU = flat_level_ADU - self.black_level
        
        self.gain = photon_level_ADU/photon_noise_ADU_squared
        
        self.rn = self.gain*read_noise_ADU
        
        self.sat_cap = self.gain*self.white_level
        
        self.varMessageLabel.set('Sensor data computed.')
        
        isovals = []
        
        for label in [self.labelBias1, self.labelBias2, self.labelFlat1, self.labelFlat2,
                      self.labelLight if useLight else self.labelSaturated]:
                      
            if label.iso is not None:
                isovals.append(label.iso)
                
        if len(isovals) > 0 and isovals[1:] == isovals[:-1]:
            con_iso = isovals[0]
        else:
            con_iso = False
        
        self.disableWidgets()
        self.busy = True
        
        # Setup window displaying calculated values, with option to save data
        self.topResults = tk.Toplevel()
        self.topResults.title('Computed sensor data')
        self.cont.addIcon(self.topResults)
        setupWindow(self.topResults, 300, 220)
        self.topResults.focus_force()
        
        ttk.Label(self.topResults, text='Computed sensor data', font=self.cont.smallbold_font,
                  anchor='center').pack(side='top', pady=(15*scsy, 5*scsy), expand=True)
        
        frameResults = ttk.Frame(self.topResults)
        frameResults.pack(side='top', expand=True)
        
        ttk.Label(frameResults, text='Gain: ').grid(row=0, column=0, sticky='W')
        ttk.Label(frameResults, text=('%.3g' % (self.gain)), width=7,
                  anchor='center').grid(row=0, column=1)
        ttk.Label(frameResults, text=' e-/ADU').grid(row=0, column=2, sticky='W')
        
        ttk.Label(frameResults, text='Read noise: ').grid(row=1, column=0, sticky='W')
        ttk.Label(frameResults, text=('%.3g' % (self.rn)), width=7,
                  anchor='center').grid(row=1, column=1)
        ttk.Label(frameResults, text=' e-').grid(row=1, column=2, sticky='W')
        
        ttk.Label(frameResults, text='Black level: ').grid(row=2, column=0, sticky='W')
        ttk.Label(frameResults, text=('%d' % round(self.black_level)), width=7,
                  anchor='center').grid(row=2, column=1)
        ttk.Label(frameResults, text=' ADU').grid(row=2, column=2, sticky='W')
        
        ttk.Label(frameResults, text='White level: ').grid(row=3, column=0, sticky='W')
        ttk.Label(frameResults, text=('%d' % round(self.white_level)), width=7,
                  anchor='center').grid(row=3, column=1)
        ttk.Label(frameResults, text=' ADU').grid(row=3, column=2, sticky='W')
        
        ttk.Label(frameResults, text='Saturation capacity: ').grid(row=4, column=0, sticky='W')
        ttk.Label(frameResults, text=('%d' % round(self.sat_cap)), width=7,
                  anchor='center').grid(row=4, column=1)
        ttk.Label(frameResults, text=' e-').grid(row=4, column=2, sticky='W')
        
        ttk.Button(self.topResults, text='Save sensor data',
                   command=lambda: self.saveSensorResults(con_iso))\
                  .pack(side='top', pady=((5*scsy, 20*scsy)), expand=True)
        
        self.wait_window(self.topResults)
        
        # Close overlying windows if a lower window is exited
        try:
            self.topCamInfo.destroy()
        except:
            pass
            
        self.busy = False
        self.enableWidgets()
        
    def updateFrameButtonText(self, type):
    
        '''Change text of "add frames" button when optionmenu selection changes.'''
    
        if type == 'Bias':
            self.varAddButtonLabel.set('Add bias frames')
        elif type == 'Dark':
            self.varAddButtonLabel.set('Add dark frames')
        elif type == 'Flat':
            self.varAddButtonLabel.set('Add flat frames')
        elif type == 'Light':
            self.varAddButtonLabel.set('Add light frame')
        elif type == 'Saturated':
            self.varAddButtonLabel.set('Add saturated frame')
        
    def saveSensorResults(self, con_iso):
    
        '''Get required camera info from user before saving calculated sensor values.'''
        
        varISO = tk.IntVar()
        varMessageLabel = tk.StringVar()
        
        varISO.set('')
        
        def executeSensorResultSave():
            
            '''Save calculated sensor values to "cameradata.txt".'''
                    
            if self.cont.isDSLR:
            
                if con_iso:
                    iso = str(con_iso)
                else:
                    # Get inputted ISO value for DSLR
                    try:
                        iso = str(int(varISO.get()))
                    except ValueError:
                        varMessageLabel.set('Invalid ISO input. Must be an integer.')
                        return None
            
            # Read camera data file            
            file = open('cameradata.txt', 'r')
            lines = file.read().split('\n')
            file.close()
                
            file = open('cameradata.txt', 'w')
                
            file.write(lines[0])
                
            for line in lines[1:-1]:
                
                line = line.split(',')
                    
                # Find relevant line in the camera data file
                if line[0] == CNAME[self.cont.cnum]:
                
                    # If no data exists for the camera
                    if self.cont.noData:
                    
                        g_idx1 = rn_idx1 = 0
                        g_idx2 = rn_idx2 = 1
                    
                        # Add the data
                        file.write('\n%s,%s,%.3g*,%.3g*,%d*,%d*,%d*,%s,%s*' % (line[0], line[1],
                                                                               self.gain, self.rn,
                                                                               round(self.sat_cap),
                                                                            round(self.black_level),
                                                                            round(self.white_level),
                                                                            'NA', line[8]))
                        if self.cont.isDSLR: file.write(',' + iso)
                        
                        self.cont.noData = False
                    
                    # If data already exists
                    else:
                    
                        # Read existing values
                        gainvals = line[2].split('-')
                        gv_stripped = [val.split('*')[0] for val in gainvals]
                        rnvals = line[3].split('-')
                        rv_stripped = [val.split('*')[0] for val in rnvals]
                        satcapvals = line[4].split('-')
                        blvals = line[5].split('-')
                        wlvals = line[6].split('-')
                        
                        # Find where to add new values, or which old values to overwrite
                        
                        if self.cont.isDSLR:
                            
                            isovals = line[9].split('-')
                          
                            if iso in isovals:
                                
                                g_idx1 = rn_idx1 = isovals.index(iso)
                                g_idx2 = rn_idx2 = g_idx1 + 1
                                    
                            else:
                                
                                g_idx1 = g_idx2 = rn_idx1 = rn_idx2 = sorted(isovals + [iso],
                                                                             key=int).index(iso)
                                    
                        else:
                            
                            if ('%.2g' % (self.rn)) in rv_stripped:
                                
                                rn_idx1 = rv_stripped.index('%.2g' % (self.rn))
                                rn_idx2 = rn_idx1 + 1
                            else:
                                
                                rn_idx1 = rn_idx2 = sorted(rv_stripped + ['%.3g' % (self.rn)],
                                                           key=float).index(('%.3g' % (self.rn)))
                            
                            if ('%.2g' % (self.gain)) in gv_stripped:
                               
                                g_idx1 = gv_stripped.index('%.2g' % (self.gain))
                                g_idx2 = g_idx1 + 1
                                
                            else:
                                
                                g_idx1 = g_idx2 = sorted(gv_stripped + ['%.3g' % (self.gain)],
                                                         key=float).index(('%.3g' % (self.gain)))
                            
                        # Add calculated values to camera data file
                        file.write('\n%s,%s,%s,%s,%s,%s,%s,%s,%s' \
                    % (line[0], line[1],
                       '-'.join(gainvals[:g_idx1] + ['%.3g*' % (self.gain)] + gainvals[g_idx2:]),
                       '-'.join(rnvals[:rn_idx1] + ['%.3g*' % (self.rn)] + rnvals[rn_idx2:]),
                       '-'.join(satcapvals[:g_idx1] + ['%d*' % round(self.sat_cap)] + satcapvals[g_idx2:]),
                       '-'.join(blvals[:g_idx1] + ['%d*' % round(self.black_level)] + blvals[g_idx2:]),
                       '-'.join(wlvals[:g_idx1] + ['%d*' % round(self.white_level)] + wlvals[g_idx2:]),
                       line[7], line[8]))
                                          
                        if self.cont.isDSLR: file.write(',%s' % ('-'.join(isovals[:g_idx1] + [iso] \
                                                                          + isovals[g_idx2:])))
                
                # Write the other lines with no changes
                else:
                    
                    file.write('\n' + ','.join(line))
                    
            file.write('\n' + lines[-1])
            file.close()
                
            # Insert calculated values to camera info lists
            
            idx = self.cont.cnum
            
            if g_idx2 == g_idx1 + 1:
                GAIN[idx][0][g_idx1] = float('%.3g' % (self.gain))
                GAIN[idx][1][g_idx1] = 1
                SAT_CAP[idx][0][g_idx1] = int(round(self.sat_cap))
                SAT_CAP[idx][1][g_idx1] = 1
                BLACK_LEVEL[idx][0][g_idx1] = int(round(self.black_level))
                BLACK_LEVEL[idx][1][g_idx1] = 1
                WHITE_LEVEL[idx][0][g_idx1] = int(round(self.white_level))
                WHITE_LEVEL[idx][1][g_idx1] = 1
                if self.cont.isDSLR: ISO[idx][g_idx1] = int(iso)
            else:
                GAIN[idx][0] = np.insert(GAIN[idx][0], g_idx1, float('%.3g' % (self.gain)))
                GAIN[idx][1] = np.insert(GAIN[idx][1], g_idx1, 1)
                SAT_CAP[idx][0] = np.insert(SAT_CAP[idx][0], g_idx1, int(round(self.sat_cap)))
                SAT_CAP[idx][1] = np.insert(SAT_CAP[idx][1], g_idx1, 1)
                BLACK_LEVEL[idx][0] = np.insert(BLACK_LEVEL[idx][0], g_idx1, int(round(self.black_level)))
                BLACK_LEVEL[idx][1] = np.insert(BLACK_LEVEL[idx][1], g_idx1, 1)
                WHITE_LEVEL[idx][0] = np.insert(WHITE_LEVEL[idx][0], g_idx1, int(round(self.white_level)))
                WHITE_LEVEL[idx][1] = np.insert(WHITE_LEVEL[idx][1], g_idx1, 1)
                if self.cont.isDSLR: ISO[idx] = np.insert(ISO[idx], g_idx1, int(iso))
                    
            if rn_idx2 == rn_idx1 + 1:
                RN[idx][0][rn_idx1] = float('%.3g' % (self.rn))
                RN[idx][1][rn_idx1] = 1
            else:
                RN[idx][0] = np.insert(RN[idx][0], rn_idx1, float('%.3g' % (self.rn)))
                RN[idx][1] = np.insert(RN[idx][1], rn_idx1, 1)
            
            for frame in [self.cont.frames[ImageCalculator], self.cont.frames[ImageSimulator],
                          self.cont.frames[PlottingTool]]:
            
                frame.reconfigureNonstaticWidgets()
                frame.setDefaultValues()
                
            self.varMessageLabel.set('Sensor information added for %s.' % CNAME[idx])
            try:
                self.topCamInfo.destroy()
            except:
                pass
            try:
                self.topResults.destroy()
            except:
                pass
        
        # Create the window asking for required camera information
        if self.cont.isDSLR and not con_iso:
        
            self.topCamInfo = tk.Toplevel()
            self.topCamInfo.title('Save sensor data')
            self.cont.addIcon(self.topCamInfo)
            setupWindow(self.topCamInfo, 300, 140)
            self.topCamInfo.focus_force()
            
            ttk.Label(self.topCamInfo, text='Input the ISO used for the images:')\
                     .pack(side='top', pady=(15*scsy, 5*scsy), expand=True)
            
            ttk.Entry(self.topCamInfo, textvariable=varISO, font=self.cont.small_font,
                      background=DEFAULT_BG, width=8).pack(side='top', pady=(7*scsy, 7*scsy),
                                                           expand=True)
        
            ttk.Button(self.topCamInfo, text='OK',
                       command=executeSensorResultSave).pack(side='top',
                                                                     pady=(0, 6*scsy), expand=True)
            ttk.Label(self.topCamInfo, textvariable=varMessageLabel, font=self.cont.small_font,
                          background=DEFAULT_BG).pack(side='top', pady=(0, 10*scsy), expand=True)
                          
        else:
        
            executeSensorResultSave()
    
    def createSelectionBoxEvent(self, event):
    
        '''Create rectangle in canvas when left-clicked.'''
    
        if self.menuActive: return None
    
        # Delete existing selection box
        event.widget.delete(self.selectionBox)
        event.widget.delete(self.measureLine)
            
        # Define list to store selction box corner coordinates
        self.selectionArea = [int(event.widget.canvasx(event.x)),
                              int(event.widget.canvasy(event.y)), 0, 0]
        
        # Create new selection box at clicked location        
        self.selectionBox = event.widget.create_rectangle(self.selectionArea[0],
                                                          self.selectionArea[1],
                                                          self.selectionArea[0]+1,
                                                          self.selectionArea[1]+1,
                                                          outline='red')
    
    def drawSelectionBoxEvent(self, event):
    
        '''Redraw selection box to follow mouse movement when held down.'''
    
        if self.menuActive: return None
        
        x = event.widget.canvasx(event.x)
        y = event.widget.canvasy(event.y)
        
        event.widget.coords(self.selectionBox, self.selectionArea[0], self.selectionArea[1], x, y)
        
        self.setFOV(self.selectionArea[0], x, self.selectionArea[1], y, True)
    
    def evaluateSelectionBoxEvent(self, event):
    
        '''Modify selection box when mouse is released.'''
    
        if self.menuActive:
            self.menuActive = False
            return None
    
        # Coordinates where mouse was released
        corner2_x = int(event.widget.canvasx(event.x))
        corner2_y = int(event.widget.canvasy(event.y))
        
        # Exchange index of coordinates to keep smallest values in the beginning of the list
        if self.selectionArea[0] > corner2_x:
            temp = corner2_x
            corner2_x = self.selectionArea[0]
            self.selectionArea[0] = temp
            
        if self.selectionArea[1] > corner2_y:
            temp = corner2_y
            corner2_y = self.selectionArea[1]
            self.selectionArea[1] = temp
            
        self.selectionArea[2] = corner2_x
        self.selectionArea[3] = corner2_y
        
        # Change out of bounds coordinates
        if self.selectionArea[0] < 0: self.selectionArea[0] = 0
        if self.selectionArea[1] < 0: self.selectionArea[1] = 0
        if self.selectionArea[2] > self.imageSize[0]: self.selectionArea[2] = self.imageSize[0]
        if self.selectionArea[3] > self.imageSize[1]: self.selectionArea[3] = self.imageSize[1]
        
        # Redraw selection bow with new coordinates
        event.widget.coords(self.selectionBox, self.selectionArea[0], self.selectionArea[1],
                            self.selectionArea[2], self.selectionArea[3])
        
        # Remove selection box if the selected area is too small
        if self.selectionArea[2] - self.selectionArea[0] <= 1 \
           or self.selectionArea[3] - self.selectionArea[1] <= 1:
            event.widget.delete(self.selectionBox)
            self.localSelection = False
            self.setFOV(0, self.imageSize[0], 0, self.imageSize[1], False)
        else:
            self.localSelection = True
            self.setFOV(self.selectionArea[0], self.selectionArea[2],
                        self.selectionArea[1], self.selectionArea[3], True)
    
    def setFOV(self, x1, x2, y1, y2, isSelection):
    
        '''Calculate the field of view of the image or selection box.'''
    
        # Display nothing if the frame is not a light frame
        if self.getSelectedLabel() is not self.labelLight:
            self.varFOV.set('')
            return None
        
        dx = self.cont.ISVal*np.abs(x1 - x2)
        dy = self.cont.ISVal*np.abs(y1 - y2)
           
        # Compensate for that every other pixel is removed in a CFA splitted image
        if self.labelLight.isSplitted:
            dx *= 2.0
            dy *= 2.0
            
        deg_x = dx/3600.0
        deg_y = dy/3600.0
        
        type = ('Selection' if isSelection else 'Image')
        
        # Set the FOV in the active angle unit
        if self.cont.dmsAngleUnit.get():
        
            deg_xi = int(deg_x)
            deg_yi = int(deg_y)
                
            min_x = (deg_x - deg_xi)*60
            min_y = (deg_y - deg_yi)*60
            min_xi = int(min_x)
            min_yi = int(min_y)
                
            sec_x = (min_x - min_xi)*60
            sec_y = (min_y - min_yi)*60
               
            self.varFOV.set(u'%s FOV: %d\u00B0 %d\' %.1f\'\' x %d\u00B0 %d\' %.1f\'\'' \
                            % (type, deg_xi, min_xi, sec_x, deg_yi, min_yi, sec_y))
            
        else:
        
            self.varFOV.set(u'%s FOV: %.3g\u00B0 x %.3g\u00B0' % (type, deg_x, deg_y))
    
    def setAngle(self, x1, x2, y1, y2):
    
        '''Calculate the angle of the measuring line.'''
    
        # Display nothing if the frame is not a light frame
        if self.getSelectedLabel() is not self.labelLight:
            self.varFOV.set('')
            return None
            
        dx = self.cont.ISVal*np.abs(x1 - x2)
        dy = self.cont.ISVal*np.abs(y1 - y2)
            
        # Compensate for that every other pixel is removed in a CFA splitted image
        if self.labelLight.isSplitted:
            dx *= 2.0
            dy *= 2.0
            
        # Compensate for any resizing
        if self.showResized:
            dx *= float(self.labelLight.photo_img.width())/self.imageSize[0]
            dy *= float(self.labelLight.photo_img.height())/self.imageSize[1]
            
        deg_r = np.sqrt(dx**2 + dy**2)/3600.0
        
        # Set the angle in the active angle unit
        if self.cont.dmsAngleUnit.get():
        
            deg_ri = int(deg_r)
                
            min_r = (deg_r - deg_ri)*60
            min_ri = int(min_r)
                
            sec_r = (min_r - min_ri)*60
               
            self.varFOV.set(u'Angle: %d\u00B0 %d\' %.1f\'\'' % (deg_ri, min_ri, sec_r))
                            
        else:
        
            self.varFOV.set(u'Angle: %.3g\u00B0' % deg_r)
    
    def showRCMenuEvent(self, event):
    
        '''Show menu at pointer location when canvas is right-clicked.'''
        
        self.menuRC.post(event.x_root, event.y_root)
        self.menuActive = True
    
    def getStatistics(self):
    
        '''Show topwindow with statistics of selected area or entire image.'''
        
        # Get raw image data
        img = self.getSelectedLabel().raw_img
        
        # Crop image if a selection box has been drawn
        if self.localSelection:
            img_crop = img[self.selectionArea[1]:self.selectionArea[3],
                           self.selectionArea[0]:self.selectionArea[2]]
        else:
            img_crop = img
        
        # Calculate values in (cropped) image
        sample_val = img_crop.shape[0]*img_crop.shape[1]
        mean_val = np.mean(img_crop)
        median_val = np.median(img_crop)
        std_val = np.std(img_crop)
        max_val = np.max(img_crop)
        min_val = np.min(img_crop)
        
        self.disableWidgets()
        self.busy = True
        
        # Setup window displaying the calculated information
        topStatistics = tk.Toplevel()
        topStatistics.title('Statistics')
        self.cont.addIcon(topStatistics)
        setupWindow(topStatistics, 300, 230)
        topStatistics.focus_force()
        
        self.menuRC.entryconfigure(8, state='disabled')
        
        ttk.Label(topStatistics, text='Statistics of selected image region' \
                                      if self.localSelection else 'Statistics of the entire image',
                  font=self.cont.smallbold_font,
                  anchor='center').pack(side='top', pady=(20*scsy, 10*scsy), expand=True)
        
        frameStatistics = ttk.Frame(topStatistics)
        frameStatistics.pack(side='top', pady=(0, 6*scsy), expand=True)
        
        ttk.Label(frameStatistics, text='Sample size: ').grid(row=0, column=0, sticky='W')
        ttk.Label(frameStatistics, text=('%s' % sample_val), width=7,
                  anchor='center').grid(row=0, column=1)
        ttk.Label(frameStatistics, text=' pixels').grid(row=0, column=2, sticky='W')
        
        ttk.Label(frameStatistics, text='Mean value: ').grid(row=1, column=0, sticky='W')
        ttk.Label(frameStatistics, text=('%.1f' % mean_val), width=7,
                  anchor='center').grid(row=1, column=1)
        ttk.Label(frameStatistics, text=' ADU').grid(row=1, column=2, sticky='W')
        
        ttk.Label(frameStatistics, text='Median value: ').grid(row=2, column=0, sticky='W')
        ttk.Label(frameStatistics, text=('%g' % median_val), width=7,
                  anchor='center').grid(row=2, column=1)
        ttk.Label(frameStatistics, text=' ADU').grid(row=2, column=2, sticky='W')
        
        ttk.Label(frameStatistics, text='Standard deviation: ').grid(row=3, column=0, sticky='W')
        ttk.Label(frameStatistics, text=('%.2f' % std_val), width=7,
                  anchor='center').grid(row=3, column=1)
        ttk.Label(frameStatistics, text=' ADU').grid(row=3, column=2, sticky='W')
        
        ttk.Label(frameStatistics, text='Maximum value: ').grid(row=4, column=0, sticky='W')
        ttk.Label(frameStatistics, text=('%d' % max_val), width=7,
                  anchor='center').grid(row=4, column=1)
        ttk.Label(frameStatistics, text=' ADU').grid(row=4, column=2, sticky='W')
        
        ttk.Label(frameStatistics, text='Minimum value: ').grid(row=5, column=0, sticky='W')
        ttk.Label(frameStatistics, text=('%d' % min_val), width=7,
                  anchor='center').grid(row=5, column=1)
        ttk.Label(frameStatistics, text=' ADU').grid(row=5, column=2, sticky='W')
        
        ttk.Button(topStatistics, text='Close', command=lambda: topStatistics.destroy())\
                  .pack(side='top', pady=(0, 15*scsy), expand=True)
        
        self.wait_window(topStatistics)
        
        try:
            self.menuRC.entryconfigure(8, state='normal')
        except:
            pass
        
        self.enableWidgets()
        self.busy = False
        
        self.menuActive = False
        
    def transferData(self):
    
        '''Get statistics of added dark or light frames and transfer values to Image Calculator.'''
    
        label = self.getSelectedLabel() # Label of selected frame
        
        # Show error if no compatible frames are added
        if not label in [self.labelDark1, self.labelDark2, self.labelLight]:
        
            self.varMessageLabel.set('Only available for dark and light frames.')
            self.menuActive = False
            return None
            
        # If the selected frame is a light frame
        if label is self.labelLight:
        
            # Show error if no selection box has been drawn
            if not self.localSelection:
            
                self.varMessageLabel.set('Please select a background or target region '\
                                         + 'of the image before transfering data.')
                self.menuActive = False
                return None
                
            # Get selected image region from user
            
            self.disableWidgets()
            self.menuRC.entryconfigure(9, state='disabled')
            self.busy = True
            
            def ok_light():
            
                self.cancelled = False
                topAskRegion.destroy()
                
            topAskRegion = tk.Toplevel()
            topAskRegion.title('Choose selected region')
            self.cont.addIcon(topAskRegion)
            setupWindow(topAskRegion, 300, 145)
            topAskRegion.focus_force()
            
            self.cancelled = True
            varBGRegion = tk.IntVar()
            varBGRegion.set(1)
            
            tk.Label(topAskRegion,
                      text='Choose which region of the image\nyou have selected.',
                      font=self.cont.small_font).pack(side='top', pady=(10*scsy, 5*scsy),
                                                      expand=True)
            
            frameRadio = ttk.Frame(topAskRegion)
            frameRadio.pack(side='top', expand=True, pady=(0, 10*scsy))
            ttk.Radiobutton(frameRadio, text='Background', variable=varBGRegion,
                            value=1).grid(row=0, column=0)
            ttk.Radiobutton(frameRadio, text='Target', variable=varBGRegion,
                            value=0).grid(row=0, column=1)
            
            ttk.Button(topAskRegion, text='OK', command=ok_light).pack(side='top', expand=True,
                                                                       pady=(0, 10*scsy))
            
            self.wait_window(topAskRegion)
            
            self.enableWidgets()
            self.menuRC.entryconfigure(9, state='normal')
            self.busy = False
            
            # Cancel if topwindow was exited
            if self.cancelled:
                self.varMessageLabel.set('Cancelled.')
                self.menuActive = False
                return None
            
            calframe = self.cont.frames[ImageCalculator]
              
            # Get raw data of selected area
            img_crop = label.raw_img[self.selectionArea[1]:self.selectionArea[3],
                                     self.selectionArea[0]:self.selectionArea[2]]
            
            # Calculate required values and transfer to corresponding widgets
            if varBGRegion.get():
                
                if self.cont.isDSLR:
                
                    bg_noise = np.std(img_crop)
                    calframe.varBGN.set('%.3g' % bg_noise)
                    
                bg_level = np.median(img_crop)
                calframe.varBGL.set('%g' % bg_level)
                    
            else:
            
                target_level = np.median(img_crop)
                calframe.varTarget.set('%g' % target_level)
                
            isostr = ''
            expstr = ''
                
            if self.labelLight.iso is not None and self.labelLight.iso in list(ISO[self.cont.cnum]):
                calframe.varISO.set(self.labelLight.iso)
                calframe.updateISO(self.labelLight.iso)
                isostr = ' ISO set to %d.' % (self.labelLight.iso)
                
            if self.labelLight.exposure is not None:
                calframe.varExp.set('%.4g' % (self.labelLight.exposure))
                expstr = ' Exposure time set to %.4g s.' % (self.labelLight.exposure)
                
            self.varMessageLabel.set(('Background data transfered to Image Calculator.' \
                                      if varBGRegion.get() \
                                      else 'Target data transfered to Image Calculator.') + isostr \
                                                                                        + expstr)
        
        # If the selected frame is a dark frame
        else:
        
            # If the camera is a DSLR
            if self.cont.isDSLR:
            
                # If only one dark frame is added
                if self.displayed_dark == 1:
                
                    # Ask if user will still proceed
                
                    self.disableWidgets()
                    self.menuRC.entryconfigure(9, state='disabled')
                    self.busy = True
            
                    topWarning = tk.Toplevel()
                    topWarning.title('Warning')
                    self.cont.addIcon(topWarning)
                    setupWindow(topWarning, 300, 180)
                    topWarning.focus_force()
                    
                    def ok_dark():
                        self.cancelled = False
                        topWarning.destroy()
                    
                    self.cancelled = True
                    
                    tk.Label(topWarning, text='Using two dark frames is recommended\nto get more ' \
                                            + 'accurate noise measurements.\nProceed with only one?',
                            font=self.cont.small_font).pack(side='top', pady=(20*scsy, 5*scsy),
                                                            expand=True)
                          
                    frameButtons = ttk.Frame(topWarning)
                    frameButtons.pack(side='top', expand=True, pady=(0, 10*scsy))
                    ttk.Button(frameButtons, text='Yes', command=ok_dark).grid(row=0, column=0)
                    ttk.Button(frameButtons, text='Cancel',
                               command=lambda: topWarning.destroy()).grid(row=0, column=1)
                    
                    self.wait_window(topWarning)
                    
                    self.enableWidgets()
                    self.menuRC.entryconfigure(9, state='normal')
                    self.busy = False

                    # Cancel if topwindow is exited
                    if self.cancelled:
                        self.varMessageLabel.set('Cancelled.')
                        self.menuActive = False
                        return None
                    
                    # Get raw image data
                    img = label.raw_img
                    
                    # Crop image if a selection box has been drawn
                    if self.localSelection:
                        img_crop = img[self.selectionArea[1]:self.selectionArea[3],
                                       self.selectionArea[0]:self.selectionArea[2]]
                    else:
                        img_crop = img
                    
                    # Calculate dark frame noise
                    dark_val = np.std(img_crop)
                
                # If two dark frames have been added
                else:
                
                    # Get raw data of images
                    img1 = self.labelDark1.raw_img
                    img2 = self.labelDark2.raw_img
                    
                    # Crop images if a selection box has been drawn
                    if self.localSelection:
                        img1_crop = img1[self.selectionArea[1]:self.selectionArea[3],
                                         self.selectionArea[0]:self.selectionArea[2]]
                        img2_crop = img2[self.selectionArea[1]:self.selectionArea[3],
                                         self.selectionArea[0]:self.selectionArea[2]]
                    else:
                        img1_crop = img1
                        img2_crop = img2
                    
                    # Calculate dark frame noise
                    delta_dark = img1_crop + 30000 - img2_crop
                    dark_val = np.std(delta_dark)/np.sqrt(2)
            
            # If the camera is a CCD            
            else:
                
                if self.displayed_dark == 1:
            
                    # Get raw image data
                    img = label.raw_img
                    
                    # Crop image if a selection box has been drawn
                    if self.localSelection:
                        img_crop = img[self.selectionArea[1]:self.selectionArea[3],
                                       self.selectionArea[0]:self.selectionArea[2]]
                    else:
                        img_crop = img
                        
                    # Calculate dark frame level
                    dark_val = np.median(img_crop)
                    
                else:
                
                    # Get raw data of images
                    img1 = self.labelDark1.raw_img
                    img2 = self.labelDark2.raw_img
                    
                    # Crop images if a selection box has been drawn
                    if self.localSelection:
                        img1_crop = img1[self.selectionArea[1]:self.selectionArea[3],
                                         self.selectionArea[0]:self.selectionArea[2]]
                        img2_crop = img2[self.selectionArea[1]:self.selectionArea[3],
                                         self.selectionArea[0]:self.selectionArea[2]]
                    else:
                        img1_crop = img1
                        img2_crop = img2
                    
                    # Calculate dark frame noise
                    dark_val = 0.5*(np.median(img1_crop) + np.median(img2_crop))
                
            # Transfer data to dark input widget and set checkbutton state
            calframe = self.cont.frames[ImageCalculator]
            calframe.varUseDark.set(1)
            calframe.toggleDarkInputMode()
            calframe.varDark.set(('%.3g' % dark_val) if self.cont.isDSLR else ('%g' % dark_val))
            
            isostr = ''
            expstr = ''
            
            isovals = []
            expvals = []
            
            for lab in [self.labelDark1, self.labelDark2]:
            
                if lab.iso is not None:
                    isovals.append(lab.iso)
                    
                if lab.exposure is not None:
                    expvals.append(lab.exposure)
                    
            if len(isovals) > 0 and isovals[1:] == isovals[:-1] \
                                and isovals[0] in list(ISO[self.cont.cnum]):
            
                calframe.varISO.set(isovals[0])
                calframe.updateISO(isovals[0])
                isostr = ' ISO set to %d.' % isovals[0]
                    
            if len(expvals) == 1 or (len(expvals) == 2 and not self.tooDiff(*expvals)):
            
                calframe.varExp.set(expvals[0])
                expstr = ' Exposure time set to %.4g s.' \
                         % (label.exposure if label.exposure is not None else expvals[0])
                    
            self.varMessageLabel.set('Dark data transfered to Image Calculator.' + isostr + expstr)
                    
        self.menuActive = False
    
    def getSelectedLabel(self):
    
        '''Return the currently selected file label.'''
    
        selectedLabel = None
    
        for label in self.labelList:
            if label.leftselected:
                selectedLabel = label
                break
                
        return selectedLabel

    def startDragEvent(self, event):
    
        '''Store coordinates of clicked location.'''
    
        event.widget.origin_x = event.x
        event.widget.origin_y = event.y
        
    def dragEvent(self, event):
    
        '''
        Scroll canvas by an amount equal to the difference between the previous location
        and the new location, and reset coordinates.
        '''
    
        event.widget.xview_scroll(event.widget.origin_x - event.x, 'unit')
        event.widget.yview_scroll(event.widget.origin_y - event.y, 'unit')
            
        event.widget.origin_x = event.x
        event.widget.origin_y = event.y
    
    def createMeasureEvent(self, event):
    
        '''Create line in canvas when right-clicked.'''
        
        if self.menuActive: return None
        
        event.widget.delete(self.selectionBox)
        event.widget.delete(self.measureLine)
        self.localSelection = False
        
        self.measurePoints = [int(event.widget.canvasx(event.x)),
                              int(event.widget.canvasy(event.y)), 0, 0]
                            
        self.measureLine = event.widget.create_line(self.measurePoints[0],
                                                    self.measurePoints[1],
                                                    self.measurePoints[0],
                                                    self.measurePoints[1],
                                                    fill='red')
    
    def drawMeasureLineEvent(self, event):
    
        '''Redraw line when mouse is dragged.'''
        
        if self.menuActive: return None
        
        x = event.widget.canvasx(event.x)
        y = event.widget.canvasy(event.y)
        
        event.widget.coords(self.measureLine, self.measurePoints[0], self.measurePoints[1], x, y)
        
        self.setAngle(self.measurePoints[0], x, self.measurePoints[1], y)
    
    def evaluateMeasureEvent(self, event):
        
        '''Store line endpoints when the mouse is released.'''
        
        if self.menuActive:
            self.menuActive = False
            return None
            
        corner2_x = int(event.widget.canvasx(event.x))
        corner2_y = int(event.widget.canvasy(event.y))
        
        self.measurePoints[2] = corner2_x
        self.measurePoints[3] = corner2_y
        
        event.widget.coords(self.measureLine, self.measurePoints[0], self.measurePoints[1],
                            self.measurePoints[2], self.measurePoints[3])
        
        # Delete the line if it is too short
        if np.abs(self.measurePoints[2] - self.measurePoints[0]) <= 1 \
           and np.abs(self.measurePoints[3] - self.measurePoints[1]) <= 1:
            event.widget.delete(self.measureLine)
            self.setFOV(0, self.labelLight.photo_img.width(),
                        0, self.labelLight.photo_img.height(), False)
        else:
            self.setAngle(self.measurePoints[0], self.measurePoints[2],
                          self.measurePoints[1], self.measurePoints[3])
    
    def updateAngle(self):
    
        '''Update the FOV/angle label according to the existing drawing.'''
    
        if self.getSelectedLabel() is self.labelLight:
        
            if self.mode == 'measure':
            
                if np.abs(self.measurePoints[2] - self.measurePoints[0]) <= 1 \
                   and np.abs(self.measurePoints[3] - self.measurePoints[1]) <= 1:
                    self.setFOV(0, self.labelLight.photo_img.width(),
                                0, self.labelLight.photo_img.height(), False)
                else:
                    self.setAngle(self.measurePoints[0], self.measurePoints[2],
                                  self.measurePoints[1], self.measurePoints[3])
                
            else:
        
                if self.localSelection:
                    self.setFOV(self.selectionArea[0], self.selectionArea[2],
                                self.selectionArea[1], self.selectionArea[3], True)
                else:
                    self.setFOV(0, self.labelLight.photo_img.width(),
                                0, self.labelLight.photo_img.height(), False)
    
    def useSelectMode(self):
    
        '''Enable selection box drawing on canvas.'''
    
        self.mode = 'select'
    
        self.canvasDisplay.unbind('<Button-1>')
        self.canvasDisplay.unbind('<B1-Motion>')
        self.canvasDisplay.unbind('<ButtonRelease-1>')
        
        self.canvasDisplay.bind('<Button-1>', self.createSelectionBoxEvent)
        self.canvasDisplay.bind('<B1-Motion>', self.drawSelectionBoxEvent)
        self.canvasDisplay.bind('<ButtonRelease-1>', self.evaluateSelectionBoxEvent)
        
        self.canvasDisplay.config(cursor='arrow')
        
        self.menuActive = False
        
    def useDragMode(self):
    
        '''Enable dragging on canvas.'''
    
        self.mode = 'drag'
    
        self.canvasDisplay.unbind('<Button-1>')
        self.canvasDisplay.unbind('<B1-Motion>')
        self.canvasDisplay.unbind('<ButtonRelease-1>')
        
        self.canvasDisplay.bind('<Button-1>', self.startDragEvent)
        self.canvasDisplay.bind('<B1-Motion>', self.dragEvent)
        
        self.canvasDisplay.config(cursor='hand2')
        
        self.menuActive = False
    
    def useMeasureMode(self):
    
        '''Enable drawing a measuring line in the canvas.'''
    
        self.mode = 'measure'
    
        self.canvasDisplay.unbind('<Button-1>')
        self.canvasDisplay.unbind('<B1-Motion>')
        self.canvasDisplay.unbind('<ButtonRelease-1>')
        
        self.canvasDisplay.bind('<Button-1>', self.createMeasureEvent)
        self.canvasDisplay.bind('<B1-Motion>', self.drawMeasureLineEvent)
        self.canvasDisplay.bind('<ButtonRelease-1>', self.evaluateMeasureEvent)
        
        self.canvasDisplay.config(cursor='crosshair')
        
        self.menuActive = False
    
    def showWarning(self, title, body, button1, button2, cmd):
    
        '''Show a window with a given message and two buttons.'''
    
        self.disableWidgets()
        self.busy = True
        
        def ok():
        
            self.cancelled = False
            cmd()
            topWarning.destroy()
    
        # Setup window
        
        topWarning = tk.Toplevel()
        topWarning.title(title)
        self.cont.addIcon(topWarning)
        setupWindow(topWarning, 300, 145)
        topWarning.focus_force()
        
        self.cancelled = True
        
        tk.Label(topWarning, text=body,
                 font=self.cont.small_font).pack(side='top', pady=(20*scsy, 5*scsy), expand=True)
        
        frameButtons = ttk.Frame(topWarning)
        frameButtons.pack(side='top', expand=True, pady=(0, 10*scsy))
        ttk.Button(frameButtons, text=button1, command=ok).grid(row=0, column=0)
        ttk.Button(frameButtons, text=button2,
                   command=lambda: topWarning.destroy()).grid(row=0, column=1)
        
        self.wait_window(topWarning)
        
        self.enableWidgets()
        self.busy = False
        
        return not self.cancelled
    
    def showHistogram(self):
    
        '''
        Create window with a histogram of the current 
        image and tools for adjusting the screen stretch.
        '''
    
        self.varM = tk.StringVar()
        label = self.getSelectedLabel()
        
        self.orig_stretched = label.stretched_img
        
        self.varM.set(0.5)
        
        self.menuRC.entryconfigure(7, state='disabled')
        self.canvasDisplay.delete(self.selectionBox)
        self.localSelection = False
        
        # Setup figure
        f = matplotlib.figure.Figure(figsize=(3.9*scsx, 3.4*scsx), dpi=100, facecolor=DEFAULT_BG,
                                     tight_layout={'pad' : 0.4})
        self.ax = f.add_subplot(111)
        self.ax.tick_params(axis='both', which='both', direction='in', top='off', bottom='on',
                            left='off', right='off', labeltop='off', labelbottom='on',
                            labelleft='off', labelright='off', pad=0)
        self.ax.tick_params(axis='x', which='major', labelsize=8, pad=4)
        
        self.ax.set_ylim([0, 1])
        
        # Compute histogram
        hist, bin_edges = np.histogram(label.stretched_img.flatten(), bins=257)
        
        self.x = np.linspace(bin_edges[0], bin_edges[-2], 200)
        
        self.ax.set_xlim([bin_edges[0], bin_edges[-2]])
        
        # Plot histogram and stretch function
        self.line1, = self.ax.plot(bin_edges[:-1], hist/(1.05*np.max(hist)), color='gray')
        self.line2, = self.ax.plot(self.x, stretch(self.x, 0.5)/65535.0, color='lime')
        
        self.disableWidgets()
        self.busy = True
        
        # Setup window
        topHist = tk.Toplevel()
        topHist.title('Histogram')
        self.cont.addIcon(topHist)
        setupWindow(topHist, 470, 520)
        topHist.focus_force()
        
        def apply():
            self.orig_stretched = label.stretched_img
            self.updateDisplayedImage(label, fromHist=True)
            self.showImage(label)
            
        frameCanvas = ttk.Frame(topHist)
        frameCanvas.pack(side='top', pady=(20*scsy, 0), expand=True)
        
        self.histcanvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(f, frameCanvas)
        self.histcanvas._tkcanvas.config(highlightthickness=0)
        
        self.histcanvas.get_tk_widget().pack(side='top')
        
        self.scaleStretch = tk.Scale(frameCanvas, from_=0.001, to=0.999, resolution=0.001,
                                     orient='horizontal', length=388*scsx, showvalue=False,
                                     command=self.updateHistStretch)
        self.scaleStretch.pack(side='top')
        
        self.scaleStretch.set(0.5)
        
        frameButtons1 = ttk.Frame(frameCanvas)
        frameButtons1.pack(side='top', fill='x')
        
        ttk.Button(frameButtons1, text='Clip black point',
                   command=lambda: self.clipBlackPoint(label)).pack(side='left', padx=10*scsx)
        tk.Label(frameButtons1, textvariable=self.varM).pack(side='left', expand=True)
        ttk.Button(frameButtons1, text='Clip white point',
                   command=lambda: self.clipWhitePoint(label)).pack(side='right', padx=10*scsx)
        
        frameButtons2 = ttk.Frame(topHist)
        frameButtons2.pack(side='top', pady=8*scsy)
        
        ttk.Button(frameButtons2, text='Autostretch',
                   command=lambda: self.applyAutoStretch(label)).pack(side='left', padx=(40*scsx, 0))
        ttk.Button(frameButtons2, text='Stretch histogram',
                   command=lambda: self.stretchHist(label)).pack(side='left', padx=10*scsx, expand=True)
        ttk.Button(frameButtons2, text='Reset to linear',
                   command=lambda: self.resetToLinear(label)).pack(side='right', padx=(0, 40*scsx))
        
        frameButtons3 = ttk.Frame(topHist)
        frameButtons3.pack(side='top', pady=(0, 20*scsy))
        
        ttk.Button(frameButtons3, text='Apply changes',
                   command=apply).pack(side='left', padx=(20*scsx, 10*scsx))
        ttk.Button(frameButtons3, text='Close',
                   command=lambda: topHist.destroy()).pack(side='right', padx=(0, 20*scsx))
        
        self.wait_window(topHist)
        
        try:
            label.stretched_img = self.orig_stretched
            self.menuRC.entryconfigure(7, state='normal')
        except:
            pass
        self.enableWidgets()
        self.busy = False
        
        self.menuActive = False
        
    def updateHistStretch(self, m):
    
        '''Update the displayed stretch function.'''
    
        self.line2.set_data(self.x, stretch(clipLevel(self.x, np.min(self.x), np.max(self.x)),
                                            float(m))/65535.0)
        self.histcanvas.draw()
        self.varM.set(m)
        
    def clipBlackPoint(self, label):
    
        '''Redraw the histogram with clipped black point.'''
    
        img = label.stretched_img
        label.stretched_img = clipLevel(img, np.min(img), 65535)
        self.updateHist(label)
    
    def clipWhitePoint(self, label):
    
        '''Redraw the histogram with clipped white point.'''
    
        img = label.stretched_img
        label.stretched_img = clipLevel(img, 0, np.max(img))
        self.updateHist(label)
    
    def stretchHist(self, label):
    
        '''Redraw a stretched version of the histogram.'''
    
        label.stretched_img = stretch(label.stretched_img, float(self.varM.get()))
        self.updateHist(label)
    
    def applyAutoStretch(self, label):
    
        '''Redraw an autostretched version of the histogram.'''
    
        label.stretched_img = autostretch(label.raw_img)
        self.updateHist(label)
    
    def resetToLinear(self, label):
    
        '''Show the histogram of the linear image.'''
    
        label.stretched_img = label.raw_img
        self.updateHist(label)
        
    def updateHist(self, label):
    
        '''Compute a new histogram of the stretched image and update the plot.'''
    
        hist, bin_edges = np.histogram(label.stretched_img.flatten(), bins=257)
                                           
        self.ax.set_xlim([bin_edges[0], bin_edges[-2]])
        self.line1.set_data(bin_edges[:-1], hist/(1.05*np.max(hist)))
        self.x = np.linspace(bin_edges[0], bin_edges[-2], 200)
        self.scaleStretch.set(0.5)
        self.updateHistStretch(0.5)
        self.histcanvas.draw()
    
    def updateDisplayedImage(self, label, filename=None, fromHist=False):
    
        '''Create a photo image from the raw image of the label.'''
    
        # Save data as temporary image
        plt.imsave('temp.jpg', label.stretched_img, cmap=plt.get_cmap('gray'), vmin=0, vmax=65535)
            
        # Open as PIL image and store as label attribute
        label.pil_img = Image.open('temp.jpg')
        
        # Store Photo Image as label attribute
        label.photo_img = ImageTk.PhotoImage(label.pil_img)
        
        # Create resized version of image if necessary
        if self.showResized or fromHist:
        
            if not fromHist:
                self.varMessageLabel.set('%s - Resizing..' % filename)
                self.labelMessage.update_idletasks()
                
            self.createResImage(label)
        
    
class MessageWindow(ttk.Frame):

    def __init__(self, parent, controller):
    
        '''Initialize Message Window frame.'''
    
        ttk.Frame.__init__(self, parent)
        
        self.cont = controller
        small_font = self.cont.small_font
        medium_font = self.cont.medium_font
        large_font = self.cont.large_font
        
        self.varHeaderLabel = tk.StringVar()
        
        self.varMessageLabel = tk.StringVar()
        
        self.varMessageLabel.set('No sensor data exists for the currently active camera.\n\n' \
                                + 'Aquire sensor data with the Image Analyser to enable this tool.')
        
        frameHeader = ttk.Frame(self)
        frameContent = ttk.Frame(self)
        frameBottom = ttk.Frame(self)
        
        frameHeader.pack(side='top', fill='x')
        frameContent.pack(side='top', fill='both', expand=True)
        frameBottom.pack(side='bottom', fill='x')
        
        labelHeader = ttk.Label(frameHeader, textvariable=self.varHeaderLabel, font=large_font,
                                anchor='center')
        
        frameNames = ttk.Frame(frameHeader)
        labelCamName = ttk.Label(frameNames, textvariable=self.cont.varCamName, anchor='center')
        labelTelName = ttk.Label(frameNames, textvariable=self.cont.varTelName, anchor='center')
        labelFLMod = ttk.Label(frameNames, textvariable=self.cont.varFLMod, anchor='center')
        
        labelHeader.pack(side='top', pady=3*scsy)
        
        ttk.Separator(frameHeader, orient='horizontal').pack(side='top', fill='x')
        
        frameNames.pack(side='top', fill='x')
        labelCamName.pack(side='left', expand=True)
        labelTelName.pack(side='left', expand=True)
        labelFLMod.pack(side='right', expand=True)
        
        tk.Label(frameContent, textvariable=self.varMessageLabel,
                  font=medium_font).pack(fill='both', expand=True)
        
        ttk.Separator(frameBottom, orient='horizontal').pack(side='top', fill='x')
        ttk.Label(frameBottom, text='').pack(side='top', fill='both')
        
        
class ToolTip:

    def __init__(self, widget, fs):
    
        '''Initialize class for showing tooltips.'''
    
        self.widget = widget
        self.fs = fs

    def showToolTip(self, tiptext):
    
        '''Display tooltip.'''
        
        self.topTip = tk.Toplevel(self.widget) # Create tooltip window
        self.topTip.wm_overrideredirect(1)     # Remove window border
        self.topTip.wm_attributes('-topmost', 1)
        
        # Set window position
        self.topTip.wm_geometry('+%d+%d' % (self.widget.winfo_pointerx() + 15*scsx,
                                            self.widget.winfo_pointery() + 15*scsy))
        
        # Define tooltip label
        label = tk.Label(self.topTip, text=tiptext, justify='left', background='white',
                         relief='solid', borderwidth=1, font=('Tahoma', self.fs))
        
        # Place tooltip label with internal padding
        label.pack(ipadx=1)
    
    def hideToolTip(self):
    
        '''Hide tooltip.'''
    
        try:
            self.topTip.destroy()
        except:
            pass
        
        
class ErrorWindow(tk.Tk):

    def __init__(self, error_message):
    
        '''Initialize error window.'''
    
        tk.Tk.__init__(self)
        
        self.title('Error')
        
        try:
            self.iconbitmap('aplab_icon.ico')
        except:
            pass
            
        errfont = tkFont.Font(root=self, family='Tahoma', size=9)
        
        ttk.Label(self, text=error_message, font=errfont).pack(pady=12*scsy, expand=True)
        ttk.Button(self, text='OK', command=lambda: self.destroy()).pack(pady=(0, 12*scsy),
                                                                         expand=True)
        
        strs = error_message.split('\n')
        lens = [len(str) for str in strs]
        
        setupWindow(self, (errfont.measure(strs[lens.index(max(lens))]) + 20), 300)
        
        self.wm_attributes('-topmost', 1)
        self.focus_force()
      
      
class Catcher: 

    def __init__(self, func, subst, widget):
    
        self.func = func 
        self.subst = subst
        self.widget = widget
        
    def __call__(self, *args):
    
        try:
        
            if self.subst:
            
                args = apply(self.subst, args)
                
            return apply(self.func, args)
            
        except SystemExit, msg:
        
            raise SystemExit, msg
            
        except:
        
            ex_type, ex, tb = sys.exc_info()
            
            msg1 = 'A Python error occured:\n\n'
            msg2 = '\nThis event has been stored in the log file "errorlog.txt".'
            
            file=open('errorlog.txt', 'a')
            
            file.write('**** ' + str(datetime.datetime.now()) + ' ****\n')
            traceback.print_exc(file=file)
            file.write('\n')
            
            file.close()
            
            error = ErrorWindow(msg1 + '\n'.join(traceback.format_tb(tb)) + '\n' \
                                + ex_type.__name__ + ': ' + ex.message + '\n' + msg2)
            error.mainloop()
            
     
def createToolTip(widget, tiptext, fs):

    '''Creates a tooltip with the given text for the given widget.'''
    
    toolTip = ToolTip(widget, fs) # Create ToolTip instance
    
    def enterWidget(event):
        toolTip.showToolTip(tiptext)
        
    def moveWidget(event):
        try:
            toolTip.topTip.wm_geometry('+%d+%d' % (event.widget.winfo_pointerx() + 15*scsx,
                                                   event.widget.winfo_pointery() + 15*scsy))
        except:
            pass
        
    def leaveWidget(event):
        toolTip.hideToolTip()
       
    # Bind the show and hide methods to the enter and leave event of the widget
    widget.bind('<Enter>', enterWidget)
    widget.bind('<Motion>', moveWidget)
    widget.bind('<Leave>', leaveWidget)
    
def setupWindow(window, width, height):

    '''Sets the given window to given size and centers it in the screen.'''
    
    width *= scsx
    height *= scsy
        
    x = (sw - width)/2
    y = (sh - height)/2
        
    window.geometry('%dx%d+%d-%d' % (width, height, x, y))
    window.update_idletasks()

def setNewFS(app, cnum, tnum, fs):

    '''Change default font size and restart application.'''
    
    file = open('cameradata.txt', 'r')
    lines = file.read().split('\n')
    file.close()
    
    file = open('cameradata.txt', 'w')
    
    for line in lines[:-1]:
        file.write(line + '\n')
        
    file.write(','.join(lines[-1].split(',')[0:2]) + ', Fontsize: %d' % fs)
    file.close()
    
    app.destroy()
    app = APLab(cnum, tnum, fs)
    app.mainloop()

def sortDataList(name, filename):

    '''Sort camera data list and return index of provided name.'''

    def natural_keys(text):
        return [(int(c) if c.isdigit() else c.lower()) for c in re.split('(\d+)', text)]

    file = open(filename, 'r')
    lines = file.read().split('\n')
    file.close()

    names = []
    sortnames = []
    rest = []
    
    nameidx = 0

    for line in lines[1:-1]:

        vals = line.split(',')
        names.append(vals[0])
        sortnames.append(vals[0])
        rest.append(','.join(vals[1:]))
        
    sortnames.sort(key=natural_keys)

    file = open(filename, 'w')

    file.write(lines[0])

    for i in range(len(names)):

        idx = names.index(sortnames[i])
        
        file.write('\n' + sortnames[i] + ',' + rest[idx])
        
    file.write('\n' + lines[-1])
    file.close()
    
    return sortnames.index(name)
    
def clipLevel(img, black_point, white_point):

    '''
    Perform a linear stretch to make the "black_point" pixel 
    values black and the "white_point" pixel values white.
    '''
    
    return (65535*(img - black_point).astype('float')/(white_point - black_point)).astype('uint16')
    
def stretch(img, m):
    
    '''Stretch the image with a "midtones transfer function".'''

    return (img*(m - 1)/((img/65535.0)*(2*m - 1) - m)).astype('uint16')
    
def autostretch(img):

    '''Returns a clipped and stretched image where the mean is at 25% gray.'''
    
    if np.min(img) < np.max(img):
    
        # Clip both ends of histogram
        img = clipLevel(img, np.min(img), np.max(img))
        
        # Stretch the image with to bring the mean level to 25 %
        new_mean = 0.25
        mean = np.mean(img/65535.0)
        m = mean*(new_mean - 1)/(2*new_mean*mean - new_mean - mean)
        new_img = stretch(img, m)
    
    else:
        new_img = 65535*np.ones(img.shape, dtype='uint16')
    
    return new_img
    
def convSig(val, toMag):

    '''Convert between electron flux and luminance.'''

    f = FOCAL_LENGTH[app.tnum][0] # Focal length [mm]
    m = app.FLModVal              # Focal length multiplier
    d = APERTURE[app.tnum][0]     # Aperture diameter [mm]
    
    # Solid angle subtended by the aperture at the location of the sensor
    
    omega = 2*np.pi*m*f*(1.0/(m*f) - 1.0/np.sqrt((0.5*d)**2 + (m*f)**2))
    
    A = (PIXEL_SIZE[app.cnum][0]*1e-6)**2 # Pixel area [m^2]
    
    T = 1.0 - app.TLoss # Telescope transmission factor
    
    E = 1.986e-16/app.avgWL # Average photon energy [J]
    
    q = QE[app.cnum][0] # Peak quantum efficiency
    
    if toMag:
        
        L_lin = val*683.0*E/(omega*A*T*q) # Luminance [cd/m^2]
        
        L_log = -2.5*np.log10(L_lin/108000.0) # Luminance [mag/arcsec^2]
    
        ret = L_log
        
    else:
    
        L_lin = 108000.0*10**(-0.4*val) # Luminance [cd/m^2]
        
        Fe = L_lin*omega*A*T*q/(683.0*E) # Electron flux [e-/s]
        
        ret = Fe
        
    return ret
    
def itpData(datastring, d_type):

    '''Recognizes user modified data in the string and returns the values with indicators.'''

    data = datastring.split('-')
    L = len(data)
    
    um = np.zeros(L)
    vals = np.zeros(L, dtype=d_type)
    
    for i in range(L):
    
        if '*' in data[i]: um[i] = 1
        vals[i] = data[i].split('*')[0]
    
    return [vals, um]
    
tk.CallWrapper = Catcher
    
# Define tooltip strings

tw = 40

TTExp = textwrap.fill('The exposure time of the subframe.', tw)
TTUseDark = textwrap.fill('[Deactivate if you don\'t have a dark frame with the same exposure time and temperature as the light frame. This will restrict the noise and flux values that can be calculated, but SNR and DR will not be affected.]', tw)
TTDarkNoise = textwrap.fill('The standard deviation of pixel values in a dark frame with the same exposure time and temperature as the relevant subframe.', tw) + '\n\n' + textwrap.fill('[This value must be from an uncalibrated frame.]', tw)
TTDarkLevel = textwrap.fill('The average or median pixel value in a dark frame with the same exposure time and temperature as the relevant subframe.', tw) + '\n\n' + textwrap.fill('[This value must be from an uncalibrated frame.]', tw)
TTBGNoise = textwrap.fill('The standard deviation of pixel values in a background region of the subframe.', tw) + '\n\n' + textwrap.fill('[This value must be from one color of the Bayer array of an uncalibrated frame.]', tw)
TTBGLevel = textwrap.fill('The average or median pixel value in a background region of the subframe.', tw) + '\n\n' + textwrap.fill('[This value must be from an uncalibrated frame.]', tw)
TTTarget = textwrap.fill('The average or median pixel value in a target region of the subframe, where the SNR is to be calculated.', tw) + '\n\n' + textwrap.fill('[This value must be from an uncalibrated frame.]', tw)
TTDF = textwrap.fill('The number of photoelectrons per second produced in each pixel by the dark current.', tw)
TTSFLum = textwrap.fill('The estimated apparent magnitude of a 1x1 arcsecond piece of the sky.', tw) + '\n\n' + textwrap.fill('[The magnitude unit used here does not correspond exactly to a visual magnitude unit, since the passband of the camera generally will be different from the visual (V) passband. The camera sensitivity is assumed to peak at 555 nm.]', tw)
TTSFElectron = textwrap.fill('The number of photoelectrons per second produced in each pixel as a result of photons from the skyglow.', tw) + '\n\n' + textwrap.fill('[This is a measure of the sky brightness. Different electron fluxes are not directly comparable between different camera models, but are comparable for the same camera model if the optical train is the same.]', tw)
TTTFLum = textwrap.fill('The estimated apparent magnitude of a 1x1 arcsecond piece of the target.', tw) + '\n\n' + textwrap.fill('[The magnitude unit used here does not correspond exactly to a visual magnitude unit, since the passband of the camera generally will be different from the visual (V) passband. The camera sensitivity is assumed to peak at 555 nm.]', tw)
TTTFElectron = textwrap.fill('The number of photoelectrons per second produced in each target pixel as a result of photons from the target.', tw) + '\n\n' + textwrap.fill('[This is a measure of the brightness of the target. Different electron fluxes are not directly comparable between different camera models, but are comparable for the same camera model if the optical train is the same.]', tw)
TTDSFPhoton = textwrap.fill('The number of photons per second that would have to reach each pixel to produce the observed electron flux from both skyglow and dark current.', tw) + '\n\n' + textwrap.fill('[Different photon fluxes are comparable between different camera models, povided that the same optical train is used and that the fluxes relate to the same color(s) of light.]', tw)
TTDSFElectron = textwrap.fill('The number of photoelectrons per second produced in each pixel either as a result of photons from the skylow, or from dark current.', tw) + '\n\n' + textwrap.fill('[Different electron fluxes are not directly comparable between different camera models, but are comparable for the same camera model if the optical train is the same.]', tw)
TTSubs = textwrap.fill('[Set higher than 1 to get the SNR and simulated image of a stacked frame rather than of a single subframe.]', tw)
TTSNR = textwrap.fill('The signal to noise ratio of the target in the subframe.', tw)
TTStackSNR = textwrap.fill('The signal to noise ratio of the target in the stacked image.', tw) + '\n\n' + textwrap.fill('[The subframes are assumed to be averaged together.]', tw)
TTDR = textwrap.fill('The dynamic range of the image indicates the size of the intensity range between the noise floor and the saturation capacity.', tw) + '\n\n' + textwrap.fill('[The intensity range doubles for every stop, or about every third dB.]', tw)
TTFL = textwrap.fill('The distance traveled by parallell rays after refraction/reflection in the primary lens/mirror before they converge in a focal point.', tw)
TTEFL = textwrap.fill('The focal length multiplied by the magnification factor of the barlow lens or focal reducer.', tw)
TTAP = textwrap.fill('The diameter of the primary lens/mirror.', tw)
TTFR = textwrap.fill('The ratio of the effective focal length to the aperture diameter.', tw) + '\n\n' + textwrap.fill('[A lower focal ratio means that a higher rate of photons can reach each pixel, making the image brighter.]', tw)
TTIS = textwrap.fill('The angle corresponding to the length of a single pixel in the image.', tw)
TTRL = textwrap.fill('The angular resolution estimated with the Rayleigh Criterion. This is the smallest angular separation of two stars that still can be resolved.', tw) + '\n\n' + textwrap.fill('[The light from the stars is assumed to have a wavelength of 550 nm. The actual resolution will usually be poorer than the estimated value, due to optical imperfections and atmospheric seeing.]', tw)
TTGain = textwrap.fill('The ratio of the number of photoelectrons produced in a pixel to the resulting pixel value in the digital image.', tw)
TTSatCap = textwrap.fill('The maximum number of photoelectrons that can be produced in a pixel before the pixel value reaches the white point.', tw)
TTBL = textwrap.fill('The mean pixel value of a bias frame, where no photons have reached the sensor.', tw)
TTWL = textwrap.fill('The highest possible pixel value in the image.', tw)
TTPS = textwrap.fill('The side length of a single pixel.', tw)
TTQE = textwrap.fill('The maximum probability that a photon reaching the sensor will result in the production of a photoelectron.', tw)
TTRN = textwrap.fill('The uncertainty in the number of photoelectrons in a pixel caused by reading the sensor.', tw) + '\n\n' + textwrap.fill('[This includes the quantization error introduced by rounding to a whole number of ADUs.]', tw)
TTDN = textwrap.fill('The uncertainty in the number of photoelectrons in a pixel produced by the randomness of the dark current.', tw)
TTSN = textwrap.fill('The uncertainty in the number of photoelectrons in a pixel produced by the randomness of the skyglow photons.', tw)
TTDSN = textwrap.fill('The uncertainty in the number of photoelectrons in a pixel caused by both skyglow and dark current.', tw)
TTTotN = textwrap.fill('The total uncertainty in the number of photoelectrons in each background pixel.', tw) + '\n\n' + textwrap.fill('[This includes read noise, dark noise and skyglow noise.]', tw)
TTStretch = textwrap.fill('[Activate to perform a histogram stretch to increase the contrast of the simulated image.]', tw)
TTTotal = textwrap.fill('The total exposure time for all the subframes combined.', tw)
TTMax = textwrap.fill('The maximum allowed exposure time for a subframe.', tw) + '\n\n' + textwrap.fill('[This will be limited by factors like tracking/guiding accuracy, unwanted saturation and risk of something ruining the exposure.]', tw)

sw = win32api.GetSystemMetrics(0) # Screen width in pixels
sh = win32api.GetSystemMetrics(1) # Screen height in pixels

scsy = scsx = sh/768.0  # Scaling after screen height

# Default background color
DEFAULT_BG = '#%02x%02x%02x' % (240, 240, 237)

# Window sizes

l_x = 1050 # Largest width
l_y = 600  # Largets height

sw_b = sw*0.9
sh_b = sh*0.9

# If width or height exceeds screen size, adjust scaling

if l_x > sw_b:
    scsx = sw_b/l_x
    
if l_y > sh_b:
    scsy = sh_b/l_y

CAL_WINDOW_SIZE = (l_x, 560)    
SIM_WINDOW_SIZE = (l_x, 560)
PLOT_WINDOW_SIZE = (l_x, 560)
AN_WINDOW_SIZE = (l_x, l_y)

# Lists for camera data
CNAME = []
TYPE = []
GAIN = []
RN = []
SAT_CAP = []
BLACK_LEVEL = []
WHITE_LEVEL = []
QE = []
PIXEL_SIZE = []
ISO = []

# Lists for telescope data
TNAME = []
FOCAL_LENGTH = []
APERTURE = []

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
        
            CNAME.append(line[0])
            TYPE.append(line[1])
            
            if not (line[1] == 'DSLR' or line[1] == 'CCD'):
            
                startup_success = False
                startup_error = 'Invalid camera type for camera model:\n"%s". ' \
                                + 'Must be "DSLR" or "CCD".' % CNAME[-1]
                break
                
            if len(line) != (10 if line[1] == "DSLR" else 9): raise IndexError
            
            GAIN.append(itpData(line[2], 'float'))
            RN.append(itpData(line[3], 'float'))
            SAT_CAP.append(itpData(line[4], 'int'))
            BLACK_LEVEL.append(itpData(line[5], 'int'))
            WHITE_LEVEL.append(itpData(line[6], 'int'))
            QE.append([('NA' if line[7] == 'NA' else float(line[7].split('*')[0])),
                        (1 if '*' in line[7] else 0)])
            PIXEL_SIZE.append([float(line[8].split('*')[0]), (1 if '*' in line[8] else 0)])
            ISO.append(np.array(line[9].split('-')).astype(int) if line[1] == 'DSLR' else [0])
            
            if line[1] == 'DSLR':
            
                if len(GAIN[-1][0]) != len(ISO[-1]):
                
                    startup_success = False
                    startup_error = 'Non-matching number of gain and ISO values\nfor ' \
                                    + 'camera model: "%s".' % CNAME[-1]
                    break
                    
                elif len(RN[-1][0]) != len(ISO[-1]):
                
                    startup_success = False
                    startup_error = 'Non-matching number of read noise and ISO values\nfor ' \
                                    + 'camera model: "%s".' % CNAME[-1]
                    break
                    
            if len(SAT_CAP[-1][0]) != len(GAIN[-1][0]):
            
                startup_success = False
                startup_error = 'Non-matching number of saturation capacity and\ngain values for ' \
                                + 'camera model: "%s".' % CNAME[-1]
                break
                
            if len(WHITE_LEVEL[-1][0]) != len(GAIN[-1][0]):
            
                startup_success = False
                startup_error = 'Non-matching number of white level and gain\nvalues for ' \
                                + 'camera model: "%s".' % CNAME[-1]
                break
            
        except IndexError:
        
            startup_success = False
            startup_error = 'Invalid data configuration in\nline %d in "cameradata.txt".' \
                            % (len(CNAME) + 1)
            break
            
        except (TypeError, ValueError):
        
            startup_success = False
            startup_error = 'Invalid data type detected for camera model:\n"%s".' % CNAME[-1]
            break
            
    for line in lines2[1:-1]:
    
        line = line.split(',')
        
        try:
            TNAME.append(line[0])
            
            if len(line) != 3: raise IndexError
            
            FOCAL_LENGTH.append([float(line[1].split('*')[0]), (1 if '*' in line[1] else 0)])
            APERTURE.append([float(line[2].split('*')[0]), (1 if '*' in line[2] else 0)])
            
        except IndexError:
        
            startup_success = False
            startup_error = 'Invalid data configuration in\nline %d in "telescopedata.txt".' \
                            % (len(TNAME) + 1)
            break
            
        except (TypeError, ValueError):
        
            startup_success = False
            startup_error = 'Invalid data type detected for telescope model:\n"%s".' % TNAME[-1]
            break
         
# Get name of default camera model and default tooltip state
            
if startup_success:
    
    try:
        definfo = (lines1[-1].split('Camera: ')[1]).split(', Tooltips: ')
        definfo2 = definfo[1].split(', Fontsize: ')
        
        CDEFAULT = definfo[0]
        TT_STATE = definfo2[0]
        FS = definfo2[1]
        if FS != 'auto': FS = int(FS)
        
        if CDEFAULT == 'none':
        
            no_cdefault = True
        
        elif not CDEFAULT in CNAME:
        
            startup_success = False
            startup_error = 'Invalid default camera name. Must\nbe the name of a camera in the list.'
            
        if not (TT_STATE == 'on' or TT_STATE == 'off'):
            
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
        
        elif not TDEFAULT in TNAME:
        
            startup_success = False
            startup_error = 'Invalid default telescope name. Must\nbe the name of a telescope in the list.'
            
    except IndexError:
    
        startup_success = False
        startup_error = 'Invalid last line in "telescope.txt". Must be\n"Telescope: <telescope name>".'
    
# Run application, or show error message if an error occured
    
if startup_success:
    app = APLab(None if no_cdefault else CNAME.index(CDEFAULT),
                None if no_tdefault else TNAME.index(TDEFAULT), FS)
    app.mainloop()
else:
    error = ErrorWindow(startup_error)
    error.mainloop()