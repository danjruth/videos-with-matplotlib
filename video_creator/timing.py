# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 14:51:46 2019

@author: Daniel Ruth
"""

import numpy as np
import scipy.optimize

class Timing:
    '''
    Controls the mapping between the "index time" (with which a Scene is 
    indexed) and the "scene time" (the actual playback time) for a Scene.
    
    The method .stime_to_time(stime) converts a "scene time" to the index time
    that is displayed at that scene time.
    
    Attributes
    ----------
        
    sduration : float.
        The duration of the scene playback, in seconds. This is calculated on
        a case-by-case basis depending on how the instance is created.
        
    Methods
    ----------
    
    __call__ : get the index time given the scene time
    get_playback_rate : Calculate the playback rate at a given scene time
    update_with_stime : update values with the Scene time
    stime_to_time : convert a scene time to an index time
    '''
    
    def __init__(self):      
        self.current_stime = np.nan
        self.current_playback_rate = np.nan
        self.current_indextime = np.nan
        
    def stime_to_time(stime):
        '''
        Function that returns the index time given the scene time. By defualt,
        returns np.nan since it has not been set yet.
        '''
        return np.nan
        
    def __call__(self,stime):
        '''
        Return the index time given the scene time.
        '''
        return self.stime_to_time(stime)
    
    def get_playback_rate(self,stime,d_stime=1e-3):
        '''
        Numerically calculate the playback rate at a given scene time.
        '''
        time_0 = self(stime)
        time_1 = self(stime+d_stime)
        playback_rate = (time_1-time_0)/d_stime
        return playback_rate
    
    def update_with_stime(self,stime):
        '''Update the instance with the scene time (time, in seconds, into the
        playback of the scene).
        '''
        self.current_stime = stime
        self.current_indextime = self(stime)
        self.current_playback_rate = self.get_playback_rate(stime)
        
    def time_to_stime(self,time):
        '''Compute the scenetime corresponding to an indextime using
        scipy.optimize.minimize.
        '''
        resid = lambda stime: (self(stime)-time)**2
        res = scipy.optimize.minimize(resid,np.array([0]),bounds=[np.array([0,self.sduration])],tol=(1e-6)**2)
        return res.x[0]

    
'''
###############################################################################
### Define some derived classes of Timing to handle common timing methods.
###############################################################################
'''
            
class LinearPlaybackDefinedSpeed(Timing):
    '''Linear playback given a range of times and defined speed.
    '''    
    def __init__(self,start_time,end_time,playback_speed):
        super().__init__()
        self.start_time = start_time
        self.end_time = end_time
        self.playback_speed = playback_speed
        self.sduration = (self.end_time-self.start_time)/self.playback_speed
    def stime_to_time(self,stime):
        return self.start_time + stime*self.playback_speed
    
class LinearPlaybackDefinedDuration(Timing):
    '''Linear playback given a range of times and total scene duration.
    '''    
    def __init__(self,start_time,end_time,sduration):
        super().__init__()
        self.start_time = start_time
        self.end_time = end_time
        self.sduration = sduration        
    def stime_to_time(self,stime):
        return self.start_time + (stime/self.sduration)*(self.end_time-self.start_time)
    
class LinearPlaybackDefinedSpeedAndDuration(Timing):
    '''Linear playback given a start time, playback speed, and scene duration.
    '''    
    def __init__(self,start_time,playback_speed,sduration):
        super().__init__()
        self.start_time = start_time
        self.playback_speed = playback_speed
        self.sduration = sduration
        duration = self.sduration*self.playback_speed
        self.end_time = self.start_time+duration
    def stime_to_time(self,stime):
        return self.start_time + (stime/self.sduration)*(self.end_time-self.start_time)
    
#class LogarithmicPlaybackDefinedSpeeds(Timing):
#    '''Logarithmic playback given the start and end times and 
#    '''
#    pass

# class ReversedLogarithmicPlaybackDefinedDuration(Timing):
#     def __init__(self,start_time,end_time,sduration):
#         super().__init__()
#         self.start_time = start_time
#         self.end_time = end_time
#         self.sduration = sduration        
#     def stime_to_time(self,stime):        
#         return 10**(np.log10(self.start_time)+stime/(self.sduration)*(np.log10(self.end_time)-np.log10(self.start_time)))
    
class LogarithmicPlaybackDefinedDuration(Timing):
    '''Linear playback given a range of times and total scene duration.
    '''    
    def __init__(self,start_time,end_time,sduration):
        super().__init__()
        self.start_time = start_time
        self.end_time = end_time
        self.sduration = sduration        
    def stime_to_time(self,stime):
        return 10**(np.log10(self.start_time)+stime/(self.sduration)*(np.log10(self.end_time)-np.log10(self.start_time)))
    
ReversedLogarithmicPlaybackDefinedDuration = LogarithmicPlaybackDefinedDuration
        
'''
###############################################################################
### End of derived Timing classes.
###############################################################################
'''

def combine_timings(timings_list):
    '''
    Combine a bunch of instances of Timing into one instance that can be used
    on a single Scene.
    '''
    new_timing = Timing()
    scene_durations = np.array([t.sduration for t in timings_list])
    scene_start_times = np.array([0]+list(np.cumsum(scene_durations)))
    total_sduration = np.sum(scene_durations)
    new_timing.sduration = total_sduration
    def stime_to_time(stime):
        possible_scene_start_times = scene_start_times[scene_start_times<=stime]
        which_timing = np.argmax(possible_scene_start_times)
        scene_start_time = possible_scene_start_times[which_timing]
        return timings_list[which_timing](stime-scene_start_time)
    new_timing.stime_to_time = stime_to_time
    
    return new_timing