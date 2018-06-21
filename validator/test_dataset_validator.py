import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm



class ScatterPlotValidator(object):
	
	def __init__(self, config):
	
		self.assets_dir = config['assets dir']
		self.log_dir = config.get('log dir', 'test')
		self.log_dir = os.path.join(self.assets_dir, self.log_dir)

		self.x_dim = int(config.get('x_dim', 0))
		self.y_dim = int(config.get('y_dim', 1))

		if not os.path.exists(self.log_dir):
			os.mkdir(self.log_dir)

		self.watch_variable = config.get('watch_variable', 'pred')


		# self.generate_method = config.get('generate_method', 'normppf')
		# if self.generate_method == 'normppf':
		# 	# self.generate_method_params = config.get('generate_method_params', '')
		# 	self.nb_samples = config.get('num_samples', 30)


	def validate(self, model, dataset, sess, step):

		x_pos_array = []
		y_pos_array = []
		label_array = []



		for ind, batch_x, batch_y in dataset.iter_test_images():
			

			if self.watch_variable == 'pred':
				y_pred = model.predict(sess, batch_y)

				x_pos_array.append(y_pred[:, self.x_dim])
				y_pos_array.append(y_pred[:, self.y_dim])
				label_array.append(batch_y)

			elif self.watch_variable == 'hidden_dist':
				z_mean, z_log_var = model.hidden_distribution(sess, batch_x)

				x_pos_array.append(
					np.concatenate([
											z_mean[:, self.x_dim:self.x_dim+1], 
									np.exp(z_log_var[:, self.x_dim:self.x_dim+1])
									], axis=1)
				)
				y_pos_array.append(
					np.concatenate([
											z_mean[:, self.y_dim:self.y_dim+1], 
										np.exp(z_log_var[:, self.y_dim:self.y_dim+1])
									], axis=1)
				)
				label_array.append(batch_y)
			else:
				raise Exception("None watch variable named " + self.watch_variable)

		x_pos_array = np.concatenate(x_pos_array, axis=0)
		y_pos_array = np.concatenate(y_pos_array, axis=0)
		label_array = np.concatenate(label_array, axis=0)


		if len(x_pos_array.shape) == 2:
			for i in range(x_pos_array.shape[1]):
				plt.figure(figsize=(6, 6))
				plt.clf()
				plt.scatter(x_pos_array[:, i], y_pos_array[:, i], c=label_array)
				plt.colorbar()
				plt.savefig(os.path.join(self.log_dir, '%07d_%d.png'%(step, i)))

		else:
			plt.figure(figsize=(6, 6))
			plt.clf()
			plt.scatter(x_pos_array, y_pos_array, c=label_array)
			plt.colorbar()
			plt.savefig(os.path.join(self.log_dir, '%07d.png'%step))

		
		# if self.generate_method == 'normppf':
			
		# 	n = self.nb_samples  # figure with 15x15 digits
		# 	digit_size = 28
		# 	figure = np.zeros((digit_size * n, digit_size * n))

		# 	#用正态分布的分位数来构建隐变量对
		# 	grid_x = norm.ppf(np.linspace(0.01, 0.99, n))
		# 	grid_y = norm.ppf(np.linspace(0.01, 0.99, n))

		# 	for i, yi in enumerate(grid_x):
		# 		for j, xi in enumerate(grid_y):
		# 			z_sample = np.array([[xi, yi]])
		# 			x_decoded = model.predict(sess, z_sample)
		# 			digit = x_decoded[0].reshape(digit_size, digit_size)
		# 			figure[i * digit_size: (i + 1) * digit_size,
		# 				j * digit_size: (j + 1) * digit_size] = digit

		# 	plt.figure(figsize=(10, 10))
		# 	plt.imshow(figure, cmap='Greys_r')
		# 	plt.savefig(os.path.join(self.log_dir, '%07d.png'%step))

		pass

