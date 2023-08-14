# videos-with-matplotlib

Tools to create videos of data in `matplotlib` figures. `Video` objects are composed of a list of `Scene` objects, and the playback of each `Scene` is set by an instance of the `Timing` class, which maps from an "index time" (the time indexing the data shown, such as times at which frames were recorded in a high-speed movie or a simulation time) to the "scene time" (the playback time since the scene began).

For each `Scene` shown, the user must define a function `draw_frame(t,fig,timing=Timing())` which draws the data at index time `t` on axes which are created on the figure `fig`. In drawing the frame, the user has access to the current scene time or playback rate (index time/scene time) through the instance of the `Timing` class passed as an argument.

## Example usage

Start by defining the data we want to show in the movie. It's defined between "index times" 2 and 10.
```python
from video_creator import *
import pandas as pd
t_min=2
t_max=10
my_data = pd.Series(index=np.linspace(t_min,t_max,1001),data=np.sin(np.linspace(t_min,t_max,1001)))
```

Before showing the data, we want a 1 second long title slide to be shown in the movie. This title constitutes a `Scene`, which is constructed below.
```python
t0 = LinearPlaybackDefinedDuration(0,1,1)
def draw_title(t,fig,timing=Timing()):
    ax = fig.add_axes([0,0,1,1])
    ax.text(0,0,'TITLE TEXT',horizontalalignment='center',verticalalignment='center',fontsize=22)
    ax.set_ylim(-1,1)
    ax.set_xlim(-1,1)
title_scene = Scene(draw_title,t0)
```

Now to show the actual data, we want the data between index times 2 and 3 to be shown at a playback rate of 0.5/second, and the rest of the data to be shown over the course of four playback seconds. This requires two instances of the `Timing` class, which are concatenated together.
```python
t1 = LinearPlaybackDefinedSpeed(t_min,3,0.5)
t2 = LinearPlaybackDefinedDuration(3,t_max,4)
timing_main = combine_timings([t1,t2])
```

Now we need to define a function which will draw the frame.
```python
def draw_main(t,fig,timing=Timing()):
  # create the axes on the figure. must be done every time a frame is drawn
  ax = fig.add_subplot(111)

  # get the value of the data to be shown at this indextime
  ix_val = np.argmin(np.abs(t-my_data.index.values))
  x_val = my_data.iloc[ix_val]

  # show the data
  ax.plot(t,x_val,'o',color='k')
  ax.set_xlim([-2,14])
  ax.set_ylim([-2,2])
  
  # we can access both the scene time and the playback rate as the frame is drawn
  ax.set_title('scene time = '+'{:02.3f}'.format(timing.current_stime)+'\n'+'playback rate is '+'{:02.3f}'.format(timing.current_playback_rate))

  fig.tight_layout()
  return None
```

With the `Timing` class and function to draw the figure defined for this main `Scene`, the `Scene` is created with
```python
main_scene = Scene(draw_main,timing_main)
```

We can draw the frame on a figure `fig` at any index time `t` by calling `Scene(t,fig)`. Alternatively, we can draw the frame at a scene playback time `time_into_scene` by calling `scene.draw_at_stime(time_into_scene,fig)`.

To make the video, we create the figure on which it is drawn, and initialize the video with the list of scenes, the figure, and the frames per second with which the video will be written. Then, we can create the video file with the `.write_video()` method. The video frame can be constructed at any "video time" `time_into_video`, or playback within the video, by calling `video(time_into_video)`.
```python
fig = plt.figure(figsize=(9,6))
video = Video([title_scene,main_scene],fig,fps=12)
video.write_video(r'video.mp4')
```

## Classes to control `Scene` playback timing

The following classes are available to control the timing of a playback of a `Scene`, all in the `timing` module. Each is initialized with three of four parameters (index start time, index end time, playback speed, and scene duration).

| Class  | Index time to playback time mapping | Index start time | Index end time | Playback speed | Scene duration |
| ------------- | ------------- | :---: | :---: | :---: | :---: |
| `LinearPlaybackDefinedSpeed`  | Linear  | X | X | X | |
| `LinearPlaybackDefinedDuration`  | Linear  | X | X | | X |
| `LinearPlaybackDefinedSpeedAndDuration`  | Linear  | X | | X | X |
| `ReversedLogarithmicPlaybackDefinedDuration`  | Logarithmic  | X | X |  | X |

## Installation

Download the code to your computer, then run `pip install -e .` .   


