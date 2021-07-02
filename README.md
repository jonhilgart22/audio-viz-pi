# audio-viz-pi

Real-time audio visualization for raspberry pi

## Materials
- Purchase everything from [this guide](https://www.hackster.io/gatoninja236/raspberry-pi-audio-spectrum-display-1791fa#things) except for the `DFRobot ESP32 FireBeetle` chip.
- Assemble following the adafruit guide [here](https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi/assembly). One tricky thing is sodering the white wire from the rainbow cable to the 24 GPIO pin. You can see an image of this below.
- You'll also need a usb microphone. I used [this one](https://www.amazon.com/gp/product/B08M37224H/ref=ppx_yo_dt_b_search_asin_image?ie=UTF8&psc=1).


<img src="media/pin_24.jpeg" alt="pin 24" width="300"/>

## Results

1. Audio Processing 
- You can display the frequency steptrum of audio in near real-time as shown below.

[![first_audio_image](https://img.youtube.com/vi/wC7Q1LEvRRQ/0.jpg)](https://www.youtube.com/watch?v=wC7Q1LEvRRQ)

- In addition, there is an option to have the color bars change gradually over time shown below. 
[![second_audio_image](https://img.youtube.com/vi/HIWIXwZ4F4o/0.jpg)](https://www.youtube.com/watch?v=HIWIXwZ4F4o)

2. Displaying Images
- With the 64x64 matrix hooked up to the pi, you can also display images such as this image of a walk in the woods.

<img src="media/walk-in-the-woods.jpeg" alt="walk_in_woods" width="300"/>

## Install

- All on your raspberry pi

1. Follow the instructions here <https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/bindings/python>
2. Install 
```shell 
apt-get libasound2-dev
``` 
on your raspberry pi

3. Install Poetry

 ```shell 
 curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
 ```

4. Install poetry dependencies 

```shell 
poetry install
```

## Run
This should all be run on your raspbrerry pi

1. Launch this program 
```shell 
sudo python3 -m run_audio_processing
```

- This uses two threads to read in audio data pushed to a queue. Then, we read data from the queue and pass it to the visuzliation program.

1. Run this
```shell
sudo ./run_audio_processing.sh
```

- This passes in audio data using a named pip from ffmeg to ```spectrum_matrix.py```

