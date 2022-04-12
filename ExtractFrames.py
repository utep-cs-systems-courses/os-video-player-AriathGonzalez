#!/usr/bin/env python3

# Step 1.

# Extracts a series of frames from the video contained in 'clip.mp4' and saves
# them as jpeg images in sequentially numbered files with the pattern
# 'frame_xxxx.jpg'.

import cv2
import os

# globals
outputDir = 'frames'
clipFileName = 'clip.mp4'
# initialize frame count
count = 0

# open the video clip
vidcap = cv2.VideoCapture(clipFileName)

# create the output directory if it doesn't exist
if not os.path.exists(outputDir):
  print(f"Output directory {outputDir} didn't exist, creating")
  os.makedirs(outputDir)

# read one frame
success,image = vidcap.read()

print(f'Reading frame {count} {success}')
while success and count < 72:

  # write the current frame out as a jpeg image
  cv2.imwrite(f"{outputDir}/frame_{count:04d}.jpg", image)

  success,image = vidcap.read()
  print(f'Reading frame {count}')
  count += 1
