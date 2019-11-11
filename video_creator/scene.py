# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 14:53:18 2019

@author: Daniel Ruth
"""

class Scene:
    '''
    Describes one portion of a video.
    '''
    
    def __init__(self,draw_fig_func,timing):
        '''
        Parameters
        ----------
        
        draw_fig_func : callable.
            Function to draw a figure. Must accept two inputs:
                - the index time at which to draw the Figure
                - optionally, an instance of Timing, if the current scene time
                  or playback rate are required
            
        timing : Timing.
            Instance of the Timing class to control the timing for the Scene.
        
        '''
        self.draw_fig_func = draw_fig_func
        self.timing = timing
        
    def __call__(self,ix_time,fig):
        '''Create the figure at a given index time.
        '''
        
        # start from a clean slate: remove all the axes
        [a.remove() for a in fig.axes]
        
        # draw on the axes
        self.draw_fig_func(ix_time,fig,timing=self.timing)
    
    def draw_at_stime(self,stime,fig):
        '''Make the figure given a scene time
        '''
        self.timing.update_with_stime(stime)
        ix_time = self.timing.current_indextime
        self(ix_time,fig)