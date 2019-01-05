#-*-coding: utf-8-*-
from socket import *
from cryptography.fernet import Fernet as fern
from sys import argv
from optparse import OptionParser as op
from platform import python_version as pv
from platform import platform as p
from os import system
from threading import Thread
from time import sleep

class Character:
	def __init__(self):
		self.status = {"Health":10, "Strong": 2, "Money": 20, "Level": 0, "Hunger": 10, "Resistance": 30}
		self.inventario = {"Health potion":[1,("Potion","Health",True),10]}
		self.xppoints = 0
		self.xp = 0
		self.equipo = {"Head":[False,"0","0"],"Chest":[False,"|","|"],"Hands":[False,None,None],"Weapon":[False,"",""]}
		self.avatar ='''\n 		 {}\n 		/{}\\{}\n 		/ \\'''.format(self.equipo["Head"][1],self.equipo["Chest"][1],self.equipo["Weapon"][1])
		n = Thread(target=self.needs)
		n.daemon = True
		n.start()
	def needs(self):
		self.xtop = 10
		count = 0
		while True:
			sleep(1)
			count += 1
			if count == self.status["Resistance"]:
				self.status["Hunger"] -= 1
				if self.status["Hunger"] <= 0:
					self.status["Health"] -= 1
			if self.xp > self.xtop:
				self.status["Level"] += 1
				if self.status["Level"] %10 == 0:
					self.xppoints += 10 * self.xtop
				else:
					self.xppoints += randint(int(self.xppoints / 4), int(self.xppoints / 2) )

class Server:
	def __init__(self, host, port , lisent, key):
		if str(pv())[0] == "3":
			raw_input = input
		if str(p())[0] == "W":
			clear = "cls"
		else:
			clear = "clear"
		self.f = fern(key)
		self.l = lisent
		self.sock = socket(AF_INET, SOCK_STREAM)
		try:
			self.sock.bind((host, port))
		except Exception as e:
			print(e)
			exit()
		self.sock.listen(self.l)
		self.sock.setblocking(False)
		self.clients = {}
		self.conns = []
		w = Thread(target=self.wait)
		w.daemon = True
		w.start()
		h = Thread(target=self.heartoall)
		h.daemon = True
		h.start()
		c = ""
		costum_clear = clear
		while c != "exit":
			c = raw_input(">")
			if c == costum_clear:
				system(clear)
			elif c[:17] == "set costume clear":
				costum_clear = c[18:]
		self.sock.shutdown(SHUT_RD)
		self.sock.close()

	def wait(self):
		count = 0
		while True:
			while len(self.conns) < self.l:
				try:
					conn, addr = self.sock.accept()
				except:
					pass
				else:
					print(addr)
					conn.setblocking(False)
					self.conns.append(conn)
					self.clients[str(conn)] = ["Client-{}".format(count),Character()]
					
					count += 1
	def heartoall(self):
		while True:
			for c in self.conns:
				try:
					msj = c.recv(1024)
					self.process(msj,self.clients[str(c)][0], c)
				except:
					pass
	def process(self, m, c, csend):
		cc = str(csend)
		cmd = self.f.decrypt(m)
		cmd = cmd.decode()
		if True:
			if cmd[0] == "*":
				print("{} : {}".format(c, cmd[1:]))
			elif cmd == "status":
				for value in self.clients[cc][1].status:
					self.send("\n{} : {}".format(value, self.clients[cc][1].status[value]), csend)
			elif cmd == "inventory":
				self.send("Item      |       Quantity      |      Type",csend)
				for item in self.clients[cc][1].inventario:
					self.send("{}      |       {}      |       {}".format(item, self.clients[cc][0],self.clients[cc][1][0]),csend)
			elif cmd[:3] == "use" or cmd[:7] == "consume":
				if cmd[0] == "u":
					n = cmd[4:]
				else:
					n = cmd[8:]
					if n in self.clients[cc][1].inventario:
						if self.clients[cc][1].inventario[n][1][2]:
							self.clients[cc][1].status[self.clients[cc][1].inventario[n][1][1]] += self.clients[cc][1].inventario[n][2]
							self.clients[cc][1].inventario[cc][0] -= 1
						else:
							self.send("**That is not a consumable item.", csend)
					else:
						self.send("**Item not found.", csend)
			else:
				self.send("**Comand not found", csend)
			self.send(">",csend)
		'''except IndexError:
			pass
		except Exception as e:
			send(str(e), csend)'''
	def send(self, m, c):
		msj = self.f.encrypt(m.encode())
		c.send("\n{}".format(msj.deocode()).encode())


if __name__ == '__main__':
	opts = op("Usage: %prog [options] [values]")
	opts.add_option("-H","--host",dest="host",help="Set server's host. (default value = 127.0.0.1) (type = string)",default="127.0.0.1", type="string")
	opts.add_option("-p","--port",dest="port",help="Set server's port. (default value = 5000) (type = int)", default=5000, type="int")
	opts.add_option("-k","--key",dest="key",help="Set cryptography key. (default value = M2fg-uTtmo5BNeMoq4U1OfVmgAomY2897J4eYct4jII=) (type = string)", default="M2fg-uTtmo5BNeMoq4U1OfVmgAomY2897J4eYct4jII=", type="string")
	opts.add_option("-l","--listen",dest="listen",help="Set how many players can be connected at the same time. (default value = 2) (type = int)", default=2, type="int")
	(o, argv) = opts.parse_args()
	o.key = o.key.encode()
	s = Server(o.host, o.port, o.listen, o.key)