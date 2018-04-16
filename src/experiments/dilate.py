import numpy as np
import cv2 as cv

# Load an color image in grayscale
img = cv.imread('./mask.png',1)

kernel = np.ones((50,50),np.uint8)
changed = cv.morphologyEx(img, cv.MORPH_DILATE, kernel)
# cv.imwrite('messigray.png',img)

cv.namedWindow('image', cv.WINDOW_NORMAL)
cv.imshow('image',changed)
cv.waitKey(0)
cv.destroyAllWindows()
