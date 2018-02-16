import numpy
import cv2
import sys

sys.path.append('./faster_rcnn')

class CharRecognizer:
	def __init__(self):
		print "char_recognition module created!"
	def find_location_of_characters(self, image):
		print 'toooodooooo'
	def find_char_sequences(self, image, plates_location):
		for plate in plates_location:
			plate_image = image[plate['y_begin']:plate['y_end'],plate['y_begin']:plate['y_end']]
