import numpy as np
import cv2 as cv
import imutils
import sys

detectionThreshold = 0.1
subtitleAreaMinY = 560.0/720.0
subtitleAreaMaxY = 710.0/720.0
screenAllBlackThreshold = 35.0

cv.namedWindow('image', cv.WINDOW_NORMAL)
mult = 1
cv.resizeWindow('image', 600*mult, 480*mult)

if len(sys.argv) < 2:
  print('Need to specify image file as an argument')
  exit(1)

frame = cv.imread(sys.argv[1],1)
frameHeight, frameWidth, _ = frame.shape
# resized = imutils.resize(frame, width=500)
# ratio = frame.shape[0] / float(resized.shape[0])

gray = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)

blurred = cv.GaussianBlur(gray, (7, 7), 0);

_, mask = cv.threshold(blurred,10,255,cv.THRESH_BINARY_INV)

kernel = np.ones((50, 50), np.uint8)
mask = cv.morphologyEx(mask, cv.MORPH_DILATE, kernel)
kernel = np.ones((40, 40), np.uint8)
mask = cv.morphologyEx(mask, cv.MORPH_ERODE, kernel)

mask[0:int(subtitleAreaMinY * frameHeight),:] = 0
mask[int(subtitleAreaMaxY * frameHeight):int(frameHeight),:] = 0

# contours = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL,
#   cv.CHAIN_APPROX_SIMPLE)[0]
# subtitleContours = []
# for c in contours:
#   contourMoments = cv.moments(c)
#   if contourMoments["m00"] == 0:
#     continue;

#   centerX = int((contourMoments["m10"] / contourMoments["m00"]) * ratio)
#   centerY = int((contourMoments["m01"] / contourMoments["m00"]) * ratio)
#   xDistanceFromSubtitleCenter = abs(frameWidth / 2.0 - centerX)/frameWidth
#   yDistanceFromSubtitleCenter = abs(frameHeight * (subtitleAreaMaxY + subtitleAreaMinY) / 2 - centerY)/frameHeight
#   if xDistanceFromSubtitleCenter < detectionThreshold and yDistanceFromSubtitleCenter < detectionThreshold:
#     # Correct the ratio
#     c = c.astype("float")
#     c *= ratio
#     c = c.astype("int")
#     subtitleContours.append(c)
averageColor = blurred[:, :].mean()

if averageColor < screenAllBlackThreshold:
  mask = np.zeros((frameHeight,frameWidth), np.uint8)

  # White out the bottom part of the screen
  mask[int(subtitleAreaMinY * frameHeight):frameHeight,:] = 255

# elif len(subtitleContours) > 0:
#   frame = cv.drawContours(frame, subtitleContours, -1, (0,255,0), 3)
frame = cv.inpaint(frame, mask, 3, cv.INPAINT_TELEA)

cv.imshow('image',frame)
cv.waitKey(0)
cv.destroyAllWindows()
