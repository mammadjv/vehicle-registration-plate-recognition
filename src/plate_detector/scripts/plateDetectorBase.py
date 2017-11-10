#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from system_messages.msg import Image
from system_messages.msg import Plates
from plateDetector import PlateDetector
from cv_bridge import CvBridge, CvBridgeError
import cv2

class PlateDetectorBase(PlateDetector):
	def __init__(self):
		PlateDetector.__init__(self)
		rospy.init_node('plate_detector_node', anonymous=True)
		image_subscriber = rospy.Subscriber("/image", Image, self.on_image_received)
		plates_publisher = rospy.Publisher('/plates', Plates, queue_size=10)

	def on_image_received(self, image):
		rgb_image = CvBridge().imgmsg_to_cv2(image.rgb, "bgr8")
		scharred_image = CvBridge().imgmsg_to_cv2(image.scharred, "mono8")
		cv2.imshow('rgb',rgb_image)
		cv2.waitKey(1)
		print "image received!"
		self.find_location_of_plate(image)

if __name__ == '__main__':
	plateDetector = PlateDetectorBase()
	rospy.spin()
