#!/bin/bash

# Using which command to find the path
ffmpeg_path=$(which ffmpeg)

# Check if ffmpeg_path contains a value
if [ -n "$ffmpeg_path" ]; then
    echo "ffmpeg is located at: $ffmpeg_path"
else
    echo "ffmpeg not found in your PATH."
fi
