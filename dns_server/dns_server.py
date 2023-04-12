#!usr/bin/python
#-*- coding: utf-8 -*-

import os
import sys
import socket
import threading

ip = "94.250.251.14"
port = 25000

domains = ["server1.net", "server2.net", "localhost"]

ip_addresses = ["94.250.251.14:5572", "192.168.0.100:5572", "127.0.0.1:5572"]

def handle(client):
	message = client.recv(1024).decode("utf-8")

	if message in domains:
		index = domains.index(message)
		ip = ip_addresses[index]

		client.send(ip.encode("utf-8"))

		print("[LOG] Succesful!")
	else:
		client.send("REQUEST=DOMAIN_NOT_FOUND".encode("utf-8"))
		print("[ERROR] Domain not found!")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ip, port))
server.listen()

print("[INFO] Server started!")
print("[INFO] IP: " + str(ip))
print("[INFO] PORT: " + str(port))

while True:
	client, address = server.accept()

	threading.Thread(target=handle, args=(client,)).start()