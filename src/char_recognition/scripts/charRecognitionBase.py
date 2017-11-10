#!/usr/bin/env python

import rospy
from charRecognition import CharRecognizer
from cv_bridge import CvBridge, CvBridgeError
import cv2

from system_messages.msg import Image
from system_messages.msg import Plates
from system_messages.msg import Plate
from geometry_msgs.msg import Point

class CharRecognizerBase(CharRecognizer):
	def __init__(self):
		CharRecognizer.__init__(self)
		self.bridge = CvBridge()
		rospy.init_node('char_recognition_node', anonymous=True)
		image_subscriber = rospy.Subscriber("/image", Image)
		plates_subscriber = rospy.Subscriber("/plates", Plates)
		ts = message_filters.TimeSynchronizer([image_subscriber, plates_subscriber], 10)
		ts.registerCallback(on_data_fully_received)

	def on_data_fully_received(self, image, plates):
		print 'khar!'

if __name__ == '__main__':
	charRecognizer = CharRecognizerBase()
	rospy.spin()
