import numpy
import cv2
import sys

sys.path.insert(0,"/home/mj/workspace/py-faster-rcnn/tools")

from get_plates_location import PositionDetector 

class PlateDetector:
	def __init__(self):
		print "plate_detector module created!"
		self.position_detector = PositionDetector()
	def find_location_of_plate(self, image):
		print 'toooodooooo'
		bboxes = self.position_detector.detect(image)
		return bboxes
