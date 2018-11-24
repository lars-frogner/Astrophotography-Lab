# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
import sys
import os
import atexit
import time
import subprocess
import threading
import datetime
import shutil
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import aplab_common as apc
from aplab_common import C

class ImageSolver(ttk.Frame):

    def __init__(self, parent, controller):

        '''Initialize Image Solver frame.'''

        ttk.Frame.__init__(self, parent)

        self.cont = controller
        small_font = self.cont.small_font
        medium_font = self.cont.medium_font
        large_font = self.cont.large_font

        atexit.register(self.stopThread)

        self.supportedformats = [('All compatible files', ('*.jpg', '*.jpeg', '*.JPG', '*.JPEG', '*.png', '*.PNG', '*.tif', '*.tiff', '*.TIF', '*.TIFF')),
                                 ('JPEG files', ('*.jpg', '*.jpeg', '*.JPG', '*.JPEG')),
                                 ('PNG files', ('*.png', '*.PNG')),
                                 ('TIFF files', ('*.tif', '*.tiff', '*.TIF', '*.TIFF'))]

        self.previousPath = os.path.expanduser('~/Pictures') # Default file path

        self.showtypes = ['Original', 'Annotated', 'Objects', 'Index']

        self.noInput = True
        self.currentImage = None

        self.solver_thread = threading.Timer(0, self.solve)

        self.varShowType = tk.StringVar()
        self.varScaleFac = tk.DoubleVar()
        self.varUseSysScale = tk.IntVar()

        self.varMessageLabel = tk.StringVar()

        self.varShowType.set(self.showtypes[0])
        self.varScaleFac.set('')

        # Define frames

        frameHeader = ttk.Frame(self)
        frameContent = ttk.Frame(self)
        frameLeft = ttk.Frame(frameContent)
        self.frameRight = ttk.Frame(frameContent)
        frameMessage = ttk.Frame(self)

        # Place frames

        frameHeader.pack(side='top', fill='x')

        frameContent.pack(side='top', fill='both', expand=True)

        frameLeft.pack(side='left', padx=(30*C.scsx, 0), fill='y')
        self.frameRight.pack(side='right', fill='both', expand=True)

        frameMessage.pack(side='bottom', fill='x')

        # *** Header frame ***

        labelHeader = ttk.Label(frameHeader, text='Image Solver', font=self.cont.large_font,
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


        frameControll = ttk.Frame(frameLeft)

        self.buttonAdd = ttk.Button(frameControll, text='Add image', width=10, command=self.addImage)
        self.buttonSolve = ttk.Button(frameControll, text='Solve', width=10, command=lambda: self.solver_thread.start())
        self.buttonAbort = ttk.Button(frameControll, text='Abort', width=10, command=lambda: self.abort_solving())

        self.buttonSolve.configure(state='disabled')

        self.progressSolve = ttk.Progressbar(frameControll, mode='indeterminate', length='{:d}p'.format(6*self.cont.small_fs))


        frameControll.pack(side='top', pady=(10*C.scsy, 10*C.scsy))

        self.buttonAdd.pack(side='top', expand=True)
        self.buttonSolve.pack(side='top', expand=True)


        frameInput = ttk.Frame(frameLeft)

        labelInput = ttk.Label(frameInput, text='Solving options', font=medium_font, anchor='center')

        self.labelToggleScale = ttk.Label(frameInput, text='Use system image scale:')
        self.checkbuttonToggleScale = tk.Checkbutton(frameInput, highlightbackground=C.DEFAULT_BG, background=C.DEFAULT_BG, activebackground=C.DEFAULT_BG,
                                                    variable=self.varUseSysScale, command=self.toggleSysScaleMode)
        labelToggleScale2 = ttk.Label(frameInput, text='', width=9)

        self.labelScaleFac = ttk.Label(frameInput, text='Image scale factor:')
        self.entryScaleFac = ttk.Entry(frameInput, textvariable=self.varScaleFac, width=5, font=small_font,
                                  background=C.DEFAULT_BG)
        labelScaleFac2 = ttk.Label(frameInput, text='x')
        frameInput.pack(side='top', pady=(10*C.scsy, 10*C.scsy))

        labelInput.grid(row=0, column=0, columnspan=2, pady=(0, 10*C.scsy))

        self.labelToggleScale.grid(row=1, column=0, sticky='W')
        self.checkbuttonToggleScale.grid(row=1, column=1)
        labelToggleScale2.grid(row=1, column=2, sticky='W')

        self.labelScaleFac.grid(row=2, column=0, sticky='W')
        self.entryScaleFac.grid(row=2, column=1)
        labelScaleFac2.grid(row=2, column=2, sticky='W')

        self.disableInputWidgets()



        frameShow = ttk.Frame(frameLeft)

        labelShow = ttk.Label(frameShow, text='Show:')

        self.optionShow = ttk.OptionMenu(frameShow, self.varShowType, None, *self.showtypes,
                                         command=self.updateShowType)

        self.optionShow.configure(state='disabled')


        frameShow.pack(side='bottom', pady=(10*C.scsy, 0))

        labelShow.grid(row=0, column=0, sticky='W')
        self.optionShow.grid(row=0, column=1)

        # *** Right frame ***

        self.labelCanv = ttk.Label(self.frameRight, text='<Added images will be displayed here>',
                                   anchor='center')

        self.canvasView = tk.Canvas(self.frameRight, width=0, height=0, bg='black')

        self.labelCanv.pack(expand=True)

        # *** Message frame ***

        self.labelMessage = ttk.Label(frameMessage, textvariable=self.varMessageLabel)

        ttk.Separator(frameMessage, orient='horizontal').pack(side='top', fill='x')
        self.labelMessage.pack(anchor='w', padx=(5*C.scsx, 0))

    def addImage(self):

        self.disableWidgets()

        # Show file selection menu and store selected file

        fullimagepath = tkinter.filedialog.askopenfilename(filetypes=self.supportedformats,
                                                           initialdir=self.previousPath)

        # Do nothing if no files were selected
        if len(fullimagepath) == 0:
            self.enableWidgets()
            return None

        imagename = fullimagepath.split('/')[-1]

        splitted = fullimagepath.split('/')
        self.imagename = splitted[-1]
        self.imagename_base = '.'.join(self.imagename.split('.')[:-1])
        self.imagepath = os.sep.join(splitted[:-1])

        self.varMessageLabel.set('Adding image {}..'.format(imagename))
        self.labelMessage.configure(foreground='navy')
        self.labelMessage.update_idletasks()

        self.previousPath = '/'.join(fullimagepath.split('/')[:-1])

        if self.noInput:
            self.showCanvas()
            self.noInput = False
        else:
            self.canvasView.delete(self.currentImage)

        self.check_solved()

        if self.is_solved:

            self.buttonSolve.configure(state='disabled')
            self.optionShow.configure(state='normal')
            self.varShowType.set(self.showtypes[1])
            self.updateShowType(self.showtypes[1])

        else:

            old_dir_path = os.path.join('aplab_astrometry', 'astrometry', 'solved_images', self.imagename)

            if os.path.isdir(old_dir_path):
                shutil.rmtree(old_dir_path)

            self.buttonSolve.configure(state='normal')
            self.optionShow.configure(state='disabled')
            self.varShowType.set(self.showtypes[0])

            self.executeAdd(fullimagepath)

        self.varMessageLabel.set('Image {} added.'.format(imagename))
        self.labelMessage.configure(foreground='navy')

        self.enableWidgets()
        self.enableInputWidgets()

    def executeAdd(self, fullimagepath):

        im = Image.open(fullimagepath)
        im_pix_w, im_pix_h = im.size

        f = np.min([float(self.frameRight.winfo_width() - 50*C.scsx)/im_pix_w,
                    float(self.frameRight.winfo_height() - 30*C.scsy)/im_pix_h])

        canv_w = int(f*im_pix_w)
        canv_h = int(f*im_pix_h)

        self.im_res = ImageTk.PhotoImage(im.resize((canv_w, canv_h), Image.ANTIALIAS))

        im = None

        self.canvasView.configure(width=canv_w, height=canv_h)

        self.currentImage = self.canvasView.create_image(0.5*canv_w, 0.5*canv_h, image=self.im_res,
                                                         anchor='center')

    def check_solved(self):

        solved_path = os.path.join('aplab_astrometry', 'astrometry', 'solved_images', self.imagename, self.imagename_base + '.solved')

        if os.path.exists(solved_path):

            f = open(solved_path, 'rb')
            self.is_solved = int.from_bytes(f.read(), byteorder='little')
            f.close()

        else:
            self.is_solved = False

    def solve(self):

        self.disableWidgets()

        self.progressSolve.pack(side='top', pady=(0, 0), expand=True)
        self.progressSolve.start()

        self.check_solved()

        args = []

        if self.varUseSysScale.get():

            try:
                res_fac = self.varScaleFac.get()
            except tk.TclError:
                res_fac = 1.0

            args.append('--scale-units arcsecperpix')
            args.append('--scale-low {:.2f}'.format(0.75*self.cont.ISVal/res_fac))
            args.append('--scale-high {:.2f}'.format(1.25*self.cont.ISVal/res_fac))

        else:
            args.append('--guess-scale')

        command = [os.path.join('aplab_astrometry', 'solve-field-wrapper.bat'),
                   self.imagepath,
                   self.imagename]
        if len(args) > 0:
            command.append(' '.join(args))

        self.labelMessage.configure(foreground='navy')

        self.buttonSolve.pack_forget()
        self.buttonAbort.pack(side='top', expand=True)

        for output in self.execute(command):
            print(output.encode(sys.stdout.encoding, errors='replace'), end='')
            self.varMessageLabel.set(output.strip())
            self.labelMessage.update_idletasks()

        self.end_solving()

    def end_solving(self):

        self.buttonAbort.pack_forget()
        self.buttonSolve.pack(side='top', expand=True)

        self.check_solved()

        if self.is_solved:

            self.buttonSolve.configure(state='disabled')
            self.optionShow.configure(state='normal')
            self.varShowType.set(self.showtypes[1])
            self.updateShowType(self.showtypes[1])

            self.varMessageLabel.set('Image successfully solved')
            self.labelMessage.configure(foreground='forestgreen')
            self.labelMessage.update_idletasks()

        else:

            shutil.rmtree(os.path.join('aplab_astrometry', 'astrometry', 'solved_images', self.imagename))

            self.buttonSolve.configure(state='normal')
            self.optionShow.configure(state='disabled')
            self.varShowType.set(self.showtypes[0])

            self.varMessageLabel.set('Couldn\'t solve image')
            self.labelMessage.configure(foreground='crimson')
            self.labelMessage.update_idletasks()

        self.progressSolve.stop()
        self.progressSolve.pack_forget()

        self.enableWidgets()

    def abort_solving(self):

        self.stopThread()
        self.end_solving()

    def execute(self, command):

        process = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True)

        print(subprocess.list2cmdline(process.args))

        for stdout_line in iter(process.stdout.readline, ""):
            yield stdout_line

        process.stdout.close()
        return_code = process.wait()

        if return_code:
            raise subprocess.CalledProcessError(return_code, command)

    def showCanvas(self):

        '''Show canvas widget.'''

        self.labelCanv.pack_forget()
        self.canvasView.pack(side='top', expand=True)

    def disableWidgets(self):

        '''Disable widgets that can be interacted with.'''

        self.buttonAdd.configure(state='disabled')
        self.buttonSolve.configure(state='disabled')
        self.disableInputWidgets()

    def enableWidgets(self):

        '''Enable widgets that can be interacted with.'''

        self.buttonAdd.configure(state='normal')

        if self.is_solved:
            self.optionShow.configure(state='normal')
        else:
            self.buttonSolve.configure(state='normal')

        self.enableInputWidgets()

    def updateShowType(self, showtype):

        if showtype == 'Original':
            fullimagepath = os.path.join('aplab_astrometry', 'astrometry', 'solved_images', self.imagename, self.imagename)
        elif showtype == 'Annotated':
            fullimagepath = os.path.join('aplab_astrometry', 'astrometry', 'solved_images', self.imagename, self.imagename_base + '-ngc.png')
        elif showtype == 'Objects':
            fullimagepath = os.path.join('aplab_astrometry', 'astrometry', 'solved_images', self.imagename, self.imagename_base + '-objs.png')
        elif showtype == 'Index':
            fullimagepath = os.path.join('aplab_astrometry', 'astrometry', 'solved_images', self.imagename, self.imagename_base + '-indx.png')

        self.executeAdd(fullimagepath)

    def readWCS(self):

        wcspath = os.path.join('aplab_astrometry', 'astrometry', 'solved_images', self.imagename, self.imagename_base + '.wcs')

        f = open(wcspath, 'r')
        line = f.read()
        f.close()

        self.wcs_entries = {}

        i = 0

        while True:

            try:
                first_word = line[80*i:80*(i+1)].split()[0]

            except IndexError:
                break

            if first_word not in ['COMMENT', 'HISTORY', 'END']:

                entry = ('/'.join(line[80*i:80*(i+1)].split('/')[:-1])).split('=')
                self.wcs_entries[entry[0].strip()] = entry[1].strip()

            i += 1

    def toggleSysScaleMode(self):

        if self.varUseSysScale.get() == 1:
            self.entryScaleFac.configure(state='normal')
        else:
            self.entryScaleFac.configure(state='disabled')

    def disableInputWidgets(self):

        self.checkbuttonToggleScale.configure(state='disabled')
        self.entryScaleFac.configure(state='disabled')

    def enableInputWidgets(self):

        self.checkbuttonToggleScale.configure(state='normal')
        self.toggleSysScaleMode()

    def stopThread(self):

        self.solver_thread.cancel()
