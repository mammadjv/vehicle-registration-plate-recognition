#include <ros/ros.h>
#include <image_transport/image_transport.h>
#include <opencv2/opencv.hpp>
#include <cv_bridge/cv_bridge.h>
#include <iostream>
#include <opencv2/imgproc/imgproc.hpp>
#include <vector>
#include <system_messages/ImageMsg.h>
#include <std_msgs/Bool.h>


// path to test video
cv::VideoCapture cap("/home/mj/datasets/lprData/20160412-115602.avi");
cv::Mat rgb, gray, scharred_image;


class ImagePubSub{
public:
	ros::Publisher publisher;
	ros::Subscriber sub;
	int i;
	std::vector<cv::Mat> captured;
	void cycleCallback(const std_msgs::BoolConstPtr& cycle_completed){
		if( cap.read(rgb)){
			this->publish(rgb);
		}     
        };

	ImagePubSub(ros::NodeHandle nh){
	    	this->publisher = nh.advertise <system_messages::ImageMsg> ("/image",1);
		this->i = 0;
    		this->sub = nh.subscribe("/cycle_completed", 1, &ImagePubSub::cycleCallback,this);
	};

	void publish(cv::Mat img){
		cv::Mat rgb;
		cv::resize(img,rgb,cv::Size(600,400));
	        system_messages::ImageMsg::Ptr image = boost::make_shared<system_messages::ImageMsg>();
	        cv::cvtColor(rgb,gray,CV_BGR2GRAY);
	        cv::blur(gray, gray,cv::Size(5,5),cv::Point(-1,-1),cv::BORDER_DEFAULT);
        	cv::Scharr(gray,scharred_image,CV_8U,0,1,1,0,cv::BORDER_DEFAULT);
	        sensor_msgs::ImagePtr rgb_msg = cv_bridge::CvImage(std_msgs::Header(), "bgr8", rgb).toImageMsg();
        	sensor_msgs::ImagePtr scharred_msg = cv_bridge::CvImage(std_msgs::Header(),"mono8",scharred_image).toImageMsg();
	        image->rgb = *rgb_msg;
			std::cout << this->i << std::endl;
			this->i++;
        	image->scharred = *scharred_msg;
        	this->publisher.publish(image);
	};
};

int main(int argc , char **argv){
    ros::init(argc,argv,"camera_node");
    ros::NodeHandle nh;
    ImagePubSub *image_pub_sub = new ImagePubSub(nh);
	ros::spin();
}
