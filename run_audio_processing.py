#!/usr/bin/python

import multiprocessing
import queue
from threading import Thread

from audio_processing import read_input_audio
from spectrum_matrix import generate_visualization

AUDIO_QUEUE = multiprocessing.Queue()


def audio_input_queue() -> None:
    print("Putting audio input into the queue")
    while True:
        audio_input = read_input_audio()
        AUDIO_QUEUE.put(audio_input)


def visualization_output_queue() -> None:
    print("Reading audio input from the queue to visualize")
    while True:
        try:
            data = AUDIO_QUEUE.get(False)
            # If `False`, the program is not blocked. `Queue.Empty` is thrown if
            # the queue is empty
            generate_visualization(data)
        except queue.Empty:
            print("empty queue")


def main() -> None:
    """The main driver program that reads in an audio stream and sends it to
    a visualization program to display
    """
    read_thread = Thread(target=audio_input_queue)
    viz_thread = Thread(target=visualization_output_queue)

    read_thread.start()
    viz_thread.start()


if __name__ == "__main__":
    main()
