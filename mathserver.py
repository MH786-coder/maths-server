import socket
from subprocess import Popen, STDOUT, PIPE
from threading import Thread
from time import sleep
import re
from datetime import datetime
from os import *
import platform

def regx_finder(text):
    # Regex to match two numbers with an operator (+, -, *, /, ^) in between
    pattern = r'(\d+)\s*([+\-*/^])\s*(\d+)'
    
    # Search for the pattern
    match = re.search(pattern, text)

    if match:
        left_side = match.group(1)  
        operator = match.group(2)
        right_side = match.group(3)
        
        # Check the length of the left and right operands
        if len(left_side) > 5:
            return False
        if len(right_side) > 5:
            return False

        # Return the cleaned-up expression if it passes the checks
        return True
    else:
        return True


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
		self.blocked_ips = set()
	
	def run(self):
		self.conn.sendall("\nPlease enter your name\n".encode())
		self.username = self.conn.recv(1024)
		user = self.username.strip().decode()
		current_time = datetime.now().ctime()
		if self.username != "" and self.addr[0] not in self.blocked_ips:
			print(f"{user} : {self.addr[0]} connected with back port {self.addr[1]} at {current_time}\nDevice name : {name}\nDevice platform : {platform.system()}")
			self.conn.sendall("Simple Math Server developed by LAHTP \n\nGive any math expressions, and I will answer you :) \n\n$ ".encode())
		else:
			print("blocked ip {} try to connect our server at {}".format(self.addr[0],datetime.now().ctime()))

		## APPLICATION LAYER 7
		p = Popen(['bc'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
		output = ProcessOutputThread(p, self.conn)
		output.start()

		# toBlock = input(r'Enter the name of the person to block thier ip : ')
		# if toBlock:
		# 	self.blocked_ips.add(toBlock)
		# 	pass

		while not p.stdout.closed or not self.conn._closed:
			try: ## PRESENTATION LAYER 6
				if self.addr[0] in self.blocked_ips:
					self.conn.sendall("You can\'t access this server, because you blocked\n".encode())
					break
				else:
					if self.username != "":
						data = self.conn.recv(1024)
						if not data:
							break
						else:
							try: 
								data = data.decode()
								query = data.strip()
								final_query = regx_finder(query)
								
								if query == 'quit' or query == 'exit':
									p.communicate(query.encode(), timeout=1)
									if p.poll() is not None:
										print("{} exit from math server at {}".format(self.username.strip().decode(),datetime.now().ctime()))
										break
									
								
								if final_query is False:
									self.conn.sendall(("Buffer size too long.").encode())
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
PORT = 3074

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