import socket
import threading

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

def main():
    host = '192.168.221.187'
    port = 5555

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    print("Connected to server.")

    # Start a thread to receive messages from server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Main thread to send messages to the server
    while True:
        message = input("Client: ")
        client_socket.send(message.encode())

if __name__ == "__main__":
    main()
