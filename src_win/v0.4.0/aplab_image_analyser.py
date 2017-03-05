# -*- coding: utf-8 -*-

import Tkinter as tk
import ttk
import tkFileDialog
import sys
import os
import subprocess
import numpy as np
import matplotlib
import FileDialog # Needed for matplotlib
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import pyfits
import exifread
import aplab_common as apc
from aplab_common import C

matplotlib.use("TkAgg") # Use TkAgg backend
matplotlib.rc('font', family='Tahoma') # Set plot font

class ImageAnalyser(ttk.Frame):

    def __init__(self, parent, controller):
    
        '''Initialize Image Analyser frame.'''
    
        ttk.Frame.__init__(self, parent)
        
        self.cont = controller
        
        self.cont.protocol('WM_DELETE_WINDOW', lambda: self.deleteTemp(True))
        
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
        self.useGreen = None # Used to decide which CFA colour to extract
        self.CFAPattern = None # Used to decide the CFA pattern of the colour camera
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
        
        frameLeft.pack(side='left', fill='both', padx=(30*C.scsx, 0))
        frameRight.pack(side='right', fill='both', padx=(30*C.scsx, 0), expand=True)
        
        frameMessage.pack(side='bottom', fill='x')
        
        # *** Header frame ***
        
        labelHeader = ttk.Label(frameHeader, text='Image Analyser', font=self.cont.large_font,
                                anchor='center')
        
        frameNames = ttk.Frame(frameHeader)
        labelCamName = ttk.Label(frameNames, textvariable=self.cont.varCamName, 
                                 font=self.cont.smallbold_font, foreground='darkslategray', 
                                 anchor='center')
        labelTelName = ttk.Label(frameNames, textvariable=self.cont.varTelName, 
                                 font=self.cont.smallbold_font, foreground='darkslategray',
                                 anchor='center')
        labelFLMod = ttk.Label(frameNames, textvariable=self.cont.varFLMod, foreground='darkslategray', 
                                 font=self.cont.smallbold_font, anchor='center')
        
        labelHeader.pack(side='top', pady=3*C.scsy)
        
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
        self.radioCCDc = ttk.Radiobutton(frameType, text='Colour CCD', variable=self.varCCDType,
                                         value='colour', command=self.changeCCDType)
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
                                    height=200*C.scsy)
        
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
        
        labelType.pack(side='top', pady=(10*C.scsy, 0))
        frameType.pack(side='top')
        
        labelAdd.pack(side='top', pady=(10*C.scsy, 0))
        self.optionAdd.pack(side='top', pady=(5*C.scsy, 5*C.scsy))
        self.buttonAdd.pack(side='top')
        
        labelFiles.pack(side='top', pady=(10*C.scsy, 5*C.scsy))
        self.frameFiles.pack(side='top', fill='both', expand=True)
        
        self.buttonClear.pack(side='top', pady=(10*C.scsy, 5*C.scsy))
        self.buttonCompute.pack(side='top', pady=(0, 10*C.scsy))
        
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
        self.labelMessage.pack(anchor='w', padx=(5*C.scsx, 0))
        
        
        self.labelList = [self.labelBias1, self.labelBias2, self.labelDark1, self.labelDark2,
                          self.labelFlat1, self.labelFlat2, self.labelLight, self.labelSaturated]
                          
        self.labelNames = {self.labelBias1 : 'temp_bias1', self.labelBias2 : 'temp_bias2', 
                           self.labelDark1 : 'temp_dark1', self.labelDark2 : 'temp_dark2',
                           self.labelFlat1 : 'temp_flat1', self.labelFlat2 : 'temp_flat2', 
                           self.labelLight : 'temp_light', self.labelSaturated : 'temp_saturated'}
                          
        # *** Right-click menu ***
        
        self.menuRC = tk.Menu(self.canvasDisplay, tearoff=0)
        self.menuRC.add_command(label='Show at 1:1 scale', command=self.useFullImage)
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
        
    def loadImage(self, label, filename=False):
    
        '''Create an image resized to fit the window.'''
        
        self.varMessageLabel.set('Reading temporary image file..' if not filename \
                                               else '%s - Reading temporary image file..' % filename)
        self.labelMessage.configure(foreground='navy')
        self.labelMessage.update_idletasks()
        
        pil_img = Image.open(self.labelNames[label] + '.jpg')
        
        self.photo_img = ImageTk.PhotoImage(pil_img)
        
        if self.showResized:
            
            self.varMessageLabel.set('Resizing..' if not filename else '%s - Resizing..' % filename)
            self.labelMessage.configure(foreground='navy')
            self.labelMessage.update_idletasks()
            
            w, h = pil_img.size
            f = np.min([(self.scrollbarCanvHor.winfo_width() - 17.0)/w,
                        self.scrollbarCanvVer.winfo_height()/float(h)])
                        
            self.photo_img_res = ImageTk.PhotoImage(pil_img.resize((int(round(f*w)), int(round(f*h))), 
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
    
        label.stretched_img = None
        label.exposure = None
        label.iso = None
    
    def addImage(self):
    
        '''Add image file and show name in list.'''
        
        self.disableWidgets()
    
        type = self.varImType.get()
        
        supportedformats = self.supportedformats if self.cont.isDSLR \
                                                 else [self.supportedformats[1]]
        
        if type == 'Bias':
        
            # Show error if two bias frames are already added
            if self.displayed_bias == 2:
                self.varMessageLabel.set('Cannot have more than 2 bias frames.')
                self.labelMessage.configure(foreground='crimson')
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
                self.labelMessage.configure(foreground='crimson')
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
                    
                    self.displayed_bias = 1
                    
                    # Display header and file name
                    
                    self.varBias1Label.set(self.adjustName(self.labelBias1, filename))
                    self.varBiasHLabel.set('Bias frame')
                    
                    self.frameBias.pack(side='top', fill='x', anchor='w')
                    self.labelBiasH.pack(side='top', fill='x', anchor='w')
                    self.labelBias1.pack(side='top', fill='x', anchor='w')
                    
                    # Show canvas if this is the first added file
                    if self.noInput: self.showCanvas()
            
                    self.showImage(self.labelBias1, filename=filename)
                    
                    self.varMessageLabel.set('Bias frame added.')
                    self.labelMessage.configure(foreground='navy')
                
                # If one file is already added
                else:
                
                    bias2path = biasfiles[0]
                    
                    filename = bias2path.split('/')[-1]
                    
                    # Show error if the same file is already added
                    if filename == self.varBias1Label.get():
                        self.varMessageLabel.set('This bias frame is already added.')
                        self.labelMessage.configure(foreground='crimson')
                        self.enableWidgets()
                        return None
                    
                    # Extract image data and store as attributes for bias 2 label
                    try:
                        self.getImage(self.labelBias2, bias2path, filename, 'bias',
                                      compare=self.labelBias1)
                    except:
                        self.enableWidgets()
                        return None
                    
                    self.displayed_bias = 2
                    
                    # Display file name after the existing one
                    
                    self.varBias2Label.set(self.adjustName(self.labelBias2, filename))
                    self.varBiasHLabel.set('Bias frames')
                    
                    self.labelBias2.pack(side='top', fill='x', anchor='w')
                    
                    self.showImage(self.labelBias2, filename=filename)
                    
                    # Cycle image type optionmenu to flat frames
                    self.varImType.set('Flat')
                    self.updateFrameButtonText('Flat')
                    
                    self.varMessageLabel.set('Bias frame added.')
                    self.labelMessage.configure(foreground='navy')
            
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
                    
                self.displayed_bias = 1
                    
                self.varBias1Label.set(self.adjustName(self.labelBias1, filename1))
                self.varBiasHLabel.set('Bias frames')
                
                self.frameBias.pack(side='top', fill='x', anchor='w')
                self.labelBiasH.pack(side='top', fill='x', anchor='w')
                self.labelBias1.pack(side='top', fill='x', anchor='w')
                
                if self.noInput: self.showCanvas()
                
                self.showImage(self.labelBias1, filename=filename1)
                    
                self.update() # Update window to show changes
                
                try:
                    self.getImage(self.labelBias2, bias2path, filename2, 'bias',
                                  compare=self.labelBias1)
                except:
                    self.enableWidgets()
                    return None
                
                self.displayed_bias = 2
                
                self.varBias2Label.set(self.adjustName(self.labelBias2, filename2))
                
                self.labelBias2.pack(side='top', fill='x', anchor='w')
                
                self.showImage(self.labelBias2, filename=filename2)
                
                self.varImType.set('Flat')
                self.updateFrameButtonText('Flat')
                
                self.varMessageLabel.set('Bias frames added.')
                self.labelMessage.configure(foreground='navy')
        
        elif type == 'Dark':
        
            if self.displayed_dark == 2:
                self.varMessageLabel.set('Cannot have more than 2 dark frames.')
                self.labelMessage.configure(foreground='crimson')
                self.enableWidgets()
                return None
        
            darkfiles = tkFileDialog.askopenfilenames(filetypes=supportedformats,
                                                      initialdir=self.previousPath)
            
            if darkfiles == '':
                self.enableWidgets()
                return None
            
            if len(darkfiles) > 2 or (len(darkfiles) > 1 and self.displayed_dark == 1):
                self.varMessageLabel.set('Cannot have more than 2 dark frames.')
                self.labelMessage.configure(foreground='crimson')
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
                    
                    self.displayed_dark = 1
                    
                    self.varDark1Label.set(self.adjustName(self.labelDark1, filename))
                    self.varDarkHLabel.set('Dark frame')
                    
                    self.frameDark.pack(side='top', fill='x', anchor='w')
                    self.labelDarkH.pack(side='top', fill='x', anchor='w')
                    self.labelDark1.pack(side='top', fill='x', anchor='w')
                    
                    if self.noInput: self.showCanvas()
            
                    self.showImage(self.labelDark1, filename=filename)
                    
                    self.varMessageLabel.set('Dark frame added.')
                    self.labelMessage.configure(foreground='navy')
                
                else:
                
                    dark2path = darkfiles[0]
                    
                    filename = dark2path.split('/')[-1]
                    
                    if filename == self.varDark1Label.get():
                        self.varMessageLabel.set('This dark frame is already added.')
                        self.labelMessage.configure(foreground='crimson')
                        self.enableWidgets()
                        return None
                    
                    try:
                        self.getImage(self.labelDark2, dark2path, filename, 'dark',
                                      compare=self.labelDark1)
                    except:
                        self.enableWidgets()
                        return None
                    
                    self.displayed_dark = 2
                    
                    self.varDark2Label.set(self.adjustName(self.labelDark2, filename))
                    self.varDarkHLabel.set('Dark frames')
                    
                    self.labelDark2.pack(side='top', fill='x', anchor='w')
                    
                    self.showImage(self.labelDark2, filename=filename)
                    
                    self.varImType.set('Light')
                    self.updateFrameButtonText('Light')
                    
                    self.varMessageLabel.set('Dark frame added.')
                    self.labelMessage.configure(foreground='navy')
            
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
                
                self.displayed_dark = 1
                    
                self.varDark1Label.set(self.adjustName(self.labelDark1, filename1))
                self.varDarkHLabel.set('Dark frames')
                
                self.frameDark.pack(side='top', fill='x', anchor='w')
                self.labelDarkH.pack(side='top', fill='x', anchor='w')
                self.labelDark1.pack(side='top', fill='x', anchor='w')
                
                if self.noInput: self.showCanvas()
                
                self.showImage(self.labelDark1, filename=filename1)
                
                self.update()
                    
                try:
                    self.getImage(self.labelDark2, dark2path, filename2, 'dark',
                                  compare=self.labelDark1)
                except:
                    self.enableWidgets()
                    return None
                
                self.displayed_dark = 2
                
                self.varDark2Label.set(self.adjustName(self.labelDark2, filename2))
                
                self.labelDark2.pack(side='top', fill='x', anchor='w')
                
                self.showImage(self.labelDark2, filename=filename2)
                    
                self.varImType.set('Light')
                self.updateFrameButtonText('Light')
                
                self.varMessageLabel.set('Dark frames added.')
                self.labelMessage.configure(foreground='navy')
            
        elif type == 'Flat':
        
            if self.displayed_flat == 2:
                self.varMessageLabel.set('Cannot have more than 2 flat frames.')
                self.labelMessage.configure(foreground='crimson')
                self.enableWidgets()
                return None
        
            flatfiles = tkFileDialog.askopenfilenames(filetypes=supportedformats,
                                                      initialdir=self.previousPath)
            
            if flatfiles == '':
                self.enableWidgets()
                return None
            
            if len(flatfiles) > 2 or (len(flatfiles) > 1 and self.displayed_flat == 1):
                self.varMessageLabel.set('Cannot have more than 2 flat frames.')
                self.labelMessage.configure(foreground='crimson')
                self.enableWidgets()
                return None
                
            self.previousPath = '/'.join(flatfiles[-1].split('/')[:-1])
                
            if len(flatfiles) == 1:
            
                if self.displayed_flat == 0:
                
                    flat1path = flatfiles[0]
                    
                    filename = flat1path.split('/')[-1]
                    
                    try:
                        self.getImage(self.labelFlat1, flat1path, filename, 'flat',
                                      splitCFA=(self.cont.isDSLR or self.varCCDType.get() == 'colour'))
                    except:
                        self.enableWidgets()
                        return None
                    
                    self.displayed_flat = 1
                        
                    colour = ' (green)' if self.useGreen == True \
                                       else (' (red)' if self.useGreen == False else '')
                    
                    self.varFlat1Label.set(self.adjustName(self.labelFlat1, filename + colour))
                    self.varFlatHLabel.set('Flat frame')
                    
                    self.frameFlat.pack(side='top', fill='x', anchor='w')
                    self.labelFlatH.pack(side='top', fill='x', anchor='w')
                    self.labelFlat1.pack(side='top', fill='x', anchor='w')
                    
                    if self.noInput: self.showCanvas()
                    
                    self.showImage(self.labelFlat1, filename=filename)
                    
                    self.varMessageLabel.set('Flat frame added.')
                    self.labelMessage.configure(foreground='navy')
                
                else:
                
                    flat2path = flatfiles[0]
                    
                    filename = flat2path.split('/')[-1]
                    
                    if filename == self.varFlat1Label.get().split(' (')[0]:
                        self.varMessageLabel.set('This flat frame is already added.')
                        self.labelMessage.configure(foreground='crimson')
                        self.enableWidgets()
                        return None
                        
                    colour = ' (green)' if self.useGreen == True \
                                       else (' (red)' if self.useGreen == False else '')
                    
                    try:
                        self.getImage(self.labelFlat2, flat2path, filename, 'flat',
                                      splitCFA=(self.cont.isDSLR or self.varCCDType.get() == 'colour'),
                                      compare=self.labelFlat1)
                    except:
                        self.enableWidgets()
                        return None
                    
                    self.displayed_flat = 2
                    
                    self.varFlat2Label.set(self.adjustName(self.labelFlat2, filename + colour))
                    self.varFlatHLabel.set('Flat frames')
                    
                    self.labelFlat2.pack(side='top', fill='x', anchor='w')
                    
                    self.showImage(self.labelFlat2, filename=filename)
                    
                    self.varImType.set('Saturated')
                    self.updateFrameButtonText('Saturated')
                    
                    self.varMessageLabel.set('Flat frame added.')
                    self.labelMessage.configure(foreground='navy')
                    
            else:
            
                flat1path = flatfiles[0]
                flat2path = flatfiles[1]
                
                filename1 = flat1path.split('/')[-1]
                filename2 = flat2path.split('/')[-1]
                
                try:
                    self.getImage(self.labelFlat1, flat1path, filename1, 'flat',
                                  splitCFA=(self.cont.isDSLR or self.varCCDType.get() == 'colour'))
                except:
                    self.enableWidgets()
                    return None
                
                self.displayed_flat = 1
                
                colour = ' (green)' if self.useGreen == True \
                                   else (' (red)' if self.useGreen == False else '')
                    
                self.varFlat1Label.set(self.adjustName(self.labelFlat1, filename1 + colour))
                self.varFlatHLabel.set('Flat frames')
                
                self.frameFlat.pack(side='top', fill='x', anchor='w')
                self.labelFlatH.pack(side='top', fill='x', anchor='w')
                self.labelFlat1.pack(side='top', fill='x', anchor='w')
                
                if self.noInput: self.showCanvas()
                
                self.showImage(self.labelFlat1, filename=filename1)
                    
                self.update()
                    
                try:
                    self.getImage(self.labelFlat2, flat2path, filename2, 'flat',
                                  splitCFA=(self.cont.isDSLR or self.varCCDType.get() == 'colour'),
                                  compare=self.labelFlat1)
                except:
                    self.enableWidgets()
                    return None
                
                self.displayed_flat = 2
                
                self.varFlat2Label.set(self.adjustName(self.labelFlat2, filename2 + colour))
                
                self.labelFlat2.pack(side='top', fill='x', anchor='w')
                
                self.showImage(self.labelFlat2, filename=filename2)
                    
                self.varImType.set('Saturated')
                self.updateFrameButtonText('Saturated')
                    
                self.varMessageLabel.set('Flat frames added.')
                self.labelMessage.configure(foreground='navy')
                
        elif type == 'Light':
        
            if self.displayed_light == 1:
                self.varMessageLabel.set('Cannot have more than 1 light frame.')
                self.labelMessage.configure(foreground='crimson')
                self.enableWidgets()
                return None
        
            lightfiles = tkFileDialog.askopenfilenames(filetypes=supportedformats,
                                                       initialdir=self.previousPath)
            
            if lightfiles == '':
                self.enableWidgets()
                return None
            
            if len(lightfiles) > 1:
                self.varMessageLabel.set('Cannot have more than 1 light frame.')
                self.labelMessage.configure(foreground='crimson')
                self.enableWidgets()
                return None
                
            self.previousPath = '/'.join(lightfiles[-1].split('/')[:-1])
                
            lightpath = lightfiles[0]
                    
            filename = lightpath.split('/')[-1]
                    
            try:
                self.getImage(self.labelLight, lightpath, filename, 'light',
                              splitCFA=(self.cont.isDSLR or self.varCCDType.get() == 'colour'))
            except:
                self.enableWidgets()
                return None
                    
            self.displayed_light = 1
                
            colour = ' (green)' if self.useGreen == True \
                               else (' (red)' if self.useGreen == False else '')
                    
            self.varLightLabel.set(self.adjustName(self.labelLight, filename + colour))
                    
            self.labelLightH.pack(side='top', fill='x', anchor='w')
            self.labelLight.pack(side='top', fill='x', anchor='w')
                    
            if self.noInput: self.showCanvas()
                    
            self.showImage(self.labelLight, filename=filename)
                    
            self.varImType.set('Dark')
            self.updateFrameButtonText('Dark')
                    
            self.varMessageLabel.set('Light frame added.')
            self.labelMessage.configure(foreground='navy')
            
        elif type == 'Saturated':
        
            if self.displayed_saturated == 1:
                self.varMessageLabel.set('Cannot have more than 1 saturated frame.')
                self.labelMessage.configure(foreground='crimson')
                self.enableWidgets()
                return None
        
            saturatedfiles = tkFileDialog.askopenfilenames(filetypes=supportedformats,
                                                           initialdir=self.previousPath)
            
            if saturatedfiles == '':
                self.enableWidgets()
                return None
            
            if len(saturatedfiles) > 1:
                self.varMessageLabel.set('Cannot have more than 1 saturated frame.')
                self.labelMessage.configure(foreground='crimson')
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
                    
            self.displayed_saturated = 1
                    
            self.varSaturatedLabel.set(self.adjustName(self.labelSaturated, filename))
                    
            self.labelSaturatedH.pack(side='top', fill='x', anchor='w')
            self.labelSaturated.pack(side='top', fill='x', anchor='w')
                    
            if self.noInput: self.showCanvas()
                    
            self.showImage(self.labelSaturated, filename=filename)
                    
            self.varImType.set('Bias')
            self.updateFrameButtonText('Bias')
                    
            self.varMessageLabel.set('Saturated frame added.')
            self.labelMessage.configure(foreground='navy')
            
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
        framewidth = self.frameFiles.winfo_width()*0.9
    
        if namewidth > framewidth:
        
            apc.createToolTip(label, name, self.cont.tt_fs)
            
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
                self.labelMessage.configure(foreground='navy')
                
            self.showWarning('Warning', 'Changing CCD type will\nremove added files. Proceed?',
                             'Yes', 'Cancel', cmd)
                             
            # Change camera type back to previous state if the window was exited
            if self.varCCDType.get() != self.currentCCDType:
                self.varCCDType.set(self.currentCCDType)
            
        else:
            # Show message that the camera type was changed
            self.varMessageLabel.set('CCD type changed to %s.' % (self.varCCDType.get()))
            self.labelMessage.configure(foreground='navy')
            self.currentCCDType = self.varCCDType.get()
     
    def clearFiles(self):
    
        '''Reset attributes and clear added files.'''
        
        self.noInput = True
        
        self.useGreen = None
        self.CFAPattern = None
        
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

        self.photo_img = None
        self.photo_img_res = None

        self.deleteTemp(False)
        
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

        self.currentImage = None
        
    def getImage(self, label, filepath, filename, type, splitCFA=False, compare=False):
    
        '''Read image data and store as label attributes.'''
        
        self.varMessageLabel.set('%s - Loading file..' % filename)
        self.labelMessage.configure(foreground='navy')
        self.labelMessage.update_idletasks()
        
        # Create path string compatible with windows terminal
        norm_filepath = os.path.normpath('"' + filepath + '"')
            
        # Create path string compatible with python file opening methods
        py_filepath = '\\'.join(filepath.split('/'))
    
        # If image is a DSLR raw image
        if '*.' + filename.split('.')[1].lower() in self.supportedformats[0][1]:
        
            self.varMessageLabel.set('%s - Converting to TIFF..' % filename)
            self.labelMessage.configure(foreground='navy')
            self.labelMessage.update_idletasks()
            
            # Create TIFF file from raw with dcraw
            subprocess.call('dcraw -4 -o 0 -D -t 0 -k 0 -H 1 -T -j -W %s' \
                            % norm_filepath.encode(sys.getfilesystemencoding()), shell=True)
            
            self.varMessageLabel.set('%s - Reading Exif metadata..' % filename)
            self.labelMessage.configure(foreground='navy')
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
                    
                    warning = 'This frame has C.ISO %d, whereas the\nother added frames have C.ISO %d.' \
                               % (iso, isovals[0]) + '\nStill proceed?' 
                    
                    if not self.showWarning('Warning', warning, 'Yes', 'Cancel', lambda: None):
                            
                        self.varMessageLabel.set('Cancelled.')
                        self.labelMessage.configure(foreground='crimson')
                        raise Exception
            
            label.exposure = self.checkExp(True, tags, compare, label, type)
            label.iso = iso
            
            self.varMessageLabel.set('%s - Extracting raw data..' % filename)
            self.labelMessage.configure(foreground='navy')
            self.labelMessage.update_idletasks()
            
            # Get array of image data
            img = plt.imread(tiff_filepath)
            
            self.varMessageLabel.set('%s - Deleting TIFF file..' % filename)
            self.labelMessage.configure(foreground='navy')
            self.labelMessage.update_idletasks()
            
            # Delete TIFF file created by dcraw
            subprocess.call('del /Q %s' \
                            % (os.path.normpath('"'  + '.'.join(filepath.split('.')[:-1]) + '.tiff"'))\
                              .encode(sys.getfilesystemencoding()),
                            shell=True)
                
        # If image is a CCD raw image
        else:
            
            # If image is a TIFF file
            if filename.split('.')[1].lower() in ['tif', 'tiff']:
            
                self.varMessageLabel.set('%s - Reading TIFF file..' % filename)
                self.labelMessage.configure(foreground='navy')
                self.labelMessage.update_idletasks()
            
                # Get array of image data from TIFF file
                img = plt.imread(py_filepath)
                
                self.varMessageLabel.set('%s - Reading Exif metadata..' % filename)
                self.labelMessage.configure(foreground='navy')
                self.labelMessage.update_idletasks()
                
                file = open(py_filepath, 'rb')
                tags = exifread.process_file(file)
                file.close()
                
                label.exposure = self.checkExp(True, tags, compare, label, type)
                
            # If image is a FITS file
            elif filename.split('.')[1].lower() in ['fit', 'fits']:
                
                self.varMessageLabel.set('%s - Reading FITS file..' % filename)
                self.labelMessage.configure(foreground='navy')
                self.labelMessage.update_idletasks()
                
                # Get array of image data from FITS file
                hdulist = pyfits.open(py_filepath)
                
                img = hdulist[0].data
                header = hdulist[0].header
                
                hdulist.close()
                
                if len(img.shape) != 2:
                    self.varMessageLabel.set('Image file "%s" contains colour channels.' \
                                            + 'Please use a non-debayered image.' % filename)
                    self.labelMessage.configure(foreground='crimson')
                    raise Exception
                
                self.varMessageLabel.set('%s - Reading FITS header..' % filename)
                self.labelMessage.configure(foreground='navy')
                self.labelMessage.update_idletasks()
                
                label.exposure = self.checkExp(False, header, compare, label, type)
        
        # If image has a CFA and a specific colour needs to be extracted
        if splitCFA:
                
            self.varMessageLabel.set('%s - Detecting CFA pattern..' % filename)
            self.labelMessage.configure(foreground='navy')
            self.labelMessage.update_idletasks()
            
            # Get which colour of pixels to extract from user if necessary
            if self.useGreen is None:
                self.busy = True
                self.askColour()
                self.wait_window(self.topAskColour)
                self.busy = False
                self.useGreen = self.varUseGreen.get()
                
            # Abort if user cancels
            if self.cancelled:
                self.varMessageLabel.set('Cancelled.')
                self.labelMessage.configure(foreground='crimson')
                raise Exception
            
            # If image is a DSLR raw image
            if self.cont.isDSLR and not filename.split('.')[1].lower() in ['tif', 'tiff', 'fit', 'fits']:
                
                # Get string of raw file information
                metadata = subprocess.check_output('dcraw -i -v %s' \
                                    % norm_filepath.encode(sys.getfilesystemencoding()), shell=True)
                    
                # Extract string representing CFA pattern
                if self.CFAPattern is None:
                    for line in metadata.split('\n'):
                        
                        parts = line.split(': ')
                            
                        if parts[0] == 'Filter pattern': self.CFAPattern = parts[1].strip()
                
            # Ask user for CFA pattern if it wasn't detected or if camera is colour CCD
            if self.CFAPattern is None:
                self.busy = True
                self.askCFAPattern()
                self.wait_window(self.topAskCFA)
                self.busy = False
                self.CFAPattern = self.varCFAPattern.get()
                
            # Abort if user cancels
            if self.cancelled:
                self.varMessageLabel.set('Cancelled.')
                self.labelMessage.configure(foreground='crimson')
                raise Exception
                
            if not self.CFAPattern in ['RG/GB', 'BG/GR', 'GR/BG', 'GB/RG']:
                self.varMessageLabel.set('CFA pattern %s not recognized.' % (self.CFAPattern))
                self.labelMessage.configure(foreground='crimson')
                raise Exception
                
            self.varMessageLabel.set('%s - Extracting %s pixels..' \
                                     % (filename, ('green' if self.useGreen else 'red')))
            self.labelMessage.configure(foreground='navy')
            self.labelMessage.update_idletasks()
            
            # Extract green and red pixels as separate images
            
            h, w = img.shape
            
            if (self.CFAPattern == 'GB/RG' and self.useGreen) \
               or (self.CFAPattern == 'GR/BG' and self.useGreen) \
               or (self.CFAPattern == 'RG/GB' and not self.useGreen):
                img = img[0:(h-1):2, 0:(w-1):2] # Quadrant 1
            elif (self.CFAPattern == 'RG/GB' and self.useGreen) \
                 or (self.CFAPattern == 'BG/GR' and self.useGreen) \
                 or (self.CFAPattern == 'GR/BG' and not self.useGreen):
                img = img[0:(h-1):2, 1:w:2] # Quadrant 2
            elif self.CFAPattern == 'GB/RG' and not self.useGreen:
                img = img[1:h:2, 0:(w-1):2] # Quadrant 3
            elif self.CFAPattern == 'BG/GR' and not self.useGreen:
                img = img[1:h:2, 1:w:2] # Quadrant 4
                
            if type == 'light':
                self.labelLight.isSplitted = True
        
        # If image is mono or is to keep all pixels
        else:
            
            if type == 'light':
                self.labelLight.isSplitted = False
        
        self.varMessageLabel.set('%s - Checking image dimensions..' % filename)
        self.labelMessage.configure(foreground='navy')
        self.labelMessage.update_idletasks()
        
        # Show error if the image size if different from the previously added image
        if compare and img.shape != compare.stretched_img.shape:
            self.varMessageLabel.set('The dimensions of "%s" does not match ' % filename \
                                     + 'those of the other added frame.')
            self.labelMessage.configure(foreground='crimson')
            raise Exception
        
        # Store raw image data as label attribute
        
        self.varMessageLabel.set('%s - Creating temporary raw data file..' % filename)
        self.labelMessage.configure(foreground='navy')
        self.labelMessage.update_idletasks()
        
        np.save(self.labelNames[label], img)
            
        self.varMessageLabel.set('%s - Applying screen stretch..' % filename)
        self.labelMessage.configure(foreground='navy')
        self.labelMessage.update_idletasks()
        
        label.stretched_img = apc.autostretch(img)
        img = None
        
        self.varMessageLabel.set('%s - Creating temporary image file..' % filename)
        self.labelMessage.configure(foreground='navy')
        self.labelMessage.update_idletasks()
        self.updateDisplayedImage(label)
                
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
                        self.labelMessage.configure(foreground='crimson')
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
                self.labelMessage.configure(foreground='crimson')
                raise Exception
                
        return exposure_num
       
    def tooDiff(self, exp1, exp2):
    
        '''Return true if the exposure times differ by more than 10%.'''
        
        return np.abs(exp1 - exp2) >= 0.05*(exp1 + exp2)
       
    def askColour(self):
    
        '''Show window with options for choosing which CFA colour to extract.'''
    
        def ok():
        
            '''Set confirmation that the window wasn't exited, and close window.'''
        
            self.cancelled = False
            self.topAskColour.destroy()
        
        # Setup window
        
        self.topAskColour = tk.Toplevel()
        self.topAskColour.title('Choose colour')
        self.cont.addIcon(self.topAskColour)
        apc.setupWindow(self.topAskColour, 300, 145)
        self.topAskColour.focus_force()
        
        self.cancelled = True
        self.varUseGreen = tk.IntVar()
        self.varUseGreen.set(1)
        
        tk.Label(self.topAskColour,
                  text='Choose which colour of pixels to extract.\nGreen is recommended unless the '\
                       + 'image\nwas taken with a red narrowband filter.',
                  font=self.cont.small_font).pack(side='top', pady=(10*C.scsy, 5*C.scsy), expand=True)
        
        frameRadio = ttk.Frame(self.topAskColour)
        frameRadio.pack(side='top', expand=True, pady=(0, 10*C.scsy))
        ttk.Radiobutton(frameRadio, text='Green', variable=self.varUseGreen,
                        value=1).grid(row=0, column=0)
        ttk.Radiobutton(frameRadio, text='Red', variable=self.varUseGreen,
                        value=0).grid(row=0, column=1)
        
        ttk.Button(self.topAskColour, text='OK', command=ok).pack(side='top', expand=True,
                                                                 pady=(0, 10*C.scsy))
    
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
        apc.setupWindow(self.topAskCFA, 300, 145)
        self.topAskCFA.focus_force()
        
        self.cancelled = True
        CFAList = ['RG/GB', 'BG/GR', 'GR/BG', 'GB/RG']
        
        self.varCFAPattern = tk.StringVar()
        self.varCFAPattern.set(CFAList[0])
        
        ttk.Label(self.topAskCFA, text='Choose the colour filter pattern of your camera.',
                  anchor='center').pack(side='top', pady=(10*C.scsy, 5*C.scsy), expand=True)
        
        ttk.OptionMenu(self.topAskCFA, self.varCFAPattern, None, *CFAList).pack(side='top',
                                                                                expand=True,
                                                                                pady=(0, 10*C.scsy))
        
        ttk.Button(self.topAskCFA, text='OK', command=ok).pack(side='top', expand=True,
                                                               pady=(0, 10*C.scsy))
    
    def showImageEvent(self, event):
    
        '''Only call the show image method when label is clicked if no topwindow is showing.'''
    
        if not self.busy: self.showImage(event.widget)
        
    def showImage(self, label, filename=False):
    
        '''Change background of given label to blue and show the photoimage of the label.'''
        
        label.configure(style='leftselectedfile.TLabel')
        
        label.leftselected = True
        label.rightselected = False
        
        for other_label in self.labelList:
        
            other_label.rightselected = False
            
            if other_label is not label:
                other_label.leftselected = False
                other_label.configure(style='file.TLabel')

        self.loadImage(label, filename=filename)
            
        # Create canvas image and store image dimensions
        self.canvasDisplay.delete(self.currentImage)
        self.canvasDisplay.delete(self.selectionBox)
        self.canvasDisplay.delete(self.measureLine)
        
        if self.showResized:
        
            # Show the resized version of the image
            
            w = self.photo_img_res.width()
            h = self.photo_img_res.height()
            cw = self.scrollbarCanvHor.winfo_width() - 17.0
            ch = self.scrollbarCanvVer.winfo_height()
                
            self.imageSize = (w, h)
            
            self.currentImage = self.canvasDisplay.create_image(cw/2, ch/2,
                                                                image=self.photo_img_res,
                                                                anchor='center')
                                                                
            self.canvasDisplay.configure(scrollregion=(0, 0, 0, 0))
            
            # Display the FOV of the non-resized light frame
            if label is self.labelLight:
                self.setFOV(0, self.photo_img.width(), 0, self.photo_img.height(), False)
            else:
                self.varFOV.set('')
                                                                
        else:
        
            self.imageSize = (self.photo_img.width(), self.photo_img.height())
        
            self.currentImage = self.canvasDisplay.create_image(0, 0, image=self.photo_img,
                                                                anchor='nw')
        
            self.canvasDisplay.configure(scrollregion=(0, 0, self.imageSize[0], self.imageSize[1]))
            
            self.setFOV(0, self.imageSize[0], 0, self.imageSize[1], False)
        
        # Update C.ISO and exposure time labels
        
        if label.exposure is not None:
            self.varImInfo.set('Exposure time: %.4g s' % label.exposure)
        else:
            self.varImInfo.set('Exposure time: Not detected')
            
        if self.cont.isDSLR:
            if label.iso is not None:
                self.varImInfo.set('C.ISO: %d        %s' % (label.iso, self.varImInfo.get()))
            else:
                self.varImInfo.set('C.ISO: Not detected        %s' % (self.varImInfo.get()))
        
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

        self.varMessageLabel.set('Done.')
        self.labelMessage.configure(foreground='navy')
        self.labelMessage.update_idletasks()
            
        self.menuActive = False
                
    def removeImageEvent(self, event):
    
        '''Mark right-clicked label with red, and remove marked labels if right-clicked again.'''
    
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
                            os.remove(self.labelNames[self.labelBias1] + '.npy')
                            os.remove(self.labelNames[self.labelBias1] + '.jpg')
                            
                            self.labelBias1.pack_forget()
                            self.varBias1Label.set('')
                            self.frameBias.pack_forget()
                            self.labelBiasH.pack_forget()
                            
                            self.displayed_bias = 0
                            
                        elif self.displayed_bias == 2:
                        
                            # Shift info from label 2 to label 1 if label 2 is removed
                        
                            if label is self.labelBias1:
                                self.labelBias1.stretched_img[:, :] = self.labelBias2.stretched_img
                                self.labelBias2.stretched_img = None
                                self.labelBias1.exposure = self.labelBias2.exposure
                                self.labelBias1.iso = self.labelBias2.iso
                                self.varBias1Label.set(self.varBias2Label.get())
                                os.remove(self.labelNames[self.labelBias1] + '.npy')
                                os.rename(self.labelNames[self.labelBias2] + '.npy', 
                                          self.labelNames[self.labelBias1] + '.npy')
                                          
                                os.remove(self.labelNames[self.labelBias1] + '.jpg')
                                os.rename(self.labelNames[self.labelBias2] + '.jpg', 
                                          self.labelNames[self.labelBias1] + '.jpg')
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
                            os.remove(self.labelNames[self.labelDark1] + '.npy')
                            os.remove(self.labelNames[self.labelDark1] + '.jpg')
                            
                            self.labelDark1.pack_forget()
                            self.varDark1Label.set('')
                            self.frameDark.pack_forget()
                            self.labelDarkH.pack_forget()
                            
                            self.displayed_dark = 0
                            
                        elif self.displayed_dark == 2:
                        
                            if label is self.labelDark1:
                                self.labelDark1.stretched_img[:, :] = self.labelDark2.stretched_img
                                self.labelDark2.stretched_img = None
                                self.labelDark1.exposure = self.labelDark2.exposure
                                self.labelDark1.iso = self.labelDark2.iso
                                self.varDark1Label.set(self.varDark2Label.get())
                                os.remove(self.labelNames[self.labelDark1] + '.npy')
                                os.rename(self.labelNames[self.labelDark2] + '.npy',
                                          self.labelNames[self.labelDark1] + '.npy')
                                
                                os.remove(self.labelNames[self.labelDark1] + '.jpg')
                                os.rename(self.labelNames[self.labelDark2] + '.jpg',
                                          self.labelNames[self.labelDark1] + '.jpg')
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
                            os.remove(self.labelNames[self.labelFlat1] + '.npy')
                            os.remove(self.labelNames[self.labelFlat1] + '.jpg')
                            
                            self.labelFlat1.pack_forget()
                            self.varFlat1Label.set('')
                            self.frameFlat.pack_forget()
                            self.labelFlatH.pack_forget()
                            
                            self.displayed_flat = 0
                            
                        elif self.displayed_flat == 2:
                        
                            if label is self.labelFlat1:
                                self.labelFlat1.stretched_img[:, :] = self.labelFlat2.stretched_img
                                self.labelFlat2.stretched_img = None
                                self.labelFlat1.exposure = self.labelFlat2.exposure
                                self.labelFlat1.iso = self.labelFlat2.iso
                                self.varFlat1Label.set(self.varFlat2Label.get())
                                os.remove(self.labelNames[self.labelFlat1] + '.npy')
                                os.rename(self.labelNames[self.labelFlat2] + '.npy', 
                                          self.labelNames[self.labelFlat1] + '.npy')
                                
                                os.remove(self.labelNames[self.labelFlat1] + '.jpg')
                                os.rename(self.labelNames[self.labelFlat2] + '.jpg', 
                                          self.labelNames[self.labelFlat1] + '.jpg')
                                if self.labelFlat2.leftselected:
                                    self.showImage(self.labelFlat1)
                            
                            self.forgetAttributes(self.labelFlat2)
                            
                            self.labelFlat2.pack_forget()
                            self.varFlat2Label.set('')
                            self.varFlatHLabel.set('Flat frame')
                            
                            self.displayed_flat = 1
                        
                    elif label is self.labelLight:
                    
                        self.forgetAttributes(self.labelLight)
                        os.remove(self.labelNames[self.labelLight] + '.npy')
                        os.remove(self.labelNames[self.labelLight] + '.jpg')
                        
                        self.labelLight.pack_forget()
                        self.varLightLabel.set('')
                        self.labelLightH.pack_forget()
                        self.displayed_light = 0
                        self.varFOV.set('')
                        
                    elif label is self.labelSaturated:
                    
                        self.forgetAttributes(self.labelSaturated)
                        os.remove(self.labelNames[self.labelSaturated] + '.npy')
                        os.remove(self.labelNames[self.labelSaturated] + '.jpg')
                        
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
                    self.clearFiles()
            else:
                self.getSelectedLabel().configure(style='leftselectedfile.TLabel')
        
            self.varMessageLabel.set('Frame removed.' if count == 1 else 'Frames removed.')
            self.labelMessage.configure(foreground='navy')
        
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
            if self.displayed_bias == 2 and \
               self.displayed_flat == 2 and \
               self.displayed_light == 1:
            
                text='A frame containing saturated pixels is required\nto compute sensor data. ' \
                      + 'Does the added\nlight frame contain saturated pixels?'
                      
                if not self.showWarning('Note', text, 'Yes', 'No', lambda: None):
                    self.varMessageLabel.set('Cancelled. Please add a saturated ' \
                                             + 'frame to compute sensor data.')
                    self.labelMessage.configure(foreground='crimson')
                    self.menuActive = False
                    return False
                    
                # Use light frame as saturated frame
                saturated = np.load(self.labelNames[self.labelLight] + '.npy')
                useLight = True
            
            # Show message if required files haven't been added
            else:
                self.varMessageLabel.set('Two bias frames, two flat frames and ' \
                             + 'one saturated (or light) frame is required to compute sensor data.')
                self.labelMessage.configure(foreground='crimson')
                return None
        else:
        
            saturated = np.load(self.labelNames[self.labelSaturated] + '.npy')
            useLight = False
            
        # Get raw image data
        bias1 = np.load(self.labelNames[self.labelBias1] + '.npy')
        bias2 = np.load(self.labelNames[self.labelBias2] + '.npy')
        flat1 = np.load(self.labelNames[self.labelFlat1] + '.npy')
        flat2 = np.load(self.labelNames[self.labelFlat2] + '.npy')
        
        # Define central crop area for flat frames
        h, w = flat1.shape
        a = int(0.25*h)
        b = int(0.75*h)
        c = int(0.25*w)
        d = int(0.75*w)

        # Define central crop area for bias frames
        h2, w2 = bias1.shape
        a2 = int(0.25*h2)
        b2 = int(0.75*h2)
        c2 = int(0.25*w2)
        d2 = int(0.75*w2)
        
        # Crop flat frames
        flat1_crop = flat1[a:b, c:d]
        flat2_crop = flat2[a:b, c:d]

        # Crop bias frames
        bias1_crop = bias1[a2:b2, c2:d2]
        bias2_crop = bias2[a2:b2, c2:d2]
        
        self.white_level = np.max(saturated)
        
        self.black_level = 0.5*(np.median(bias1_crop) + np.median(bias2_crop))
        flat_level_ADU = 0.5*(np.median(flat1_crop) + np.median(flat2_crop))
        
        delta_bias = bias1_crop + 30000 - bias2_crop
        delta_flat = flat1_crop + 30000 - flat2_crop
        
        read_noise_ADU = np.std(delta_bias)/np.sqrt(2)
        
        flat_noise_ADU = np.std(delta_flat)/np.sqrt(2)
        
        photon_noise_ADU_squared = flat_noise_ADU**2 - read_noise_ADU**2
        photon_level_ADU = flat_level_ADU - self.black_level
        
        self.gain = photon_level_ADU/photon_noise_ADU_squared
        
        self.rn = self.gain*read_noise_ADU
        
        self.sat_cap = self.gain*self.white_level
        
        self.varMessageLabel.set('Sensor data computed.')
        self.labelMessage.configure(foreground='navy')
        
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
        apc.setupWindow(self.topResults, 300, 220)
        self.topResults.focus_force()
        
        ttk.Label(self.topResults, text='Computed sensor data', font=self.cont.smallbold_font,
                  anchor='center').pack(side='top', pady=(15*C.scsy, 5*C.scsy), expand=True)
        
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
                  .pack(side='top', pady=((5*C.scsy, 20*C.scsy)), expand=True)
        
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
                    # Get inputted C.ISO value for DSLR
                    try:
                        iso = str(int(varISO.get()))
                    except ValueError:
                        varMessageLabel.set('Invalid C.ISO input. Must be an integer.')
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
                if line[0] == C.CNAME[self.cont.cnum]:
                
                    # If no data exists for the camera
                    if self.cont.noData:
                    
                        g_idx1 = rn_idx1 = 0
                        g_idx2 = rn_idx2 = 1
                    
                        # Add the data
                        file.write('\n%s,%s,%.3g*,%.3g*,%d*,%d*,%d*,%s,%s,%s,%s' \
                                    % (line[0], line[1], self.gain, self.rn, round(self.sat_cap),
                                       round(self.black_level), round(self.white_level), 'NA',
                                       line[8], line[9], line[10]))
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
                            
                            isovals = line[11].split('-')
                          
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
                        file.write('\n%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' \
                    % (line[0], line[1],
                       '-'.join(gainvals[:g_idx1] + ['%.3g*' % (self.gain)] + gainvals[g_idx2:]),
                       '-'.join(rnvals[:rn_idx1] + ['%.3g*' % (self.rn)] + rnvals[rn_idx2:]),
                       '-'.join(satcapvals[:g_idx1] + ['%d*' % round(self.sat_cap)] + satcapvals[g_idx2:]),
                       '-'.join(blvals[:g_idx1] + ['%d*' % round(self.black_level)] + blvals[g_idx2:]),
                       '-'.join(wlvals[:g_idx1] + ['%d*' % round(self.white_level)] + wlvals[g_idx2:]),
                       line[7], line[8], line[9], line[10]))
                                          
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
                C.GAIN[idx][0][g_idx1] = float('%.3g' % (self.gain))
                C.GAIN[idx][1][g_idx1] = 1
                C.SAT_CAP[idx][0][g_idx1] = int(round(self.sat_cap))
                C.SAT_CAP[idx][1][g_idx1] = 1
                C.BLACK_LEVEL[idx][0][g_idx1] = int(round(self.black_level))
                C.BLACK_LEVEL[idx][1][g_idx1] = 1
                C.WHITE_LEVEL[idx][0][g_idx1] = int(round(self.white_level))
                C.WHITE_LEVEL[idx][1][g_idx1] = 1
                if self.cont.isDSLR: C.ISO[idx][g_idx1] = int(iso)
            else:
                C.GAIN[idx][0] = np.insert(C.GAIN[idx][0], g_idx1, float('%.3g' % (self.gain)))
                C.GAIN[idx][1] = np.insert(C.GAIN[idx][1], g_idx1, 1)
                C.SAT_CAP[idx][0] = np.insert(C.SAT_CAP[idx][0], g_idx1, int(round(self.sat_cap)))
                C.SAT_CAP[idx][1] = np.insert(C.SAT_CAP[idx][1], g_idx1, 1)
                C.BLACK_LEVEL[idx][0] = np.insert(C.BLACK_LEVEL[idx][0], g_idx1, int(round(self.black_level)))
                C.BLACK_LEVEL[idx][1] = np.insert(C.BLACK_LEVEL[idx][1], g_idx1, 1)
                C.WHITE_LEVEL[idx][0] = np.insert(C.WHITE_LEVEL[idx][0], g_idx1, int(round(self.white_level)))
                C.WHITE_LEVEL[idx][1] = np.insert(C.WHITE_LEVEL[idx][1], g_idx1, 1)
                if self.cont.isDSLR: C.ISO[idx] = np.insert(C.ISO[idx], g_idx1, int(iso))
                    
            if rn_idx2 == rn_idx1 + 1:
                C.RN[idx][0][rn_idx1] = float('%.3g' % (self.rn))
                C.RN[idx][1][rn_idx1] = 1
            else:
                C.RN[idx][0] = np.insert(C.RN[idx][0], rn_idx1, float('%.3g' % (self.rn)))
                C.RN[idx][1] = np.insert(C.RN[idx][1], rn_idx1, 1)
            
            for frame in [self.cont.frames[ImageCalculator], self.cont.frames[ImageSimulator],
                          self.cont.frames[PlottingTool]]:
            
                frame.reconfigureNonstaticWidgets()
                frame.setDefaultValues()
                
            self.varMessageLabel.set('Sensor information added for %s.' % C.CNAME[idx])
            self.labelMessage.configure(foreground='navy')
            try:
                self.topCamInfo.destroy()
            except:
                pass
            self.topResults.destroy()
        
        # Create the window asking for required camera information
        if self.cont.isDSLR and not con_iso:
        
            self.topCamInfo = tk.Toplevel()
            self.topCamInfo.title('Save sensor data')
            self.cont.addIcon(self.topCamInfo)
            apc.setupWindow(self.topCamInfo, 300, 140)
            self.topCamInfo.focus_force()
            
            ttk.Label(self.topCamInfo, text='Input the C.ISO used for the images:')\
                     .pack(side='top', pady=(15*C.scsy, 5*C.scsy), expand=True)
            
            ttk.Entry(self.topCamInfo, textvariable=varISO, font=self.cont.small_font,
                      background=C.DEFAULT_BG, width=8).pack(side='top', pady=(7*C.scsy, 7*C.scsy),
                                                           expand=True)
        
            ttk.Button(self.topCamInfo, text='OK',
                       command=executeSensorResultSave).pack(side='top',
                                                                     pady=(0, 6*C.scsy), expand=True)
            ttk.Label(self.topCamInfo, textvariable=varMessageLabel, font=self.cont.small_font,
                          background=C.DEFAULT_BG).pack(side='top', pady=(0, 10*C.scsy), expand=True)
                          
        else:
        
            executeSensorResultSave()
    
    def createSelectionBoxEvent(self, event):
    
        '''Create rectangle in canvas when left-clicked.'''
    
        if self.menuActive: return None
    
        # Delete existing selection box
        event.widget.delete(self.selectionBox)
        event.widget.delete(self.measureLine)
            
        # Define list to store selection box corner coordinates
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
            dx *= float(self.photo_img.width())/self.imageSize[0]
            dy *= float(self.photo_img.height())/self.imageSize[1]
            
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
        img = np.load(self.labelNames[self.getSelectedLabel()] + '.npy')
        
        # Crop image if a selection box has been drawn
        if self.localSelection:
            img_crop = img[self.selectionArea[1]:self.selectionArea[3],
                           self.selectionArea[0]:self.selectionArea[2]]
        else:
            img_crop = img
        
        # Calculate values in (cropped) image
        sample_val = img_crop.shape[0]*img_crop.shape[1]
        try:
            mean_val = np.mean(img_crop)
            median_val = np.median(img_crop)
            std_val = np.std(img_crop)
            max_val = np.max(img_crop)
            min_val = np.min(img_crop)
        except MemoryError:
            self.varMessageLabel.set('Not enough memory available. Please select a limited region ' \
                                     + 'of the image before computing statistics.')
            self.labelMessage.configure(foreground='crimson')
            return None
        
        self.disableWidgets()
        self.busy = True
        
        # Setup window displaying the calculated information
        topStatistics = tk.Toplevel()
        topStatistics.title('Statistics')
        self.cont.addIcon(topStatistics)
        apc.setupWindow(topStatistics, 300, 230)
        topStatistics.focus_force()
        
        self.menuRC.entryconfigure(8, state='disabled')
        
        ttk.Label(topStatistics, text='Statistics of selected image region' \
                                      if self.localSelection else 'Statistics of the entire image',
                  font=self.cont.smallbold_font,
                  anchor='center').pack(side='top', pady=(20*C.scsy, 10*C.scsy), expand=True)
        
        frameStatistics = ttk.Frame(topStatistics)
        frameStatistics.pack(side='top', pady=(0, 6*C.scsy), expand=True)
        
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
                  .pack(side='top', pady=(0, 15*C.scsy), expand=True)
        
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
            self.labelMessage.configure(foreground='crimson')
            self.menuActive = False
            return None
            
        # If the selected frame is a light frame
        if label is self.labelLight:
        
            # Show error if no selection box has been drawn
            if not self.localSelection:
            
                self.varMessageLabel.set('Please select a background or target region '\
                                         + 'of the image before transfering data.')
                self.labelMessage.configure(foreground='crimson')
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
            apc.setupWindow(topAskRegion, 300, 145)
            topAskRegion.focus_force()
            
            self.cancelled = True
            varBGRegion = tk.IntVar()
            varBGRegion.set(1)
            
            tk.Label(topAskRegion,
                      text='Choose which region of the image\nyou have selected.',
                      font=self.cont.small_font).pack(side='top', pady=(10*C.scsy, 5*C.scsy),
                                                      expand=True)
            
            frameRadio = ttk.Frame(topAskRegion)
            frameRadio.pack(side='top', expand=True, pady=(0, 10*C.scsy))
            ttk.Radiobutton(frameRadio, text='Background', variable=varBGRegion,
                            value=1).grid(row=0, column=0)
            ttk.Radiobutton(frameRadio, text='Target', variable=varBGRegion,
                            value=0).grid(row=0, column=1)
            
            ttk.Button(topAskRegion, text='OK', command=ok_light).pack(side='top', expand=True,
                                                                       pady=(0, 10*C.scsy))
            
            self.wait_window(topAskRegion)
            
            self.enableWidgets()
            self.menuRC.entryconfigure(9, state='normal')
            self.busy = False
            
            # Cancel if topwindow was exited
            if self.cancelled:
                self.varMessageLabel.set('Cancelled.')
                self.labelMessage.configure(foreground='crimson')
                self.menuActive = False
                return None
            
            calframe = self.cont.frames[ImageCalculator]
              
            # Get raw data of selected area
            img_crop = np.load(self.labelNames[label] + '.npy')[self.selectionArea[1]:self.selectionArea[3],
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
                
            if self.labelLight.iso is not None and self.labelLight.iso in list(C.ISO[self.cont.cnum]):
                calframe.varISO.set(self.labelLight.iso)
                calframe.updateISO(self.labelLight.iso)
                isostr = ' C.ISO set to %d.' % (self.labelLight.iso)
                
            if self.labelLight.exposure is not None:
                calframe.varExp.set('%.4g' % (self.labelLight.exposure))
                expstr = ' Exposure time set to %.4g s.' % (self.labelLight.exposure)
                
            self.varMessageLabel.set(('Background data transferred to Image Calculator.' \
                                      if varBGRegion.get() \
                                      else 'Target data transferred to Image Calculator.') + isostr \
                                                                                        + expstr)
            self.labelMessage.configure(foreground='navy')
        
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
                    apc.setupWindow(topWarning, 300, 180)
                    topWarning.focus_force()
                    
                    def ok_dark():
                        self.cancelled = False
                        topWarning.destroy()
                    
                    self.cancelled = True
                    
                    tk.Label(topWarning, text='Using two dark frames is recommended\nto get more ' \
                                            + 'accurate noise measurements.\nProceed with only one?',
                            font=self.cont.small_font).pack(side='top', pady=(20*C.scsy, 5*C.scsy),
                                                            expand=True)
                          
                    frameButtons = ttk.Frame(topWarning)
                    frameButtons.pack(side='top', expand=True, pady=(0, 10*C.scsy))
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
                        self.labelMessage.configure(foreground='crimson')
                        self.menuActive = False
                        return None
                    
                    # Get raw image data
                    img = np.load(self.labelNames[label] + '.npy')
                    
                    # Crop image if a selection box has been drawn
                    if self.localSelection:
                        img_crop = img[self.selectionArea[1]:self.selectionArea[3],
                                       self.selectionArea[0]:self.selectionArea[2]]
                    else:
                        img_crop = img
                    
                    # Calculate dark frame noise
                    try:
                        dark_val = np.std(img_crop)
                    except MemoryError:
                        h, w = img_crop.shape
                        a = int(0.25*h)
                        b = int(0.75*h)
                        c = int(0.25*w)
                        d = int(0.75*w)
                        dark_val = np.std(img_crop[a:b, c:d])
                
                # If two dark frames have been added
                else:
                
                    # Get raw data of images
                    img1 = np.load(self.labelNames[self.labelDark1] + '.npy')
                    img2 = np.load(self.labelNames[self.labelDark2] + '.npy')
                    
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
                    try:
                        dark_val = np.std(delta_dark)/np.sqrt(2)
                    except MemoryError:
                        h, w = delta_dark.shape
                        a = int(0.25*h)
                        b = int(0.75*h)
                        c = int(0.25*w)
                        d = int(0.75*w)
                        dark_val = np.std(delta_dark[a:b, c:d])/np.sqrt(2)
            
            # If the camera is a CCD            
            else:
                
                if self.displayed_dark == 1:
            
                    # Get raw image data
                    img = np.load(self.labelNames[label] + '.npy')
                    
                    # Crop image if a selection box has been drawn
                    if self.localSelection:
                        img_crop = img[self.selectionArea[1]:self.selectionArea[3],
                                       self.selectionArea[0]:self.selectionArea[2]]
                    else:
                        img_crop = img
                        
                    # Calculate dark frame level
                    try:
                        dark_val = np.median(img_crop)
                    except MemoryError:
                        h, w = img_crop.shape
                        a = int(0.25*h)
                        b = int(0.75*h)
                        c = int(0.25*w)
                        d = int(0.75*w)
                        dark_val = np.median(img_crop[a:b, c:d])
                    
                else:
                
                    # Get raw data of images
                    img1 = np.load(self.labelNames[self.labelDark1] + '.npy')
                    img2 = np.load(self.labelNames[self.labelDark2] + '.npy')
                    
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
                    try:
                        dark_val = 0.5*(np.median(img1_crop) + np.median(img2_crop))
                    except MemoryError:
                        h, w = img1_crop.shape
                        a = int(0.25*h)
                        b = int(0.75*h)
                        c = int(0.25*w)
                        d = int(0.75*w)
                        dark_val = 0.5*(np.median(img1_crop[a:b, c:d]) + np.median(img2_crop[a:b, c:d]))
                
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
                                and isovals[0] in list(C.ISO[self.cont.cnum]):
            
                calframe.varISO.set(isovals[0])
                calframe.updateISO(isovals[0])
                isostr = ' C.ISO set to %d.' % isovals[0]
                    
            if len(expvals) == 1 or (len(expvals) == 2 and not self.tooDiff(*expvals)):
            
                calframe.varExp.set(expvals[0])
                expstr = ' Exposure time set to %.4g s.' \
                         % (label.exposure if label.exposure is not None else expvals[0])
                    
            self.varMessageLabel.set('Dark data transferred to Image Calculator.' + isostr + expstr)
            self.labelMessage.configure(foreground='navy')
                    
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
            self.setFOV(0, self.photo_img.width(),
                        0, self.photo_img.height(), False)
        else:
            self.setAngle(self.measurePoints[0], self.measurePoints[2],
                          self.measurePoints[1], self.measurePoints[3])
    
    def updateAngle(self):
    
        '''Update the FOV/angle label according to the existing drawing.'''
    
        if self.getSelectedLabel() is self.labelLight:
        
            if self.mode == 'measure':
            
                if np.abs(self.measurePoints[2] - self.measurePoints[0]) <= 1 \
                   and np.abs(self.measurePoints[3] - self.measurePoints[1]) <= 1:
                    self.setFOV(0, self.photo_img.width(),
                                0, self.photo_img.height(), False)
                else:
                    self.setAngle(self.measurePoints[0], self.measurePoints[2],
                                  self.measurePoints[1], self.measurePoints[3])
                
            else:
        
                if self.localSelection:
                    self.setFOV(self.selectionArea[0], self.selectionArea[2],
                                self.selectionArea[1], self.selectionArea[3], True)
                else:
                    self.setFOV(0, self.photo_img.width(),
                                0, self.photo_img.height(), False)
    
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
        apc.setupWindow(topWarning, 300, 145)
        topWarning.focus_force()
        
        self.cancelled = True
        
        tk.Label(topWarning, text=body,
                 font=self.cont.small_font).pack(side='top', pady=(20*C.scsy, 5*C.scsy), expand=True)
        
        frameButtons = ttk.Frame(topWarning)
        frameButtons.pack(side='top', expand=True, pady=(0, 10*C.scsy))
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
        f = matplotlib.figure.Figure(figsize=(3.9*C.scsx, 3.4*C.scsx), dpi=100, facecolor=C.DEFAULT_BG,
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
        self.line2, = self.ax.plot(self.x, apc.stretch(self.x, 0.5)/65535.0, color='lime')
        
        self.disableWidgets()
        self.busy = True
        
        # Setup window
        topHist = tk.Toplevel()
        topHist.title('Histogram')
        self.cont.addIcon(topHist)
        apc.setupWindow(topHist, 470, 520)
        topHist.focus_force()
        
        def apply():
            self.orig_stretched = label.stretched_img
            self.updateDisplayedImage(label, fromHist=True)
            self.showImage(label)
            
        frameCanvas = ttk.Frame(topHist)
        frameCanvas.pack(side='top', pady=(20*C.scsy, 0), expand=True)
        
        self.histcanvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(f, frameCanvas)
        self.histcanvas._tkcanvas.config(highlightthickness=0)
        
        self.histcanvas.get_tk_widget().pack(side='top')
        
        self.scaleStretch = tk.Scale(frameCanvas, from_=0.001, to=0.999, resolution=0.001,
                                     orient='horizontal', length=388*C.scsx, showvalue=False,
                                     command=self.updateHistStretch)
        self.scaleStretch.pack(side='top')
        
        self.scaleStretch.set(0.5)
        
        frameButtons1 = ttk.Frame(frameCanvas)
        frameButtons1.pack(side='top', fill='x')
        
        ttk.Button(frameButtons1, text='Clip black point',
                   command=lambda: self.clipBlackPoint(label)).pack(side='left', padx=10*C.scsx)
        tk.Label(frameButtons1, textvariable=self.varM).pack(side='left', expand=True)
        ttk.Button(frameButtons1, text='Clip white point',
                   command=lambda: self.clipWhitePoint(label)).pack(side='right', padx=10*C.scsx)
        
        frameButtons2 = ttk.Frame(topHist)
        frameButtons2.pack(side='top', pady=8*C.scsy)
        
        ttk.Button(frameButtons2, text='Autostretch',
                   command=lambda: self.applyAutoStretch(label)).pack(side='left', padx=(40*C.scsx, 0))
        ttk.Button(frameButtons2, text='Stretch histogram',
                   command=lambda: self.stretchHist(label)).pack(side='left', padx=10*C.scsx, expand=True)
        ttk.Button(frameButtons2, text='Reset to linear',
                   command=lambda: self.resetToLinear(label)).pack(side='right', padx=(0, 40*C.scsx))
        
        frameButtons3 = ttk.Frame(topHist)
        frameButtons3.pack(side='top', pady=(0, 20*C.scsy))
        
        ttk.Button(frameButtons3, text='Apply changes',
                   command=apply).pack(side='left', padx=(20*C.scsx, 10*C.scsx))
        ttk.Button(frameButtons3, text='Close',
                   command=lambda: self.closeHist(topHist)).pack(side='right', padx=(0, 20*C.scsx))
        
        self.wait_window(topHist)
        
        try:
            label.stretched_img = self.orig_stretched
            self.menuRC.entryconfigure(7, state='normal')
        except:
            pass
        self.enableWidgets()
        self.busy = False
        
        self.menuActive = False
        
    def closeHist(self, toplevel):

        self.orig_stretched = None
        toplevel.destroy()

    def updateHistStretch(self, m):
    
        '''Update the displayed stretch function.'''
    
        self.line2.set_data(self.x, apc.stretch(apc.clipLevel(self.x, np.min(self.x), np.max(self.x)),
                                            float(m))/65535.0)
        self.histcanvas.draw()
        self.varM.set(m)
        
    def clipBlackPoint(self, label):
    
        '''Redraw the histogram with clipped black point.'''
    
        img = label.stretched_img
        label.stretched_img = apc.clipLevel(img, np.min(img), 65535)
        self.updateHist(label)
    
    def clipWhitePoint(self, label):
    
        '''Redraw the histogram with clipped white point.'''
    
        img = label.stretched_img
        label.stretched_img = apc.clipLevel(img, 0, np.max(img))
        self.updateHist(label)
    
    def stretchHist(self, label):
    
        '''Redraw a stretched version of the histogram.'''
    
        label.stretched_img = apc.stretch(label.stretched_img, float(self.varM.get()))
        self.updateHist(label)
    
    def applyAutoStretch(self, label):
    
        '''Redraw an auto-stretched version of the histogram.'''
    
        label.stretched_img = apc.autostretch(np.load(self.labelNames[label] + '.npy'))
        self.updateHist(label)
    
    def resetToLinear(self, label):
    
        '''Show the histogram of the linear image.'''
    
        label.stretched_img = np.load(self.labelNames[label] + '.npy')
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
    
    def updateDisplayedImage(self, label, fromHist=False):
    
        '''Create a photo image from the raw image of the label.'''
    
        # Save data as temporary image
        plt.imsave(self.labelNames[label] + '.jpg', label.stretched_img, cmap=plt.get_cmap('gray'), vmin=0, vmax=65535)

        plt.close('all')
        
        # Create resized version of image if necessary
        if fromHist: self.loadImage(label)
   
    def deleteTemp(self, exit):
    
        for file in self.labelNames.values():
            try:
                os.remove(file + '.npy')
            except WindowsError:
                pass
            try:
                os.remove(file + '.jpg')
            except WindowsError:
                pass
   
        if exit: self.cont.destroy()
