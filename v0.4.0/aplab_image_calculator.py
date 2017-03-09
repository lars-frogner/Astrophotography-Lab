# -*- coding: utf-8 -*-

import Tkinter as tk
import ttk
import numpy as np
import aplab_common as apc
from aplab_common import C

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
        
        self.varTransfLim = tk.IntVar()
        
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
        
        frameLeft.pack(side='left', padx=(30*C.scsx, 0), expand=True)
        frameMiddle.pack(side='left', expand=True)
        frameRight.pack(side='right', padx=(0, 30*C.scsx), expand=True)
        
        frameOptics.pack(side='top', pady=(25*C.scsy, 50*C.scsy), expand=True)
        ttk.Label(frameLeft, text='User modified camera/optics data is displayed in blue',
                  foreground='dimgray').pack(side='bottom', pady=(8*C.scsy, 25*C.scsy))
        frameSensor.pack(side='bottom', expand=True)
        
        frameUpMiddle.pack(side='top', pady=(25*C.scsy, 20*C.scsy), expand=True)
        frameLowMiddle.pack(side='bottom', pady=(0, 25*C.scsy), expand=True)
        
        frameSignal.pack(side='top', pady=(25*C.scsy, 50*C.scsy), expand=True)
        frameNoise.pack(side='bottom', pady=(0, 25*C.scsy), expand=True)
        
        frameMessage.pack(side='bottom', fill='x')
        
        # *** Header frame ***
        
        labelHeader = ttk.Label(frameHeader, text='Image Calculator', font=large_font, anchor='center')
        
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
        
        labelSignal = ttk.Label(frameSignal, text='Signal', font=medium_font, anchor='center', width=28)
        labelSignal.grid(row=0, column=0, columnspan=3, pady=5*C.scsy)
        
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
        labelNoiseHeader.grid(row=0, column=0, columnspan=3, pady=5*C.scsy)
        
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
        self.entryExp = ttk.Entry(frameUpMiddle, textvariable=self.varExp, width=9, font=small_font,
                                  background=C.DEFAULT_BG)
        labelExp2 = ttk.Label(frameUpMiddle, text='seconds')
        
        labelToggleDark = ttk.Label(frameUpMiddle, text='Use dark frame info:')
        self.checkbuttonToggleDark = tk.Checkbutton(frameUpMiddle, variable=self.varUseDark,
                                                    font=small_font, command=self.toggleDarkInputMode)
        labelToggleDark2 = ttk.Label(frameUpMiddle, text='', width=9)
        
        self.labelDark = ttk.Label(frameUpMiddle, textvariable=self.varDarkLabel)
        self.entryDark = ttk.Entry(frameUpMiddle, textvariable=self.varDark, font=small_font,
                                   background=C.DEFAULT_BG, width=9)
        self.labelDark2 = ttk.Label(frameUpMiddle, text='ADU')
        
        self.labelBGN = ttk.Label(frameUpMiddle, text='Background noise:')
        self.entryBGN = ttk.Entry(frameUpMiddle, textvariable=self.varBGN, font=small_font,
                                  background=C.DEFAULT_BG, width=9)
        self.labelBGN2 = ttk.Label(frameUpMiddle, text='ADU')
        
        labelBGL = ttk.Label(frameUpMiddle, text='Background level:')
        self.entryBGL = ttk.Entry(frameUpMiddle, textvariable=self.varBGL, font=small_font,
                                  background=C.DEFAULT_BG, width=9)
        labelBGL2 = ttk.Label(frameUpMiddle, text='ADU')
        
        labelTarget = ttk.Label(frameUpMiddle, text='Target level:')
        self.entryTarget = ttk.Entry(frameUpMiddle, textvariable=self.varTarget, font=small_font,
                                     background=C.DEFAULT_BG, width=9)
        labelTarget2 = ttk.Label(frameUpMiddle, text='ADU')
        
        # Define lower middle frame widgets
        
        buttonData = ttk.Button(frameLowMiddle, text='Calculate data', command=self.processInput,
                                width=14)
                                
        frameLim = ttk.Frame(frameLowMiddle)
        labelLim = ttk.Label(frameLim, text='Transfer limit signal only:')
        self.checkbuttonLim = tk.Checkbutton(frameLim, variable=self.varTransfLim)
        
        buttonTransferSim = ttk.Button(frameLowMiddle, text='Transfer data to Image Simulator',
                                       command=self.cont.transferToSim, width=29)
        buttonTransferPlot = ttk.Button(frameLowMiddle, text='Transfer data to Plotting Tool',
                                        command=self.cont.transferToPlot, width=29)
        
        buttonClear = ttk.Button(frameLowMiddle, text='Clear input', command=self.cont.clearInput)                    
        
        self.setDefaultValues()
        
        # Place upper middle frame widgets
        
        labelInput.grid(row=0, column=0, columnspan=3, pady=(0, 10*C.scsy))
        
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
        
        buttonData.grid(row=0, column=0, pady=(0, 22*C.scsy))
        
        frameLim.grid(row=1, column=0)
        labelLim.pack(side='left')
        self.checkbuttonLim.pack(side='left')
        
        buttonTransferSim.grid(row=2, column=0)
        buttonTransferPlot.grid(row=3, column=0)
        buttonClear.grid(row=4, column=0, pady=(11*C.scsy, 0))
        
        # Place more widgets according to camera type
        self.reconfigureNonstaticWidgets()
        
        # *** Message frame ***
        
        self.labelMessage = ttk.Label(frameMessage, textvariable=self.varMessageLabel, anchor='center')
        ttk.Separator(frameMessage, orient='horizontal').pack(side='top', fill='x')
        self.labelMessage.pack(fill='x')
        
        if self.cont.tooltipsOn.get():
            self.activateTooltips()

    def emptyInfoLabels(self):
    
        '''Clear labels showing calculated values.'''
    
        self.varSNRInfo.set('-')
        self.varDRInfo.set('-')
        self.varSNInfo.set('-')
        self.varDNInfo.set('-')
        self.varTBGNInfo.set('-')
        self.varDFInfo.set('-')
        try:
            self.labelSF2.configure(background=C.DEFAULT_BG, foreground='black')
            self.labelTF2.configure(background=C.DEFAULT_BG, foreground='black')
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
        
        self.varISO.set(C.ISO[self.cont.cnum][self.gain_idx])
        self.varGain.set(C.GAIN[self.cont.cnum][0][self.gain_idx])
        self.varRN.set(C.RN[self.cont.cnum][0][self.rn_idx])
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
        
        self.varGainInfo.set('%.3g' % C.GAIN[self.cont.cnum][0][self.gain_idx])
        self.varSatCapInfo.set('%d' % C.SAT_CAP[self.cont.cnum][0][self.gain_idx])
        self.varBLInfo.set('%d' % C.BLACK_LEVEL[self.cont.cnum][0][self.gain_idx])
        self.varWLInfo.set('%d' % C.WHITE_LEVEL[self.cont.cnum][0][self.gain_idx])
        self.varPSInfo.set('%g' % C.PIXEL_SIZE[self.cont.cnum][0])
        self.varQEInfo.set('-' if not self.cont.hasQE else ('%d' % (C.QE[self.cont.cnum][0]*100)))
        
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
        
        self.varRNInfo.set('%.1f' % C.RN[self.cont.cnum][0][self.rn_idx])
        
        self.checkbuttonLim.configure(state='disabled')
        self.varTransfLim.set(0)
        
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
        self.optionISO.set_menu(*([None] + list(C.ISO[self.cont.cnum])))
        self.optionGain.set_menu(*([None] + list(C.GAIN[self.cont.cnum][0])))
        self.optionRN.set_menu(*([None] + list(C.RN[self.cont.cnum][0])))
            
        if self.cont.isDSLR:
                
            # DSLRs use the ISO optionmenu and the background noise entry
                
            self.labelISO.grid(row=1, column=0, sticky='W')
            self.optionISO.grid(row=1, column=1)
            
            self.labelBGN.grid(row=6, column=0, sticky='W')
            self.entryBGN.grid(row=6, column=1)
            self.labelBGN2.grid(row=6, column=2, sticky='W')
        
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
    
        self.varGainInfo.set('%.3g' % C.GAIN[self.cont.cnum][0][self.gain_idx])
        self.varRNInfo.set('%.1f' % C.RN[self.cont.cnum][0][self.rn_idx])
        self.varSatCapInfo.set('%d' % C.SAT_CAP[self.cont.cnum][0][self.gain_idx])
        self.varBLInfo.set('%d' % C.BLACK_LEVEL[self.cont.cnum][0][self.gain_idx])
        self.varWLInfo.set('%d' % C.WHITE_LEVEL[self.cont.cnum][0][self.gain_idx])
        
        # Set text colour according to whether the data is default or user added
        self.labelGainI2.configure(foreground=('black' if C.GAIN[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelRNI2.configure(foreground=('black' if C.RN[self.cont.cnum][1][self.rn_idx] == 0 else 'navy'))
        self.labelSatCap2.configure(foreground=('black' if C.SAT_CAP[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelBL2.configure(foreground=('black' if C.BLACK_LEVEL[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
        self.labelWL2.configure(foreground=('black' if C.WHITE_LEVEL[self.cont.cnum][1][self.gain_idx] == 0 else 'navy'))
    
    def updateOpticsLabels(self):
    
        '''Update labels in the optics frame with the current values.'''
    
        self.varFLInfo.set('%g' % C.FOCAL_LENGTH[self.cont.tnum][0])
        self.varEFLInfo.set('%g' % (C.FOCAL_LENGTH[self.cont.tnum][0]*self.cont.FLModVal))
        self.varAPInfo.set('%g' % C.APERTURE[self.cont.tnum][0])
        self.varFRInfo.set(u'\u0192/%g' % round(C.FOCAL_LENGTH[self.cont.tnum][0]*self.cont.FLModVal\
                                                /C.APERTURE[self.cont.tnum][0], 1))
        self.varISInfo.set('%.3g' % (self.cont.ISVal))
        self.varRLInfo.set('%.2g' % (1.22*5.5e-4*180*3600/(C.APERTURE[self.cont.tnum][0]*np.pi)))
        
        # Set text colour according to whether the data is default or user added
        self.labelFL2.configure(foreground=('black' if C.FOCAL_LENGTH[self.cont.tnum][1] == 0 else 'navy'))
        self.labelAP2.configure(foreground=('black' if C.APERTURE[self.cont.tnum][1] == 0 else 'navy'))
        
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
                apc.createToolTip(self.labelSN2, C.TTSN, self.cont.tt_fs)
                apc.createToolTip(self.labelSF2, C.TTSFLum if self.cont.lumSignalType.get() else C.TTSFElectron,
                              self.cont.tt_fs)
            
        else:
        
            # Dark input, noise and current widgets remain hidden
            
            # Change labels for skyglow noise/flux
            self.varSNTypeLabel.set('Sky and dark noise: ')
            
            if self.cont.tooltipsOn.get(): apc.createToolTip(self.labelSN2, C.TTDSN, self.cont.tt_fs)
            
            if not self.cont.isDSLR:
            
                self.varSFTypeLabel.set('Background signal: ')
                
                if self.cont.tooltipsOn.get():
                    apc.createToolTip(self.labelSF2, C.TTDSFPhoton if self.cont.lumSignalType.get() else C.TTDSFElectron,
                                  self.cont.tt_fs)
            
        self.emptyInfoLabels() # Clear labels
    
    def processInput(self):
    
        '''Check that the inputted values are valid, then run calculations method.'''
        
        try:
            self.exposure = self.varExp.get()
            
        except ValueError:
            self.varMessageLabel.set('Invalid input for exposure time.')
            self.labelMessage.configure(foreground='crimson')
            self.emptyInfoLabels()
            return None
        
        self.use_dark = self.varUseDark.get()
        
        try:
            self.dark_input = self.varDark.get()
            
        except ValueError:
            if self.use_dark:
                self.varMessageLabel.set('Invalid input for dark frame noise.' \
                                         if self.cont.isDSLR else 'Invalid input for dark frame level.')
                self.labelMessage.configure(foreground='crimson')
                self.emptyInfoLabels()
                return None
            else:
                self.dark_input = 0
        
        try:
            self.bgn = self.varBGN.get()
            
        except ValueError:
            if self.cont.isDSLR:
                self.varMessageLabel.set('Invalid input for background noise.')
                self.labelMessage.configure(foreground='crimson')
                self.emptyInfoLabels()
                return None
            else:
                self.bgn = 0
        
        try:
            self.bgl = self.varBGL.get()
            
        except ValueError:
            self.varMessageLabel.set('Invalid input for background level.')
            self.labelMessage.configure(foreground='crimson')
            self.emptyInfoLabels()
            return None
            
        try:
            self.target = self.varTarget.get()
            
        except ValueError:
            self.varTarget.set('')
            self.target = 0
        
        if self.cont.isDSLR:
        
            if self.bgl < C.BLACK_LEVEL[self.cont.cnum][0][self.gain_idx]:
                self.varMessageLabel.set('The background level cannot be lower than the black level.')
                self.labelMessage.configure(foreground='crimson')
                self.emptyInfoLabels()
                return None
                
        elif self.use_dark:
        
            if self.dark_input < C.BLACK_LEVEL[self.cont.cnum][0][self.gain_idx]:
                self.varMessageLabel.set('The dark frame level cannot be lower than the black level.')
                self.labelMessage.configure(foreground='crimson')
                self.emptyInfoLabels()
                return None
                
            if self.bgl < self.dark_input:
                self.varMessageLabel.set('The background level cannot be lower than the dark frame level.')
                self.labelMessage.configure(foreground='crimson')
                self.emptyInfoLabels()
                return None
            
        if 0 < self.target < self.bgl:
            self.varMessageLabel.set('The target level cannot be lower than the background level.')
            self.labelMessage.configure(foreground='crimson')
            self.emptyInfoLabels()
            return None
        
        if self.target > C.WHITE_LEVEL[self.cont.cnum][0][self.gain_idx]:
            self.varMessageLabel.set('The target level cannot be higher than the white level.')
            self.labelMessage.configure(foreground='crimson')
            self.emptyInfoLabels()
            return None
        
        self.calculate()
    
    def calculate(self):
    
        '''Calculate SNR, dynamic range, noise and flux values and set to the corresponding labels.'''
        
        message = 'Image data calculated.'
        
        gain = C.GAIN[self.cont.cnum][0][self.gain_idx] # Gain [e-/ADU]
        rn = C.RN[self.cont.cnum][0][self.rn_idx]       # Read noise [e-]
        
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
            sky_signal_e = (self.bgl - C.BLACK_LEVEL[self.cont.cnum][0][self.gain_idx])*gain
            
            # Signal from target [e-]
            target_signal_e = 0 if self.target == 0 else (self.target - self.bgl)*gain
        
            sat_cap = C.SAT_CAP[self.cont.cnum][0][self.gain_idx] # Saturation capacity [e-]
                
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
                dark_signal_e = (self.dark_input - C.BLACK_LEVEL[self.cont.cnum][0][self.gain_idx])*gain
                sky_signal_e = (self.bgl - self.dark_input)*gain # Signal from skyglow [e-]
            else:
                dark_signal_e = 0 # Set to 0 if dark frame level is not provided
                sky_signal_e = (self.bgl - C.BLACK_LEVEL[self.cont.cnum][0][self.gain_idx])*gain
                
            # Signal from target [e-]
            target_signal_e = 0 if self.target == 0 else (self.target - self.bgl)*gain
                
            sat_cap = C.SAT_CAP[self.cont.cnum][0][self.gain_idx] # Saturation capacity [e-]
                
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
        
            sf = self.cont.convSig(self.sf, True)
            self.varSFInfo.set('%.4g' % sf)
            self.setLumColour(sf, self.labelSF2)
            
            if self.target != 0:
                tf = self.cont.convSig(self.tf, True)
                self.varTFInfo.set('%.4g' % tf)
                self.setLumColour(tf, self.labelTF2)
                self.checkbuttonLim.configure(state='normal')
            else:
                self.varTFInfo.set('-')
                self.labelTF2.configure(background=C.DEFAULT_BG, foreground='black')
                self.checkbuttonLim.configure(state='disabled')
                self.varTransfLim.set(0)
        else:
            self.varSFInfo.set('%.3g' % (self.sf))
            self.checkbuttonLim.configure(state=('normal' if self.target != 0 else 'disabled'))
            self.varTFInfo.set('-' if self.target == 0 else '%.3g' % (self.tf))
            self.labelTF2.configure(background=C.DEFAULT_BG, foreground='black')
        
        self.dataCalculated = True
        
        self.varMessageLabel.set(message)
        self.labelMessage.configure(foreground='navy')
 
    def activateTooltips(self):
    
        '''Add tooltips to all relevant widgets.'''
        
        apc.createToolTip(self.entryExp, C.TTExp, self.cont.tt_fs)
        apc.createToolTip(self.checkbuttonToggleDark, C.TTUseDark, self.cont.tt_fs)
        apc.createToolTip(self.entryDark, C.TTDarkNoise if self.cont.isDSLR else C.TTDarkLevel, self.cont.tt_fs)
        apc.createToolTip(self.entryBGN, C.TTBGNoise, self.cont.tt_fs)
        apc.createToolTip(self.entryBGL, C.TTBGLevel, self.cont.tt_fs)
        apc.createToolTip(self.entryTarget, C.TTTarget, self.cont.tt_fs)
        apc.createToolTip(self.labelSNR2, C.TTSNR, self.cont.tt_fs)
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
        apc.createToolTip(self.labelDF2, C.TTDF, self.cont.tt_fs)
        apc.createToolTip(self.labelSF2, C.TTSFLum if self.cont.hasQE else C.TTSFElectron, self.cont.tt_fs)
        apc.createToolTip(self.labelTF2, C.TTTFLum if self.cont.hasQE else C.TTTFElectron, self.cont.tt_fs)
        apc.createToolTip(self.checkbuttonLim, C.TTLim, self.cont.tt_fs)
 
    def deactivateTooltips(self):
    
        '''Remove tooltips from all widgets.'''
    
        for widget in [self.entryExp, self.checkbuttonToggleDark, self.entryDark, self.entryBGN,
                       self.entryBGL, self.entryTarget, self.labelSNR2, self.labelDR2,
                       self.labelFL2, self.labelEFL2, self.labelAP2, self.labelFR2, self.labelIS2, 
                       self.labelRL2, self.labelGainI2, self.labelSatCap2, self.labelBL2, self.labelWL2, 
                       self.labelPS2, self.labelQE2, self.labelRNI2, self.labelDN2, self.labelSN2,
                       self.labelTBGN2, self.labelDF2, self.labelSF2, self.labelTF2,
                       self.checkbuttonLim]:
                           
            widget.unbind('<Enter>')
            widget.unbind('<Motion>')
            widget.unbind('<Leave>')
              
    def setLumColour(self, sf, label):
    
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
    
