#!/usr/bin/python
## This is an example of a simple sound capture script.
##
## The script opens an ALSA pcm for sound capture. Set
## various attributes of the capture, and reads in a loop,
## Then prints the volume.
##
## To test it out, run it and shout at your microphone:
# borrowed from https://www.raspberrypi.org/forums/viewtopic.php?t=212857

import audioop
import time
from struct import unpack
from typing import Optional

import numpy as np

import alsaaudio
from constants import NUM_CHANNELS, PERIOD_SIZE, SAMPLE_RATE


def read_input_audio(testing: bool = False) -> Optional[alsaaudio.PCM]:
    # Open the device in blocking capture mode.
    # The period size controls the internal number of frames per period.
    # The significance of this parameter is documented in the ALSA api.
    # For our purposes, it is suficcient to know that reads from the device
    # will return this many frames
    try:
        I, data = alsaaudio.PCM(
            alsaaudio.PCM_CAPTURE,
            alsaaudio.PCM_NORMAL,
            cardindex=1,  # the USB audio device
            channels=NUM_CHANNELS,
            rate=SAMPLE_RATE,
            format=alsaaudio.PCM_FORMAT_S16_LE,
            periodsize=PERIOD_SIZE,
        ).read()
    except alsaaudio.ALSAAudioError as e:
        print(f"Error reading in audio {e}")
        return None

    unpacked_data = np.array(
        unpack(str(2 * PERIOD_SIZE) + "B", data)
    )  # unpack from pytes
    return unpacked_data
