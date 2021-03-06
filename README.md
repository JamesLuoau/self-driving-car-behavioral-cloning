#Learn human driving behavior based on deep neural network

##### Table of Contents  
1.. [Overview](#Overview)

2.. [Existing Solutions](#Existing_Solutions)

2.1 [Nvidia](#nvidia)

2.2 [Commaai](#commaai)

3.. Model(#model)

4.. [Data Collection](#data_collection)

5.. [Iterations](#iterations)

5.1 [Iteration 1, Centre Image Only, no dropout](#centre_image_no_dropout)

5.2 [Iteration 2 Centre Image Only with 0.5 dropout](#centre_image_dropout_5)

5.3 [Iteration 3 Center/Left/Right Images](#centre_left_right_images)

5.4 [Iteration 3 Center/Left/Right Images With Crop](#centre_left_right_images_crop)

5.5 [Iteration 5 Shift Image Randomly](#centre_left_right_images_crop_shift)

5.6 [Iteration 6 Shift and Flip](#centre_left_right_images_crop_shift_flip)

5.7 [Iteration 7 Shift, Flip, Brightness and Shadown](#centre_left_right_images_crop_shift_flip_brightness_shadown)

5.8 [Iteration 8 Feeding data distribution](#data_distribution)

6.. [Todos](#todos)


<a name="Overview"/>

#Overview
This is [UDacity](https://www.udacity.com/drive) Self Driving Car Behavioral Cloning Project

Lots of blog / repositories in internet just show you their final result, but how did they reach their beautiful 
final result is really the most important part for a learner point of view.

This repository arms to help me as a newbie and helps you who is learning deep learning

1. Easy to experiment, from simply apply CNN model to very complex data augment
2. Reproducible, every bad result we keep it reproducible so that we know we made a mistake buy what reason
3. Visualise what's going on
4. Build more understanding about how deep learning works

To help achieve above goal, all code base has been formed by below layers or pipes

| Layer             | Purpose                                                                                           |
| ------------------|---------------------------------------------------------------------------------------------------|
| DriveDataSet      | Represent the data you recorded                                                                   |
| --filter_method   | What data you'd like to added in                                                                  |
| RecordAllocator   | Before pass recorded data to data augment, percentage of different data you'd like to added in    |
| generators        | Data augment process you'd like to apply to, easy to extend to any order                          |
| DataGenerator     | Read from RecordAllocator, pass to generator, then feed data into Keras generator                 |
| model             | the Network                                                                                       |
| Trainer           | create Model, read data from DataGenerator, do the real training                                  |


When we put everything together, the simple form of code looks like:
```python
def raw_data_centre_image_only():
    # Create DriveDataSet from csv file, you can specify crop image, using all cameras and which data will included in
    data_set = DriveDataSet.from_csv(
        "datasets/udacity-sample-track-1/driving_log.csv", crop_images=False, all_cameras_images=False,
        filter_method=drive_record_filter_include_all)
    # What the data distribution will be, below example just randomly return data from data set, so that the
    # distribution will be same with what original data set have
    allocator = RecordRandomAllocator(data_set)
    # what's the data augment pipe line have, this have no pipe line, just the image itself
    augment = image_itself
    # connect allocator and augment together
    data_generator = DataGenerator(allocator.allocate, augment)
    # create the model
    model = nvidia(input_shape=data_set.output_shape(), dropout=0.5)
    # put everthing together, start a real Keras training process with fit_generator
    Trainer(model, learning_rate=0.0001, epoch=10, custom_name=raw_data_centre_image_only.__name__).fit_generator(
        data_generator.generate(batch_size=128)
    )
raw_data_centre_image_only()
```

the code to make our car running in both track 1 and 2
```python
def segment_std_distribution_shift_flip_brightness_shadow():
    data_set = DriveDataSet.from_csv(
        "datasets/udacity-sample-track-1/driving_log.csv", crop_images=True, all_cameras_images=True,
        filter_method=drive_record_filter_include_all)
    # fine tune every part of training data so that make it meat normal distribution
    allocator = AngleSegmentRecordAllocator(
        data_set,
        AngleSegment((-1.5, -0.5), 10),  # big sharp left
        AngleSegment((-0.5, -0.25), 14),  # sharp left
        AngleSegment((-0.25, -0.249), 3),  # sharp turn left (zero right camera)
        AngleSegment((-0.249, -0.1), 10),  # big turn left
        AngleSegment((-0.1, 0), 11),  # straight left
        AngleSegment((0, 0.001), 4),  # straight zero center camera
        AngleSegment((0.001, 0.1), 11),  # straight right
        AngleSegment((0.1, 0.25), 10),  # big turn right
        AngleSegment((0.25, 0.251), 3),  # sharp turn right (zero left camera)
        AngleSegment((0.251, 0.5), 14),  # sharp right
        AngleSegment((0.5, 1.5), 10)  # big sharp right
    )
    # a pipe line with shift -> flip -> brightness -> shadow augment processes
    augment = pipe_line_generators(
        shift_image_generator(angle_offset_pre_pixel=0.002),
        flip_generator,
        brightness_image_generator(0.35),
        shadow_generator
    )
    data_generator = DataGenerator(allocator.allocate, augment)
    model = nvidia(input_shape=data_set.output_shape(), dropout=0.5)
    Trainer(model, learning_rate=0.0001, epoch=45, multi_process=use_multi_process,
            custom_name="bigger_angle_shift_0.002_bright_0.35_angles_35_30_35").fit_generator(
        data_generator.generate(batch_size=256)
    )
```

<a name="Existing_Solutions"/>

#Existing Solutions
<a name="nvidia"/>

###NVIDIA
Nvidia has published a nice paper [End to End Learning for Self-Driving Cars](https://images.nvidia.com/content/tegra/automotive/images/2016/solutions/pdf/end-to-end-dl-using-px.pdf).

<a href="http://www.youtube.com/watch?feature=player_embedded&v=-96BEoXJMs0
" target="_blank"><img src="http://img.youtube.com/vi/-96BEoXJMs0/0.jpg" 
alt="NVIDIA AI Car Demonstration" width="400" height="360" border="10" /></a>

<a name="commaai"/>

###Commaai
1. [The Paper](https://arxiv.org/abs/1608.01230)
2. [Github Repository](https://github.com/commaai/research)
3. [train_steering_model.py](https://github.com/commaai/research/blob/master/train_steering_model.py)

<a name="data_collection"/>

#Data Collection
1. [UDacity](https://d17h27t6h515a5.cloudfront.net/topher/2016/December/584f6edd_data/data.zip) 
provided a simulator and produced a sample data for track 1 that you can use.
**this is recommended way**
2. Generate your data from UDacity Self-Driving Car Simulator
3. [Sully Chen](https://github.com/SullyChen) 
had a [TensorFlow implementation](https://github.com/SullyChen/Autopilot-TensorFlow) 
and shared his own [dataset](https://drive.google.com/file/d/0B-KJCaaF7ellQUkzdkpsQkloenM/view?usp=sharing)

UDacity Sample data

<a href="http://www.youtube.com/watch?feature=player_embedded&v=LLCXS-uCMSw" target="_blank">
<img src="http://img.youtube.com/vi/LLCXS-uCMSw/0.jpg" alt="UDacity Sample Data" width="320" height="360" border="10" /></a>

<a name="model"/>

#Model
##nvidia
![nvidia model](images/nvidia_model.png)


<a name="iterations"/>

#Iterations
<a name="centre_image_no_dropout"/>

##Iteration 1, Centre Image Only, no dropout
```python
def raw_data_centre_image_only():
    # Create DriveDataSet from csv file, you can specify crop image, using all cameras and which data will included in
    data_set = DriveDataSet.from_csv(
        "datasets/udacity-sample-track-1/driving_log.csv", crop_images=False, all_cameras_images=False,
        filter_method=drive_record_filter_include_all)
    # What the data distribution will be, below example just randomly return data from data set, so that the
    # distribution will be same with what original data set have
    allocator = RecordRandomAllocator(data_set)
    # what's the data augment pipe line have, this have no pipe line, just the image itself
    augment = image_itself
    # connect allocator and augment together
    data_generator = DataGenerator(allocator.allocate, augment)
    # create the model
    model = nvidia(input_shape=data_set.output_shape(), dropout=0.0)
    # put everthing together, start a real Keras training process with fit_generator
    Trainer(model, learning_rate=0.0001, epoch=10, custom_name=raw_data_centre_image_only.__name__).fit_generator(
        data_generator.generate(batch_size=128)
    )
```
**50seconds** per epoch, final loss **0.004**, total trainable params: **2,882,619**, the weights file has 128mb

car gose wild and running into water before bridge

![centre_camera_nvidia_no_dropout](images/results/centre_camera_nvidia_no_dropout.gif "centre_camera_nvidia_no_dropout")


<a name="centre_image_dropout_5"/>

##Iteration 2 Centre Image Only with 0.5 dropout
dropout created much better result, with everything remands same, it able to drive
much more smooth and able to pass bridge, from now on we will always has 0.5 dropout
```python
def raw_data_centre_image_dropout_5():
    data_set = DriveDataSet.from_csv(
        "datasets/udacity-sample-track-1/driving_log.csv", crop_images=False, all_cameras_images=False,
        filter_method=drive_record_filter_include_all)
    allocator = RecordRandomAllocator(data_set)
    augment = image_itself
    data_generator = DataGenerator(allocator.allocate, augment)
    # dropout=0.5 was the only difference
    model = nvidia(input_shape=data_set.output_shape(), dropout=0.5)
    Trainer(model, learning_rate=0.0001, epoch=10, custom_name=raw_data_centre_image_dropout_5.__name__).fit_generator(
        data_generator.generate(batch_size=128)
    )
```
**50seconds** per epoch, final loss **0.012**, total trainable params: **2,882,619**, the weights file has 128mb
![raw_data_centre_image_dropout_5](images/results/centre_camera_nvidia_drop0.5.gif "centre_camera_nvidia_drop0.5")

<a name="centre_left_right_images"/>

##Iteration 3 Center/Left/Right Images
It fails on road which don't have a clear edge. what if we add left and right camera 
images in? as they are more point towards to road edge, we are expecting model will
gain better knowledge about road edge.

Compare to iteration 2, our car at least trying to make a little turn before run out.
```python
def raw_data_centre_left_right_image():
    # all_cameras_images=True was the only difference
    data_set = DriveDataSet.from_csv(
        "datasets/udacity-sample-track-1/driving_log.csv", crop_images=False, all_cameras_images=True,
        filter_method=drive_record_filter_include_all)
    allocator = RecordRandomAllocator(data_set)
    generator = image_itself
    data_generator = DataGenerator(allocator.allocate, generator)
    model = nvidia(input_shape=data_set.output_shape(), dropout=0.5)
    Trainer(model, learning_rate=0.0001, epoch=10, custom_name=raw_data_centre_left_right_image.__name__).fit_generator(
        data_generator.generate(batch_size=128)
    )
```
**50seconds** per epoch, final loss **0.024**, total trainable params: **2,882,619**, the weights file has 128mb
![center_left_right](images/results/center_left_right.gif "center_left_right")

<a name="centre_left_right_images_crop"/>

##Iteration 4 Center/Left/Right with Crop
By remove the informat we know won't effecting steering angle, for example sky, we 
can make our model more focuse to the things that matters.
by reduce image size from 160x320 to 66x200, we reduced the training time from 50 seconds 
epoch to 10 seconds! the trainable parames reduced from **2,882,619** to **252,219**
and the result is amazing, we are able to pass until next right turn

The cropped version of sample data video:

<a href="http://www.youtube.com/watch?feature=player_embedded&v=pxG46j9kK0I" target="_blank">
<img src="http://img.youtube.com/vi/pxG46j9kK0I/0.jpg" alt="UDacity Sample Data Cropped Version" width="320" height="200" border="10" /></a>

```python
def raw_data_centre_left_right_image_crop():
    # crop_images=True was the only difference
    data_set = DriveDataSet.from_csv(
        "datasets/udacity-sample-track-1/driving_log.csv", crop_images=True, all_cameras_images=True,
        filter_method=drive_record_filter_include_all)
    allocator = RecordRandomAllocator(data_set)
    generator = image_itself
    data_generator = DataGenerator(allocator.allocate, generator)
    model = nvidia(input_shape=data_set.output_shape(), dropout=0.5)
    Trainer(model, learning_rate=0.0001, epoch=10, custom_name=raw_data_centre_left_right_image_crop.__name__).fit_generator(
        data_generator.generate(batch_size=128)
    )
```
**10seconds** per epoch, final loss **0.033**, total trainable params: **252,219**, the weights file has 6.4mb
![centre_left_right_crop](images/results/centre_left_right_crop.gif "centre_left_right_crop")

<a name="centre_left_right_images_crop_shift"/>

##Iteration 5 Shift Image Randomly
so far we have made use of all provided data, and our car able to drive half of the lap,
it seems that we need some how create more data so that our car knows how to make a good
right turn.
Other idea is that shift the images and adjust angles accordingly.
for example, center image with angle 0, move 10 pixels left would result angle 0.02

![shift_center_images](images/shift_center_images.gif "shift_center_images")

As we introduced random generator here, every batch our model will see different image so that we can't cache,
the crop we did and enable multi_process is a life saver (espicially we will do more augment later),

If we allow images shift 100 pixels, the number of samples could grow from 24,100 images to 2,410,000
that's great for your model

```python
def raw_data_centre_left_right_crop_shift():
    data_set = DriveDataSet.from_csv(
        "datasets/udacity-sample-track-1/driving_log.csv", crop_images=True, all_cameras_images=True,
        filter_method=drive_record_filter_include_all)
    allocator = RecordRandomAllocator(data_set)
    # shift_image_generator added in
    generator = shift_image_generator(angle_offset_pre_pixel=0.002)
    data_generator = DataGenerator(allocator.allocate, generator)
    model = nvidia(input_shape=data_set.output_shape(), dropout=0.5)
    # have to enable multi_process as image generator becomes to bottle neck
    Trainer(model, learning_rate=0.0001, epoch=20, multi_process=use_multi_process,
            custom_name=raw_data_centre_left_right_crop_shift.__name__).fit_generator(
        data_generator.generate(batch_size=128)
    )
```
**160seconds** per epoch, final loss **0.036**, total trainable params: **252,219**, the weights file has 6.4mb

We are able to run whole lap without crush, great achievement!!

![raw_data_centre_left_right_crop_shift](images/results/raw_data_centre_left_right_crop_shift.gif "raw_data_centre_left_right_crop_shift")
![raw_data_centre_left_right_crop_shift track 2](images/results/raw_data_centre_left_right_crop_shift track 2.gif "raw_data_centre_left_right_crop_shift track 2")

<a name="centre_left_right_images_crop_shift_flip"/>

##Iteration 6, Shift and Flip
In last iteration, our car able to run in track 1, but fail in track 2, also wheels 
has cross the degoue zoom, which is conside as not safe.

Flip is a way to generate image by a mirror-reversal of an original across a horizontal axis.

```python
def raw_data_centre_left_right_crop_shift_flip():
    data_set = DriveDataSet.from_csv(
        "datasets/udacity-sample-track-1/driving_log.csv", crop_images=True, all_cameras_images=True,
        filter_method=drive_record_filter_include_all)
    allocator = RecordRandomAllocator(data_set)
    # shift_image_generator was the only difference
    generator = pipe_line_generators(
        shift_image_generator(angle_offset_pre_pixel=0.002),
        flip_generator
    )
    data_generator = DataGenerator(allocator.allocate, generator)
    model = nvidia(input_shape=data_set.output_shape(), dropout=0.5)
    Trainer(model, learning_rate=0.0001, epoch=20, multi_process=use_multi_process,
            custom_name=raw_data_centre_left_right_crop_shift_flip.__name__).fit_generator(
        data_generator.generate(batch_size=128)
    )
```
**160seconds** per epoch, final loss **0.035**, total trainable params: **252,219**, the weights file has 6.4mb

![raw_data_centre_left_right_crop_shift_flip](images/results/raw_data_centre_left_right_crop_shift_flip.gif "raw_data_centre_left_right_crop_shift_flip")

Youtube Full Version

<a href="http://www.youtube.com/watch?feature=player_embedded&v=FWNCuCbronw" target="_blank">
<img src="http://img.youtube.com/vi/FWNCuCbronw/0.jpg" alt="raw_data_centre_left_right_crop_shift_flip" width="320" height="200" border="10" /></a>

<a name="centre_left_right_images_crop_shift_flip_brightness_shadown"/>

##Iteration 7, Shift, Flip, Brightness and Shadown
Track 2 had a much darker road, also shadows from montain, in this iteration we add 
brightness and shadow randomly to images.

Below code will take 1 image from training set, apply shift, flip, brightness and shadown
create 20 images and save it as gif.
```python
    dataset = DriveDataSet.from_csv("datasets/udacity-sample-track-1/driving_log.csv")

    generator = pipe_line_generators(
        shift_image_generator(angle_offset_pre_pixel=0.002),
        flip_generator,
        brightness_image_generator(0.25),
        shadow_generator
    )
    Video.from_generators("test/resources/generator_pipe_line.gif", dataset[60], 20, generator)
```
![generator_pipe_line](images/generator_pipe_line.gif "generator_pipe_line")

```python
def raw_data_centre_left_right_crop_shift_flip():
    data_set = DriveDataSet.from_csv(
        "datasets/udacity-sample-track-1/driving_log.csv", crop_images=True, all_cameras_images=True,
        filter_method=drive_record_filter_include_all)
    allocator = RecordRandomAllocator(data_set)
    # shift_image_generator was the only difference
    generator = pipe_line_generators(
        shift_image_generator(angle_offset_pre_pixel=0.002),
        flip_generator
    )
    data_generator = DataGenerator(allocator.allocate, generator)
    model = nvidia(input_shape=data_set.output_shape(), dropout=0.5)
    Trainer(model, learning_rate=0.0001, epoch=20, multi_process=use_multi_process,
            custom_name=raw_data_centre_left_right_crop_shift_flip.__name__).fit_generator(
        data_generator.generate(batch_size=128)
    )
```
**180seconds** per epoch, final loss **0.035**, total trainable params: **252,219**, the weights file has 6.4mb

![raw_data_centre_left_right_crop_shift_flip](images/results/raw_data_centre_left_right_crop_shift_flip.gif "raw_data_centre_left_right_crop_shift_flip")

Youtube Full Version

<a href="http://www.youtube.com/watch?feature=player_embedded&v=FWNCuCbronw" target="_blank">
<img src="http://img.youtube.com/vi/FWNCuCbronw/0.jpg" alt="raw_data_centre_left_right_crop_shift_flip" width="320" height="200" border="10" /></a>

<a name="data_distribution"/>

###Iteration 8 Feeding data distribution
We are still not able to make sharper turns, 
it looks we running out of option? one way is go back to simulator and generate more data,
also we know the model should work, the issue must be in the data, either not enough or we baies the model too much,
in track 1, car is turning left far more than right, maybe that's why our car not able to handle the turning right 

Let's look back and see what kind of data we feed into model.
The Udacity Sample data has below distribution

![angle_distribution_original](images/angle_distribution_original.png)

The straight angle (zero degree) has far more chance feeding into model, where the real
turn looks becomes very minor to system.

As we have a augment pipe line, what happens if we invove pipe line in?
![angle_distribution_generator_random_allocator](images/angle_distribution_generator_random_allocator.png)


As you can see, angle 0 (going straight) has far more samples, as we used left and right camera data, 0.25 and -0.25
is same.
what it happened in real world of our steering angle distributed? I guess maybe it's 25% of left and right turn, 50% 
of straight.

Develop a system that able to control data distribution would benefit our experiment, 
A record allocator called AngleSegmentRecordAllocator is here to serve this purpose.

AngleSegmentRecordAllocator request multiple AngleSegment objects which define the start 
end point of angles as well as how many percentage this segment will allocate into training set.

Based on the original distribution, we'd like to create 11 segment to change the final
training set into a normal distribution

below code will generator 25,600 samples and plot the angle distribution
```python
data_set = create_real_dataset(filter_method=drive_record_filter_include_all)
allocator = AngleSegmentRecordAllocator(
    data_set,
    AngleSegment((-1.5, -0.5), 10),    # big sharp left
    AngleSegment((-0.5, -0.25), 14),   # sharp left
    AngleSegment((-0.25, -0.249), 3),  # sharp turn left (zero right camera)
    AngleSegment((-0.249, -0.1), 10),  # big turn left
    AngleSegment((-0.1, 0), 11),       # straight left
    AngleSegment((0, 0.001), 4),      # straight zero center camera
    AngleSegment((0.001, 0.1), 11),    # straight right
    AngleSegment((0.1, 0.25), 10),     # big turn right
    AngleSegment((0.25, 0.251), 3),   # sharp turn right (zero left camera)
    AngleSegment((0.251, 0.5), 14),   # sharp right
    AngleSegment((0.5, 1.5), 10)     # big sharp right
)
generator = pipe_line_generators(
    shift_image_generator(angle_offset_pre_pixel=0.002),
    flip_generator,
    brightness_image_generator(0.25)
)
_angle_distribution(
    "angle_distribution_generator_exclude_duplicated_small_angles_40_20_40_pipe_line", 100, 256,
    allocator=allocator.allocate,
    angle_offset_pre_pixel=0.002,
    generator=generator
)
```
![angle_distribution_segment_11](images/angle_distribution_segment_11.png)

after this process, we got confidence that right / left turn, straight are got 
better chance to feed into model.
the result are very promise, we are able to run in both tracks and all turns are smooth

Track 1 (The training track)

<a href="http://www.youtube.com/watch?feature=player_embedded&v=aIbBFLhGVUU" target="_blank">
<img src="http://img.youtube.com/vi/aIbBFLhGVUU/0.jpg" alt="raw_data_centre_left_right_crop_shift_flip" width="320" height="200" border="10" /></a>

Track 2 (The track model never see)

<a href="http://www.youtube.com/watch?feature=player_embedded&v=BhEuwRFVVQA" target="_blank">
<img src="http://img.youtube.com/vi/BhEuwRFVVQA/0.jpg" alt="raw_data_centre_left_right_crop_shift_flip" width="320" height="200" border="10" /></a>

<a name="other_thinking"/>

#Other Experiment

<a name="remove_zero_angles_or_not"/>

## Remove Zero Angles or Remove Duplicated Small Angles
I saw lots of blog says if put too many zero angles to model, model will bias to zero.

my experiment shows that instead remove lots of data, it's better to add more 
data to make it normal distributed. (remove zero angle data will reduce the training sample to half)


<a name="todos"/>

#TODOs

##Data
Don't use Udacity sample data, record our own with 4 laps, 8 laps, see how it effecting the rest especially generalization

##More Models
There are lot more waiting to explorer. the model has been totally been left out, only 
nvidia has been tested in this repo, feel free to fork this repo and experience more.

1. nvidia with regularizer and YUV channels
2. commaai model
3. design some new model
4. add RNN
5. check udacity competition 2 and bring more model in

##Visualization
visualize how CNN sees the input picture could be fun, and could help us understanding if training is good or not