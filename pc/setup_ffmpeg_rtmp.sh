#!/bin/bash
ffmpeg -fflags nobuffer -flags low_delay -listen 1 -i rtmp://0.0.0.0:5000/live/drone -f v4l2 /dev/video10
