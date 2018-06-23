import cv2
import numpy as np
from os import listdir
from os.path import isfile, join
import time
from matplotlib import pyplot as plt
import math
import imutils


kernel5x1 = np.ones((5,1),np.uint8)
kernel5x5 = np.ones((5,5),np.uint8)
kernel5x3 = np.ones((5,3),np.uint8)
kernel3x5 = np.ones((3,5),np.uint8)
kernel3x3 = np.ones((3,3),np.uint8)
kernel3x1 = np.ones((3,1),np.uint8)
kernel1x3 = np.ones((1,3),np.uint8)
kernel1x5 = np.ones((1,5),np.uint8)
kernel35x1 = np.ones((39,1),np.uint8)
kernel1x35 = np.ones((1,39),np.uint8)
kernel9x9 = np.ones((9,9),np.uint8)
kernel11x11 = np.ones((11,11),np.uint8)




def find_upper_down_contour(thresh):
	__, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	selected_boundaries = list()
	upper_contour = None
	down_contour = None
	for cnt in contours:
		x,y,w,h = cv2.boundingRect(cnt)
		if(w < thresh.shape[1]/2):
			continue
		bounding_rect = {'x_begin':x , 'y_begin':y, 'x_end':x+w, 'y_end':y+h, 'cnt':cnt , 'type':'None'}
		selected_boundaries.append(bounding_rect)
	selected_boundaries = sorted(selected_boundaries, key=lambda k: k['y_begin'])
	if(len(selected_boundaries)>0):
		upper_contour = selected_boundaries[0]
		down_contour = selected_boundaries[len(selected_boundaries)-1]
		for rect in selected_boundaries:
			if(rect['y_begin'] > upper_contour['y_begin'] and rect['y_begin'] < thresh.shape[0]/2):
				upper_contour = rect
			if(rect['y_begin'] < down_contour['y_begin'] and rect['y_begin'] > thresh.shape[0]/2):
				down_contour = rect
		upper_down_contours = list()
		upper_down_contours.append(upper_contour)
		if(upper_contour['y_begin'] != down_contour['y_begin'] and upper_contour['x_begin'] != down_contour['x_begin']):
			upper_down_contours.append(down_contour)	
		for cnt in upper_down_contours:
			rect = cv2.minAreaRect(cnt['cnt'])
			box = cv2.boxPoints(rect)
			box = np.int0(box)
			box = sorted(box, key=lambda k: k[0])
			begin = (box[0]+box[1])/2
			end = (box[2]+box[3])/2
			degree = int(math.atan2(float(begin[1]-end[1]),float(begin[0]-end[0]))*180/3.14)
			if(degree <0):
				degree = degree + 180
			else:
				degree = degree - 180
			cnt['angle'] = degree
			
		return upper_down_contours
	return list()



def get_contours_bounding_rect(contours):
	bounding_rects = []
	for cnt in contours:
	        x,y,w,h = cv2.boundingRect(cnt)
		bounding_rect = {'x_begin':x , 'y_begin':y, 'x_end':x+w, 'y_end':y+h, 'type': 'None' , 'prob':'-1'}
		bounding_rects.append(bounding_rect)
	return bounding_rects


def is_between(cnt1, cnt2):
	if((cnt1['y_begin'] >= cnt2['y_begin'] and cnt1['y_begin'] <= cnt2['y_end']) or \
	(cnt1['y_begin'] <= cnt2['y_begin'] and cnt1['y_end'] >= cnt2['y_begin']) or \
	(cnt1['y_begin'] >= cnt2['y_begin'] and cnt1['y_end'] <= cnt2['y_end']) or \
	(cnt1['y_begin'] <= cnt2['y_begin'] and cnt1['y_end'] >= cnt2['y_end'])):
		return True
	return False

