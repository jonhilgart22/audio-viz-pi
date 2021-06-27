# adapted from https://www.hackster.io/gatoninja236/raspberry-pi-audio-spectrum-display-1791fa#things
import alsaaudio as aa
import wave
from struct import unpack
import numpy as np
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from typing import List, Any
import time
from constants import NUM_CHANNELS

__all__ = ["generate_visualization"]


def read_in_wav_file(file_name: str = "test.wav"):
    wavfile = wave.open(file_name)
    SAMPLE_RATE = wavfile.getframerate()
    NUM_CHANNELS = wavfile.getnchannels()
    return wavfile


# Constants
SAMPLE_RATE = 44100
CHUNK = 4096
N_ROWS = 64
N_COLS = 64


def create_d_matrix() -> RGBMatrix:
    # Use the rgbmatrix library to create a matrix class
    # we will use this to create our visuzliations
    options = RGBMatrixOptions()
    options.rows = N_ROWS
    options.cols = N_COLS
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = "adafruit-hat"
    options.drop_privileges = False
    Dmatrix = RGBMatrix(options=options)
    return Dmatrix


def calculate_levels(data: Any, previous_power: List[int]) -> List[int]:
    """
    Create the matrix visualization

	Args:
		data ([type]): input sound wave
        previous_power([type]): the previous wavelength power array

	Returns:
		[type]: np array of int
	"""
    data = unpack("%dh" % (len(data) / 2), data)
    data = np.array(data, dtype="h")
    if len(data) == 0:
        print("Len of data is zero")
        return np.zeros(1), 0
    fourier = np.fft.rfft(data)
    fourier = np.delete(fourier, len(fourier) - 1)
    power = np.log10(np.abs(fourier)) ** 2
    print(power, "power")
    if len(power) == N_ROWS:  # this is the size of the matrix
        min_value = np.min(power)
        max_value = np.max(power)
        # https://stats.stackexchange.com/questions/281162/scale-a-number-between-a-range
        matrix = np.int_(N_ROWS * (power - min_value) / (max_value - min_value))
        # matrix = power
    else:
        try:
            reshaped_power = np.reshape(power, (N_ROWS, N_COLS))
        except ValueError as e:
            print(e, "---error---")
            print(previous_power, "pwervioud power")
            reshaped_power = np.reshape(previous_power, (N_ROWS, N_COLS))

        matrix = np.int_(np.average(reshaped_power, axis=1))
    print(matrix.shape, "matrix shape")
    print(matrix, "matrix")
    # matrix = np.array([np.random.randint(10, 64) for i in range(64)])
    print(len(matrix), "len matrix")
    return matrix, power


def write_to_led_matrix(data: Any):
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
        periodsize=CHUNK,
    )
    previous_power = 0
    output.write(data)
    Dmatrix = create_d_matrix()
    matrix, current_power = calculate_levels(data, previous_power)
    if len(matrix) == 1:  # finished
        return None
    previous_power = current_power
    Dmatrix.Clear()
    print("Writing to a matrix")
    for y in range(0, N_ROWS):  # write to the matrix
        for x in range(int(matrix[y])):
            # print(x, y, " x,y")
            x *= 2  # original 2
            if x < 32:
                # https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/bindings/python/rgbmatrix/core.pyx#L32
                Dmatrix.SetPixel(y, x, 255, 50, 50)  # r,g,b
                Dmatrix.SetPixel(y, x - 1, 255, 50, 50)
            elif x < 50:
                Dmatrix.SetPixel(y, x, 255, 25, 0)
                Dmatrix.SetPixel(y, x - 1, 255, 25, 0)
            else:
                Dmatrix.SetPixel(y, x, 255, 100, 50)
                Dmatrix.SetPixel(y, x - 1, 255, 100, 50)
    print("Finished writing to the led matrix")


def generate_visualization(data=None) -> None:
    """
    main input function that listens to a .wav file and draws corresponding pixels
    or takes in buffer input from an audio device
    
    :param data: either a buffer stream from audio in or none. If None, reads a .wav file
    """
    reading_input_file = False
    if data is None:
        reading_input_file = True
        wavfile = read_in_wav_file("moo.wav")
        data = wavfile.readframes(CHUNK)
        print(data, "data")

    if reading_input_file:
        print("reading input file")
        while data != "":
            write_to_led_matrix(data)
    else:
        write_to_led_matrix(data)


if __name__ == "__main__":
    generate_visualization()
