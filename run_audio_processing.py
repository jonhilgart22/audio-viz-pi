#!/usr/bin/python

from audio_processing import read_input_audio

from spectrum_matrix import generate_visualization
import time
import multiprocessing
from threading import Thread

import queue
import numpy as np
from time import sleep

AUDIO_QUEUE = multiprocessing.Queue()


def audio_input_queue():
    print("Putting audio input into the queue")
    while True:
        audio_input = read_input_audio()
        AUDIO_QUEUE.put(audio_input)


def visualization_output_queue():
    print("Reading audio input from the queue to visualize")
    while True:
        try:
            data = AUDIO_QUEUE.get(False)
            # If `False`, the program is not blocked. `Queue.Empty` is thrown if
            # the queue is empty
            generate_visualization(data)
        except queue.Empty:
            print("empty queue")
            data = None


def main():
    """The main driver program that reads in an audio stream and sends it to
    a visualization program to display
    """
    read_thread = Thread(target=audio_input_queue)
    viz_thread = Thread(target=visualization_output_queue)

    read_thread.start()
    viz_thread.start()


if __name__ == "__main__":
    main()
