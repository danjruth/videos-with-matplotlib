# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 14:53:45 2019

@author: Daniel Ruth
"""

import numpy as np
import matplotlib.animation as manimation
import copy

class Video:
    '''
    Organizes a collection of Scenes into a video and enables saving them as a
    single video file. "video time" designates the time, in seconds, into the 
    playback of the video.
    '''
    
    def __init__(self,scenes,fig,fps=30):
        '''
        Parameters
        ----------
        
        scenes : list.
            A list of instances of the Scene class which comprimise the video.
            
        fig : matplotlib Figure
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
            for vti,video_time in enumerate(self.video_times):
                print('Writing frame '+str(vti)+'/'+str(len(self.video_times))+'...')
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
        print('Writing the images')
        n_digits = len(str(int(len(self.video_times))))
        #for fi,video_time in tqdm(enumerate(self.video_times),desc='writing the frames'):
        for fi,video_time in enumerate(self.video_times):
            self(video_time)
            self.fig.savefig(directory+'frame_'+str(fi).zfill(n_digits)+extension)
