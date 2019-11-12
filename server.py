import socket
import threading

import handshake
import framing

class ThreadedServer():
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((self.host, self.port))

	def listen(self):
		self.sock.listen(5)
		print(f"Websocket Server is listening on {self.port}")
		while True:
			client, address = self.sock.accept()
			client.settimeout(60)
			threading.Thread(target = self.listenToClient, args = (client,address)).start()

	def listenToClient(self, client, address):
		size = 20000
		print(f"> Getting data from {client.getpeername()}")
		
		# Handshake Phase
		handshake_data = client.recv(size)
		client.send(bytes(handshake.response_handshake(handshake_data), 'utf-8'))

		while True:
			try:
				# Getting Data Phase
				data = client.recv(size)
				if data:
					frame = framing.parse_frame(data)
					real_payload = framing.get_real_payload(frame['MASK'], frame['MASK_KEY'], frame['PAYLOAD'])
					opcode = frame['OPCODE']
					if opcode == 0x00:
						# Continuation
						# TODO
						pass
					elif opcode == 0x01:
						# Text frame

						# Requirment 1
						# If client send '!echo <message>', server should reply the same <message>
						text_payload = real_payload.decode('utf-8')
						if text_payload.startswith('!echo '):
							message = text_payload[6:]
							client.send(framing.build_frame(1, 0, 0, 0, 0x01, 0, len(message), 0, bytes(message, 'utf-8')))						

						# Requirment 2
						# If client send '!submission', server should reply .zip file including
						if text_payload == '!submission':
							file_ = open('OlengCaptain.zip', 'rb').read()
							client.send(framing.build_frame(1, 0, 0, 0, 0x02, 0, len(file_), 0, file_))

					elif opcode == 0x02:
						# Binary frame

						# Requirment 3
						# If client send binary file, server should validate file using md5 checksum
						# TODO
						pass
					elif opcode == 0x08:
						# Connection close

						client.close()
					elif opcode == 0x09:
						# Ping Control Frame
						 message = framing.build_frame(
							frame['FIN'],
							frame['RSV1'],
							frame['RSV2'],
							frame['RSV3'],
							0x0A, # Pong
							frame['MASK'],
							frame['PAYLOAD_LEN'],
							frame['MASK_KEY'],
							frame['PAYLOAD']
						)
						# Put send message here
					elif opcode == 0x0A:
						# Pong Control Frame
						pass # Does nothing

			except:
				client.close()
				return False

if __name__ == "__main__":
	# while True:
	# 	port_num = input("Port? ")
	# 	try:
	# 		port_num = int(port_num)
	# 		break
	# 	except ValueError:
	# 		pass

	ThreadedServer('', 8000).listen()