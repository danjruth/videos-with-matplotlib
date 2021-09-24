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
        '''
        Draw the frame at the given index time. Involves clearing the Figure
        and calling the draw_fig_func for that index time.
        
        Parameters
        ----------
        ix_time : float
            The index time at which to draw the frame.
            
        fig : matplotlib Figure
            The figure on which to draw the frame.
        '''
        
        # start from a clean slate: remove all the axes
        #[a.remove() for a in fig.axes]
        fig.clf()
        
        # remove texts drawn directly on the figure
        for ti in range(len(fig.texts)):
            del fig.texts[ti]
        
        # draw on the axes
        self.draw_fig_func(ix_time,fig,timing=self.timing)
    
    def draw_at_stime(self,stime,fig):
        '''
        Draw the frame at the given scene time (playback time into the scene).
        Involves updating the Timing instance with the scene time to find the 
        corresponding index time, and calling __call__ with that index time.
    
        Parameters
        ----------
        stime : float
            The playback time into the scene, in seconds.
            
        fig : matplotlib Figure
            The figure on which to draw the frame.
        '''
        self.timing.update_with_stime(stime)
        ix_time = self.timing.current_indextime
        self(ix_time,fig)