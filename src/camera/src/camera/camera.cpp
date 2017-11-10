#include <ros/ros.h>
#include <image_transport/image_transport.h>
#include <opencv2/opencv.hpp>
#include <cv_bridge/cv_bridge.h>
#include <iostream>
#include <opencv2/imgproc/imgproc.hpp>
#include <vector>
#include <system_messages/Image.h>

int main(int argc , char **argv){
    ros::init(argc,argv,"camera_node");
    ros::NodeHandle nh;
    ros::Publisher publisher = nh.advertise <system_messages::Image> ("/camera/image",1);
    ros::Rate loopRate(30);

    cv::VideoCapture cap("/home/mohammad/catkin_ws/PersonRecognition/python_scripts/dataset/rgb_2.avi");
    cv::Mat rgb, gray, scharred_image;

    system_messages::Image::Ptr image = boost::make_shared<system_messages::Image>();

    while(nh.ok()){
        // capture and convert the image
	if (!cap.read(rgb))
            break;

        cv::cvtColor(rgb,gray,CV_BGR2GRAY);
        cv::blur(gray, gray,cv::Size(5,5),cv::Point(-1,-1),cv::BORDER_DEFAULT);
        cv::Scharr(gray,scharred_image,CV_8U,0,1,1,0,cv::BORDER_DEFAULT);

        sensor_msgs::ImagePtr rgb_msg = cv_bridge::CvImage(std_msgs::Header(), "bgr8", rgb).toImageMsg();
        sensor_msgs::ImagePtr scharred_msg = cv_bridge::CvImage(std_msgs::Header(),"mono8",scharred_image).toImageMsg();
        image->rgb = *rgb_msg;
        image->scharred = *scharred_msg;
        publisher.publish(image);
        ros::spinOnce();
        loopRate.sleep();
    }
return 0;
}
