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
#		rospy.init_node('plate_detector_node', anonymous=True)
		self.image_subscriber = rospy.Subscriber("/image", ImageMsg, self.on_image_received)
		self.plates_publisher = rospy.Publisher('/plates', Plates, queue_size=1000)
		self.cycle_complete_publisher = rospy.Publisher('/cycle_completed',Bool,queue_size = 1)
		self.r = rospy.Rate(10)
	def on_image_received(self, image):
		rgb_image = CvBridge().imgmsg_to_cv2(image.rgb, "bgr8")
		scharred_image = CvBridge().imgmsg_to_cv2(image.scharred, "mono8")
#		print str(image.index) + "   index " 
#		print rgb_image.__class__
#		cv2.imshow('rgb',rgb_image)
#		cv2.waitKey(1)
#		print "received"
#		cycle_completed_msg = Bool()
#                cycle_completed_msg.data = True
 #               self.cycle_complete_publisher.publish(cycle_completed_msg)
#		return
#		print rgb_image.shape
#		bboxes = self.find_location_of_plate(rgb_image)
		bboxes = list()
		bboxes.append([1 , 2 , 3, 4])
#		bboxes = None
		if(len(bboxes) == 0):
#			print "no boudning box extracted"
			cycle_completed_msg = Bool()
			cycle_completed_msg.data = True
			self.cycle_complete_publisher.publish(cycle_completed_msg)
		else:
#			print len(bboxes)
			plates_msg = Plates()
			for bbox in bboxes:
#				print bbox
				plate_msg = Plate()
				plate_msg.top_left.x = bbox[0]
				plate_msg.top_left.y = bbox[1]
				plate_msg.down_right.x = bbox[2]
				plate_msg.down_right.y = bbox[3]
				plates_msg.plates.append(plate_msg)
			self.plates_publisher.publish(plates_msg)
#		self.r.sleep()

if __name__ == '__main__':
	rospy.init_node('plate_detector_node', anonymous=True)
	plateDetector = PlateDetectorBase()
	rospy.spin()
