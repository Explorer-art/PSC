#!usr/bin/python
#-*- coding: utf-8 -*-

import os
import sys
import random
import socket
import struct
import threading

ip = "192.168.0.100"
port = 5072

number_maximum_lenght = 10

welcome_message_status = False
welcome_message = "Welcome!\n"

allowed_ip = []

banned_ip = []

numbers = []

clients = []

file = open("allowed_ip.txt", "r")
lines = file.readlines()

for line in lines:
	allowed_ip.append(line.strip())

file.close()

file = open("banned_ip.txt", "r")
lines = file.readlines()

for line in lines:
	blocked_ip.append(line.strip())

file.close()

def amount(): #Количество подключённых пользователей
	amount = 0

	for client in clients:
		amount += 1

	return amount

def list(): #Список подключённых пользователей
	for number in numbers:
		print(number + ", ", end="")

def send_message(client, message, number_connect): #Отправка сообщения отдельному пользователю
	if number_connect in numbers:
		number_connect_index = numbers.index(number_connect)
		client_data = clients[number_connect_index]
		client_data.send(message)

		print("[LOG] Sended new message")

def broadcast(message): #Отправка сообщения всем пользователям
	for client in clients:
		client.send(message.encode("utf-8"))

	print("[LOG] Broadcast message sended")

def receive_file_size(sck: socket.socket): #Определение размера передоваемого файла
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

def receive_file(sck: socket.socket, filename): #Принятие передоваемого файла
	file_size = receive_file_size(sck)

	with open(filename, "wb") as file:
		received_bytes = 0

		while received_bytes < file_size:
			chunk = sck.recv(1024)

			if chunk:
				file.write(chunk)
				received_bytes += len(chunk)

def send_file(sck: socket.socket, filename): #Отправка файла
	filesize = os.path.getsize(filename)
	sck.sendall(struct.pack("<Q", filesize))

	with open(filename, "rb") as file:
		while read_bytes := file.read(1024):
			sck.sendall(read_bytes)

def handle(client, address, number): #Пользователь
	client.send("REQUEST=NUMBER_CONNECT".encode("utf-8"))

	message = client.recv(1024).decode("utf-8")

	number_lenght = len(message)

	if number_lenght == number_maximum_lenght:
		number_connect = message
	else:
		client.send("REQUEST=ERROR_VERY_LONG_USERNAME".encode("utf-8"))

		print("[LOG] The number is too long " + str(address))

		print("[LOG] " + str(address) + " kicked")

		client.close()

	client.send("REQUEST=PUBLIC_KEY".encode("utf-8"))

	filename = "temp/" + number_connect + ".pem"

	receive_file(client, filename)
	
	n = True
	while n == True:
		if os.path.isfile("temp/" + number + ".pem") == True:
			send_file(client, "temp/" + number + ".pem")
			
			n = False

	message = client.recv(1024).decode("utf-8")

	if message == "REQUEST=OKAY":
		numbers.append(number)
		clients.append(client)

		print(f"[LOG] User {number} {address} connected to PSC!")

		if welcome_message_status == True:
			data = "REQUEST=WELCOME_MESSAGE:" + welcome_message
			client.send(data.encode("utf-8"))

			print(f"[LOG] User {number} {address} sended  welcome message {welcome_message}")
		else:
			client.send("REQUEST=NOT_WELCOME_MESSAGE".encode("utf-8"))
	else:
		print(f"[ERROR] Error confirm user {address}")

		client.send("REQUEST=ERROR_NO_CONFIRM_CONNECT".encode("utf-8"))

		print("[LOG] " + str(address) + " kicked")

		client.close()
		os.remove("temp/" + number + ".pem")

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

				print(f"[LOG] User {number} disable")

				client.close()

				os.remove("temp/" + number + ".pem")

				break
			else:
				print("[LOG] A new message has been received")

				send_message(client, message, number_connect)
		except:
			print(f"[LOG] User {address} kicked")
			client.close()
			os.remove("temp/" + number + ".pem")
			break

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ip, port))
server.listen()

print("[INFO] Server started!")

print("[INFO] IP: " + ip)
print("[INFO] PORT: " + str(port))

while True: #Основной цикл сервера
	client, address = server.accept()

	print("[LOG] Connected " + str(address))

	message = client.recv(1024).decode("utf-8")

	if message != "REQUEST=CONNECT":
		print(f"[LOG] User {address} kicked")

		client.close()

	if address[0] in banned_ip:
		print(f"[ERROR] User {address} banned!")

		client.send("REQUEST=BANNED".encode("utf-8"))

		print("[LOG] User " + str(address) + " kicked")

		client.close()

	if address[0] not in allowed_ip:
		print(f"[ERROR] User {address} not found in the list of allowed IP addresses!")

		client.send("REQUEST=ERROR_AUTH".encode("utf-8"))

		print("[LOG] User " + str(address) + " kicked")

		client.close()
	elif address[0] in allowed_ip:
		print(f"[LOG] User {address} succesful auth!")

	number = str(random.randint(1000000000, 9999999999)) #Генерация номера пользователя

	data = "REQUEST=" + number
	client.send(data.encode("utf-8"))

	threading.Thread(target=handle, args=(client, address, number,)).start()