def remove_abuse_contours(thresh_image,bounding_rects, w_max, image_width, image_height):
	selected_contours = []
	for i in range(len(bounding_rects)-1,-1,-1):
		cnt  = bounding_rects[i]
	        w = cnt['x_end'] - cnt['x_begin']
        	h = cnt['y_end'] - cnt['y_begin']
		if(w > image_width/4):
			bounding_rects.pop(i)
			continue
        	if( h < 10):
			bounding_rects.pop(i)
                	continue
        	if( w < 20 and h < 20):
			bounding_rects.pop(i)
                	continue
		if((i < 2 or i == len(bounding_rects)-1) and h > 7*thresh_image.shape[0]/8):
			bounding_rects.pop(i)
			continue
		contour_image = thresh_image[cnt['y_begin']:cnt['y_end'], cnt['x_begin']:cnt['x_end']]
		whites =  float(len(np.where((contour_image == 255))[0]))
		if ((w < image_width/10 and h < image_height/5 and (whites)/(w*h) > 0.1)):
			bounding_rects.pop(i)
			continue
		if (cnt['x_end']  - cnt['x_begin'] < 10):
			bounding_rects.pop(i)
			continue

		if ((cnt['x_begin'] > 3*thresh_image.shape[1]/5 or cnt['x_begin'] < thresh_image.shape[1]/5) and cnt['y_end'] < thresh_image.shape[0]/2):
			bounding_rects.pop(i)
			continue

	## delete full inside contours
	for i in range(len(bounding_rects)-1,-1,-1):
		contour_inside_numbers = 0
		cnt1  = bounding_rects[i]
		selected_j = 0
		for j in range(len(bounding_rects)-1,-1,-1):
			if(i == j):
				continue
			cnt2 = bounding_rects[j]
			if(cnt2['x_begin'] >= cnt1['x_begin'] and cnt2['x_end'] <= cnt1['x_end'] and cnt2['y_begin'] >= cnt1['y_begin'] and cnt2['y_end'] <= cnt1['y_end']):
				contour_inside_numbers = contour_inside_numbers + 1
				selected_j = j
		if(contour_inside_numbers == 1):
			bounding_rects.pop(selected_j)
		if(contour_inside_numbers > 1):
			aspect_ratio = float(cnt1['x_end'] - cnt1['x_begin'])/float(cnt1['y_end'] - cnt1['y_begin'])
			if(aspect_ratio > 0.5):
				bounding_rects.pop(i)

	## delete semi inside contours
	for i in range(len(bounding_rects)-1,-1,-1):
		contour_inside_numbers = 0
		cnt1  = bounding_rects[i]
		selected_j = 0
		for j in range(len(bounding_rects)-1,-1,-1):
			if(i == j):
				continue
			cnt2 = bounding_rects[j]
			if(cnt2['x_begin'] > cnt1['x_begin'] and cnt2['x_begin'] < cnt1['x_end'] and \
#cnt2['x_end'] >= cnt1['x_end'] and\
is_between(cnt1,cnt2) and float(cnt1['x_end']-cnt2['x_begin'])/float(cnt2['x_end']-cnt2['x_begin']) > 0.5):
				cnt1['x_end'] = cnt2['x_begin']

	for i in range(len(bounding_rects)-1,-1,-1):
		cnt  = bounding_rects[i]
		number_of_in_ranges = 0
		for j in range(len(bounding_rects)-1,-1,-1):
			if(i==j):
				continue
			other_cnt = bounding_rects[j]
			if(is_between(cnt, other_cnt) == True):
				number_of_in_ranges = number_of_in_ranges + 1
		if(number_of_in_ranges <7):
			bounding_rects.pop(i)
			continue

	selected_contours = bounding_rects		
	return selected_contours
	
