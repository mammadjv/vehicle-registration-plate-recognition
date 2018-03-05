#!/usr/bin/env python

import rospy
from charRecognition import CharRecognizer
from cv_bridge import CvBridge, CvBridgeError
import cv2

from system_messages.msg import Image
from system_messages.msg import Plates
from system_messages.msg import Plate
from geometry_msgs.msg import Point
import message_filters
from message_filters import TimeSynchronizer, Subscriber
from std_msgs.msg import Bool


class CharRecognizerBase(CharRecognizer):
	def __init__(self):
		CharRecognizer.__init__(self)
		self.bridge = CvBridge()
#		rospy.init_node('char_recognition_node', anonymous=True)
		self.cycle_state_publisher = rospy.Publisher('/cycle_completed', Bool, queue_size=10)
		self.image_subscriber = message_filters.Subscriber("/image", Image)
		self.plates_subscriber = message_filters.Subscriber("/plates", Plates)
		self.ts = message_filters.TimeSynchronizer([self.image_subscriber, self.plates_subscriber], 10)
		self.ts.registerCallback(self.on_data_fully_received)

	def on_data_fully_received(self, image, plates_location_msg):
#		print "khar!"
		plates_location = []
		for plate_location in plates_location_msg.plates:
			plate_point = {"x_begin" : plate_location.top_left.x,"y_begin" : plate_location.top_left.y, "x_end" : plate_location.down_right.x, "y_end" : plate_location.down_right.y}
			plates_location.append(plate_point)
		
#		self.find_char_sequences(image, plates_location) 
		cycle_state_msg = Bool()
		cycle_state_msg.data = True
		self.cycle_state_publisher.publish(cycle_state_msg)
#		self.find_char_sequences(image, plates)	

if __name__ == '__main__':
        rospy.init_node('char_recognition_node', anonymous=False)
	charRecognizer = CharRecognizerBase()
	rospy.spin()
