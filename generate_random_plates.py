import cv2
import numpy as np
from os import listdir
from os.path import isfile, join
import sys
from operator import itemgetter
from random import randint
from random import shuffle
import random
import struct


def hex2rgb(rgb):
    return struct.unpack('BBB', rgb.decode('hex'))

def rgb2hex(rgb):
    return struct.pack('BBB',*rgb).encode('hex')

def get_annotation(annots,image_name):
	for annot in annots:
		info = annot[0]
		if(info['image'] == image_name):
			return annot
	return None

def get_contours_bounding_rect(contours):
	bounding_rects = []
	for cnt in contours:
	        x,y,w,h = cv2.boundingRect(cnt)
		bounding_rect = {'x_begin':x , 'y_begin':y, 'x_end':x+w, 'y_end':y+h}
		bounding_rects.append(bounding_rect)
	return bounding_rects

def remove_abuse_contours(bounding_rects, w_max, image_width, image_height):
	selected_contours = []
	for i in range(len(bounding_rects)-1,-1,-1):
		cnt  = bounding_rects[i]
	        w = cnt['x_end'] - cnt['x_begin']
        	h = cnt['y_end'] - cnt['y_begin']
        	if( w < 10 or h < 10):
			bounding_rects.pop(i)
                	continue
		if(cnt['y_begin'] > image_height/2 or cnt['y_end'] < image_height/2 or cnt['x_begin'] > image_width/2 or cnt['x_end'] < image_width/2):
			bounding_rects.pop(i)
			continue
	selected_contours = bounding_rects
	return selected_contours

def get_contour(image, cnt):
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	kernel = np.ones((3,3),np.uint8)
	
#	gray = cv2.erode(gray,kernel,iterations = 1)
#	gray = cv2.dilate(gray,kernel,iterations = 1)
#	gray = cv2.dilate(gray,kernel,iterations = 1)
#	gray = cv2.erode(gray,kernel,iterations = 1)
#	gray = cv2.erode(gray,kernel,iterations = 1)
#	gray = cv2.dilate(gray,kernel,iterations = 1)
#	gray = cv2.erode(gray,kernel,iterations = 1)

#	ret,thresh = cv2.threshold(gray,80,255,cv2.THRESH_BINARY_INV)
	#thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
	#thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2)
	#thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#	cv2.imshow('gray_open_closed' , image)
	thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,15,2)

#	thresh = cv2.erode(thresh,kernel,iterations = 1)
#	thresh = cv2.dilate(thresh,kernel,iterations = 1)

	__, contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	bounding_rects = get_contours_bounding_rect(contours)
	bounding_rects = remove_abuse_contours(bounding_rects, thresh.shape[1]/2,thresh.shape[1],thresh.shape[0])
	if(len(bounding_rects) > 0):
		sample_contour = bounding_rects[0]
		return [thresh[sample_contour['y_begin']:sample_contour['y_end'], sample_contour['x_begin']:sample_contour['x_end']] , image[sample_contour['y_begin']:sample_contour['y_end'], sample_contour['x_begin']:sample_contour['x_end']]]
	return  None 

def get_random_image(image, desired_list, cnt):
	while(1==1):
		num_index = random.sample(xrange(0,len(desired_list)+1), 1)[0]
		number_image = cv2.imread(desired_list[num_index])
		number_image = cv2.resize(number_image,(cnt['x_end']-cnt['x_begin'],cnt['y_end']-cnt['y_begin']))
		generated_images = get_contour(number_image,cnt)
#		print generated_images
		if(generated_images != None):
			return generated_images
#		cv2.imshow('image',colored_image_croped)
#		cv2.imshow('thresh',thresh_image_croped)
#		cv2.waitKey(0)




def adjust_gamma(image, gamma=1.0):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
 
	# apply gamma correction using the lookup table
	return cv2.LUT(image, table)


pic_path = "/home/mohammad/Documents/char_analyzer/1/sample_plates_1/"
text_file = open('/home/mohammad/Documents/char_analyzer/1/annotation_new_1.txt','r')


