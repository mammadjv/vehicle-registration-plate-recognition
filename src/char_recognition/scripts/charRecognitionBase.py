#!/usr/bin/env python

import rospy
from charRecognition import CharRecognizer
from cv_bridge import CvBridge, CvBridgeError
import cv2
import numpy as np
from system_messages.msg import ImageMsg
from system_messages.msg import Plates
from sensor_msgs.msg import Image
from system_messages.msg import Plate
from geometry_msgs.msg import Point
import message_filters
from message_filters import TimeSynchronizer, Subscriber
from std_msgs.msg import Bool


class CharRecognizerBase(CharRecognizer):
	def __init__(self):
		CharRecognizer.__init__(self)
		self.bridge = CvBridge()
		self.cycle_state_publisher = rospy.Publisher('/cycle_completed', Bool, queue_size=1)
		self.plates_image_publisher = rospy.Publisher('/plates_image', Image, queue_size=1)
		self.image_subscriber = message_filters.Subscriber("/image", ImageMsg)
		self.plates_subscriber = message_filters.Subscriber("/plates", Plates)
		self.ts = message_filters.TimeSynchronizer([self.image_subscriber, self.plates_subscriber], 1)
		self.ts.registerCallback(self.on_data_fully_received)

	def on_data_fully_received(self, image, plates_location_msg):
		plates_location = []
		for plate_location in plates_location_msg.plates:
			plate_point = {"x_begin" : plate_location.top_left.x,"y_begin" : plate_location.top_left.y, "x_end" : plate_location.down_right.x, "y_end" : plate_location.down_right.y}
			plates_location.append(plate_point)
		
		char_list , croped_images = self.find_char_sequences(CvBridge().imgmsg_to_cv2(image.rgb, "bgr8"), plates_location)
		cycle_state_msg = Bool()
		cycle_state_msg.data = True
		if(len(croped_images) == 0):
			self.cycle_state_publisher.publish(cycle_state_msg)
			return
		plates_image = croped_images[0]
		i = 0
		for croped in croped_images:
			if(i == 0):
				i = i + 1
				continue
			plates_image = np.concatenate((plates_image, croped), axis=0)
			i = i + 1
		self.plates_image_publisher.publish(self.bridge.cv2_to_imgmsg(plates_image, "bgr8"))
		self.cycle_state_publisher.publish(cycle_state_msg)

if __name__ == '__main__':
        rospy.init_node('char_recognition_node', anonymous=True)
	charRecognizer = CharRecognizerBase()
	rospy.spin()
