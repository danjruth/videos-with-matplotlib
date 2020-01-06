# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 12:20:39 2020

@author: ldeike
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as manimation
import copy

class Spin:
    
    def __init__(self,fig,ax,period=3,azim_init=0,elev=30):
        self.fig = fig
        self.ax = ax
        self.period = period
        self.azim_init = azim_init
        self.elev = elev
    
    def write_video(self,fpath_video,fps=30,metadata_dict=None):
        
        dt = 1./fps
        self.times = np.arange(0,self.period-dt,dt)
        
        if metadata_dict is None:
            metadata_dict = {}
        
        # create the writer for the video file
        FFMpegWriter = copy.deepcopy(manimation.writers['ffmpeg'])
        writer = copy.deepcopy(FFMpegWriter(fps=fps, metadata=metadata_dict))
        with writer.saving(self.fig, fpath_video, 100):
            for ti,time in enumerate(self.times):
                print('Writing frame '+str(ti)+'/'+str(len(self.times))+'...')
                self.ax.set_elev(self.elev)
                writer.grab_frame()