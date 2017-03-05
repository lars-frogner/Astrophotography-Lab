# -*- coding: utf-8 -*-

import Tkinter as tk
import ttk
import os
import time
import datetime
import numpy as np
import matplotlib
import FileDialog # Needed for matplotlib
from PIL import Image, ImageTk
import sidereal
import ephem
import aplab_common as apc
from aplab_common import C

matplotlib.use("TkAgg") # Use TkAgg backend
matplotlib.rc('font', family='Tahoma') # Set plot font

class FOVCalculator(ttk.Frame):

    def __init__(self, parent, controller):
        
        '''Initialize FOV Calculator frame.'''
    
        ttk.Frame.__init__(self, parent)
        
        self.cont = controller
        small_font = self.cont.small_font
        medium_font = self.cont.medium_font
        large_font = self.cont.large_font
        
        self.topCanvas = tk.Toplevel()
        self.topCanvas.destroy()
        
        self.utcOffset = datetime.datetime.now() - datetime.datetime.utcnow()
        
        self.varDate = tk.StringVar()
        self.varTime = tk.StringVar()
        self.varLat = tk.StringVar()
        self.varLon = tk.StringVar()
        
        self.cont.protocol('WM_DELETE_WINDOW', self.saveCoords)
        
        file = open('coordinates.txt', 'r')
        coords = file.read().split(',')
        file.close()
            
        self.varLat.set(coords[0])
        self.varLon.set(coords[1])
        
        self.validLat = coords[0] != ''
        self.validLon = coords[1] != ''
        
        file = open('objectdata.txt', 'r')
        lines = file.read().split('\n')
        file.close()
        
        self.obj_idx = 0
        
        self.validDate = True
        self.validTime = True
        
        self.obDes = []
        self.obName = []
        self.imWidth = []
        self.obRA = []
        self.obDec = []
        self.obMag = []
        self.obType = []
        self.imCred = []
        
        for line in lines[1:]:
        
            line = line.split(',')
            
            self.obDes.append(line[0])
            self.obName.append(line[0] + line[1])
            self.imWidth.append(float(line[2]))
            self.obRA.append([float(line[3]), float(line[4])])
            self.obDec.append([float(line[5]), float(line[6])])
            self.obMag.append(line[7])
            self.obType.append(line[8])
            self.imCred.append(','.join(line[9:]))
        
        all = range(len(self.obDes))
        
        l_messier = all[:-11]
        l_ic = []
        l_ngc = []
        l_solar = all[-11:]
        
        grouplist = ['All', 'Messier', 'IC', 'NGC', 'Solar system']
        self.groups = {'All' : all, 'Messier' : l_messier, 'IC' : l_ic, 'NGC' : l_ngc, 'Solar system' : l_solar}
        self.varCurrGroup = tk.StringVar()
        self.varCurrGroup.set('All')
        
        l_cl = [i for i in all if 'Cluster' in self.obType[i]]
        l_globcl = [i for i in all if self.obType[i] == 'Globular Cluster']
        l_opcl = [i for i in all if self.obType[i] == 'Open Cluster']
        l_nb = [i for i in all if ('Nebula' in self.obType[i] or self.obType[i] == 'Supernova Remnant')]
        l_stnb = [i for i in all if self.obType[i] == 'Starforming Nebula']
        l_plnb = [i for i in all if self.obType[i] == 'Planetary Nebula']
        l_srnb = [i for i in all if self.obType[i] == 'Supernova Remnant']
        l_gl = [i for i in all if 'Galaxy' in self.obType[i]]
        l_spgl = [i for i in all if self.obType[i] == 'Spiral Galaxy']
        l_elgl = [i for i in all if self.obType[i] == 'Elliptical Galaxy']
        l_legl = [i for i in all if self.obType[i] == 'Lenticular Galaxy']
        l_otds = [i for i in all if (self.obType[i] in ['Binary Star', 'Milky Way Patch', 'Asterism'])]
        l_pl = [i for i in all if (self.obType[i] in ['Terrestrial Planet', 'Gas Giant'])]
        l_tp = [i for i in all if self.obType[i] == 'Terrestrial Planet']
        l_gg = [i for i in all if self.obType[i] == 'Gas Giant']
        l_dp = [i for i in all if self.obType[i] == 'Dwarf Planet']
        l_otss = [i for i in all if (self.obType[i] in ['Star', 'Moon'])]
        
        typelist = ['All', 'Star Cluster', ' -Globular Cluster', ' -Open Cluster', 'Nebula', 
                    ' -Starforming Nebula', ' -Planetary Nebula', ' -Supernova Remnant',
                    'Galaxy', ' -Spiral Galaxy', ' -Elliptical Galaxy', ' -Lenticular Galaxy', 
                    'Planet', ' -Terrestrial Planet', ' -Gas Giant', 'Dwarf Planet', 'Other (Deep Sky)',
                    'Other (Solar System)']
        self.types = {'All' : all, 'Star Cluster' : l_cl, ' -Globular Cluster' : l_globcl, 
                      ' -Open Cluster' : l_opcl, 'Nebula' : l_nb, ' -Starforming Nebula' : l_stnb, 
                      ' -Planetary Nebula' : l_plnb, ' -Supernova Remnant' : l_srnb,
                      'Galaxy' : l_gl, ' -Spiral Galaxy' : l_spgl, ' -Elliptical Galaxy' : l_elgl, 
                      ' -Lenticular Galaxy' : l_legl, 'Other (Deep Sky)' : l_otds, 'Planet' : l_pl,
                      ' -Terrestrial Planet' : l_tp, ' -Gas Giant' : l_gg, 'Dwarf Planet' : l_dp,
                      'Other (Solar System)' : l_otss}
        self.varCurrType = tk.StringVar()
        self.varCurrType.set('All')
        
        altlist = ['All', 'Above horizon', u'Above 20\u00B0', u'Above 40\u00B0', u'Above 60\u00B0']
        self.alts = {'All' : False, 'Above horizon' : 0, u'Above 20\u00B0' : 20, 
                     u'Above 40\u00B0' : 40, u'Above 60\u00B0' : 60}
        self.varCurrAlt = tk.StringVar()
        self.varCurrAlt.set('All')
        
        self.varName = tk.StringVar()
        self.varType = tk.StringVar()
        self.varMag = tk.StringVar()
        self.varRADec = tk.StringVar()
        self.varAzAlt = tk.StringVar()
        self.varPhase = tk.StringVar()
        
        self.varVis = tk.IntVar()
        self.varVis.set(0)
        
        self.currentImage = None
        
        self.varST = tk.StringVar()
        self.varResults = tk.StringVar()
        self.varFOV = tk.StringVar()
        self.varCredit = tk.StringVar()
        
        self.sinfo = 'Search for object'
        self.varST.set(self.sinfo)
        self.varResults.set('%d objects listed' % len(all))
        
        self.varMessageLabel = tk.StringVar()
        
        # Define frames
        
        frameHeader = ttk.Frame(self)
        frameContent = ttk.Frame(self)
        frameLeft = ttk.Frame(frameContent)
        self.frameRight = ttk.Frame(frameContent)
        frameMessage = ttk.Frame(self)
        
        # Place frames
        
        frameHeader.pack(side='top', fill='x')
        
        frameContent.pack(side='top', fill='both', expand=True)
        
        frameLeft.pack(side='left', padx=(30*C.scsx, 0))
        self.frameRight.pack(side='right', fill='both', expand=True)
        
        frameMessage.pack(side='bottom', fill='x')
        
        # *** Header frame ***
        
        labelHeader = ttk.Label(frameHeader, text='FOV Calculator', font=self.cont.large_font,
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
        
        frameInput = ttk.Frame(frameLeft)
        
        labelTime = ttk.Label(frameInput, text='Time: ')
        self.entryTime = ttk.Entry(frameInput, textvariable=self.varTime, width=5,
                                   foreground='forestgreen', validate='key',
                                   validatecommand=(self.register(self.valTime), '%P', '%S'))
        buttonCurrent = ttk.Button(frameInput, text='Now', command=self.setCurrentDT, width=4)
        labelDate = ttk.Label(frameInput, text='Date: ')
        self.entryDate = ttk.Entry(frameInput, textvariable=self.varDate, width=10, 
                                   foreground='forestgreen', validate='key',
                                   validatecommand=(self.register(self.valDate), '%P', '%S'))
             
        labelLat1 = ttk.Label(frameInput, text='Latitude: ')
        self.entryLat = ttk.Entry(frameInput, textvariable=self.varLat, width=10, 
                                  foreground='forestgreen', validate='key',
                                  validatecommand=(self.register(self.valLat), '%P'))
        labelLat2 = ttk.Label(frameInput, text=u'\u00B0')
        
        labelLon1 = ttk.Label(frameInput, text='Longitude: ')
        self.entryLon = ttk.Entry(frameInput, textvariable=self.varLon, width=10, 
                                  foreground='forestgreen', validate='key',
                                  validatecommand=(self.register(self.valLon), '%P'))
        labelLon2 = ttk.Label(frameInput, text=u'\u00B0')
        
        self.setCurrentDT(set=False)
        
        frameInput.pack(side='top', pady=(5*C.scsy, 20*C.scsy))
        
        labelTime.grid(row=0, column=0, sticky='W')
        self.entryTime.grid(row=0, column=1, padx=(6, 0), sticky='W')
        buttonCurrent.grid(row=0, column=2, padx=(3, 0), sticky='W')
        labelDate.grid(row=1, column=0, sticky='W')
        self.entryDate.grid(row=1, column=1, columnspan=2, sticky='W')
        
        labelLat1.grid(row=2, column=0, sticky='W')
        self.entryLat.grid(row=2, column=1, columnspan=2, pady=(3, 0), sticky='W')
        #labelLat2.grid(row=2, column=2, sticky='W')
        
        labelLon1.grid(row=3, column=0, sticky='W')
        self.entryLon.grid(row=3, column=1, columnspan=2, pady=(3, 0), sticky='W')
        #labelLon2.grid(row=3, column=2, sticky='W')
        
        frameSearch = ttk.Frame(frameLeft)
        frameSearch.pack(side='top', fill='x', pady=(0, 5*C.scsy))
        
        self.entrySearch = ttk.Entry(frameSearch, textvariable=self.varST, foreground='gray',
                                     font=('Tahoma', self.cont.small_fs, 'italic'), validate='key',
                                     validatecommand=(self.register(self.search), '%P'), width=16)
        self.entrySearch.pack(side='left')
        
        labelResults = ttk.Label(frameSearch, textvariable=self.varResults, 
                                 font=('Tahoma', self.cont.tt_fs), foreground='dim gray')
        labelResults.pack(side='right', expand=True)
        
        self.entrySearch.bind('<ButtonPress-1>', self.prepSearch)
        self.entrySearch.bind('<FocusOut>', self.endSearch)
        
        frameObjects = ttk.Frame(frameLeft)
        frameObjects.pack(side='top', expand=True)
        
        scrollbarObjects = ttk.Scrollbar(frameObjects)
        self.listboxObjects = tk.Listbox(frameObjects, height=8, width=35, font=small_font,
                                         selectmode='browse', yscrollcommand=scrollbarObjects.set)
        
        scrollbarObjects.pack(side='right', fill='y')
        self.listboxObjects.pack(side='right', fill='both')
        
        for idx in all:
            self.listboxObjects.insert('end', self.obName[idx])
            
        scrollbarObjects.config(command=self.listboxObjects.yview) # Add scrollbar to listbox
        
        self.listboxObjects.bind('<ButtonRelease-1>', self.selectObjectController)
        
        self.listboxObjects.activate(self.obj_idx)
        self.listboxObjects.selection_set(self.obj_idx)
        
        frameOpts = ttk.Frame(frameLeft)
        frameOpts.pack(side='top', fill='x', pady=(5*C.scsy, 0))
       
        labelGroup = ttk.Label(frameOpts, text='Group:')
        optionGroup = ttk.OptionMenu(frameOpts, self.varCurrGroup, None, *grouplist, 
                                     command=self.changeFilter)
        
        labelType = ttk.Label(frameOpts, text='Type:')
        optionType = ttk.OptionMenu(frameOpts, self.varCurrType, None, *typelist, 
                                    command=self.changeFilter)
        
        labelAlt = ttk.Label(frameOpts, text='Altitude:')
        self.optionAlt = ttk.OptionMenu(frameOpts, self.varCurrAlt, None, *altlist, 
                                        command=self.changeFilter)
        
        labelGroup.grid(row=0, column=0, sticky='W')
        optionGroup.grid(row=0, column=1, sticky='EW')
        
        labelType.grid(row=1, column=0, sticky='W')
        optionType.grid(row=1, column=1, sticky='EW')
        
        labelAlt.grid(row=2, column=0, sticky='W')
        self.optionAlt.grid(row=2, column=1, sticky='EW')
        
        frameInfo = ttk.Frame(frameLeft, borderwidth=2, relief='groove')
        
        labelName1 = ttk.Label(frameInfo, text='Name: ', width=10)
        labelName2 = ttk.Label(frameInfo, textvariable=self.varName, width=26, anchor='center')
        
        labelType1 = ttk.Label(frameInfo, text='Type: ')
        labelType2 = ttk.Label(frameInfo, textvariable=self.varType)
        
        labelMag1 = ttk.Label(frameInfo, text='App. mag.: ')
        labelMag2 = ttk.Label(frameInfo, textvariable=self.varMag)
        
        labelRADec1 = ttk.Label(frameInfo, text='RA | Dec: ')
        labelRADec2 = ttk.Label(frameInfo, textvariable=self.varRADec)
        
        labelAzAlt1 = ttk.Label(frameInfo, text='Az | Alt: ')
        labelAzAlt2 = ttk.Label(frameInfo, textvariable=self.varAzAlt)
        
        self.labelPhase1 = ttk.Label(frameInfo, text='Phase: ')
        self.labelPhase2 = ttk.Label(frameInfo, textvariable=self.varPhase)
        
        frameInfo.pack(side='top', pady=(10*C.scsy, 5*C.scsy), fill='x')
        
        labelName1.grid(row=0, column=0, sticky='W')
        labelName2.grid(row=0, column=1)
        
        labelType1.grid(row=1, column=0, sticky='W')
        labelType2.grid(row=1, column=1)
        
        labelMag1.grid(row=2, column=0, sticky='W')
        labelMag2.grid(row=2, column=1)
        
        labelRADec1.grid(row=3, column=0, sticky='W')
        labelRADec2.grid(row=3, column=1)
        
        labelAzAlt1.grid(row=4, column=0, sticky='W')
        labelAzAlt2.grid(row=4, column=1)
        
        self.buttonPlot = ttk.Button(frameLeft, text='Plot altitude', command=self.plotAlt)
        self.buttonPlot.pack(side='top', pady=(10*C.scsy, 10*C.scsy), expand=True)
        
        # *** Right frame ***
        
        self.canvasView = tk.Canvas(self.frameRight, width=0, height=0, bg='black')
        self.canvasView.pack(side='top', expand=True)
        
        self.labelCredit = ttk.Label(self.frameRight, textvariable=self.varCredit, anchor='center',
                                foreground='darkgray')
        self.labelCredit.pack(side='bottom', fill='x')
        
        self.labelFOV = ttk.Label(self.frameRight, textvariable=self.varFOV, anchor='center')
        self.labelFOV.pack(side='bottom', fill='x')
        
        # *** Message frame ***
        
        self.labelMessage = ttk.Label(frameMessage, textvariable=self.varMessageLabel)
        
        ttk.Separator(frameMessage, orient='horizontal').pack(side='top', fill='x')
        self.labelMessage.pack(anchor='w', padx=(5*C.scsx, 0))
    
    def allValid(self):
        return self.validDate and self.validTime and self.validLat and self.validLon
    
    def saveCoords(self):
        
        file = open('coordinates.txt', 'w')
        file.write('%s,%s' % (self.varLat.get() if self.validLat else '', self.varLon.get() if self.validLon else ''))
        file.close()
        self.cont.destroy()
    
    def changeFilter(self, var):
    
        self.search(self.varST.get() if self.varST.get() != self.sinfo else '', upd=True)
    
    def selectObjectController(self, event):
    
        if self.listboxObjects.size() > 0: self.selectObject(self.obName.index(self.listboxObjects.get(self.listboxObjects.curselection())))
    
    def getSSAttr(self, idx):
    
        if self.obName[idx] == 'Sun':
            body = ephem.Sun()
            phase = False
        elif self.obName[idx] == 'Mercury':
            body = ephem.Mercury()
            phase = True
        elif self.obName[idx] == 'Venus':
            body = ephem.Venus()
            phase = True
        elif self.obName[idx] == 'Moon':
            body = ephem.Moon()
            phase = True
        if self.obName[idx] == 'Mars':
            body = ephem.Mars()
            phase = False
        if self.obName[idx] == 'Ceres':
            body = ephem.readdb('Ceres,e,10.58392,80.49834,73.93568,2.7656737,0,0.0780542,' \
                                + '292.3363,1/22/1999,2000.0,3.34,0.12')
            phase = False
        if self.obName[idx] == 'Jupiter':
            body = ephem.Jupiter()
            phase = False
        if self.obName[idx] == 'Saturn':
            body = ephem.Saturn()
            phase = False
        if self.obName[idx] == 'Uranus':
            body = ephem.Uranus()
            phase = False
        if self.obName[idx] == 'Neptune':
            body = ephem.Neptune()
            phase = False
        if self.obName[idx] == 'Pluto':
            body = ephem.Pluto()
            phase = False
                
        if self.validDate and self.validTime:
            
            date = self.varDate.get().split('-')
            time = self.varTime.get().split(':')
                
            ut = datetime.datetime(int(date[0]), int(date[1]), int(date[2]),
                                   hour=int(time[0]), minute=int(time[1])) - self.utcOffset
                                       
            body.compute('%d/%d/%d %d:%d' % (ut.year, ut.month, ut.day, ut.hour, ut.minute))
                                       
        else:
                
            body.compute()
                
        ra = body.a_ra.__str__().split(':')
        dec = body.a_dec.__str__().split(':')
        ra_h = int(ra[0])
        dec_d = int(dec[0])
        ra_m = round(float(ra[1]) + float(ra[2])/60.0)
        dec_am = round(float(dec[1]) + float(dec[2])/60.0)
        
        if phase: phase = body.phase
        
        return [ra_h, ra_m, dec_d, dec_am, body.size, body.mag, phase]
    
    def selectObject(self, idx):
    
        self.canvasView.delete(self.currentImage)
    
        f = np.min([float(self.frameRight.winfo_width() - 50*C.scsx)/C.RES_X[self.cont.cnum][0],
                    float(self.frameRight.winfo_height() \
                    - self.labelFOV.winfo_height() \
                    - self.labelCredit.winfo_height() - 30*C.scsy)/C.RES_Y[self.cont.cnum][0]])
        
        canv_w = int(f*C.RES_X[self.cont.cnum][0])
        canv_h = int(f*C.RES_Y[self.cont.cnum][0])
        
        self.canvasView.configure(width=canv_w, height=canv_h)
        
        self.obj_idx = idx
        
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'Objects\\%s.jpg' % self.obDes[self.obj_idx])
        
        self.varCredit.set(self.imCred[self.obj_idx])
        
        self.varName.set(self.obName[self.obj_idx])
        self.varType.set(self.obType[self.obj_idx])
        
        if not self.obj_idx in self.groups['Solar system']:
            self.varMag.set(self.obMag[self.obj_idx])
            self.varRADec.set(u'%dh %02dm | %d\u00B0 %02d\'' % (self.obRA[self.obj_idx][0], 
                                                                round(self.obRA[self.obj_idx][1]), 
                                                                self.obDec[self.obj_idx][0], 
                                                                round(self.obDec[self.obj_idx][1])))
            im_ang_w = self.imWidth[self.obj_idx]
        
        else:
        
            ra_h, ra_m, dec_d, dec_am, size, mag, phase = self.getSSAttr(self.obj_idx)
                
            self.varMag.set('%.1f' % mag)
            
            self.varRADec.set(u'%dh %02dm | %d\u00B0 %02d\'' % (ra_h, ra_m, dec_d, dec_am))
                
            im_ang_w = size*2.05 if self.obName[self.obj_idx] == 'Saturn' else size
            
            if phase:
                self.labelPhase1.grid(row=5, column=0, sticky='W')
                self.labelPhase2.grid(row=5, column=1)
                self.varPhase.set('%.1f%%' % phase)
            else:
                self.labelPhase1.grid_forget()
                self.labelPhase2.grid_forget()
        
        im = Image.open(path)
        im_pix_w, im_pix_h = im.size
        
        self.canvasView.configure(bg='#%02x%02x%02x' \
                           % tuple(np.median(list(im.getdata())[:30*im_pix_w], axis=0).astype(int)))
        
        view_ang_w = C.RES_X[self.cont.cnum][0]*self.cont.ISVal
        
        im_new_pix_w = im_ang_w*canv_w/view_ang_w
        im_new_pix_h = im_new_pix_w*float(im_pix_h)/im_pix_w
        
        self.im_res = ImageTk.PhotoImage(im.resize((int(round(im_new_pix_w)),
                                                    int(round(im_new_pix_h))), Image.ANTIALIAS))
                                                    
        self.currentImage = self.canvasView.create_image(0.5*canv_w, 0.5*canv_h, image=self.im_res,
                                                         anchor='center')
                                                         
        self.canvasView.tag_bind(self.currentImage, '<ButtonPress-1>', self.startDragEvent)
        self.canvasView.tag_bind(self.currentImage, '<B1-Motion>', self.dragEvent)
        
        self.setAzAlt()
        
        if self.topCanvas.winfo_exists(): self.plotAlt()
    
    def setFOV(self):
    
        deg_x = self.cont.ISVal*C.RES_X[self.cont.cnum][0]/3600.0
        deg_y = self.cont.ISVal*C.RES_Y[self.cont.cnum][0]/3600.0
        
        if self.cont.dmsAngleUnit.get():
        
            deg_xi = int(deg_x)
            deg_yi = int(deg_y)
                    
            min_x = (deg_x - deg_xi)*60
            min_y = (deg_y - deg_yi)*60
            min_xi = int(min_x)
            min_yi = int(min_y)
                    
            sec_x = (min_x - min_xi)*60
            sec_y = (min_y - min_yi)*60
                   
            self.varFOV.set(u'Field of view: %d\u00B0 %d\' %.1f\'\' x %d\u00B0 %d\' %.1f\'\'' \
                            % (deg_xi, min_xi, sec_x, deg_yi, min_yi, sec_y))
                            
        else:
        
            self.varFOV.set(u'Field of view: %.3g\u00B0 x %.3g\u00B0' % (deg_x, deg_y))
    
    def prepSearch(self, event):
    
        if event.widget.get() == self.sinfo:
            self.varST.set('')
            self.entrySearch.configure(foreground='black', font=('Tahoma', self.cont.small_fs))
            
    def endSearch(self, event):
    
        if event.widget.get() == '':
            self.varST.set(self.sinfo)
            self.entrySearch.configure(foreground='gray', font=('Tahoma', self.cont.small_fs, 'italic'))
        
    def search(self, newstr, upd=False):
    
        self.listboxObjects.delete(0, 'end')
            
        group = self.groups[self.varCurrGroup.get()]
        type = self.types[self.varCurrType.get()]
        
        alt_str = self.varCurrAlt.get()
        alt = self.alts[alt_str]
        
        s = 0
        
        for idx in self.groups['All']:
            if idx in group and idx in type:
                obj = self.obName[idx]
                if newstr.lower() in obj.lower() \
                   and (alt_str == 'All' or self.getAzAlt(idx)[2] >= alt):
                    s += 1
                    self.listboxObjects.insert('end', obj)
        
        self.varResults.set('%d object%s listed' % (s, ('s' if s != 1 else '')))
        
        if s > 0:
            name = self.obName[self.obj_idx]
            activelist = self.listboxObjects.get(0, 'end')
            if name in activelist:
                i = activelist.index(name)
                self.listboxObjects.activate(i)
                self.listboxObjects.selection_set(i)
                self.listboxObjects.see(i)
            elif upd:
                self.selectObject(self.obName.index(activelist[0]))
                self.listboxObjects.selection_set(0)
        
        return True
    
    def adjustAlt(self, ok):
    
        if ok and self.allValid():
            self.changeFilter(None)
            self.optionAlt.configure(state='normal')
            self.buttonPlot.configure(state='normal')
        elif ok:
            self.varCurrAlt.set('All')
            self.changeFilter(None)
            self.optionAlt.configure(state='disabled')
            self.buttonPlot.configure(state='disabled')
    
    def valDate(self, newstr, diff):
    
        valid = True
        
        try:
            int(diff)
            ok = True
            
            parts = newstr.split('-')
            yr = parts[0]
            mnd = parts[1]
            day = parts[2]
            
            if len(yr) > 4 or len(mnd) > 2 or len(day) > 2:
                ok = False
            elif len(mnd) == 2 and len(day) == 2 \
                 and ((int(mnd) in [1, 3, 5, 7, 8, 10, 12] and int(day) > 31) \
                 or (int(mnd) > 12 or int(mnd) < 1) \
                 or int(day) < 1 \
                 or (int(mnd) in [4, 6, 9, 11] and int(day) > 30) \
                 or (int(mnd) == 2 and int(yr) % 4 == 0 and int(day) > 29) \
                 or (int(mnd) == 2 and (int(yr) % 4 != 0 or (int(yr) % 4 == 0 \
                 and int(yr) % 100 == 0 and int(yr) % 400 != 0)) and int(day) > 28)):
                 valid = False
                 
        except:
            ok = False
            
        if len(newstr) == 10 and ok:
            self.entryDate.configure(foreground=('forestgreen' if valid else 'crimson'))
        elif ok:
            self.entryDate.configure(foreground='black')
        
        self.validDate = valid and len(newstr) == 10
        
        self.adjustAlt(ok)
        
        return ok
    
    def valTime(self, newstr, diff):
    
        valid = True
    
        try:
            int(diff)
            ok = True
            
            parts = newstr.split(':')
            hr = parts[0]
            min = parts[1]
            
            if len(hr) > 2 or len(min) > 2:
                ok = False
            elif len(hr) == 2 and len(min) == 2 and (int(hr) > 23 or int(min) > 59):
                 valid = False
                 
        except:
            ok = False
            
        if len(newstr) == 5 and ok:
            self.entryTime.configure(foreground=('forestgreen' if valid else 'crimson'))
        elif ok:
            self.entryTime.configure(foreground='black')
        
        self.validTime = valid and len(newstr) == 5
        
        self.adjustAlt(ok)
        
        return ok
    
    def valLat(self, newstr):
    
        valid = True
    
        try:
            if len(newstr) > 0:
                
                if newstr[0] == '.' or newstr[0] == '-.':
                    raise ValueError
                if newstr == '-':
                    valid = False
                elif float(newstr) > 90 or float(newstr) < -90:
                    valid = False
            
            ok = True
            
        except:
            ok = False
            
        if len(newstr) > 0 and ok:
            self.entryLat.configure(foreground=('forestgreen' if valid else 'crimson'))
            
        self.validLat = valid and len(newstr) > 0
        
        self.adjustAlt(ok)
        
        return ok
        
    def valLon(self, newstr):
    
        valid = True
    
        try:
            if len(newstr) > 0:
                
                if newstr[0] == '.' or newstr[0] == '-.':
                    raise ValueError
                if newstr == '-':
                    valid = False
                elif float(newstr) > 180 or float(newstr) < -180:
                    valid = False
            
            ok = True
            
        except:
            ok = False
            
        if len(newstr) > 0 and ok:
            self.entryLon.configure(foreground=('forestgreen' if valid else 'crimson'))
            
        self.validLon = valid and len(newstr) > 0
        
        self.adjustAlt(ok)
        
        return ok
    
    def setCurrentDT(self, set=True):
    
        tm = time.localtime()
        self.varDate.set('%d-%02d-%02d' % (tm[0], tm[1], tm[2]))
        self.varTime.set('%02d:%02d' % (tm[3], tm[4]))
        
        self.entryDate.configure(foreground='forestgreen')
        self.entryTime.configure(foreground='forestgreen')
        
        self.validDate = True
        self.validTime = True
        
        if set:
            self.adjustAlt(True)
            self.setAzAlt()
    
    def getAzAlt(self, idx):
        
        if not idx in self.groups['Solar system']:
            ra_rad = (self.obRA[idx][0] + self.obRA[idx][1]/60.0)*np.pi/12
            dec_rad = (self.obDec[idx][0] + self.obDec[idx][1]/60.0)*np.pi/180
        else:
            attrs = self.getSSAttr(idx)
            ra_rad = (attrs[0] + attrs[1]/60.0)*np.pi/12
            dec_rad = (attrs[2] + attrs[3]/60.0)*np.pi/180
        
        RD = sidereal.RADec(ra_rad, dec_rad)
        
        date = self.varDate.get().split('-')
        time = self.varTime.get().split(':')
        
        ut = datetime.datetime(int(date[0]), int(date[1]), int(date[2]),
                               hour=int(time[0]), minute=int(time[1])) - self.utcOffset
        
        eLong = float(self.varLon.get())
        if eLong < 0: eLong = 360 + eLong
        
        H = RD.hourAngle(ut, eLong*np.pi/180)
        
        nLat = float(self.varLat.get())
        
        altaz = RD.altAz(H, nLat*np.pi/180)
        
        az = altaz.az*180/np.pi
        az_h = int(az)
        
        alt = altaz.alt*180/np.pi
        alt_deg = int(alt)
        
        return [az_h, (az - az_h)*60, alt_deg, (alt - alt_deg)*60]
    
    def computeAlt(self, idx):
    
        if not idx in self.groups['Solar system']:
            ra_rad = (self.obRA[idx][0] + self.obRA[idx][1]/60.0)*np.pi/12
            dec_rad = (self.obDec[idx][0] + self.obDec[idx][1]/60.0)*np.pi/180
        else:
            attrs = self.getSSAttr(idx)
            ra_rad = (attrs[0] + attrs[1]/60.0)*np.pi/12
            dec_rad = (attrs[2] + attrs[3]/60.0)*np.pi/180
        
        ob_RD = sidereal.RADec(ra_rad, dec_rad)
        
        useSun = True
        
        if useSun:
            sun_attrs = self.getSSAttr(self.obName.index('Sun'))
            sun_ra_rad = (sun_attrs[0] + sun_attrs[1]/60.0)*np.pi/12
            sun_dec_rad = (sun_attrs[2] + sun_attrs[3]/60.0)*np.pi/180
            
            sun_RD = sidereal.RADec(sun_ra_rad, sun_dec_rad)
         
        useMoon = self.varUseMoon.get()
        
        if useMoon:
            moon_attrs = self.getSSAttr(self.obName.index('Moon'))
            moon_ra_rad = (moon_attrs[0] + moon_attrs[1]/60.0)*np.pi/12
            moon_dec_rad = (moon_attrs[2] + moon_attrs[3]/60.0)*np.pi/180
            
            moon_RD = sidereal.RADec(moon_ra_rad, moon_dec_rad)
        
        date = self.varDate.get().split('-')
        time = self.varTime.get().split(':')
        
        current_lt = datetime.datetime(int(date[0]), int(date[1]), int(date[2]),
                                       hour=int(time[0]), minute=int(time[1]))
        
        start_ut = current_lt - self.utcOffset - datetime.timedelta(hours=12)
                                     
        
        eLong = float(self.varLon.get())
        if eLong < 0: eLong = 360 + eLong
        eLong *= np.pi/180
        nLat = float(self.varLat.get())*np.pi/180
        
        N = 289
        dt = datetime.timedelta(minutes=5)
        
        ut_times = [start_ut + dt*i for i in xrange(N)]
        
        times = []
        ob_alts = np.zeros(N, dtype='float')
        sun_alts = False if not useSun else np.zeros(N, dtype='float')
        moon_alts = False if not useMoon else np.zeros(N, dtype='float')
        
        if useMoon and useSun:
        
            for i in range(N):
            
                ob_H = ob_RD.hourAngle(ut_times[i], eLong)
                ob_altaz = ob_RD.altAz(ob_H, nLat)
                ob_alts[i] = ob_altaz.alt*180/np.pi
                
                sun_H = sun_RD.hourAngle(ut_times[i], eLong)
                sun_altaz = sun_RD.altAz(sun_H, nLat)
                sun_alts[i] = sun_altaz.alt*180/np.pi
                
                moon_H = moon_RD.hourAngle(ut_times[i], eLong)
                moon_altaz = moon_RD.altAz(moon_H, nLat)
                moon_alts[i] = moon_altaz.alt*180/np.pi
                
                times.append(ut_times[i] + self.utcOffset)
                
        elif useSun:
        
            for i in range(N):
            
                ob_H = ob_RD.hourAngle(ut_times[i], eLong)
                ob_altaz = ob_RD.altAz(ob_H, nLat)
                ob_alts[i] = ob_altaz.alt*180/np.pi
                
                sun_H = sun_RD.hourAngle(ut_times[i], eLong)
                sun_altaz = sun_RD.altAz(sun_H, nLat)
                sun_alts[i] = sun_altaz.alt*180/np.pi
                
                times.append(ut_times[i] + self.utcOffset)
                
        elif useMoon:
        
            for i in range(N):
            
                ob_H = ob_RD.hourAngle(ut_times[i], eLong)
                ob_altaz = ob_RD.altAz(ob_H, nLat)
                ob_alts[i] = ob_altaz.alt*180/np.pi
                
                moon_H = moon_RD.hourAngle(ut_times[i], eLong)
                moon_altaz = moon_RD.altAz(moon_H, nLat)
                moon_alts[i] = moon_altaz.alt*180/np.pi
                
                times.append(ut_times[i] + self.utcOffset)
                
        else:
        
            for i in range(N):
            
                ob_H = ob_RD.hourAngle(ut_times[i], eLong)
                ob_altaz = ob_RD.altAz(ob_H, nLat)
                ob_alts[i] = ob_altaz.alt*180/np.pi
                
                times.append(ut_times[i] + self.utcOffset)
        
        ha0 = ob_RD.hourAngle(start_ut, eLong)*12/np.pi
        
        ha0_next_whole = np.ceil(ha0)
        ha_offset = ha0_next_whole - ha0
        
        return [current_lt, times, ha0_next_whole, ha_offset, ob_alts, sun_alts, moon_alts]
            
    def plotAlt(self):
    
        if not self.allValid():
            try:
                self.topCanvas.destroy()
            except:
                pass
            self.varMessageLabel.set('Valid place and time input is required to calculate altitude.')
            return None
    
        if not self.topCanvas.winfo_exists():
    
            self.topCanvas = tk.Toplevel(bg=C.DEFAULT_BG)
            self.topCanvas.title('Altitude plot')
            self.cont.addIcon(self.topCanvas)
            apc.setupWindow(self.topCanvas, 900, 550)
            self.topCanvas.wm_attributes('-topmost', 1)
            self.topCanvas.focus_force()
            
            self.varUseMoon = tk.IntVar()
            self.varUseSun = tk.IntVar()
            self.varUseMoon.set(0)
            self.varUseSun.set(0)
        
            f = matplotlib.figure.Figure(figsize=(8.6*C.scsx, 4.7*C.scsy), dpi=100, facecolor=C.DEFAULT_BG)
            self.ax1 = f.add_subplot(111)
            self.ax2 = self.ax1.twiny()
            self.ax1.tick_params(axis='both', which='major', labelsize=8)
            self.ax2.tick_params(axis='both', which='major', labelsize=8)
            
            box = self.ax1.get_position()
            self.ax1.set_position([box.x0, box.y0, box.width*0.77, box.height])
            self.ax2.set_position([box.x0, box.y0, box.width*0.77, box.height])
                    
            self.canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(f, self.topCanvas)
            self.canvas._tkcanvas.config(highlightthickness=0)
        
            self.canvas.get_tk_widget().pack(side='top', expand=True)
            
            frameCheck = ttk.Frame(self.topCanvas)
            frameCheck.pack(side='top', expand=True)
            
            ttk.Label(frameCheck, text='Show Moon: ').grid(row=0, column=0, sticky='W')
            self.checkbuttonMoon = tk.Checkbutton(frameCheck, variable=self.varUseMoon, command=self.plotAlt)
            self.checkbuttonMoon.grid(row=0, column=1)
            
            ttk.Label(frameCheck, text='Show day/night: ').grid(row=1, column=0, sticky='W')
            self.checkbuttonSun = tk.Checkbutton(frameCheck, variable=self.varUseSun, command=self.plotAlt)
            self.checkbuttonSun.grid(row=1, column=1)
        
        if self.obName[self.obj_idx] == 'Moon':
            self.varUseMoon.set(0)
            self.checkbuttonMoon.configure(state='disabled')
        else:
            self.checkbuttonMoon.configure(state='normal')
            
        current_lt, times, ha0_next_whole, ha_offset, alts, sun_alts, moon_alts = self.computeAlt(self.obj_idx)
        
        self.ax1.cla()
        self.ax2.cla()
        self.ax1.set_xlim([0, 24])
        self.ax2.set_xlim([0, 24])
        xvals = np.linspace(0, 24, len(alts))
        
        if self.varUseSun.get():
            civilTwt_pos = [xvals[sun_alts <= 0], 'gainsboro']
            nauticalTw_pos = [xvals[sun_alts <= -6], 'lightgray']
            astronomicalTw_pos = [xvals[sun_alts <= -12], 'silver']
            night_pos = [xvals[sun_alts <= -18], 'darkgray']
        
        current_t = current_lt.hour + current_lt.minute/60.0 + current_lt.second/3600.0
        
        t0 = times[0].hour + times[0].minute/60.0 + times[0].second/3600.0
        t0_next_whole = np.ceil(t0)
        t_offset = t0_next_whole - t0
        
        if (alts > 0).all():
            state = 'circ'
        elif (alts < 0).all():
            state = 'nv'
        else:
            state = 'rs'
            
            sort_idx = np.abs(alts).argsort()
            
            notTooClose = 3 < np.abs(sort_idx[1] - sort_idx[0]) < 286
            
            if sort_idx[0] > 0:
                if alts[sort_idx[0] - 1] > 0:
                    set_idx = sort_idx[0]
                    rise_idx = sort_idx[1] if notTooClose else sort_idx[2]
                else:
                    set_idx = sort_idx[1] if notTooClose else sort_idx[2]
                    rise_idx = sort_idx[0]
            else:
                if alts[sort_idx[0] + 1] < 0:
                    set_idx = sort_idx[0]
                    rise_idx = sort_idx[1] if notTooClose else sort_idx[2]
                else:
                    set_idx = sort_idx[1] if notTooClose else sort_idx[2]
                    rise_idx = sort_idx[0]
                
        top_idx = alts.argmax()
        
        if self.varUseMoon.get():
            self.ax1.plot(xvals, moon_alts, ':', color='gray', zorder=2)
            m, = self.ax1.plot([xvals[144]], [moon_alts[144]], 'h', color='gray', label='Moon', zorder=3)
        
        self.ax1.plot(xvals, alts, '-', color='mediumblue', zorder=2)
        p1, = self.ax1.plot([xvals[144]], [alts[144]], '8', color='mediumblue', zorder=4,
                           label=u'Altitude: %.1f\u00B0 at %02d:%02d' % (alts[144], times[144].hour, 
                                                                         times[144].minute))
               
        ymin, ymax = self.ax1.get_ylim()
        self.ax1.set_ylim([ymin, ymax])
        self.ax2.set_ylim([ymin, ymax])
        self.ax1.plot([24 - t0, 24 - t0], [ymin, ymax], '-', color='darkslategray', label='Midnight', zorder=1)
        
        leftdate = '%d-%02d-%02d' % (times[0].year, times[0].month, times[0].day)
        rightdate = '%d-%02d-%02d' % (times[-1].year, times[-1].month, times[-1].day)
        self.ax1.text(24 - t0 + 0.47, ymin + 0.80*(ymax - ymin), rightdate, ha='center', va='bottom', 
                     rotation=90, name='Tahoma', size=self.cont.tt_fs, color='darkslategray', zorder=2)
        self.ax1.text(24 - t0 - 0.3, ymin + 0.80*(ymax - ymin), leftdate, ha='center', va='bottom', 
                     rotation=90, name='Tahoma', size=self.cont.tt_fs, color='darkslategray', zorder=2)
        
        p2, = self.ax1.plot([xvals[top_idx]], [alts[top_idx]], '.', color='navy', zorder=3,
                           label=u'Culmination: %.1f\u00B0 at %02d:%02d' % (alts[top_idx], 
                                                                            times[top_idx].hour, 
                                                                            times[top_idx].minute))
        
        if ymin < 0 and ymax > 0: self.ax1.plot([xvals[0], xvals[-1]], [0, 0], '-', color='dimgray', 
                                                zorder=1)
        
        p0, = self.ax1.plot([], [], color='white', label=(self.obName[self.obj_idx]))
        if state == 'rs':
            p3, = self.ax1.plot([xvals[set_idx]], [alts[set_idx]], marker=7, color='navy', zorder=3,
                               label='Set time: %02d:%02d' % (times[set_idx].hour, times[set_idx].minute))
            p4, = self.ax1.plot([xvals[rise_idx]], [alts[rise_idx]], marker=6, color='navy', 
                               zorder=3, label='Rise time: %02d:%02d' % (times[rise_idx].hour, 
                                                                         times[rise_idx].minute))
        
            l = self.ax1.legend(handles=[p0, p1, p2, p3, p4], loc='center left', bbox_to_anchor=(1, 0.7), 
                                numpoints=1, fontsize=self.cont.tt_fs)
        else:
            p3, = self.ax1.plot([], [], color='white', 
                               label=('(Circumpolar)' if state == 'circ' else '(Never visible)'))
            l = self.ax1.legend(handles=[p0, p3, p1, p2], loc='center left', bbox_to_anchor=(1, 0.7), 
                                numpoints=1, fontsize=self.cont.tt_fs)
            l.get_texts()[1].set_color('forestgreen' if state == 'circ' else 'crimson')
            
        l.get_texts()[0].set_color('mediumblue')
        
        if self.varUseSun.get():
            for darkstate in [civilTwt_pos, nauticalTw_pos, astronomicalTw_pos, night_pos]:
                
                pos = darkstate[0]
                colour = darkstate[1]
                
                if len(pos) == 0: continue
                
                hops = np.where((pos[1:] - pos[:-1]) > 1.5*(xvals[1] - xvals[0]))[0]
                
                if len(hops) > 0:
                    idx = hops[0] + 1
                    self.ax1.fill_between(pos[:idx], ymin, ymax, color=colour)
                    self.ax1.fill_between(pos[idx:], ymin, ymax, color=colour)
                else:
                    self.ax1.fill_between(pos, ymin, ymax, color=colour)
            
            s1, = self.ax1.plot([], [], 's', color='white', label='Day')
            s2, = self.ax1.plot([], [], 's', color=civilTwt_pos[1], label='Civil twilight')
            s3, = self.ax1.plot([], [], 's', color=nauticalTw_pos[1], label='Nautical twilight')
            s4, = self.ax1.plot([], [], 's', color=astronomicalTw_pos[1], label='Astronomical twilight')
            s5, = self.ax1.plot([], [], 's', color=night_pos[1], label='Night')
        
        if self.varUseSun.get() and self.varUseMoon.get():
            handlelist = [m, s1, s2, s3, s4, s5]
            self.ax2.legend(handles=handlelist, loc='center left', bbox_to_anchor=(1, 0.3), 
                            numpoints=1, fontsize=self.cont.tt_fs)
        elif self.varUseSun.get():
            handlelist = [s1, s2, s3, s4, s5]
            self.ax2.legend(handles=handlelist, loc='center left', bbox_to_anchor=(1, 0.3), 
                            numpoints=1, fontsize=self.cont.tt_fs)
        elif self.varUseMoon.get():
            handlelist = [m]
            self.ax2.legend(handles=handlelist, loc='center left', bbox_to_anchor=(1, 0.3), 
                            numpoints=1, fontsize=self.cont.tt_fs)
        
        self.ax1.set_xticks([t_offset + i for i in range(0, 24, 2)])
        self.ax2.set_xticks([ha_offset + i for i in range(0, 24, 2)])
        
        whole_t_hours = np.array([t0_next_whole + i for i in range(0, 24, 2)])
        whole_t_hours[whole_t_hours >= 24] -= 24
        self.ax1.set_xticklabels(['%02d:00' % t for t in whole_t_hours])
        
        whole_ha_hours = np.array([ha0_next_whole + i for i in range(0, 24, 2)])
        whole_ha_hours[whole_ha_hours >= 24] -= 24
        self.ax2.set_xticklabels(['%d' % ha for ha in whole_ha_hours])
        
        self.ax1.set_xlabel('Local time', name='Tahoma', fontsize=self.cont.small_fs)
        self.ax2.set_xlabel('Hour angle of object', name='Tahoma', fontsize=self.cont.small_fs)
        self.ax1.set_ylabel('Altitude [degrees]', name='Tahoma', fontsize=self.cont.small_fs)
        #self.ax1.set_title(self.obName[self.obj_idx], name='Tahoma', weight='heavy', 
        #                  fontsize=self.cont.medium_fs)
        
        
        self.canvas.draw()
    
    def setAzAlt(self):
    
        if not self.allValid():
            self.varAzAlt.set('')
            return None
            
        az_h, az_m, alt_deg, alt_am = self.getAzAlt(self.obj_idx)
        
        self.varAzAlt.set(u'%d\u00B0 %02d\' | %d\u00B0 %02d\'' % (az_h, round(az_m), 
                                                                  alt_deg, round(np.abs(alt_am))))
   
    def startDragEvent(self, event):
    
        '''Store coordinates of clicked location.'''
    
        event.widget.origin_x = event.x
        event.widget.origin_y = event.y
        
    def dragEvent(self, event):
    
        '''
        Scroll canvas by an amount equal to the difference between the previous location
        and the new location, and reset coordinates.
        '''
    
        self.canvasView.move(self.currentImage, event.x - event.widget.origin_x,
                             event.y - event.widget.origin_y)
            
        event.widget.origin_x = event.x
        event.widget.origin_y = event.y
   