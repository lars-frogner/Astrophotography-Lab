'''
Version: 0.1.0-alpha
'''

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
import os
import subprocess
import pyfits
import re

matplotlib.use("TkAgg") # Use TkAgg backend


class APLab(tk.Tk):

    def __init__(self, cnum, fs):
    
        '''Initialize application.'''
    
        tk.Tk.__init__(self) # Run parent constructor
        
        self.container = ttk.Frame(self) # Define main frame
        
        self.cnum = cnum # Index if camera in camera data lists. None if no camera is selected.
        self.toolsConfigured = False # True if the non-"Image Analyzer" classes are initialized
        
        self.title('Astrophotography Lab 0.1.0') # Set window title
        
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
        self.snrMode = tk.IntVar()
        self.simMode = tk.IntVar()
        self.plMode = tk.IntVar()
        self.anMode = tk.IntVar()
        
        self.snrMode.set(0)
        self.simMode.set(0)
        self.plMode.set(0)
        self.anMode.set(1)
        
        # Define attributes to keep track of current flux unit
        self.photonFluxUnit = tk.IntVar()
        self.electronFluxUnit = tk.IntVar()
        
        # Define attributes to keep track of tooltip states
        self.tooltipsOn = tk.IntVar()
        self.tooltipsOn.set(1 if TT_STATE == 'on' else 0)
        
        self.defaultTTState = tk.IntVar()
        self.defaultTTState.set(1 if TT_STATE == 'on' else 0)
        
        # Setup window menu
        self.menubar = tk.Menu(self)
        
        # "Tool" menu
        menuTool = tk.Menu(self.menubar, tearoff=0)
        menuTool.add_checkbutton(label='Image Analyzer', variable=self.anMode,
                                 command=self.enterAnFrame)
        menuTool.add_checkbutton(label='SNR Calculator', variable=self.snrMode,
                                 command=self.enterSNRFrame)
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
        
        # "Input" menu
        self.menuInput = tk.Menu(self.menubar, tearoff=0)
        self.menuInput.add_command(label='Clear input',
                                   command=self.clearInput)
        self.menuInput.add_command(label='Transfer input to Image Simulator',
                                   command=self.transferToSim)
        self.menuInput.add_command(label='Transfer input to Plotting Tool',
                                   command=self.transferToPlot)
        
        self.menubar.add_cascade(label='Input', menu=self.menuInput)
        
        # "Settings" menu
        self.menuSettings = tk.Menu(self.menubar, tearoff=0)
        
        # "Camera" submenu of "Settings"
        self.menuCamera = tk.Menu(self.menubar, tearoff=0)
        self.menuCamera.add_command(label='Change camera', command=self.changeCamera)
        self.menuCamera.add_command(label='Modify camera parameters', command=self.modifyCamParams)
        
        self.menuSettings.add_cascade(label='Camera', menu=self.menuCamera)
        
        # "Tooltips" submenu of "Settings"
        self.menuTT = tk.Menu(self.menubar, tearoff=0)
        self.menuTT.add_command(label='Toggle tooltips', command=self.toggleTooltips)
        if self.tooltipsOn.get():
            self.menuTT.add_command(label='Turn off as default', command=self.toogleDefaultTTState)
        else:
            self.menuTT.add_command(label='Turn on as default', command=self.toogleDefaultTTState)
            
        self.menuSettings.add_cascade(label='Tooltips', menu=self.menuTT)
        
        self.menuSettings.add_command(label='Change font size', command=self.changeFS)
        
        # "Flux unit" submenu of "Settings"
        menuFluxUnit = tk.Menu(self.menubar, tearoff=0)
        menuFluxUnit.add_checkbutton(label='photons/s', variable=self.photonFluxUnit,
                                     command=self.setPhotonFluxUnit)
        menuFluxUnit.add_checkbutton(label='e-/s', variable=self.electronFluxUnit,
                                     command=self.setElectronFluxUnit)
        
        self.menuSettings.add_cascade(label='Flux unit', menu=menuFluxUnit)
        
        self.menubar.add_cascade(label='Settings', menu=self.menuSettings)
        
        # Show menubar
        self.config(menu=self.menubar)
        
        # Some menu items are disabled on startup
        self.menubar.entryconfig(2, state='disabled')
        self.menuInput.entryconfig(1, state='disabled')
        self.menuInput.entryconfig(2, state='disabled')
        self.menuSettings.entryconfig(0, state='disabled')
        self.menuSettings.entryconfig(1, state='disabled')
        self.menuSettings.entryconfig(3, state='disabled')
        
        # Dictionary to hold all frames
        self.frames = {}
        
        # Initialize Image Analyzer class
        frameAn = ImageAnalyzer(self.container, self)
        self.frames[ImageAnalyzer] = frameAn
        frameAn.grid(row=0, column=0, sticky='NSEW')
        
        # Show start page
        self.showFrame(ImageAnalyzer)
        
        # Resize and recenter window
        setupWindow(self, *AN_WINDOW_SIZE)
        
        self.focus_force()
    
    def setupToolsController(self):
    
        '''Runs initialization method camera selection method if neccessary.'''
        
        # If no camera is selected
        if self.cnum is None:
            
            # Run selection method
            if not self.changeCamera():
                return None # Return None if topwindow was exited
                
        # Initialize other tool classes
        self.setupTools(self.cnum)
        
        return True
    
    def setupTools(self, cnum):
    
        '''Create instances of the SNRCalculator, ImageSimulator and PlottingTool classes.'''
    
        self.cnum = cnum # The index of the current camera model in the camera data lists
        self.isDSLR = TYPE[self.cnum] == 'DSLR' # Boolean to keep track of camera type
        self.hasQE = QE[self.cnum] != 'NA' # True if a QE value exists for the camera
        
        # Set default flux unit
        self.photonFluxUnit.set(self.hasQE)
        self.electronFluxUnit.set(not self.hasQE)
        
        # Setup frames and add to dictionary
        frameSNR = SNRCalculator(self.container, self)
        frameSim = ImageSimulator(self.container, self)
        framePlot = PlottingTool(self.container, self)
        
        self.frames[SNRCalculator] = frameSNR
        self.frames[ImageSimulator] = frameSim
        self.frames[PlottingTool] = framePlot
        
        frameSNR.grid(row=0, column=0, sticky='NSEW')
        frameSim.grid(row=0, column=0, sticky='NSEW')
        framePlot.grid(row=0, column=0, sticky='NSEW')
        
        self.toolsConfigured = True
        
    def showFrame(self, page):
    
        '''Shows the given frame.'''
        
        self.frames[page].tkraise()
  
    def enterPlotFrame(self):
    
        '''Shows the Plotting Tool frame.'''
    
        # Do nothing if already in plotting frame
        if not self.snrMode.get() and not self.simMode.get() and not self.anMode.get():
            self.plMode.set(1) # Keep state from changing
            return None
        
        # Run tool initialization if neccessary
        if not self.toolsConfigured:
            if self.setupToolsController() is None:
                self.plMode.set(0)
                return None
        
        self.frames[PlottingTool].varMessageLabel.set('') # Clear message label
        self.showFrame(PlottingTool) # Show plot frame
        
        # Resize and recenter window
        setupWindow(self, *PLOT_WINDOW_SIZE)
        
        # Configure menu items
        self.menubar.entryconfig(2, state='normal')
        self.menuFile.entryconfig(0, state='disabled')
        self.menuInput.entryconfig(1, state='normal')
        self.menuInput.entryconfig(2, state='disabled')
        self.menuSettings.entryconfig(0, state='normal')
        self.menuSettings.entryconfig(1, state='normal')
        self.menuSettings.entryconfig(3, state='normal')
               
        self.plMode.set(1)
        self.snrMode.set(0)
        self.simMode.set(0)
        self.anMode.set(0)
        
    def enterSNRFrame(self):
    
        '''Shows the SNR Calculator frame.'''
        
        # Do nothing if already in calculator frame
        if not self.simMode.get() and not self.plMode.get() and not self.anMode.get():
            self.snrMode.set(1) # Keep state from changing
            return None
        
        # Run tool initialization if neccessary
        if not self.toolsConfigured:
            if self.setupToolsController() is None:
                self.snrMode.set(0)
                return None
                
        self.frames[SNRCalculator].varMessageLabel.set('') # Clear message label
        self.showFrame(SNRCalculator) # Show calculator frame
        
        # Resize and recenter window
        setupWindow(self, *SNR_WINDOW_SIZE)
        
        # Configure menu items
        self.menubar.entryconfig(2, state='normal')
        self.menuFile.entryconfig(0, state='normal')
        self.menuInput.entryconfig(1, state='normal')
        self.menuInput.entryconfig(2, state='normal')
        self.menuSettings.entryconfig(0, state='normal')
        self.menuSettings.entryconfig(1, state='normal')
        self.menuSettings.entryconfig(3, state='normal')
            
        self.snrMode.set(1)
        self.simMode.set(0)
        self.plMode.set(0)
        self.anMode.set(0)
        
    def enterSimFrame(self):
    
        '''Shows the Image Simulator frame.'''
        
        # Do nothing if already in simulator frame
        if not self.snrMode.get() and not self.plMode.get() and not self.anMode.get():
            self.simMode.set(1) # Keep state from changing
            return None
        
        # Run tool initialization if neccessary
        if not self.toolsConfigured:
            if self.setupToolsController() is None:
                self.simMode.set(0)
                return None
                
        self.frames[ImageSimulator].varMessageLabel.set('') # Clear message label
        self.showFrame(ImageSimulator) # Show simulator frame
        
        # Resize and recenter window
        setupWindow(self, *SIM_WINDOW_SIZE)
        
        # Configure menu items
        self.menubar.entryconfig(2, state='normal')
        self.menuFile.entryconfig(0, state='disabled')
        self.menuInput.entryconfig(1, state='disabled')
        self.menuInput.entryconfig(2, state='normal')
        self.menuSettings.entryconfig(0, state='normal')
        self.menuSettings.entryconfig(1, state='normal')
        self.menuSettings.entryconfig(3, state='normal')
            
        self.snrMode.set(0)
        self.simMode.set(1)
        self.plMode.set(0)
        self.anMode.set(0)
    
    def enterAnFrame(self):
    
        '''Shows the Image Analyzer frame.'''
    
        # Do nothing if already in analyzer frame
        if not self.snrMode.get() and not self.simMode.get() and not self.plMode.get():
            self.anMode.set(1) # Keep state from changing
            return None
            
        self.frames[ImageAnalyzer].varMessageLabel.set('') # Clear message label
        self.showFrame(ImageAnalyzer)
        
        # Resize and recenter window
        setupWindow(self, *AN_WINDOW_SIZE)
        
        # Configure menu items
        self.menubar.entryconfig(2, state='disabled')
        self.menuInput.entryconfig(1, state='disabled')
        self.menuInput.entryconfig(2, state='disabled')
        self.menuSettings.entryconfig(0, state='disabled')
        self.menuSettings.entryconfig(1, state='disabled')
        self.menuSettings.entryconfig(3, state='disabled')
        
        self.snrMode.set(0)
        self.simMode.set(0)
        self.plMode.set(0)
        self.anMode.set(1)
    
    def saveData(self):
    
        '''Creates window with options for saving image data.'''
    
        frame = self.frames[SNRCalculator]
        
        # Show error if no image data is calculated
        if not frame.dataCalculated:
        
            frame.varMessageLabel.set('Image data must be calculated before saving.')
            
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
        self.menubar.entryconfig(1, state='normal')
        self.menubar.entryconfig(2, state='normal')
        self.menubar.entryconfig(3, state='normal')
        self.menubar.entryconfig(4, state='normal')
        
    def executeSave(self):
    
        '''Saves image data to text file.'''
    
        keywords = self.varKeywords.get() # Get user inputted keyword string
        
        if not ',' in keywords and keywords != '':
        
            self.topSave.destroy() # Close window
            
            # Append image data to the text file
            
            file = open('imagedata.txt', 'a')
            
            frame = self.frames[SNRCalculator]
                
            file.write('%s,%s,%d,%d,%g,%d,%g,%g,%g,%g,%d,%.3f,%.3f,%.3f\n' % (NAME[self.cnum],
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
                                                      frame.sf/(QE[self.cnum] if self.hasQE else 1),
                                                      frame.tf/(QE[self.cnum] if self.hasQE else 1)))
            
            file.close()
            
            frame.varMessageLabel.set('Image data saved.')
        
        # Show error message if the keyword contains a ","
        elif ',' in keywords:
        
            self.varSaveError.set('Keyword cannot contain a ",".')
        
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
        self.menubar.entryconfig(1, state='normal')
        self.menubar.entryconfig(2, state='normal')
        self.menubar.entryconfig(3, state='normal')
        self.menubar.entryconfig(4, state='normal')
        
    def executeLoad(self, names, keywords, datalist):
    
        '''Gets relevant loaded data and inserts to relevant widgets.'''
    
        frame = self.currentFrame()
    
        datanum = keywords.index(self.varLoadData.get()) # Index of data to load
        
        name = names[datanum]    # Camera name for selected save
        data = datalist[datanum] # Data from selected save
       
        # If image data is from the same camera model
        if name == NAME[self.cnum]:
        
            # If SNR Calculator is the active frame
            if self.snrMode.get():
            
                # Set loaded data in calculator frame
                frame.gain_idx = int(data[0])
                frame.rn_idx = int(data[1])
                frame.varISO.set(ISO[self.cnum][frame.gain_idx])
                frame.varGain.set(GAIN[self.cnum][frame.gain_idx])
                frame.varRN.set(RN[self.cnum][frame.rn_idx])
                frame.varExp.set(data[2])
                frame.varUseDark.set(int(data[3]))
                frame.varDark.set(data[4] if int(data[3]) else '')
                frame.varBGN.set(data[5] if self.isDSLR else '')
                frame.varBGL.set(data[6])
                frame.varTarget.set(data[7])
                
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
                frame.varGain.set(GAIN[self.cnum][frame.gain_idx])
                frame.varRN.set(RN[self.cnum][frame.rn_idx])
                frame.varExp.set(data[2])
                frame.varDF.set(data[9])
                frame.varSF.set(data[10])
                frame.varTF.set(data[11])
                frame.varSubs.set(1)
            
                if int(data[8]):
                    self.setPhotonFluxUnit()
                else:
                    self.setElectronFluxUnit()
            
                frame.dataCalculated = False # Previously calculated data is no longer valid
                frame.updateSensorLabels() # Update sensor info labels in case the ISO has changed
                frame.emptyInfoLabels() # Clear other info labels
                frame.canvasSim.delete('all') # Clear simulated image
                frame.varMessageLabel.set('Image data loaded.' if int(data[3]) else \
                'Note: loaded signal data does not contain a separate value for dark current.')
            
            # If Plotting Tool is the active frame
            else:
                
                # Set loaded data in plot frame
                frame.gain_idx = int(data[0])
                frame.rn_idx = int(data[1])
                frame.varISO.set(ISO[self.cnum][frame.gain_idx])
                frame.varGain.set(GAIN[self.cnum][frame.gain_idx])
                frame.varRN.set(RN[self.cnum][frame.rn_idx])
                frame.varExp.set(data[2])
                frame.varDF.set(data[9])
                frame.varSF.set(data[10])
                frame.varTF.set(data[11])
            
                if int(data[8]):
                    self.setPhotonFluxUnit()
                else:
                    self.setElectronFluxUnit()
                
                frame.ax.cla() # Clear plot
                frame.varMessageLabel.set('Image data loaded.' if int(data[3]) else \
                'Note: loaded signal data does not contain a separate value for dark current.')
        
        # If image data is from another camera model:
        # If Image Simulator or Plotting Tool is the active frame
        elif (not self.snrMode.get()) and int(data[8]) and self.hasQE:
        
            # Set skyglow and target flux
            frame.varSF.set(data[10])
            frame.varTF.set(data[11])
            
            self.setPhotonFluxUnit()
        
            if self.simMode.get():
                frame.dataCalculated = False # Previously calculated data is no longer valid
                frame.emptyInfoLabels() # Clear info labels
                frame.canvasSim.delete('all') # Clear simulated image
            else:
                frame.ax.cla() # Clear plot
            frame.varMessageLabel.set('Image data is from another camera model. Only flux data loaded.')
        
        # If SNR Calculator is the active frame
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
            return None
        
        # Read data file
        lines = file.read().split('\n')
        file.close()
        
        # Show error message if data file is empty
        if len(lines) == 1:
            
            frame.varMessageLabel.set('No image data to manage.')
            
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
        self.menubar.entryconfig(1, state='normal')
        self.menubar.entryconfig(2, state='normal')
        self.menubar.entryconfig(3, state='normal')
        self.menubar.entryconfig(4, state='normal')
    
    def executeManage(self, names, keywords, display_keywords, datafull, delete=True):
    
        '''Deletes selected data, or creates window for renaming selected save.'''
    
        linenum = display_keywords.index(self.varManageData.get()) # Index of relevant data
        
        if delete:
            
            file = open('imagedata.txt', 'w')
            
            # Rewrite the data file without the line containing the data selected for deleting
            
            for i in range(linenum):
                
                    file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
                               % tuple([names[i]] + [keywords[i]] + [datafull[i]]))
                
            if linenum < len(keywords):
                
                for i in range(linenum+1, len(keywords)):
                    
                    file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
                               % tuple([names[i]] + [keywords[i]] + [datafull[i]]))
                      
                        
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
        setupWindow(self.topCamera, 300, 300)
        self.topCamera.focus_force()
        
        labelCamera = ttk.Label(self.topCamera, text='Choose camera:', font=self.medium_font,
                                anchor='center')
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
            for i in range(len(NAME)):
                self.listboxCamera.insert(i, NAME[i])
        elif restrict == 'DSLR':
            for i in range(len(NAME)):
                if TYPE[i] == 'DSLR': self.listboxCamera.insert(i, NAME[i])
        elif restrict == 'CCD':
            for i in range(len(NAME)):
                if TYPE[i] == 'CCD': self.listboxCamera.insert(i, NAME[i])
            
        scrollbarCamera.config(command=self.listboxCamera.yview) # Add scrollbar to listbox
        
        if self.cnum is not None: self.listboxCamera.activate(self.cnum)
        
        self.varSetDefault = tk.IntVar()
        
        frameDefault = ttk.Frame(self.topCamera)
        buttonChange = ttk.Button(self.topCamera, text='OK', command=self.executeChange)
        
        frameDefault.pack(side='top', expand=True)
        buttonChange.pack(side='top', pady=(10*scsy, 25*scsy), expand=True)
        
        labelDefault = ttk.Label(frameDefault, text='Use as default:')
        checkbuttonDefault = tk.Checkbutton(frameDefault, variable=self.varSetDefault)
        
        labelDefault.grid(row=0, column=0)
        checkbuttonDefault.grid(row=0, column=1)
        
        self.cancelled = True
        
        self.wait_window(self.topCamera)
        self.menubar.entryconfig(1, state='normal')
        if not self.anMode.get(): self.menubar.entryconfig(2, state='normal')
        self.menubar.entryconfig(3, state='normal')
        self.menubar.entryconfig(4, state='normal')
            
        return not self.cancelled
       
    def executeChange(self):
    
        '''Configures widgets according to the selected new camera.'''
        
        self.cancelled = False
    
        self.cnum = NAME.index(self.listboxCamera.get('active')) # Get index of new camera
        
        # Sets the new camera name in bottom line in camera data file if "Set as default" is selected
        if self.varSetDefault.get():
            
            file = open('cameradata.txt', 'r')
            lines = file.read().split('\n')
            file.close()
            
            file = open('cameradata.txt', 'w')
            for line in lines[:-1]:
                file.write(line + '\n')
            file.write('Camera: ' + NAME[self.cnum] + ',' + ','.join(lines[-1].split(',')[1:]))
            file.close()
            
        if not self.toolsConfigured:
            self.topCamera.destroy()
            return None
        
        self.isDSLR = TYPE[self.cnum] == 'DSLR' # Set new camera type
        self.hasQE = QE[self.cnum] != 'NA' # Set new QE state
        
        snrframe = self.frames[SNRCalculator]
        simframe = self.frames[ImageSimulator]
        plotframe = self.frames[PlottingTool]
        
        # Reset frames to original states
        snrframe.setDefaultValues()
        snrframe.toggleDarkInputMode()
        if self.tooltipsOn.get():
            createToolTip(snrframe.entryDark, TTDarkNoise if self.isDSLR else TTDarkLevel, self.tt_fs)
        
        simframe.setDefaultValues()
        
        plotframe.setDefaultValues()
        
        # Update widgets
        snrframe.reconfigureNonstaticWidgets()
        simframe.reconfigureNonstaticWidgets()
        plotframe.reconfigureNonstaticWidgets()
        
        plotframe.toggleActiveWidgets(plotframe.plotList[0])
        
        self.topCamera.destroy() # Close change camera window
        self.currentFrame().varMessageLabel.set('Camera changed.')

    def modifyCamParams(self):
    
        '''Creates window with options for modifying camera data.'''
    
        # Read camera data file
        file = open('cameradata.txt', 'r')
        self.lines = file.read().split('\n')
        file.close()
        
        # Store parameter values
        self.currentvalues = self.lines[self.cnum + 1].split(',')
        
        self.gain_idx = 0
        self.rn_idx = 0
    
        self.varParam = tk.StringVar()
        self.varISO = tk.IntVar()
        self.varGain = tk.DoubleVar()
        self.varRN = tk.DoubleVar()
        
        self.varNewParamVal = tk.StringVar()
        self.varCurrentParamVal = tk.StringVar()
        self.varErrorModify = tk.StringVar()
        
        # List of modifyable parameters
        paramlist = ['Gain', 'Read noise', 'Sat. cap.', 'Black level', 'White level', 'QE']
        self.isolist = self.currentvalues[8].split('-') if self.isDSLR else ['0'] # List of ISO values
        self.gainlist = self.currentvalues[2].split('-')                          # List of gain values
        self.rnlist = self.currentvalues[3].split('-')     # List of read noise values
        self.satcaplist = self.currentvalues[4].split('-') # List of saturation capacity values
        self.bllist = self.currentvalues[5].split('-')     # List of black level values
        self.wllist = self.currentvalues[6].split('-')     # List of white level values
        
        self.varParam.set(paramlist[0])
        self.varISO.set(self.isolist[0])
        self.varGain.set(self.gainlist[0])
        self.varRN.set(self.rnlist[0])
        
        self.varNewParamVal.set('')
        self.varCurrentParamVal.set('Current value: ' + self.gainlist[0] + ' e-/ADU')
        
        self.menubar.entryconfig(1, state='disabled')
        self.menubar.entryconfig(2, state='disabled')
        self.menubar.entryconfig(3, state='disabled')
        self.menubar.entryconfig(4, state='disabled')
    
        # Setup window
        self.topModify = tk.Toplevel()
        self.topModify.title('Modify parameters')
        self.addIcon(self.topModify)
        setupWindow(self.topModify, 280, 210)
        self.topModify.focus_force()
        
        frameParam = ttk.Frame(self.topModify)
        
        labelParam = ttk.Label(frameParam, text='Parameter:', anchor='center', width=11)
        optionParam = ttk.OptionMenu(frameParam, self.varParam, None, *paramlist,
                                     command=self.updateParam)
                                     
        self.labelISO = ttk.Label(frameParam, text='ISO:', anchor='center', width=11)
        self.optionISO = ttk.OptionMenu(frameParam, self.varISO, None, *self.isolist,
                                        command=self.updateParamISO)
        
        self.labelGain = ttk.Label(frameParam, text='Gain:', anchor='center', width=11)
        self.optionGain = ttk.OptionMenu(frameParam, self.varGain, None, *self.gainlist,
                                         command=self.updateParamGain)
        
        self.labelRN = ttk.Label(frameParam, text='RN:', anchor='center', width=11)
        self.optionRN = ttk.OptionMenu(frameParam, self.varRN, None, *self.rnlist,
                                       command=self.updateParamRN)
        
        labelCurrent = ttk.Label(self.topModify, textvariable=self.varCurrentParamVal)
        
        labelSet = ttk.Label(self.topModify, text='Input new value:', anchor='center')
        entryNewVal = ttk.Entry(self.topModify, textvariable=self.varNewParamVal,
                                font=self.small_font, background=DEFAULT_BG)
        
        buttonSet = ttk.Button(self.topModify, text='Set value', command=self.setNewParamVal)
        
        errorModify = ttk.Label(self.topModify, textvariable=self.varErrorModify, anchor='center')
        
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
        
        self.wait_window(self.topModify)
        self.menubar.entryconfig(1, state='normal')
        self.menubar.entryconfig(2, state='normal')
        self.menubar.entryconfig(3, state='normal')
        self.menubar.entryconfig(4, state='normal')

    def updateParam(self, selected_param):
    
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
                
            self.varCurrentParamVal.set('Current value: ' + self.gainlist[0] + ' e-/ADU')
            
        elif selected_param == 'Read noise':
        
            if self.isDSLR:
                self.labelISO.grid(row=0, column=1)
                self.optionISO.grid(row=1, column=1)
            elif len(self.rnlist) > 1:
                self.labelRN.grid(row=0, column=1)
                self.optionRN.grid(row=1, column=1)
                
            self.varCurrentParamVal.set('Current value: ' + self.rnlist[0] + ' e-')
            
        elif selected_param == 'Sat. cap.':
        
            if self.isDSLR:
                self.labelISO.grid(row=0, column=1)
                self.optionISO.grid(row=1, column=1)
            elif len(self.gainlist) > 1:
                self.labelGain.grid(row=0, column=1)
                self.optionGain.grid(row=1, column=1)
        
            self.varCurrentParamVal.set('Current value: ' + self.satcaplist[0] + ' e-')
    
        elif selected_param == 'Black level':
        
            if self.isDSLR:
                self.labelISO.grid(row=0, column=1)
                self.optionISO.grid(row=1, column=1)
            elif len(self.gainlist) > 1:
                self.labelGain.grid(row=0, column=1)
                self.optionGain.grid(row=1, column=1)
                
            self.varCurrentParamVal.set('Current value: ' + self.bllist[0] + ' ADU')
        
        elif selected_param == 'White level':
        
            if self.isDSLR:
                self.labelISO.grid(row=0, column=1)
                self.optionISO.grid(row=1, column=1)
            elif len(self.gainlist) > 1:
                self.labelGain.grid(row=0, column=1)
                self.optionGain.grid(row=1, column=1)
        
            self.varCurrentParamVal.set('Current value: ' + self.wllist[0] + ' ADU')
            
        elif selected_param == 'QE':
        
            if self.hasQE:
                self.varCurrentParamVal.set('Current value: ' + self.currentvalues[7])
            else:
                self.varCurrentParamVal.set('No value exists.')
    
    def updateParamISO(self, selected_iso):
    
        '''Update the label showing the current gain or read noise value when a new ISO is selected.'''
    
        # Store index of selected iso
        self.gain_idx = self.isolist.index(selected_iso)
        self.rn_idx = self.gain_idx
        
        if self.varParam.get() == 'Gain':
            self.varCurrentParamVal.set('Current value: ' + self.gainlist[self.gain_idx] + ' e-/ADU')
        elif self.varParam.get() == 'Read noise':
            self.varCurrentParamVal.set('Current value: ' + self.rnlist[self.rn_idx] + ' e-')
        elif self.varParam.get() == 'Sat. cap.':
            self.varCurrentParamVal.set('Current value: ' + self.satcaplist[self.gain_idx] + ' e-')
        elif self.varParam.get() == 'Black level':
            self.varCurrentParamVal.set('Current value: ' + self.bllist[self.gain_idx] + ' ADU')
        elif self.varParam.get() == 'White level':
            self.varCurrentParamVal.set('Current value: ' + self.wllist[self.gain_idx] + ' ADU')
            
    def updateParamGain(self, selected_gain):
    
        '''Update the label showing the current gain value when a new gain is selected.'''
    
        self.gain_idx = self.gainlist.index(selected_gain) # Store index of selected gain
        
        if self.varParam.get() == 'Gain':
            self.varCurrentParamVal.set('Current value: ' + selected_gain + ' e-/ADU')
        elif self.varParam.get() == 'Sat. cap.':
            self.varCurrentParamVal.set('Current value: ' + self.satcaplist[self.gain_idx] + ' e-')
        elif self.varParam.get() == 'Black level':
            self.varCurrentParamVal.set('Current value: ' + self.bllist[self.gain_idx] + ' ADU')
        elif self.varParam.get() == 'White level':
            self.varCurrentParamVal.set('Current value: ' + self.wllist[self.gain_idx] + ' ADU')
        
    def updateParamRN(self, selected_rn):
    
        '''Update the label showing the current read noise value when a new read noise is selected.'''
    
        self.rn_idx = self.rnlist.index(selected_rn) # Store index of selected read noise
        self.varCurrentParamVal.set('Current value: ' + selected_rn + ' e-')
    
    def setNewParamVal(self):
    
        '''Writes new camera data file with the new value of the selected parameter.'''
    
        snrframe = self.frames[SNRCalculator]
        simframe = self.frames[ImageSimulator]
        plotframe = self.frames[PlottingTool]
        
        newval = self.varNewParamVal.get()
        
        # Show error message if the new inputted value is not a number
        try:
            float(newval)
        except ValueError:
            self.varErrorModify.set('Invalid value. Please insert a number.')
            return None
    
        # Write new camera data file
        
        file = open('cameradata.txt', 'w')
        
        idx = self.cnum + 1
        
        file.write(self.lines[0])
        
        for i in range(1, idx):
            file.write('\n' + self.lines[i])
        
        if self.varParam.get() == 'Gain':
        
            self.gainlist[self.gain_idx] = newval
            file.write('\n%s,%s,%s' % (','.join(self.currentvalues[:2]),
                                       '-'.join(self.gainlist),
                                       ','.join(self.currentvalues[3:])))
            GAIN[self.cnum][self.gain_idx] = float(newval)
            self.varCurrentParamVal.set('Current value: ' + newval + ' e-/ADU')
            
        elif self.varParam.get() == 'Read noise':
        
            self.rnlist[self.rn_idx] = newval
            file.write('\n%s,%s,%s' % (','.join(self.currentvalues[:3]),
                                       '-'.join(self.rnlist),
                                       ','.join(self.currentvalues[4:])))
            RN[self.cnum][self.rn_idx] = float(newval)
            self.varCurrentParamVal.set('Current value: ' + newval + ' e-')
            
        elif self.varParam.get() == 'Sat. cap.':
        
            self.satcaplist[self.gain_idx] = newval
            file.write('\n%s,%s,%s' % (','.join(self.currentvalues[:4]),
                                       '-'.join(self.satcaplist),
                                       ','.join(self.currentvalues[5:])))
            SAT_CAP[self.cnum][self.gain_idx] = int(newval)
            self.varCurrentParamVal.set('Current value: ' + newval + ' e-')
        
        elif self.varParam.get() == 'Black level':
            self.bllist[self.gain_idx] = newval
            file.write('\n%s,%s,%s' % (','.join(self.currentvalues[:5]),
                                       '-'.join(self.bllist),
                                       ','.join(self.currentvalues[6:])))
            BLACK_LEVEL[self.cnum][self.gain_idx] = int(newval)
            self.varCurrentParamVal.set('Current value: ' + newval + ' ADU')
            
        elif self.varParam.get() == 'White level':
            
            self.wllist[self.gain_idx] = newval
            file.write('\n%s,%s,%s' % (','.join(self.currentvalues[:6]),
                                       '-'.join(self.wllist),
                                       ','.join(self.currentvalues[7:])))
            WHITE_LEVEL[self.cnum][self.gain_idx] = int(newval)
            self.varCurrentParamVal.set('Current value: ' + newval + ' ADU')
            
        elif self.varParam.get() == 'QE':
        
            file.write('\n%s,%s' % (','.join(self.currentvalues[:7]), newval))
            if self.isDSLR: file.write(',%s' % (','.join(self.currentvalues[8:])))
                
            QE[self.cnum] = float(newval)
            self.varCurrentParamVal.set('Current value: ' + newval)
        
        for i in range((idx + 1), len(self.lines)):
            file.write('\n' + self.lines[i])
            
        file.close()
        
        # Reset all frames in order for the parameter change to take effect

        self.hasQE = QE[self.cnum] != 'NA'
        
        snrframe.setDefaultValues()
        simframe.setDefaultValues()
        plotframe.setDefaultValues()
        
        snrframe.reconfigureNonstaticWidgets()
        simframe.reconfigureNonstaticWidgets()
        plotframe.reconfigureNonstaticWidgets()
        
        self.currentFrame().varMessageLabel.set('Camera parameter modified.')
        
        # Update widgets and attributes in the window with the new parameter value
        self.optionISO.set_menu(*([None] + self.isolist))
        self.optionGain.set_menu(*([None] + self.gainlist))
        self.optionRN.set_menu(*([None] + self.rnlist))
        
        self.varISO.set(self.isolist[self.gain_idx])
        self.varGain.set(self.gainlist[self.gain_idx])
        self.varRN.set(self.rnlist[self.rn_idx])
        
        self.varNewParamVal.set('')
        self.varErrorModify.set('')
        
        file = open('cameradata.txt', 'r')
        self.lines = file.read().split('\n')
        file.close()
        
        self.currentvalues = self.lines[self.cnum + 1].split(',')
        
    def transferToSim(self):
    
        '''Transfer relevant inputted or calculated values to widgets in the Image Simulator frame.'''
    
        snrframe = self.frames[SNRCalculator]
        simframe = self.frames[ImageSimulator]
        plotframe = self.frames[PlottingTool]
        
        # If SNR Calculator is the active frame
        if self.snrMode.get():
        
            # Show error message if flux data hasn't been calculated
            if not snrframe.dataCalculated:
                snrframe.varMessageLabel.set('Data must be calculated before transfering input.')
                return None
        
            # Set values
            simframe.gain_idx = snrframe.gain_idx
            simframe.rn_idx = snrframe.rn_idx
            simframe.varISO.set(ISO[self.cnum][snrframe.gain_idx])
            simframe.varGain.set(GAIN[self.cnum][snrframe.gain_idx])
            simframe.varRN.set(RN[self.cnum][snrframe.rn_idx])
            simframe.varExp.set('%g' % snrframe.exposure)
            simframe.varDF.set('%.3f' % snrframe.df)
            simframe.varSF.set('%.3f' % (snrframe.sf/QE[self.cnum] if self.photonFluxUnit.get() \
                                                                   else snrframe.sf))
            simframe.varTF.set('%.3f' % (snrframe.tf/QE[self.cnum] if self.photonFluxUnit.get() \
                                                                   else snrframe.tf))
            simframe.varSubs.set(1)
            
            simframe.dataCalculated = False # Previously calculated data is no longer valid
            simframe.updateSensorLabels() # Update sensor info labels in case the ISO has changed
            simframe.emptyInfoLabels() # Clear other info labels
            simframe.canvasSim.delete('all') # Clear simulated image
            snrframe.varMessageLabel.set('Input transfered to Image Simulator.' \
                                         if snrframe.varUseDark.get() \
                                         else 'Input transfered. Note that transfered signal ' \
                                       + 'data does not contain a separate value for dark current.')
        
        # If Plotting Tool is the active frame
        elif self.plMode.get():
        
            simframe.setDefaultValues() # Reset Image Simulator frame
        
            # Set values that are not invalid
            
            simframe.gain_idx = plotframe.gain_idx
            simframe.rn_idx = plotframe.rn_idx
            simframe.varISO.set(ISO[self.cnum][plotframe.gain_idx])
            simframe.varGain.set(GAIN[self.cnum][plotframe.gain_idx])
            simframe.varRN.set(RN[self.cnum][plotframe.rn_idx])
            
            
            try:
                simframe.varExp.set('%g' % plotframe.varExp.get())
            except ValueError:
                pass
        
            try:
                simframe.varDF.set('%.3f' % plotframe.varDF.get())
            except ValueError:
                pass
        
            try:
                simframe.varSF.set('%.3f' % plotframe.varSF.get())
            except ValueError:
                pass
            
            try:
                simframe.varTF.set('%.3f' % plotframe.varTF.get())
            except ValueError:
                pass
            
            simframe.varSubs.set(1)
            
            simframe.updateSensorLabels() # Update sensor info labels in case the ISO has changed
            simframe.emptyInfoLabels() # Clear other info labels
            simframe.canvasSim.delete('all') # Clear simulated image
            plotframe.varMessageLabel.set('Input transfered to Image Simulator.')
        
    def transferToPlot(self):
    
        '''Transfer relevant inputted or calculated values to widgets in the Plotting Tool frame.'''
    
        snrframe = self.frames[SNRCalculator]
        simframe = self.frames[ImageSimulator]
        plotframe = self.frames[PlottingTool]
        
        # If SNR Calculator is the active frame
        if self.snrMode.get():
        
            # Show error message if flux data hasn't been calculated
            if not snrframe.dataCalculated:
                snrframe.varMessageLabel.set('Data must be calculated before transfering input.')
                return None
        
            # Set values
            plotframe.gain_idx = snrframe.gain_idx
            plotframe.rn_idx = snrframe.rn_idx
            plotframe.varISO.set(ISO[self.cnum][snrframe.gain_idx])
            plotframe.varGain.set(GAIN[self.cnum][snrframe.gain_idx])
            plotframe.varRN.set(RN[self.cnum][snrframe.rn_idx])
            plotframe.varExp.set('%g' % snrframe.exposure)
            plotframe.varDF.set('%.3f' % snrframe.df)
            plotframe.varSF.set('%.3f' % (snrframe.sf/QE[self.cnum] if self.photonFluxUnit.get() \
                                                                    else snrframe.sf))
            plotframe.varTF.set('%.3f' % (snrframe.tf/QE[self.cnum] if self.photonFluxUnit.get() \
                                                                    else snrframe.tf))
            
            plotframe.ax.cla() # Clear plot
            snrframe.varMessageLabel.set('Input transfered to Plotting Tool.' \
                                         if snrframe.varUseDark.get() \
                                         else 'Input transfered. Note that transfered signal data ' \
                                            + 'does not contain a separate value for dark current.')
        
        # If Plotting Tool is the active frame
        elif self.simMode.get():
        
            plotframe.setDefaultValues() # Reset Plotting Tool frame
        
            # Set values that are not invalid
        
            plotframe.gain_idx = simframe.gain_idx
            plotframe.rn_idx = simframe.rn_idx
            plotframe.varISO.set(ISO[self.cnum][simframe.gain_idx])
            plotframe.varGain.set(GAIN[self.cnum][simframe.gain_idx])
            plotframe.varRN.set(RN[self.cnum][simframe.rn_idx])
            
            try:
                plotframe.varExp.set('%g' % simframe.varExp.get())
            except ValueError:
                pass
        
            try:
                plotframe.varDF.set('%.3f' % simframe.varDF.get())
            except ValueError:
                pass
        
            try:
                plotframe.varSF.set('%.3f' % simframe.varSF.get())
            except ValueError:
                pass
            
            try:
                plotframe.varTF.set('%.3f' % simframe.varTF.get())
            except ValueError:
                pass
            
            plotframe.ax.cla() # Clear plot
            simframe.varMessageLabel.set('Input transfered to Plotting Tool.')
    
    def setElectronFluxUnit(self):
    
        '''Use [e-/s] as unit for flux.'''
    
        # Do nothing if e-/s is already used
        if not self.photonFluxUnit.get():
            self.electronFluxUnit.set(1)
            return None
            
        self.photonFluxUnit.set(0)
        self.electronFluxUnit.set(1)
    
        snrframe = self.frames[SNRCalculator]
        simframe = self.frames[ImageSimulator]
        plotframe = self.frames[PlottingTool]
        
        # Change unit labels
        snrframe.varSFLabel.set('e-/s')
        snrframe.varTFLabel.set('e-/s')
        
        simframe.varSFLabel.set('e-/s')
        simframe.varTFLabel.set('e-/s')
        
        plotframe.varSFLabel.set('e-/s')
        plotframe.varTFLabel.set('e-/s')
        
        # Change tooltips
        if self.tooltipsOn.get():
            createToolTip(snrframe.labelSF2, TTSFElectron if snrframe.varUseDark.get() \
                                             or self.isDSLR else TTDSFElectron, self.tt_fs)
            createToolTip(snrframe.labelTF2, TTTFElectron, self.tt_fs)
            createToolTip(simframe.entrySF, TTSFElectron, self.tt_fs)
            createToolTip(simframe.entryTF, TTTFElectron, self.tt_fs)
            createToolTip(plotframe.entrySF, TTSFElectron, self.tt_fs)
            createToolTip(plotframe.entryTF, TTTFElectron, self.tt_fs)
        
        # Change displayed flux values if they have been calculated
        if snrframe.dataCalculated:
        
            snrframe.varSFInfo.set('%.3g' % (snrframe.sf)) 
            snrframe.varTFInfo.set('%.3g' % (snrframe.tf))
            
        self.currentFrame().varMessageLabel.set('Using e-/s as unit for flux.')
            
    def setPhotonFluxUnit(self):
    
        '''Use [photons/s] as unit for flux.'''
    
        # Do nothing if photons/s is already used
        if not self.electronFluxUnit.get():
            self.photonFluxUnit.set(1)
            return None
            
        if not self.hasQE:
            self.photonFluxUnit.set(0)
            self.currentFrame().varMessageLabel.set('Camera doesn\'t have QE data. Cannot use photons/s.')
            return None
            
        self.photonFluxUnit.set(1)
        self.electronFluxUnit.set(0)
    
        snrframe = self.frames[SNRCalculator]
        simframe = self.frames[ImageSimulator]
        plotframe = self.frames[PlottingTool]
        
        # Change unit labels
        snrframe.varSFLabel.set('photons/s')
        snrframe.varTFLabel.set('photons/s')
        
        simframe.varSFLabel.set('photons/s')
        simframe.varTFLabel.set('photons/s')
        
        plotframe.varSFLabel.set('photons/s')
        plotframe.varTFLabel.set('photons/s')
        
        # Change tooltips
        if self.tooltipsOn.get():
            createToolTip(snrframe.labelSF2, TTSFPhoton if snrframe.varUseDark.get() \
                                             or self.isDSLR else TTDSFPhoton, self.tt_fs)
            createToolTip(snrframe.labelTF2, TTTFPhoton, self.tt_fs)
            createToolTip(simframe.entrySF, TTSFPhoton, self.tt_fs)
            createToolTip(simframe.entryTF, TTTFPhoton, self.tt_fs)
            createToolTip(plotframe.entrySF, TTSFPhoton, self.tt_fs)
            createToolTip(plotframe.entryTF, TTTFPhoton, self.tt_fs)
        
        # Change displayed flux values if they have been calculated
        if snrframe.dataCalculated:
        
            snrframe.varSFInfo.set('%.3g' % (snrframe.sf/QE[self.cnum]))
            snrframe.varTFInfo.set('%.3g' % (snrframe.tf/QE[self.cnum]))
    
        self.currentFrame().varMessageLabel.set('Using photons/s as unit for flux.')

    def addIcon(self, window):
    
        '''Set icon if it exists.'''
    
        try:
            window.iconbitmap('aplab_icon.ico')
        except:
            pass
        
    def currentFrame(self):
    
        '''Returns the class corresponding to the currently active frame.'''
    
        return self.frames[SNRCalculator if self.snrMode.get() \
                                         else (ImageSimulator if self.simMode.get() else PlottingTool)]

    def toggleTooltips(self):
    
        '''Turn tooltips on or off.'''
    
        if self.tooltipsOn.get():
        
            self.frames[SNRCalculator].deactivateTooltips()
            self.frames[ImageSimulator].deactivateTooltips()
            self.frames[PlottingTool].deactivateTooltips()
        
            self.tooltipsOn.set(0)
            
            self.currentFrame().varMessageLabel.set('Tooltips deactivated.')
            
        else:
                                       
            self.frames[SNRCalculator].activateTooltips()
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
    
        topFS = tk.Toplevel()
        topFS.title('Change font size')
        setupWindow(topFS, 150, 130)
        self.addIcon(topFS)
        topFS.focus_force()
        
        labelFS = ttk.Label(topFS, text='Choose font size:', anchor='center')
        optionFS = ttk.OptionMenu(topFS, varFS, None, *fs_vals)
        buttonFS = ttk.Button(topFS, text='OK', command=lambda: setNewFS(self, self.cnum, varFS.get()))
        
        labelFS.pack(side='top', pady=(12*scsy, 0), expand=True)
        optionFS.pack(side='top', pady=12*scsy, expand=True)
        buttonFS.pack(side='top', pady=(0, 12*scsy), expand=True)
    
        if self.anMode.get():
            self.frames[ImageAnalyzer].varMessageLabel.set('Warning: changing font size ' \
                                                            + 'will restart the application.')
                                                            
        self.wait_window(topFS)
        self.menubar.entryconfig(1, state='normal')
        if not self.anMode.get(): self.menubar.entryconfig(2, state='normal')
        self.menubar.entryconfig(3, state='normal')
        self.menubar.entryconfig(4, state='normal')
    
    def clearInput(self):
    
        '''Reset input widgets in the active tool.'''
    
        if self.anMode.get():
        
            self.frames[ImageAnalyzer].clearFiles()
            
        else:
        
            frame = self.currentFrame()
        
            frame.setDefaultValues()
            
            if self.snrMode.get():
                frame.toggleDarkInputMode()
            elif self.plMode.get():
                frame.toggleActiveWidgets(frame.plotList[0])
    
     
