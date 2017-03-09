# -*- coding: utf-8 -*-

import Tkinter as tk
import ttk
import tkFont
import sys
import datetime
import traceback
import textwrap
import re
import subprocess
import numpy as np
import matplotlib

class C:

    is_win = sys.platform == 'win32'

    gfont = 'Tahoma' if is_win else 'FreeSans'

    matplotlib.use("TkAgg") # Use TkAgg backend
    matplotlib.rc('font', family=gfont) # Set plot font

    # Define tooltip strings

    tw = 40

    TTExp = textwrap.fill('The exposure time of the subframe.', tw)
    TTUseDark = textwrap.fill('[Deactivate if you don\'t have a dark frame with the same exposure time and temperature as the light frame. This will restrict the noise and flux values that can be calculated, but SNR and DR will not be affected.]', tw)
    TTDarkNoise = textwrap.fill('The standard deviation of pixel values in a dark frame with the same exposure time and temperature as the relevant subframe.', tw) + '\n\n' + textwrap.fill('[This value must be from an uncalibrated frame.]', tw)
    TTDarkLevel = textwrap.fill('The average or median pixel value in a dark frame with the same exposure time and temperature as the relevant subframe.', tw) + '\n\n' + textwrap.fill('[This value must be from an uncalibrated frame.]', tw)
    TTBGNoise = textwrap.fill('The standard deviation of pixel values in a background region of the subframe.', tw) + '\n\n' + textwrap.fill('[This value must be from one colour of the Bayer array of an uncalibrated frame.]', tw)
    TTBGLevel = textwrap.fill('The average or median pixel value in a background region of the subframe.', tw) + '\n\n' + textwrap.fill('[This value must be from an uncalibrated frame.]', tw)
    TTTarget = textwrap.fill('The average or median pixel value in a target region of the subframe, where the SNR is to be calculated.', tw) + '\n\n' + textwrap.fill('[This value must be from an uncalibrated frame.]', tw)
    TTDF = textwrap.fill('The number of photoelectrons per second produced in each pixel by the dark current.', tw)
    TTSFLum = textwrap.fill('The estimated apparent magnitude of a 1x1 arcsecond piece of the sky.', tw) + '\n\n' + textwrap.fill('[The magnitude unit used here does not correspond exactly to a visual magnitude unit, since the passband of the camera generally will be different from the visual (V) passband. The camera sensitivity is assumed to peak at 555 nm.]', tw)
    TTSFElectron = textwrap.fill('The number of photoelectrons per second produced in each pixel as a result of photons from the skyglow.', tw) + '\n\n' + textwrap.fill('[This is a measure of the sky brightness. Different electron fluxes are not directly comparable between different camera models, but are comparable for the same camera model if the optical train is the same.]', tw)
    TTTFLum = textwrap.fill('The estimated apparent magnitude of a 1x1 arcsecond piece of the target.', tw) + '\n\n' + textwrap.fill('[The magnitude unit used here does not correspond exactly to a visual magnitude unit, since the passband of the camera generally will be different from the visual (V) passband. The camera sensitivity is assumed to peak at 555 nm.]', tw)
    TTTFElectron = textwrap.fill('The number of photoelectrons per second produced in each target pixel as a result of photons from the target.', tw) + '\n\n' + textwrap.fill('[This is a measure of the brightness of the target. Different electron fluxes are not directly comparable between different camera models, but are comparable for the same camera model if the optical train is the same.]', tw)
    TTLFLum = textwrap.fill(u'The luminance (in mag/arcsec\u00B2) of the brightest part of the target that you don\'t want to become completely saturated during an exposure. This is used to find an upper limit to the exposure time for that particular target.', tw)
    TTLFElectron = textwrap.fill(u'The electron flux of the brightest part of the target that you don\'t want to become completely saturated during an exposure. This is used to find an upper limit to the exposure time for that particular target.', tw)
    TTDSFPhoton = textwrap.fill('The number of photons per second that would have to reach each pixel to produce the observed electron flux from both skyglow and dark current.', tw) + '\n\n' + textwrap.fill('[Different photon fluxes are comparable between different camera models, provided that the same optical train is used and that the fluxes relate to the same colour(s) of light.]', tw)
    TTDSFElectron = textwrap.fill('The number of photoelectrons per second produced in each pixel either as a result of photons from the skyglow, or from dark current.', tw) + '\n\n' + textwrap.fill('[Different electron fluxes are not directly comparable between different camera models, but are comparable for the same camera model if the optical train is the same.]', tw)
    TTSubs = textwrap.fill('[Set higher than 1 to get the SNR and simulated image of a stacked frame rather than of a single subframe.]', tw)
    TTSNR = textwrap.fill('The signal to noise ratio of the target in the subframe.', tw)
    TTStackSNR = textwrap.fill('The signal to noise ratio of the target in the stacked image.', tw) + '\n\n' + textwrap.fill('[The subframes are assumed to be averaged together.]', tw)
    TTDR = textwrap.fill('The dynamic range of the image indicates the size of the intensity range between the noise floor and the saturation capacity.', tw) + '\n\n' + textwrap.fill('[The intensity range doubles for every stop, or about every third dB.]', tw)
    TTFL = textwrap.fill('The distance travelled by parallel rays after refraction/reflection in the primary lens/mirror before they converge in a focal point.', tw)
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
    TTQE = textwrap.fill('The maximum probability that a photon reaching the sensor will result in the production of a photo-electron.', tw)
    TTRN = textwrap.fill('The uncertainty in the number of photoelectrons in a pixel caused by reading the sensor.', tw) + '\n\n' + textwrap.fill('[This includes the quantization error introduced by rounding to a whole number of ADUs.]', tw)
    TTDN = textwrap.fill('The uncertainty in the number of photoelectrons in a pixel produced by the randomness of the dark current.', tw)
    TTSN = textwrap.fill('The uncertainty in the number of photoelectrons in a pixel produced by the randomness of the skyglow photons.', tw)
    TTDSN = textwrap.fill('The uncertainty in the number of photoelectrons in a pixel caused by both skyglow and dark current.', tw)
    TTTotN = textwrap.fill('The total uncertainty in the number of photoelectrons in each background pixel.', tw) + '\n\n' + textwrap.fill('[This includes read noise, dark noise and skyglow noise.]', tw)
    TTStretch = textwrap.fill('[Activate to perform a histogram stretch to increase the contrast of the simulated image.]', tw)
    TTTotal = textwrap.fill('The total exposure time for all the subframes combined.', tw)
    TTMax = textwrap.fill('The maximum allowed exposure time for a subframe.', tw) + '\n\n' + textwrap.fill('[This will be limited by factors like tracking/guiding accuracy, unwanted saturation and risk of something ruining the exposure.]', tw)
    TTSet = textwrap.fill('These settings are expected to nearly maximise SNR, while keeping the exposure time as short as possible and avoiding unwanted saturation.', tw) + '\n\n' + textwrap.fill('But due to the uncertainties in the underlying data, they shouldn\'t be trusted blindly, but rather be considered as guidelines.', tw)
    TTLim = textwrap.fill('If checked, the calculated target signal will be copied to the limit signal input box of the respective tool when you click one of the transfer buttons. (For CCDs, transferring to the Plotting Tool will be unaffected.)', tw)

    TT_STATE = ''

    if is_win:

        import win32api

        sw = win32api.GetSystemMetrics(0) # Screen width in pixels
        sh = win32api.GetSystemMetrics(1) # Screen height in pixels

    else:

        screendims = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4', shell=True, stdout=subprocess.PIPE).communicate()[0]

        sw = int(screendims.split('x')[0]) # Screen width in pixels
        sh = int(screendims.split('x')[1].split('\n')[0]) # Screen height in pixels

    scsy = scsx = sh/768.0  # Scaling after screen height

    # Default background colour
    DEFAULT_BG = '#%02x%02x%02x' % ((240, 240, 237) if is_win else (217, 217, 217))

    # Window sizes

    l_x = 1050 # Largest width
    l_y = 620  # Largest height

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
    AN_WINDOW_SIZE = (l_x, 600)
    FOV_WINDOW_SIZE = (l_x, l_y)

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
    RES_X = []
    RES_Y = []
    ISO = []

    # Lists for telescope data
    TNAME = []
    FOCAL_LENGTH = []
    APERTURE = []

     
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
        self.topTip.wm_geometry('+%d+%d' % (self.widget.winfo_pointerx() + 15*C.scsx,
                                            self.widget.winfo_pointery() + 15*C.scsy))
        
        # Define tooltip label
        label = tk.Label(self.topTip, text=tiptext, justify='left', background='white',
                         relief='solid', borderwidth=1, font=(C.gfont, self.fs))
        
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
            
        errfont = tkFont.Font(root=self, family=C.gfont, size=9)
        
        ttk.Label(self, text=error_message, font=errfont).pack(pady=12*C.scsy, expand=True)
        ttk.Button(self, text='OK', command=lambda: self.destroy()).pack(pady=(0, 12*C.scsy),
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
            toolTip.topTip.wm_geometry('+%d+%d' % (event.widget.winfo_pointerx() + 15*C.scsx,
                                                   event.widget.winfo_pointery() + 15*C.scsy))
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
    
    width *= C.scsx
    height *= C.scsy
        
    x = (C.sw - width)/2
    y = (C.sh - height)/2
        
    window.geometry('%dx%d+%d-%d' % (width, height, x, y))
    window.update_idletasks()

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
        img = stretch(img, m)
    
    else:
        img = 65535*np.ones(img.shape, dtype='uint16')
    
    return img
    
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
     
def smoothstep(edge0, edge1, x):

    # Scale, bias and saturate x to 0..1 range
    x = max(0.0, min((float(x) - edge0)/(edge1 - edge0), 1.0))

    # Evaluate polynomial
    return x*x*(3 - 2*x)