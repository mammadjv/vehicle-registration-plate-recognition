#include <ros/ros.h>
#include <image_transport/image_transport.h>
#include <opencv2/opencv.hpp>
#include <cv_bridge/cv_bridge.h>
#include <iostream>
#include <opencv2/imgproc/imgproc.hpp>
#include <vector>


using namespace std;
using namespace cv;
using namespace image_transport;

int main(int argc , char **argv){
    ros::init(argc,argv,"camera_node");
    ros::NodeHandle nh;
    ImageTransport it(nh);
    Publisher publisher = it.advertise("/camera/image",1);
    ros::Rate loopRate(30);
    while(nh.ok()){
	std::cout << "khar!\n";
        ros::spinOnce();
        loopRate.sleep();
    }
}

