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
    
    period : float.
        The period (in seconds) of each axes's rotation.
        
    azim_init : float, or list of floats.
        The initial azimuth (in degrees) for each of the axes.
        
    oscillate : bool.
        If True, oscillates the azimuth sinusoidally instead of spinning the 
        axes all the way around.
        
    oscillate_amplitude : float.
        The amplitude (in degrees) of the oscillation, if oscillate is True.
        
    Methods
    ----------
    write_video : save the animation as a video file.
    write_images : save the animation as a sequence of images.  
    '''
    
    def __init__(self,fig,ax,period=3,azim_init=-60,oscillate=False,oscillate_amplitude=45.):
        self.fig = fig
        self.ax = ax
        self.period = period
        self.azim_init = azim_init
        self.oscillate = oscillate
        self.oscillate_amplitude = oscillate_amplitude
        
        # make things lists if they're not already
        if type(self.ax) is not list:
            self.ax = [ax,]
            self.azim_init = [azim_init,]
            
    def _compute_frame_times(self,fps):
        '''calculate the times for each frame
        '''        
        dt = 1./fps
        times = np.arange(0,self.period-dt,dt)
        return times
    
    def _update_axes(self,time):
        '''update the azimuth on each axes given the time
        '''
        for ax,azim_init in zip(self.ax,self.azim_init):
            if self.oscillate == False:
                ax.azim = azim_init+time/self.period*360.
            if self.oscillate == True:
                ax.azim =  azim_init + self.oscillate_amplitude * np.sin(time/self.period*2*np.pi)
                print(ax.azim)
    
    def write_video(self,fpath_video,fps=30,metadata_dict=None):
        '''Save the animation as a video file.
        '''        
        times = self._compute_frame_times(fps)        
        if metadata_dict is None:
            metadata_dict = {}
        
        # create the writer for the video file
        FFMpegWriter = copy.deepcopy(manimation.writers['ffmpeg'])
        writer = copy.deepcopy(FFMpegWriter(fps=fps, metadata=metadata_dict))
        with writer.saving(self.fig, fpath_video, 100):
            
            # write each frame
            for ti,time in enumerate(times):
                print('Writing frame '+str(ti)+'/'+str(len(times))+'...')
                self._update_axes(time)
                writer.grab_frame()
                
    def write_images(self,directory,fps=30,extension='.png'):
        '''Save each frame as an image in a directory.
        '''
        print('Writing the images')
        times = self._compute_frame_times(fps)
        n_digits = len(str(int(len(times))))
        for ti,time in enumerate(times):
            print('Writing frame '+str(ti)+'/'+str(len(times))+'...')
            self._update_axes(time)
            self.fig.savefig(directory+'frame_'+str(ti).zfill(n_digits)+extension)
