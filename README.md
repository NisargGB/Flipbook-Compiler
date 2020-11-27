# Flipbook Compiler Project

This is a prototype language design and it's compiler to render flipbook videos froma set of source images
The language specifications, syntax and features are as follows - 

## Introduction

A flip book is a book with a series of pictures that vary gradually from one page to the next, so that when the pages are turned rapidly the pictures appear to animate by simulating motion or some other change. A user designing a flipbook probably doesn't want to specify eah of the individual frame and it's components. Rather, they would wish to specify the range of frames where an object should be displayed or moved about across the frames to simulate motion. To make the best use of this language, users must use transparent png images to display objects in their flipbook.

The videos are rendered at 15 FPS.

## How to code a flipbook

(Refer code.flip for a sample code)
The code is written in a .flip file and each new command is in a different line.
Comments are specified by starting the line with '#'
A line can either be comment or a command, not both.

For the purpose of this project and a POC, we experiment with  3 basic commands in the language - 

    frame_size <Height> <Width>
        
        Task: Sets the dimensions of the final video to be rendered.

        Args: Height - Integer specifying the height of the final video
              Width  - Integer specifying the width of the final video
        
        Note: This command can be ignored, and default video frame size of (512, 512) will be chosen. If not ignored this command must be the **first non-comment line** in the file.

    
    show <image_path> <start_frame> <end_frame> <scale> <top_offset> <right_offset>

        Taks: Displays an image in frames from [start_frame, end_frame)

        Args: image_path - The path to the image that is to be placed in the flipbook. Should be relative to the resource directory given
              start_frame - The starting frame number (starting from 0) from which the image has to be displayed
              end_frame - The ending frame number (not included) till which image should be displayed
              scale - The factor by which the image of the object should e scaled before displaying it
              top_offset - Vertical distance between top left corner of object image and upper edge of frame
              right_offset - Horizontal distance between top left corner of object image and left edge of frame

    
    move <image_path> <start_frame> <end_frame> <scale> <start_top_offset> <start_right_offset> <end_top_offset> <end_right_offset>

        Taks: Displays and moves an image in frames from [start_frame, end_frame) from start to end position specified by the offsets. Follows a straight line motion between the given positions. The speed of the obct will be calculated by the distance to be travelled and the number of frames ssigned for the motion.

        Args: image_path - The path to the image that is to be placed in the flipbook. Should be relative to the resource directory given
              start_frame - The starting frame number (starting from 0) from which the image has to be displayed
              end_frame - The ending frame number (not included) till which image should be displayed
              scale - The factor by which the image of the object should e scaled before displaying it
              start_top_offset - Starting Vertical distance between top left corner of object image and upper edge of frame
              start_right_offset - starting Horizontal distance between top left corner of object image and left edge of frame
              end_top_offset - Ending Vertical distance between top left corner of object image and upper edge of frame
              end_right_offset - Ending Horizontal distance between top left corner of object image and left edge of frame

        Note: This command will not affect any existing or future object. It rather brings in the object, moves it and then removes it from subsequent frames. To make it presist, user has to use the 'show' command after the move period.


## Compiler specifications

Use Python 3
Required libraries: numpy, opencv, argparse

To compile your code - 
    
    $python3 compiler.py <yourcode.flip> --resource_dir <res_dir_path> --output <outfile_path>

    Args: yourcode.flip - The path to the .flip code file to be compiled
          res_dir_path - The path to the directory containing source images required for rendering video
          outfile_path - The path and name of the output **.avi** file to be created

    For example - 
    python3 compiler.py sample_code.flip --resource_dir resources --output sample_video.avi

This creates a video .avi file with given name.
Runs at 15 FPS

## Sample
[The sample source code](sample_code.flip)
[The sample rendered video of Newton](bin/sample_video.avi)

## Extensibility

There is a lot of scope to expand the capapbilities of this language. Some suggestions are as follows -
1. Image rotation can be done along with Image scaling
2. More complex motion commands can be introduced for object movements. For example, circular motion can be introduced by specifying radius and angle of revolution.
3. Image processing commands can be introduced - Like changing contrast, brigtness, etc.