import numpy as np
import cv2 as cv
import imutils

detectionThreshold = 0.1
subtitleAreaMinY = 560.0/720.0
subtitleAreaMaxY = 700.0/720.0
screenAllBlackThreshold = 35.0

cv.namedWindow('image', cv.WINDOW_NORMAL)
mult = 1
cv.resizeWindow('image', 600*mult, 480*mult)

def draw(frame, out):
  frameHeight, frameWidth, _ = frame.shape
  resized = imutils.resize(frame, width=500)
  ratio = frame.shape[0] / float(resized.shape[0])

  gray = cv.cvtColor(resized,cv.COLOR_BGR2GRAY)
  blurred = cv.GaussianBlur(gray, (1, 1), 0);
  _, thresh = cv.threshold(blurred,10,255,cv.THRESH_BINARY_INV)

  contours = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL,
    cv.CHAIN_APPROX_SIMPLE)
  contours = contours[0] if imutils.is_cv2() else contours[1]

  subtitleContours = []
  for c in contours:
    contourMoments = cv.moments(c)
    if contourMoments["m00"] == 0:
      continue;

    centerX = int((contourMoments["m10"] / contourMoments["m00"]) * ratio)
    centerY = int((contourMoments["m01"] / contourMoments["m00"]) * ratio)
    xDistanceFromSubtitleCenter = abs(frameWidth / 2.0 - centerX)/frameWidth
    yDistanceFromSubtitleCenter = abs(frameHeight * (subtitleAreaMaxY + subtitleAreaMinY) / 2 - centerY)/frameHeight
    if xDistanceFromSubtitleCenter < detectionThreshold and yDistanceFromSubtitleCenter < detectionThreshold:

      # Correct the ratio
      c = c.astype("float")
      c *= ratio
      c = c.astype("int")
      subtitleContours.append(c)

  averageColor = blurred[:, :].mean()

  if averageColor < screenAllBlackThreshold:
    mask = np.zeros((frameHeight,frameWidth), np.uint8)

    # White out the bottom part of the screen
    mask[int(subtitleAreaMinY * frameHeight):int(subtitleAreaMaxY * frameHeight),:] = 255

    frame = cv.inpaint(frame, mask, 3, cv.INPAINT_TELEA)
  elif len(subtitleContours) > 0:
    c = subtitleContours[0]
    contours = np.array(c)
    mask = np.zeros((frameHeight,frameWidth), np.uint8)
    cv.fillPoly(mask, pts =[contours], color=(255,255,255))

    # Black out the top part of the screen in the mask
    mask[0:int(subtitleAreaMinY * frameHeight),:] = 0
    mask[int(subtitleAreaMaxY * frameHeight):frameHeight,:] = 0

    # Grow the mask to ensure the black of the subtitle is covered by the mask
    # https://docs.opencv.org/3.4.1/d9/d61/tutorial_py_morphological_ops.html
    kernel = np.ones((10, 10), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_DILATE, kernel)

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
