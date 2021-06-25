# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 14:52:46 2019

@author: Daniel Ruth
"""

import numpy as np

#class TimeScaler:
    
    

class TimeScalerIxAndIx:
    '''
    Fader given the start and end indextimes of the fade.
    '''
    
    def __init__(self,start_indextime,end_indextime,use_log=False):
        self.start_indextime = start_indextime
        self.end_indextime = end_indextime
        self.use_log = use_log
        
    def __call__(self,timing):
        indextime = timing.current_indextime
        
        # if it's after the fade has started
        if indextime >= self.start_indextime:
            
            # if it's during the fade, calculate the value
            if indextime < self.end_indextime:
                if self.use_log:
                    val = (np.log(self.end_indextime)-np.log(indextime)) / (np.log(self.end_indextime)-np.log(self.start_indextime))
                else:
                    val = (indextime-self.start_indextime) / (self.end_indextime-self.start_indextime)
                    
            # if it's after the fade ends, return 1
            else:
                val = 1
         
        # if it's befor the fade, return 0
        else:
            val = 0
            
        return val
        
class TimeScalerStartIxAndDuration:
    '''
    Fader given a start indextime and sceneduration. Trickier since the 
    scenetime corresponding to the start_indextime is not known until it 
    occurs.
    '''
    def __init__(self,start_indextime,duration_scenetime):
        self.start_indextime = start_indextime
        self.duration_scenetime = duration_scenetime
        self.start_scenetime = np.nan
        self.end_scenetime = np.nan
    
    def __call__(self,timing):
        stime = timing.current_stime
        
        # now that we have a timing object, calculate the start and end scenetimes
        if np.isnan(self.start_scenetime):
            self.start_scenetime = timing.time_to_stime(self.start_indextime)
            self.end_scenetime = self.start_scenetime+self.duration_scenetime
        
        # if it's after the fade has started
        if stime >= self.start_scenetime:
            
            # if it's during the fade, calculate the value
            if stime < self.end_scenetime:
                val = (stime-self.start_scenetime) / self.duration_scenetime
            
            # if it's after the fade ends, return 1
            else:
                val = 1
         
        # if it's befor the fade, return 0
        else:
            val = 0
            
        return val
    
class TimeScalerDurationAndEndIx:
    '''
    Fader given a scene duration and ending index time.
    '''
    
    def __init__(self,duration_scenetime,end_indextime):
        self.duration_scenetime = duration_scenetime
        self.end_indextime = end_indextime
        self.start_scenetime = np.nan
        self.end_scenetime = np.nan
        
    def __call__(self,timing):
        stime = timing.current_stime
        
        # now that we have a timing object, calculate the start and end scenetimes
        if np.isnan(self.start_scenetime):
            self.end_scenetime = timing.time_to_stime(self.end_indextime)
            self.start_scenetime = self.end_scenetime - self.duration_scenetime
            
        # if it's after the fade has started
        if stime >= self.start_scenetime:
            
            # if it's during the fade, calculate the value
            if stime < self.end_scenetime:
                val = (self.end_scenetime-stime) / self.sduration
            
            # if it's after the fade ends, return 1
            else:
                val = 1
         
        # if it's befor the fade, return 0
        else:
            val = 0
            
        return val