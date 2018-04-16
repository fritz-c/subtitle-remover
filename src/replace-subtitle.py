import numpy as np
import cv2 as cv
import imutils

detectionThreshold = 0.1
subtitleAreaMinY = 560.0/720.0
subtitleAreaMaxY = 710.0/720.0
subtitleAreaMinX = 107.0/1240.0
subtitleAreaMaxX = 1170.0/1240.0
screenAllBlackThreshold = 35.0

cv.namedWindow('image', cv.WINDOW_NORMAL)
mult = 1
cv.resizeWindow('image', 600*mult, 480*mult)

def draw(frame, out):
  frameHeight, frameWidth, _ = frame.shape

  gray = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
  blurred = cv.GaussianBlur(gray, (7, 7), 0);
  _, mask = cv.threshold(blurred,10,255,cv.THRESH_BINARY_INV)

  averageColor = blurred[:, :].mean()

  if averageColor < screenAllBlackThreshold:
    mask = np.zeros((frameHeight,frameWidth), np.uint8)

    # White out the bottom part of the screen
    mask[int(subtitleAreaMinY * frameHeight):int(subtitleAreaMaxY * frameHeight),:] = 255
  else:
    # Grow the mask to remove the text
    # https://docs.opencv.org/3.4.1/d9/d61/tutorial_py_morphological_ops.html
    kernel = np.ones((50, 50), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_DILATE, kernel)
    kernel = np.ones((40, 40), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_ERODE, kernel)

  mask[0:int(subtitleAreaMinY * frameHeight),:] = 0
  mask[int(subtitleAreaMaxY * frameHeight):int(frameHeight),:] = 0
  mask[:,0:int(subtitleAreaMinX * frameWidth)] = 0
  mask[:,int(subtitleAreaMaxX * frameWidth):int(frameWidth)] = 0

  # https://docs.opencv.org/3.4.1/df/d3d/tutorial_py_inpainting.html
  frame = cv.inpaint(frame, mask, 3, cv.INPAINT_TELEA)

  cv.imshow('image',frame)
  out.write(frame)


cap = cv.VideoCapture('../shared/video.mp4')
# cap = cv.VideoCapture('../shared/fade.mp4')

# Use the same codec as the input video
fourcc = int(cap.get(cv.CAP_PROP_FOURCC))
width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH));
height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT));
fps = float(cap.get(cv.CAP_PROP_FPS));

out = cv.VideoWriter('../shared/real-output.mp4', fourcc, fps, (width, height))

# skipSeconds = 15
# for x in range(1,int(skipSeconds*fps)):
#   cap.grab()

while(cap.isOpened()):
  ret, frame = cap.read()
  if ret==True:
    draw(frame, out)
  else:
    break
  if cv.waitKey(1) & 0xFF == ord('q'):
    break

cap.release()
out.release()
cv.destroyAllWindows()
