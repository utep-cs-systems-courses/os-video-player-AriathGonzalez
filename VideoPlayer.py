#!/usr/bin/env python3

import cv2
import threading
from threading import *
import queue

class Queue:
    q = queue.Queue()
    qLock = threading.Lock()
    full = Semaphore(0)
    nFull = 0
    empty = Semaphore(24)
    nEmpty = 24

# Reader thread. Reads mp4 file. Generate frames. Put frames into Q.
class ExtractFrame(threading.Thread):
    def __init__(self, fileName, outputBuffer, maxFramesToLoad=999):
        print("Init...")
        threading.Thread.__init__(self)
        self.fileName = fileName
        self.outputBuffer = outputBuffer
        self.maxFramesToLoad = maxFramesToLoad

    # Produces full Q cells, puts frames into Q.
    def run(self):
        print("Run...ExtractFrame")
        print("Q...")
        for n in list(self.outputBuffer.q.queue):
            print(n, end=" ")

        # Initialize frame count
        count = 0

        # open video file
        vidcap = cv2.VideoCapture(self.fileName)

        # Produce new frame.
        success, frame = vidcap.read()

        # Check if available nEmpty.
        if self.outputBuffer.nEmpty > 0:
            print("Passed first if?")
            self.outputBuffer.empty.acquire()  # Decrement.
            self.outputBuffer.nEmpty -= 1

            self.outputBuffer.qLock.acquire()

            # Insert into Q.
            self.outputBuffer.q.put(frame)

            self.outputBuffer.qLock.release()

            self.outputBuffer.full.release()
            self.outputBuffer.nFull += 1

            print(f'Reading frame {count} {success}')
            while success and count < self.maxFramesToLoad:
                # Produce new frame.
                success, frame = vidcap.read()

                # Check if available nEmpty.
                if self.outputBuffer.nEmpty > 0:
                    print("Passed 2nd if?")

                    self.outputBuffer.empty.acquire()  # Decrement.
                    self.outputBuffer.nEmpty -= 1
                    self.outputBuffer.qLock.acquire()

                    # Insert into Q.
                    self.outputBuffer.q.put(frame)

                    self.outputBuffer.qLock.release()

                    self.outputBuffer.full.release()
                    self.outputBuffer.nFull += 1
                    print(f'Reading frame {count} {success}')
                    count += 1

            #for n in list(self.outputBuffer.q.queue):
                #print(n, end=" ")
            print('Frame extraction complete')

# BW-izer thread. Reads color frames from Q. Generates monochrome frames. Put frames into Q.
class ConvertToGrayscale(threading.Thread):

    def __init__(self, outputBuffer):
        threading.Thread.__init__(self)
        self.outputBuffer = outputBuffer
        print("Init...")

    # Reads color frames -> generates monochrome.
    def run(self):
        print("Run... ConvertToGrayscale")
        print("Q...")
        for n in list(self.outputBuffer.q.queue):
            print(n, end=" ")

        print("Converting frames...")

        # initialize frame count
        count = 0

        # Get q size.
        size = self.outputBuffer.q.qsize()

        while count < size:
            # Get frame.
            frame = self.outputBuffer.q.get()
            # Convert frame to grayscale.
            grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            self.outputBuffer.q.put(grayscaleFrame)
            count += 1

# Displayer thread. Reads monochrome frames. Display frames at a normal frame rate.
class DisplayFrame(threading.Thread):

    def __init__(self, inputBuffer):
        threading.Thread.__init__(self)
        self.inputBuffer = inputBuffer
        print("Init...")

    # Produces empty Q cells. Thread takes frames from Q and displays them
    def run(self) -> None:
        print("Run...DisplayFrame")
        print("Q...")
        for n in list(self.inputBuffer.q.queue):
            print(n, end=" ")
        # Initialize frame count.
        count = 0

        # Go through each frame in the buffer until the buffer is empty.
        while not self.inputBuffer.q.empty():
            self.inputBuffer.full.acquire()
            self.inputBuffer.nFull -= 1

            self.inputBuffer.qLock.acquire()

            # Get the next frame.
            frame = self.inputBuffer.q.get()

            self.inputBuffer.qLock.release()

            self.inputBuffer.empty.release()
            self.inputBuffer.nEmpty += 1

            print(f'Displaying frame {count}')

            # display the image in a window called "video" and wait 42ms
            # before displaying the next frame
            cv2.imshow('Video', frame)
            if cv2.waitKey(42) and 0xFF == ord("q"):
                break

            count += 1

        print('Finished displaying all frames')
        # cleanup the windows
        cv2.destroyAllWindows()

def main():
    print("Main stuff...")
    Q = Queue()

    # Create threads
    extractFrame = ExtractFrame("clip.mp4", Q, 72)
    convertToGrayscale = ConvertToGrayscale(Q)
    displayFrame = DisplayFrame(Q)

    # Start threads
    extractFrame.start()
    extractFrame.join()
    convertToGrayscale.start()
    convertToGrayscale.join()
    displayFrame.start()
    displayFrame.join()

if __name__ == "__main__":
    main()