import socket
from subprocess import Popen, STDOUT, PIPE
from threading import Thread
from time import sleep
from datetime import datetime
from os import *

def update_clients(Ip):
	with open("clients.txt","w") as clients:
		clients.write(Ip)

def upload_blocklist(IP):
	with open("blocklist.ips", "a") as file:
		if file.write(IP+'\n'):
			print("\nINFO : {} upload to blocklist\n".format(IP))
		else:
			pass

def CheckBlockedIps(IP):
	try:
		file = open("blocklist.ips","r")
		blockedIp = file.readlines()
		
		for Ips in blockedIp:
			if Ips.strip() == IP:
				return True
		return False
	except Exception as e:
		print(e)

def start_new_math_thread(conn, addr):
	t = MathServerCommunicationThread(conn, addr)
	t.start()

class ProcessOutputThread(Thread): #OOPS
	def __init__(self, proc, conn):
		Thread.__init__(self)
		self.proc = proc
		self.conn = conn
		
	def run(self):
		while not self.proc.stdout.closed and not self.conn._closed:
			try:
				self.conn.sendall(self.proc.stdout.readline())
			except:
				pass
			
class MathServerCommunicationThread(Thread):
	def __init__(self, conn, addr):
		Thread.__init__(self)
		self.conn = conn
		self.addr = addr
		self.username = ""
	
	def run(self):
		update_clients(self.addr[1])
		self.conn.sendall("\nPlease enter your name:\n".encode())
		self.username = self.conn.recv(1024)
		user = self.username.strip().decode()
		current_time = datetime.now().ctime()
		if self.username != "":
			if CheckBlockedIps(self.addr[1]):
				upload_blocklist(self.addr[1])
			else:
				print(f"{user} : {self.addr[0]} connnected with {self.addr[1]} at {current_time}")
				self.conn.sendall("Simple Maths Server Developed by Mohamed Hathim\n".encode())
		else:
			self.conn.sendall("Credential required\n".encode())
			self.conn.close()
			

		## APPLICATION LAYER 7
		p = Popen(['bc'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
		output = ProcessOutputThread(p, self.conn)
		output.start()

		while not p.stdout.closed or not self.conn._closed:
			try: ## PRESENTATION LAYER 
				if self.username != "":
					data = self.conn.recv(1024)
					if not data:
						break
					else:
						try: 
							data = data.decode()
							query = data.strip()

							if len(query) > 16:
								self.conn.sendall(("Buffer length too strong ").strip().encode())
							
							if query == 'quit' or query == 'exit':
								p.communicate(query.encode(), timeout=1)
								if p.poll() is not None:
									print("{} exit from math server at {}".format(self.username.strip().decode(),datetime.now().ctime()))
									break

							query = query + '\n'
							p.stdin.write(query.encode())
							p.stdin.flush()
								
						except:
							self.conn.sendall("Click {} or {} to exit from server".format("quit","exit").encode())
				
				else:
					self.conn.sendall("Username must wanted".encode())
			except:
				pass
		self.conn.close()

HOST = ''
PORT = 1111

## SESSION LAYER 5
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen() # Look for calling bell
while True: # To accept many incoming connections.
	conn, addr = s.accept() # Open door
	sleep(1)
	start_new_math_thread(conn, addr)
s.close()