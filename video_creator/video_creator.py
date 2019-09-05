# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 13:41:27 2019

@author: Daniel Ruth
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as manimation
from tqdm import tqdm
import copy

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
        self.current_stime = stime
        self.current_indextime = self(stime)
        self.current_playback_rate = self.get_playback_rate(stime)

    
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
        duration = self.sduration/self.playback_speed
        self.end_time = self.start_time+duration
    def stime_to_time(self,stime):
        return self.start_time + (stime/self.sduration)*(self.end_time-self.start_time)
    
#class LogarithmicPlaybackDefinedSpeeds(Timing):
#    '''Logarithmic playback given the start and end times and 
#    '''
#    pass

class ReversedLogarithmicPlaybackDefinedDuration(Timing):
    def __init__(self,start_time,end_time,sduration):
        super().__init__()
        self.start_time = start_time
        self.end_time = end_time
        self.sduration = sduration        
    def stime_to_time(self,stime):        
        return 10**(np.log10(self.start_time)+stime/(self.sduration)*(np.log10(self.end_time)-np.log10(self.start_time)))
        
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
        
class Video:
    '''
    Organizes a collection of Scenes into a video and enables saving them as a
    single video file.
    '''
    
    def __init__(self,scenes,fig,fps=30):
        '''
        Parameters
        ----------
        
        scenes : list.
            A list of instances of the Scene class which comprimise the video.
            
        fig : toolkit.display.Figure.
            The figure on which all the Scenes are drawn.
            
        fps : float.
            The number of frames per second with which to create the video.
            This parameter only controls the temporal resolution of the
            resulting video file, not its duration or the content shown.
        '''
        
        self.scenes = scenes
        self.fig = fig
        self.fps = fps
        self._process_times()
        
    def _process_times(self):
        '''Calculate each Scene's duration and when its video start time, as
        well as the total video duration and the video times of each frame.
        '''
        
        # get the duration of each scene and the start videotimes for each scene
        self.scene_durations = np.array([s.timing.sduration for s in self.scenes])
        self.scene_start_times = np.array([0]+list(np.cumsum(self.scene_durations))[:-1])
        
        # the total duration of the video
        self.duration = np.sum(self.scene_durations)
        
        # calculate the video times
        dt = 1./self.fps
        self.video_times = np.arange(0,self.duration,dt)
        
    def _scene_and_stime(self,vtime):
        '''Given a video time, return the corresponding Scene and the scene
        time within that Scene.
        '''
        possible_scene_start_times = self.scene_start_times[self.scene_start_times<=vtime]
        scene_ix = np.argmax(possible_scene_start_times)
        scene = self.scenes[scene_ix]
        stime = vtime-possible_scene_start_times[scene_ix]
        return scene,stime
    
    def __call__(self,video_time):
        '''Create the frame at a given video time on the figure.
        '''
        scene,stime = self._scene_and_stime(video_time)
        scene.draw_at_stime(stime,self.fig)
        
    def write_video(self,fpath_video,metadata_dict=None):
        '''Write the video to a single video file.
        '''
        if metadata_dict is None:
            metadata_dict = {}
        
        # create the writer for the video file
        FFMpegWriter = copy.deepcopy(manimation.writers['ffmpeg'])
        writer = copy.deepcopy(FFMpegWriter(fps=self.fps, metadata=metadata_dict))
        with writer.saving(self.fig, fpath_video, 100):
            #for video_time in tqdm(self.video_times,desc='writing the video file'):
            for video_time in self.video_times:
                self(video_time)
                writer.grab_frame()
                
#    def write_gif(self,fpath_gif):
#        '''Requires imagemagick, which isn't installed yet'''
#        
#        writer = manimation.ImageMagickWriter(fps=self.fps)
#        with writer.saving(self.fig, fpath_gif, self.fig.get_dpi()):
#            for video_time in tqdm(self.video_times,desc='writing the GIF'):
#                self(video_time)
#                writer.grab_frame()
                
#    def write_html(self,fpath_video,metadata_dict=None):
#        '''Write the video to a single html file, does not work.
#        '''
#        if metadata_dict is None:
#            metadata_dict = {}
#        
#        # create the writer for the video file
#        HTMLWriter = manimation.writers['html']
#        writer = HTMLWriter(fps=self.fps, metadata=metadata_dict)        
#        with writer.saving(self.fig, fpath_video, 100):
#            for video_time in tqdm(self.video_times,desc='writing the video file'):
#                self(video_time)
#                writer.grab_frame()        
        
    def write_images(self,directory,extension='.png'):
        '''Save each frame as an image in a directory.
        '''
        n_digits = len(str(int(len(self.video_times))))
        for fi,video_time in tqdm(enumerate(self.video_times),desc='writing the frames'):
            self(video_time)
            fig.savefig(directory+'frame_'+str(fi).zfill(n_digits)+extension)
