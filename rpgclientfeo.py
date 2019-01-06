#-*-coding utf-8-*-
from socket import *
from cryptography.fernet import Fernet as fern
from optparse import OptionParser as op
from sys import argv
from platform import python_version as pv
from platform import platform as p
from threading import Thread
from os import system

class Client:
	def __init__(self, ip, port, key):
		self.sock = socket(AF_INET, SOCK_STREAM)
		self.sock.connect((ip, port))
		self.f = fern(key)
		self.avatar = ""
		self.missions = {}
	def write(self):
		while True:
			try:
				msj = self.sock.recv(1024)
				msj = self.f.decrypt(msj)
				msj = msj.decode()
				self.process(msj)
			except Exception as e:
				print(e)
	def send(self, msj):
		msj = self.f.encrypt(msj.encode())
		self.sock.send(msj)
	def process(self, cmd):
		if cmd[:6] == "avatar":
			self.avatar = cmd[7:]
		elif cmd[:11] == "add mission":
			print("**New mission.")
			count = 12
			o = len(self.missions)
			for c in cmd[12:]:
				if c == " ":
					if len(self.missions) == 0:
						self.missions[cmd[12:count]] = cmd[count + 1:]
				else:
					count += 1
		elif cmd == "**You are death.":
			print(cmd)
			exit()
		else:
			print(cmd)
			


	def combat(self):
		pass

if __name__ == '__main__':
	opt = op("Usage: %prog [usage] [value]")
	opt.add_option("-s", "--server",dest="server",help="Set server's ip. (default value = 127.0.0.1) (value's type = string)",default="127.0.0.1", type="string")
	opt.add_option("-p","--port",dest="port",help="Set server's port. (default value = 5000) (type = int)", default=5000, type="int")
	opt.add_option("-k","--key",dest="key",help="Set cryptography key. (default value = M2fg-uTtmo5BNeMoq4U1OfVmgAomY2897J4eYct4jII=) (type = string)", default="M2fg-uTtmo5BNeMoq4U1OfVmgAomY2897J4eYct4jII=", type="string")
	(o, argv) = opt.parse_args()
	c = Client(o.server, o.port, o.key)
	hear = Thread(target=c.write)
	hear.daemon = True
	hear.start()
	cmd = ""
	if str(pv())[0] == "3":
		raw_input = input
	if str(p())[0] == "W":
		clear = "cls"
	else:
		clear = "clear"
	while cmd != "exit":
		cmd = raw_input(">")
		if cmd == clear:
			system(clear)
		elif cmd == "missions":
			for mission in c.missions:
				print("{} : {}".format(mission, c.missions[mission]))
		else:
			c.send(cmd)