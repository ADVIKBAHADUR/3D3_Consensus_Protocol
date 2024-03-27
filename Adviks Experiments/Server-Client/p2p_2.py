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
            response = "0"
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
    server_port = 5590

    # Start server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_host, server_port))
    server_socket.listen(5)
    print("Server listening on {}:{}".format(server_host, server_port))

    while True:
        client_socket, addr = server_socket.accept()
        print("Client connected from:", addr)

        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.setDaemon(True)  # Set as daemon thread
        client_handler.start()

def start_client():
    # Client configuration
    client_ports = [5591, 5592]  # List of server ports
    client_sockets = []  # List to hold client sockets

    # Start a thread for each server
    for client_port in client_ports:
        client_host = input("Enter the IP address of server at port {}: ".format(client_port))
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((client_host, client_port))
        client_sockets.append((client_socket, client_host, client_port))  # Append client socket, host, and port to the list
        print("Connected to server at {}:{}".format(client_host, client_port))

    # Start a thread to receive messages from each server
    for client_socket, _, _ in client_sockets:
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.setDaemon(True)  # Set as daemon thread
        receive_thread.start()

    # Main thread to send messages to selected server
    while True:
        print("Select a server to send a message:")
        for i, (_, host, port) in enumerate(client_sockets):
            print("{}. {} : {}".format(i + 1, host, port))
        choice = input("Enter your choice (1-{}): ".format(len(client_sockets)))
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(client_sockets):
            print("Invalid choice. Please enter a number between 1 and {}.".format(len(client_sockets)))
            continue
        message = input("Enter your message: ")
        selected_socket, _, _ = client_sockets[int(choice) - 1]
        selected_socket.send(message.encode())

def main():
    # Start server thread
    server_thread = threading.Thread(target=start_server)
    server_thread.setDaemon(True)  # Set as daemon thread
    server_thread.start()

    # Start client thread
    client_thread = threading.Thread(target=start_client)
    client_thread.setDaemon(True)  # Set as daemon thread
    client_thread.start()

    # Keep the main thread running
    while True:
        pass

if __name__ == "__main__":
    main()
