#!/usr/bin/env bash

# From: http://sourabhbajaj.com/blog/2017/02/07/gui-applications-docker-mac/

# Build docker image if necessary
# docker build -t opencv-py .

# Start xquartz if it's not already running
# open -a XQuartz

IP=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
xhost + $IP

docker run -ti --rm \
  -e DISPLAY=$IP:0 \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "$(pwd)/shared":/app/shared \
  -v "$(pwd)/src":/app/src \
  opencv-py
