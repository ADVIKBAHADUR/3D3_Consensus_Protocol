import socket
import threading

class Node:
    def __init__(self, port, initial_peer=None):
        self.port = port
        self.peers = set()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('localhost', port))
        self.server.listen(5)
        self.mutex = threading.Lock()
        self.running = True

        if initial_peer:
            self.connect_to_peer(initial_peer)

        threading.Thread(target=self.listen_for_peers).start()

    def listen_for_peers(self):
        while self.running:
            conn, addr = self.server.accept()
            threading.Thread(target=self.handle_peer_connection, args=(conn,)).start()

    def handle_peer_connection(self, conn):
        with self.mutex:
            data = conn.recv(1024).decode()
            print(f"Received data: {data}")
            if data.startswith("PEERS"):
                peer_port = int(data.split()[1])
                self.peers.add(peer_port)
                print(f"Node {self.port}: Connected to node {peer_port}, Peers: {self.peers}")
                self.send_peers(conn)
                conn.close()

    def connect_to_peer(self, peer_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', peer_port))
        sock.send("PEERS".encode())
        sock.close()

    def send_peers(self, conn):
        self.peers.add(self.port)  # Include own port in the list of peers
        peers_msg = "PEERS " + ' '.join(str(peer) for peer in self.peers)
        conn.send(peers_msg.encode())

    def stop(self):
        self.running = False
        self.server.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 nodes.py <port> [initial_peer]")
        sys.exit(1)

    port = int(sys.argv[1])
    initial_peer = int(sys.argv[2]) if len(sys.argv) > 2 else None

    node = Node(port, initial_peer)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        node.stop()
