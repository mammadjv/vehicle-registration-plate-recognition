#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from system_messages.msg import Image
from system_messages.msg import Plates
from system_messages.msg import Plate
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
#		cv2.imshow('rgb',rgb_image)
#		cv2.waitKey(1)
		print "image received!"
		bboxes = self.find_location_of_plate(image)
		plates_msg = Plates()
		for bbox in bboxes:
			plate_msg = Plate()
			plate_msg.top_left.x = bbox[0]
			plate_msg.top_left.y = bbox[1]
			plate_msg.down_right.x = bbox[2]
			plate_msg.down_right.y = bbox[3]
			plates_msg.append(plate_msg)
		plate_publisher.publish(plates_msg)

if __name__ == '__main__':
	plateDetector = PlateDetectorBase()
	rospy.spin()
