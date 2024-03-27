import socket
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect(('192.168.221.187', 5000))
name = input("Enter your name: ")
my_socket.send(name.encode())
data = my_socket.recv(1024)
print(data.decode())
#my_socket.close()