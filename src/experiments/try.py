import numpy as np
import cv2 as cv

# Load an color image in grayscale
img = cv.imread('messi5.jpg',0)

cv.imwrite('messigray.png',img)

# cv.namedWindow('image', cv.WINDOW_NORMAL)
# cv.imshow('image',img)
# cv.waitKey(0)
# cv.destroyAllWindows()
