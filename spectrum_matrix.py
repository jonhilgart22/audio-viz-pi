# adapted from https://www.hackster.io/gatoninja236/raspberry-pi-audio-spectrum-display-1791fa#things
import time
import wave
from struct import unpack
from typing import Any, List, Tuple

import numpy as np

import alsaaudio as aa
from constants import NUM_CHANNELS, PERIOD_SIZE, SAMPLE_RATE
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

__all__ = ["generate_visualization"]


def read_in_wav_file(file_name: str = "test.wav"):
    wavfile = wave.open(file_name)
    SAMPLE_RATE = wavfile.getframerate()
    NUM_CHANNELS = wavfile.getnchannels()
    return wavfile


# Constants
N_ROWS = 64
N_COLS = 64


# These need to be constants in order to not reinitialize the matrix class for every audio sample
# Use the rgbmatrix library to create a matrix class
# we will use this to create our visuzliations
options = RGBMatrixOptions()
options.rows = N_ROWS
options.cols = N_COLS
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = "adafruit-hat"
options.drop_privileges = False
D_MATRIX = RGBMatrix(options=options)


def moving_average(x: List[int], w: int) -> List[int]:
    return np.int_(np.convolve(x, np.ones(w), "same") / w)


def calculate_levels(
    data: Any, previous_power: List[int]
) -> Tuple[List[int], List[int]]:
    """
    Create the matrix visualization

	Args:
		data ([type]): input sound wave
        previous_power([type]): the previous wavelength power array

	Returns:
		[type]: np array of int
	"""
    if len(data) == 0:
        print("Len of data is zero")
        return np.zeros(1), 0
    fourier = np.fft.rfft(data)
    fourier = np.delete(fourier, len(fourier) - 1)
    power = np.log10(np.abs(fourier)) ** 2
    try:
        reshaped_power = np.reshape(power, (N_ROWS, int(PERIOD_SIZE / N_ROWS)))
    except ValueError as e:
        print(e, "---error---")
        reshaped_power = np.reshape(previous_power, (N_ROWS, int(PERIOD_SIZE / N_ROWS)))
    matrix = np.int_(np.average(reshaped_power, axis=1))
    min_value = np.min(matrix)
    max_value = np.max(matrix)
    # https://stats.stackexchange.com/questions/281162/scale-a-number-between-a-range
    max_value = max_value * 0.7
    if max_value > N_ROWS:
        max_value = N_ROWS
    matrix = np.int_(max_value * ((matrix - min_value) / (max_value - min_value)))
    matrix = moving_average(matrix, 4)

    return matrix, power


def write_to_led_matrix(data: Any, r_val: int, g_val: int, b_val: int) -> None:
    """"Write to each individual LED of our 64x64 matrix

    Args:
        data (): the buffer of input audio data
        r_val: int the value for red to visualize
        g_val:int the value for green to visualize
        b_val:int the value for blue to visualize

    Returns:
        [type]: [description]
    """
    output = aa.PCM(
        aa.PCM_PLAYBACK,
        aa.PCM_NORMAL,
        channels=NUM_CHANNELS,
        rate=SAMPLE_RATE,
        format=aa.PCM_FORMAT_S16_LE,
        periodsize=PERIOD_SIZE,
    )
    previous_power = 0
    output.write(data)
    matrix, current_power = calculate_levels(data, previous_power)
    if len(matrix) == 1:  # finished
        return None
    previous_power = current_power
    print("Writing to a matrix")
    D_MATRIX.Clear()
    for x in range(0, N_ROWS):  # write to the matrix
        for y in range(int(matrix[x]) * 2):
            # create color gradient
            aug_r_val = r_val + y
            aug_g_val = g_val + y
            aug_b_val = b_val + y
            if aug_r_val > 255:
                aug_r_val = r_val
            if aug_g_val > 255:
                aug_g_val = r_val
            if aug_b_val > 255:
                aug_b_val = r_val
            D_MATRIX.SetPixel(x, y, aug_r_val, aug_g_val, aug_b_val)  # r,g,b
            D_MATRIX.SetPixel(x, y - 1, aug_r_val, aug_g_val, aug_b_val)
    print("Finished writing to the led matrix")


def generate_visualization(
    r_val: int, g_val: int, b_val: int, data: Any = None,
) -> None:
    """
    main input function that read from a .wav file and draws corresponding pixels
    or takes in buffer input from an audio device
    
    :param data: either a buffer stream from audio in or none. If None, reads a .wav file

    """

    reading_input_file = False
    if data is None:
        reading_input_file = True
        wavfile = read_in_wav_file("moo.wav")
        data = wavfile.readframes(PERIOD_SIZE)
        # starting color is dark red
        r_val = 100
        g_val = 10
        b_val = 10

    if reading_input_file:
        print("reading input file")
        while data != "":
            write_to_led_matrix(data, r_val, g_val, b_val)
    else:  # used to pass live audio to the visualization program
        write_to_led_matrix(data, r_val, g_val, b_val)


if __name__ == "__main__":
    generate_visualization()
