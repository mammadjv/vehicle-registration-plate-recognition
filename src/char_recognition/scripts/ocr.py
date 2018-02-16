import cv2
import numpy as np

image = cv2.imread('/home/mohammad/Pictures/plate_2.png')
#image = cv2.resize(image,(0,0), fx = 4 , fy = 3)
width_0 =  image.shape[1]
height_0 = image.shape[0]
image = cv2.resize(image,(370,83))
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
kernel = np.ones((3,3),np.uint8)

gray = cv2.erode(gray,kernel,iterations = 1)
gray = cv2.dilate(gray,kernel,iterations = 1)
gray = cv2.dilate(gray,kernel,iterations = 1)
gray = cv2.erode(gray,kernel,iterations = 1)
gray = cv2.erode(gray,kernel,iterations = 1)
gray = cv2.dilate(gray,kernel,iterations = 1)
gray = cv2.erode(gray,kernel,iterations = 1)

#gray = cv2.GaussianBlur(gray, (3, 3), 0)
#ret,thresh = cv2.threshold(gray,130,255,cv2.THRESH_BINARY_INV)
#thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
#thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2)

#thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

#kernel = np.ones((3,3),np.uint8)

#thresh = cv2.erode(thresh,kernel,iterations = 1)
#thresh = cv2.dilate(thresh,kernel,iterations = 1)
#thresh = cv2.dilate(thresh,kernel,iterations = 1)
#thresh = cv2.erode(thresh,kernel,iterations = 1)
#thresh = cv2.erode(thresh,kernel,iterations = 1)
#thresh = cv2.dilate(thresh,kernel,iterations = 1)
#thresh = cv2.erode(thresh,kernel,iterations = 1)

cv2.imshow('first_thresh' , gray)
#gray = cv2.resize(gray ,(180,40))
#gray = cv2.resize(gray,(370,83))
#cv2.imshow('second_thresh' , thresh)
thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,11,2)
#thresh = cv2.dilate(thresh,kernel,iterations = 1)
#thresh = cv2.blur(thresh, (3, 3), 0)
#thresh = cv2.blur(thresh, (3, 3), 0)
#thresh = cv2.resize(thresh, (500,300))
#thresh = cv2.resize(thresh,(width_0,height_0))
#edged = cv2.Canny(thresh, 100, 150 ,0)
#thresh = cv2.resize(thresh,(370,83))

#thresh = cv2.erode(thresh,kernel,iterations = 1)
#thresh = cv2.dilate(thresh,kernel,iterations = 1)
#thresh = cv2.erode(thresh,kernel,iterations = 1)
#thresh = cv2.adaptiveThreshold(thresh,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2)


contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
for cnt in contours :
#	print cnt
#	print "@@@@"
#	ellipse = cv2.fitEllipse(cnt)
#	cv2.ellipse(image,ellipse,(0,255,0),2)

	x,y,w,h = cv2.boundingRect(cnt)
#	cv2.drawContours(image, [cnt], 0, (0,255,0), 3)
	cv2.rectangle(image,(x,y),(x+w,y+h),(255,255,0),2)

cv2.imshow('plate', thresh)
#cv2.imshow('edged', edged)
cv2.imshow('rgb', image)
cv2.waitKey(0)
