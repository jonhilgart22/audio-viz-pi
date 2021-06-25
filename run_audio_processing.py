#!/usr/bin/python

from audio_processing import read_input_audio

from spectrum_matrix import generate_visualization
import time


def main():
    """The main driver program that reads in an audio stream and sends it to
    a visualization program to display
    """
    # create queues to read and process data
    # https://stackoverflow.com/questions/34619779/implement-realtime-signal-processing-in-python-how-to-capture-audio-continuous
    while True:
        audio_input = read_input_audio()
        # unpacked_data = unpack("%dh" % (len(data) / 2), data)
        if audio_input:
            print("made it to generate viz")
            generate_visualization(audio_input)


if __name__ == "__main__":
    main()
