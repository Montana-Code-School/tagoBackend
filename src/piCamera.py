import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
from zones import Zone

def nothing(x):
    pass

# setup variables
imageNumber = 1
saveImage = True
zone1 = Zone()

# setup camera
camera = PiCamera()
camera.vflip = True
camera.hflip = True
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera)

# setup background subtractor
fgbg = cv2.createBackgroundSubtractorMOG2(varThreshold=80, detectShadows=True)

# setup window
cv2.namedWindow('image')
cv2.setMouseCallback('image', zone1.setSquare)

# setup blank heatmap
heatMap = np.zeros((480, 640), dtype=np.uint8)

time.sleep(0.1)

for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
    image = frame.array

    mask = fgbg.apply(image, 1)

    heatMap = cv2.addWeighted(heatMap, 0.97, mask, 0.03, 0)

    heatMap_color = cv2.applyColorMap(heatMap, cv2.COLORMAP_JET)

    if zone1.rectReady == True:
        frame = zone1.drawSquare(image)

    while time.localtime().tm_sec % 5 == 0:
        if saveImage == True:
            cv2.imwrite('./public/img/area' + str(imageNumber) + '.jpg', heatMap_color)
            zone1.getRoiValue(heatMap)
            saveImage = False
            imageNumber += 1
            print "Saved Image"

    saveImage = True

    cv2.imshow('image', image)
    cv2.imshow('mask', mask)
    cv2.imshow('heatmap', heatMap_color)
    rawCapture.truncate(0)

    if cv2.waitKey(1) & 0xff == ord('q'):
        break

cv2.destroyAllWindows()
