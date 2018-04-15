FROM victorhcm/opencv:3.2.0-python3.4

RUN apt-get update && apt-get install -y python3-tk
RUN pip3 install matplotlib imutils

COPY . /app
WORKDIR /app/src

# RUN g++ -O3 subre.cpp -lopencv_videoio -lopencv_photo -lopencv_core -lopencv_imgproc -lopencv_highgui --std=c++11 -o subtitle_remover

# CMD ["/app/subtitle_remover", "/app/shared/short.mp4", "/app/shared/out.mp4"]
CMD ["bash"]