def get_best_contours(image):
	start = time.time()
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.blur(gray,(3,3))
	start = time.time()

	thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,35,2)
	thresh_eroded_1x35 = cv2.erode(thresh,kernel1x35,iterations = 1)
	thresh = thresh - thresh_eroded_1x35
	upper_down_contours = find_upper_down_contour(thresh_eroded_1x35)
	draw_rgb_image = image.copy()
	if(len(upper_down_contours) > 0):

		image = imutils.rotate_bound(image, -upper_down_contours[0]['angle'])
		thresh = imutils.rotate_bound(thresh, -upper_down_contours[0]['angle'])
		gray = imutils.rotate_bound(gray, -upper_down_contours[0]['angle'])
		thresh_eroded_1x35 = imutils.rotate_bound(thresh_eroded_1x35, -upper_down_contours[0]['angle'])
		upper_down_contours = find_upper_down_contour(thresh_eroded_1x35)
		if(len(upper_down_contours) == 2):
			thresh = thresh[upper_down_contours[0]['y_end']:upper_down_contours[1]['y_begin'],0:thresh_eroded_1x35.shape[1]-1].copy()
			draw_rgb_image = image[upper_down_contours[0]['y_end']:upper_down_contours[1]['y_begin'],0:thresh_eroded_1x35.shape[1]-1].copy()
		if(len(upper_down_contours) == 1):
			if(upper_down_contours[0]['y_end'] < thresh_eroded_1x35.shape[0]/2):
				draw_rgb_image = image[upper_down_contours[0]['y_end']:thresh_eroded_1x35.shape[0]-1,0:thresh_eroded_1x35.shape[1]-1].copy()
				thresh = thresh[upper_down_contours[0]['y_end']:thresh_eroded_1x35.shape[0]-1,0:thresh_eroded_1x35.shape[1]-1].copy()
				thresh_eroded_1x35 = thresh_eroded_1x35[upper_down_contours[0]['y_end']:thresh_eroded_1x35.shape[0]-1,0:thresh_eroded_1x35.shape[1]-1].copy()

			else:
				draw_rgb_image = image[1:upper_down_contours[0]['y_begin'],0:thresh_eroded_1x35.shape[1]-1]
				thresh = thresh[1:upper_down_contours[0]['y_begin'],0:thresh_eroded_1x35.shape[1]-1]
				thresh_eroded_1x35 = thresh_eroded_1x35[1:upper_down_contours[0]['y_begin'],0:thresh_eroded_1x35.shape[1]-1]

	thresh[0:1,0:thresh.shape[1]-1] = 0
	thresh[thresh.shape[0]-1:thresh.shape[0],0:thresh.shape[1]-1] = 0

	thresh[0:thresh.shape[0],0:1] = 0
	thresh[0:thresh.shape[0],thresh.shape[1]-1:thresh.shape[1]] = 0

	ret , thresh = cv2.threshold(thresh,254,255,cv2.THRESH_BINARY)

	__, contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	
	bounding_rects = get_contours_bounding_rect(contours)
	bounding_rects = sorted(bounding_rects, key=lambda k: k['x_begin'])
	bounding_rects = remove_abuse_contours(thresh, bounding_rects, thresh.shape[1]/2,thresh.shape[1],thresh.shape[0])

	print time.time() - start
	for cnt in bounding_rects:
		x_begin = cnt['x_begin']
		y_begin = cnt['y_begin']
		x_end = cnt['x_end']
		y_end = cnt['y_end']
		croped = draw_rgb_image[y_begin:y_end , x_begin:x_end]
	for cnt in bounding_rects:
		x_begin = cnt['x_begin']
		y_begin = cnt['y_begin']
		x_end = cnt['x_end']
		y_end = cnt['y_end']
	cv2.imshow('thresh', thresh)
	cv2.namedWindow('thresh',cv2.WINDOW_NORMAL)
	cv2.moveWindow("thresh",10,10)	
	if(len(bounding_rects) < 7):
		return list(), image, image
	return bounding_rects , draw_rgb_image, thresh

	cv2.imshow('thresh', thresh)
	cv2.namedWindow('thresh',cv2.WINDOW_NORMAL)
	cv2.moveWindow("thresh",10,10)

	cv2.imshow('thresh1', thresh_eroded_1x35)
	cv2.namedWindow('thresh1',cv2.WINDOW_NORMAL)
	cv2.moveWindow("thresh1",10,200)

	cv2.imshow('image', image)
	cv2.namedWindow('image',cv2.WINDOW_NORMAL)
	cv2.moveWindow("image",10,400)

	cv2.imshow('draw_rgb_image', draw_rgb_image)
	cv2.namedWindow('draw_rgb_image',cv2.WINDOW_NORMAL)
	cv2.moveWindow("draw_rgb_image",500,10)

	cv2.imshow('gray', gray)
	cv2.namedWindow('gray',cv2.WINDOW_NORMAL)
	cv2.moveWindow("gray",500,200)
	cv2.waitKey(0)
