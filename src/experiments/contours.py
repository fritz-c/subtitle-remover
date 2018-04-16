import numpy as np
import cv2 as cv

# Load a color image
frame = cv.imread('still.jpg',1)

grayFrame = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
grayFrame = np.float32(grayFrame)

# lower_black = np.array([0,0,0])
# upper_black = np.array([7,7,7])
# Threshold the HSV image to get only blue colors
# thresh = cv.inRange(frame, lower_black, upper_black)
_,thresh = cv.threshold(cv.cvtColor(frame, cv.COLOR_RGB2GRAY),10,255,cv.THRESH_BINARY_INV)

# Invert?
# thresh = cv.bitwise_not(thresh)

im2, contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_TC89_KCOS)

withContours = cv.drawContours(frame, contours, -1, (0,255,0), 3)

# Bitwise-AND mask and original image
# res = cv.bitwise_and(frame, frame, mask= thresh)







cv.namedWindow('image', cv.WINDOW_NORMAL)
cv.resizeWindow('image', 600, 480)
# cv.imshow('image', frame)
cv.imshow('image', thresh)
cv.imshow('image', withContours)
# cv.imshow('image', res)
cv.waitKey(0)
cv.destroyAllWindows()
