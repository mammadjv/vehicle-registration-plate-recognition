#include <ros/ros.h>
#include <image_transport/image_transport.h>
#include <opencv2/opencv.hpp>
#include <cv_bridge/cv_bridge.h>
#include <iostream>
#include <opencv2/imgproc/imgproc.hpp>
#include <vector>
#include <system_messages/Image.h>
#include <std_msgs/Bool.h>

cv::VideoCapture cap("/home/mj/datasets/lprData/20160412-115602.avi");
cv::Mat rgb, gray, scharred_image;

class ImagePubSub{
public:
	ros::Publisher publisher;
	ros::Subscriber sub;
	void cycleCallback(const std_msgs::Bool::ConstPtr& cycle_completed){
                if(cycle_completed->data == true){
                        if (!cap.read(rgb))
                                return;
                        this->publish(rgb);
                }
        };

	ImagePubSub(ros::NodeHandle nh){
	    	publisher = nh.advertise <system_messages::Image> ("/image",1);
    		sub = nh.subscribe("/cycle_completed", 1000, &ImagePubSub::cycleCallback,this);
	};

	void publish(cv::Mat rgb){
	        system_messages::Image::Ptr image = boost::make_shared<system_messages::Image>();
	        cv::cvtColor(rgb,gray,CV_BGR2GRAY);
	        cv::blur(gray, gray,cv::Size(5,5),cv::Point(-1,-1),cv::BORDER_DEFAULT);
        	cv::Scharr(gray,scharred_image,CV_8U,0,1,1,0,cv::BORDER_DEFAULT);
	        sensor_msgs::ImagePtr rgb_msg = cv_bridge::CvImage(std_msgs::Header(), "bgr8", rgb).toImageMsg();
        	sensor_msgs::ImagePtr scharred_msg = cv_bridge::CvImage(std_msgs::Header(),"mono8",scharred_image).toImageMsg();
	        image->rgb = *rgb_msg;
        	image->scharred = *scharred_msg;
        	this->publisher.publish(image);
	};
};

int main(int argc , char **argv){
    ros::init(argc,argv,"camera_node");
    ros::NodeHandle nh;
    ImagePubSub *image_pub_sub = new ImagePubSub(nh);
    if (!cap.read(rgb))
    	return 0;
    image_pub_sub->publish(rgb);
//    ros::spinOnce();
    ros::spin();
return 0;
}
