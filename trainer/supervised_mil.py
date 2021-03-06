# -*- coding: utf-8 -*-
# MIT License
# 
# Copyright (c) 2018 ZhicongYan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

import os
import sys
import queue
import threading
import numpy as np

sys.path.append('.')
sys.path.append('../')

import tensorflow as tf

from validator.validator import get_validator

from .base_trainer import BaseTrainer 

class SupervisedMILTrainer(BaseTrainer):
	'''	Supervised Trainer for Multiple Instance Learning,
	the input data is a bag of images and corresponding label,
	it trains the model with a bag and a label per step,

	The difference between SupervisedTrainer and SupervisedMILTrainer is that
	SupervisedMILTrainer do not need to group the input data into a batch
		
	'''
	def __init__(self, config, model, sess):
		super(SupervisedMILTrainer, self).__init__(config, model, sess)

		self.config = config
		self.model = model

		self.dataset_phase = self.config.get('dataset phase', 'train')

		self.nb_threads = int(self.config.get('nb reading threads', 4))
		self.buffer_depth = int(self.config.get('buffer depth', 50))
		self.train_data_queue = queue.Queue(maxsize=self.buffer_depth)


	def train(self, sess, dataset, model):
		
		self.train_initialize(sess, model)

		# start threads for read data
		self.coord = tf.train.Coordinator()
		threads = [threading.Thread(target=self.read_data_loop, 
								args=(self.coord, dataset, self.train_data_queue, self.dataset_phase, 'supervised', self.nb_threads))]
		for t in threads:
			t.start()

		while True:
			epoch, x_bag, y_label = self.train_data_queue.get()
			step = self.train_inner_step(epoch, model, dataset, x_bag, y_label)

			if self.train_data_queue.empty() and step % 100 == 0:
				print('info : train data buffer empty')
			if step > int(self.config['train steps']):
				break

		# join all thread when in multi thread model
		self.coord.request_stop()
		while not self.train_data_queue.empty():
			epoch, x_bag, y_label = self.train_data_queue.get()
		self.train_data_queue.task_done()
		self.coord.join(threads)

