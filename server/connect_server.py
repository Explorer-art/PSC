#!usr/bin/python
#-*- coding: utf-8 -*-

import os
import sys
import socket
import struct
import threading

ip = "192.168.0.100"
port = 5072

number_maximum_lenght = 3

number_r = 0 # Для тестирования

welcome_message_status = False
welcome_message = "Добро пожаловать!\n"

allowed_ip = []

black_list_ip = []

numbers = []

clients = []

file = open("allowed_ip.txt", "r")
lines = file.readlines()

for line in lines:
	allowed_ip.append(line.strip())

file.close()

file = open("black_list_ip.txt", "r")
lines = file.readlines()

for line in lines:
	black_list_ip.append(line.strip())

file.close()

def broadcast_b(message, client_sender):
	for client in clients:
		if client != client_sender:
			client.send(message)

			print("[ЛОГ] Новое сообщение отправлено")

def broadcast(client, message, number_connect):
	if number_connect in numbers:
		number_connect_index = numbers.index(number_connect)
		client_data = clients[number_connect_index]
		client_data.send(message)

		print("[ЛОГ] Новое сообщение отправлено")
	else:
		print(f"[ЛОГ] Пользователь {username_connect} не подключен к линии связи.")

		data = "Пользователь " + username_connect + " не подключен к линии связи. Попробуйте позже."
		client.send(data.encode("utf-8"))

def receive_file_size(sck: socket.socket):
	fmt = "<Q"
	expected_bytes = struct.calcsize(fmt)
	received_bytes = 0
	stream = bytes()

	while received_bytes < expected_bytes:
		chunk = sck.recv(expected_bytes - received_bytes)
		stream += chunk
		received_bytes += len(chunk)

	filesize = struct.unpack(fmt, stream)[0]

	return filesize

def receive_file(sck: socket.socket, filename):
	file_size = receive_file_size(sck)

	with open(filename, "wb") as file:
		received_bytes = 0

		while received_bytes < file_size:
			chunk = sck.recv(1024)

			if chunk:
				file.write(chunk)
				received_bytes += len(chunk)

def send_file(sck: socket.socket, filename):
	filesize = os.path.getsize(filename)
	sck.sendall(struct.pack("<Q", filesize))

	with open(filename, "rb") as file:
		while read_bytes := file.read(1024):
			sck.sendall(read_bytes)

def handle(client, address, number, number_connect):
	n = True
	while n == True:
		if os.path.isfile("temp/" + number + ".pem") == True:
			send_file(client, "temp/" + number + ".pem")
			
			n = False

	message = client.recv(1024).decode("utf-8")

	if message == "REQUEST=OKAY":
		numbers.append(number)
		clients.append(client)

		print(f"[ЛОГ] Пользователь {number} {address} успешно подключен к защищённой линии связи!")

		if welcome_message_status == True:
			data = "REQUEST=WELCOME_MESSAGE:" + welcome_message
			client.send(data.encode("utf-8"))

			print(f"[ЛОГ] Пользователю {number} {address} отправлено приветственное сообщение {welcome_message}")
		else:
			client.send("REQUEST=NOT_WELCOME_MESSAGE".encode("utf-8"))
	else:
		print(f"[ОШИБКА] Ошибка при подтверждении подключения пользователя {address}")

		client.send("REQUEST=ERROR_NO_CONFIRM_CONNECT".encode("utf-8"))

		print("[ЛОГ] " + str(address) + " отключен")

		client.close()

	while True:
		try:
			message = client.recv(1024)
			print(message)

			request = message.decode("utf-8", "replace")

			if request == "REQUEST=EXIT":
				number_index = clients.index(client)
				clients.remove(client)
				number = numbers[number_index]
				numbers.pop(number_index)

				print(f"[ЛОГ] Пользователь {number} вышел")

				client.close()

				os.remove("temp/" + number + ".pem")
			else:
				print("[ЛОГ] Получено новое сообщение")

				broadcast(client, message, number_connect)
		except:
			print("[ЛОГ] Пользователь отключен")
			client.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ip, port))
server.listen()

print("[ИНФО] Сервер включен!")

print("[ИНФО] Айпи: " + ip)
print("[ИНФО] Порт: " + str(port))

while True:
	client, address = server.accept()

	print("[ЛОГ] Подключился " + str(address))

	message = client.recv(1024).decode("utf-8")

	if message != "REQUEST=CONNECT":
		print(f"[ЛОГ] Пользователь {address} отключился")

		client.close()

	if address[0] not in allowed_ip:
		print(f"[ОШИБКА] Пользователь {address} не найден в списке разрешённых IP!")

		client.send("REQUEST=ERROR_AUTH".encode("utf-8"))

		print("[ЛОГ] Пользователь " + str(address) + " отключен")

		client.close()
	elif address[0] in allowed_ip:
		print(f"[ЛОГ] Пользователь {address} успешно авторизировался!")

	if address[0] == "192.168.0.100":
		number_r = number_r + 1
		number = "00" + str(number_r)
	#elif address[0] == "192.168.0.150":
	#	number = "001"

	data = "REQUEST=" + number
	client.send(data.encode("utf-8"))

	client.send("REQUEST=NUMBER_CONNECT".encode("utf-8"))

	message = client.recv(1024).decode("utf-8")

	number_lenght = len(message)

	if number_lenght == number_maximum_lenght:
		number_connect = message
	else:
		client.send("REQUEST=ERROR_VERY_LONG_USERNAME".encode("utf-8"))

		print("[ЛОГ] Слишком длинный номер " + str(address))

		print("[ЛОГ] " + str(address) + " отключен")

		client.close()

	client.send("REQUEST=PUBLIC_KEY".encode("utf-8"))

	filename = "temp/" + number_connect + ".pem"

	receive_file(client, filename)

	threading.Thread(target=handle, args=(client, address, number, number_connect,)).start()