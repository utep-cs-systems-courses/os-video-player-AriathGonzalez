#!/usr/bin/env python3

import cv2
import time
import threading
import queue

class Queue:
    q = queue.Queue()
    q2 = queue.Queue()
    qLock = threading.Lock()
    full = threading.Semaphore(0)
    nFull = 0
    empty = threading.Semaphore(10)
    nEmpty = 10
    timeToDisplay = False

# Reader thread. Reads mp4 file. Generate frames. Put frames into Q.
class ExtractFrame(threading.Thread):
    def __init__(self, fileName, Q, maxFramesToLoad=999):
        print("Init...")
        threading.Thread.__init__(self)
        self.fileName = fileName
        self.Q = Q
        self.maxFramesToLoad = maxFramesToLoad

    # Produces full Q cells, puts frames into Q.
    def run(self):
        while True:
            print("Run...ExtractFrame")

            # Initialize frame count
            count = 0

            # open video file
            vidcap = cv2.VideoCapture(self.fileName)

            success = True
            while success and count < self.maxFramesToLoad:
                # If full sleep, until completely empty
                # Produce new frame.
                if self.Q.nEmpty > 0:
                    success, frame = vidcap.read()

                    self.Q.empty.acquire()
                    self.Q.nEmpty -= 1

                    # Insert into Q
                    self.Q.qLock.acquire()
                    self.Q.q.put(frame)
                    self.Q.qLock.release()

                    self.Q.full.release()
                    self.Q.nFull += 1

                    print(f'Reading frame {count} {success}')
                    count += 1
                #elif self.Q.nEmpty != 10:
                #else:
                    #time.sleep(0.5)
            print('Frame extraction complete')
            break

# BW-izer thread. Reads color frames from Q. Generates monochrome frames. Put frames into Q.
class ConvertToGrayscale(threading.Thread):

    def __init__(self, Q, maxFramesToLoad):
        threading.Thread.__init__(self)
        self.Q = Q
        self.maxFramesToLoad = maxFramesToLoad
        print("Init...")

    # Reads color frames -> generates monochrome.
    def run(self):
        while True:
            # While full, convert
            print("Run... ConvertToGrayscale")

            print("Converting frames...")

            # initialize frame count
            count = 0

            # Get q size.
            #size = self.Q.q.qsize()

            while count < self.maxFramesToLoad:
                #if self.Q.nFull > 0:
                if not self.Q.q.empty():
                    print(f'Converting frame {count}')
                    # Get frame.
                    frame = self.Q.q.get()

                    # Convert frame to grayscale. (Rn converting grayscale to grayscale?)
                    grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    self.Q.qLock.acquire()
                    self.Q.q2.put(grayscaleFrame)
                    self.Q.qLock.release()

                    count += 1
                    #if self.Q.q.empty():
                        #self.Q.timeToDisplay = True
                #else:
                    #time.sleep(0.5)
            break

# Displayer thread. Reads monochrome frames. Display frames at a normal frame rate.
class DisplayFrame(threading.Thread):

    def __init__(self, Q, maxFramesToLoad):
        threading.Thread.__init__(self)
        self.Q = Q
        self.maxFramesToLoad = maxFramesToLoad
        print("Init...")

    # Produces empty Q cells. Thread takes frames from Q and displays them
    def run(self) -> None:
        while True:

            # Sleep until time to display(nEmpty 0 or nFull = 10)

            print("Run...DisplayFrame")
            count = 0

            # Go through each frame in the buffer until the buffer is empty.
            #while not self.Q.q.empty():
            while count < self.maxFramesToLoad :
                #if self.Q.nFull > 0:
                if self.Q.nFull > 0 and not self.Q.q2.empty():
                    while self.Q.nFull > 0:
                        self.Q.full.acquire()
                        self.Q.nFull -= 1

                        self.Q.qLock.acquire()

                        # Get the next frame.
                        frame = self.Q.q2.get()

                        self.Q.qLock.release()

                        self.Q.empty.release()
                        self.Q.nEmpty += 1

                        print(f'Displaying frame {count}')
                        count += 1
                        # Sleep until time to display
                        cv2.imshow('Video', frame)
                        if cv2.waitKey(42) and 0xFF == ord("q"):
                            break
                #else:
                    #cv2.destroyAllWindows()
                    #time.sleep(0.5)

            print('Finished displaying all frames')
            # cleanup the windows
            cv2.destroyAllWindows()
            break

def main():
    print("Main stuff...")
    Q = Queue()

    # Create threads
    extractFrame = ExtractFrame("clip.mp4", Q, 72)
    convertToGrayscale = ConvertToGrayscale(Q, 72)
    displayFrame = DisplayFrame(Q, 72)

    # Start threads
    extractFrame.start()
    #extractFrame.join()
    convertToGrayscale.start()
    #convertToGrayscale.join()
    displayFrame.start()
    #displayFrame.join()

if __name__ == "__main__":
    main()