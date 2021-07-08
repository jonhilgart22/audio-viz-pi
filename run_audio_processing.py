#!/usr/bin/python

import multiprocessing
import queue
from threading import Thread
import numpy as np
from audio_processing import read_input_audio
from spectrum_matrix import generate_visualization

AUDIO_QUEUE = multiprocessing.Queue()


def audio_input_queue() -> None:
    print("Putting audio input into the queue")
    while True:
        audio_input = read_input_audio()
        AUDIO_QUEUE.put(audio_input)


def visualization_output_queue(
    rand_int_lower: int = 0, rand_int_upper: int = 5
) -> None:
    print("Reading audio input from the queue to visualize")
    # starting color is dark red
    r_val = 100
    g_val = 10
    b_val = 10
    # bools for color transitions
    r_going_up = True
    r_going_down = False
    g_going_up = True
    g_going_down = False
    b_going_up = True
    b_going_down = False
    while True:
        try:
            data = AUDIO_QUEUE.get(False)
            # If `False`, the program is not blocked. `Queue.Empty` is thrown if
            # the queue is empty
            generate_visualization(r_val, g_val, b_val, data=data)
            # create some randomnes2 so that color transitions aren't deterministic
            if r_going_up:
                r_val += np.random.randint(rand_int_lower, rand_int_upper)
            elif r_going_down:
                r_val -= np.random.randint(rand_int_lower, rand_int_upper)

            if g_going_up:
                g_val += np.random.randint(rand_int_lower, rand_int_upper)
            elif g_going_down:
                g_val -= np.random.randint(rand_int_lower, rand_int_upper)

            if b_going_up:
                b_val += np.random.randint(rand_int_lower, rand_int_upper)
            elif b_going_down:
                b_val -= np.random.randint(rand_int_lower, rand_int_upper)
            # adjust limits
            if r_val > 255:
                r_val = 255
                r_going_down = True
                r_going_up = False
            elif r_val < 0:
                r_val = 0
                r_going_up = True
                r_going_down = False

            if g_val > 255:
                g_val = 255
                g_going_down = True
                g_going_up = False
            elif g_val < 0:
                g_val = 0
                g_going_up = True
                g_going_down = False

            if b_val > 255:
                b_val = 255
                b_going_down = True
                b_going_up = False
            elif b_val < 0:
                b_val = 0
                b_going_up = True
                b_going_down = False
        except queue.Empty:
            print("empty queue")


def main() -> None:
    """The main driver program that reads in an audio stream and sends it to
    a visualization program to display
    """
    audio_input_thread = Thread(target=audio_input_queue)
    viz_thread = Thread(target=visualization_output_queue)

    audio_input_thread.start()
    viz_thread.start()


if __name__ == "__main__":
    main()
