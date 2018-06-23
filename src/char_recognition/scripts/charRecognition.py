import numpy
import cv2
import sys
from operator import itemgetter, attrgetter
from pattern_perceptor import PatternPerceptor
import time
import numpy as np
import ocr as ocr


dictionary = {'0':'ein' , '1':'1' , '2':'2', '3':'3', '4':'4', '5':'5' , '6':'6', '7':'7', '8':'8', '9':'9' , '10':'lam' , '11':'sin', '12':'be', '13':'ghaf', '14':'mim', '15':'ta', '16':'dal', '17':'he', '18':'nun', '19':'jim', '20':'sad', '21':'ye'}
inverse_dictionary = {'ein':0 , '1':1 , '2':2, '3':3, '4':4, '5':5 , '6':6, '7':7, '8':8, '9':9 , 'lam':10 , 'sin':11, 'be':12, 'ghaf':13, 'mim':14, 'ta':15, 'dal':16, 'he':17, 'nun':18,'jim':19, 'sad':20, 'ye':21}

kernel5x1 = np.ones((5,5),np.uint8)

class CharRecognizer:
	def __init__(self):
		self.i = 0
		print "char_recognition module created!"
		## path to caffemodel and prototxt files
		self.pattern_perceptor = PatternPerceptor('/home/mj/datasets/ocr_data/train/deploy.prototxt', '/home/mj/datasets/ocr_data/train/numbers.caffemodel')

	def find_char_sequences(self, image, plates_location):
		char_list = list()
		croped_images = list()
		for plate in plates_location:
			plate_image = image[plate['y_begin']:plate['y_end'], plate['x_begin']:plate['x_end']]
			plate_image = cv2.resize(plate_image,(300,120))
			bounding_rects, plate_image, thresh = self.find_bounding_rects(plate_image)
			draw_image = plate_image.copy()
			
			if (len(bounding_rects) < 8):
				continue
			self.find_chars_type(bounding_rects, plate_image)
			for cnt in bounding_rects:
				cnt['type'] = dictionary[str(cnt['type'])]
				x_begin = cnt['x_begin']
				y_begin = cnt['y_begin']
				x_end = cnt['x_end']
				y_end = cnt['y_end']
				if(cnt['type'] == '4' or cnt['type'] == 'ein'):
					sub_section = thresh[y_begin:y_end, x_begin:x_end]
					sub_section = cv2.erode(sub_section,kernel5x1,iterations = 1)
					down_side = sub_section[(sub_section.shape[0]/2):sub_section.shape[0],(sub_section.shape[1])-10:(sub_section.shape[1])]
					whites = np.where(down_side == 255)
					if(np.size(whites[0]) < 8):
						cnt['type'] = '4'
					else:
						cnt['type'] = 'ein'
				print cnt['type'] , cnt['prob']
#				rgb_sub = draw_image[y_begin:y_end, x_begin:x_end]
#				cv2.putText(draw_image,cnt['type'],(cnt['x_begin'],cnt['y_end']), cv2.FONT_HERSHEY_SIMPLEX, 0.8,(255,255,255),3,cv2.LINE_AA)
#				draw_image[y_begin:y_end, x_begin:x_end] = rgb_sub
			selected_centers = list()
			selected_center_index = 0
			max_prob = 0
			i = 0
			for cnt in bounding_rects:
				if(i == len(bounding_rects)-1 and inverse_dictionary[cnt['type']] == 1):
					cnt['type'] = 'None'
					continue
				if(i == len(bounding_rects)-1):
					if(cnt['type'] == 'ein'):
						cnt['type'] = '6'
				if(inverse_dictionary[cnt['type']] ==  0 or inverse_dictionary[cnt['type']] > 9):
					if(cnt['prob'] > max_prob):
						max_prob = cnt['prob']
						selected_center_index = i
				i = i + 1
			if(selected_center_index < 2 or selected_center_index > len(bounding_rects)-5):
				continue
			bounding_rects = bounding_rects[selected_center_index-2:selected_center_index+6]
			for cnt in bounding_rects:
				if(cnt['type'] == None):
					continue
				x_begin = cnt['x_begin']
				y_begin = cnt['y_begin']
				x_end = cnt['x_end']
				y_end = cnt['y_end']
#				cv2.rectangle(draw_image,(x_begin,y_begin), (x_end,y_end),(255,0,255),1)
				rgb_sub = draw_image[y_begin:y_end, x_begin:x_end]
				cv2.putText(draw_image,cnt['type'],(cnt['x_begin'],cnt['y_end']), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,255,255),3,cv2.LINE_AA)
				draw_image[y_begin:y_end, x_begin:x_end] = rgb_sub

			cv2.imshow('draw', draw_image)
			cv2.waitKey(0)

			char_list.append(bounding_rects)

			croped_images.append(cv2.resize(plate_image,(120,30)))
		return char_list , croped_images

	def find_chars_type(self, bounding_rects, croped_image):
#		print croped_image.shape
		for cnt in bounding_rects:
#			y_begin, y_end , x_begin , x_end = , 
			char_image = croped_image[ cnt['y_begin']:cnt['y_end'], cnt['x_begin']:cnt['x_end']].copy()
			char_type , prob = self.pattern_perceptor.recognize(char_image)
#			print "prob" , prob , char_type , "#########"
			cnt['type'] = char_type
			cnt['prob'] = prob

	def get_contours_bounding_rect(self, contours):
		bounding_rects = []
		for cnt in contours:
	        	x,y,w,h = cv2.boundingRect(cnt)
			bounding_rect = {'x_begin':x , 'y_begin':y, 'x_end':x+w, 'y_end':y+h , 'type':'nothing'}
			bounding_rects.append(bounding_rect)
		return bounding_rects

	def remove_abuse_contours(self, bounding_rects, w_max, image_width, image_height):
		selected_contours = []
		for i in range(len(bounding_rects)-1,-1,-1):
			cnt  = bounding_rects[i]
	        	w = cnt['x_end'] - cnt['x_begin']
	        	h = cnt['y_end'] - cnt['y_begin']
        		if( w < 10 or h < 10 or (w <30 and h < 20) or w > w_max):
				bounding_rects.pop(i)
                		continue
			if( cnt['x_begin'] < 5 or cnt['y_begin'] < 5 or cnt['x_end'] > image_width-5 or cnt['y_end']> image_height-5 or cnt['y_end'] < image_height/2):
				bounding_rects.pop(i)
				continue
		for i in range(len(bounding_rects)-1,-1,-1):
			contour_inside_numbers = 0
			cnt1  = bounding_rects[i]
			selected_j = 0
			for j in range(len(bounding_rects)-1,-1,-1):
				cnt2 = bounding_rects[j]
				if(cnt2['x_begin'] > cnt1['x_begin'] and cnt2['x_end'] < cnt1['x_end'] and cnt2['y_begin'] > cnt1['y_begin'] and cnt2['y_end'] < cnt1['y_end']):
					contour_inside_numbers = contour_inside_numbers + 1
					selected_j = j
			if(contour_inside_numbers == 1):
				bounding_rects.pop(selected_j)
			if(contour_inside_numbers > 1):
				aspect_ratio = float(cnt1['x_end'] - cnt1['x_begin'])/float(cnt1['y_end'] - cnt1['y_begin'])
				if(aspect_ratio > 0.5):
					bounding_rects.pop(i)
		selected_contours = bounding_rects
		return selected_contours	


	def find_bounding_rects(self, image):
		bounding_rects, image, thresh = ocr.get_best_contours(image)
		return bounding_rects, image, thresh
