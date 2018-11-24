# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import aplab_common as apc
from aplab_common import C

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

        self.varPlotMode = tk.StringVar()
        self.varPlotMode.set('single')
        self.varTypeLabel = tk.StringVar()
        self.varTypeLabel.set('Choose plot type')
        self.varPlotType = tk.StringVar()

        self.varISO = tk.IntVar()
        self.varGain = tk.DoubleVar()
        self.varRN = tk.DoubleVar()
        self.varExp = tk.DoubleVar()
        self.varDF = tk.DoubleVar()
        self.varSF = tk.DoubleVar()
        self.varTF = tk.DoubleVar()
        self.varLF = tk.DoubleVar()
        self.varTotal = tk.DoubleVar()
        self.varMax = tk.DoubleVar()
        self.varMessageLabel = tk.StringVar()

        self.varSFLabel = tk.StringVar()
        self.varTFLabel = tk.StringVar()
        self.varLFLabel = tk.StringVar()

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

        f = matplotlib.figure.Figure(figsize=(6.5*C.scsx, 4.7*C.scsy), dpi=100, facecolor=C.DEFAULT_BG)
        self.ax = f.add_subplot(111)
        self.ax.tick_params(axis='both', which='major', labelsize=8)

        self.canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(f, frameRight)
        self.canvas._tkcanvas.config(highlightthickness=0)

        # Set default attribute values

        self.varSFLabel.set(u'mag/arcsec\u00B2' if self.cont.hasQE else 'e-/s')
        self.varTFLabel.set(u'mag/arcsec\u00B2' if self.cont.hasQE else 'e-/s')
        self.varLFLabel.set(u'mag/arcsec\u00B2' if self.cont.hasQE else 'e-/s')

        self.setDefaultValues()

        # Place frames

        frameHeader.pack(side='top', fill='x')

        frameContent.pack(side='top', fill='both', expand=True)

        frameLeft.pack(side='left', fill='both', padx=(50*C.scsx, 0), expand=True)

        frameUpLeft.pack(side='top', pady=(5*C.scsy, 0), expand=True)
        frameLowLeft.pack(side='top', pady=(0, 20*C.scsy), expand=True)
        frameButton.pack(side='bottom', pady=(0, 30*C.scsy), expand=True)

        frameRight.pack(side='right', expand=True)

        frameMessage.pack(side='bottom', fill='x')

        # *** Header frame ***

        labelHeader = ttk.Label(frameHeader, text='Plotting Tool', font=large_font, anchor='center')

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

        # Define upper left frame widgets

        labelMode = ttk.Label(frameUpLeft, text='Plotting mode:', font=self.cont.smallbold_font,
                              anchor='center')

        frameMode = ttk.Frame(frameUpLeft)

        radioSing = ttk.Radiobutton(frameMode, text='Single plots', variable=self.varPlotMode,
                                    value='single', command=self.changePlotMode)
        radioComp = ttk.Radiobutton(frameMode, text='Comparison plots', variable=self.varPlotMode,
                                    value='comparison', command=self.changePlotMode)

        labelPlotType = ttk.Label(frameUpLeft, textvariable=self.varTypeLabel, font=self.cont.smallbold_font,
                                  anchor='center', width=33)
        self.optionPlotType = ttk.OptionMenu(frameUpLeft, self.varPlotType, None, *self.plotList,
                                             command=self.toggleActiveWidgets)

        # Define lower left frame widgets

        labelInput = ttk.Label(frameLowLeft, text='Imaging parameters', font=medium_font,
                               anchor='center')

        self.labelISO = ttk.Label(frameLowLeft, text='ISO:')
        self.optionISO = ttk.OptionMenu(frameLowLeft, self.varISO, None, *C.ISO[self.cont.cnum],
                                        command=self.updateISO)

        self.labelGain = ttk.Label(frameLowLeft, text='Gain:')
        self.optionGain = ttk.OptionMenu(frameLowLeft, self.varGain, None, *C.GAIN[self.cont.cnum][0],
                                         command=self.updateGain)
        self.labelGain2 = ttk.Label(frameLowLeft, text='e-/ADU')

        self.labelRN = ttk.Label(frameLowLeft, text='Read noise:')
        self.optionRN = ttk.OptionMenu(frameLowLeft, self.varRN, None, *C.RN[self.cont.cnum][0],
                                       command=self.updateRN)
        self.labelRN2 = ttk.Label(frameLowLeft, text='e-')

        if not C.is_win:
            self.optionISO.config(width=6)
            self.optionGain.config(width=6)
            self.optionRN.config(width=6)

        self.labelExp = ttk.Label(frameLowLeft, text='Exposure time:')
        self.entryExp = ttk.Entry(frameLowLeft, textvariable=self.varExp, font=small_font,
                                  background=C.DEFAULT_BG, width=9)
        labelExp2 = ttk.Label(frameLowLeft, text='seconds')

        self.labelDF = ttk.Label(frameLowLeft, text='Dark current:')
        self.entryDF = ttk.Entry(frameLowLeft, textvariable=self.varDF, font=small_font,
                                  background=C.DEFAULT_BG, width=9)
        labelDF2 = ttk.Label(frameLowLeft, text='e-/s')

        self.labelSF = ttk.Label(frameLowLeft, text='Skyglow:')
        self.entrySF = ttk.Entry(frameLowLeft, textvariable=self.varSF, font=small_font,
                                  background=C.DEFAULT_BG, width=9)
        labelSF2 = ttk.Label(frameLowLeft, textvariable=self.varSFLabel)

        self.labelTF = ttk.Label(frameLowLeft, text='Target signal:')
        self.entryTF = ttk.Entry(frameLowLeft, textvariable=self.varTF, font=small_font,
                                  background=C.DEFAULT_BG, width=9)
        labelTF2 = ttk.Label(frameLowLeft, textvariable=self.varTFLabel)

        self.labelLF = ttk.Label(frameLowLeft, text='Max signal:')
        self.entryLF = ttk.Entry(frameLowLeft, textvariable=self.varLF, font=small_font,
                                  background=C.DEFAULT_BG, width=9)
        self.labelLF2 = ttk.Label(frameLowLeft, textvariable=self.varLFLabel)

        self.labelTotal = ttk.Label(frameLowLeft, text='Total imaging time:')
        self.entryTotal = ttk.Entry(frameLowLeft, textvariable=self.varTotal, font=small_font,
                                  background=C.DEFAULT_BG, width=9)
        labelTotal2 = ttk.Label(frameLowLeft, text='hours')

        self.labelMax = ttk.Label(frameLowLeft, text='Max exposure time:')
        self.entryMax = ttk.Entry(frameLowLeft, textvariable=self.varMax, font=small_font,
                                  background=C.DEFAULT_BG, width=9)
        self.labelMax2 = ttk.Label(frameLowLeft, text='seconds')

        # Define button frame widgets

        buttonDraw = ttk.Button(frameButton, text='Draw graph', command=self.processInput)
        buttonTransferSim = ttk.Button(frameButton, text='Transfer input to Image Simulator',
                                        command=self.cont.transferToSim, width=29)
        buttonClear = ttk.Button(frameButton, text='Clear input', command=self.cont.clearInput)

        # Place upper left frame widgets

        labelMode.pack(side='top')
        frameMode.pack(side='top')

        radioSing.grid(row=0, column=0)
        radioComp.grid(row=0, column=1)

        labelPlotType.pack(side='top', pady=(10*C.scsy, 0))
        self.optionPlotType.pack(side='top')

        # Place lower left frame widgets

        labelInput.grid(row=0, column=0, columnspan=3, pady=10*C.scsy)

        self.labelExp.grid(row=3, column=0, sticky='W')
        self.entryExp.grid(row=3, column=1)
        labelExp2.grid(row=3, column=2, sticky='W')

        self.labelDF.grid(row=4, column=0, sticky='W')
        self.entryDF.grid(row=4, column=1)
        labelDF2.grid(row=4, column=2, sticky='W')

        self.labelSF.grid(row=5, column=0, sticky='W')
        self.entrySF.grid(row=5, column=1)
        labelSF2.grid(row=5, column=2, sticky='W')

        self.labelTF.grid(row=6, column=0, sticky='W')
        self.entryTF.grid(row=6, column=1)
        labelTF2.grid(row=6, column=2, sticky='W')

        self.labelTotal.grid(row=8, column=0, sticky='W')
        self.entryTotal.grid(row=8, column=1)
        labelTotal2.grid(row=8, column=2, sticky='W')

        # Place more widgets according to camera type
        self.reconfigureNonstaticWidgets()

        # Place button frame widgets
        buttonDraw.grid(row=0, column=0)
        buttonTransferSim.grid(row=1, column=0, pady=(14*C.scsy, 11*C.scsy))
        buttonClear.grid(row=2, column=0)

        # *** Right frame (plot window) ***

        self.canvas.get_tk_widget().pack()

        # *** Message frame ***

        self.labelMessage = ttk.Label(frameMessage, textvariable=self.varMessageLabel, anchor='center')

        ttk.Separator(frameMessage, orient='horizontal').pack(side='top', fill='x')
        self.labelMessage.pack(fill='x')

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
        self.p12 = 'Saturation capacity vs. ISO'
        self.p13 = 'Read noise vs. ISO'
        self.p14 = 'Gain vs. ISO'
        self.p15 = 'Exposure time limits vs. ISO'

        self.pc1 = 'Sub exposure time'
        self.pc2 = 'Number of subframes'
        self.pc3 = 'Skyglow'
        self.pc4 = 'ISO'

        # Set list of available plot types depending on camera type
        if self.varPlotMode.get() == 'single':
            if self.cont.isDSLR:
                self.plotList = [self.p1, self.p7, self.p10, self.p2, self.p3,
                                 self.p4, self.p5, self.p9, self.p8, self.p6,
                                 self.p11, self.p12, self.p13, self.p14, self.p15]
            else:
                self.plotList = [self.p1, self.p7, self.p10, self.p2, self.p3, self.p4, self.p9,
                                 self.p8]
        else:
            if self.cont.isDSLR:
                self.plotList = [self.pc1, self.pc2, self.pc3, self.pc4]
            else:
                self.plotList = [self.pc1, self.pc2, self.pc3]

        self.varPlotType.set(self.plotList[0])

        self.varISO.set(C.ISO[self.cont.cnum][self.gain_idx])
        self.varGain.set(C.GAIN[self.cont.cnum][0][self.gain_idx])
        self.varRN.set(C.RN[self.cont.cnum][0][self.rn_idx])
        self.varExp.set('')
        self.varDF.set('')
        self.varSF.set('')
        self.varTF.set('')
        self.varLF.set('')
        self.varTotal.set('')
        self.varMax.set(600)

        # Clear plot
        self.ax.cla()
        self.canvas.draw()

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

        self.labelLF.grid_forget()
        self.entryLF.grid_forget()
        self.labelLF2.grid_forget()

        self.labelMax.grid_forget()
        self.entryMax.grid_forget()
        self.labelMax2.grid_forget()

        # Set selectable values in the optionmenus according to camera model

        self.optionPlotType.set_menu(*([None] + self.plotList))

        self.optionISO.set_menu(*([None] + list(C.ISO[self.cont.cnum])))
        self.optionGain.set_menu(*([None] + list(C.GAIN[self.cont.cnum][0])))
        self.optionRN.set_menu(*([None] + list(C.RN[self.cont.cnum][0])))

        if self.cont.isDSLR:

            # DSLRs use the ISO optionmenu and max exposure entry

            self.labelISO.grid(row=1, column=0, sticky='W')
            self.optionISO.grid(row=1, column=1)

            self.labelLF.grid(row=7, column=0, sticky='W')
            self.entryLF.grid(row=7, column=1)
            self.labelLF2.grid(row=7, column=2, sticky='W')

            self.labelMax.grid(row=9, column=0, sticky='W')
            self.entryMax.grid(row=9, column=1)
            self.labelMax2.grid(row=9, column=2, sticky='W')

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

        '''Update index of selected ISO.'''

        self.gain_idx = int(np.where(C.ISO[self.cont.cnum] == selected_iso)[0])
        self.rn_idx = self.gain_idx

    def updateGain(self, selected_gain):

        '''Update index of selected gain.'''

        self.gain_idx = int(np.where(C.GAIN[self.cont.cnum][0] == selected_gain)[0])

    def updateRN(self, selected_rn):

        '''Update index of selected read noise.'''

        self.rn_idx = int(np.where(C.RN[self.cont.cnum][0] == selected_rn)[0])

    def toggleActiveWidgets(self, type):

        '''Activate or deactivate relevant widgets when changing plot type.'''

        if type == self.p1:

            self.useExp = False
            self.useTotal = False
            self.useMax = False
            self.useDF = True
            self.useSF = True
            self.useTF = True
            self.useLF = False

            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='disabled')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            self.entryLF.configure(state='disabled')

        elif type == self.p2:

            self.useExp = False
            self.useTotal = True
            self.useMax = False
            self.useDF = True
            self.useSF = True
            self.useTF = True
            self.useLF = False

            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='disabled')
            self.entryTotal.configure(state='normal')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            self.entryLF.configure(state='disabled')

        elif type == self.p3:

            self.useExp = True
            self.useTotal = False
            self.useMax = False
            self.useDF = True
            self.useSF = True
            self.useTF = True
            self.useLF = False

            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='normal')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            self.entryLF.configure(state='disabled')

        elif type == self.p4:

            self.useExp = True
            self.useTotal = False
            self.useMax = False
            self.useDF = True
            self.useSF = True
            self.useTF = True
            self.useLF = False

            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='normal')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            self.entryLF.configure(state='disabled')

        elif type == self.p5:

            self.useExp = False
            self.useTotal = True
            self.useMax = True
            self.useDF = True
            self.useSF = True
            self.useTF = True
            self.useLF = True

            self.optionISO.configure(state='disabled')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='disabled')
            self.entryTotal.configure(state='normal')
            self.entryMax.configure(state='normal')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            self.entryLF.configure(state='normal')

        elif type == self.p6:

            self.useExp = True
            self.useTotal = False
            self.useMax = False
            self.useDF = True
            self.useSF = True
            self.useTF = True
            self.useLF = False

            self.optionISO.configure(state='disabled')
            self.optionGain.configure(state='normal')
            self.entryExp.configure(state='normal')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            self.entryLF.configure(state='disabled')

        elif type == self.p7:

            self.useExp = True
            self.useTotal = False
            self.useMax = False
            self.useDF = True
            self.useSF = True
            self.useTF = True
            self.useLF = False

            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='normal')
            self.entryExp.configure(state='normal')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            self.entryLF.configure(state='disabled')

        elif type == self.p8:

            self.useExp = True
            self.useTotal = False
            self.useMax = False
            self.useDF = True
            self.useSF = True
            self.useTF = True
            self.useLF = False

            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='normal')
            self.entryExp.configure(state='normal')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            self.entryLF.configure(state='disabled')

        elif type == self.p9:

            self.useExp = False
            self.useTotal = False
            self.useMax = False
            self.useDF = True
            self.useSF = True
            self.useTF = True
            self.useLF = False

            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='normal')
            self.entryExp.configure(state='disabled')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            self.entryLF.configure(state='disabled')

        elif type == self.p10:

            self.useExp = True
            self.useTotal = False
            self.useMax = False
            self.useDF = True
            self.useSF = True
            self.useTF = True
            self.useLF = False

            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='normal')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            self.entryLF.configure(state='disabled')

        elif type == self.p11:

            self.useExp = False
            self.useTotal = False
            self.useMax = False
            self.useDF = False
            self.useSF = False
            self.useTF = False
            self.useLF = False

            self.optionISO.configure(state='disabled')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='disabled')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='disabled')
            self.entrySF.configure(state='disabled')
            self.entryTF.configure(state='disabled')
            self.entryLF.configure(state='disabled')

        elif type == self.p12:

            self.useExp = False
            self.useTotal = False
            self.useMax = False
            self.useDF = False
            self.useSF = False
            self.useTF = False
            self.useLF = False

            self.optionISO.configure(state='disabled')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='disabled')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='disabled')
            self.entrySF.configure(state='disabled')
            self.entryTF.configure(state='disabled')
            self.entryLF.configure(state='disabled')

        elif type == self.p13:

            self.useExp = False
            self.useTotal = False
            self.useMax = False
            self.useDF = False
            self.useSF = False
            self.useTF = False
            self.useLF = False

            self.optionISO.configure(state='disabled')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='disabled')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='disabled')
            self.entrySF.configure(state='disabled')
            self.entryTF.configure(state='disabled')
            self.entryLF.configure(state='disabled')

        elif type == self.p14:

            self.useExp = False
            self.useTotal = False
            self.useMax = False
            self.useDF = False
            self.useSF = False
            self.useTF = False
            self.useLF = False

            self.optionISO.configure(state='disabled')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='disabled')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='disabled')
            self.entrySF.configure(state='disabled')
            self.entryTF.configure(state='disabled')
            self.entryLF.configure(state='disabled')

        elif type == self.p15:

            self.useExp = False
            self.useTotal = False
            self.useMax = False
            self.useDF = True
            self.useSF = True
            self.useTF = False
            self.useLF = True

            self.optionISO.configure(state='disabled')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='disabled')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='disabled')
            self.entryLF.configure(state='normal')

        elif type == self.pc1:

            self.useExp = False
            self.useTotal = True
            self.useMax = False
            self.useDF = True
            self.useSF = True
            self.useTF = True
            self.useLF = False

            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='normal')
            self.entryExp.configure(state='disabled')
            self.entryTotal.configure(state='normal')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            self.entryLF.configure(state='disabled')

        elif type == self.pc2:

            self.useExp = True
            self.useTotal = False
            self.useMax = False
            self.useDF = True
            self.useSF = True
            self.useTF = True
            self.useLF = False

            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='normal')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            self.entryLF.configure(state='disabled')

        elif type == self.pc3:

            self.useExp = True
            self.useTotal = False
            self.useMax = False
            self.useDF = True
            self.useSF = True
            self.useTF = True
            self.useLF = False

            self.optionISO.configure(state='normal')
            self.optionGain.configure(state='normal')
            self.entryExp.configure(state='normal')
            self.entryTotal.configure(state='disabled')
            self.entryMax.configure(state='disabled')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            self.entryLF.configure(state='disabled')

        elif type == self.pc4:

            self.useExp = False
            self.useTotal = True
            self.useMax = True
            self.useDF = True
            self.useSF = True
            self.useTF = True
            self.useLF = True

            self.optionISO.configure(state='disabled')
            self.optionGain.configure(state='disabled')
            self.entryExp.configure(state='disabled')
            self.entryTotal.configure(state='normal')
            self.entryMax.configure(state='normal')
            self.entryDF.configure(state='normal')
            self.entrySF.configure(state='normal')
            self.entryTF.configure(state='normal')
            self.entryLF.configure(state='normal')

    def changePlotMode(self):

        if self.varPlotMode.get() == 'single':
            if self.cont.isDSLR:
                self.plotList = [self.p1, self.p7, self.p10, self.p2, self.p3,
                                 self.p4, self.p5, self.p9, self.p8, self.p6,
                                 self.p11, self.p12, self.p13, self.p14, self.p15]
            else:
                self.plotList = [self.p1, self.p7, self.p10, self.p2, self.p3, self.p4, self.p9,
                                 self.p8]

            self.varTypeLabel.set('Choose plot type')

        else:
            if self.cont.isDSLR:
                self.plotList = [self.pc1, self.pc2, self.pc3, self.pc4]
            else:
                self.plotList = [self.pc1, self.pc2, self.pc3]

            self.varTypeLabel.set('Choose parameter')

        self.varPlotType.set(self.plotList[0])
        self.optionPlotType.set_menu(*([None] + self.plotList))
        self.toggleActiveWidgets(self.plotList[0])

    def processInput(self):

        '''Check that all inputted values are valid and run plot method.'''

        try:
            self.exposure = self.varExp.get()

        except tk.TclError:
            if self.useExp:
                self.varMessageLabel.set('Invalid input for exposure time.')
                self.labelMessage.configure(foreground='crimson')
                return None

        try:
            if self.useDF:
                self.df = self.varDF.get()

        except tk.TclError:
            self.varMessageLabel.set('Invalid input for dark current.')
            self.labelMessage.configure(foreground='crimson')
            return None

        try:
            if self.useSF:
                self.sf = (self.cont.convSig(self.varSF.get(), False) if self.cont.lumSignalType.get() \
                                                            else self.varSF.get())

        except tk.TclError:
            self.varMessageLabel.set('Invalid input for skyglow.')
            self.labelMessage.configure(foreground='crimson')
            return None

        try:
            if self.useTF:
                self.tf = (self.cont.convSig(self.varTF.get(), False) if self.cont.lumSignalType.get() \
                                                            else self.varTF.get())

        except tk.TclError:
            self.varMessageLabel.set('Invalid input for target signal.')
            self.labelMessage.configure(foreground='crimson')
            return None

        try:
            if self.useLF:
                self.lf = (self.cont.convSig(self.varLF.get(), False) if self.cont.lumSignalType.get() \
                                                            else self.varLF.get())


                if self.useTF and self.lf < self.tf:

                    self.varMessageLabel.set('Max signal cannot be lower than target signal.')
                    self.labelMessage.configure(foreground='crimson')
                    return None

        except tk.TclError:

            if self.useTF:

                self.varLF.set('{:.2g}'.format(self.tf))
                self.lf = self.tf

            else:
                self.varMessageLabel.set('Invalid input for max signal.')
                self.labelMessage.configure(foreground='crimson')
                return None

        try:
            self.total = self.varTotal.get()*3600

        except tk.TclError:
            if self.useTotal:
                self.varMessageLabel.set('Invalid input for total imaging time.')
                self.labelMessage.configure(foreground='crimson')
                return None

        try:
            self.max = self.varMax.get()

        except tk.TclError:
            if self.useMax and self.cont.isDSLR:
                self.varMessageLabel.set('Invalid input for max exposure time.')
                self.labelMessage.configure(foreground='crimson')
                return None

        self.plot()

    def plot(self):

        '''Calculate and plot data for relevant plot type.'''

        type = self.varPlotType.get()
        small_fs = self.cont.small_fs
        medium_fs = self.cont.medium_fs

        if type == self.p1:

            exposure = np.linspace(0, 900, 201)

            rn = C.RN[self.cont.cnum][0][self.rn_idx]

            snr = self.tf*exposure/np.sqrt(self.tf*exposure + self.sf*exposure \
                                           + self.df*exposure + rn**2)

            self.ax.cla()
            self.ax.plot(exposure, snr, '-', color='crimson')
            self.ax.set_title(self.p1, name=C.gfont, weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Sub exposure time [s]', name=C.gfont, fontsize=small_fs)
            self.ax.set_ylabel('Target SNR', name=C.gfont, fontsize=small_fs)
            self.canvas.draw()

        elif type == self.p2:

            exposure = np.linspace(1, 900, 200)

            subs = self.total/exposure

            rn = C.RN[self.cont.cnum][0][self.rn_idx]

            snr = self.tf*exposure/np.sqrt(self.tf*exposure + self.sf*exposure \
                                           + self.df*exposure + rn**2)
            stack_snr = snr*np.sqrt(subs)

            self.ax.cla()
            self.ax.plot(exposure, stack_snr, '-', color='forestgreen')
            self.ax.set_title(self.p2, name=C.gfont, weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Sub exposure time [s]', name=C.gfont, fontsize=small_fs)
            self.ax.set_ylabel('Stack SNR', name=C.gfont, fontsize=small_fs)
            self.canvas.draw()

        elif type == self.p3:

            subs = np.linspace(0, 200, 201)

            rn = C.RN[self.cont.cnum][0][self.rn_idx]

            snr = self.tf*self.exposure/np.sqrt(self.tf*self.exposure + self.sf*self.exposure \
                                                + self.df*self.exposure + rn**2)
            stack_snr = snr*np.sqrt(subs)

            self.ax.cla()
            self.ax.plot(subs, stack_snr, '-', color='forestgreen')
            self.ax.set_title(self.p3, name=C.gfont, weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Number of subframes', name=C.gfont, fontsize=small_fs)
            self.ax.set_ylabel('Stack SNR', name=C.gfont, fontsize=small_fs)
            self.canvas.draw()

        elif type == self.p4:

            subs = np.linspace(2, 201, 200)

            rn = C.RN[self.cont.cnum][0][self.rn_idx]

            snr = self.tf*self.exposure/np.sqrt(self.tf*self.exposure + self.sf*self.exposure \
                                                + self.df*self.exposure + rn**2)
            delta_snr = snr*(np.sqrt(subs[1:]) - np.sqrt(subs[:-1]))

            self.ax.cla()
            self.ax.plot(subs[:-1], delta_snr, '-', color='forestgreen')
            self.ax.set_title(self.p4, name=C.gfont, weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Number of subframes', name=C.gfont, fontsize=small_fs)
            self.ax.set_ylabel('Stack SNR increase with one additional frame', name=C.gfont,
                               fontsize=small_fs)
            self.canvas.draw()

        elif type == self.p5:

            iso = C.ISO[self.cont.cnum]

            if len(iso) < 2:
                self.varMessageLabel.set('At least two ISO values required.')
                self.labelMessage.configure(foreground='crimson')
                return None

            maxf = self.lf + self.sf + self.df

            sat_cap = C.SAT_CAP[self.cont.cnum][0]

            isTooLong = 0.9*sat_cap/maxf > self.max

            exposure = 0.9*sat_cap/maxf*np.invert(isTooLong) + self.max*isTooLong
            subs = self.total/exposure

            rn = C.RN[self.cont.cnum][0]

            snr = self.tf*exposure/np.sqrt(self.tf*exposure + self.sf*exposure \
                                           + self.df*exposure + rn**2)
            stack_snr = snr*np.sqrt(subs)

            xvals = np.linspace(0, 1, len(iso))
            self.ax.cla()
            self.ax.plot(xvals, stack_snr, 'o-', color='forestgreen')

            y_ofs = [-15, -30, -45]

            for i in range(len(iso)):
                self.ax.annotate('{:d} x {:d} s'.format(int(subs[i]), int(np.ceil(exposure[i]))), name=C.gfont,
                                 fontsize=self.cont.tt_fs, xy=(xvals[i], stack_snr[i]),
                                 xytext=(-20, y_ofs[i % 3]), textcoords='offset points',
                                 arrowprops=dict(arrowstyle='->', facecolor='black'))
            self.ax.text(0.5, 0.05,
                         'Exposure time limited if unwanted saturation occurs',
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes, name=C.gfont, fontsize=self.cont.tt_fs)

            self.ax.set_title(self.p5, name=C.gfont, weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('ISO', name=C.gfont, fontsize=small_fs)
            self.ax.set_xticks(xvals)
            self.ax.set_xticklabels([str(i) for i in iso])
            plt.setp(self.ax.get_xticklabels(), rotation=30, horizontalalignment='right')
            self.ax.set_ylabel('Maximum stack SNR', name=C.gfont, fontsize=small_fs)
            self.canvas.draw()

        elif type == self.p6:

            iso = C.ISO[self.cont.cnum]

            if len(iso) < 2:
                self.varMessageLabel.set('At least two ISO values required.')
                self.labelMessage.configure(foreground='crimson')
                return None

            sat_cap = C.SAT_CAP[self.cont.cnum][0]

            rn = C.RN[self.cont.cnum][0]
            tbgn = np.sqrt(rn**2 + self.df*self.exposure + self.sf*self.exposure)

            dr = np.log10(sat_cap/tbgn)/np.log10(2)

            xvals = np.linspace(0, 1, len(iso))
            self.ax.cla()
            self.ax.plot(xvals, dr, 'o-', color='navy')
            self.ax.set_title(self.p6, name=C.gfont, weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('ISO', name=C.gfont, fontsize=small_fs)
            self.ax.set_xticks(xvals)
            self.ax.set_xticklabels([str(i) for i in iso])
            plt.setp(self.ax.get_xticklabels(), rotation=30, horizontalalignment='right')
            self.ax.set_ylabel('Dynamic range [stops]', name=C.gfont, fontsize=small_fs)
            self.canvas.draw()

        elif type == self.p7:

            if self.cont.lumSignalType.get():
                f = self.cont.convSig(self.sf, True)
                if f < 20:
                    min = f - 1
                    max = 22
                elif f > 21:
                    min = 19
                    max = f + 1
                else:
                    min = 19
                    max = 22
                sf = self.cont.convSig(np.linspace(max, min, 200), False)
            else:
                sf = np.linspace(0, 2*self.sf, 201)

            rn = C.RN[self.cont.cnum][0][self.rn_idx]

            snr = self.tf*self.exposure/np.sqrt(self.tf*self.exposure + sf*self.exposure \
                                                + self.df*self.exposure + rn**2)
            current_snr = self.tf*self.exposure/np.sqrt(self.tf*self.exposure + self.sf*self.exposure \
                                                        + self.df*self.exposure + rn**2)

            self.ax.cla()
            self.ax.plot((self.cont.convSig(sf, True) if self.cont.lumSignalType.get() else sf), snr, '-',
                         color='crimson')
            p, = self.ax.plot((self.cont.convSig(self.sf, True) if self.cont.lumSignalType.get() else self.sf),
                              current_snr, 'o', color='crimson', label='Current values')
            self.ax.legend(handles=[p], loc='best', numpoints=1, fontsize=small_fs)
            self.ax.set_title(self.p7, name=C.gfont, weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Skyglow {}'.format(u'[mag/arcsec\u00B2]' \
                                               if self.cont.lumSignalType.get() else '[e-/s]'),
                               name=C.gfont, fontsize=small_fs)
            self.ax.set_ylabel('Target SNR', name=C.gfont, fontsize=small_fs)
            self.canvas.draw()

        elif type == self.p8:

            if self.cont.lumSignalType.get():
                f = self.cont.convSig(self.sf, True)
                if f < 20:
                    min = f - 1
                    max = 22
                elif f > 21:
                    min = 19
                    max = f + 1
                else:
                    min = 19
                    max = 22
                sf = self.cont.convSig(np.linspace(max, min, 200), False)
            else:
                sf = np.linspace(0, 2*self.sf, 201)

            sat_cap = C.SAT_CAP[self.cont.cnum][0][self.gain_idx]

            rn = C.RN[self.cont.cnum][0][self.rn_idx]

            tbgn = np.sqrt(rn**2 + self.df*self.exposure + sf*self.exposure)
            current_tbgn = np.sqrt(rn**2 + self.df*self.exposure + self.sf*self.exposure)

            dr = np.log10(sat_cap/tbgn)/np.log10(2)
            current_dr = np.log10(sat_cap/current_tbgn)/np.log10(2)

            self.ax.cla()
            self.ax.plot((self.cont.convSig(sf, True) if self.cont.lumSignalType.get() else sf), dr, '-',
                         color='navy')
            p, = self.ax.plot((self.cont.convSig(self.sf, True) if self.cont.lumSignalType.get() else self.sf),
                              current_dr, 'o', color='navy', label='Current values')
            self.ax.legend(handles=[p], loc='best', numpoints=1, fontsize=small_fs)
            self.ax.set_title(self.p8, name=C.gfont, weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Skyglow {}'.format(u'[mag/arcsec\u00B2]' \
                                               if self.cont.lumSignalType.get() else '[e-/s]'),
                               name=C.gfont, fontsize=small_fs)
            self.ax.set_ylabel('Dynamic range [stops]', name=C.gfont, fontsize=small_fs)
            self.canvas.draw()

        elif type == self.p9:

            exposure = np.linspace(1, 900, 200)

            sat_cap = C.SAT_CAP[self.cont.cnum][0][self.gain_idx]

            rn = C.RN[self.cont.cnum][0][self.rn_idx]

            tbgn = np.sqrt(rn**2 + self.df*exposure + self.sf*exposure)

            dr = np.log10(sat_cap/tbgn)/np.log10(2)

            self.ax.cla()
            self.ax.plot(exposure, dr, '-', color='navy')
            self.ax.set_title(self.p9, name=C.gfont, weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Sub exposure time [s]', name=C.gfont, fontsize=small_fs)
            self.ax.set_ylabel('Dynamic range [stops]', name=C.gfont, fontsize=small_fs)
            self.canvas.draw()

        elif type == self.p10:

            if self.cont.lumSignalType.get():
                f = self.cont.convSig(self.tf, True)
                if f < 20:
                    min = f - 1
                    max = 22
                elif f > 21:
                    min = 19
                    max = f + 1
                else:
                    min = 19
                    max = 22
                tf = self.cont.convSig(np.linspace(max, min, 200), False)
            else:
                tf = np.linspace(0, 2*self.sf, 201)

            rn = C.RN[self.cont.cnum][0][self.rn_idx]

            snr = tf*self.exposure/np.sqrt(tf*self.exposure + self.sf*self.exposure \
                                           + self.df*self.exposure + rn**2)
            current_snr = self.tf*self.exposure/np.sqrt(self.tf*self.exposure + self.sf*self.exposure \
                                                        + self.df*self.exposure + rn**2)

            self.ax.cla()
            self.ax.plot((self.cont.convSig(tf, True) if self.cont.lumSignalType.get() else tf), snr, '-',
                         color='crimson')
            p, = self.ax.plot((self.cont.convSig(self.tf, True) if self.cont.lumSignalType.get() else self.tf),
                              current_snr, 'o', color='crimson', label='Current values')
            self.ax.legend(handles=[p], loc='best', numpoints=1, fontsize=small_fs)
            self.ax.set_title(self.p10, name=C.gfont, weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Target signal {}'.format(u'[mag/arcsec\u00B2]' \
                                                     if self.cont.lumSignalType.get() else '[e-/s]'),
                               name=C.gfont, fontsize=small_fs)
            self.ax.set_ylabel('Target SNR', name=C.gfont, fontsize=small_fs)
            self.canvas.draw()

        elif type == self.p11:

            gain = C.GAIN[self.cont.cnum][0]
            sat_cap = C.SAT_CAP[self.cont.cnum][0]

            if len(gain) < 2:
                self.varMessageLabel.set('At least two ISO values required.')
                self.labelMessage.configure(foreground='crimson')
                return None

            self.ax.cla()
            self.ax.plot(gain, sat_cap, '-o', color='darkviolet')
            self.ax.set_title(self.p11, name=C.gfont, weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('Gain [e-/ADU]', name=C.gfont, fontsize=small_fs)
            self.ax.set_ylabel('Saturation capacity [e-]', name=C.gfont, fontsize=small_fs)
            self.ax.set_xscale('log')
            self.ax.set_yscale('log')
            self.canvas.draw()

        elif type == self.p12:

            iso = C.ISO[self.cont.cnum]

            if len(iso) < 2:
                self.varMessageLabel.set('At least two ISO values required.')
                self.labelMessage.configure(foreground='crimson')
                return None

            sat_cap = C.SAT_CAP[self.cont.cnum][0]

            xvals = np.linspace(0, 1, len(iso))
            self.ax.cla()
            self.ax.plot(xvals, sat_cap, 'o-', color='darkviolet')
            self.ax.set_title(self.p12, name=C.gfont, weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('ISO', name=C.gfont, fontsize=small_fs)
            self.ax.set_xticks(xvals)
            self.ax.set_xticklabels([str(i) for i in iso])
            plt.setp(self.ax.get_xticklabels(), rotation=30, horizontalalignment='right')
            self.ax.set_ylabel('Saturation capacity [e-]', name=C.gfont, fontsize=small_fs)
            self.canvas.draw()

        elif type == self.p13:

            iso = C.ISO[self.cont.cnum]

            if len(iso) < 2:
                self.varMessageLabel.set('At least two ISO values required.')
                self.labelMessage.configure(foreground='crimson')
                return None

            rn = C.RN[self.cont.cnum][0]

            xvals = np.linspace(0, 1, len(iso))
            self.ax.cla()
            self.ax.plot(xvals, rn, 'o-', color='greenyellow')
            self.ax.set_title(self.p13, name=C.gfont, weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('ISO', name=C.gfont, fontsize=small_fs)
            self.ax.set_xticks(xvals)
            self.ax.set_xticklabels([str(i) for i in iso])
            plt.setp(self.ax.get_xticklabels(), rotation=30, horizontalalignment='right')
            self.ax.set_ylabel('Read noise [e-]', name=C.gfont, fontsize=small_fs)
            self.canvas.draw()

        elif type == self.p14:

            iso = C.ISO[self.cont.cnum]

            if len(iso) < 2:
                self.varMessageLabel.set('At least two ISO values required.')
                self.labelMessage.configure(foreground='crimson')
                return None

            gain = C.GAIN[self.cont.cnum][0]

            xvals = np.linspace(0, 1, len(iso))
            self.ax.cla()
            self.ax.plot(xvals, gain, 'o-', color='slategray')
            self.ax.set_title(self.p14, name=C.gfont, weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('ISO', name=C.gfont, fontsize=small_fs)
            self.ax.set_xticks(xvals)
            self.ax.set_xticklabels([str(i) for i in iso])
            plt.setp(self.ax.get_xticklabels(), rotation=30, horizontalalignment='right')
            self.ax.set_ylabel('Gain [e-/ADU]', name=C.gfont, fontsize=small_fs)
            self.canvas.draw()

        elif type == self.p15:

            iso = C.ISO[self.cont.cnum]

            if len(iso) < 2:
                self.varMessageLabel.set('At least two ISO values required.')
                self.labelMessage.configure(foreground='crimson')
                return None

            maxf = self.lf + self.sf + self.df

            sat_cap = C.SAT_CAP[self.cont.cnum][0]
            rn = C.RN[self.cont.cnum][0]

            max_exp_time = sat_cap/maxf

            rn_percentage_limit = 0.4 # Amount of read noise relative to total background noise

            min_exp_time = (1.0/rn_percentage_limit**2 - 1.0)*rn**2/(self.df + self.sf)

            xvals = np.linspace(0, 1, len(iso))
            self.ax.cla()
            self.ax.plot(xvals, max_exp_time, 'o-', color='crimson', label='Upper limit')
            self.ax.plot(xvals, min_exp_time, 'o-', color='forestgreen', label='Lower limit')
            self.ax.set_title(self.p15, name=C.gfont, weight='heavy', fontsize=medium_fs)
            self.ax.set_xlabel('ISO', name=C.gfont, fontsize=small_fs)
            self.ax.set_xticks(xvals)
            self.ax.set_xticklabels([str(i) for i in iso])
            plt.setp(self.ax.get_xticklabels(), rotation=30, horizontalalignment='right')
            self.ax.set_ylabel('Exposure time [s]', name=C.gfont, fontsize=small_fs)
            self.ax.legend(loc='best')
            self.canvas.draw()

        elif type == self.pc1:

            exposure = np.linspace(1, 900, 200)
            rn = C.RN[self.cont.cnum][0][self.rn_idx]

            snr1 = self.tf*exposure/np.sqrt(self.tf*exposure + self.sf*exposure \
                                           + self.df*exposure + rn**2)
            snr1_min, snr1_max, snr1 = self.norm(snr1)

            subs2 = self.total/exposure
            snr2 = self.tf*exposure/np.sqrt(self.tf*exposure + self.sf*exposure \
                                            + self.df*exposure + rn**2)
            stack_snr2 = snr2*np.sqrt(subs2)
            stack_snr2_min, stack_snr2_max, stack_snr2 = self.norm(stack_snr2)

            sat_cap3 = C.SAT_CAP[self.cont.cnum][0][self.gain_idx]
            tbgn3 = np.sqrt(rn**2 + self.df*exposure + self.sf*exposure)
            dr3 = np.log10(sat_cap3/tbgn3)/np.log10(2)
            dr3_min, dr3_max, dr3 = self.norm(dr3)

            self.ax.cla()
            self.ax.plot(exposure, snr1, '-', color='crimson',
                         label='Target SNR: {:.1f} - {:.1f}'.format(snr1_min, snr1_max))
            self.ax.plot(exposure, stack_snr2, '-', color='forestgreen',
                         label='Stack SNR: {:.1f} - {:.1f}'.format(stack_snr2_min, stack_snr2_max))
            self.ax.plot(exposure, dr3, '-', color='navy',
                         label='Dynamic range: {:.1f} - {:.1f} stops'.format(dr3_min, dr3_max))
            self.ax.legend(loc='best', fontsize=small_fs)
            self.ax.set_title(self.pc1 + ' comparison plot', name=C.gfont, weight='heavy',
                              fontsize=medium_fs)
            self.ax.set_xlabel('Sub exposure time [s]', name=C.gfont, fontsize=small_fs)
            self.ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
            self.ax.set_yticklabels(['Min', '', '', '', '', 'Max'])
            self.ax.set_ylabel('Value', name=C.gfont, fontsize=small_fs)
            self.canvas.draw()

        elif type == self.pc2:

            subs = np.linspace(0, 200, 201)
            rn = C.RN[self.cont.cnum][0][self.rn_idx]
            snr = self.tf*self.exposure/np.sqrt(self.tf*self.exposure + self.sf*self.exposure \
                                                + self.df*self.exposure + rn**2)

            stack_snr1 = snr*np.sqrt(subs)
            stack_snr1_min, stack_snr1_max, stack_snr1 = self.norm(stack_snr1[:-1])

            delta_snr1 = snr*(np.sqrt(subs[1:]) - np.sqrt(subs[:-1]))
            delta_snr1_min, delta_snr1_max, delta_snr1 = self.norm(delta_snr1)

            self.ax.cla()
            self.ax.plot(subs[:-1], stack_snr1, '-', color='crimson',
                         label='Stack SNR: {:.1f} - {:.1f}'.format(stack_snr1_min, stack_snr1_max))
            self.ax.plot(subs[:-1], delta_snr1, '-', color='forestgreen',
                         label='Stack SNR increase: {:.1f} - {:.1f}'.format(delta_snr1_min, delta_snr1_max))
            self.ax.legend(loc='best', fontsize=small_fs)
            self.ax.set_title(self.pc2 + ' comparison plot', name=C.gfont, weight='heavy',
                              fontsize=medium_fs)
            self.ax.set_xlabel('Number of subframes', name=C.gfont, fontsize=small_fs)
            self.ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
            self.ax.set_yticklabels(['Min', '', '', '', '', 'Max'])
            self.ax.set_ylabel('Value', name=C.gfont, fontsize=small_fs)
            self.canvas.draw()

        elif type == self.pc3:

            if self.cont.lumSignalType.get():
                f = self.cont.convSig(self.sf, True)
                if f < 20:
                    min = f - 1
                    max = 22
                elif f > 21:
                    min = 19
                    max = f + 1
                else:
                    min = 19
                    max = 22
                sf = self.cont.convSig(np.linspace(max, min, 200), False)
            else:
                sf = np.linspace(0, 2*self.sf, 201)

            rn = C.RN[self.cont.cnum][0][self.rn_idx]

            snr1 = self.tf*self.exposure/np.sqrt(self.tf*self.exposure + sf*self.exposure \
                                                + self.df*self.exposure + rn**2)
            snr1_min, snr1_max, snr1 = self.norm(snr1)
            current_snr1 = self.tf*self.exposure/np.sqrt(self.tf*self.exposure + self.sf*self.exposure \
                                                        + self.df*self.exposure + rn**2)

            sat_cap1 = C.SAT_CAP[self.cont.cnum][0][self.gain_idx]
            tbgn1 = np.sqrt(rn**2 + self.df*self.exposure + sf*self.exposure)
            current_tbgn1 = np.sqrt(rn**2 + self.df*self.exposure + self.sf*self.exposure)
            dr1 = np.log10(sat_cap1/tbgn1)/np.log10(2)
            dr1_min, dr1_max, dr1 = self.norm(dr1)
            current_dr1 = np.log10(sat_cap1/current_tbgn1)/np.log10(2)

            self.ax.cla()
            self.ax.plot((self.cont.convSig(sf, True) if self.cont.lumSignalType.get() else sf), snr1, '-',
                         color='crimson', label='Target SNR: {:.1f} - {:.1f}'.format(snr1_min, snr1_max))
            self.ax.plot((self.cont.convSig(sf, True) if self.cont.lumSignalType.get() else sf), dr1, '-',
                         color='forestgreen',
                         label='Dynamic range: {:.1f} - {:.1f} stops'.format(dr1_min, dr1_max))
            self.ax.legend(loc='best', fontsize=small_fs)
            self.ax.plot((self.cont.convSig(self.sf, True) if self.cont.lumSignalType.get() else self.sf),
                         (current_snr1 - snr1_min)/(snr1_max - snr1_min), 'o', color='crimson')
            self.ax.plot((self.cont.convSig(self.sf, True) if self.cont.lumSignalType.get() else self.sf),
                         (current_dr1 - dr1_min)/(dr1_max - dr1_min), 'o', color='forestgreen')
            self.ax.set_title(self.pc3 + ' comparison plot', name=C.gfont, weight='heavy',
                              fontsize=medium_fs)
            self.ax.set_xlabel('Skyglow {}'.format(u'[mag/arcsec\u00B2]' \
                                               if self.cont.lumSignalType.get() else '[e-/s]'),
                               name=C.gfont, fontsize=small_fs)
            self.ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
            self.ax.set_yticklabels(['Min', '', '', '', '', 'Max'])
            self.ax.set_ylabel('Value', name=C.gfont, fontsize=small_fs)
            self.canvas.draw()

        elif type == self.pc4:

            iso = C.ISO[self.cont.cnum]

            if len(iso) < 2:
                self.varMessageLabel.set('At least two ISO values required.')
                self.labelMessage.configure(foreground='crimson')
                return None

            maxf = self.lf + self.sf + self.df

            sat_cap = C.SAT_CAP[self.cont.cnum][0]
            rn = C.RN[self.cont.cnum][0]
            isTooLong = 0.9*sat_cap/maxf > self.max
            exposure = 0.9*sat_cap/maxf*np.invert(isTooLong) + self.max*isTooLong

            subs1 = self.total/exposure
            snr1 = self.tf*exposure/np.sqrt(self.tf*exposure + self.sf*exposure \
                                           + self.df*exposure + rn**2)
            stack_snr1 = snr1*np.sqrt(subs1)
            stack_snr1_min, stack_snr1_max, stack_snr1 = self.norm(stack_snr1)

            tbgn2 = np.sqrt(rn**2 + self.df*exposure + self.sf*exposure)
            dr2 = np.log10(sat_cap/tbgn2)/np.log10(2)
            dr2_min, dr2_max, dr2 = self.norm(dr2)

            xvals = np.linspace(0, 1, len(iso))
            self.ax.cla()
            self.ax.plot(xvals, stack_snr1, '-o', color='crimson',
                         label='Max stack SNR: {:.1f} - {:.1f}'.format(stack_snr1_min, stack_snr1_max))
            self.ax.plot(xvals, dr2, '-o', color='forestgreen',
                         label='Dynamic range: {:.1f} - {:.1f} stops'.format(dr2_min, dr2_max))
            self.ax.legend(loc='best', fontsize=small_fs)
            self.ax.set_title(self.pc4 + ' comparison plot', name=C.gfont, weight='heavy',
                              fontsize=medium_fs)
            self.ax.set_xlabel('ISO', name=C.gfont, fontsize=small_fs)
            self.ax.set_xticks(xvals)
            self.ax.set_xticklabels([str(i) for i in iso])
            plt.setp(self.ax.get_xticklabels(), rotation=30, horizontalalignment='right')
            self.ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
            self.ax.set_yticklabels(['Min', '', '', '', '', 'Max'])
            self.ax.set_ylabel('Value', name=C.gfont, fontsize=small_fs)
            self.canvas.draw()

        self.varMessageLabel.set('Data plotted.')
        self.labelMessage.configure(foreground='navy')

    def norm(self, vals):

        min_val = np.min(vals)
        max_val = np.max(vals)

        return (min_val, max_val, (vals - min_val)/(max_val - min_val))

    def activateTooltips(self):

        '''Add tooltips to all relevant widgets.'''

        if self.cont.isDSLR:

            apc.createToolTip(self.labelISO, C.TTISO, self.cont.tt_fs)
            apc.createToolTip(self.optionISO, C.TTISO, self.cont.tt_fs)

        elif len(C.GAIN[self.cont.cnum][0]) > 1:

            apc.createToolTip(self.labelGain, C.TTGain, self.cont.tt_fs)
            apc.createToolTip(self.optionGain, C.TTGain, self.cont.tt_fs)

        apc.createToolTip(self.labelExp, C.TTExp, self.cont.tt_fs)
        apc.createToolTip(self.labelDF, C.TTDF, self.cont.tt_fs)
        apc.createToolTip(self.labelSF, C.TTSFLum if self.cont.hasQE else C.TTSFElectron, self.cont.tt_fs)
        apc.createToolTip(self.labelTF, C.TTTFLum if self.cont.hasQE else C.TTTFElectron, self.cont.tt_fs)
        apc.createToolTip(self.labelLF, C.TTLFLum if self.cont.hasQE else C.TTLFElectron, self.cont.tt_fs)
        apc.createToolTip(self.labelTotal, C.TTTotal, self.cont.tt_fs)
        apc.createToolTip(self.labelMax, C.TTMax, self.cont.tt_fs)

        apc.createToolTip(self.entryExp, C.TTExp, self.cont.tt_fs)
        apc.createToolTip(self.entryDF, C.TTDF, self.cont.tt_fs)
        apc.createToolTip(self.entrySF, C.TTSFLum if self.cont.hasQE else C.TTSFElectron, self.cont.tt_fs)
        apc.createToolTip(self.entryTF, C.TTTFLum if self.cont.hasQE else C.TTTFElectron, self.cont.tt_fs)
        apc.createToolTip(self.entryLF, C.TTLFLum if self.cont.hasQE else C.TTLFElectron, self.cont.tt_fs)
        apc.createToolTip(self.entryTotal, C.TTTotal, self.cont.tt_fs)
        apc.createToolTip(self.entryMax, C.TTMax, self.cont.tt_fs)

    def deactivateTooltips(self):

        '''Remove tooltips from all widgets.'''

        if self.cont.isDSLR:

            self.labelISO.unbind('<Enter>')
            self.labelISO.unbind('<Motion>')
            self.labelISO.unbind('<Leave>')
            self.optionISO.unbind('<Enter>')
            self.optionISO.unbind('<Motion>')
            self.optionISO.unbind('<Leave>')

        elif len(C.GAIN[self.cont.cnum][0]) > 1:

            self.labelGain.unbind('<Enter>')
            self.labelGain.unbind('<Motion>')
            self.labelGain.unbind('<Leave>')
            self.optionGain.unbind('<Enter>')
            self.optionGain.unbind('<Motion>')
            self.optionGain.unbind('<Leave>')

        for widget in [self.labelExp, self.labelDF, self.labelSF, self.labelTF, self.labelLF,
                       self.labelTotal, self.labelMax,
                       self.entryExp, self.entryDF, self.entrySF, self.entryTF, self.entryLF,
                       self.entryTotal, self.entryMax]:

            widget.unbind('<Enter>')
            widget.unbind('<Motion>')
            widget.unbind('<Leave>')

