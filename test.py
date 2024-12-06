import socket
from threading import Thread

# Function to append connected IPs to blocklist
def upload_blocklist(IP):
    try:
        with open("blocklist.ips", "a") as file:
            file.write(IP + "\n")
    except Exception as e:
        print(f"Error updating blocklist: {e}")

# Function to check if an IP is already blocked
def CheckBlockIps(IP):
    try:
        with open("blocklist.ips", "r") as file:
            blocked_ips = file.readlines()
        for blocked_ip in blocked_ips:
            if blocked_ip.strip() == IP:
                return True
        return False
    except FileNotFoundError:
        # If file does not exist, no IPs are blocked yet
        print("Blocklist file not found. No IPs are currently blocked.")
        return False

# Thread to handle client communication
class ClientHandler(Thread):
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr

    def run(self):
        ip, port = self.addr
        print(f"Connection received from {ip}:{port}")

        # Check if the IP is already blocked
        if CheckBlockIps(ip):
            print(f"Blocked IP attempted to connect: {ip}")
            self.conn.sendall(b"Your IP is blocked. Goodbye!\n")
            self.conn.close()
            return

        # Add the connected IP to the blocklist
        upload_blocklist(ip)

        # Send a welcome message
        self.conn.sendall(b"Welcome to the Math Server! Type 'quit' to exit.\n")

        while True:
            try:
                # Receive data from the client
                data = self.conn.recv(1024).decode().strip()
                if not data or data.lower() == 'quit':
                    print(f"{ip}:{port} disconnected.")
                    break

                # Evaluate mathematical expressions
                try:
                    result = eval(data)
                    self.conn.sendall(f"Result: {result}\n".encode())
                except Exception as e:
                    self.conn.sendall(f"Error: Invalid expression. {e}\n".encode())
            except Exception as e:
                print(f"Error with {ip}:{port}: {e}")
                break

        self.conn.close()

# Server setup
def main():
    host = ''
    port = 1111

    # Create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print("Math Server is running...")

    while True:
        # Accept client connections
        conn, addr = server_socket.accept()
        ip, port = addr
        print(f"New connection from {ip}:{port}")

        # Start a new thread for the client
        client_thread = ClientHandler(conn, addr)
        client_thread.start()

if __name__ == "__main__":
    main()
