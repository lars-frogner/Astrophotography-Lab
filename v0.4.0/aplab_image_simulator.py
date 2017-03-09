# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import aplab_common as apc
from aplab_common import C

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
        self.varLF = tk.DoubleVar()
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
        self.varLFLabel = tk.StringVar()
        
        self.tot = 0
        self.max = 0
        
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
        self.varLFLabel.set(u'mag/arcsec\u00B2' if self.cont.hasQE else 'e-/s')
        
        # Place frames
        
        frameHeader.pack(side='top', fill='x')
        
        frameContent.pack(side='top', fill='both', expand=True)
        
        frameLeft.pack(side='left', padx=(30*C.scsx, 0), expand=True)
        frameMiddle.pack(side='left', expand=True)
        frameRight.pack(side='right', padx=(0, 30*C.scsx), expand=True)
        
        frameOptics.pack(side='top', pady=(25*C.scsy, 50*C.scsy), expand=True)
        ttk.Label(frameLeft, text='User modified camera/optics data is displayed in blue' \
                                    + '\n\n*Only required to get suggested camera settings',
                  foreground='dimgray').pack(side='bottom', pady=(8*C.scsy, 25*C.scsy))
        frameSensor.pack(side='bottom', expand=True)
        
        frameUpMiddle.pack(side='top', pady=(20*C.scsy, 40*C.scsy), expand=True)
        frameLowMiddle.pack(side='bottom', pady=(0, 25*C.scsy), expand=True)
        
        frameSignal.pack(side='top', pady=(25*C.scsy, 50*C.scsy), expand=True)
        frameNoise.pack(side='bottom', pady=(0, 25*C.scsy), expand=True)
        
        frameMessage.pack(side='bottom', fill='x')
        
        # *** Header frame ***
        
        labelHeader = ttk.Label(frameHeader, text='Image Simulator', font=large_font, anchor='center')
        
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
        
        # Define optics frame widgets
        
        labelOptics = ttk.Label(frameOptics, text='Optics', font=medium_font, anchor='center', width=28)
        labelOptics.grid(row=0, column=0, columnspan=3, pady=5*C.scsy)
        
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
        labelSensor.grid(row=0, column=0, columnspan=3, pady=5*C.scsy)
        
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
        labelSignal.grid(row=0, column=0, columnspan=3, pady=5*C.scsy)
        
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
        labelNoise.grid(row=0, column=0, columnspan=3, pady=5*C.scsy)
        
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
        self.optionISO = ttk.OptionMenu(frameUpMiddle, self.varISO, None, *C.ISO[self.cont.cnum],
                                        command=self.updateISO)
        
        self.labelGain = ttk.Label(frameUpMiddle, text='Gain:')
        self.optionGain = ttk.OptionMenu(frameUpMiddle, self.varGain, None, *C.GAIN[self.cont.cnum][0],
                                         command=self.updateGain)
        self.labelGain2 = ttk.Label(frameUpMiddle, text='e-/ADU')
        
        self.labelRN = ttk.Label(frameUpMiddle, text='Read noise:')
        self.optionRN = ttk.OptionMenu(frameUpMiddle, self.varRN, None, *C.RN[self.cont.cnum][0],
                                       command=self.updateRN)
        self.labelRN2 = ttk.Label(frameUpMiddle, text='e-')
        
        if not C.is_win:
            self.optionISO.config(width=6)
            self.optionGain.config(width=6)
            self.optionRN.config(width=6)
        
        labelExp = ttk.Label(frameUpMiddle, text='Exposure time:')
        self.entryExp = ttk.Entry(frameUpMiddle, textvariable=self.varExp, font=small_font,
                                  background=C.DEFAULT_BG, width=9)
        labelExp2 = ttk.Label(frameUpMiddle, text='seconds')
        
        labelDF = ttk.Label(frameUpMiddle, text='Dark current:')
        self.entryDF = ttk.Entry(frameUpMiddle, textvariable=self.varDF, font=small_font,
                                 background=C.DEFAULT_BG, width=9)
        labelDF2 = ttk.Label(frameUpMiddle, text='e-/s')
        
        labelSF = ttk.Label(frameUpMiddle, text='Skyglow:')
        self.entrySF = ttk.Entry(frameUpMiddle, textvariable=self.varSF, font=small_font,
                                 background=C.DEFAULT_BG, width=9)
        labelSF2 = ttk.Label(frameUpMiddle, textvariable=self.varSFLabel)
        
        labelTF = ttk.Label(frameUpMiddle, text='Target signal:')
        self.entryTF = ttk.Entry(frameUpMiddle, textvariable=self.varTF, font=small_font,
                                 background=C.DEFAULT_BG, width=9)
        labelTF2 = ttk.Label(frameUpMiddle, textvariable=self.varTFLabel)
        
        labelLF = ttk.Label(frameUpMiddle, text='*Limit signal:')
        self.entryLF = ttk.Entry(frameUpMiddle, textvariable=self.varLF, font=small_font,
                                 background=C.DEFAULT_BG, width=9)
        labelLF2 = ttk.Label(frameUpMiddle, textvariable=self.varLFLabel)
        
        labelSubs = ttk.Label(frameUpMiddle, text='Number of subframes:')
        self.entrySubs = ttk.Entry(frameUpMiddle, textvariable=self.varSubs, font=small_font,
                                   background=C.DEFAULT_BG, width=9)
        labelSubs2 = ttk.Label(frameUpMiddle, text='', width=9)
        
        # Define lower middle frame widgets
        
        buttonData = ttk.Button(frameLowMiddle, text='Calculate data', command=self.processInput, 
                                width=14)
        buttonSim = ttk.Button(frameLowMiddle, text='Simulate image', command=self.simulateController, 
                               width=14)
        buttonSug = ttk.Button(frameLowMiddle, text='Get suggested imaging settings', 
                               command=self.getSuggestedSettings, width=26)
        buttonTransferPlot = ttk.Button(frameLowMiddle, text='Transfer input to Plotting Tool',
                                        command=self.cont.transferToPlot, width=26)
        buttonClear = ttk.Button(frameLowMiddle, text='Clear input', command=self.cont.clearInput)
        
        # Place upper left frame widgets
        
        labelInput.grid(row=0, column=0, columnspan=3, pady=(0, 10*C.scsy))
        
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
        
        labelLF.grid(row=7, column=0, sticky='W')
        self.entryLF.grid(row=7, column=1)
        labelLF2.grid(row=7, column=2, sticky='W')
        
        labelSubs.grid(row=8, column=0, sticky='W')
        self.entrySubs.grid(row=8, column=1)
        labelSubs2.grid(row=8, column=2)
        
        # Place lower middle frame widgets
        
        buttonData.grid(row=0, column=0)
        buttonSim.grid(row=1, column=0)
        buttonSug.grid(row=2, column=0, pady=(6*C.scsy, 0))
        buttonTransferPlot.grid(row=3, column=0, pady=(22*C.scsy, 11*C.scsy))
        buttonClear.grid(row=4, column=0)
        
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
        
        self.varISO.set(C.ISO[self.cont.cnum][self.gain_idx])
        self.varGain.set(C.GAIN[self.cont.cnum][0][self.gain_idx])
        self.varRN.set(C.RN[self.cont.cnum][0][self.rn_idx])
        self.varExp.set('')
        self.varDF.set('')
        self.varSF.set('')
        self.varTF.set('')
        self.varLF.set('')
        self.varSubs.set(1)
        self.varStretch.set(0)
        
        self.varGainInfo.set('{:.3g}'.format(C.GAIN[self.cont.cnum][0][self.gain_idx]))
        self.varSatCapInfo.set('{:d}'.format(C.SAT_CAP[self.cont.cnum][0][self.gain_idx]))
        self.varBLInfo.set('{:d}'.format(C.BLACK_LEVEL[self.cont.cnum][0][self.gain_idx]))
        self.varWLInfo.set('{:d}'.format(C.WHITE_LEVEL[self.cont.cnum][0][self.gain_idx]))
        self.varPSInfo.set('{:g}'.format(C.PIXEL_SIZE[self.cont.cnum][0]))
        self.varQEInfo.set('-' if not self.cont.hasQE else ('{:d}'.format(int(C.QE[self.cont.cnum][0]*100))))
        self.varRNInfo.set('{:.1f}'.format(self.varRN.get()))
        
        # Set text colour according to whether the data is default or user added
        self.labelGainI2.configure(foreground=('black' \
                                   if C.GAIN[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelRNI2.configure(foreground=('black' \
                                 if C.RN[self.cont.cnum][1][self.rn_idx] == 0 else 'navy'))
        self.labelSatCap2.configure(foreground=('black' \
                                    if C.SAT_CAP[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelBL2.configure(foreground=('black' \
                                if C.BLACK_LEVEL[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelWL2.configure(foreground=('black' \
                                if C.WHITE_LEVEL[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelPS2.configure(foreground=('black' if C.PIXEL_SIZE[self.cont.cnum][1] == 0 else 'navy'))
        self.labelQE2.configure(foreground=('black' if C.QE[self.cont.cnum][1] == 0 else 'navy'))
        
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
        self.optionISO.set_menu(*([None] + list(C.ISO[self.cont.cnum])))
        self.optionGain.set_menu(*([None] + list(C.GAIN[self.cont.cnum][0])))
        self.optionRN.set_menu(*([None] + list(C.RN[self.cont.cnum][0])))
            
        if self.cont.isDSLR:
        
            # DSLRs use the ISO optionmenu
            self.labelISO.grid(row=1, column=0, sticky='W')
            self.optionISO.grid(row=1, column=1)
                
        else:
        
            # CCDs use gain and/or read noise optionmenus if they have more than one value to use
                
            if len(C.GAIN[self.cont.cnum][0]) > 1:
                    
                self.labelGain.grid(row=1, column=0, sticky='W')
                self.optionGain.grid(row=1, column=1)
                self.labelGain2.grid(row=1, column=2, sticky='W')
                    
            if len(C.RN[self.cont.cnum][0]) > 1:
                    
                self.labelRN.grid(row=2, column=0, sticky='W')
                self.optionRN.grid(row=2, column=1)
                self.labelRN2.grid(row=2, column=2, sticky='W')

    def updateISO(self, selected_iso):
    
        '''Update index of selected ISO and update sensor labels.'''
        
        self.gain_idx = int(np.where(C.ISO[self.cont.cnum] == selected_iso)[0])
        self.rn_idx = self.gain_idx
        
        self.updateSensorLabels()
    
    def updateGain(self, selected_gain):
    
        '''Update index of selected gain and update sensor labels.'''
    
        self.gain_idx = int(np.where(C.GAIN[self.cont.cnum][0] == selected_gain)[0])
        
        self.updateSensorLabels()
    
    def updateRN(self, selected_rn):
            
        '''Update index of selected ISO and update sensor labels.'''
            
        self.rn_idx = int(np.where(C.RN[self.cont.cnum][0] == selected_rn)[0])
        
        self.updateSensorLabels()
    
    def updateSensorLabels(self):
    
        '''
        Update labels with the gain, read noise and saturation
        level values of currently selected ISO/gain/RN.
        '''
    
        self.varGainInfo.set('{:.3g}'.format(C.GAIN[self.cont.cnum][0][self.gain_idx]))
        self.varRNInfo.set('{:.1f}'.format(C.RN[self.cont.cnum][0][self.rn_idx]))
        self.varSatCapInfo.set('{:d}'.format(C.SAT_CAP[self.cont.cnum][0][self.gain_idx]))
        self.varBLInfo.set('{:d}'.format(C.BLACK_LEVEL[self.cont.cnum][0][self.gain_idx]))
        self.varWLInfo.set('{:d}'.format(C.WHITE_LEVEL[self.cont.cnum][0][self.gain_idx]))
        
        # Set text colour according to whether the data is default or user added
        self.labelGainI2.configure(foreground=('black' if C.GAIN[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelRNI2.configure(foreground=('black' if C.RN[self.cont.cnum][1][self.rn_idx] == 0 else 'navy'))
        self.labelSatCap2.configure(foreground=('black' if C.SAT_CAP[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelBL2.configure(foreground=('black' if C.BLACK_LEVEL[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelWL2.configure(foreground=('black' if C.WHITE_LEVEL[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
    
    def updateOpticsLabels(self):
    
        '''Update labels in the optics frame with the current values.'''
    
        self.varFLInfo.set('{:g}'.format(C.FOCAL_LENGTH[self.cont.tnum][0]))
        self.varEFLInfo.set('{:g}'.format(C.FOCAL_LENGTH[self.cont.tnum][0]*self.cont.FLModVal))
        self.varAPInfo.set('{:g}'.format(C.APERTURE[self.cont.tnum][0]))
        self.varFRInfo.set(u'\u0192/{:g}'.format(round(C.FOCAL_LENGTH[self.cont.tnum][0]*self.cont.FLModVal\
                                                /C.APERTURE[self.cont.tnum][0], 1)))
        self.varISInfo.set('{:.3g}'.format(self.cont.ISVal))
        self.varRLInfo.set('{:.2g}'.format(1.22*5.5e-4*180*3600/(C.APERTURE[self.cont.tnum][0]*np.pi)))
        
        # Set text colour according to whether the data is default or user added
        self.labelFL2.configure(foreground=('black' if C.FOCAL_LENGTH[self.cont.tnum][1] == 0 else 'navy'))
        self.labelAP2.configure(foreground=('black' if C.APERTURE[self.cont.tnum][1] == 0 else 'navy'))
    
    def processInput(self):
    
        '''Check that the inputted values are valid, then run calculations method.'''
        
        self.noInvalidInput = False
        
        try:
            self.exposure = self.varExp.get()
            
        except tk.TclError:
            self.varMessageLabel.set('Invalid input for exposure time.')
            self.labelMessage.configure(foreground='crimson')
            self.emptyInfoLabels()
            return None
        
        try:
            self.df = self.varDF.get()
            
        except tk.TclError:
            self.varMessageLabel.set('Invalid input for dark current.')
            self.labelMessage.configure(foreground='crimson')
            self.emptyInfoLabels()
            return None
        
        try:
            self.sf = (self.cont.convSig(self.varSF.get(), False) if self.cont.lumSignalType.get() \
                                                        else self.varSF.get())
            
        except tk.TclError:
            self.varMessageLabel.set('Invalid input for skyglow.')
            self.labelMessage.configure(foreground='crimson')
            self.emptyInfoLabels()
            return None
            
        try:
            self.tf = (self.cont.convSig(self.varTF.get(), False) if self.cont.lumSignalType.get() \
                                                        else self.varTF.get())
            
        except tk.TclError:
            self.varMessageLabel.set('Invalid input for target signal.')
            self.labelMessage.configure(foreground='crimson')
            self.emptyInfoLabels()
            return None
            
        try:
            self.subs = self.varSubs.get()
            
        except tk.TclError:
            self.varMessageLabel.set('Invalid input for number of subframes. Must be an integer.')
            self.labelMessage.configure(foreground='crimson')
            self.emptyInfoLabels()
            return None
        
        self.noInvalidInput = True
        
        self.calculate()
    
    def calculate(self):
    
        '''Calculate SNR, dynamic range and noise values and set to the corresponding labels.'''
        
        gain = C.GAIN[self.cont.cnum][0][self.gain_idx] # Gain [e-/ADU]
        rn = C.RN[self.cont.cnum][0][self.rn_idx]       # Read noise [e-]
        
        dark_signal_e = self.df*self.exposure   # Signal from dark current [e-]
        sky_signal_e = self.sf*self.exposure    # Signal from skyglow [e-]
        target_signal_e = self.tf*self.exposure # Signal from target signal [e-]
        
        sat_cap = C.SAT_CAP[self.cont.cnum][0][self.gain_idx] # Saturation capacity [e-]
        
        dn = np.sqrt(dark_signal_e)                          # Dark noise [e-]
        sn = np.sqrt(sky_signal_e)                           # Skyglow noise [e-]
        tbgn = np.sqrt(rn**2 + dark_signal_e + sky_signal_e) # Total background noise [e-]
        
        snr = target_signal_e/np.sqrt(target_signal_e + tbgn**2) # Signal to noise ratio in subframe
        stack_snr = snr*np.sqrt(self.subs)        # Signal to noise ratio in stacked frame
        
        self.dr = np.log10(sat_cap/tbgn)/np.log10(2.0) # Dynamic range [stops]
        factor = 10*np.log(2.0)/np.log(10.0)
        
        # Update labels
        self.varSNRInfo.set('{:.1f}'.format(snr))
        self.varStackSNRInfo.set('{:.1f}'.format(stack_snr))
        self.varDRInfo.set('{:.1f}'.format(self.dr if self.cont.stopsDRUnit.get() else self.dr*factor))
        self.varDNInfo.set('{:.1f}'.format(dn))
        self.varSNInfo.set('{:.1f}'.format(sn))
        self.varTBGNInfo.set('{:.1f}'.format(tbgn))
        
        self.dataCalculated = True
        
        self.varMessageLabel.set('SNR calculated.')
        self.labelMessage.configure(foreground='navy')
    
    def simulateController(self, fromCheckbutton=False):
    
        '''Changes the displayed simulated image according to various conditions.'''
        
        # If the "Simulate image" button is pressed
        if not fromCheckbutton:
        
            # Calculate data and run simulation if all input is valid
        
            self.processInput()
        
            if self.noInvalidInput:
            
                # Show error message if the number of subframes is too high (to avoid memory error)
                if self.subs > 200:
                    self.varMessageLabel.set(\
                    'Please decrease number of subframes to 200 or less before simulating.')
                    self.labelMessage.configure(foreground='crimson')
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
        self.labelMessage.configure(foreground='navy')
        self.labelMessage.update_idletasks()
    
        gain = float(C.GAIN[self.cont.cnum][0][self.gain_idx]) # Gain [e-/ADU]
        rn = C.RN[self.cont.cnum][0][self.rn_idx] # Read noise [e-]
    
        dark_signal_e = self.df*self.exposure # Mean dark current signal [e-]
        sky_signal_e = self.sf*self.exposure # Mean sky background signal [e-]
        target_signal_e = self.tf*self.exposure # Mean target signal [e-]

        imsize = (256, 256, self.subs) # Image dimensions (including stack size)
            
        map = np.where(self.img_orig > 0.0) # Locations of target pixels
        
        # Generate sky, target and dark images from Poisson distributions
        dark = np.random.poisson(dark_signal_e, imsize)/gain
        sky = np.random.poisson(sky_signal_e, imsize)/gain
        target = np.random.poisson(target_signal_e, imsize)/gain
        
        # Generate bias images with correct amount of Gaussian read noise
        bias = C.BLACK_LEVEL[self.cont.cnum][0][self.gain_idx] \
               + (np.random.normal(0, rn, imsize).astype(int))/gain
        
        # Combine signals to get final images
        img = bias + dark + sky
        for i in range(self.subs):
            img[:, :, i][map] += target[:, :, i][map]*self.img_orig[map]
        
        # Truncate invalid pixel values
        img[img < 0.0] = 0.0
        img[img > C.WHITE_LEVEL[self.cont.cnum][0][self.gain_idx]] \
                                                     = C.WHITE_LEVEL[self.cont.cnum][0][self.gain_idx]
        
        # Take mean of images to get a stacked image
        img = np.mean(img, axis=2)
        
        # Scale pixel values to be between 0 and 1, with 1 corresponding to the saturation capacity
        img = img/C.WHITE_LEVEL[self.cont.cnum][0][self.gain_idx]
        
        # Save linear and non-linear version of the simulated image
        plt.imsave('sim.jpg', img, cmap=plt.get_cmap('gray'), vmin = 0.0, vmax = 1.0)
        plt.imsave('sim_str.jpg', apc.autostretch(img), cmap=plt.get_cmap('gray'), vmin=0, vmax=65535)
        
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
        self.labelMessage.configure(foreground='navy')

    def activateTooltips(self):
    
        '''Add tooltips to all relevant widgets.'''
    
        apc.createToolTip(self.entryExp, C.TTExp, self.cont.tt_fs)
        apc.createToolTip(self.entryDF, C.TTDF, self.cont.tt_fs)
        apc.createToolTip(self.entrySF, C.TTSFLum if self.cont.hasQE else C.TTSFElectron, self.cont.tt_fs)
        apc.createToolTip(self.entryTF, C.TTTFLum if self.cont.hasQE else C.TTTFElectron, self.cont.tt_fs)
        apc.createToolTip(self.entryLF, C.TTLFLum if self.cont.hasQE else C.TTLFElectron, self.cont.tt_fs)
        apc.createToolTip(self.entrySubs, C.TTSubs, self.cont.tt_fs)
        apc.createToolTip(self.labelSNR2, C.TTSNR, self.cont.tt_fs)
        apc.createToolTip(self.labelStackSNR2, C.TTStackSNR, self.cont.tt_fs)
        apc.createToolTip(self.labelDR2, C.TTDR, self.cont.tt_fs)
        apc.createToolTip(self.labelFL2, C.TTFL, self.cont.tt_fs)
        apc.createToolTip(self.labelEFL2, C.TTEFL, self.cont.tt_fs)
        apc.createToolTip(self.labelAP2, C.TTAP, self.cont.tt_fs)
        apc.createToolTip(self.labelFR2, C.TTFR, self.cont.tt_fs)
        apc.createToolTip(self.labelIS2, C.TTIS, self.cont.tt_fs)
        apc.createToolTip(self.labelRL2, C.TTRL, self.cont.tt_fs)
        apc.createToolTip(self.labelGainI2, C.TTGain, self.cont.tt_fs)
        apc.createToolTip(self.labelSatCap2, C.TTSatCap, self.cont.tt_fs)
        apc.createToolTip(self.labelBL2, C.TTBL, self.cont.tt_fs)
        apc.createToolTip(self.labelWL2, C.TTWL, self.cont.tt_fs)
        apc.createToolTip(self.labelPS2, C.TTPS, self.cont.tt_fs)
        apc.createToolTip(self.labelQE2, C.TTQE, self.cont.tt_fs)
        apc.createToolTip(self.labelRNI2, C.TTRN, self.cont.tt_fs)
        apc.createToolTip(self.labelDN2, C.TTDN, self.cont.tt_fs)
        apc.createToolTip(self.labelSN2, C.TTSN, self.cont.tt_fs)
        apc.createToolTip(self.labelTBGN2, C.TTTotN, self.cont.tt_fs)
        
        if self.topCanvas.winfo_exists():
            
            apc.createToolTip(self.checkbuttonStretch, C.TTStretch, self.cont.tt_fs)
        
    def deactivateTooltips(self):
    
        '''Remove tooltips from all widgets.'''
    
        for widget in [self.entryExp, self.entryDF, self.entrySF, self.entryTF, self.entryLF,
                       self.entrySubs, self.labelSNR2, self.labelStackSNR2, self.labelDR2, self.labelFL2, 
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
            self.topCanvas = tk.Toplevel(bg=C.DEFAULT_BG)
            self.topCanvas.title('Simulated image')
            self.cont.addIcon(self.topCanvas)
            apc.setupWindow(self.topCanvas, 330, 350)
            self.topCanvas.focus_force()
            self.topCanvas.wm_attributes('-topmost', 1)
                
            self.canvasSim = tk.Canvas(self.topCanvas, width=round(320*C.scsy),
                                       height=round(320*C.scsy), bg='white', bd=2,
                                       relief='groove')
                
            self.canvasSim.pack(side='top', expand=True)
        
            # Create stretch checkbutton
            frameStretch = ttk.Frame(self.topCanvas)
        
            labelStretch = ttk.Label(frameStretch, text='Stretch:')
            self.checkbuttonStretch = tk.Checkbutton(frameStretch, variable=self.varStretch,
                                      command=lambda: self.simulateController(fromCheckbutton=True))
            if self.cont.tooltipsOn.get():
                apc.createToolTip(self.checkbuttonStretch, C.TTStretch, self.cont.tt_fs)
            
            frameStretch.pack(side='bottom', expand=True)
        
            labelStretch.pack(side='left')
            self.checkbuttonStretch.pack(side='left')
            
            self.topCanvas.update()
    
    def getSuggestedSettings(self):
        
        try:
            df = self.varDF.get()
            sf = (self.cont.convSig(self.varSF.get(), False) if self.cont.lumSignalType.get() \
                                                            else self.varSF.get())
            tf = (self.cont.convSig(self.varTF.get(), False) if self.cont.lumSignalType.get() \
                                                        else self.varTF.get())
                
        except tk.TclError:
            self.varMessageLabel.set(\
                 'Requires valid input for dark current, skyglow and target signal.')
            self.labelMessage.configure(foreground='crimson')
            self.emptyInfoLabels()
            return None
            
        try:
            lf = (self.cont.convSig(self.varLF.get(), False) if self.cont.lumSignalType.get() \
                                                            else self.varLF.get())
        except tk.TclError:
            self.varLF.set('')
            lf = tf
            
        maxf = lf + sf + df
        
        varTot = tk.DoubleVar()
        varMax = tk.DoubleVar()
        varMessageLabel = tk.StringVar()
        
        varTot.set('' if self.tot == 0 else self.tot/3600)
        varMax.set('' if self.max == 0 else self.max)
        
        def findCameraSettings():
        
            try:
                self.tot = varTot.get()*3600
            except:
                varMessageLabel.set('Invalid total imaging time.')
                return None
                
            try:
                self.max = varMax.get()
            except:
                varMessageLabel.set('Invalid max exposure time.')
                return None
        
            if self.cont.isDSLR:
        
                iso = C.ISO[self.cont.cnum]
                
                sat_cap = C.SAT_CAP[self.cont.cnum][0]
                
                isTooLong = 0.9*sat_cap/maxf > self.max
                exposure1 = 0.9*sat_cap/maxf*np.invert(isTooLong) + self.max*isTooLong
                    
                subs1 = self.tot/exposure1
                
                rn1 = C.RN[self.cont.cnum][0]
                
                snr1 = tf*exposure1/np.sqrt(tf*exposure1 + sf*exposure1 + df*exposure1 + rn1**2)
                stack_snr1 = snr1*np.sqrt(subs1)
            
                idx = np.argmax(stack_snr1)
                
                opt_iso = iso[idx]
                opt_exp = exposure1[idx]
                sat_exp = (0.9*sat_cap/maxf)[idx]
                opt_subs = subs1[idx]
                
            else:
                idx = self.rn_idx
                opt_iso = False
                opt_exp = np.min([0.9*C.SAT_CAP[self.cont.cnum][self.gain_idx]/maxf, self.max])
                sat_exp = 0.9*C.SAT_CAP[self.cont.cnum][self.gain_idx]/maxf
                opt_subs = self.tot/opt_exp
            
            exposure2 = np.linspace(1, 900, 200)
            subs2 = self.tot/exposure2
            
            rn2 = C.RN[self.cont.cnum][0][idx]
            
            in_snr = tf*opt_exp/np.sqrt(tf*opt_exp + sf*opt_exp + df*opt_exp + rn2**2)
            in_stack_snr = in_snr*np.sqrt(opt_subs)
            
            snr2 = tf*exposure2/np.sqrt(tf*exposure2 + sf*exposure2 + df*exposure2 + rn2**2)
            stack_snr2 = snr2*np.sqrt(subs2)
            
            better_exps = exposure2[:-27][(stack_snr2[27:] - stack_snr2[:-27])/stack_snr2[:-27] < 0.003]
            if len(better_exps) > 0 and better_exps[0] < opt_exp:
                opt_exp = int(round(better_exps[0]/10.0)*10)
                opt_subs = self.tot/opt_exp
                
            snr = tf*opt_exp/np.sqrt(tf*opt_exp + sf*opt_exp + df*opt_exp + rn2**2)
            stack_snr = snr*np.sqrt(opt_subs)
            
            tbgn = np.sqrt(sf*opt_exp + df*opt_exp + rn2**2)
            sat_cap = C.SAT_CAP[self.cont.cnum][0][idx if opt_iso else self.gain_idx]
            dr = np.log10(sat_cap/tbgn)/np.log10(2.0)
            if self.cont.dBDRUnit.get(): dr *= 10*np.log(2.0)/np.log(10.0)
            
            topSettings.destroy()
            self.displaySuggestedSettings(opt_iso, opt_exp, sat_exp, self.max, int(np.ceil(opt_subs)), 
                                          in_stack_snr, snr, stack_snr, dr)
            
        topSettings = tk.Toplevel()
        topSettings.title('Get suggested imaging settings')
        self.cont.addIcon(topSettings)
        apc.setupWindow(topSettings, 300, 180)
        topSettings.focus_force()
    
        ttk.Label(topSettings, text='Please provide the requested information:')\
                 .pack(side='top', pady=(15*C.scsy, 10*C.scsy), expand=True)
            
        frameInput = ttk.Frame(topSettings)
        frameInput.pack(side='top', pady=(7*C.scsy, 10*C.scsy), expand=True)
            
        ttk.Label(frameInput, text='Total imaging time: ').grid(row=0, column=0, sticky='W')
        entryTot = ttk.Entry(frameInput, textvariable=varTot, font=self.cont.small_font,
                  background=C.DEFAULT_BG, width=6)
        entryTot.grid(row=0, column=1)
        ttk.Label(frameInput, text=' hours').grid(row=0, column=2, sticky='W')
                  
        ttk.Label(frameInput, text='Max exposure time: ').grid(row=1, column=0, sticky='W')
        entryMax = ttk.Entry(frameInput, textvariable=varMax, font=self.cont.small_font,
                  background=C.DEFAULT_BG, width=6)
        entryMax.grid(row=1, column=1)
        ttk.Label(frameInput, text=' seconds').grid(row=1, column=2, sticky='W')
           
        if self.cont.tooltipsOn.get():
            apc.createToolTip(entryTot, C.TTTotal, self.cont.tt_fs)
            apc.createToolTip(entryMax, C.TTMax, self.cont.tt_fs)
        
        frameButtons = ttk.Frame(topSettings)
        frameButtons.pack(side='top', expand=True, pady=(10*C.scsy, 10*C.scsy))
        ttk.Button(frameButtons, text='Done',
                   command=findCameraSettings).grid(row=0, column=0, padx=(0, 5*C.scsx))
        ttk.Button(frameButtons, text='Cancel',
                   command=lambda: topSettings.destroy()).grid(row=0, column=1)
              
        ttk.Label(topSettings, textvariable=varMessageLabel, font=self.cont.small_font,
                  background=C.DEFAULT_BG).pack(side='top', pady=(0, 5*C.scsy), expand=True)
   
    def displaySuggestedSettings(self, iso, exp, sat_exp, max, subs, in_stack_snr, snr, stack_snr, dr):
    
        topSettings = tk.Toplevel()
        topSettings.title('Suggested imaging settings')
        self.cont.addIcon(topSettings)
        apc.setupWindow(topSettings, 330, 430)
        topSettings.focus_force()
        
        frameTop = ttk.Frame(topSettings)
        frameTop.pack(side='top', pady=(20, 6*C.scsy), expand=True)
        
        ttk.Label(frameTop, text='Suggested imaging settings',
                  font=self.cont.smallbold_font,
                  anchor='center').pack(side='top', pady=(0, 10*C.scsy))
        
        frameResults = ttk.Frame(frameTop)
        frameResults.pack(side='top')
        
        if iso:
            labelISO1 = ttk.Label(frameResults, text='ISO: ')
            labelISO1.grid(row=0, column=0, sticky='W')
            labelISO2 = ttk.Label(frameResults, text=('{:d}'.format(iso)), width=7, anchor='center')
            labelISO2.grid(row=0, column=1)
            apc.createToolTip(labelISO2, C.TTSet, self.cont.tt_fs)
        
        labelExp1 = ttk.Label(frameResults, text='Exposure time: ')
        labelExp1.grid(row=1, column=0, sticky='W')
        labelExp2 = ttk.Label(frameResults, text=('{:d}'.format(exp)), width=7, anchor='center')
        labelExp2.grid(row=1, column=1)
        labelExp3 = ttk.Label(frameResults, text=' seconds')
        labelExp3.grid(row=1, column=2, sticky='W')
        
        labelSubs1 = ttk.Label(frameResults, text='Number of subframes: ')
        labelSubs1.grid(row=2, column=0, sticky='W')
        labelSubs2 = ttk.Label(frameResults, text=('{:d}'.format(subs)), width=7, anchor='center')
        labelSubs2.grid(row=2, column=1)
        
        for widget in [labelExp2, labelSubs2]:
            apc.createToolTip(widget, C.TTSet, self.cont.tt_fs)
        
        frameMiddle = ttk.Frame(topSettings)
        frameMiddle.pack(side='top', pady=(8*C.scsy, 6*C.scsy), expand=True)
        
        ttk.Label(frameMiddle, text='Resulting signal values',
                  font=self.cont.smallbold_font,
                  anchor='center').pack(side='top', pady=(0, 10*C.scsy))
        
        frameResultVals = ttk.Frame(frameMiddle)
        frameResultVals.pack(side='top')
        
        ttk.Label(frameResultVals, text='Sub SNR: ').grid(row=0, column=0, sticky='W')
        ttk.Label(frameResultVals, text=('{:.1f}'.format(snr)), width=7,
                  anchor='center').grid(row=0, column=1)
        
        ttk.Label(frameResultVals, text='Stack SNR: ').grid(row=1, column=0, sticky='W')
        ttk.Label(frameResultVals, text=('{:.1f}'.format(stack_snr)), width=7,
                  anchor='center').grid(row=1, column=1)
        
        ttk.Label(frameResultVals, text='Dynamic range: ').grid(row=2, column=0, sticky='W')
        ttk.Label(frameResultVals, text=('{:.1f}'.format(dr)), width=7,
                  anchor='center').grid(row=2, column=1)
        ttk.Label(frameResultVals, text=(' stops' if self.cont.stopsDRUnit.get() else ' dB'))\
                 .grid(row=2, column=2, sticky='W')
        
        frameBottom = ttk.Frame(topSettings)
        frameBottom.pack(side='top', pady=(8*C.scsy, 10*C.scsy), expand=True)
                 
        ttk.Label(frameBottom, text='Detailed information',
                  font=self.cont.smallbold_font,
                  anchor='center').pack(side='top', pady=(0, 10*C.scsy))
        
        frameCompVals = ttk.Frame(frameBottom)
        frameCompVals.pack(side='top')
        
        ttk.Label(frameCompVals, text='User limited exp. time: ').grid(row=0, column=0, sticky='W')
        ttk.Label(frameCompVals, text=('{:d}'.format(max)), width=7,
                  anchor='center').grid(row=0, column=1)
        ttk.Label(frameCompVals, text=' seconds').grid(row=0, column=2, sticky='W')
        
        ttk.Label(frameCompVals, text='Saturation limited exp. time: ').grid(row=1, column=0, sticky='W')
        ttk.Label(frameCompVals, text=('{:d}'.format(sat_exp)), width=7,
                  anchor='center').grid(row=1, column=1)
        ttk.Label(frameCompVals, text=' seconds').grid(row=1, column=2, sticky='W')
        
        ttk.Label(frameCompVals, text='Reduced exp. time: ').grid(row=2, column=0, sticky='W')
        ttk.Label(frameCompVals, text=('{:d}'.format(exp)), width=7,
                  anchor='center').grid(row=2, column=1)
        ttk.Label(frameCompVals, text=' seconds').grid(row=2, column=2, sticky='W')
        
        ttk.Label(frameCompVals, text='Stack SNR loss from reduction: ').grid(row=3, column=0, sticky='W')
        ttk.Label(frameCompVals, text=('{:.2f}%%'.format((in_stack_snr - stack_snr)*100/stack_snr)), width=7,
                  anchor='center').grid(row=3, column=1)
        
        ttk.Button(topSettings, text='Close', command=lambda: topSettings.destroy())\
                  .pack(side='bottom', pady=(0, 15*C.scsy), expand=True)
