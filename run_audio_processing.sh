#!/bin/sh
# make the LED react to live sounds by use of a USB microphone
# I am too lazy to look up how to make the python program read from STDIN so i will just
# make the equivalent thing by creating test.wav as a nmed pipe. It's an old linux trick.

rm test.wav; mkfifo test.wav

# background the python program. It will patiently wait for input
sudo python3 spectrum_matrix.py &

# Now run ffmpeg
# see my own post, https://drjohnstechtalk.com/blog/2019/04/live-stream-to-youtube-from-a-raspberry-pi-webcam/
ffmpeg \
-thread_queue_size 4096 \
-f alsa -i plughw:1,0 \
-ac 2 \
-y \
test.wav