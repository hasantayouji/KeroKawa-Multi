import zmq
import numpy as np
from utils.Utils import save_log


class ZmqConnect:
	def __init__(self, connect_to="tcp://localhost:5555"):
		self.context = zmq.Context()
		self.zmq_socket = self.context.socket(zmq.PUSH)
		self.zmq_socket.connect(connect_to)
		self.conto = connect_to
		save_log('Connecting to ZMQ server: ' + connect_to)

	def imsend(self, arrayname, array):
		md = self.conv_array(array, arrayname)
		self.zmq_socket.send_json(md)
		self.zmq_socket.send(array, flags=0, copy=True, track=False)
		save_log(f'Send ZMQ image to {self.conto}')

	def sendstring(self, arrayname):
		self.zmq_socket.send_json(arrayname)
		save_log(f'Send ZMQ string to {self.conto}')

	def conv_array(self, A, message):
		dtipe = str(A.dtype)
		sep = A.shape
		md = dict(
			dtype=dtipe,
			shape=sep,
			msg=message,
			)
		return md


class ZmqImageShowServer:
	def __init__(self, open_port="tcp://*:5555"):
		self.context = zmq.Context()
		self.zmq_socket = self.context.socket(zmq.PULL)
		self.zmq_socket.bind(open_port)
		self.opo = open_port
		save_log(f'Opening ZMQ server: {open_port}')

	def imreceive(self):
		arrayname = self.zmq_socket.recv_json()
		image_data = self.zmq_socket.recv(flags=0, copy=True, track=False)
		a = np.frombuffer(image_data, dtype=arrayname['dtype'])
		image = a.reshape(arrayname['shape'])
		save_log(f'Receiving ZMQ image in port {self.opo}')
		return arrayname['msg'], image

	def string_receive(self):
		arrayname = self.zmq_socket.recv_json()
		save_log(f'Receiving ZMQ string in port {self.opo}')
		return arrayname
