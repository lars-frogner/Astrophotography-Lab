# -*- coding: utf-8 -*-

import Tkinter as tk
import ttk
import tkFont
import webbrowser
import numpy as np
import aplab_common as apc
from aplab_common import C, MessageWindow
from aplab_image_calculator import ImageCalculator
from aplab_image_simulator import ImageSimulator
from aplab_plotting_tool import PlottingTool
from aplab_image_analyser import ImageAnalyser
from aplab_fov_calculator import FOVCalculator

class ToolManager(tk.Tk):

    def __init__(self, cnum, tnum, fs):
    
        '''Initialize application.'''
    
        tk.Tk.__init__(self) # Run parent constructor
        
        self.container = ttk.Frame(self) # Define main frame
        
        self.cnum = cnum # Index if camera in camera data lists. None if no camera is selected.
        self.tnum = tnum
        self.toolsConfigured = False # True if the non-"Image Analyser" classes are initialized
        
        self.title('Astrophotography Lab 0.4.0') # Set window title
        
        self.addIcon(self) # Add window icon if it exists
        
        if fs == 'auto':
        
            fs = 8 # Smallest font size

            # Adjust font size according to horizontal screen resolution
            if C.sw >= 1024:
                if C.sw >= 1280:
                    if C.sw >= 1440:
                        if C.sw >= 1920:
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
        style.configure('TLabel', font=self.small_font, background=C.DEFAULT_BG)
        style.configure('file.TLabel', font=self.small_font, background='white')
        style.configure('leftselectedfile.TLabel', font=self.small_font, background='royalblue')
        style.configure('rightselectedfile.TLabel', font=self.small_font, background='crimson')
        style.configure('leftrightselectedfile.TLabel', font=self.small_font, background='forestgreen')
        style.configure('TButton', font=self.small_font, background=C.DEFAULT_BG)
        style.configure('TFrame', background=C.DEFAULT_BG)
        style.configure('files.TFrame', background='white')
        style.configure('TMenubutton', font=self.small_font, background=C.DEFAULT_BG)
        style.configure('TRadiobutton', font=self.small_font, background=C.DEFAULT_BG)
        
        self.container.pack(side='top', fill='both', expand=True) # Pack main frame
        
        # Make rows and columns expand with window
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Define attributes to keep track of active page
        self.calMode = tk.IntVar()
        self.simMode = tk.IntVar()
        self.plMode = tk.IntVar()
        self.anMode = tk.IntVar()
        self.fovMode = tk.IntVar()
        
        self.calMode.set(0)
        self.simMode.set(0)
        self.plMode.set(0)
        self.anMode.set(1)
        self.fovMode.set(0)
        
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
        self.tooltipsOn.set(1 if C.TT_STATE == 'on' else 0)
        
        self.defaultTTState = tk.IntVar()
        self.defaultTTState.set(1 if C.TT_STATE == 'on' else 0)
        
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
        menuTool.add_checkbutton(label='FOV Calculator', variable=self.fovMode,
                                 command=self.enterFOVFrame)
        
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
        
        # "Help" menu
        self.menuHelp = tk.Menu(self.menubar, tearoff=0)
        self.menuHelp.add_command(label='User guide', command=self.showUserGuide)
        
        self.menubar.add_cascade(label='Help', menu=self.menuHelp)
        
        # Show menubar
        self.config(menu=self.menubar)
        
        # Some menu items are disabled on startup
        self.menuFile.entryconfig(0, state='disabled')
        self.menuFile.entryconfig(1, state='disabled')
        
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
        apc.setupWindow(self, *C.AN_WINDOW_SIZE)
        
        # If no camera is active
        if self.cnum is None:
            
            # Run camera selection method
            if not self.changeCamera():
                self.destroy()
                return None
                
        else:
            self.isDSLR = C.TYPE[self.cnum] == 'DSLR'  # Set new camera type
            self.hasQE = C.QE[self.cnum][0] != 'NA'    # Set new C.QE state
            self.noData = C.GAIN[self.cnum][0][0] == 0 # Determine if camera data exists
            
            self.varCamName.set('Camera: ' + C.CNAME[self.cnum])
            
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
        
            self.varTelName.set('Telescope: ' + C.TNAME[self.tnum])
        
        # Image scale for the selected camera-telescope combination
        self.ISVal = np.arctan2(C.PIXEL_SIZE[self.cnum][0]*1e-3,
                                C.FOCAL_LENGTH[self.tnum][0]*self.FLModVal)*180*3600/np.pi
        
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
        frameFOV = FOVCalculator(self.container, self)
        
        self.frames[ImageCalculator] = frameCal
        self.frames[ImageSimulator] = frameSim
        self.frames[PlottingTool] = framePlot
        self.frames[FOVCalculator] = frameFOV
        
        frameCal.grid(row=0, column=0, sticky='NSEW')
        frameSim.grid(row=0, column=0, sticky='NSEW')
        framePlot.grid(row=0, column=0, sticky='NSEW')
        frameFOV.grid(row=0, column=0, sticky='NSEW')
        
        self.toolsConfigured = True
        
        # Show start page
        self.showFrame(ImageAnalyser)
        
        self.focus_force()
        
    def showFrame(self, page):
    
        '''Shows the given frame.'''
        
        self.frames[page].tkraise()
    
    def showUserGuide(self):
    
        webbrowser.open('http://oaltais.github.io/aplab/userguide.html')
    
    def enterPlotFrame(self):
    
        '''Shows the Plotting Tool frame.'''
    
        # Do nothing if already in plotting frame
        if not self.calMode.get() and not self.simMode.get() \
           and not self.anMode.get() and not self.fovMode.get():
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
        
        # Resize and re-center window
        apc.setupWindow(self, *C.PLOT_WINDOW_SIZE)
        
        # Configure menu items
        self.menuFile.entryconfig(0, state='disabled')
        self.menuFile.entryconfig(1, state='normal')
               
        self.plMode.set(1)
        self.calMode.set(0)
        self.simMode.set(0)
        self.anMode.set(0)
        self.fovMode.set(0)
        
    def enterCalFrame(self):
    
        '''Shows the Image Calculator frame.'''
        
        # Do nothing if already in calculator frame
        if not self.simMode.get() and not self.plMode.get() \
           and not self.anMode.get() and not self.fovMode.get():
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
        
        # Resize and re-center window
        apc.setupWindow(self, *C.CAL_WINDOW_SIZE)
        
        # Configure menu items
        self.menuFile.entryconfig(0, state='normal')
        self.menuFile.entryconfig(1, state='normal')
            
        self.calMode.set(1)
        self.simMode.set(0)
        self.plMode.set(0)
        self.anMode.set(0)
        self.fovMode.set(0)
        
    def enterSimFrame(self):
    
        '''Shows the Image Simulator frame.'''
        
        # Do nothing if already in simulator frame
        if not self.calMode.get() and not self.plMode.get() \
           and not self.anMode.get() and not self.fovMode.get():
            self.simMode.set(1) # Keep state from changing
            return None
        
        if self.noData:
            self.frames[MessageWindow].varHeaderLabel.set('Image Simulator')
            self.showFrame(MessageWindow)
        else:
            self.frames[ImageSimulator].varMessageLabel.set('') # Clear message label
            self.showFrame(ImageSimulator) # Show simulator frame
        
        # Resize and re-center window
        apc.setupWindow(self, *C.SIM_WINDOW_SIZE)
        
        # Configure menu items
        self.menuFile.entryconfig(0, state='disabled')
        self.menuFile.entryconfig(1, state='normal')
            
        self.calMode.set(0)
        self.simMode.set(1)
        self.plMode.set(0)
        self.anMode.set(0)
        self.fovMode.set(0)
    
    def enterAnFrame(self):
    
        '''Shows the Image Analyser frame.'''
    
        # Do nothing if already in Analyser frame
        if not self.calMode.get() and not self.simMode.get() \
           and not self.plMode.get() and not self.fovMode.get():
            self.anMode.set(1) # Keep state from changing
            return None
            
        self.frames[ImageAnalyser].varMessageLabel.set('') # Clear message label
        self.showFrame(ImageAnalyser)
        
        # Close simulation window if it is open
        try:
            self.frames[ImageSimulator].topCanvas.destroy()
        except:
            pass
        
        # Resize and re-center window
        apc.setupWindow(self, *C.AN_WINDOW_SIZE)
        
        # Configure menu items
        self.menuFile.entryconfig(0, state='disabled')
        self.menuFile.entryconfig(1, state='disabled')
        
        self.calMode.set(0)
        self.simMode.set(0)
        self.plMode.set(0)
        self.anMode.set(1)
        self.fovMode.set(0)
    
    def enterFOVFrame(self):
    
        '''Shows the FOV Calculator frame.'''
    
        # Do nothing if already in FOV frame
        if not self.calMode.get() and not self.simMode.get() \
           and not self.plMode.get() and not self.anMode.get():
            self.fovMode.set(1) # Keep state from changing
            return None
         
        fovframe = self.frames[FOVCalculator]
         
        fovframe.varMessageLabel.set('') # Clear message label
        self.showFrame(FOVCalculator)
        
        # Close simulation window if it is open
        try:
            self.frames[ImageSimulator].topCanvas.destroy()
        except:
            pass
        
        # Resize and re-center window
        apc.setupWindow(self, *C.AN_WINDOW_SIZE)
        fovframe.update()
        fovframe.selectObject(fovframe.obj_idx)
        fovframe.setFOV()
        
        # Configure menu items
        self.menuFile.entryconfig(0, state='disabled')
        self.menuFile.entryconfig(1, state='disabled')
        
        self.calMode.set(0)
        self.simMode.set(0)
        self.plMode.set(0)
        self.anMode.set(0)
        self.fovMode.set(1)
    
    def saveData(self):
    
        '''Creates window with options for saving image data.'''
    
        frame = self.frames[ImageCalculator]
        
        # Show error if no image data is calculated
        if not frame.dataCalculated:
        
            frame.varMessageLabel.set('Image data must be calculated before saving.')
            frame.labelMessage.configure(foreground='crimson')
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
        apc.setupWindow(self.topSave, 300, 145)
        
        labelSave = tk.Label(self.topSave, text='Input image keywords\n(target, location, date etc.)',
                             font=self.small_font)
        entryKeywords = ttk.Entry(self.topSave, textvariable=self.varKeywords, font=self.small_font,
                                  background=C.DEFAULT_BG, width=35)
        buttonSave = ttk.Button(self.topSave, text='Save', command=self.executeSave)
        labelSaveError = ttk.Label(self.topSave, textvariable=self.varSaveError)
        
        labelSave.pack(side='top', pady=10*C.scsy, expand=True)
        entryKeywords.pack(side='top', pady=5*C.scsy, expand=True)
        buttonSave.pack(side='top', pady=6*C.scsy, expand=True)
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
                
            file.write('%s,%s,%d,%d,%g,%d,%g,%g,%g,%g,%d,%.3f,%.3f,%.3f,0\n' % (C.CNAME[self.cnum],
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
                                             (apc.convSig(frame.sf, True) if self.hasQE else frame.sf),
                                             (apc.convSig(frame.tf, True) if self.hasQE else frame.tf)))
            
            file.close()
            
            frame.varMessageLabel.set('Image data saved.')
            frame.labelMessage.configure(foreground='navy')
        
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
            frame.labelMessage.configure(foreground='crimson')
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
            frame.labelMessage.configure(foreground='crimson')
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
        apc.setupWindow(self.topLoad, 300, 135)
        self.addIcon(self.topLoad)
        self.topLoad.focus_force()
        
        labelLoad = ttk.Label(self.topLoad, text='Choose image data to load:', anchor='center')
        optionLoad = ttk.OptionMenu(self.topLoad, self.varLoadData, None, *keywords)
        buttonLoad = ttk.Button(self.topLoad, text='Load',
                                command=lambda: self.executeLoad(names, keywords, data))
        
        labelLoad.pack(side='top', pady=10*C.scsy, expand=True)
        optionLoad.pack(side='top', pady=6*C.scsy, expand=True)
        buttonLoad.pack(side='top', pady=14*C.scsy, expand=True)
        
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
        if name == C.CNAME[self.cnum]:
        
            # If Image Calculator is the active frame
            if self.calMode.get():
            
                # Set loaded data in calculator frame
                frame.gain_idx = int(data[0])
                frame.rn_idx = int(data[1])
                frame.varISO.set(C.ISO[self.cnum][frame.gain_idx])
                frame.varGain.set(C.GAIN[self.cnum][0][frame.gain_idx])
                frame.varRN.set(C.RN[self.cnum][0][frame.rn_idx])
                frame.varExp.set(data[2])
                frame.varUseDark.set(int(data[3]))
                frame.varDark.set(data[4] if int(data[3]) else '')
                frame.varBGN.set(data[5] if self.isDSLR else '')
                frame.varBGL.set(data[6])
                frame.varTarget.set(data[7] if float(data[7]) > 0 else '')
                
                frame.dataCalculated = False # Previously calculated data is no longer valid
                frame.toggleDarkInputMode() # Change to the dark input mode that was used for the data
                frame.updateSensorLabels() # Update sensor info labels in case the C.ISO has changed
                frame.emptyInfoLabels() # Clear other info labels
                frame.varMessageLabel.set('Image data loaded.')
                frame.labelMessage.configure(foreground='navy')
        
            # If Image Simulator is the active frame
            elif self.simMode.get():
                
                # Set loaded data in simulator frame
                frame.gain_idx = int(data[0])
                frame.rn_idx = int(data[1])
                frame.varISO.set(C.ISO[self.cnum][frame.gain_idx])
                frame.varGain.set(C.GAIN[self.cnum][0][frame.gain_idx])
                frame.varRN.set(C.RN[self.cnum][0][frame.rn_idx])
                frame.varExp.set(data[2])
                frame.varDF.set(data[9] if float(data[9]) > 0 else 0)
                frame.varSF.set(data[10])
                frame.varTF.set(data[11] if float(data[11]) > 0 else 0)
                frame.varLF.set(data[12] if float(data[12]) > 0 else '')
                frame.varSubs.set(1)
            
                if int(data[8]):
                    self.setLumSignalType()
                else:
                    self.setElectronSignalType()
            
                frame.dataCalculated = False # Previously calculated data is no longer valid
                frame.updateSensorLabels() # Update sensor info labels in case the C.ISO has changed
                frame.emptyInfoLabels() # Clear other info labels
                frame.varMessageLabel.set('Image data loaded.' if int(data[3]) else \
                'Note: loaded signal data does not contain a separate value for dark current.')
                frame.labelMessage.configure(foreground='navy')
            
            # If Plotting Tool is the active frame
            else:
                
                # Set loaded data in plot frame
                frame.gain_idx = int(data[0])
                frame.rn_idx = int(data[1])
                frame.varISO.set(C.ISO[self.cnum][frame.gain_idx])
                frame.varGain.set(C.GAIN[self.cnum][0][frame.gain_idx])
                frame.varRN.set(C.RN[self.cnum][0][frame.rn_idx])
                frame.varExp.set(data[2])
                frame.varDF.set(data[9] if float(data[9]) > 0 else 0)
                frame.varSF.set(data[10])
                frame.varTF.set(data[11] if float(data[11]) > 0 else 0)
                frame.varLF.set(data[12] if float(data[12]) > 0 else '')
            
                if int(data[8]):
                    self.setLumSignalType()
                else:
                    self.setElectronSignalType()
                
                frame.ax.cla() # Clear plot
                frame.varMessageLabel.set('Image data loaded.' if int(data[3]) else \
                'Note: loaded signal data does not contain a separate value for dark current.')
                frame.labelMessage.configure(foreground='navy')
        
        # If image data is from another camera model:
        # If Image Simulator or Plotting Tool is the active frame
        elif (not self.calMode.get()) and int(data[8]) and self.hasQE:
        
            # Set signal data
            frame.varSF.set(data[10])
            frame.varTF.set(data[11])
            frame.varLF.set(data[12] if float(data[12]) > 0 else '')
            
            self.setLumSignalType()
        
            if self.simMode.get():
                frame.dataCalculated = False # Previously calculated data is no longer valid
                frame.emptyInfoLabels() # Clear info labels
            else:
                frame.ax.cla() # Clear plot
            frame.varMessageLabel.set('Signal data loaded.')
            frame.labelMessage.configure(foreground='navy')
        
        # If Image Calculator is the active frame
        else:
            
            frame.varMessageLabel.set('Image data is from another camera model. No data loaded.')
            frame.labelMessage.configure(foreground='crimson')
            
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
            frame.labelMessage.configure(foreground='crimson')
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
            frame.labelMessage.configure(foreground='crimson')
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
        apc.setupWindow(self.topManage, 300, 170)
        self.topManage.focus_force()
        
        labelManage = ttk.Label(self.topManage, text='Choose image data:',anchor='center')
        optionManage = ttk.OptionMenu(self.topManage, self.varManageData, None, *display_keywords)
        frameLow = ttk.Frame(self.topManage)
        
        labelManage.pack(side='top', pady=10*C.scsy, expand=True)
        optionManage.pack(side='top', pady=6*C.scsy, expand=True)
        frameLow.pack(side='top', pady=14*C.scsy, expand=True)
        
        buttonRename = ttk.Button(frameLow, text='Rename',
                                  command=lambda: self.executeManage(names,
                                                                     keywords,
                                                                     display_keywords,
                                                                     data))
        buttonDelete = ttk.Button(frameLow, text='Delete',
                                  command=lambda: self.executeManage(names,
                                                                     keywords,
                                                                     display_keywords,
                                                                     data,
                                                                     mode='delete'))
                                                                     
        buttonAddLim = ttk.Button(frameLow, text='Add limit signal', 
                                  command=lambda: self.executeManage(names,
                                                                     keywords,
                                                                     display_keywords,
                                                                     data,
                                                                     mode='add'))
        
        buttonRename.grid(row=0, column=0, padx=(0, 5*C.scsx))
        buttonDelete.grid(row=0, column=1)
        buttonAddLim.grid(row=1, column=0, columnspan=2, pady=(5*C.scsy, 0))
        
        if not self.calMode.get(): buttonAddLim.configure(state='disabled')
        
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
    
    def executeManage(self, names, keywords, display_keywords, datafull, mode='rename'):
    
        '''Deletes selected data, or creates window for renaming selected save.'''
    
        linenum = display_keywords.index(self.varManageData.get()) # Index of relevant data
        
        if mode == 'delete':
            
            file = open('imagedata.txt', 'w')
            
            # Rewrite the data file without the line containing the data selected for deleting
            
            for i in range(linenum):
            
                    file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
                               % tuple([names[i]] + [keywords[i]] + datafull[i]))
                
            if linenum < len(keywords):
                
                for i in range(linenum+1, len(keywords)):
                
                    file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
                               % tuple([names[i]] + [keywords[i]] + datafull[i]))
                      
                        
            file.close()
            
            # Go back to an updated managing window
            self.topManage.destroy()
            self.manageData()
            self.currentFrame().varMessageLabel.set('Image data deleted.')
            self.currentFrame().labelMessage.configure(foreground='navy')
        
        elif mode == 'add':
        
            calframe = self.frames[ImageCalculator]
            
            if C.CNAME[self.cnum] != names[linenum]:
            
                calframe.varMessageLabel.set(\
                         'Cannot add limit signal to a file saved from another camera.')
                calframe.labelMessage.configure(foreground='crimson')
                return None
        
            if not calframe.dataCalculated or calframe.tf == 0:
        
                calframe.varMessageLabel.set(\
                         'Target signal must be calculated before it can be saved as limit signal.')
                calframe.labelMessage.configure(foreground='crimson')
                return None
                
            file = open('imagedata.txt', 'w')
            
            for i in range(linenum):
                
                file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
                           % tuple([names[i]] + [keywords[i]] + datafull[i]))

            file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%.3f\n' \
                       % tuple([names[linenum]] + [keywords[linenum]] + datafull[linenum][:-1] \
                               + [apc.convSig(calframe.tf, True) if self.hasQE else calframe.tf]))
            
            if linenum < len(keywords):
                
                for i in range(linenum+1, len(keywords)):

                    file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
                               % tuple([names[i]] + [keywords[i]] + datafull[i]))
                         
            file.close()
            
            # Go back to an updated managing window
            self.topManage.destroy()
            self.currentFrame().varMessageLabel.set('Limit signal value saved to the image data file.')
            self.currentFrame().labelMessage.configure(foreground='navy')
        
        else:
        
            # Create window for inputting new save name
        
            self.varNewname = tk.StringVar()
            self.varNewnameError = tk.StringVar()
            
            self.varNewname.set(keywords[linenum])
            
            self.topRename = tk.Toplevel()
            self.topRename.title('Insert new name')
            self.addIcon(self.topRename)
            apc.setupWindow(self.topRename, 300, 135)
            self.topRename.focus_force()
            
            labelRename = ttk.Label(self.topRename, text='Insert new name:', anchor='center')
            entryRename = ttk.Entry(self.topRename, textvariable=self.varNewname, font=self.small_font,
                                    background=C.DEFAULT_BG, width=35)
            buttonRename = ttk.Button(self.topRename, text='Rename',
                                      command=lambda: self.executeRename(names,
                                                                         keywords,
                                                                         datafull,
                                                                         linenum))
            labelRenameError = ttk.Label(self.topRename, textvariable=self.varNewnameError)
            
            labelRename.pack(side='top', pady=10*C.scsy, expand=True)
            entryRename.pack(side='top', pady=5*C.scsy, expand=True)
            buttonRename.pack(side='top', pady=6*C.scsy, expand=True)
            labelRenameError.pack(side='top', expand=True)
        
    def executeRename(self, names, keywords, datafull, linenum):
    
        '''Renames the selected data save.'''
    
        if self.varNewname.get() != '' and not ',' in self.varNewname.get():
        
            file = open('imagedata.txt', 'w')
            
            # Rewrites the data file, using the new keyword for the selected data save
            
            for i in range(linenum):
                
                file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
                           % tuple([names[i]] + [keywords[i]] + datafull[i]))

            file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
                       % tuple([names[linenum]] + [self.varNewname.get()] + datafull[linenum]))
            
            if linenum < len(keywords):
                
                for i in range(linenum+1, len(keywords)):

                    file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
                               % tuple([names[i]] + [keywords[i]] + datafull[i]))
                         
            file.close()
            
            # Go back to an updated managing window
            self.topRename.destroy()
            self.topManage.destroy()
            self.manageData()
            self.currentFrame().varMessageLabel.set('Image data renamed.')
            self.currentFrame().labelMessage.configure(foreground='navy')
        
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
        apc.setupWindow(self.topCamera, 300, 330)
        self.topCamera.focus_force()
        
        labelCamera = tk.Label(self.topCamera, text='Choose camera:', font=self.medium_font)
        frameSelection = ttk.Frame(self.topCamera)
        
        labelCamera.pack(side='top', pady=(18*C.scsy, 8*C.scsy), expand=True)
        frameSelection.pack(side='top', pady=10*C.scsy, expand=True)
        
        scrollbarCamera = ttk.Scrollbar(frameSelection)
        self.listboxCamera = tk.Listbox(frameSelection, height=8, width=28, font=self.small_font,
                                        selectmode='single', yscrollcommand=scrollbarCamera.set)
        
        scrollbarCamera.pack(side='right', fill='y')
        self.listboxCamera.pack(side='right', fill='both')
        
        self.listboxCamera.focus_force()
        
        # Insert camera names into listbox
        if restrict == 'no':
            for i in range(len(C.CNAME)):
                self.listboxCamera.insert(i, C.CNAME[i])
        elif restrict == 'DSLR':
            for i in range(len(C.CNAME)):
                if C.TYPE[i] == 'DSLR': self.listboxCamera.insert(i, C.CNAME[i])
        elif restrict == 'CCD':
            for i in range(len(C.CNAME)):
                if C.TYPE[i] == 'CCD': self.listboxCamera.insert(i, C.CNAME[i])
            
        scrollbarCamera.config(command=self.listboxCamera.yview) # Add scrollbar to listbox
        
        if self.cnum is not None: self.listboxCamera.activate(self.cnum)
        
        self.varSetDefaultC = tk.IntVar()
        
        frameDefault = ttk.Frame(self.topCamera)
        buttonChange = ttk.Button(self.topCamera, text='OK', command=self.executeCamChange)
        buttonAddNew = ttk.Button(self.topCamera, text='Add new camera', command=self.addNewCamera)
        
        frameDefault.pack(side='top', expand=True)
        buttonChange.pack(side='top', pady=(10*C.scsy, 5*C.scsy), expand=True)
        buttonAddNew.pack(side='top', pady=(0, 25*C.scsy), expand=True)
        
        labelDefault = ttk.Label(frameDefault, text='Use as default:')
        checkbuttonDefault = tk.Checkbutton(frameDefault, variable=self.varSetDefaultC)
        
        labelDefault.grid(row=0, column=0)
        checkbuttonDefault.grid(row=0, column=1)
        
        self.cancelled = True
        
        self.wait_window(self.topCamera)
        try:
            self.menubar.entryconfig(1, state='normal')
            self.menubar.entryconfig(2, state='normal')
            self.menubar.entryconfig(3, state='normal')
            self.menubar.entryconfig(4, state='normal')
        except:
            pass
            
        # Return true if the window wasn't closed with the X
        return not self.cancelled
       
    def executeCamChange(self):
    
        '''Configures widgets according to the selected new camera.'''
        
        self.cancelled = False
    
        self.cnum = C.CNAME.index(self.listboxCamera.get('active')) # Get index of new camera
        
        # Calculate new image scale value if a telescope is selected
        if self.tnum is not None:
            self.ISVal = np.arctan2(C.PIXEL_SIZE[self.cnum][0]*1e-3,
                                    C.FOCAL_LENGTH[self.tnum][0]*self.FLModVal)*180*3600/np.pi
            
        # Sets the new camera name in bottom line in camera data file if "Set as default" is selected
        if self.varSetDefaultC.get():
            
            file = open('cameradata.txt', 'r')
            lines = file.read().split('\n')
            file.close()
            
            file = open('cameradata.txt', 'w')
            for line in lines[:-1]:
                file.write(line + '\n')
            file.write('Camera: ' + C.CNAME[self.cnum] + ',' + ','.join(lines[-1].split(',')[1:]))
            file.close()
            
        self.varCamName.set('Camera: ' + C.CNAME[self.cnum])
        
        anframe = self.frames[ImageAnalyser]
            
        self.isDSLR = C.TYPE[self.cnum] == 'DSLR' # Set new camera type
        self.hasQE = C.QE[self.cnum][0] != 'NA' # Set new C.QE state
        self.noData = C.GAIN[self.cnum][0][0] == 0
        
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
            anframe.labelMessage.configure(foreground='navy')
            return None
        
        calframe = self.frames[ImageCalculator]
        simframe = self.frames[ImageSimulator]
        plotframe = self.frames[PlottingTool]
        
        # Reset frames to original states
        calframe.setDefaultValues()
        calframe.toggleDarkInputMode()
        if self.tooltipsOn.get():
            apc.createToolTip(calframe.entryDark, C.TTDarkNoise if self.isDSLR else C.TTDarkLevel, self.tt_fs)
        
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
        self.currentFrame().labelMessage.configure(foreground='navy')

    def addNewCamera(self):
    
        '''Shows a window with options for adding a new camera.'''
    
        varCamName = tk.StringVar()
        varCamType = tk.StringVar()
        varPS = tk.StringVar()
        varRX = tk.IntVar()
        varRY = tk.IntVar()
        varRX.set('')
        varRY.set('')
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
                
            try:
                rx = varRX.get()
            except:
                varMessageLabel.set('Invalid resolution input.')
                return None
                
            try:
                ry = varRY.get()
            except:
                varMessageLabel.set('Invalid resolution input.')
                return None
                
            if name == '' or ',' in name:
                varMessageLabel.set('Invalid camera name input.')
                return None
                    
            if name in C.CNAME:
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
            file.write('\n%s,%s,0,0,0,0,0,NA,%g*,%d*,%d*' % (name, type, ps, rx, ry))
            if type == 'DSLR': file.write(',0')
            file.write('\n' + lines[-1])
            file.close()
            
            # Sort camera list
            idx = apc.sortDataList(name, 'cameradata.txt')
            
            # Insert camera name and type to camera info lists
            C.CNAME.insert(idx, name)
            C.TYPE.insert(idx, type)
            C.GAIN.insert(idx, [np.array([0]), np.array([1])])
            C.RN.insert(idx, [np.array([0]), np.array([1])])
            C.SAT_CAP.insert(idx, [[0], [1]])
            C.BLACK_LEVEL.insert(idx, [[0], [1]])
            C.WHITE_LEVEL.insert(idx, [[0], [1]])
            C.QE.insert(idx, ['NA', 1])
            C.PIXEL_SIZE.insert(idx, [ps, 1])
            C.RES_X.insert(idx, [rx, 1])
            C.RES_Y.insert(idx, [ry, 1])
            C.ISO.insert(idx, (np.array([0])))
            
            self.cancelled = False
            self.topAddNewCam.destroy()
            self.topCamera.destroy()
            self.changeCamera()
    
        # Setup window
        self.topAddNewCam = tk.Toplevel()
        self.topAddNewCam.title('Add new camera')
        self.addIcon(self.topAddNewCam)
        apc.setupWindow(self.topAddNewCam, 300, 200)
        self.topAddNewCam.focus_force()
        
        varCamType.set('DSLR')
            
        ttk.Label(self.topAddNewCam, text='Please provide requested camera information:')\
                 .pack(side='top', pady=(15*C.scsy, 10*C.scsy), expand=True)
            
        frameInput = ttk.Frame(self.topAddNewCam)
        frameInput.pack(side='top', pady=(7*C.scsy, 10*C.scsy), expand=True)
                  
        ttk.Label(frameInput, text='Camera type: ').grid(row=0, column=0, sticky='W')
        ttk.OptionMenu(frameInput, varCamType, None, 'DSLR', 'CCD').grid(row=0, column=1)
            
        ttk.Label(frameInput, text='Camera name: ').grid(row=1, column=0, sticky='W')
        ttk.Entry(frameInput, textvariable=varCamName, font=self.small_font,
                  background=C.DEFAULT_BG, width=20).grid(row=1, column=1)
                  
        ttk.Label(frameInput, text=u'Pixel size (in \u03bcm): ').grid(row=2, column=0, sticky='W')
        ttk.Entry(frameInput, textvariable=varPS, font=self.small_font,
                  background=C.DEFAULT_BG, width=6).grid(row=2, column=1, sticky='W')
        
        ttk.Label(frameInput, text='Resolution: ').grid(row=3, column=0, sticky='W')
        frameRes = ttk.Frame(frameInput)
        frameRes.grid(row=3, column=1, sticky='W')
        ttk.Entry(frameRes, textvariable=varRX, font=self.small_font,
                  background=C.DEFAULT_BG, width=6).pack(side='left')
        ttk.Label(frameRes, text=' x ').pack(side='left')
        ttk.Entry(frameRes, textvariable=varRY, font=self.small_font,
                  background=C.DEFAULT_BG, width=6).pack(side='left')
        
        ttk.Button(self.topAddNewCam, text='OK',
                   command=executeAddNew).pack(side='top', pady=(0, 10*C.scsy), expand=True)
        ttk.Label(self.topAddNewCam, textvariable=varMessageLabel, font=self.small_font,
                  background=C.DEFAULT_BG).pack(side='top', pady=(0, 10*C.scsy), expand=True)
        
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
        apc.setupWindow(self.topTelescope, 320, 330)
        self.topTelescope.focus_force()
        
        labelTelescope = tk.Label(self.topTelescope, text='Choose telescope or lens:',
                                  font=self.medium_font)
        frameSelection = ttk.Frame(self.topTelescope)
        
        labelTelescope.pack(side='top', pady=(18*C.scsy, 8*C.scsy), expand=True)
        frameSelection.pack(side='top', pady=10*C.scsy, expand=True)
        
        scrollbarTelescope = ttk.Scrollbar(frameSelection)
        self.listboxTelescope = tk.Listbox(frameSelection, height=8, width=32, font=self.small_font,
                                           selectmode='single', yscrollcommand=scrollbarTelescope.set)
        
        scrollbarTelescope.pack(side='right', fill='y')
        self.listboxTelescope.pack(side='right', fill='both')
        
        self.listboxTelescope.focus_force()
        
        # Insert telescope names into listbox
        for i in range(len(C.TNAME)):
            self.listboxTelescope.insert(i, C.TNAME[i])
            
        scrollbarTelescope.config(command=self.listboxTelescope.yview) # Add scrollbar to listbox
        
        if self.tnum is not None: self.listboxTelescope.activate(self.tnum)
        
        self.varSetDefaultT = tk.IntVar()
        
        frameDefault = ttk.Frame(self.topTelescope)
        buttonChange = ttk.Button(self.topTelescope, text='OK', command=self.executeTelChange)
        buttonAddNew = ttk.Button(self.topTelescope, text='Add new telescope or lens',
                                  command=self.addNewTelescope)
        
        frameDefault.pack(side='top', expand=True)
        buttonChange.pack(side='top', pady=(10*C.scsy, 5*C.scsy), expand=True)
        buttonAddNew.pack(side='top', pady=(0, 25*C.scsy), expand=True)
        
        labelDefault = ttk.Label(frameDefault, text='Use as default:')
        checkbuttonDefault = tk.Checkbutton(frameDefault, variable=self.varSetDefaultT)
        
        labelDefault.grid(row=0, column=0)
        checkbuttonDefault.grid(row=0, column=1)
        
        self.cancelled = True
        
        self.wait_window(self.topTelescope)
        try:
            self.menubar.entryconfig(1, state='normal')
            self.menubar.entryconfig(2, state='normal')
            self.menubar.entryconfig(3, state='normal')
            self.menubar.entryconfig(4, state='normal')
        except:
            pass
            
        return not self.cancelled
        
    def executeTelChange(self):
    
        '''Configures widgets according to the selected new telescope.'''
        
        self.cancelled = False
    
        self.tnum = C.TNAME.index(self.listboxTelescope.get('active')) # Get index of new telescope
        
        # Calculate new image scale value if a camera is selected
        if self.cnum is not None:
            self.ISVal = np.arctan2(C.PIXEL_SIZE[self.cnum][0]*1e-3,
                                    C.FOCAL_LENGTH[self.tnum][0]*self.FLModVal)*180*3600/np.pi
        
        # Sets the new telescope name in bottom line in telescope data file if "Set as default" is selected
        if self.varSetDefaultT.get():
            
            file = open('telescopedata.txt', 'r')
            lines = file.read().split('\n')
            file.close()
            
            file = open('telescopedata.txt', 'w')
            for line in lines[:-1]:
                file.write(line + '\n')
            file.write('Telescope: ' + C.TNAME[self.tnum])
            file.close()
            
        self.varTelName.set('Telescope: ' + C.TNAME[self.tnum])
            
        anframe = self.frames[ImageAnalyser]
            
        if not self.toolsConfigured:
            self.topTelescope.destroy()
            anframe.varMessageLabel.set('Telescope selected.')
            anframe.labelMessage.configure(foreground='navy')
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
        self.currentFrame().labelMessage.configure(foreground='navy')
        
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
                    
            if name in C.TNAME:
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
            idx = apc.sortDataList(name, 'telescopedata.txt')
            
            # Insert telescope name, aperture and focal length to telescope info lists
            C.TNAME.insert(idx, name)
            C.FOCAL_LENGTH.insert(idx, [fl, 1])
            C.APERTURE.insert(idx, [aperture, 1])
            
            self.cancelled = False
            self.topAddNewTel.destroy()
            self.topTelescope.destroy()
            self.changeTelescope()
    
        # Setup window
        self.topAddNewTel = tk.Toplevel()
        self.topAddNewTel.title('Add new telescope or lens')
        self.addIcon(self.topAddNewTel)
        apc.setupWindow(self.topAddNewTel, 300, 220)
        self.topAddNewTel.focus_force()
            
        tk.Label(self.topAddNewTel, text='Please provide requested\ntelescope/lens information:',
                 font=self.small_font)\
                 .pack(side='top', pady=(15*C.scsy, 10*C.scsy), expand=True)
            
        frameInput = ttk.Frame(self.topAddNewTel)
        frameInput.pack(side='top', pady=(7*C.scsy, 10*C.scsy), expand=True)
            
        ttk.Label(frameInput, text='Name: ').grid(row=0, column=0, sticky='W')
        ttk.Entry(frameInput, textvariable=varTelName, font=self.small_font,
                  background=C.DEFAULT_BG, width=20).grid(row=0, column=1, columnspan=2)
                  
        ttk.Label(frameInput, text='Aperture: ').grid(row=1, column=0, sticky='W')
        ttk.Entry(frameInput, textvariable=varAp, font=self.small_font,
                  background=C.DEFAULT_BG, width=12).grid(row=1, column=1, sticky='W')
        tk.Label(frameInput, text='mm', font=self.small_font).grid(row=1, column=2, sticky='W')
                  
        ttk.Label(frameInput, text='Focal length: ').grid(row=2, column=0, sticky='W')
        ttk.Entry(frameInput, textvariable=varFL, font=self.small_font,
                  background=C.DEFAULT_BG, width=12).grid(row=2, column=1, sticky='W')
        tk.Label(frameInput, text='mm', font=self.small_font).grid(row=2, column=2, sticky='W')
        
        ttk.Button(self.topAddNewTel, text='OK',
                   command=executeAddNew).pack(side='top', pady=(0, 10*C.scsy), expand=True)
        ttk.Label(self.topAddNewTel, textvariable=varMessageLabel, font=self.small_font,
                  background=C.DEFAULT_BG).pack(side='top', pady=(0, 10*C.scsy), expand=True)
        
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
            self.currentFrame().labelMessage.configure(foreground='navy')
            
            self.ISVal = np.arctan2(C.PIXEL_SIZE[self.cnum][0]*1e-3,
                                    C.FOCAL_LENGTH[self.tnum][0]*self.FLModVal)*180*3600/np.pi
                                    
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
        apc.setupWindow(topChangeFLMod, 220, 160)
        self.addIcon(topChangeFLMod)
        topChangeFLMod.focus_force()
        
        tk.Label(topChangeFLMod, text='Input the magnification factor of\nthe barlow or focal reducer:',
                 font=self.small_font).pack(side='top', pady=(12*C.scsy, 0), expand=True)
        entryFLMod = ttk.Entry(topChangeFLMod, textvariable=varFLMod, font=self.small_font,
                               background=C.DEFAULT_BG, width=10).pack(side='top', pady=12*C.scsy,
                                                                     expand=True)
        
        frameButtons = ttk.Frame(topChangeFLMod)
        frameButtons.pack(side='top', pady=(0, 12*C.scsy), expand=True)
        
        ttk.Button(frameButtons, text='OK', command=ok).grid(row=0, column=0)
        ttk.Button(frameButtons, text='Cancel',
                   command=lambda: topChangeFLMod.destroy()).grid(row=0, column=1)
                   
        ttk.Label(topChangeFLMod, textvariable=varMessageLabel,
                  anchor='center').pack(side='top', pady=(0, 3*C.scsy), expand=True)
        
        self.wait_window(topChangeFLMod)
        try:
            self.menubar.entryconfig(1, state='normal')
            self.menubar.entryconfig(2, state='normal')
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
        apc.setupWindow(self.topCModify, 280, 210)
        self.topCModify.focus_force()
        
        # Show a message if no camera data exists
        if self.noData:
        
            tk.Label(self.topCModify, text='No sensor data exists for\nthe currently active camera.\n\n' \
                                          + 'You can aquire sensor data\nwith the Image Analyser.',
                     font=self.small_font).pack(side='top', pady=20*C.scsy, expand=True)
            
            ttk.Button(self.topCModify, text='OK', command=lambda: self.topCModify.destroy())\
                .pack(side='top', pady=(0, 10*C.scsy), expand=True)
            
            self.wait_window(self.topCModify)
        
            try:
                self.menubar.entryconfig(1, state='normal')
                self.menubar.entryconfig(2, state='normal')
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
        paramlist = ['Gain', 'Read noise', 'Sat. cap.', 'Black level', 'White level', 'C.QE',
                     'Pixel size']
        self.isolist = self.currentCValues[11].split('-') if self.isDSLR else ['0'] # List of C.ISO values
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
                                     
        self.labelISO = ttk.Label(frameParam, text='C.ISO:', anchor='center', width=11)
        self.optionISO = ttk.OptionMenu(frameParam, self.varISO, None, *self.isolist,
                                        command=self.updateParamISO)
        
        self.labelGain = ttk.Label(frameParam, text='Gain:', anchor='center', width=11)
        self.optionGain = ttk.OptionMenu(frameParam, self.varGain, None, *self.gainlist,
                                         command=self.updateParamGain)
        
        self.labelRN = ttk.Label(frameParam, text='C.RN:', anchor='center', width=11)
        self.optionRN = ttk.OptionMenu(frameParam, self.varRN, None, *self.rnlist,
                                       command=self.updateParamRN)
        
        labelCurrent = ttk.Label(self.topCModify, textvariable=self.varCurrentCParamVal)
        
        labelSet = ttk.Label(self.topCModify, text='Input new value:', anchor='center')
        entryNewVal = ttk.Entry(self.topCModify, textvariable=self.varNewCParamVal,
                                font=self.small_font, background=C.DEFAULT_BG)
        
        buttonSet = ttk.Button(self.topCModify, text='Set value', command=self.setNewCamParamVal)
        
        errorModify = ttk.Label(self.topCModify, textvariable=self.varErrorModifyC, anchor='center')
        
        frameParam.pack(side='top', pady=(10*C.scsy, 0), expand=True)
        
        labelParam.grid(row=0, column=0)
        optionParam.grid(row=1, column=0)
        
        if self.isDSLR:
            self.labelISO.grid(row=0, column=1)
            self.optionISO.grid(row=1, column=1)
        elif len(self.gainlist) > 1:
            self.labelGain.grid(row=0, column=1)
            self.optionGain.grid(row=1, column=1)
        
        labelCurrent.pack(side='top', pady=10*C.scsy, expand=True)
        labelSet.pack(side='top', expand=True)
        entryNewVal.pack(side='top', pady=5*C.scsy, expand=True)
        buttonSet.pack(side='top', pady=5*C.scsy, expand=True)
        errorModify.pack(side='top', expand=True)
        
        self.currentFrame().varMessageLabel.set(\
        'Note: changing the value of a camera parameter will reset the application.')
        self.currentFrame().labelMessage.configure(foreground='navy')
        
        self.wait_window(self.topCModify)
        
        try:
            self.menubar.entryconfig(1, state='normal')
            self.menubar.entryconfig(2, state='normal')
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
            
        elif selected_param == 'C.QE':
        
            if self.hasQE:
                self.varCurrentCParamVal.set('Current value: ' + self.currentCValues[7].split('*')[0] \
                                             + (' (modified)' if '*' in self.currentCValues[7] else ''))
            else:
                self.varCurrentCParamVal.set('No value exists.')
            
        elif selected_param == 'Pixel size':
        
            self.varCurrentCParamVal.set('Current value: ' + self.currentCValues[8].split('*')[0] \
                                         + u' \u03bcm' \
                                         + (' (modified)' if '*' in self.currentCValues[8] else ''))
                                         
        elif selected_param == 'Horizontal resolution':
        
            self.varCurrentCParamVal.set('Current value: ' + self.currentCValues[9].split('*')[0] \
                                         + (' (modified)' if '*' in self.currentCValues[9] else ''))
                                         
        elif selected_param == 'Vertical resolution':
        
            self.varCurrentCParamVal.set('Current value: ' + self.currentCValues[10].split('*')[0] \
                                         + (' (modified)' if '*' in self.currentCValues[10] else ''))
    
    def updateParamISO(self, selected_iso):
    
        '''Update the label showing the current gain or read noise value when a new C.ISO is selected.'''
    
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
            C.GAIN[self.cnum][0][self.gain_idx] = float(newval)
            C.GAIN[self.cnum][1][self.gain_idx] = 1
            self.varCurrentCParamVal.set('Current value: ' + newval + ' e-/ADU (modified)')
            
        elif self.varCParam.get() == 'Read noise':
        
            self.rnlist[self.rn_idx] = newval + '*'
            file.write('\n%s,%s,%s' % (','.join(self.currentCValues[:3]),
                                       '-'.join(self.rnlist),
                                       ','.join(self.currentCValues[4:])))
            C.RN[self.cnum][0][self.rn_idx] = float(newval)
            C.RN[self.cnum][1][self.rn_idx] = 1
            self.varCurrentCParamVal.set('Current value: ' + newval + ' e- (modified)')
            
        elif self.varCParam.get() == 'Sat. cap.':
        
            self.satcaplist[self.gain_idx] = newval + '*'
            file.write('\n%s,%s,%s' % (','.join(self.currentCValues[:4]),
                                       '-'.join(self.satcaplist),
                                       ','.join(self.currentCValues[5:])))
            C.SAT_CAP[self.cnum][0][self.gain_idx] = int(newval)
            C.SAT_CAP[self.cnum][1][self.gain_idx] = 1
            self.varCurrentCParamVal.set('Current value: ' + newval + ' e- (modified)')
        
        elif self.varCParam.get() == 'Black level':
            self.bllist[self.gain_idx] = newval + '*'
            file.write('\n%s,%s,%s' % (','.join(self.currentCValues[:5]),
                                       '-'.join(self.bllist),
                                       ','.join(self.currentCValues[6:])))
            C.BLACK_LEVEL[self.cnum][0][self.gain_idx] = int(newval)
            C.BLACK_LEVEL[self.cnum][1][self.gain_idx] = 1
            self.varCurrentCParamVal.set('Current value: ' + newval + ' ADU (modified)')
            
        elif self.varCParam.get() == 'White level':
            
            self.wllist[self.gain_idx] = newval + '*'
            file.write('\n%s,%s,%s' % (','.join(self.currentCValues[:6]),
                                       '-'.join(self.wllist),
                                       ','.join(self.currentCValues[7:])))
            C.WHITE_LEVEL[self.cnum][0][self.gain_idx] = int(newval)
            C.WHITE_LEVEL[self.cnum][1][self.gain_idx] = 1
            self.varCurrentCParamVal.set('Current value: ' + newval + ' ADU (modified)')
            
        elif self.varCParam.get() == 'C.QE':
        
            file.write('\n%s,%s,%s' % (','.join(self.currentCValues[:7]),
                                       newval + '*',
                                       ','.join(self.currentCValues[8:])))
            C.QE[self.cnum][0] = float(newval)
            C.QE[self.cnum][1] = 1
            self.varCurrentCParamVal.set('Current value: ' + newval + ' (modified)')
            
        elif self.varCParam.get() == 'Pixel size':
        
            file.write('\n%s,%s,%s' % (','.join(self.currentCValues[:8]),
                                       newval + '*',
                                       ','.join(self.currentCValues[9:])))
                
            C.PIXEL_SIZE[self.cnum][0] = float(newval)
            C.PIXEL_SIZE[self.cnum][1] = 1
            self.varCurrentCParamVal.set('Current value: ' + newval + u' \u03bcm (modified)')
            
        elif self.varCParam.get() == 'Horizontal resolution':
        
            file.write('\n%s,%d*,%s' % (','.join(self.currentCValues[:9]),
                                       float(newval),
                                       ','.join(self.currentCValues[10:])))
                
            C.RES_X[self.cnum][0] = int(float(newval))
            C.RES_X[self.cnum][1] = 1
            self.varCurrentCParamVal.set('Current value: ' + newval + ' (modified)')
            
        elif self.varCParam.get() == 'Vertical resolution':
        
            file.write('\n%s,%d*' % (','.join(self.currentCValues[:10]), float(newval)))
            if self.isDSLR: file.write(',%s' % (self.currentCValues[11]))
                
            C.RES_Y[self.cnum][0] = int(float(newval))
            C.RES_Y[self.cnum][1] = 1
            self.varCurrentCParamVal.set('Current value: ' + newval + ' (modified)')
        
        for i in range((idx + 1), len(self.lines)):
            file.write('\n' + self.lines[i])
            
        file.close()
        
        # Reset all frames in order for the parameter change to take effect

        self.hasQE = C.QE[self.cnum][0] != 'NA'
        
        calframe.setDefaultValues()
        simframe.setDefaultValues()
        plotframe.setDefaultValues()
        
        calframe.reconfigureNonstaticWidgets()
        simframe.reconfigureNonstaticWidgets()
        plotframe.reconfigureNonstaticWidgets()
        
        self.currentFrame().varMessageLabel.set('Camera parameter modified.')
        self.currentFrame().labelMessage.configure(foreground='navy')
        
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
        apc.setupWindow(self.topTModify, 280, 210)
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
                                font=self.small_font, background=C.DEFAULT_BG)
        
        buttonSet = ttk.Button(self.topTModify, text='Set value', command=self.setNewTelParamVal)
        
        errorModify = ttk.Label(self.topTModify, textvariable=self.varErrorModifyT, anchor='center')
        
        frameParam.pack(side='top', pady=(10*C.scsy, 0), expand=True)
        
        labelParam.grid(row=0, column=0)
        optionParam.grid(row=1, column=0)
        
        labelCurrent.pack(side='top', pady=10*C.scsy, expand=True)
        labelSet.pack(side='top', expand=True)
        entryNewVal.pack(side='top', pady=5*C.scsy, expand=True)
        buttonSet.pack(side='top', pady=5*C.scsy, expand=True)
        errorModify.pack(side='top', expand=True)
        
        self.currentFrame().varMessageLabel.set(\
        'Note: changing the value of a telescope/lens parameter will reset the application.')
        self.currentFrame().labelMessage.configure(foreground='navy')
        
        self.wait_window(self.topTModify)
        
        try:
            self.menubar.entryconfig(1, state='normal')
            self.menubar.entryconfig(2, state='normal')
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
                
            C.FOCAL_LENGTH[self.tnum][0] = float(newval)
            C.FOCAL_LENGTH[self.tnum][1] = 1
            self.varCurrentTParamVal.set('Current value: ' + newval + ' mm (modified)')
        
        elif self.varTParam.get() == 'Aperture':
        
            file.write('\n%s,%s,%s' % (self.currentTValues[0], self.currentTValues[1], newval + '*'))
                
            C.APERTURE[self.tnum][0] = float(newval)
            C.APERTURE[self.tnum][1] = 1
            self.varCurrentTParamVal.set('Current value: ' + newval + ' mm (modified)')
        
        for i in range((idx + 1), len(self.lines)):
            file.write('\n' + self.lines[i])
            
        file.close()
        
        calframe.setDefaultValues()
        simframe.setDefaultValues()
        plotframe.setDefaultValues()
        
        self.currentFrame().varMessageLabel.set('Telescope parameter modified.')
        self.currentFrame().labelMessage.configure(foreground='navy')
        
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
                calframe.varMessageLabel.set('Data must be calculated before it can be transferred.')
                calframe.labelMessage.configure(foreground='crimson')
                return None
        
            if calframe.varTransfLim.get():
                simframe.varLF.set('%g' % (apc.convSig(calframe.tf, True) if self.lumSignalType.get() \
                                   else calframe.tf))
                calframe.varMessageLabel.set('Target flux transferred as limit flux to Image Simulator.')
                calframe.labelMessage.configure(foreground='crimson')
                return None
        
            # Set values
            simframe.gain_idx = calframe.gain_idx
            simframe.rn_idx = calframe.rn_idx
            simframe.varISO.set(C.ISO[self.cnum][calframe.gain_idx])
            simframe.varGain.set(C.GAIN[self.cnum][0][calframe.gain_idx])
            simframe.varRN.set(C.RN[self.cnum][0][calframe.rn_idx])
            simframe.varExp.set('%g' % calframe.exposure)
            simframe.varDF.set('%g' % calframe.df)
            simframe.varSF.set('%g' % (apc.convSig(calframe.sf, True) if self.lumSignalType.get() \
                                                                    else calframe.sf))
            simframe.varTF.set(0 if calframe.tf == 0 \
                               else ('%g' % (apc.convSig(calframe.tf, True) if self.lumSignalType.get() \
                                                                          else calframe.tf)))
            simframe.varSubs.set(1)
            
            simframe.dataCalculated = False # Previously calculated data is no longer valid
            simframe.updateSensorLabels() # Update sensor info labels in case the C.ISO has changed
            simframe.emptyInfoLabels() # Clear other info labels
            calframe.varMessageLabel.set('Data transferred to Image Simulator.' \
                                         if calframe.varUseDark.get() \
                                         else 'Data transferred. Note that transferred signal ' \
                                       + 'data does not contain a separate value for dark current.')
            calframe.labelMessage.configure(foreground='navy')
        
        # If Plotting Tool is the active frame
        elif self.plMode.get():
        
            simframe.setDefaultValues() # Reset Image Simulator frame
        
            # Set values that are not invalid
            
            simframe.gain_idx = plotframe.gain_idx
            simframe.rn_idx = plotframe.rn_idx
            simframe.varISO.set(C.ISO[self.cnum][plotframe.gain_idx])
            simframe.varGain.set(C.GAIN[self.cnum][0][plotframe.gain_idx])
            simframe.varRN.set(C.RN[self.cnum][0][plotframe.rn_idx])
            
            
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
            
            try:
                simframe.varLF.set('%g' % plotframe.varLF.get())
            except ValueError:
                pass
            
            simframe.varSubs.set(1)
            
            simframe.updateSensorLabels() # Update sensor info labels in case the C.ISO has changed
            simframe.emptyInfoLabels() # Clear other info labels
            plotframe.varMessageLabel.set('Input transferred to Image Simulator.')
            plotframe.labelMessage.configure(foreground='navy')
        
    def transferToPlot(self):
    
        '''Transfer relevant inputted or calculated values to widgets in the Plotting Tool frame.'''
    
        calframe = self.frames[ImageCalculator]
        simframe = self.frames[ImageSimulator]
        plotframe = self.frames[PlottingTool]
        
        # If Image Calculator is the active frame
        if self.calMode.get():
        
            # Show error message if flux data hasn't been calculated
            if not calframe.dataCalculated:
                calframe.varMessageLabel.set('Data must be calculated before it can be transferred.')
                calframe.labelMessage.configure(foreground='crimson')
                return None
        
            if calframe.varTransfLim.get() and self.isDSLR:
                plotframe.varLF.set('%g' % (apc.convSig(calframe.tf, True) if self.lumSignalType.get() \
                                   else calframe.tf))
                calframe.varMessageLabel.set('Target flux transferred as limit flux to Plotting Tool.')
                calframe.labelMessage.configure(foreground='navy')
                return None
        
            # Set values
            plotframe.gain_idx = calframe.gain_idx
            plotframe.rn_idx = calframe.rn_idx
            plotframe.varISO.set(C.ISO[self.cnum][calframe.gain_idx])
            plotframe.varGain.set(C.GAIN[self.cnum][0][calframe.gain_idx])
            plotframe.varRN.set(C.RN[self.cnum][0][calframe.rn_idx])
            plotframe.varExp.set('%g' % calframe.exposure)
            plotframe.varDF.set('%g' % calframe.df)
            plotframe.varSF.set('%g' % (apc.convSig(calframe.sf, True) if self.lumSignalType.get() \
                                                                     else calframe.sf))
            plotframe.varTF.set(0 if calframe.tf == 0 \
                                else ('%g' % (apc.convSig(calframe.tf, True) if self.lumSignalType.get() \
                                                                          else calframe.tf)))
            
            plotframe.ax.cla() # Clear plot
            calframe.varMessageLabel.set('Data transferred to Plotting Tool.' \
                                         if calframe.varUseDark.get() \
                                         else 'Data transferred. Note that transferred signal data ' \
                                            + 'does not contain a separate value for dark current.')
            calframe.labelMessage.configure(foreground='navy')
        
        # If Plotting Tool is the active frame
        elif self.simMode.get():
        
            plotframe.setDefaultValues() # Reset Plotting Tool frame
        
            # Set values that are not invalid
        
            plotframe.gain_idx = simframe.gain_idx
            plotframe.rn_idx = simframe.rn_idx
            plotframe.varISO.set(C.ISO[self.cnum][simframe.gain_idx])
            plotframe.varGain.set(C.GAIN[self.cnum][0][simframe.gain_idx])
            plotframe.varRN.set(C.RN[self.cnum][0][simframe.rn_idx])
            
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
            
            try:
                plotframe.varLF.set('%g' % simframe.varLF.get())
            except ValueError:
                pass
            
            plotframe.ax.cla() # Clear plot
            simframe.varMessageLabel.set('Input transferred to Plotting Tool.')
            simframe.labelMessage.configure(foreground='navy')
    
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
        simframe.varLFLabel.set('e-/s')
        
        plotframe.varSFLabel.set('e-/s')
        plotframe.varTFLabel.set('e-/s')
        plotframe.varLFLabel.set('e-/s')
        
        # Change tooltips
        if self.tooltipsOn.get():
            apc.createToolTip(calframe.labelSF2, C.TTSFElectron if calframe.varUseDark.get() \
                                             or self.isDSLR else C.TTDSFElectron, self.tt_fs)
            apc.createToolTip(calframe.labelTF2, C.TTTFElectron, self.tt_fs)
            apc.createToolTip(simframe.entrySF, C.TTSFElectron, self.tt_fs)
            apc.createToolTip(simframe.entryTF, C.TTTFElectron, self.tt_fs)
            apc.createToolTip(simframe.entryLF, C.TTLFElectron, self.tt_fs)
            apc.createToolTip(plotframe.entrySF, C.TTSFElectron, self.tt_fs)
            apc.createToolTip(plotframe.entryTF, C.TTTFElectron, self.tt_fs)
            apc.createToolTip(plotframe.entryLF, C.TTLFElectron, self.tt_fs)
        
        # Change displayed flux values if they have been calculated
        if calframe.dataCalculated:
            calframe.varSFInfo.set('%.3g' % (calframe.sf)) 
            calframe.varTFInfo.set('-' if calframe.tf == 0 else '%.3g' % (calframe.tf))
            
            calframe.labelSF2.configure(background=C.DEFAULT_BG, foreground='black')
            calframe.labelTF2.configure(background=C.DEFAULT_BG, foreground='black')
            
        try:
            sig = simframe.varSF.get()
            simframe.varSF.set('%.3g' % apc.convSig(sig, False))
        except:
            pass
                
        try:
            sig = simframe.varTF.get()
            simframe.varTF.set('%.3g' % apc.convSig(sig, False))
        except:
            pass
                
        try:
            sig = simframe.varLF.get()
            simframe.varLF.set('%.3g' % apc.convSig(sig, False))
        except:
            pass
               
        try:
            sig = plotframe.varSF.get()
            plotframe.varSF.set('%.3g' % apc.convSig(sig, False))
        except:
            pass
                
        try:
            sig = plotframe.varTF.get()
            plotframe.varTF.set('%.3g' % apc.convSig(sig, False))
        except:
            pass
               
        try:
            sig = plotframe.varLF.get()
            plotframe.varLF.set('%.3g' % apc.convSig(sig, False))
        except:
            pass
            
        self.currentFrame().varMessageLabel.set(\
                       'Using electron flux as signal quantity. Relevant values have been converted.')
        self.currentFrame().labelMessage.configure(foreground='navy')
            
    def setLumSignalType(self):
    
        '''Use luminance as signal quantity.'''
    
        # Do nothing if luminance is already used
        if not self.electronSignalType.get():
            self.lumSignalType.set(1)
            return None
            
        if not self.hasQE:
            self.lumSignalType.set(0)
            self.currentFrame().varMessageLabel\
                                .set('Camera doesn\'t have C.QE data. Cannot estimate luminance.')
            self.currentFrame().labelMessage.configure(foreground='crimson')
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
        simframe.varLFLabel.set(u'mag/arcsec\u00B2')
        
        plotframe.varSFLabel.set(u'mag/arcsec\u00B2')
        plotframe.varTFLabel.set(u'mag/arcsec\u00B2')
        plotframe.varLFLabel.set(u'mag/arcsec\u00B2')
        
        # Change tooltips
        if self.tooltipsOn.get():
            apc.createToolTip(calframe.labelSF2, C.TTSFLum if calframe.varUseDark.get() \
                                             or self.isDSLR else C.TTDSFPhoton, self.tt_fs)
            apc.createToolTip(calframe.labelTF2, C.TTTFLum, self.tt_fs)
            apc.createToolTip(simframe.entrySF, C.TTSFLum, self.tt_fs)
            apc.createToolTip(simframe.entryTF, C.TTTFLum, self.tt_fs)
            apc.createToolTip(simframe.entryLF, C.TTLFLum, self.tt_fs)
            apc.createToolTip(plotframe.entrySF, C.TTSFLum, self.tt_fs)
            apc.createToolTip(plotframe.entryTF, C.TTTFLum, self.tt_fs)
            apc.createToolTip(plotframe.entryLF, C.TTLFLum, self.tt_fs)
        
        # Change displayed flux values if they have been calculated
        if calframe.dataCalculated:
        
            sf = apc.convSig(calframe.sf, True)
            calframe.varSFInfo.set('%.4g' % sf)
            calframe.setLumColour(sf, calframe.labelSF2)
            
            if calframe.tf == 0:
                calframe.varTFInfo.set('-')
                calframe.labelTF2.configure(background=C.DEFAULT_BG, foreground='black')
            else:
                tf = apc.convSig(calframe.tf, True)
                calframe.varTFInfo.set('%.4g' % tf)
                calframe.setLumColour(tf, calframe.labelTF2) 
                
        try:
            sig = simframe.varSF.get()
            simframe.varSF.set('%.4g' % apc.convSig(sig, True))
        except:
            pass
                
        try:
            sig = simframe.varTF.get()
            simframe.varTF.set('%.4g' % apc.convSig(sig, True))
        except:
            pass
                
        try:
            sig = simframe.varLF.get()
            simframe.varLF.set('%.4g' % apc.convSig(sig, True))
        except:
            pass
               
        try:
            sig = plotframe.varSF.get()
            plotframe.varSF.set('%.4g' % apc.convSig(sig, True))
        except:
            pass
                
        try:
            sig = plotframe.varTF.get()
            plotframe.varTF.set('%.4g' % apc.convSig(sig, True))
        except:
            pass
               
        try:
            sig = plotframe.varLF.get()
            plotframe.varLF.set('%.4g' % apc.convSig(sig, True))
        except:
            pass
            
        self.currentFrame().varMessageLabel.set(\
                         'Using luminance as signal quantity. Relevant values have been converted.')
        self.currentFrame().labelMessage.configure(foreground='navy')

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
            self.currentFrame().labelMessage.configure(foreground='navy')
            
        else:
                                       
            self.frames[ImageCalculator].activateTooltips()
            self.frames[ImageSimulator].activateTooltips()
            self.frames[PlottingTool].activateTooltips()
            
            self.tooltipsOn.set(1)
    
            self.currentFrame().varMessageLabel.set('Tooltips activated.')
            self.currentFrame().labelMessage.configure(foreground='navy')

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
            self.currentFrame().labelMessage.configure(foreground='navy')
            
        else:
        
            self.menuTT.insert_command(1, label='Turn off as default', command=self.toogleDefaultTTState)
            
            file.write(lines[-1].split(',')[0] + ', Tooltips: on,' + lines[-1].split(',')[2])
            
            self.defaultTTState.set(1)
            
            self.currentFrame().varMessageLabel.set('Default tooltip state: on')
            self.currentFrame().labelMessage.configure(foreground='navy')
            
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
        apc.setupWindow(topFS, 150, 130)
        self.addIcon(topFS)
        topFS.focus_force()
        
        labelFS = ttk.Label(topFS, text='Choose font size:', anchor='center')
        optionFS = ttk.OptionMenu(topFS, varFS, None, *fs_vals)
        buttonFS = ttk.Button(topFS, text='OK', command=lambda: apc.setNewFS(self, self.cnum, self.tnum,
                              varFS.get()))
        
        labelFS.pack(side='top', pady=(12*C.scsy, 0), expand=True)
        optionFS.pack(side='top', pady=12*C.scsy, expand=True)
        buttonFS.pack(side='top', pady=(0, 12*C.scsy), expand=True)
    
        self.currentFrame().varMessageLabel.set('Warning: changing font size ' \
                                                + 'will restart the application.')
        self.currentFrame().labelMessage.configure(foreground='crimson')
                                                            
        self.wait_window(topFS)
        try:
            self.menubar.entryconfig(1, state='normal')
            self.menubar.entryconfig(2, state='normal')
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
        apc.setupWindow(topWarning, 300, 145)
        topWarning.focus_force()
        
        tk.Label(topWarning, text='Are you sure you want to\nclear the inputted information?',
                 font=self.small_font).pack(side='top', pady=(20*C.scsy, 5*C.scsy), expand=True)
        
        frameButtons = ttk.Frame(topWarning)
        frameButtons.pack(side='top', expand=True, pady=(0, 10*C.scsy))
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
        self.frames[FOVCalculator].setFOV()
    
    def setDegAngleUnit(self):
    
        '''Use [degree] as angle unit.'''
    
        # Do nothing if deg is already used
        if not self.dmsAngleUnit.get():
            self.degAngleUnit.set(1)
            return None
            
        self.dmsAngleUnit.set(0)
        self.degAngleUnit.set(1)
        
        self.frames[ImageAnalyser].updateAngle()
        self.frames[FOVCalculator].setFOV()
   