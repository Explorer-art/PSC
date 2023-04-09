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

ip = "192.168.0.100"
port = 5072

check_dir_keys = os.path.isdir("keys")
check_file_public_key = os.path.isfile("keys/public_key.pem")
check_file_private_key = os.path.isfile("keys/private_key.pem")

if check_dir_keys == False:
	os.mkdir("keys")

if check_file_public_key == True and check_file_private_key == True:
	os.remove("keys/public_key.pem")
	os.remove("keys/private_key.pem")

	(public_key, private_key) = rsa.newkeys(512)

	print("Генерация публичного ключа..")

	public_key_data = public_key.save_pkcs1()

	file = open("keys/public_key.pem", "wb")
	file.write(public_key_data)
	file.close()

	print("Публичный ключ сгенерирован")

	print("Генерация приватного ключа..")

	private_key_data = private_key.save_pkcs1()

	file = open("keys/private_key.pem", "wb")
	file.write(private_key_data)
	file.close()

	print("Приватный ключ сгенерирован")

	print("")

	print("Ключи успешно сгенерированы!")

	file = open("keys/public_key.pem")
	public_key_data = file.read()
	public_key = rsa.PublicKey.load_pkcs1(public_key_data)
	file.close()

	file = open("keys/private_key.pem")
	private_key_data = file.read()
	private_key = rsa.PrivateKey.load_pkcs1(private_key_data)
	file.close()
elif check_file_public_key == False and check_file_private_key == False:
	(public_key, private_key) = rsa.newkeys(512)

	print("Генерация публичного ключа..")

	public_key_data = public_key.save_pkcs1()

	file = open("keys/public_key.pem", "wb")
	file.write(public_key_data)
	file.close()

	print("Публичный ключ сгенерирован")

	print("Генерация приватного ключа..")

	private_key_data = private_key.save_pkcs1()

	file = open("keys/private_key.pem", "wb")
	file.write(private_key_data)
	file.close()

	print("Приватный ключ сгенерирован")

	print("")

	print("Ключи успешно сгенерированы!")

	file = open("keys/private_key.pem")
	private_key_data = file.read()
	private_key = rsa.PrivateKey.load_pkcs1(private_key_data)
	file.close()

os.system("cls")

print("Защищённая линия связи")
print("")

number_connect = input("Введите номер абонента к которому вы хотите подключиться: ")
print("")

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

def receive(client):
	global status
	while status == True:
		try:
			message = client.recv(1024)

			decrypt_message = rsa.decrypt(message, private_key)

			print("\n" + decrypt_message.decode("utf-8") + "\n")
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

			os.remove("keys/public_key.pem")
			os.remove("keys/private_key.pem")

			print("Выход..")

			os.system("cls")

			sys.exit()

		if message != "":
			message = number + " > " + message

		print(message)

		message = message.encode("utf-8")

		encrypt_message = rsa.encrypt(message, public_key)

		client.send(encrypt_message)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ip, port))

print("Подключение..")

client.send("REQUEST=CONNECT".encode("utf-8"))

message = client.recv(1024).decode("utf-8")

if message == "REQUEST=ERROR_AUTH":
	print("Ошибка! Авторизация не пройдена.")

	client.close()

	status = False

	sys.exit()

number = message[8:11]

message = client.recv(1024).decode("utf-8")

if message == "REQUEST=NUMBER_CONNECT":
	client.send(number_connect.encode("utf-8"))

message = client.recv(1024).decode("utf-8")


if message == "REQUEST=PUBLIC_KEY":
	send_file(client, "keys/public_key.pem")
elif message == "REQUEST=ERROR_VERY_LONG_USERNAME":
	print("Ошибка! Слишком длинный номер.")

	client.close()

	status = False

	sys.exit()

print("Ожидание подключения..")

receive_file(client, "keys/public_key.pem")

print("Подлючение найдено!")

file = open("keys/public_key.pem")
public_key_data = file.read()
public_key = rsa.PublicKey.load_pkcs1(public_key_data)
file.close()

client.send("REQUEST=OKAY".encode("utf-8"))
print("Успешное подключение!")
time.sleep(2)

os.system("cls")

print("Защищённая линия связи")
print("")
print("Ваш номер: " + number)
print("")
print("")

message = client.recv(1024).decode("utf-8")

data = message[0:24]

if data == "REQUEST=WELCOME_MESSAGE:":
	welcome_message = message[25:99999]

	print(welcome_message)

receive_thread = threading.Thread(target=receive, args=(client,))  # Получение всех сообщений
receive_thread.start()
writer_thread = threading.Thread(target=writer, args=(client,))  # Отправка сообщений
writer_thread.start()