#!/usr/bin/env python3

# Producer needs to produce faster for smooth (fps)

import cv2
import threading
import queue

class Queue:
    q = queue.Queue()
    q2 = queue.Queue()
    qLock = threading.Lock()
    full = threading.Semaphore(0)
    empty = threading.Semaphore(10)

# Reader thread. Reads mp4 file. Generate frames. Put frames into Q.
class ExtractFrame(threading.Thread):
    def __init__(self, fileName, Q, maxFramesToLoad=999):
        print("Init ExtractFrame")
        threading.Thread.__init__(self)
        self.fileName = fileName
        self.Q = Q
        self.maxFramesToLoad = maxFramesToLoad

    # Produces full Q cells, puts frames into q.
    def run(self):
        print("Run Extract")
        # Initialize frame count
        count = 0

        # open video file
        vidcap = cv2.VideoCapture(self.fileName)

        success = True
        while success and count < self.maxFramesToLoad:
            success, frame = vidcap.read()

            # Uses Empty cells, so check if any Empty available. Otherwise, block thread.
            self.Q.empty.acquire()

            # Insert into Q
            self.Q.qLock.acquire()
            self.Q.q.put(frame)
            self.Q.qLock.release()

            self.Q.full.release()

            count += 1
        print('Frame extraction complete')

# BW-izer thread. Reads color frames from q. Generates monochrome frames. Put monochrome frames into q2.
class ConvertToGrayscale(threading.Thread):

    def __init__(self, Q, maxFramesToLoad):
        print("Init ConvertFrame")
        threading.Thread.__init__(self)
        self.Q = Q
        self.maxFramesToLoad = maxFramesToLoad

    # Reads color frames -> generates monochrome.
    def run(self):
        print("Run Convert")
        count = 0

        while count < self.maxFramesToLoad:
            # Check if available frames from q, otherwise, block thread.
            if not self.Q.q.empty():
                # Get frame.
                frame = self.Q.q.get()

                # Convert frame to grayscale.
                grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                self.Q.qLock.acquire()
                self.Q.q2.put(grayscaleFrame)
                self.Q.qLock.release()

                count += 1
        print('Frame conversion complete')


# Displayer thread. Reads monochrome frames. Display frames at a normal frame rate.
class DisplayFrame(threading.Thread):

    def __init__(self, Q, maxFramesToLoad):
        print("Init DisplayFrame")
        threading.Thread.__init__(self)
        self.Q = Q
        self.maxFramesToLoad = maxFramesToLoad

    # Produces empty Q cells. Thread takes frames from q2 and displays them
    def run(self) -> None:
        print("Run DisplayFrame")
        count = 0

        # Go through each frame in the buffer until the buffer is empty.
        while count < self.maxFramesToLoad:
            # Uses Full cells, so check if any Full available and any frames in q2. Otherwise, block thread.
            if not self.Q.q2.empty():
                self.Q.full.acquire()

                self.Q.qLock.acquire()
                frame = self.Q.q2.get()
                self.Q.qLock.release()

                self.Q.empty.release()

                count += 1

                cv2.imshow('Video', frame)
                if cv2.waitKey(21) and 0xFF == ord("q"):
                    break

        print('Finished displaying all frames')
        # cleanup the windows
        cv2.destroyAllWindows()

def main():
    Q = Queue()

    # Create threads
    extractFrame = ExtractFrame("clip.mp4", Q, 72)
    convertToGrayscale = ConvertToGrayscale(Q, 72)
    displayFrame = DisplayFrame(Q, 72)

    # Start threads
    extractFrame.start()
    convertToGrayscale.start()
    displayFrame.start()

if __name__ == "__main__":
    main()