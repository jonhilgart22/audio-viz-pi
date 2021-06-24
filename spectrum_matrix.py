# adapted from https://www.hackster.io/gatoninja236/raspberry-pi-audio-spectrum-display-1791fa#things
import alsaaudio as aa
import wave
from struct import unpack
import numpy as np
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from typing import List

wavfile = wave.open("test.wav")
SAMPLE_RATE = wavfile.getframerate()
NUM_CHANNELS = wavfile.getnchannels()

# Constants
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
    Dmatrix = RGBMatrix(options=options)
    Dmatrix.Clear()
    return Dmatrix


def calculate_levels(data, chunk, previous_power: List[int]) -> List[int]:
    """
    Create the matrix visualization

	Args:
		data ([type]): input sound wave
		chunk ([type]): total number of pixels in our matrix
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
    try:
        reshaped_power = np.reshape(power, (N_ROWS, int(chunk / N_COLS)))
    except ValueError as e:
        print(e, "---error---")
        reshaped_power = np.reshape(previous_power, (N_ROWS, int(chunk / N_COLS)))

    matrix = np.int_(np.average(reshaped_power, axis=1))
    return matrix, previous_power


def main():
    """
    main input function that listens to a .wav file and draws corresponding pixels
    """
    data = wavfile.readframes(CHUNK)
    Dmatrix = create_d_matrix()
    previous_power = 0
    output = aa.PCM(
        aa.PCM_PLAYBACK,
        aa.PCM_NORMAL,
        channels=NUM_CHANNELS,
        rate=SAMPLE_RATE,
        format=aa.PCM_FORMAT_S16_LE,
        periodsize=CHUNK,
    )

    while data != "":
        output.write(data)
        matrix, current_power = calculate_levels(data, CHUNK, previous_power)
        if len(matrix) == 1:  # finished
            break
        previous_power = current_power
        Dmatrix.Clear()
        for y in range(0, N_ROWS):
            for x in range(matrix[y]):
                x *= 2
                if x < 32:
                    # https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/bindings/python/rgbmatrix/core.pyx#L32
                    Dmatrix.SetPixel(y, x, 100, 50, 50)  # r,g,b
                    Dmatrix.SetPixel(y, x - 1, 100, 50, 50)
                elif x < 50:
                    Dmatrix.SetPixel(y, x, 25, 25, 0)
                    Dmatrix.SetPixel(y, x - 1, 25, 25, 0)
                else:
                    Dmatrix.SetPixel(y, x, 50, 100, 50)
                    Dmatrix.SetPixel(y, x - 1, 50, 100, 50)
        data = wavfile.readframes(CHUNK)


if __name__ == "__main__":
    main()
