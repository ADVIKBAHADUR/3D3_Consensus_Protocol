import socket
import threading
import time
import pickle
import random
import queue
import argparse

def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # does not need to be reachable
            s.connect(('11.247.223.253', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

class P2PNode:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.last_bad_nodes = []
        self.connected_nodes = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))

        self.message_queue = queue.Queue()
        self.message_thread = threading.Thread(target=self.process_messages)
        self.message_thread.daemon = True
        self.message_thread.start()

        self.ack_char = "ô̵̱"
        self.touch_char = "t̷̻̂"
        self.userlist_char = "é̵̡"
        self.request_userlist_char = "l̶̮͛"
        self.msg_char = "m̴̬͒"

    def add_bad_node(self, addr):
        if addr not in self.last_bad_nodes:
            self.last_bad_nodes.append(addr)

    def del_bad_node(self, addr):
        if addr in self.last_bad_nodes:
            self.last_bad_nodes.remove(addr)

    def send_message(self, message, in_node = None):
        print(f"in_node: {in_node}")
        if in_node is not None:
            if (in_node in self.last_bad_nodes):
                return
            if (in_node == (self.ip, self.port)):
                return
            if (self.connected_nodes != []):
                check_nodes = [row[:2] for row in self.connected_nodes]
                #print(f"nodez {check_nodes}")
                if in_node not in check_nodes:
                    self.connected_nodes.append(in_node[0], in_node[1], 3)
                    self.request_userlist()
            else:
                self.connected_nodes.append(in_node[0], in_node[1], 3)
                self.request_userlist()
            if (message == self.ack_char):
                self.sock.sendto(pickle.dumps(message), in_node)
                return
        else: pass
        for i, no in enumerate(self.connected_nodes):
            node = self.connected_nodes[i][0] , self.connected_nodes[i][1]
            try:
                self.connected_nodes[i] = self.connected_nodes[i][0], self.connected_nodes[i][1], 4
                self.sock.sendto(pickle.dumps(message), node)
                counter = 0
                time_start = time.time_ns()
                time_diff = random.randint(30, 40) * 10 ** 8
                while (self.connected_nodes[i][2] == 4):
                    if (time.time_ns() - time_start >= time_diff):
                        counter += 1
                        if counter >= 3:
                            counter = 0
                            self.connected_nodes.pop(i)
                            self.add_bad_node(node)
                            print(f"Removed {node}")
                            break
                        else:
                            print(f"No ACK from {node} - Resending...")
                            self.sock.sendto(pickle.dumps(message), node)
                        time_start = time.time_ns()
                        time_diff = random.randint(30, 40) * 10 ** 8
                    
            except Exception as e:
                print(f"Error sending message to {node}: {e}")

        #print(f"da_nodez {self.connected_nodes}")

    def queue_message(self, message, in_node = None):
        #print(f"queue:{message}")
        if in_node is not None:
            self.message_queue.put((message))
            self.message_queue.put((in_node))
        else:
            self.message_queue.put(message)
            self.message_queue.put(('0.0.0.0', 0000))

    def process_messages(self):
        while True:
            message = self.message_queue.get()
            in_node = self.message_queue.get()
            if (in_node == ('0.0.0.0', 0000)):
                self.send_message(message)
            else: self.send_message(message, in_node)

    def receive_messages(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                self.del_bad_node(addr)
                message = pickle.loads(data)
                print(f"msg{message}")
                if message != self.ack_char:
                    #self.sock.sendto(pickle.dumps("ACK", addr))
                    #print(f"msg1{addr}")
                    #if (self.connected_nodes != []):
                     #   check_nodes = [row[:2] for row in self.connected_nodes]
                      #  if addr not in check_nodes:
                       #     self.connected_nodes.append((self.ip, addr[1], 3))
                   # else: self.connected_nodes.append((self.ip, addr[1], 3))
                    
                    self.send_message(self.ack_char, addr)  # Send ACK

                    print(f"{addr[0]}|{addr[1]}> {message}")
                    if isinstance(message, list):
                        #print(f"msg re: {message}")
                        self.userlist_man(message, addr)
                else :
                    #print("ACK! ", end="")
                    check_nodes = [row[:2] for row in self.connected_nodes]
                    try:                    
                        i = check_nodes.index(addr)
                        #print(i)
                    except ValueError: pass
                    else:
                        self.connected_nodes[i] = self.connected_nodes[i][0], self.connected_nodes[i][1], 2
                        #print(f" HELPME {self.connected_nodes[i][2]}")
            except Exception as e:
                print(f"Error receiving message: {e}")

    def request_userlist(self):
        check_nodes = [row[:2] for row in self.connected_nodes]
        self.queue_message(self.request_userlist_char, check_nodes)

    def userlist_man(self, conn_nodes, addr):
        #print(f"\nconn: {conn_nodes}\n")
        clean_list = True
        ss = conn_nodes
        #print(f"msg ss: {ss}")
        sa = addr
        evil = self.connected_nodes
        if ss == []: 
            clean_list = False
        else:
            check_nodes = [row[:2] for row in evil]
            for addr in ss:
                if addr not in check_nodes:
                    self.queue_message(self.touch_char, addr)
                for addr in check_nodes:
                    if addr not in ss:
                        if addr != sa:
                            #print(f"addr: {addr}    self: {(self.ip, self.port)}")
                            clean_list = False
                            break
        if clean_list == False:
            self.request_userlist()

def main(value = None):

    CLEAR_SCREEN = '\u001Bc'
    print("", end=CLEAR_SCREEN)

    if value is not None:
        if value == 1:
            my_ip = '127.0.0.1'
    else:
        my_ip = get_ip()

    my_port_number = random.randint(2000, 9999)
    node = P2PNode(my_ip, my_port_number)

    print(f"\n\t--- Your IP is: {my_ip} ---\n\t--- Your Port is: {my_port_number} ---\n")

    user_input = input("Their port number (Skip if you're the first): ")

    # Start thread for receiving messages from other nodes
    receive_thread = threading.Thread(target=node.receive_messages)
    receive_thread.daemon = True
    receive_thread.start()

    if user_input != "":
        if user_input.isdigit():
            node.queue_message(node.touch_char, (my_ip, int(user_input)) )
            node.request_userlist()

    print("Send messages, or type /help for more")
    
    # Keep the main thread alive
    while True:
        while node.message_queue.empty():
            #print(node.connected_nodes)
            user_input = input()
            if user_input.lower() == 'exit':
                break
            elif user_input == "":
                #print(f"\nLIES {node.connected_nodes}\n")
                node.request_userlist()
            else:
                node.queue_message(user_input)

    node.sock.close()  # Close the socket when done

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optional integer parameter")
    parser.add_argument("-v", "--value", type=int, help="An optional integer value")
    args = parser.parse_args()

    main(args.value)




