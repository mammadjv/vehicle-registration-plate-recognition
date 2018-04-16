#!/usr/bin/pythom
import numpy as np
import cv2
import time
import caffe

class PatternPerceptor:
        def __init__(self, model, trainedfile):
		print "pattern perceptor module added"
		self.net = caffe.Net(model, trainedfile, caffe.TEST)
#		self.trainedfile = trainedfile
		self.transformer = caffe.io.Transformer({'data': self.net.blobs['data'].data.shape})
		self.transformer.set_transpose('data', (2,0,1))  # move image channels to outermost dimension
	# transformer.set_mean('data', mu)            # subtract the dataset-mean value in each channel
		self.transformer.set_mean('data', np.asarray([215,215,215]))         # subtract the dataset-mean value in each channel
		self.transformer.set_raw_scale('data', 255)      # rescale from [0, 1] to [0, 255]
		self.transformer.set_channel_swap('data', (2,1,0))  # swap channels from RGB to BGR


	def recognize(self,source):
		caffe.set_mode_gpu()
		caffe.set_device(0)
		start = time.time()
#		image = caffe.io.load_image('/home/mj/datasets/ocr_data/train/3/6.jpg')
		image = source
		image = image / 255.
		image = image[:,:,(2,1,0)]

		transformed_image = self.transformer.preprocess('data', image)	
		# copy the image data into the memory allocated for the net
		self.net.blobs['data'].data[...] = transformed_image
		### perform classification
		output = self.net.forward()
#		print('time ' + str(time.time() - start))

		output_prob = output['prob'][0]  # the output probability vector for the first image in the batch

		return output_prob.argmax() , output_prob[output_prob.argmax()][0][0]
