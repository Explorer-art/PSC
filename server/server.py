#!usr/bin/python
#-*- coding: utf-8 -*-

import os
import sys
import random
import socket
import struct
import threading

ip = "94.250.251.14"
port = 5072

number_maximum_lenght = 10
username_maximum_lenght = 50

welcome_message_status = False
welcome_message = "Welcome!\n"

allowed_ip = []

banned_ip = []

numbers = []

clients = []

addresses = []

usernames = []

numbers_connect = []

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
		client_data.send(message.encode("utf-8"))

def broadcast(message): #Отправка сообщения всем пользователям
	for client in clients:
		client.send(message.encode("utf-8"))

	print("[LOG] Broadcast message sended")

def handle(client, address, number): #Пользователь
	client.send("REQUEST=NUMBER_CONNECT".encode("utf-8"))

	message = client.recv(1024).decode("utf-8")

	number_lenght = len(message)

	if number_lenght == number_maximum_lenght: #Проверка длины номера
		number_connect = message

		numbers_connect.append(number_connect)
	else:
		client.send("REQUEST=ERROR_VERY_LONG_OR_SHORT_NUMBER".encode("utf-8"))

		print("[LOG] The number is too long or short " + str(address))

		print("[LOG] " + str(address) + " kicked")

		client.close()

	client.send("REQUEST=USERNAME".encode("utf-8"))

	username = client.recv(1024).decode("utf-8")

	username_lenght = len(message)

	if username_lenght <= number_maximum_lenght: #Проверка длины имени пользователя
		username = message
	else:
		client.send("REQUEST=ERROR_VERY_LONG_OR_SHORT_USERNAME".encode("utf-8"))

		print("[LOG] The username is too long or short " + str(address))

		print("[LOG] " + str(address) + " kicked")

		client.close()
		numbers_connect.remove(number)

	client.send("REQUEST=WAITING".encode("utf-8"))

	n = True

	while n == True:
		if number in numbers_connect:
			if number_connect in numbers_connect:
				client.send("REQUEST=SUCCESFUL_CONNECT".encode("utf-8"))

				n = False

	message = client.recv(1024).decode("utf-8")

	if message == "REQUEST=OKAY":
		numbers.append(number)
		clients.append(client)
		addresses.append(address[0])
		usernames.append(username)

		print(f"[LOG] User {number} {address} connected to PSC!")

		if welcome_message_status == True:
			data = "REQUEST=WELCOME_MESSAGE:" + welcome_message
			client.send(data.encode("utf-8"))

			print(f"[LOG] User {number} {address} sended  welcome message {welcome_message}")
		else:
			client.send("REQUEST=NOT_WELCOME_MESSAGE".encode("utf-8"))
	else:
		print(f"[ERROR] No confirm user {address}")

		client.send("REQUEST=ERROR_NO_CONFIRM_CONNECT".encode("utf-8"))

		print("[LOG] " + str(address) + " kicked")

		client.close()
		numbers_connect.remove(number)

	while True:
		try:
			message = client.recv(1024).decode("utf-8")

			if message == "REQUEST=EXIT":
				number_index = clients.index(client)
				clients.remove(client)
				number = numbers[number_index]
				numbers.pop(number_index)

				print("[LOG] User " + str(number) + " (" + str(address[0]) + ":" + str(address[1]) + ") leave")

				client.close()
				numbers.remove(number)
				numbers_connect.remove(number)
				break
			else:
				send_message(client, message, number_connect)
				
				print("[LOG] User " + str(number) + " (" + str(address[0]) + ":" + str(address[1]) + ") send " + number_connect + " message: " + message)
		except:
			print("[LOG] User " + str(number) + " (" + str(address[0]) + ":" + str(address[1]) + ") leave")

			client.close()
			numbers.remove(number)
			numbers_connect.remove(number)
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

	elif address[0] in addresses:
		print(f"[ERROR] User {address} already connected.")

		client.send("REQUEST=ALREADY_CONNECTED".encode("utf-8"))

		print("[LOG] User " + str(address) + " kicked")
		client.close()

	client.send("REQUEST=SUCCESFUL_AUTH".encode("utf-8"))

	message = client.recv(1024).decode("utf-8")

	if message == "REQUEST=NUMBER":
		s = True

		while s == True:
			number = str(random.randint(1000000000, 9999999999)) #Генерация номера пользователя

			if number not in numbers:
				s = False

		data = "REQUEST=" + number
		client.send(data.encode("utf-8"))

		threading.Thread(target=handle, args=(client, address, number,)).start()