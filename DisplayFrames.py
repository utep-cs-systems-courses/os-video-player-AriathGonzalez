#!/usr/bin/env python3

# Step 3.

# Loads a series of frames sequentially from files with the names
# 'grayscale_xxxx.jpg' and displays them with a 42ms delay.

import cv2
import time

# globals
outputDir = 'frames'
frameDelay = 42       # the answer to everything

# initialize frame count
count = 0

# Generate the filename for the first frame 
frameFileName = f'{outputDir}/grayscale_{count:04d}.jpg'

# load the frame
frame = cv2.imread(frameFileName)

while frame is not None:
    
    print(f'Displaying frame {count}')
    # Display the frame in a window called "Video"
    cv2.imshow('Video', frame)

    # Wait for 42 ms and check if the user wants to quit
    if cv2.waitKey(frameDelay) and 0xFF == ord("q"):
        break    
    
    # get the next frame filename
    count += 1
    frameFileName = f'{outputDir}/grayscale_{count:04d}.jpg'

    # Read the next frame file
    frame = cv2.imread(frameFileName)

# make sure we cleanup the windows, otherwise we might end up with a mess
cv2.destroyAllWindows()
