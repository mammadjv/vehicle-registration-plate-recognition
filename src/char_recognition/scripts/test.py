import numpy
import cv2
import sys
from operator import itemgetter, attrgetter
from pattern_perceptor import PatternPerceptor
import time
import numpy as np
import ocr as ocr


pattern_perceptor = PatternPerceptor('/home/mj/datasets/ocr_data/train/deploy.prototxt', '/home/mj/datasets/ocr_data/train/numbers.caffemodel')

image = cv2.imread('/home/mj/datasets/ocr_data/train/3/6.jpg')
output , prob = pattern_perceptor.recognize(image)
print output, prob
