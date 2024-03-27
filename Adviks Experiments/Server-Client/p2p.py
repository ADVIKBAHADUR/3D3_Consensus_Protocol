import socket
import threading

def handle_client(client_socket):
    while True:
        try:
            # Receive message from client
            message = client_socket.recv(1024).decode()
            if not message:
                print("Client disconnected")
                break
            print("Client:", message)
            
            # Send message back to client
            response = input("Server: ")
            client_socket.send(response.encode())
        except ConnectionResetError:
            print("Client disconnected forcibly")
            break

def receive_messages(client_socket):
    while True:
        try:
            # Receive message from server
            message = client_socket.recv(1024).decode()
            if not message:
                print("Server disconnected")
                break
            print("Server:", message)
        except ConnectionResetError:
            print("Server disconnected forcibly")
            break

def start_server():
    # Server configuration
    server_host = '0.0.0.0'
    server_port = 5555

    # Start server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_host, server_port))
    server_socket.listen(5)
    print("Server listening on {}:{}".format(server_host, server_port))

    while True:
        client_socket, addr = server_socket.accept()
        print("Client connected from:", addr)

        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

def start_client():
    # Client configuration
    client_port = 5556

    # Start client
    client_host = input("Enter the IP address to connect to: ")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((client_host, client_port))
    print("Connected to server.")

    # Start a thread to receive messages from server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Main thread to send messages to the server
    while True:
        message = input("Client: ")
        client_socket.send(message.encode())

def main():
    # Start server thread
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    # Start client thread
    client_thread = threading.Thread(target=start_client)
    client_thread.start()

if __name__ == "__main__":
    main()
