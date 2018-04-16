import numpy as np
import cv2 as cv

def outputChanges(x):
  blockSize = cv.getTrackbarPos('blockSize','image') + 2
  kSize = cv.getTrackbarPos('kSize','image') * 2 + 1
  k = cv.getTrackbarPos('k','image') / 100.0
  thresh = cv.getTrackbarPos('thresh','image') / 100.0
  print(blockSize, kSize, k, thresh)

cv.namedWindow('image', cv.WINDOW_NORMAL)
cv.resizeWindow('image', 600, 480)

# create trackbars for color change
cv.createTrackbar('blockSize','image',0,100,outputChanges)
cv.createTrackbar('kSize','image',0,15,outputChanges)
cv.createTrackbar('k','image',14,100,outputChanges)
cv.createTrackbar('thresh','image',0,100,outputChanges)

# Load a color image
origFrame = cv.imread('still.jpg',1)
frame = origFrame.copy()

while(1):
  cv.imshow('image',frame)
  k = cv.waitKey(2) & 0xFF
  if k == 27 or k == ord('q'):
    break

  # get current positions of four trackbars
  blockSize = cv.getTrackbarPos('blockSize','image') + 2
  kSize = cv.getTrackbarPos('kSize','image') * 2 + 1
  k = cv.getTrackbarPos('k','image') / 100.0
  thresh = cv.getTrackbarPos('thresh','image') / 100.0

  frame = origFrame.copy()
  grayFrame = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
  _, grayFrame = cv.threshold(grayFrame,10,255,cv.THRESH_BINARY_INV)
  grayFrame = np.float32(grayFrame)

  dst = cv.cornerHarris(grayFrame,blockSize,kSize,k)
  #result is dilated for marking the corners, not important
  dst = cv.dilate(dst,None)
  dst = cv.dilate(dst,None)
  dst = cv.dilate(dst,None)
  dst = cv.dilate(dst,None)
  # Threshold for an optimal value, it may vary depending on the image.
  frame[dst>thresh*dst.max()]=[0,0,255]

cv.destroyAllWindows()
