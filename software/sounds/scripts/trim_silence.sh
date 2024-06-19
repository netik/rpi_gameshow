#!/bin/bash

ffmpeg -i $1 -af "silenceremove=start_periods=1:start_threshold=-60dB:start_silence=1:stop_periods=1:stop_silence=1:detection=peak" $2

