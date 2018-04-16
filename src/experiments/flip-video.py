import numpy as np
import cv2 as cv

cap = cv.VideoCapture('short.mp4')

# Use the same codec as the input video
fourcc = int(cap.get(cv.CAP_PROP_FOURCC))
width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH));
height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT));
fps = float(cap.get(cv.CAP_PROP_FPS));

out = cv.VideoWriter('output.mp4', fourcc, fps, (width,height))
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        frame = cv.flip(frame,0)
        # write the flipped frame
        out.write(frame)
        cv.imshow('frame',frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
# Release everything if job is finished
cap.release()
out.release()
cv.destroyAllWindows()
