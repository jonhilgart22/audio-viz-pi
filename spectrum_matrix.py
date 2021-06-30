# adapted from https://www.hackster.io/gatoninja236/raspberry-pi-audio-spectrum-display-1791fa#things
import alsaaudio as aa
import wave
from struct import unpack
import numpy as np
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from typing import List, Any, Tuple
import time
from constants import NUM_CHANNELS, PERIOD_SIZE, SAMPLE_RATE

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
    if len(power) == N_ROWS:  # this is the size of the matrix
        min_value = np.min(power)
        max_value = np.max(power)
        # https://stats.stackexchange.com/questions/281162/scale-a-number-between-a-range
        # matrix = np.int_(N_ROWS * (power - min_value) / (max_value - min_value))
        matrix = power
    else:
        try:
            reshaped_power = np.reshape(power, (N_ROWS, N_COLS))
        except ValueError as e:
            print(e, "---error---")
            reshaped_power = np.reshape(previous_power, (N_ROWS, N_COLS))
        matrix = np.int_(np.average(reshaped_power, axis=1))

    return matrix, power


def write_to_led_matrix(data: Any) -> None:
    """"Write to each individual LED of our 64x64 matrix

    Args:
        data (): the buffer of input audio data

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
        for y in range(int(matrix[x])):
            # print(x, y, "x y")
            if y < 32:
                # https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/bindings/python/rgbmatrix/core.pyx#L32
                D_MATRIX.SetPixel(x, y, 255, 50, 50)  # r,g,b
                D_MATRIX.SetPixel(x, y - 1, 255, 50, 50)
            elif y < 50:
                D_MATRIX.SetPixel(x, y, 255, 25, 0)
                D_MATRIX.SetPixel(x, y - 1, 255, 25, 0)
            else:
                D_MATRIX.SetPixel(x, y, 255, 100, 50)
                D_MATRIX.SetPixel(x, y - 1, 255, 100, 50)
    print("Finished writing to the led matrix")


def generate_visualization(data: Any = None) -> None:
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

    if reading_input_file:
        print("reading input file")
        while data != "":
            write_to_led_matrix(data)
    else:  # used to pass live audio to the visualization program
        write_to_led_matrix(data)


if __name__ == "__main__":
    generate_visualization()
