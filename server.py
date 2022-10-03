
import socket
from sqlite3 import connect
import threading
import uuid
from copy import deepcopy
from collections import namedtuple

PORT = 65432
SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"
CLIENTS = namedtuple('CLIENTS', ['client_id', 'name', 'conn', 'addr'])
DISCONNECT_MESSAGES = ['!dc']

clients = []

server = socket.socket(socket.AF_INET,
                       socket.SOCK_STREAM)

server.bind(ADDRESS)


def startChat():

	print("[STARTING] Server is working on: " + SERVER)

	server.listen()

	while True:
		conn, addr = server.accept()
		conn.send("NAME".encode(FORMAT))

		name = conn.recv(1024).decode(FORMAT)
		client_id = uuid.uuid4()
		client = CLIENTS(client_id, name, conn, addr)
		clients.append(client)

		print(f"[CONNECTION] {name} connected from {addr}")

		broadcastMessage(f"{name} has joined the chat!".encode(FORMAT))

		conn.send('Connection successful!'.encode(FORMAT))

		thread = threading.Thread(target=handle, args=(client_id, name, conn, addr))
		thread.start()

		print(f"[INFO] Active Connections: {threading.activeCount()-1}")


def is_disconnect(name, message):
	message = message.decode(FORMAT)
	m = deepcopy(message)
	m = m.strip(f'{name}: ')
	print(f'[DEBUG] Stripped message: {m}')
	return True if m in DISCONNECT_MESSAGES else False

def disconnect(client_id, name, conn):
	conn.send("DISCONNECT".encode(FORMAT))
	global clients
	clients = [c for c in clients if c.client_id != client_id]
	broadcastMessage(f'{name} disconnected from the server.'.encode(FORMAT))


def handle(client_id, name, conn, addr):

	print(f"[INFO] New connection {addr}")
	connected = True
	while connected:
		message = conn.recv(1024)

		if is_disconnect(name, message):
			disconnect(client_id, name, conn)
			break
		broadcastMessage(message)

	conn.close()
	print(f'[INFO] name: {name} is disconnected !')


def broadcastMessage(message):
	for client in clients:
		connection = client.conn
		print(f'[INFO] {client.name} sent {message} from {client.addr}')
		connection.send(message)


startChat()
