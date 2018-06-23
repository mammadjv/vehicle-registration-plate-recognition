#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from std_msgs.msg import Bool
from system_messages.msg import ImageMsg
from sensor_msgs.msg import Image
from system_messages.msg import Plates
from system_messages.msg import Plate
from plateDetector import PlateDetector
from cv_bridge import CvBridge, CvBridgeError
import cv2


class PlateDetectorBase(PlateDetector):
	def __init__(self):
		PlateDetector.__init__(self)
		self.image_subscriber = rospy.Subscriber("/image", ImageMsg, self.on_image_received)
		self.plates_publisher = rospy.Publisher('/plates', Plates, queue_size=1000)
		self.cycle_complete_publisher = rospy.Publisher('/cycle_completed',Bool,queue_size = 1)
		self.show_image_publisher = rospy.Publisher('/all_image', Image, queue_size=1)
		self.r = rospy.Rate(10)
		self.bridge = CvBridge()
	def on_image_received(self, image):
		rgb_image = CvBridge().imgmsg_to_cv2(image.rgb, "bgr8")
		scharred_image = CvBridge().imgmsg_to_cv2(image.scharred, "mono8")

		bboxes = self.find_location_of_plate(rgb_image)
		paint_image = rgb_image.copy()
		if(len(bboxes) == 0):
			cycle_completed_msg = Bool()
			cycle_completed_msg.data = True
			self.cycle_complete_publisher.publish(cycle_completed_msg)
		else:
			plates_msg = Plates()
			for bbox in bboxes:
				plate_msg = Plate()
				plate_msg.top_left.x = bbox[0]
				plate_msg.top_left.y = bbox[1]
				plate_msg.down_right.x = bbox[2]
				plate_msg.down_right.y = bbox[3]
				plates_msg.plates.append(plate_msg)
				cv2.rectangle(paint_image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0,255,0), 2)
			self.plates_publisher.publish(plates_msg)
		self.show_image_publisher.publish(self.bridge.cv2_to_imgmsg(paint_image, "bgr8"))

if __name__ == '__main__':
	rospy.init_node('plate_detector_node', anonymous=True)
	plateDetector = PlateDetectorBase()
	rospy.spin()
