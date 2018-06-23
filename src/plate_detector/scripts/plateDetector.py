import numpy
import cv2
import sys

#### add absolute path of py_faster_rcnn/tools to PYTHONPATH, in my case, "/home/mj/workspace/py-faster-rcnn/tools"
sys.path.insert(0,"/home/mj/workspace/py-faster-rcnn/tools")

import sys
import _init_paths
from fast_rcnn.config import cfg
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms
from utils.timer import Timer
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
import caffe, os, cv2
import argparse


#### add absolute path of py_faster_rcnn to PYTHONPATH, in my case, "/home/mj/workspace/py-faster-rcnn/"
sys.path.insert(0,"/home/mj/workspace/py-faster-rcnn/")

CLASSES = ('__background__',
                'plate')

NETS = {'vgg16': ('VGG16',
                  'VGG16_faster_rcnn_final.caffemodel'),
        'zf': ('ZF',
                  'ZF_faster_rcnn_final.caffemodel')}


class PlateDetector:
	def __init__(self):
		print "plate_detector module created!"
		#### add model files here, prototxt file is under /path/to/py_faster_rcnn/models/plates/faster_rcnn_alt_opt/
		prototxt = '/home/mj/workspace/py-faster-rcnn/models/plates/faster_rcnn_alt_opt/faster_rcnn_test.pt'
		#### set path to caffe model
                caffemodel = '/home/mj/workspace/py-faster-rcnn/output/default/train/plates_faster_rcnn_final.caffemodel'
                if not os.path.isfile(caffemodel):
                        raise IOError(('{:s} not found.\nDid you run ./data/script/'
'fetch_faster_rcnn_models.sh?').format(caffemodel))

                self.net = caffe.Net(prototxt, caffemodel, caffe.TEST)
                print '\n\nLoaded network {:s}'.format(caffemodel)
                # Warmup on a dummy image
                im = 128 * np.ones((300, 500, 3), dtype=np.uint8)
                for i in xrange(2):
                        an = im_detect(self.net, im)
	def find_location_of_plate(self, image):
		timer = Timer()
                timer.tic()
                scores, boxes = im_detect(self.net, image)
                timer.toc()
                print ('Detection took {:.3f}s for '
                   '{:d} object proposals').format(timer.total_time, boxes.shape[0])

                CONF_THRESH = 0.8
                NMS_THRESH = 0.2
                for cls_ind, cls in enumerate(CLASSES[1:]):
                       cls_ind += 1 # because we skipped background
                       cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
                       cls_scores = scores[:, cls_ind]
                dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
                keep = nms(dets, NMS_THRESH)
                dets = dets[keep, :]
                inds = np.where(dets[:, -1] >= NMS_THRESH)[0]
		bboxes = list()
                if len(inds) == 0:
                        return list()
                for i in inds:
                        bbox = dets[i, :4]
                        score = dets[i, -1]
			bboxes.append(bbox)
                return bboxes

