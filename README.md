# Subtitle Remover

*Usage*
 * Install [XQuartz](https://www.xquartz.org/)
 * Change settings as described in [Running GUI applications using Docker for Mac](http://sourabhbajaj.com/blog/2017/02/07/gui-applications-docker-mac/) (namely, enable “Allow connections from network clients” option)
 * Restart XQuartz
```
# Build docker image
docker build -t opencv-py .

# Run bash inside docker image
./start.sh

# Start running python scripts!
# For example:
python3 replace-subtitle.py
```

*Copying audio after subtitles removed([source](http://answers.opencv.org/question/35590/add-audio-channel-to-a-video-created-with-opencv/))*
```sh
ffmpeg -i <sub removed video file> -i <original video file> -map 0:0 -map 1:1 -c:v copy -c:a copy <output file name>
```
