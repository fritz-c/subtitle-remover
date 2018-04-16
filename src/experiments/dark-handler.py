import numpy as np
import cv2 as cv
import imutils
import sys

subtitleAreaMinY = 560.0/720.0
subtitleAreaMaxY = 700.0/720.0

cv.namedWindow('image', cv.WINDOW_NORMAL)
mult = 1
cv.resizeWindow('image', 600*mult, 480*mult)

if len(sys.argv) < 2:
  print('Need to specify image file as an argument')
  exit(1)

frame = cv.imread(sys.argv[1],1)
frameHeight, frameWidth, _ = frame.shape
resized = imutils.resize(frame, width=500)

gray = cv.cvtColor(resized,cv.COLOR_BGR2GRAY)

blurred = cv.GaussianBlur(gray, (1, 1), 0);

_, thresh = cv.threshold(blurred,10,255,cv.THRESH_BINARY_INV)

averageColor = blurred[:, :].mean()

print(frame[:, :, :].mean())
print(gray[:, :].mean())
print(blurred[:, :].mean())

if averageColor < 20.0:
  mask = np.zeros((frameHeight,frameWidth), np.uint8)

  # White out the bottom part of the screen
  mask[int(subtitleAreaMinY * frameHeight):frameHeight,:] = 255

  frame = cv.inpaint(frame, mask, 3, cv.INPAINT_TELEA)

# cv.imwrite('messigray.png',frame)

cv.imshow('image',frame)
cv.waitKey(0)
cv.destroyAllWindows()
