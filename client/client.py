#!usr/bin/python
#-*- coding: utf-8 -*-

import os
import sys
import time
import rsa
import socket
import struct
import threading

status = True

ip = "94.250.251.14"
port = 5072

os.system("cls")

print("Защищённая линия связи")
print("")

username = input("Введите имя пользователя: ")

def receive(client):
	global status
	while status == True:
		try:
			message = client.recv(1024).decode("utf-8")

			print("\n" + message + "\n")
		except:
			client.close()

			status = False

			sys.exit()

def writer(client):
	global status
	while status == True:
		message = input("\nВведите сообщение: ")

		if message == "!info":
			print("Информация:")
			print("Версия: 1.0")
			print("Автор: Truzme_")
			print("")
		elif message == "!exit":
			print("Отключение..")

			client.send("REQUEST=EXIT".encode("utf-8"))

			client.close()

			status = False

			print("Выход..")

			os.system("cls")

			sys.exit()

		if message != "":
			message = username + " > " + message

			print(message)

			client.send(message.encode("utf-8"))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ip, port))

print("Подключение..")

client.send("REQUEST=CONNECT".encode("utf-8"))

message = client.recv(1024).decode("utf-8")

if message == "REQUEST=BANNED":
	print("Вы забанены!")

	client.close()

	status = False

	sys.exit()

print("Авторизация..")

if message == "REQUEST=ERROR_AUTH":
	print("Ошибка! Авторизация не пройдена.")

	client.close()

	status = False

	sys.exit()
elif message == "REQUEST=ALREADY_CONNECTED":
	print("Ошибка! Вы уже подключены к системе!")

	client.close()

	status == False

	sts.exit()
elif message == "REQUEST=SUCCESFUL_AUTH":
	print("Авторизация успешно пройдена!")

	client.send("REQUEST=NUMBER".encode("utf-8"))

message = client.recv(1024).decode("utf-8")

number = message[8:18]

print("Ваш номер: " + number)

message = client.recv(1024).decode("utf-8")

if message == "REQUEST=NUMBER_CONNECT":
	number_connect = input("Введите номер пользователя к которому вы хотите подключиться: ")

	client.send(number_connect.encode("utf-8"))

message = client.recv(1024).decode("utf-8")

if message == "REQUEST=ERROR_VERY_LONG_OR_SHORT_NUMBER":
	print("Ошибка! Слишком длинный или короткий номер.")

	client.close()

	status = False

	sys.exit()
elif message == "REQUEST=USERNAME":
	client.send(username.encode("utf-8"))

message = client.recv(1024).decode("utf-8")

if message == "REQUEST=ERROR_VERY_LONG_OR_SHORT_USERNAME":
	print("Ошибка! Слишком длинное или короткое имя пользователя.")

	client.close()

	status = False

	sys.exit()
elif message == "REQUEST=WAITING":
	print("Ожидание подключения пользователя..")

	message = client.recv(1024).decode("utf-8")

if message == "REQUEST=SUCCESFUL_CONNECT":
	client.send("REQUEST=OKAY".encode("utf-8"))

	message = client.recv(1024).decode("utf-8")

	if message == "REQUEST=ERROR_NO_CONFIRM_CONNECT":
		print("Ошибка! Подключение не подтверждено.")

		client.close()

		status = False

		sys.exit()

	data = message[0:24]

	if data == "REQUEST=WELCOME_MESSAGE:":
		welcome_message = message[25:99999]

		print(welcome_message)

	print("Успешное подключение!")
	time.sleep(2)

	os.system("cls")

	print("Защищённая линия связи")
	print("")
	print("Имя пользователя: " + username)
	print("Ваш номер: " + number)
	print("")
	print("")

	receive_thread = threading.Thread(target=receive, args=(client,))  # Получение всех сообщений
	receive_thread.start()
	writer_thread = threading.Thread(target=writer, args=(client,))  # Отправка сообщений
	writer_thread.start()