class SNRCalculator(ttk.Frame):
    
    def __init__(self, parent, controller):
    
        '''Initialize SNR Calculator frame.'''
    
        ttk.Frame.__init__(self, parent)
        
        self.cont = controller
        small_font = self.cont.small_font
        medium_font = self.cont.medium_font
        large_font = self.cont.large_font
        
        # Define attributes
        
        self.varCamName = tk.StringVar()
        
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
        
        self.varSNRInfo = tk.StringVar()
        self.varDRInfo = tk.StringVar()
        self.varGainInfo = tk.StringVar()
        self.varSatCapInfo = tk.StringVar()
        self.varBLInfo = tk.StringVar()
        self.varWLInfo = tk.StringVar()
        self.varQEInfo = tk.StringVar()
        self.varRNInfo = tk.StringVar()
        self.varSNInfo = tk.StringVar()
        self.varDNInfo = tk.StringVar()
        self.varTBGNInfo = tk.StringVar()
        self.varDFInfo = tk.StringVar()
        self.varSFInfo = tk.StringVar()
        self.varTFInfo = tk.StringVar()
        
        self.varRNLabel = tk.StringVar()
        self.varDNLabel = tk.StringVar()
        self.varSNLabel = tk.StringVar()
        self.varTBGNLabel = tk.StringVar()
        self.varSFLabel = tk.StringVar()
        self.varTFLabel = tk.StringVar()
        
        # Set default attribute values
        
        self.varRNLabel.set('e-')
        self.varDNLabel.set('e-')
        self.varSNLabel.set('e-')
        self.varTBGNLabel.set('e-')
        self.varSFLabel.set('photons/s' if self.cont.hasQE else 'e-/s')
        self.varTFLabel.set('photons/s' if self.cont.hasQE else 'e-/s')
        
        # Define frames
        
        frameHeader = ttk.Frame(self)
        
        frameContent = ttk.Frame(self)
        
        frameLeft = ttk.Frame(frameContent)
        
        frameUpLeft = ttk.Frame(frameLeft)
        frameLowLeft = ttk.Frame(frameLeft, borderwidth=2, relief='groove')
        
        frameRight = ttk.Frame(frameContent)
        
        frameSensor = ttk.Frame(frameRight, borderwidth=2, relief='groove')
        frameNoise = ttk.Frame(frameRight, borderwidth=2, relief='groove')
        frameFlux = ttk.Frame(frameRight, borderwidth=2, relief='groove')
        
        frameMessage = ttk.Frame(self)
        
        # Place frames
        
        frameHeader.pack(side='top', fill='x')
        
        frameContent.pack(side='top', fill='both', expand=True)
        
        frameLeft.pack(side='left', fill='y', padx=(30*scsx, 0), expand=True)
        
        frameUpLeft.pack(side='top', pady=(40*scsy, 0), expand=True)
        frameLowLeft.pack(side='bottom', pady=(0, 30*scsy), expand=True)
        
        frameRight.pack(side='right', fill='both', padx=(0, 30*scsx), expand=True)
        
        frameSensor.pack(side='top', pady=(25*scsy, 0), expand=True)
        frameNoise.pack(side='top', expand=True)
        frameFlux.pack(side='bottom', pady=(0, 25*scsy), expand=True)
        
        frameMessage.pack(side='bottom', fill='x')
        
        # *** Header frame ***
        
        labelHeader = ttk.Label(frameHeader, text='SNR Calculator', font=large_font, anchor='center')
        labelCamName = ttk.Label(frameHeader, textvariable=self.varCamName, anchor='center')
        
        labelHeader.pack(side='top', pady=(10*scsy, 0))
        labelCamName.pack(side='top')
        ttk.Separator(frameHeader, orient='horizontal').pack(side='top', fill='x')
        
        # *** Left frame ***
        
        # Define upper left frame widgets
        
        labelInput = ttk.Label(frameUpLeft, text='Image data', font=medium_font, anchor='center')
        
        self.labelISO = ttk.Label(frameUpLeft, text='ISO:')
        self.optionISO = ttk.OptionMenu(frameUpLeft, self.varISO, None, *ISO[self.cont.cnum],
                                        command=self.updateISO)
                                        
        self.labelGain = ttk.Label(frameUpLeft, text='Gain:')
        self.optionGain = ttk.OptionMenu(frameUpLeft, self.varGain, None, *GAIN[self.cont.cnum],
                                         command=self.updateGain)
        self.labelGain2 = ttk.Label(frameUpLeft, text='e-/ADU')
        
        self.labelRN = ttk.Label(frameUpLeft, text='Read noise:')
        self.optionRN = ttk.OptionMenu(frameUpLeft, self.varRN, None, *RN[self.cont.cnum],
                                       command=self.updateRN)
        self.labelRN2 = ttk.Label(frameUpLeft, text='e-')
        
        self.setDefaultValues()
        
        labelExp = ttk.Label(frameUpLeft, text='Exposure time:')
        self.entryExp = ttk.Entry(frameUpLeft, textvariable=self.varExp, width=9, font=small_font,
                                  background=DEFAULT_BG)
        labelExp2 = ttk.Label(frameUpLeft, text='seconds')
        
        labelToggleDark = ttk.Label(frameUpLeft, text='Use dark frame info:')
        self.checkbuttonToggleDark = tk.Checkbutton(frameUpLeft, variable=self.varUseDark,
                                                    font=small_font, command=self.toggleDarkInputMode)
        labelToggleDark2 = ttk.Label(frameUpLeft, text='', width=9)
        
        self.labelDark = ttk.Label(frameUpLeft, textvariable=self.varDarkLabel)
        self.entryDark = ttk.Entry(frameUpLeft, textvariable=self.varDark, font=small_font,
                                   background=DEFAULT_BG, width=9)
        self.labelDark2 = ttk.Label(frameUpLeft, text='ADU')
        
        self.labelBGN = ttk.Label(frameUpLeft, text='Background noise:')
        self.entryBGN = ttk.Entry(frameUpLeft, textvariable=self.varBGN, font=small_font,
                                  background=DEFAULT_BG, width=9)
        self.labelBGN2 = ttk.Label(frameUpLeft, text='ADU')
        
        labelBGL = ttk.Label(frameUpLeft, text='Background level:')
        self.entryBGL = ttk.Entry(frameUpLeft, textvariable=self.varBGL, font=small_font,
                                  background=DEFAULT_BG, width=9)
        labelBGL2 = ttk.Label(frameUpLeft, text='ADU')
        
        labelTarget = ttk.Label(frameUpLeft, text='Target level:')
        self.entryTarget = ttk.Entry(frameUpLeft, textvariable=self.varTarget, font=small_font,
                                     background=DEFAULT_BG, width=9)
        labelTarget2 = ttk.Label(frameUpLeft, text='ADU')
        
        # Define button widget
        buttonSNR = ttk.Button(frameLeft, text='Calculate SNR', command=self.processInput)
        
        # Define lower left frame widgets
        
        labelSNR = ttk.Label(frameLowLeft, text='Target SNR:')
        self.labelSNR2 = ttk.Label(frameLowLeft, textvariable=self.varSNRInfo, anchor='center', width=5)
        
        labelDR = ttk.Label(frameLowLeft, text='Dynamic range:')
        self.labelDR2 = ttk.Label(frameLowLeft, textvariable=self.varDRInfo, anchor='center', width=5)
        labelDR3 = ttk.Label(frameLowLeft, text='stops')
        
        # Place upper left frame widgets
        
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
        
        # Place button widget
        buttonSNR.pack(side='bottom', pady=(0, 40*scsy), expand=True)
        
        # Place lower left frame widgets
        
        labelSNR.grid(row=0, column=0, sticky='W')
        self.labelSNR2.grid(row=0, column=1)
        
        labelDR.grid(row=1, column=0, sticky='W')
        self.labelDR2.grid(row=1, column=1)
        labelDR3.grid(row=1, column=2, sticky='W')
        
        # Place more widgets according to camera type
        self.reconfigureNonstaticWidgets()
        
        # *** Right frame ***
        
        # Define sensor frame widgets
        
        labelSensor = ttk.Label(frameSensor, text='Sensor info', font=medium_font, anchor='center',
                                width=28)
        labelSensor.grid(row=0, column=0, columnspan=3, pady=5*scsy)
        
        labelGainI = ttk.Label(frameSensor, text='Gain: ')
        self.labelGainI2 = ttk.Label(frameSensor, textvariable=self.varGainInfo, anchor='center', width=7)
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
        
        labelQE = ttk.Label(frameSensor, text='Quantum efficiency: ')
        self.labelQE2 = ttk.Label(frameSensor, textvariable=self.varQEInfo, anchor='center', width=7)
        labelQE3 = ttk.Label(frameSensor, text='%')
        
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
        
        # Define flux frame widgets
        
        labelFlux = ttk.Label(frameFlux, text='Signal', font=medium_font, anchor='center', width=28)
        labelFlux.grid(row=0, column=0, columnspan=3, pady=5*scsy)
        
        self.labelDF = ttk.Label(frameFlux, text='Dark current: ')
        self.labelDF2 = ttk.Label(frameFlux, textvariable=self.varDFInfo, anchor='center', width=6)
        self.labelDF3 = ttk.Label(frameFlux, text='e-/s')
        
        labelSF = ttk.Label(frameFlux, textvariable=self.varSFTypeLabel)
        self.labelSF2 = ttk.Label(frameFlux, textvariable=self.varSFInfo, anchor='center', width=6)
        labelSF3 = ttk.Label(frameFlux, textvariable=self.varSFLabel, font=small_font)
        
        labelTF = ttk.Label(frameFlux, text='Target flux: ')
        self.labelTF2 = ttk.Label(frameFlux, textvariable=self.varTFInfo, anchor='center', width=6)
        labelTF3 = ttk.Label(frameFlux, textvariable=self.varTFLabel)
        
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
        
        labelQE.grid(row=6, column=0, sticky='W')
        self.labelQE2.grid(row=6, column=1)
        labelQE3.grid(row=6, column=2, sticky='W')
        
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
        
        # Place flux frame widgets
        
        self.labelDF.grid(row=1, column=0, sticky='W')
        self.labelDF2.grid(row=1, column=1)
        self.labelDF3.grid(row=1, column=2, sticky='W')
        
        labelSF.grid(row=2, column=0, sticky='W')
        self.labelSF2.grid(row=2, column=1)
        labelSF3.grid(row=2, column=2, sticky='W')
        
        labelTF.grid(row=3, column=0, sticky='W')
        self.labelTF2.grid(row=3, column=1)
        labelTF3.grid(row=3, column=2, sticky='W')
        
        # *** Message frame ***
        labelMessage = ttk.Label(frameMessage, textvariable=self.varMessageLabel, anchor='center')
        ttk.Separator(frameMessage, orient='horizontal').pack(side='top', fill='x')
        labelMessage.pack(side='top', fill='both')
        
        if self.cont.tooltipsOn.get(): self.activateTooltips()

    def emptyInfoLabels(self):
    
        '''Clear labels showing calculated values.'''
    
        self.varSNRInfo.set('-')
        self.varDRInfo.set('-')
        self.varSNInfo.set('-')
        self.varDNInfo.set('-')
        self.varTBGNInfo.set('-')
        self.varDFInfo.set('-')
        self.varSFInfo.set('-')
        self.varTFInfo.set('-')
        
    def setDefaultValues(self):
    
        '''Set all relevant class attributes to their default values.'''
        
        # Variables to keep track of currently selected ISO, gain or read noise in the optionmenus
        self.gain_idx = 0
        self.rn_idx = 0
        
        self.dataCalculated = False # Used to indicate if calculated data exists
        
        # Default widget values
        self.varCamName.set('Camera: ' + NAME[self.cont.cnum])
        
        self.varISO.set(ISO[self.cont.cnum][self.gain_idx])
        self.varGain.set(GAIN[self.cont.cnum][self.gain_idx])
        self.varRN.set(RN[self.cont.cnum][self.rn_idx])
        self.varExp.set('')
        self.varUseDark.set(1)
        self.varDark.set('')
        self.varBGN.set('')
        self.varBGL.set('')
        self.varTarget.set('')
        
        self.varDarkLabel.set('Dark frame noise:' if self.cont.isDSLR else 'Dark frame level:')
        self.varSNTypeLabel.set('Skyglow noise: ')
        self.varSFTypeLabel.set('Skyglow flux: ')
        self.varMessageLabel.set('')
        
        self.varGainInfo.set('%.3g' % self.varGain.get())
        self.varSatCapInfo.set('%d' % SAT_CAP[self.cont.cnum][self.gain_idx])
        self.varBLInfo.set('%d' % BLACK_LEVEL[self.cont.cnum][self.gain_idx])
        self.varWLInfo.set('%d' % WHITE_LEVEL[self.cont.cnum][self.gain_idx])
        self.varQEInfo.set('-' if not self.cont.hasQE else ('%d' % (QE[self.cont.cnum]*100)))
        self.varRNInfo.set('%.1f' % self.varRN.get())
        
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
        self.optionGain.set_menu(*([None] + list(GAIN[self.cont.cnum])))
        self.optionRN.set_menu(*([None] + list(RN[self.cont.cnum])))
            
        if self.cont.isDSLR:
                
            # DSLRs use the ISO optionmenu and the background noise entry
                
            self.labelISO.grid(row=1, column=0, sticky='W')
            self.optionISO.grid(row=1, column=1)
            
            self.labelBGN.grid(row=6, column=0, sticky='W')
            self.entryBGN.grid(row=6, column=1)
            self.labelBGN2.grid(row=6, column=2, sticky='W')
                
        else:
                
            # CCDs use gain and/or read noise optionmenus if they have more than one value to use
                
            if len(GAIN[self.cont.cnum]) > 1:
                    
                self.labelGain.grid(row=1, column=0, sticky='W')
                self.optionGain.grid(row=1, column=1)
                self.labelGain2.grid(row=1, column=2, sticky='W')
                    
            if len(RN[self.cont.cnum]) > 1:
                    
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
    
        self.gain_idx = int(np.where(GAIN[self.cont.cnum] == selected_gain)[0])
        
        self.updateSensorLabels()
    
    def updateRN(self, selected_rn):
            
        '''Update index of selected ISO and update sensor labels.'''
        
        self.rn_idx = int(np.where(RN[self.cont.cnum] == selected_rn)[0])
        
        self.updateSensorLabels()
    
    def updateSensorLabels(self):
    
        '''
        Update labels with the gain, read noise and saturation
        level values of currently selected ISO/gain/RN.
        '''
    
        self.varGainInfo.set('%.3g' % GAIN[self.cont.cnum][self.gain_idx])
        self.varRNInfo.set('%.1f' % RN[self.cont.cnum][self.rn_idx])
        self.varSatCapInfo.set('%d' % SAT_CAP[self.cont.cnum][self.gain_idx])
        self.varBLInfo.set('%d' % BLACK_LEVEL[self.cont.cnum][self.gain_idx])
        self.varWLInfo.set('%d' % WHITE_LEVEL[self.cont.cnum][self.gain_idx])
    
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
            self.varSNTypeLabel.set('Skyglow noise: ')
            self.varSFTypeLabel.set('Skyglow flux: ')
            
            # Change tooltips
            if self.cont.tooltipsOn.get():
                createToolTip(self.labelSN2, TTSN, self.cont.tt_fs)
                createToolTip(self.labelSF2, TTSFPhoton if self.cont.photonFluxUnit.get() else TTSFElectron,
                              self.cont.tt_fs)
            
        else:
        
            # Dark input, noise and current widgets remain hidden
            
            # Change labels for skyglow noise/flux
            self.varSNTypeLabel.set('Skyglow and dark noise: ')
            
            if self.cont.tooltipsOn.get(): createToolTip(self.labelSN2, TTDSN, self.cont.tt_fs)
            
            if not self.cont.isDSLR:
            
                self.varSFTypeLabel.set('Background flux: ')
                
                if self.cont.tooltipsOn.get():
                    createToolTip(self.labelSF2, TTDSFPhoton if self.cont.photonFluxUnit.get() else TTDSFElectron,
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
            self.varMessageLabel.set('Invalid input for target level.')
            self.emptyInfoLabels()
            return None
        
        if self.cont.isDSLR:
        
            if self.bgl < BLACK_LEVEL[self.cont.cnum][self.gain_idx]:
                self.varMessageLabel.set('The background level cannot be lower than the black level.')
                self.emptyInfoLabels()
                return None
                
        elif self.use_dark:
        
            if self.dark_input < BLACK_LEVEL[self.cont.cnum][self.gain_idx]:
                self.varMessageLabel.set('The dark frame level cannot be lower than the black level.')
                self.emptyInfoLabels()
                return None
                
            if self.bgl < self.dark_input:
                self.varMessageLabel.set('The background level cannot be lower than the dark frame level.')
                self.emptyInfoLabels()
                return None
            
        if self.target < self.bgl:
            self.varMessageLabel.set('The target level cannot be lower than the background level.')
            self.emptyInfoLabels()
            return None
        
        if self.target > WHITE_LEVEL[self.cont.cnum][self.gain_idx]:
            self.varMessageLabel.set('The target level cannot be higher than the white level.')
            self.emptyInfoLabels()
            return None
        
        self.calculate()
    
    def calculate(self):
    
        '''Calculate SNR, dynamic range, noise and flux values and set to the corresponding labels.'''
        
        gain = GAIN[self.cont.cnum][self.gain_idx] # Gain [e-/ADU]
        rn = RN[self.cont.cnum][self.rn_idx]       # Read noise [e-]
        
        # For DSLRs
        if self.cont.isDSLR:
            
            if self.use_dark:
            
                dark_signal_e = (self.dark_input*gain)**2 - rn**2 # Signal from dark current [e-]
                
                # Show error if the provided dark frame noise (for DSLRs) is lower than the read noise
                if dark_signal_e < 0:
                    self.varMessageLabel.set(\
                    'Dark frame noise cannot be lower than the read noise. Using lowest possible value.')
                    self.varDark.set('%.2f' % (rn/gain))
                    dark_signal_e = 0
                    
            else:
                dark_signal_e = 0 # Set to 0 if dark frame noise is not provided
            
            sky_signal_e = (self.bgl - BLACK_LEVEL[self.cont.cnum][self.gain_idx])*gain # Signal from skyglow [e-]
            target_signal_e = (self.target - self.bgl)*gain              # Signal from target [e-]
        
            sat_cap = SAT_CAP[self.cont.cnum][self.gain_idx] # Saturation capacity [e-]
                
            tbgn = self.bgn*gain                          # Total background noise [e-]
            dn = np.sqrt(dark_signal_e)                   # Dark noise [e-]
            sn = np.sqrt(tbgn**2 - rn**2 - dark_signal_e) # Skyglow noise [e-]
     
            self.df = dark_signal_e/self.exposure   # Dark current [e-/s]
            self.sf = sky_signal_e/self.exposure    # Skyglow flux [e-/s]
            self.tf = target_signal_e/self.exposure # Target flux [e-/s]
        
        # For CCDs
        else:
            
            if self.use_dark:
                # Signal from dark current [e-]
                dark_signal_e = (self.dark_input - BLACK_LEVEL[self.cont.cnum][self.gain_idx])*gain
                sky_signal_e = (self.bgl - self.dark_input)*gain # Signal from skyglow [e-]
            else:
                dark_signal_e = 0 # Set to 0 if dark frame level is not provided
                sky_signal_e = (self.bgl - BLACK_LEVEL[self.cont.cnum][self.gain_idx])*gain
                
            target_signal_e = (self.target - self.bgl)*gain  # Signal from target [e-]
                
            sat_cap = SAT_CAP[self.cont.cnum][self.gain_idx] # Saturation capacity [e-]
                
            dn = np.sqrt(dark_signal_e)                          # Dark noise [e-]
            sn = np.sqrt(sky_signal_e)                           # Skyglow noise [e-]
            tbgn = np.sqrt(rn**2 + dark_signal_e + sky_signal_e) # Total background noise [e-]
                
            self.df = dark_signal_e/self.exposure   # Dark current [e-/s]
            self.sf = sky_signal_e/self.exposure    # Skyglow flux [e-/s]
            self.tf = target_signal_e/self.exposure # Target flux [e-/s]
            
        snr = target_signal_e/np.sqrt(target_signal_e + tbgn**2) # Signal to noise ratio
        dr = np.log10(sat_cap/tbgn)/np.log10(2.0)                # Dynamic range [stops]
              
        # Update labels
        self.varSNRInfo.set('%.1f' % snr)
        self.varDRInfo.set('%.1f' % dr)
        self.varSNInfo.set('%.1f' % sn)
        self.varDNInfo.set('%.1f' % dn)
        self.varTBGNInfo.set('%.1f' % tbgn)
        self.varDFInfo.set('%.3g' % self.df)
        self.varSFInfo.set('%.3g' % (self.sf/QE[self.cont.cnum] if self.cont.photonFluxUnit.get() else self.sf))
        self.varTFInfo.set('%.3g' % (self.tf/QE[self.cont.cnum] if self.cont.photonFluxUnit.get() else self.tf))
        
        self.dataCalculated = True
        
        self.varMessageLabel.set('SNR calculated.')
 
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
        createToolTip(self.labelGainI2, TTGain, self.cont.tt_fs)
        createToolTip(self.labelSatCap2, TTSatCap, self.cont.tt_fs)
        createToolTip(self.labelBL2, TTBL, self.cont.tt_fs)
        createToolTip(self.labelWL2, TTWL, self.cont.tt_fs)
        createToolTip(self.labelQE2, TTQE, self.cont.tt_fs)
        createToolTip(self.labelRNI2, TTRN, self.cont.tt_fs)
        createToolTip(self.labelDN2, TTDN, self.cont.tt_fs)
        createToolTip(self.labelSN2, TTSN, self.cont.tt_fs)
        createToolTip(self.labelTBGN2, TTTotN, self.cont.tt_fs)
        createToolTip(self.labelDF2, TTDF, self.cont.tt_fs)
        createToolTip(self.labelSF2, TTSFPhoton if self.cont.hasQE else TTSFElectron, self.cont.tt_fs)
        createToolTip(self.labelTF2, TTTFPhoton if self.cont.hasQE else TTTFElectron, self.cont.tt_fs)
 
    def deactivateTooltips(self):
    
        '''Remove tooltips from all widgets.'''
    
        for widget in [self.entryExp, self.checkbuttonToggleDark, self.entryDark, self.entryBGN,
                       self.entryBGL, self.entryTarget, self.labelSNR2, self.labelDR2,
                       self.labelGainI2, self.labelSatCap2, self.labelBL2,
                       self.labelWL2, self.labelQE2, self.labelRNI2, self.labelDN2, self.labelSN2,
                       self.labelTBGN2, self.labelDF2, self.labelSF2, self.labelTF2]:
                           
            widget.unbind('<Enter>')
            widget.unbind('<Motion>')
            widget.unbind('<Leave>')
                           
          
class ImageSimulator(ttk.Frame):
    
    def __init__(self, parent, controller):
    
        '''Initialize Image Simulator frame.'''
    
        ttk.Frame.__init__(self, parent)
        
        self.cont = controller
        small_font = self.cont.small_font
        medium_font = self.cont.medium_font
        large_font = self.cont.large_font
        
        # Define attributes
        
        self.varCamName = tk.StringVar()
        
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
        self.varQEInfo = tk.StringVar()
        self.varRNInfo = tk.StringVar()
        self.varSNInfo = tk.StringVar()
        self.varDNInfo = tk.StringVar()
        self.varTBGNInfo = tk.StringVar()
        
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
        
        frameUpLeft = ttk.Frame(frameLeft)
        frameMiddleLeft = ttk.Frame(frameLeft)
        frameLowLeft = ttk.Frame(frameLeft, borderwidth=2, relief='groove')
        
        frameMiddle = ttk.Frame(frameContent)
        
        frameRight = ttk.Frame(frameContent)
        
        frameSensor = ttk.Frame(frameRight, borderwidth=2, relief='groove')
        frameNoise = ttk.Frame(frameRight, borderwidth=2, relief='groove')
        
        frameMessage = ttk.Frame(self)
        
        # Setup canvas
        self.canvasSim = tk.Canvas(frameMiddle, width=round(320*scsy), height=round(320*scsy),
                                   bg='white', bd=2, relief='groove')
            
        # Read demonstration image
        self.img_orig = matplotlib.image.imread('sim_orig_image.png')
        
        # Set default attribute values
        
        self.varRNLabel.set('e-')
        self.varDNLabel.set('e-')
        self.varSNLabel.set('e-')
        self.varTBGNLabel.set('e-')
        self.varSFLabel.set('photons/s' if self.cont.hasQE else 'e-/s')
        self.varTFLabel.set('photons/s' if self.cont.hasQE else 'e-/s')
        
        self.setDefaultValues()
        
        # Place frames
        
        frameHeader.pack(side='top', fill='x')
        
        frameContent.pack(side='top', fill='both', expand=True)
        
        frameLeft.pack(side='left', fill='both', padx=(30*scsx, 0), expand=True)
        
        frameUpLeft.pack(side='top', pady=(30*scsy, 0), expand=True)
        frameLowLeft.pack(side='bottom', pady=(0, 35*scsy), expand=True)
        frameMiddleLeft.pack(side='bottom', pady=(10*scsy, 15*scsy), expand=True)
        
        frameMiddle.pack(side='left', expand=True)
        
        frameRight.pack(side='right', fill='both', padx=(0, 30*scsx), expand=True)
        
        frameSensor.pack(side='top', pady=(25*scsy, 0), expand=True)
        frameNoise.pack(side='bottom', pady=(0, 15*scsy), expand=True)
        
        frameMessage.pack(side='bottom', fill='x')
        
        # *** Header frame ***
        
        labelHeader = ttk.Label(frameHeader, text='Image Simulator', font=large_font, anchor='center')
        labelCamName = ttk.Label(frameHeader, textvariable=self.varCamName, anchor='center')
        
        labelHeader.pack(side='top', fill='both', pady=(10*scsy, 0))
        labelCamName.pack(side='top', fill='both')
        ttk.Separator(frameHeader, orient='horizontal').pack(side='top', fill='x')
        
        # *** Left frame ***
        
        # Define upper left frame widgets
        
        labelInput = ttk.Label(frameUpLeft, text='Imaging parameters', font=medium_font, anchor='center')
        
        self.labelISO = ttk.Label(frameUpLeft, text='ISO:')
        self.optionISO = ttk.OptionMenu(frameUpLeft, self.varISO, None, *ISO[self.cont.cnum],
                                        command=self.updateISO)
        
        self.labelGain = ttk.Label(frameUpLeft, text='Gain:')
        self.optionGain = ttk.OptionMenu(frameUpLeft, self.varGain, None, *GAIN[self.cont.cnum],
                                         command=self.updateGain)
        self.labelGain2 = ttk.Label(frameUpLeft, text='e-/ADU')
        
        self.labelRN = ttk.Label(frameUpLeft, text='Read noise:')
        self.optionRN = ttk.OptionMenu(frameUpLeft, self.varRN, None, *RN[self.cont.cnum],
                                       command=self.updateRN)
        self.labelRN2 = ttk.Label(frameUpLeft, text='e-')
        
        labelExp = ttk.Label(frameUpLeft, text='Exposure time:')
        self.entryExp = ttk.Entry(frameUpLeft, textvariable=self.varExp, font=small_font,
                                  background=DEFAULT_BG, width=9)
        labelExp2 = ttk.Label(frameUpLeft, text='seconds')
        
        labelDF = ttk.Label(frameUpLeft, text='Dark current:')
        self.entryDF = ttk.Entry(frameUpLeft, textvariable=self.varDF, font=small_font,
                                 background=DEFAULT_BG, width=9)
        labelDF2 = ttk.Label(frameUpLeft, text='e-/s')
        
        labelSF = ttk.Label(frameUpLeft, text='Skyglow flux:')
        self.entrySF = ttk.Entry(frameUpLeft, textvariable=self.varSF, font=small_font,
                                 background=DEFAULT_BG, width=9)
        labelSF2 = ttk.Label(frameUpLeft, textvariable=self.varSFLabel)
        
        labelTF = ttk.Label(frameUpLeft, text='Target flux:')
        self.entryTF = ttk.Entry(frameUpLeft, textvariable=self.varTF, font=small_font,
                                 background=DEFAULT_BG, width=9)
        labelTF2 = ttk.Label(frameUpLeft, textvariable=self.varTFLabel)
        
        labelSubs = ttk.Label(frameUpLeft, text='Number of subframes:')
        self.entrySubs = ttk.Entry(frameUpLeft, textvariable=self.varSubs, font=small_font,
                                   background=DEFAULT_BG, width=9)
        labelSubs2 = ttk.Label(frameUpLeft, text='', width=9)
        
        # Define middle left frame widgets
        
        buttonSNR = ttk.Button(frameMiddleLeft, text='Calculate SNR', command=self.processInput)
        buttonSim = ttk.Button(frameMiddleLeft, text='Simulate image', command=self.simulateController)
        
        frameStretch = ttk.Frame(frameMiddleLeft)
        
        labelStretch = ttk.Label(frameStretch, text='Stretch:')
        self.checkbuttonStretch = tk.Checkbutton(frameStretch, variable=self.varStretch,
                                                 command=lambda: self.simulateController(fromCheckbutton=True))
        
        # Define lower left frame widgets
        
        labelSNR = ttk.Label(frameLowLeft, text='Target SNR:')
        self.labelSNR2 = ttk.Label(frameLowLeft, textvariable=self.varSNRInfo, anchor='center', width=5)
        
        labelStackSNR = ttk.Label(frameLowLeft, text='Stack SNR')
        self.labelStackSNR2 = ttk.Label(frameLowLeft, textvariable=self.varStackSNRInfo, anchor='center',
                                        width=5)
        
        labelDR = ttk.Label(frameLowLeft, text='Dynamic range:')
        self.labelDR2 = ttk.Label(frameLowLeft, textvariable=self.varDRInfo, anchor='center', width=5)
        labelDR3 = ttk.Label(frameLowLeft, text='stops')
        
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
        
        # Place middle left frame widgets
            
        buttonSNR.grid(row=0, column=0)
        ttk.Label(frameMiddleLeft, text='', width=2).grid(row=0, column=1)
        buttonSim.grid(row=0, column=2)
        
        frameStretch.grid(row=1, column=2)
        
        labelStretch.pack(side='left')
        self.checkbuttonStretch.pack(side='left')
        
        # Place lower left frame widgets
        
        labelSNR.grid(row=0, column=0, sticky='W')
        self.labelSNR2.grid(row=0, column=1)
        
        labelStackSNR.grid(row=1, column=0, sticky='W')
        self.labelStackSNR2.grid(row=1, column=1)
        
        labelDR.grid(row=2, column=0, sticky='W')
        self.labelDR2.grid(row=2, column=1)
        labelDR3.grid(row=2, column=2, sticky='W')
        
        # Place more widgets according to camera type
        self.reconfigureNonstaticWidgets()
        
        # *** Middle frame ***
        
        labelSimHeader = ttk.Label(frameMiddle, text='Simulated image', font=medium_font, anchor='center')
        
        labelSimHeader.pack(side='top')
        self.canvasSim.pack(side='top')
        
        # *** Right frame ***
        
        # Define sensor frame widgets
        
        labelSensor = ttk.Label(frameSensor, text='Sensor info', font=medium_font, anchor='center',
                                width=28)
        labelSensor.grid(row=0, column=0, columnspan=3, pady=5*scsy)
        
        labelGainI = ttk.Label(frameSensor, text='Gain: ')
        self.labelGainI2 = ttk.Label(frameSensor, textvariable=self.varGainInfo, anchor='center', width=7)
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
        
        labelQE = ttk.Label(frameSensor, text='Quantum efficiency:')
        self.labelQE2 = ttk.Label(frameSensor, textvariable=self.varQEInfo, anchor='center', width=7)
        labelQE3 = ttk.Label(frameSensor, text='%')
        
        # Define noise frame widgets
        
        labelNoise = ttk.Label(frameNoise, text='Noise', font=medium_font, anchor='center', width=26)
        labelNoise.grid(row=0, column=0, columnspan=3, pady=5*scsy)
        
        labelRNI = ttk.Label(frameNoise, text='Read noise: ')
        self.labelRNI2 = ttk.Label(frameNoise, textvariable=self.varRNInfo, anchor='center', width=5)
        labelRNI3 = ttk.Label(frameNoise, textvariable=self.varRNLabel)
        
        labelDN = ttk.Label(frameNoise, text='Dark noise: ')
        self.labelDN2 = ttk.Label(frameNoise, textvariable=self.varDNInfo, anchor='center', width=5)
        labelDN3 = ttk.Label(frameNoise, textvariable=self.varDNLabel)
        
        labelSN = ttk.Label(frameNoise, text='Skyglow noise: ')
        self.labelSN2 = ttk.Label(frameNoise, textvariable=self.varSNInfo, anchor='center', width=5)
        labelSN3 = ttk.Label(frameNoise, textvariable=self.varSNLabel)
        
        labelTBGN = ttk.Label(frameNoise, text='Total background noise: ')
        self.labelTBGN2 = ttk.Label(frameNoise, textvariable=self.varTBGNInfo, anchor='center', width=5)
        labelTBGN3 = ttk.Label(frameNoise, textvariable=self.varTBGNLabel)
        
        # # Place sensor frame widgets
        
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
        
        labelQE.grid(row=6, column=0, sticky='W')
        self.labelQE2.grid(row=6, column=1)
        labelQE3.grid(row=6, column=2, sticky='W')
        
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
        
        # *** Message frame ***
        
        self.labelMessage = ttk.Label(frameMessage, textvariable=self.varMessageLabel, anchor='center')
        
        ttk.Separator(frameMessage, orient='horizontal').pack(side='top', fill='x')
        self.labelMessage.pack(side='top', fill='both')
        
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
        
        self.varCamName.set('Camera: ' + NAME[self.cont.cnum])
        
        self.varISO.set(ISO[self.cont.cnum][self.gain_idx])
        self.varGain.set(GAIN[self.cont.cnum][self.gain_idx])
        self.varRN.set(RN[self.cont.cnum][self.rn_idx])
        self.varExp.set('')
        self.varDF.set('')
        self.varSF.set('')
        self.varTF.set('')
        self.varSubs.set(1)
        self.varStretch.set(0)
        
        self.varGainInfo.set('%.3g' % self.varGain.get())
        self.varSatCapInfo.set('%d' % SAT_CAP[self.cont.cnum][self.gain_idx])
        self.varBLInfo.set('%d' % BLACK_LEVEL[self.cont.cnum][self.gain_idx])
        self.varWLInfo.set('%d' % WHITE_LEVEL[self.cont.cnum][self.gain_idx])
        self.varQEInfo.set('-' if not self.cont.hasQE else ('%d' % (QE[self.cont.cnum]*100)))
        self.varRNInfo.set('%.1f' % self.varRN.get())
        self.varMessageLabel.set('')
        
        self.canvasSim.delete('all') # Clear plot
        
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
        self.optionGain.set_menu(*([None] + list(GAIN[self.cont.cnum])))
        self.optionRN.set_menu(*([None] + list(RN[self.cont.cnum])))
            
        if self.cont.isDSLR:
        
            # DSLRs use the ISO optionmenu
            self.labelISO.grid(row=1, column=0, sticky='W')
            self.optionISO.grid(row=1, column=1)
                
        else:
        
            # CCDs use gain and/or read noise optionmenus if they have more than one value to use
                
            if len(GAIN[self.cont.cnum]) > 1:
                    
                self.labelGain.grid(row=1, column=0, sticky='W')
                self.optionGain.grid(row=1, column=1)
                self.labelGain2.grid(row=1, column=2, sticky='W')
                    
            if len(RN[self.cont.cnum]) > 1:
                    
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
    
        self.gain_idx = int(np.where(GAIN[self.cont.cnum] == selected_gain)[0])
        
        self.updateSensorLabels()
    
    def updateRN(self, selected_rn):
            
        '''Update index of selected ISO and update sensor labels.'''
            
        self.rn_idx = int(np.where(RN[self.cont.cnum] == selected_rn)[0])
        
        self.updateSensorLabels()
    
    def updateSensorLabels(self):
    
        '''
        Update labels with the gain, read noise and saturation
        level values of currently selected ISO/gain/RN.
        '''
    
        self.varGainInfo.set('%.3g' % GAIN[self.cont.cnum][self.gain_idx])
        self.varRNInfo.set('%.1f' % RN[self.cont.cnum][self.rn_idx])
        self.varSatCapInfo.set('%d' % SAT_CAP[self.cont.cnum][self.gain_idx])
        self.varBLInfo.set('%d' % BLACK_LEVEL[self.cont.cnum][self.gain_idx])
        self.varWLInfo.set('%d' % WHITE_LEVEL[self.cont.cnum][self.gain_idx])
    
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
            self.sf = (self.varSF.get()*QE[self.cont.cnum] if self.cont.photonFluxUnit.get() else self.varSF.get())
            
        except ValueError:
            self.varMessageLabel.set('Invalid input for sky flux.')
            self.emptyInfoLabels()
            return None
            
        try:
            self.tf = (self.varTF.get()*QE[self.cont.cnum] if self.cont.photonFluxUnit.get() else self.varTF.get())
            
        except ValueError:
            self.varMessageLabel.set('Invalid input for target flux.')
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
        
        gain = GAIN[self.cont.cnum][self.gain_idx] # Gain [e-/ADU]
        rn = RN[self.cont.cnum][self.rn_idx]       # Read noise [e-]
        
        dark_signal_e = self.df*self.exposure   # Signal from dark current [e-]
        sky_signal_e = self.sf*self.exposure    # Signal from skyglow flux [e-]
        target_signal_e = self.tf*self.exposure # Signal from target flux [e-]
        
        sat_cap = SAT_CAP[self.cont.cnum][self.gain_idx] # Saturation capacity [e-]
        
        dn = np.sqrt(dark_signal_e)                          # Dark noise [e-]
        sn = np.sqrt(sky_signal_e)                           # Skyglow noise [e-]
        tbgn = np.sqrt(rn**2 + dark_signal_e + sky_signal_e) # Total background noise [e-]
        
        snr = target_signal_e/np.sqrt(target_signal_e + tbgn**2) # Signal to noise ratio in subframe
        stack_snr = snr*np.sqrt(self.subs)        # Signal to noise ratio in stacked frame
        dr = np.log10(sat_cap/tbgn)/np.log10(2.0) # Dynamic range [stops]
        
        # Update labels
        self.varSNRInfo.set('%.1f' % snr)
        self.varStackSNRInfo.set('%.1f' % stack_snr)
        self.varDRInfo.set('%.1f' % dr)
        self.varDNInfo.set('%.1f' % dn)
        self.varSNInfo.set('%.1f' % sn)
        self.varTBGNInfo.set('%.1f' % tbgn)
        
        self.dataCalculated = True
        
        self.varMessageLabel.set('SNR calculated.')
    
    def simulateController(self, fromCheckbutton=False):
    
        '''Changes the dispayed simulated image according ta various conditions.'''
    
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
    
        gain = float(GAIN[self.cont.cnum][self.gain_idx]) # Gain [e-/ADU]
        rn = RN[self.cont.cnum][self.rn_idx] # Read noise [e-]
    
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
        bias = BLACK_LEVEL[self.cont.cnum][self.gain_idx] + (np.random.normal(0, rn, imsize).astype(int))/gain
        
        # Combine signals to get final images
        img = bias + dark + sky
        for i in range(self.subs):
            img[:, :, i][map] += target[:, :, i][map]*self.img_orig[map]
        
        # Truncate invalid pixel values
        img[np.where(img < 0.0)] = 0.0
        img[np.where(img > WHITE_LEVEL[self.cont.cnum][self.gain_idx])] = WHITE_LEVEL[self.cont.cnum][self.gain_idx]
        
        # Take mean of images to get a stacked image
        img = np.mean(img, axis=2)
        
        # Scale pixel values to be between 0 and 1, with 1 corresponding to the saturation capacity
        img = img/WHITE_LEVEL[self.cont.cnum][self.gain_idx]
        
        # Save linear and nonlinear version of the simulated image
        plt.imsave('sim.jpg', img, cmap=plt.get_cmap('gray'), vmin = 0.0, vmax = 1.0)
        plt.imsave('sim_str.jpg', img, cmap=plt.get_cmap('gray'))
        
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
        createToolTip(self.entrySF, TTSFPhoton if self.cont.hasQE else TTSFElectron, self.cont.tt_fs)
        createToolTip(self.entryTF, TTTFPhoton if self.cont.hasQE else TTTFElectron, self.cont.tt_fs)
        createToolTip(self.entrySubs, TTSubs, self.cont.tt_fs)
        createToolTip(self.labelSNR2, TTSNR, self.cont.tt_fs)
        createToolTip(self.labelStackSNR2, TTStackSNR, self.cont.tt_fs)
        createToolTip(self.labelDR2, TTDR, self.cont.tt_fs)
        createToolTip(self.labelGainI2, TTGain, self.cont.tt_fs)
        createToolTip(self.labelSatCap2, TTSatCap, self.cont.tt_fs)
        createToolTip(self.labelBL2, TTBL, self.cont.tt_fs)
        createToolTip(self.labelWL2, TTWL, self.cont.tt_fs)
        createToolTip(self.labelQE2, TTQE, self.cont.tt_fs)
        createToolTip(self.labelRNI2, TTRN, self.cont.tt_fs)
        createToolTip(self.labelDN2, TTDN, self.cont.tt_fs)
        createToolTip(self.labelSN2, TTSN, self.cont.tt_fs)
        createToolTip(self.labelTBGN2, TTTotN, self.cont.tt_fs)
        createToolTip(self.checkbuttonStretch, TTStretch, self.cont.tt_fs)
        
    def deactivateTooltips(self):
    
        '''Remove tooltips from all widgets.'''
    
        for widget in [self.entryExp, self.entryDF, self.entrySF, self.entryTF, self.entrySubs,
                       self.labelSNR2, self.labelStackSNR2, self.labelDR2, self.labelGainI2,
                       self.labelSatCap2, self.labelBL2, self.labelWL2, self.labelQE2,
                       self.labelRNI2, self.labelDN2, self.labelSN2, self.labelTBGN2,
                       self.checkbuttonStretch]:
                           
            widget.unbind('<Enter>')
            widget.unbind('<Motion>')
            widget.unbind('<Leave>')
    
    
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
        
        self.varCamName = tk.StringVar()
        
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
        
        frameRight = ttk.Frame(frameContent)
        
        frameMessage = ttk.Frame(self)
        
        # Setup canvas
        
        f = matplotlib.figure.Figure(figsize=(6.5*scsx, 4.7*scsy), dpi=100, facecolor=DEFAULT_BG)
        self.ax = f.add_subplot(111)
        self.ax.tick_params(axis='both', which='major', labelsize=8)
        
        self.canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(f, frameRight)
        self.canvas._tkcanvas.config(highlightthickness=0)
        
        # Set dafault attribute values
        
        self.varSFLabel.set('photons/s' if self.cont.hasQE else 'e-/s')
        self.varTFLabel.set('photons/s' if self.cont.hasQE else 'e-/s')
        
        self.setDefaultValues()
        
        # Place frames
        
        frameHeader.pack(side='top', fill='x')
        
        frameContent.pack(side='top', fill='both', expand=True)
        
        frameLeft.pack(side='left', fill='both', padx=(50*scsx, 0), expand=True)
        
        frameUpLeft.pack(side='top', pady=(30*scsy, 0), expand=True)
        frameLowLeft.pack(side='top', pady=(0, 30*scsy), expand=True)
        
        frameRight.pack(side='right', expand=True)
        
        frameMessage.pack(side='bottom', fill='x')
        
        # *** Header frame ***
        
        labelHeader = ttk.Label(frameHeader, text='Plotting Tool', font=large_font, anchor='center')
        labelCamName = ttk.Label(frameHeader, textvariable=self.varCamName, anchor='center')
        
        labelHeader.pack(side='top', fill='both', pady=(10*scsy, 0))
        labelCamName.pack(side='top', fill='both')
        ttk.Separator(frameHeader, orient='horizontal').pack(side='top', fill='x')
        
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
        self.optionGain = ttk.OptionMenu(frameLowLeft, self.varGain, None, *GAIN[self.cont.cnum],
                                         command=self.updateGain)
        self.labelGain2 = ttk.Label(frameLowLeft, text='e-/ADU')
        
        self.labelRN = ttk.Label(frameLowLeft, text='Read noise:')
        self.optionRN = ttk.OptionMenu(frameLowLeft, self.varRN, None, *RN[self.cont.cnum],
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
        
        labelSF = ttk.Label(frameLowLeft, text='Skyglow flux:')
        self.entrySF = ttk.Entry(frameLowLeft, textvariable=self.varSF, font=small_font,
                                  background=DEFAULT_BG, width=9)
        labelSF2 = ttk.Label(frameLowLeft, textvariable=self.varSFLabel)
        
        labelTF = ttk.Label(frameLowLeft, text='Target flux:')
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
        
        labelSpacer = ttk.Label(frameLowLeft, text='', width=9)
        
        # Define button widget
        buttonDraw = ttk.Button(frameLeft, text='Draw graph', command=self.processInput)
        
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
        
        labelSpacer.grid(row=8, column=2)
        
        # Place more widgets according to camera type
        self.reconfigureNonstaticWidgets()
        
        # Place button widget
        buttonDraw.pack(side='bottom', pady=(0, 30*scsy), expand=True)
        
        # *** Right frame (plot window) ***

        self.canvas.get_tk_widget().pack()
        
        # *** Message frame ***
        
        labelMessage = ttk.Label(frameMessage, textvariable=self.varMessageLabel, anchor='center')
        
        ttk.Separator(frameMessage, orient='horizontal').pack(side='top', fill='x')
        labelMessage.pack(side='top', fill='both')
        
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
        self.p7 = 'Target SNR vs. skyglow flux'
        self.p10 = 'Target SNR vs. target flux'
        self.p2 = 'Stack SNR vs. sub exposure time'
        self.p3 = 'Stack SNR vs. number of subframes'
        self.p4 = 'Stack SNR increase vs. number of subframes'
        self.p5 = 'Maximum stack SNR vs. ISO'
        self.p9 = 'Dynamic range vs. sub exposure time'
        self.p8 = 'Dynamic range vs. skyglow flux'
        self.p6 = 'Dynamic range vs. ISO'
        self.p11 = 'Saturation capacity vs. gain'
        
        # Set list of available plot types depending on camera type
        if self.cont.isDSLR:
            self.plotList = [self.p1, self.p7, self.p10, self.p2, self.p3,
                             self.p4, self.p5, self.p9, self.p8, self.p6, self.p11]
        else:
            self.plotList = [self.p1, self.p7, self.p10, self.p2, self.p3, self.p4, self.p9, self.p8]
        
        self.varCamName.set('Camera: ' + NAME[self.cont.cnum])
        
        self.varPlotType.set(self.plotList[0])
        
        self.varISO.set(ISO[self.cont.cnum][self.gain_idx])
        self.varGain.set(GAIN[self.cont.cnum][self.gain_idx])
        self.varRN.set(RN[self.cont.cnum][self.rn_idx])
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
        self.optionGain.set_menu(*([None] + list(GAIN[self.cont.cnum])))
        self.optionRN.set_menu(*([None] + list(RN[self.cont.cnum])))
                
        if self.cont.isDSLR:
        
            # DSLRs use the ISO optionmenu and max exposure entry
            
            self.labelISO.grid(row=1, column=0, sticky='W')
            self.optionISO.grid(row=1, column=1)
            
            self.labelMax.grid(row=8, column=0, sticky='W')
            self.entryMax.grid(row=8, column=1)
            self.labelMax2.grid(row=8, column=2, sticky='W')
                
        else:
        
            # CCDs use gain and/or read noise optionmenus if they have more than one value to use
            
            if len(GAIN[self.cont.cnum]) > 1:
                
                self.labelGain.grid(row=1, column=0, sticky='W')
                self.optionGain.grid(row=1, column=1)
                self.labelGain2.grid(row=1, column=2, sticky='W')
                
            if len(RN[self.cont.cnum]) > 1:
                
                self.labelRN.grid(row=2, column=0, sticky='W')
                self.optionRN.grid(row=2, column=1)
                self.labelRN2.grid(row=2, column=2, sticky='W')
    
    def updateISO(self, selected_iso):
    
        '''Update index of selected ISO.'''
    
        self.gain_idx = int(np.where(ISO[self.cont.cnum] == selected_iso)[0])
        self.rn_idx = self.gain_idx
    
    def updateGain(self, selected_gain):
    
        '''Update index of selected gain.'''
    
        self.gain_idx = int(np.where(GAIN[self.cont.cnum] == selected_gain)[0])
    
    def updateRN(self, selected_rn):
    
        '''Update index of selected read noise.'''
    
        self.rn_idx = int(np.where(RN[self.cont.cnum] == selected_rn)[0])
    
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
                self.sf = (self.varSF.get()*QE[self.cont.cnum] if self.cont.photonFluxUnit.get() else self.varSF.get())
            
        except ValueError:
            self.varMessageLabel.set('Invalid input for sky flux.')
            return None
            
        try:
            if self.useFlux:
                self.tf = (self.varTF.get()*QE[self.cont.cnum] if self.cont.photonFluxUnit.get() else self.varTF.get())
            
        except ValueError:
            self.varMessageLabel.set('Invalid input for target flux.')
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
            
            rn = RN[self.cont.cnum][self.rn_idx]
            
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
            
            rn = RN[self.cont.cnum][self.rn_idx]
            
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
            
            rn = RN[self.cont.cnum][self.rn_idx]
            
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
            
            rn = RN[self.cont.cnum][self.rn_idx]
            
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
            
            sat_cap = SAT_CAP[self.cont.cnum]
            
            isTooLong = 0.3*sat_cap/self.sf > self.max
            
            exposure = 0.3*sat_cap/self.sf*np.invert(isTooLong) + self.max*isTooLong
            subs = self.total/exposure
            
            rn = RN[self.cont.cnum]
            
            snr = self.tf*exposure/np.sqrt(self.tf*exposure + self.sf*exposure \
                                           + self.df*exposure + rn**2)
            stack_snr = snr*np.sqrt(subs)
            
            self.ax.cla()
            self.ax.plot(iso, stack_snr, 'o-', color='forestgreen')
            self.ax.set_title(self.p5, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('ISO', name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('Maximum stack SNR', name='Tahoma', fontsize=small_fs)
            self.canvas.draw()
            
        elif type == self.p6:
        
            iso = ISO[self.cont.cnum]
            
            if len(iso) < 2:
                self.varMessageLabel.set('At least two ISO values required.')
                return None
            
            sat_cap = SAT_CAP[self.cont.cnum]
                
            rn = RN[self.cont.cnum]
            tbgn = np.sqrt(rn**2 + self.df*self.exposure + self.sf*self.exposure)
            
            dr = np.log10(sat_cap/tbgn)/np.log10(2)
            
            self.ax.cla()
            self.ax.plot(iso, dr, 'o-', color='navy')
            self.ax.set_title(self.p6, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('ISO', name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('Dynamic range [stops]', name='Tahoma', fontsize=small_fs)
            self.canvas.draw()
            
        elif type == self.p7:
        
            sf = np.linspace(0, 2*self.sf, 201)
        
            rn = RN[self.cont.cnum][self.rn_idx]
            
            snr = self.tf*self.exposure/np.sqrt(self.tf*self.exposure + sf*self.exposure \
                                                + self.df*self.exposure + rn**2)
            current_snr = self.tf*self.exposure/np.sqrt(self.tf*self.exposure + self.sf*self.exposure \
                                                        + self.df*self.exposure + rn**2)
            
            self.ax.cla()
            self.ax.plot((sf/QE[self.cont.cnum] if self.cont.photonFluxUnit.get() else sf), snr, '-', color='crimson')
            self.ax.plot((self.sf/QE[self.cont.cnum] if self.cont.photonFluxUnit.get() else self.sf), current_snr, 'o',
                         color='crimson')
            self.ax.set_title(self.p7, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Skyglow flux %s' % ('[photons/s]' if self.cont.photonFluxUnit.get() else '[e-/s]'),
                               name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('Target SNR', name='Tahoma', fontsize=small_fs)
            self.canvas.draw()

        elif type == self.p8:
           
            sf = np.linspace(0, 2*self.sf, 201)
        
            sat_cap = SAT_CAP[self.cont.cnum][self.gain_idx]
            
            rn = RN[self.cont.cnum][self.rn_idx]
            
            tbgn = np.sqrt(rn**2 + self.df*self.exposure + sf*self.exposure)
            current_tbgn = np.sqrt(rn**2 + self.df*self.exposure + self.sf*self.exposure)
            
            dr = np.log10(sat_cap/tbgn)/np.log10(2)
            current_dr = np.log10(sat_cap/current_tbgn)/np.log10(2)
            
            self.ax.cla()
            self.ax.plot((sf/QE[self.cont.cnum] if self.cont.photonFluxUnit.get() else sf), dr, '-', color='navy')
            self.ax.plot((self.sf/QE[self.cont.cnum] if self.cont.photonFluxUnit.get() else self.sf), current_dr, 'o',
                         color='navy')
            self.ax.set_title(self.p8, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Skyglow flux %s' % ('[photons/s]' if self.cont.photonFluxUnit.get() else '[e-/s]'),
                               name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('Dynamic range [stops]', name='Tahoma', fontsize=small_fs)
            self.canvas.draw()
            
        elif type == self.p9:
        
            exposure = np.linspace(1, 900, 200)
        
            sat_cap = SAT_CAP[self.cont.cnum][self.gain_idx]
            
            rn = RN[self.cont.cnum][self.rn_idx]
            
            tbgn = np.sqrt(rn**2 + self.df*exposure + self.sf*exposure)
            
            dr = np.log10(sat_cap/tbgn)/np.log10(2)
            
            self.ax.cla()
            self.ax.plot(exposure, dr, '-', color='navy')
            self.ax.set_title(self.p9, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Sub exposure time [s]', name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('Dynamic range [stops]', name='Tahoma', fontsize=small_fs)
            self.canvas.draw()
            
        elif type == self.p10:
        
            tf = np.linspace(0, 2*self.tf, 201)
            
            rn = RN[self.cont.cnum][self.rn_idx]
            
            snr = tf*self.exposure/np.sqrt(tf*self.exposure + self.sf*self.exposure \
                                           + self.df*self.exposure + rn**2)
            current_snr = self.tf*self.exposure/np.sqrt(self.tf*self.exposure + self.sf*self.exposure \
                                                        + self.df*self.exposure + rn**2)
            
            self.ax.cla()
            self.ax.plot((tf/QE[self.cont.cnum] if self.cont.photonFluxUnit.get() else tf), snr, '-', color='crimson')
            self.ax.plot((self.tf/QE[self.cont.cnum] if self.cont.photonFluxUnit.get() else self.tf), current_snr, 'o',
                         color='crimson')
            self.ax.set_title(self.p10, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Target flux %s' % ('[photons/s]' if self.cont.photonFluxUnit.get() else '[e-/s]'),
                               name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('Target SNR', name='Tahoma', fontsize=small_fs)
            self.canvas.draw()
            
        elif type == self.p11:
        
            gain = GAIN[self.cont.cnum]
            sat_cap = SAT_CAP[self.cont.cnum]
            
            if len(gain) < 2:
                self.varMessageLabel.set('At least two ISO values required.')
                return None
            
            self.ax.cla()
            self.ax.plot(np.log10(gain)/np.log10(2.0), np.log10(sat_cap)/np.log10(2.0), '-o', color='darkviolet')
            self.ax.set_title(self.p11, name='Tahoma', weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('log2(gain)', name='Tahoma', fontsize=small_fs)
            self.ax.set_ylabel('log2(saturation capacity)', name='Tahoma', fontsize=small_fs)
            self.canvas.draw()
            
        self.varMessageLabel.set('Data plotted.')
            
    def activateTooltips(self):
    
        '''Add tooltips to all relevant widgets.'''
        
        createToolTip(self.entryExp, TTExp, self.cont.tt_fs)
        createToolTip(self.entryDF, TTDF, self.cont.tt_fs)
        createToolTip(self.entrySF, TTSFPhoton if self.cont.hasQE else TTSFElectron, self.cont.tt_fs)
        createToolTip(self.entryTF, TTTFPhoton if self.cont.hasQE else TTTFElectron, self.cont.tt_fs)
        createToolTip(self.entryTotal, TTTotal, self.cont.tt_fs)
        createToolTip(self.entryMax, TTMax, self.cont.tt_fs)
        
    def deactivateTooltips(self):
    
        '''Remove tooltips from all widgets.'''
    
        for widget in [self.entryExp, self.entryDF, self.entrySF, self.entryTF, self.entryTotal,
                       self.entryMax]:
                           
            widget.unbind('<Enter>')
            widget.unbind('<Motion>')
            widget.unbind('<Leave>')
    
    
class ImageAnalyzer(ttk.Frame):

    def __init__(self, parent, controller):
    
        '''Initialize Image Analyzer frame.'''
    
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
        
        self.noInput = True # True if no files are added
        self.useGreen = None # Used to decide which CFA color to extract
        self.CFAPattern = None # Used to decide the CFA pattern of the color camera
        self.currentImage = None # ID for the currently showing canvas image
        self.selectionBox = None # ID for the canvas selection box
        self.localSelection = False # True if a valid selection box is displayed
        self.menuActive = False # True when the right-click menu is showing
        self.previousPath = os.path.expanduser('~/Pictures') # Default file path
        self.busy = False # True when a topwindow is showing to disable use of other widgets
        self.currentCamType = 'DSLR' # Camera type for the added images
        
        # Define values to keep track of number of added files
        self.displayed_bias = 0
        self.displayed_dark = 0
        self.displayed_flat = 0
        self.displayed_light = 0
        self.displayed_saturated = 0
        
        # Define widget variables
        
        self.varCamType = tk.StringVar()
        
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
        
        self.varMessageLabel = tk.StringVar()
        
        self.varCamType.set('DSLR')
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
        frameRight.pack(side='right', fill='both', padx=(30*scsx, 0), pady=(20*scsy, 0), expand=True)
        
        frameMessage.pack(side='bottom', fill='x')
        
        # *** Header frame ***
        
        labelHeader = ttk.Label(frameHeader, text='Image Analyzer', font=self.cont.large_font,
                                anchor='center')
        
        labelHeader.pack(side='top', fill='both', pady=(10*scsy, 5*scsy))
        ttk.Separator(frameHeader, orient='horizontal').pack(side='top', fill='x')
        
        # *** Left frame ***
        
        # Define left frame widgets
        labelType = ttk.Label(frameLeft, text='Camera type:', font=self.cont.smallbold_font,
                              anchor='center')
        frameType = ttk.Frame(frameLeft)
        self.radioDSLR = ttk.Radiobutton(frameType, text='DSLR', variable=self.varCamType,
                                         value='DSLR', command=self.changeCamType)
        self.radioCCDm = ttk.Radiobutton(frameType, text='Mono CCD', variable=self.varCamType,
                                         value='CCDm', command=self.changeCamType)
        self.radioCCDc = ttk.Radiobutton(frameType, text='Color CCD', variable=self.varCamType,
                                         value='CCDc', command=self.changeCamType)
        
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
        
        self.buttonCompute = ttk.Button(frameLeft, text='Compute sensor data',
                                        command=self.computeSensorData)
        
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
        self.radioDSLR.grid(row=0, column=0)
        self.radioCCDm.grid(row=0, column=1)
        self.radioCCDc.grid(row=0, column=2)
        
        labelAdd.pack(side='top', pady=(10*scsy, 0))
        self.optionAdd.pack(side='top', pady=(5*scsy, 5*scsy))
        self.buttonAdd.pack(side='top')
        
        labelFiles.pack(side='top', pady=(10*scsy, 5*scsy))
        self.frameFiles.pack(side='top', fill='both', expand=True)
        
        self.buttonCompute.pack(side='top', pady=15*scsy)
        
        # *** Right frame ***
        
        self.labelCanv = ttk.Label(frameRight, text='<Add an image to display here>', anchor='center')
        
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
        
        self.labelCanv.pack(expand=True)
        
        # *** Message frame ***
        
        self.labelMessage = ttk.Label(frameMessage, textvariable=self.varMessageLabel, anchor='center')
        
        ttk.Separator(frameMessage, orient='horizontal').pack(side='top', fill='x')
        self.labelMessage.pack(side='top', fill='both')
        
        
        self.labelList = [self.labelBias1, self.labelBias2, self.labelDark1, self.labelDark2,
                          self.labelFlat1, self.labelFlat2, self.labelLight, self.labelSaturated]
                          
        # *** Right-click menu ***
        
        self.menuRC = tk.Menu(self.canvasDisplay, tearoff=0)
        self.menuRC.add_command(label='Select mode', command=self.useSelectMode)
        self.menuRC.add_command(label='Drag mode', command=self.useDragMode)
        self.menuRC.add_separator()
        self.menuRC.add_command(label='Get statistics', command=self.getStatistics)
        self.menuRC.add_command(label='Transfer to SNR Calculator', command=self.transferData)
        
        # Clear selection state of file labels
        for label in self.labelList:
            label.leftselected = False
            label.rightselected = False
    
    def addImage(self):
    
        '''Add image file and show name in list.'''
        
        self.disableWidgets()
    
        type = self.varImType.get()
        
        supportedformats = [self.supportedformats[0]] if self.varCamType.get() == 'DSLR' \
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
                        self.getImage(self.labelBias1, bias1path, filename)
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
                        self.getImage(self.labelBias2, bias2path, filename, compare=self.labelBias1)
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
                    self.getImage(self.labelBias1, bias1path, filename1)
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
                    self.getImage(self.labelBias2, bias2path, filename2, compare=self.labelBias1)
                except:
                    self.enableWidgets()
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
                        self.getImage(self.labelDark1, dark1path, filename)
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
                        self.getImage(self.labelDark2, dark2path, filename, compare=self.labelDark1)
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
                    self.getImage(self.labelDark1, dark1path, filename1)
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
                    self.getImage(self.labelDark2, dark2path, filename2, compare=self.labelDark1)
                except:
                    self.enableWidgets()
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
                        self.getImage(self.labelFlat1, flat1path, filename,
                                      splitCFA=(self.varCamType.get() != 'CCDm'))
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
                        self.getImage(self.labelFlat2, flat2path, filename,
                                      splitCFA=(self.varCamType.get() != 'CCDm'),
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
                    self.getImage(self.labelFlat1, flat1path, filename1,
                                  splitCFA=(self.varCamType.get() != 'CCDm'))
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
                    self.getImage(self.labelFlat2, flat2path, filename2,
                                  splitCFA=(self.varCamType.get() != 'CCDm'), compare=self.labelFlat1)
                except:
                    self.enableWidgets()
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
                self.getImage(self.labelLight, lightpath, filename,
                              splitCFA=(self.varCamType.get() != 'CCDm'))
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
                self.getImage(self.labelSaturated, saturatedpath, filename)
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
    
        self.radioDSLR.configure(state='disabled')
        self.radioCCDm.configure(state='disabled')
        self.radioCCDc.configure(state='disabled')
        self.optionAdd.configure(state='disabled')
        self.buttonAdd.configure(state='disabled')
        self.buttonCompute.configure(state='disabled')
        for label in self.labelList:
            label.configure(state='disabled')
        
    def enableWidgets(self):
    
        '''Enable widgets that can be interacted with.'''
    
        self.radioDSLR.configure(state='normal')
        self.radioCCDm.configure(state='normal')
        self.radioCCDc.configure(state='normal')
        self.optionAdd.configure(state='normal')
        self.buttonAdd.configure(state='normal')
        self.buttonCompute.configure(state='normal')
        for label in self.labelList:
            label.configure(state='normal')
    
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
        
    def changeCamType(self):
    
        '''Warn user that added data will be lost when changing camera type.'''
    
        # If files have been added
        if not self.noInput:
        
            self.disableWidgets()
            self.busy = True
            
            # Show warning topwindow
            self.changeCamWarning()
            self.wait_window(self.topChange)
            
            # Change camera type back to previous state if the window was exited
            if self.varCamType.get() != self.currentCamType:
                self.varCamType.set(self.currentCamType)
                
            self.busy = False
            self.enableWidgets()
            
        else:
            # Show message that the camera type was changed
            self.varMessageLabel.set('Camera type changed to %s.' \
                                     % ('DSLR' if self.varCamType.get() == 'DSLR' \
                                        else ('Mono CCD' if self.varCamType.get() == 'CCDm' \
                                                         else 'Color CCD')))
            self.currentCamType = self.varCamType.get()
        
    def changeCamWarning(self):
    
        '''Show warning window with proceed and cancel options.'''
    
        def ok():
            
            '''Clear added files if user proceeds.'''
                
            self.clearFiles()
            self.currentCamType = self.varCamType.get()
            self.topChange.destroy()
            self.varMessageLabel.set('Camera type changed to %s.' \
                                     % ('DSLR' if self.varCamType.get() == 'DSLR' \
                                        else ('Mono CCD' if self.varCamType.get() == 'CCDm' \
                                                         else 'Color CCD')))
          
        # Create warning window
        self.topChange = tk.Toplevel()
        self.topChange.title('Warning')
        self.cont.addIcon(self.topChange)
        setupWindow(self.topChange, 300, 145)
        self.topChange.focus_force()
            
        tk.Label(self.topChange, text='Changing camera type will\nremove added files. Proceed?',
                  font=self.cont.small_font).pack(side='top', pady=(20*scsy, 5*scsy), expand=True)
                      
        frameButtons = ttk.Frame(self.topChange)
        frameButtons.pack(side='top', expand=True, pady=(0, 10*scsy))
        ttk.Button(frameButtons, text='Yes', command=ok).grid(row=0, column=0)
        ttk.Button(frameButtons, text='Cancel',
                   command=lambda: self.topChange.destroy()).grid(row=0, column=1)
        
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
            label.raw_img = None
            label.photo_img = None
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
        
    def getImage(self, label, filepath, filename, splitCFA=False, compare=False):
    
        '''Read image data and store as label attributes.'''
        
        self.varMessageLabel.set('Loading %s..' % filename)
        self.labelMessage.update_idletasks()
        
        # Create path string compatible with windows terminal
        norm_filepath = os.path.normpath('"' + filepath + '"')
            
        # Create path string compatible with python file opening methods
        py_filepath = '\\'.join(filepath.split('/'))
    
        # If image is a DSLR raw image
        if self.varCamType.get() == 'DSLR':
        
            self.varMessageLabel.set('Converting to TIFF.. (%s)' % filename)
            self.labelMessage.update_idletasks()
            
            # Create TIFF file from raw with dcraw
            subprocess.call('dcraw -4 -o 0 -D -t 0 -k 0 -H 1 -T -j -W %s' % norm_filepath, shell=True)
            
            self.varMessageLabel.set('Extracting data.. (%s)' % filename)
            self.labelMessage.update_idletasks()
            
            # Get array of image data
            img = plt.imread(py_filepath.split('.')[0] + '.tiff')
            
            self.varMessageLabel.set('Deleting TIFF.. (%s)' % filename)
            self.labelMessage.update_idletasks()
            
            # Delete TIFF file created by dcraw
            subprocess.call('del /Q %s' % (os.path.normpath('"' + filepath.split('.')[0] + '.tiff"')),
                            shell=True)
            
            self.varMessageLabel.set('Checking image dimensions.. (%s)' % filename)
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
            
                # Get array of image data from TIFF file
                img = plt.imread(py_filepath)
                
            # If image is a FITS file
            elif filename.split('.')[1].lower() in ['fit', 'fits']:
            
                # Get array of image data from FITS file
                img = pyfits.getdata(py_filepath, 0)
                
            if len(img.shape) != 2:
                self.varMessageLabel.set('Image file "%s" contains color channels.' \
                                         + 'Please use a non-debayered image.' % filename)
                raise Exception
                
        # If image has a CFA and a specific color needs to be extracted
        if splitCFA:
            
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
            if self.varCamType.get() == 'DSLR':
                
                self.varMessageLabel.set('Detecting CFA pattern.. (%s)' % filename)
                self.labelMessage.update_idletasks()
                
                # Get string of raw file information
                metadata = subprocess.check_output('dcraw -i -v %s' % norm_filepath, shell=True)
                    
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
                self.varMessageLabel.set('Error: CFA pattern %s not recognized.' % self.CFAPattern)
                raise Exception
                
            self.varMessageLabel.set('Extracting %s pixels.. (%s)' \
                                     % (('green' if self.useGreen else 'red'), filename))
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
        
        # If image is mono or is to keep all pixels
        else:
            
            new_img = img
        
        # Store raw image data as label attribute
        label.raw_img = new_img[:, :]
            
        self.varMessageLabel.set('Creating preview image.. (%s)' % filename)
        self.labelMessage.update_idletasks()
            
        # Save data as temporary image
        plt.imsave('temp.jpg', new_img, cmap=plt.get_cmap('gray'))
            
        # Open as PIL image and equalize histogram
        pil_img = Image.open('temp.jpg')
            
        # Store preview image as label attribute
        label.photo_img = ImageTk.PhotoImage(pil_img)
                
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
        self.imageSize = (label.photo_img.width(), label.photo_img.height())
        self.canvasDisplay.configure(scrollregion=(0, 0, self.imageSize[0], self.imageSize[1]))
        self.currentImage = self.canvasDisplay.create_image(0, 0, image=label.photo_img, anchor='nw')
    
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
                        
                            self.labelBias1.raw_img = None
                            self.labelBias1.photo_img = None
                            self.labelBias1.pack_forget()
                            self.varBias1Label.set('')
                            self.frameBias.pack_forget()
                            self.labelBiasH.pack_forget()
                            
                            self.displayed_bias = 0
                            
                        elif self.displayed_bias == 2:
                        
                            # Shift info from label 2 to label 1 if label 2 is removed
                        
                            if label is self.labelBias1:
                                self.labelBias1.raw_img = self.labelBias2.raw_img[:, :]
                                self.labelBias1.photo_img = self.labelBias2.photo_img
                                self.varBias1Label.set(self.varBias2Label.get())
                                if self.labelBias2.leftselected:
                                    self.showImage(self.labelBias1)
                            
                            self.labelBias2.raw_img = None
                            self.labelBias2.photo_img = None
                            self.labelBias2.pack_forget()
                            self.varBias2Label.set('')
                            self.varBiasHLabel.set('Bias frame')
                            
                            self.displayed_bias = 1
                        
                    elif label is self.labelDark1 or label is self.labelDark2:
                    
                        if self.displayed_dark == 1:
                        
                            self.labelDark1.raw_img = None
                            self.labelDark1.photo_img = None
                            self.labelDark1.pack_forget()
                            self.varDark1Label.set('')
                            self.frameDark.pack_forget()
                            self.labelDarkH.pack_forget()
                            
                            self.displayed_dark = 0
                            
                        elif self.displayed_dark == 2:
                        
                            if label is self.labelDark1:
                                self.labelDark1.raw_img = self.labelDark2.raw_img[:, :]
                                self.labelDark1.photo_img = self.labelDark2.photo_img
                                self.varDark1Label.set(self.varDark2Label.get())
                                if self.labelDark2.leftselected:
                                    self.showImage(self.labelDark1)
                            
                            self.labelDark2.raw_img = None
                            self.labelDark2.photo_img = None
                            self.labelDark2.pack_forget()
                            self.varDark2Label.set('')
                            self.varDarkHLabel.set('Dark frame')
                            
                            self.displayed_dark = 1
                        
                    elif label is self.labelFlat1 or label is self.labelFlat2:
                    
                        if self.displayed_flat == 1:
                        
                            self.labelFlat1.raw_img = None
                            self.labelFlat1.photo_img = None
                            self.labelFlat1.pack_forget()
                            self.varFlat1Label.set('')
                            self.frameFlat.pack_forget()
                            self.labelFlatH.pack_forget()
                            
                            self.displayed_flat = 0
                            
                        elif self.displayed_flat == 2:
                        
                            if label is self.labelFlat1:
                                self.labelFlat1.raw_img = self.labelFlat2.raw_img[:, :]
                                self.labelFlat1.photo_img = self.labelFlat2.photo_img
                                self.varFlat1Label.set(self.varFlat2Label.get())
                                if self.labelFlat2.leftselected:
                                    self.showImage(self.labelFlat1)
                            
                            self.labelFlat2.raw_img = None
                            self.labelFlat2.photo_img = None
                            self.labelFlat2.pack_forget()
                            self.varFlat2Label.set('')
                            self.varFlatHLabel.set('Flat frame')
                            
                            self.displayed_flat = 1
                        
                    elif label is self.labelLight:
                    
                        self.labelLight.raw_img = None
                        self.labelLight.photo_img = None
                        self.labelLight.pack_forget()
                        self.varLightLabel.set('')
                        self.labelLightH.pack_forget()
                        self.displayed_light = 0
                        
                    elif label is self.labelSaturated:
                    
                        self.labelSaturated.raw_img = None
                        self.labelSaturated.photo_img = None
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
                
                self.disableWidgets()
                self.busy = True
                
                # Setup window
                topAskUseLight = tk.Toplevel()
                topAskUseLight.title('Note')
                self.cont.addIcon(topAskUseLight)
                setupWindow(topAskUseLight, 300, 180)
                topAskUseLight.focus_force()
                        
                def yes():
                    self.cancelled = False
                    topAskUseLight.destroy()
                    
                self.cancelled = True
                        
                tk.Label(topAskUseLight, text='A frame containing saturated pixels is required\nto ' \
                     + 'compute sensor data. Does the added\nlight frame contain saturated pixels?',
                         font=self.cont.small_font).pack(side='top', pady=(20*scsy, 5*scsy),
                         expand=True)
                              
                frameButtons = ttk.Frame(topAskUseLight)
                frameButtons.pack(side='top', expand=True, pady=(0, 10*scsy))
                ttk.Button(frameButtons, text='Yes', command=yes).grid(row=0, column=0)
                ttk.Button(frameButtons, text='No',
                           command=lambda: topAskUseLight.destroy()).grid(row=0, column=1)
                        
                self.wait_window(topAskUseLight)
                        
                self.enableWidgets()
                self.busy = False
                
                # Cancel if user exits topwindow
                if self.cancelled:
                    self.varMessageLabel.set('Cancelled. Please add a saturated ' \
                                             + 'frame to compute sensor data.')
                    self.menuActive = False
                    return False
                
                # Use light frame as saturated frame
                saturated = self.labelLight.raw_img
            
            # Show message if required files haven't been added
            else:
                self.varMessageLabel.set('Two bias frames, two flat frames and ' \
                             + 'one saturated (or light) frame is required to compute sensor data.')
                return None
        else:
        
            saturated = self.labelSaturated.raw_img
            
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
        ttk.Label(frameResults, text=('%.3g' % self.gain), width=7,
                  anchor='center').grid(row=0, column=1)
        ttk.Label(frameResults, text=' e-/ADU').grid(row=0, column=2, sticky='W')
        
        ttk.Label(frameResults, text='Read noise: ').grid(row=1, column=0, sticky='W')
        ttk.Label(frameResults, text=('%.3g' % self.rn), width=7,
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
        
        ttk.Button(self.topResults, text='Save sensor data', command=self.saveSensorResults)\
                  .pack(side='top', pady=((5*scsy, 20*scsy)), expand=True)
        
        self.wait_window(self.topResults)
        
        # Close overlying windows if a lower window is exited
        try:
            self.topCamInfo.destroy()
        except:
            pass
        try:
            self.topSaveResults.destroy()
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
        
    def saveSensorResults(self):
    
        '''Show window where user can specify camera or add a new camera.'''
    
        self.topSaveResults = tk.Toplevel()
        self.topSaveResults.title('Select camera')
        self.cont.addIcon(self.topSaveResults)
        setupWindow(self.topSaveResults, 300, 300)
        self.topSaveResults.focus_force()
        
        labelCamera = ttk.Label(self.topSaveResults, text='Choose camera or add new:',
                                font=self.cont.medium_font, anchor='center')
        frameSelection = ttk.Frame(self.topSaveResults)
        
        labelCamera.pack(side='top', pady=(18*scsy, 8*scsy), expand=True)
        frameSelection.pack(side='top', pady=10*scsy, expand=True)
        
        scrollbarCamera = ttk.Scrollbar(frameSelection)
        self.listboxCamera = tk.Listbox(frameSelection, height=8, width=28, font=self.cont.small_font,
                                        selectmode='single', yscrollcommand=scrollbarCamera.set)
        
        scrollbarCamera.pack(side='right', fill='y')
        self.listboxCamera.pack(side='right', fill='both')
        
        self.listboxCamera.focus_force()
        
        isDSLR = self.varCamType.get() == 'DSLR'
        
        self.listboxCamera.insert(0, 'Add new camera')
        for i in range(len(NAME)):
            if (TYPE[i] == 'DSLR' and isDSLR) or (TYPE[i] == 'CCD' and not isDSLR):
                self.listboxCamera.insert(i+1, NAME[i])
            
        scrollbarCamera.config(command=self.listboxCamera.yview)
        
        ttk.Button(self.topSaveResults, text='OK', command=self.getUserCamInfo)\
                  .pack(side='top', pady=((0, 20*scsy)), expand=True)
    
    def getUserCamInfo(self):
    
        '''Get required camera info from user before saving calculated sensor values.'''
    
        name = self.listboxCamera.get('active')
        addNew = name == 'Add new camera'
        isDSLR = self.varCamType.get() == 'DSLR'
            
        varCamName = tk.StringVar()
        varISO = tk.IntVar()
        varMessageLabel = tk.StringVar()
        
        varISO.set('')
        
        def executeSensorResultSave(name):
            
            '''Save calculated sensor values to "cameradata.txt".'''
        
            if addNew:
            
                # Get inputted name of new camera
                name = varCamName.get()
                
                if name == '' or ',' in name:
                    varMessageLabel.set('Invalid camera name input.')
                    return None
                    
                if name in NAME:
                    varMessageLabel.set('This camera is already added.')
                    return None
                    
            if isDSLR:
            
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
                
            # If a new camera is added
            if addNew:
            
                # Create new line with calculated info
                file.write('\n' + '\n'.join(lines[1:-1]))
                file.write('\n%s,%s,%.3g,%.3g,%d,%d,%d,%s' % (name, ('DSLR' if isDSLR else 'CCD'),
                                                              self.gain, self.rn, round(self.sat_cap),
                                              round(self.black_level), round(self.white_level), 'NA'))
                if isDSLR: file.write(',' + iso)
                file.write('\n' + lines[-1])
                file.close()
                
                # Sort camera list
                idx = sortCamList(name)
                
                # Insert camera name and calculated values to camera info lists
                NAME.insert(idx, name)
                TYPE.insert(idx, ('DSLR' if isDSLR else 'CCD'))
                GAIN.insert(idx, np.array([float('%.3g' % self.gain)]))
                RN.insert(idx, np.array([float('%.3g' % self.rn)]))
                SAT_CAP.insert(idx, [int(round(self.sat_cap))])
                BLACK_LEVEL.insert(idx, [int(round(self.black_level))])
                WHITE_LEVEL.insert(idx, [int(round(self.white_level))])
                QE.insert(idx, 'NA')
                ISO.insert(idx, (np.array([int(iso)]) if isDSLR else [0]))
            
            # If the camera already exists            
            else:
                
                for line in lines[1:-1]:
                
                    line = line.split(',')
                    
                    # Find relevant line in the camera data file
                    if line[0] == name:
                    
                        # Read existing values
                        gainvals = line[2].split('-')
                        rnvals = line[3].split('-')
                        satcapvals = line[4].split('-')
                        blvals = line[5].split('-')
                        wlvals = line[6].split('-')
                    
                        # Find where to add new values, or which old values to overwrite
                    
                        if isDSLR:
                        
                            isovals = line[8].split('-')
                        
                            if iso in isovals:
                            
                                g_idx1 = rn_idx1 = isovals.index(iso)
                                g_idx2 = rn_idx2 = g_idx1 + 1
                                
                            else:
                            
                                g_idx1 = g_idx2 = rn_idx1 = rn_idx2 = sorted(isovals + [iso],
                                                                             key=int).index(iso)
                                
                        else:
                        
                            if ('%.2g' % self.rn) in rnvals:
                            
                                rn_idx1 = rnvals.index('%.2g' % self.rn)
                                rn_idx2 = rn_idx1 + 1
                            else:
                            
                                rn_idx1 = rn_idx2 = sorted(rnvals + ['%.3g' % self.rn],
                                                           key=float).index(('%.3g' % self.rn))
                        
                            if ('%.2g' % self.gain) in gainvals:
                            
                                g_idx1 = gainvals.index('%.2g' % self.gain)
                                g_idx2 = g_idx1 + 1
                            
                            else:
                            
                                g_idx1 = g_idx2 = sorted(gainvals + ['%.3g' % self.gain],
                                                         key=float).index(('%.3g' % self.gain))
                        
                        # Add calculated values to camera data file
                        file.write('\n%s,%s,%s,%s,%s,%s,%s,%s' \
                % (name, ('DSLR' if isDSLR else 'CCD'),
                   '-'.join(gainvals[:g_idx1] + ['%.3g' % self.gain] + gainvals[g_idx2:]),
                   '-'.join(rnvals[:rn_idx1] + ['%.3g' % self.rn] + rnvals[rn_idx2:]),
                   '-'.join(satcapvals[:g_idx1] + ['%d' % round(self.sat_cap)] + satcapvals[g_idx2:]),
                   '-'.join(blvals[:g_idx1] + ['%d' % round(self.black_level)] + blvals[g_idx2:]),
                   '-'.join(wlvals[:g_idx1] + ['%d' % round(self.white_level)] + wlvals[g_idx2:]),
                   line[7]))
                                      
                        if isDSLR: file.write(',%s' % ('-'.join(isovals[:g_idx1] + [iso] \
                                                                        + isovals[g_idx2:])))
                        
                    else:
                    
                        file.write('\n' + ','.join(line))
                    
                file.write('\n' + lines[-1])
                file.close()
                
                # Insert calculated values to camera info lists
                
                idx = NAME.index(name)
                
                if g_idx2 == g_idx1 + 1:
                    GAIN[idx][g_idx1] = float('%.3g' % self.gain)
                    SAT_CAP[idx][g_idx1] = int(round(self.sat_cap))
                    BLACK_LEVEL[idx][g_idx1] = int(round(self.black_level))
                    WHITE_LEVEL[idx][g_idx1] = int(round(self.white_level))
                else:
                    GAIN[idx] = np.insert(GAIN[idx], g_idx1, float('%.3g' % self.gain))
                    SAT_CAP[idx] = np.insert(SAT_CAP[idx], g_idx1, int(round(self.sat_cap)))
                    BLACK_LEVEL[idx] = np.insert(BLACK_LEVEL[idx], g_idx1,
                                                 int(round(self.black_level)))
                    WHITE_LEVEL[idx] = np.insert(WHITE_LEVEL[idx], g_idx1,
                                                 int(round(self.white_level)))
                    if isDSLR: ISO[idx] = np.insert(ISO[idx], g_idx1, int(iso))
                    
                if rn_idx2 == rn_idx1 + 1:
                    RN[idx][rn_idx1] = float('%.3g' % self.rn)
                else:
                    RN[idx] = np.insert(RN[idx], rn_idx1, float('%.3g' % self.rn))
                
            self.cont.toolsConfigured = False
            self.varMessageLabel.set('Sensor information added for camera "%s".' % name)
            try:
                self.topCamInfo.destroy()
            except:
                pass
            self.topSaveResults.destroy()
            self.topResults.destroy()
        
        # Create the window asking for required camera information
        if addNew or isDSLR:
        
            self.topCamInfo = tk.Toplevel()
            self.topCamInfo.title('Save sensor data')
            self.cont.addIcon(self.topCamInfo)
            setupWindow(self.topCamInfo, 300, 160)
            self.topCamInfo.focus_force()
            
            ttk.Label(self.topCamInfo, text='Please provide requested camera information:')\
                     .pack(side='top', pady=(15*scsy, 5*scsy), expand=True)
            
            inputFrame = ttk.Frame(self.topCamInfo)
            inputFrame.pack(side='top', pady=(7*scsy, 5*scsy), expand=True)
            
            if addNew:
            
                ttk.Label(inputFrame, text='Camera name: ').grid(row=0, column=0, sticky='W')
                ttk.Entry(inputFrame, textvariable=varCamName, font=self.cont.small_font,
                          background=DEFAULT_BG, width=20).grid(row=0, column=1)
            
            if isDSLR:
            
                ttk.Label(inputFrame, text='ISO: ').grid(row=1, column=0, sticky='W')
                ttk.Entry(inputFrame, textvariable=varISO, font=self.cont.small_font,
                          background=DEFAULT_BG, width=8).grid(row=1, column=1)
        
            ttk.Button(self.topCamInfo, text='OK',
                       command=lambda: executeSensorResultSave(name)).pack(side='top',
                                                                    pady=(0, 10*scsy), expand=True)
            ttk.Label(self.topCamInfo, textvariable=varMessageLabel, font=self.cont.small_font,
                          background=DEFAULT_BG).pack(side='top', pady=(0, 10*scsy), expand=True)
                          
        else:
        
            executeSensorResultSave(name)
    
    def createSelectionBoxEvent(self, event):
    
        '''Create rectangle in canvas when left-clicked.'''
    
        if self.menuActive: return None
    
        # Delete existing selection box
        event.widget.delete(self.selectionBox)
            
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
        
        event.widget.coords(self.selectionBox, self.selectionArea[0], self.selectionArea[1],
                            event.widget.canvasx(event.x), event.widget.canvasy(event.y))
                            
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
        else:
            self.localSelection = True
        
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
        setupWindow(topStatistics, 300, 180)
        topStatistics.focus_force()
        
        ttk.Label(topStatistics, text='Statistics of selected image region' \
                                      if self.localSelection else 'Statistics of the entire image',
                  font=self.cont.smallbold_font,
                  anchor='center').pack(side='top', pady=(10*scsy, 0), expand=True)
        
        frameStatistics = ttk.Frame(topStatistics)
        frameStatistics.pack(side='top', pady=(0, 15*scsy), expand=True)
        
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
        
        self.wait_window(topStatistics)
        
        self.enableWidgets()
        self.busy = False
        
        self.menuActive = False
        
    def transferData(self):
    
        '''Get statistics of added dark or light frames and transfer values to SNR Calculator.'''
    
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
            
            self.disableWidgets()
            self.busy = True
            
            # Cancel if topwindow was exited
            if self.cancelled:
                self.varMessageLabel.set('Cancelled.')
                self.menuActive = False
                return None
                
            # Setup other tools and choose camera if neccessary
            if not self.preparedDataTransfer(): return None
            
            snrframe = self.cont.frames[SNRCalculator]
              
            # Get raw data of selected area
            img_crop = label.raw_img[self.selectionArea[1]:self.selectionArea[3],
                                     self.selectionArea[0]:self.selectionArea[2]]
            
            # Calculate required values and transfer to corresponding widgets
            if varBGRegion.get():
                
                if self.varCamType.get() == 'DSLR':
                
                    bg_noise = np.std(img_crop)
                    snrframe.varBGN.set('%.3g' % bg_noise)
                    
                bg_level = np.median(img_crop)
                snrframe.varBGL.set('%g' % bg_level)
                    
            else:
            
                target_level = np.median(img_crop)
                snrframe.varTarget.set('%g' % target_level)
                
            self.varMessageLabel.set('Background data transfered to SNR Calculator.' \
                                     if varBGRegion.get() \
                                     else 'Target data transfered to SNR Calculator.')
        
        # If the selected frame is a dark frame
        else:
        
            # If the camera is a DSLR
            if self.varCamType.get() == 'DSLR':
            
                # If only one dark frame is added
                if self.displayed_dark == 1:
                
                    # Ask if user will still proceed
                
                    self.disableWidgets()
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
                    
                    tk.Label(topWarning, text='Using two dark frames is recommended\nto get more' \
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
            
            # Setup other tools and choose camera if neccessary
            if not self.preparedDataTransfer(): return None
                
            # Transfer data to dark input widget and set checkbutton state
            snrframe = self.cont.frames[SNRCalculator]
            snrframe.varUseDark.set(1)
            snrframe.toggleDarkInputMode()
            snrframe.varDark.set('%g' % dark_val)
                
            self.varMessageLabel.set('Dark data transfered to SNR Calculator.')
                    
        self.menuActive = False
    
    def preparedDataTransfer(self):
    
        '''Initialize the other tools if necessary and provide option to change camera.'''
    
        camtype = 'DSLR' if self.varCamType.get() == 'DSLR' else 'CCD'
    
        # If no camera is selected or the selected camera is if incorrect type
        if self.cont.cnum is None or TYPE[self.cont.cnum] != camtype:
        
            # Bring up camera selection window
        
            self.disableWidgets()
            self.busy = True
            
            success = self.cont.changeCamera(restrict=camtype)
            
            self.enableWidgets()
            self.busy = False
            
            # Cancel if the topwindow was exited
            if not success:
                self.varMessageLabel.set('Cancelled.')
                self.menuActive = False
                return False
        
        # If the currently selected camera is valid
        else:
        
            # Show window with option to change camera before proceeding
        
            self.disableWidgets()
            self.busy = True
            
            topMessage = tk.Toplevel()
            topMessage.title('Note')
            self.cont.addIcon(topMessage)
            setupWindow(topMessage, 300, 180)
            topMessage.focus_force()
                    
            def ok():
                self.cancelled = False
                topMessage.destroy()
                
            def change():
                self.cancelled = not self.cont.changeCamera(restrict=camtype)
                topMessage.destroy()
                
            self.cancelled = True
                    
            tk.Label(topMessage, text='Current camera is\n"%s".\nProceed?' % NAME[self.cont.cnum],
                     font=self.cont.small_font).pack(side='top', pady=(20*scsy, 5*scsy), expand=True)
                          
            frameButtons = ttk.Frame(topMessage)
            frameButtons.pack(side='top', expand=True, pady=(0, 10*scsy))
            ttk.Button(frameButtons, text='Yes', command=ok).grid(row=0, column=0)
            ttk.Button(frameButtons, text='Change camera', command=change).grid(row=0, column=1)
                    
            self.wait_window(topMessage)
                    
            self.enableWidgets()
            self.busy = False
            
            if self.cancelled:
                self.varMessageLabel.set('Cancelled.')
                self.menuActive = False
                return False
        
        # Initialize the other tools if they haven't been already
        if not self.cont.toolsConfigured:
                
            self.cont.setupTools(self.cont.cnum)
            self.cont.showFrame(ImageAnalyzer)
            
        return True
    
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
    
    def useSelectMode(self):
    
        '''Enable selection box drawing on canvas.'''
    
        self.canvasDisplay.unbind('<Button-1>')
        self.canvasDisplay.unbind('<B1-Motion>')
        
        self.canvasDisplay.bind('<Button-1>', self.createSelectionBoxEvent)
        self.canvasDisplay.bind('<B1-Motion>', self.drawSelectionBoxEvent)
        self.canvasDisplay.bind('<ButtonRelease-1>', self.evaluateSelectionBoxEvent)
        
        self.canvasDisplay.config(cursor='arrow')
        
        self.menuActive = False
        
    def useDragMode(self):
    
        '''Enable dragging on canvas.'''
    
        self.canvasDisplay.unbind('<Button-1>')
        self.canvasDisplay.unbind('<B1-Motion>')
        self.canvasDisplay.unbind('<ButtonRelease-1>')
        
        self.canvasDisplay.bind('<Button-1>', self.startDragEvent)
        self.canvasDisplay.bind('<B1-Motion>', self.dragEvent)
        
        self.canvasDisplay.config(cursor='hand2')
        
        self.menuActive = False
    
        
class ToolTip:

    def __init__(self, widget, fs):
    
        '''Initialize class for showing tooltips.'''
    
        self.widget = widget
        self.fs = fs

    def showToolTip(self, tiptext):
    
        '''Display tooltip.'''
        
        self.topTip = tk.Toplevel(self.widget) # Create tooltip window
        self.topTip.wm_overrideredirect(1)     # Remove window border
        
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

    def __init__(self):
    
        '''Initialize error window.'''
    
        tk.Tk.__init__(self)
        
        self.title('Error')
        
        try:
            self.iconbitmap('aplab_icon.ico')
        except:
            pass
            
        errfont = tkFont.Font(root=self, family='Tahoma', size=9)
        
        tk.Label(self, text=startup_error, font=errfont).pack(pady=12*scsy)
        ttk.Button(self, text='OK', command=lambda: self.destroy()).pack(pady=(0, 12*scsy))
        
        strs = startup_error.split('\n')
        lens = [len(str) for str in strs]
        
        setupWindow(self, (errfont.measure(strs[lens.index(max(lens))]) + 20), 100)
        
     
def createToolTip(widget, tiptext, fs):

    '''Creates a tooltip with the given text for the given widget.'''
    
    toolTip = ToolTip(widget, fs) # Create ToolTip instance
    
    def enterWidget(event):
        toolTip.showToolTip(tiptext)
        
    def moveWidget(event):
        toolTip.topTip.wm_geometry('+%d+%d' % (event.widget.winfo_pointerx() + 15*scsx,
                                               event.widget.winfo_pointery() + 15*scsy))
        
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

def setNewFS(app, cnum, fs):

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
    app = APLab(cnum, fs)
    app.mainloop()

def sortCamList(name):

    '''Sort camera data list and return index of provided name.'''

    def natural_keys(text):
        return [(int(c) if c.isdigit() else c) for c in re.split('(\d+)', text)]

    file = open('cameradata.txt', 'r')
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

    file = open('cameradata.txt', 'w')

    file.write(lines[0])

    for i in range(len(names)):

        idx = names.index(sortnames[i])
        
        file.write('\n' + sortnames[i] + ',' + rest[idx])
        
    file.write('\n' + lines[-1])
    file.close()
    
    return sortnames.index(name)
    
# Define tooltip strings
TTExp = '''\
The exposure time of the subframe.'''
TTUseDark = '''\
Deactivate if you don\'t have a dark frame
with the same exposure time and temperature
as the light frame. This will restrict the
noise and flux values that can be calculated,
but SNR and DR will not be affected.'''
TTDarkNoise = '''\
The standard deviation of pixel values in a
dark frame with the same exposure time and
temperature as the relevant subframe. This
value must be from an uncalibrated frame.'''
TTDarkLevel = '''\
The average or median pixel value in a dark
frame with the same exposure time and
temperature as the relevant subframe. This
value must be from an uncalibrated frame.'''
TTBGNoise = '''\
The standard deviation of pixel values in
a background region of the subframe. This
value must be from one color of the Bayer
array of an uncalibrated frame.'''
TTBGLevel = '''\
The average or median pixel value in a
background region of the subframe. This
value must be from an uncalibrated frame.'''
TTTarget = '''\
The average or median pixel value in a target
region of the subframe, where the SNR is to be
calculated. This value must be from an
uncalibrated frame.'''
TTDF = '''\
The number of photoelectrons per second
produced in each pixel by the dark current.'''
TTSFPhoton = '''\
The number of skyglow photons per second
reaching each pixel. This is a measure of the
sky brightness. Different photon fluxes are
comparable between different camera models,
povided that the same optical train is used
and that the fluxes relate to the same color(s)
of light.'''
TTSFElectron = '''\
The number of photoelectrons per second
produced in each pixel as a result of photons
from the skyglow. This is a measure of the sky
brightness. Different electron fluxes are not
directly comparable between different camera
models, but are comparable for the same camera
model if the optical train is the same.'''
TTTFPhoton = '''\
The number of target photons per second
reaching each target pixel. This is a measure
of the brightness of the target. Different
photon fluxes are comparable between different
camera models, povided that the same optical
train is used and that the fluxes relate to the
same color(s) of light.'''
TTTFElectron = '''\
The number of photoelectrons per second
produced in each target pixel as a result of
photons from the target. This is a measure of
the brightness of the target. Different electron
fluxes are not directly comparable between
different camera models, but are comparable
for the same camera model if the optical train
is the same.'''
TTDSFPhoton = '''\
The number of photons per second that would
have to reach each pixel to produce the
observed electron flux from both skyglow and
dark current. Different photon fluxes are
comparable between different camera models,
povided that the same optical train is used
and that the fluxes relate to the same
color(s) of light.'''
TTDSFElectron = '''\
The number of photoelectrons per second
produced in each pixel either as a result of
photons from the skylow, or from dark current.
Different electron fluxes are not directly
comparable between different camera models,
but are comparable for the same camera model
if the optical train is the same.'''
TTSubs = '''\
Set higher than 1 to get the SNR and simulated
image of a stacked frame rather than of a single
subframe.'''
TTSNR = '''\
The signal to noise ratio of the target in the
subframe.'''
TTStackSNR = '''\
The signal to noise ratio of the target in the
stacked image. The subframes are assumed to be
averaged together.'''
TTDR = '''\
The dynamic range of the image in stops. This
indicates the size of the intensity range between
the noise floor and the saturation capacity. An
increase of 1 stop corresponds to doubling the
intensity range.'''
TTGain = '''\
The ratio of the number of photoelectrons
produced in a pixel to the resulting pixel value
in the digital image.'''
TTSatCap = '''\
The maximum number of photoelectrons that can be
produced in a pixel before the pixel value reaches
the white point.'''
TTBL = '''\
The mean pixel value of a bias frame, where no
photons have reached the sensor.'''
TTWL = '''\
The highest possible pixel value in the image.'''
TTQE = '''\
The probability that a photon reaching the sensor
will result in the production of a photoelectron.'''
TTRN = '''\
The uncertainty in the number of photoelectrons
in a pixel caused by reading the sensor. This
includes the quantization error introduced by
rounding to a whole number of ADUs.'''
TTDN = '''\
The uncertainty in the number of photoelectrons
in a pixel produced by the randomness of the
dark current.'''
TTSN = '''\
The uncertainty in the number of photoelectrons in
a pixel produced by the randomness of the skyglow
photons.'''
TTDSN = '''\
The uncertainty in the number of photoelectrons
in a pixel caused by both skyglow and dark current.'''
TTTotN = '''\
The total uncertainty in the number of
photoelectrons in each background pixel. This
includes read noise, dark noise and skyglow
noise.'''
TTStretch = '''\
Activate to perform a histogram stretch to
increase the contrast of the simulated image.'''
TTTotal = '''\
The total exposure time for all the subframes
combined.'''
TTMax = '''\
The maximum allowed exposure time for a
subframe. This will be limited by factors
like tracking/guiding accuracy, unwanted
saturation and risk of something ruining
the exposure.'''
    
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

SNR_WINDOW_SIZE = (700, 550)    
SIM_WINDOW_SIZE = (l_x, 535)
PLOT_WINDOW_SIZE = (l_x, 560)
AN_WINDOW_SIZE = (l_x, l_y)

# Lists for camera data
NAME = []
TYPE = []
GAIN = []
RN = []
SAT_CAP = []
BLACK_LEVEL = []
WHITE_LEVEL = []
QE = []
ISO = []

startup_success = True # Set to false if an error occurs while reading camera data
startup_error = ''     # Error message to show
no_default = False     # Set to true if there is no default camera

# Try to read camera data and store in lists

try:
    file = open('cameradata.txt', 'r')
    
except IOError:

    startup_success = False
    startup_error = 'Could not find "cameradata.txt".'

if startup_success:
    
    lines = file.read().split('\n')
    file.close()

    for line in lines[1:-1]:

        line = line.split(',')
        
        try:
        
            NAME.append(line[0])
            TYPE.append(line[1])
            
            if not (line[1] == 'DSLR' or line[1] == 'CCD'):
            
                startup_success = False
                startup_error = 'Invalid camera type for camera model:\n"%s". ' \
                                + 'Must be "DSLR" or "CCD".' % NAME[-1]
                break
                
            if len(line) != (9 if line[1] == "DSLR" else 8):
            
                raise IndexError
                
            GAIN.append(np.array(line[2].split('-')).astype(float))
            RN.append(np.array(line[3].split('-')).astype(float))
            SAT_CAP.append(np.array(line[4].split('-')).astype(int))
            BLACK_LEVEL.append(np.array(line[5].split('-')).astype(int))
            WHITE_LEVEL.append(np.array(line[6].split('-')).astype(int))
            QE.append(line[7] if line[7] == 'NA' else float(line[7]))
            ISO.append(np.array(line[8].split('-')).astype(int) if line[1] == 'DSLR' else [0])
            
            if line[1] == 'DSLR':
            
                if len(GAIN[-1]) != len(ISO[-1]):
                
                    startup_success = False
                    startup_error = 'Non-matching number of gain and ISO values\nfor ' \
                                    + 'camera model: "%s".' % NAME[-1]
                    break
                    
                elif len(RN[-1]) != len(ISO[-1]):
                
                    startup_success = False
                    startup_error = 'Non-matching number of read noise and ISO values\nfor ' \
                                    + 'camera model: "%s".' % NAME[-1]
                    break
                    
            if len(SAT_CAP[-1]) != len(GAIN[-1]):
            
                startup_success = False
                startup_error = 'Non-matching number of saturation capacity and\ngain values for ' \
                                + 'camera model: "%s".' % NAME[-1]
                break
                
            if len(WHITE_LEVEL[-1]) != len(GAIN[-1]):
            
                startup_success = False
                startup_error = 'Non-matching number of white level and gain\nvalues for ' \
                                + 'camera model: "%s".' % NAME[-1]
                break
            
        except IndexError:
        
            startup_success = False
            startup_error = 'Invalid data configuration in\nline %d in "cameradata.txt".' \
                            % (len(NAME) + 1)
            break
            
        except (TypeError, ValueError):
        
            startup_success = False
            startup_error = 'Invalid data type detected for camera model:\n"%s".' % NAME[-1]
            break
         
# Get name of default camera model and default tooltip state
            
if startup_success:
    
    try:
        definfo = (lines[-1].split('Camera: ')[1]).split(', Tooltips: ')
        definfo2 = definfo[1].split(', Fontsize: ')
        
        DEFAULT = definfo[0]
        TT_STATE = definfo2[0]
        FS = definfo2[1]
        if FS != 'auto': FS = int(FS)
        
        if DEFAULT == 'none':
        
            no_default = True
        
        elif not DEFAULT in NAME:
        
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
    
# Run application, or show error message if an error occured
    
if startup_success:
    app = APLab(None if no_default else NAME.index(DEFAULT), FS)
    app.mainloop()
else:
    error = ErrorWindow()
    error.mainloop()