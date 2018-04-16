import numpy as np
import cv2 as cv

cap = cv.VideoCapture('short.mp4')

cv.namedWindow('frame', cv.WINDOW_NORMAL)
while(cap.isOpened()):
    ret, frame = cap.read()
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    cv.imshow('frame',gray)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv.destroyAllWindows()
