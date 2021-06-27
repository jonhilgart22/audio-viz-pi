#!/usr/bin/python
## This is an example of a simple sound capture script.
##
## The script opens an ALSA pcm for sound capture. Set
## various attributes of the capture, and reads in a loop,
## Then prints the volume.
##
## To test it out, run it and shout at your microphone:
# borrowed from https://www.raspberrypi.org/forums/viewtopic.php?t=212857

import alsaaudio, time, audioop
from struct import unpack
from typing import Optional, Tuple
import time
from constants import NUM_CHANNELS


SAMPLE_RATE = 44100


def read_input_audio(testing: bool = False) -> Optional[alsaaudio.PCM]:
    # Open the device in nonblocking capture mode. The last argument could
    # just as well have been zero for blocking mode. Then we could have
    # left out the sleep call in the bottom of the loop
    # print("inside audio processing .py")
    try:
        I, data = alsaaudio.PCM(
            alsaaudio.PCM_CAPTURE,
            alsaaudio.PCM_NORMAL,
            cardindex=1,
            channels=NUM_CHANNELS,
            rate=SAMPLE_RATE,
            format=alsaaudio.PCM_FORMAT_S16_LE,
            periodsize=128,  # map to the 64x64 matrix size, 128 or  8192. 128 is too fast?
        ).read()
        # print(data, "data inside audio processing")
    except alsaaudio.ALSAAudioError as e:
        print(f"Error reading in audio {e}")
        return None

    # # Set attributes: Stereo, 8000 Hz, 16 bit little endian samples
    # inp.setchannels(2)
    # inp.setrate(8000)
    # inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

    # The period size controls the internal number of frames per period.
    # The significance of this parameter is documented in the ALSA api.
    # For our purposes, it is suficcient to know that reads from the device
    # will return this many frames. Each frame being 2 bytes long.
    # This means that the reads below will return either 320 bytes of data
    # or 0 bytes of data. The latter is possible because we are in nonblocking
    # mode.
    # inp.setperiodsize(160)

    if testing:
        # while True:
        # I, data = inp.read()
        print(I, data, "I data")
        if I:
            unpacked_data = unpack("%dh" % (len(data) / 2), data)
            print(audioop.max(data, 2))
        time.sleep(0.01)
        return None
    else:

        return data


if __name__ == "__main__":
    read_input_audio()