pic_files = [f for f in listdir(pic_path) if isfile(join(pic_path, f)) and f.endswith(".jpg")]

lines = text_file.readlines()
annots = []
for line in lines:
	value = eval(line)
	annots.append(value)
text_file.close()

#sorted_list = []
#print annots
#for annot in annots:
#	sortedlist = sorted(annot , key=lambda elem: "%02d" % (elem['x_begin'])
#	newlist = sorted(annot, key=lambda k: k['x_begin'])
#	sorted_list.append(newlist)
#	newtext.write("%s\n" % newlist)
#	print newlist

#newlist = sorted(annots, key=lambda k: k['x_begin']) 

#print newlist
#sys.exit()
numbers_path = '/home/mohammad/Documents/char_analyzer/classified_numbers/'
chars_path = '/home/mohammad/Documents/char_analyzer/classified_chars/'

number_folders = listdir(numbers_path)
numbers = []
for number_folder in number_folders:
	same_numbers = listdir(numbers_path+number_folder)
	for number in same_numbers:
		if(number.endswith(".jpg") or number.endswith(".png")):
			numbers.append(numbers_path+number_folder+'/'+number)

shuffle(numbers)


char_folders = listdir(chars_path)
chars = []
for char_folder in char_folders:
	same_chars = listdir(chars_path+char_folder)
	for char in same_chars:
		if(char.endswith(".jpg") or char.endswith(".png")):
			chars.append(chars_path+char_folder+'/'+char)

shuffle(chars)

for plate_pic in pic_files:
	plate = cv2.imread(pic_path+plate_pic)
	annot = get_annotation(annots,plate_pic)
	print plate_pic
	image = plate
	i = 0
	black_code = ""
	white_code = ""
	for cnt in annot:
		if(i == 0):
			image = plate
			black_code = hex2rgb(cnt['black_code'])[::-1]
			print str(cnt['black_code']) + '   black_code'
			white_code = hex2rgb(cnt['white_code'])[::-1]
			print str(cnt['white_code']) + '   white_code'
			image = cv2.resize(image,(370,83))
		else:
			x_begin = cnt['x_begin']
			y_begin = cnt['y_begin']
			x_end = cnt['x_end']
			y_end = cnt['y_end']
#			cv2.rectangle(image,(x_begin,y_begin),(x_end,y_end),(0,(y_end*y_begin)%255,(x_begin*x_end)%255),1)
			sample_thresh = plate
			sample_colored = plate
			if(i != 3):
				[sample_thresh, sample_colored] = get_random_image(image, numbers, cnt)
			else:
				[sample_thresh, sample_colored] = get_random_image(image, chars, cnt)
			white_positions =  np.where((sample_thresh == 255))
			black_positions =  np.where((sample_thresh == 0))
			sample_colored[white_positions] = black_code
			sample_colored[black_positions] = white_code
			sample_colored = cv2.resize(sample_colored,(x_end - x_begin,y_end-y_begin))
			image[cnt['y_begin']:cnt['y_end'],cnt['x_begin']:cnt['x_end']] = sample_colored
#			cv2.imshow('thresh',sample_thresh)
#			cv2.imshow('colored',sample_colored)
#			cv2.waitKey(2)
		i = i + 1
#	for gamma in np.arange(0.5, 1.7, 0.5):
		# ignore when gamma is 1 (there will be no change to the image)
#		if gamma == 1:
#			continue
		# apply gamma correction and show the images
#		gamma = gamma if gamma > 0 else 0.1
#		adjusted = adjust_gamma(image, gamma=gamma)
#		cv2.putText(adjusted, "g={}".format(gamma), (10, 30),
#		cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
#		cv2.imshow("Images", np.hstack([image, adjusted]))
#		cv2.imwrite(pic_path+image_name, adjusted)
#		cv2.waitKey(0)
#	print random.sample(xrange(1,50), 48)

	cv2.imshow('rgb', image)
	cv2.waitKey(0)
sys.exit()
image = None

