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

def main():
    host = '127.0.0.1'
    port = 40674

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print("Server listening on {}:{}".format(host, port))

    while True:
        client_socket, addr = server_socket.accept()
        print("Client connected from:", addr)

        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    main()
