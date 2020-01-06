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
    '''
    Class to animate a 3d plot spinning around the z axis.
    
    Parameters
    ----------
    fig : matplotlib Figure.
        The matplotlib figure on which the axes exist.
        
    ax : matplotlib Axes, or list of Axes.
        The 3d axes to animate. Can be either just a single axes or a list of 
        axes.
    
    period : float, or list of floats.
        The period (in seconds) of each axes's rotation.
        
    azim_init : float, or list of floats.
        The initial azimuth (in degrees) for each of the axes.
        
    Methods
    ----------
    write_video : save the animation as a video file.    
    '''
    
    def __init__(self,fig,ax,period=3,azim_init=0):
        self.fig = fig
        self.ax = ax
        self.period = period
        self.azim_init = azim_init
        
        # make things lists if they're not already
        if type(self.ax) is not list:
            self.ax = [ax,]
            self.period = [period,]
            self.azim_init = [azim_init,]
    
    def write_video(self,fpath_video,fps=30,metadata_dict=None):
        
        dt = 1./fps
        times = np.arange(0,self.period-dt,dt)
        
        if metadata_dict is None:
            metadata_dict = {}
        
        # create the writer for the video file
        FFMpegWriter = copy.deepcopy(manimation.writers['ffmpeg'])
        writer = copy.deepcopy(FFMpegWriter(fps=fps, metadata=metadata_dict))
        with writer.saving(self.fig, fpath_video, 100):
            
            # write each frame
            for ti,time in enumerate(times):
                print('Writing frame '+str(ti)+'/'+str(len(times))+'...')
                
                # update the azimuth for each axes
                for ax,period,azim_init in zip(self.ax,self.period,self.azim_init):
                    ax.set_azim(azim_init+time/period*360.)
                    writer.grab_frame()