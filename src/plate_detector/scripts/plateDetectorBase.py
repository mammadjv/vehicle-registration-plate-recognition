#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from plateDetector import PlateDetector

class PlateDetectorBase(PlateDetector):
	def __init__(self):
		PlateDetector.__init__(self)
		rospy.init_node('plate_detector_node', anonymous=True)
		rospy.Subscriber("chatter", String, self.on_image_received)

if __name__ == '__main__':
	plateDetector = PlateDetectorBase()
	rospy.spin()
