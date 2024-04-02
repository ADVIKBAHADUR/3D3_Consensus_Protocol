import socket
import threading
import pickle
import time
import sys

node_list = []  # global Variable to hold the IP addresses of the nodes in the group

#self_ip_addr = socket.gethostbyname(socket.gethostname())
self_ip_addr = '0.0.0.0'
srvr_ip_addr = '10.6.86.44'
print(f"Self IP Address= {self_ip_addr}")
srvr_tcp_port = 5090
self_tcp_port = 5091
udp_port = 5190
snd_udp_port = 5188
srvr_con_sts = "Server is Down"

# a. Send Broadcast UDP Message from Server to All Nodes to update the IP List
# b. Send CHAT Message in the group 
def send_udp_msg(udp_sock, msg):
    global node_list
    serialised_data = pickle.dumps(msg)

    print(f"Nodes available to send the message : send_udp_msg {node_list}")
    for ip_addr in node_list: 
      if(ip_addr != self_ip_addr):
        try:
          udp_sock.sendto(serialised_data,(ip_addr, udp_port))
        except socket.error as err:
          print(f"Could Not Send message to {ip_addr}: send_udp_msg  : {err}")
    

# TCP Server - Sub function - Active Connection Thread - Sends the Updated Node(IP) List
# to all Nodes in the group in UDP message
def start_conn_thread(conn,bc_sock,addr):
    global node_list
    print(f"Client Node Connected at Server : {addr}")
    if addr[0] not in node_list:
      node_list.append(addr[0])
      send_udp_msg(bc_sock,node_list)
      print(f"New Node {addr} Added in Node List \nNow Updated Node List at Server {node_list}")
    while True:
      try :
        msg = conn.recv(1024)
        if not msg:
          conn.close()
          print(f"Server Side No msf recv Error occurred")
          node_list.remove(addr[0])
          send_udp_msg(bc_sock,node_list)
          print(f"Node {addr} removed from Node List \nNow Updated Node List at Server {node_list}")
          break
      except socket.error as err:
        conn.close()
        print(f"Server Side conn.recv Error : {err}")
        node_list.remove(addr[0])
        send_udp_msg(bc_sock,node_list)
        print(f"Node {addr} removed from Node List \n Now Updated Node List at Server {node_list}")
        break


# TCP Server Thread - Accepts the TCP connections and Active Connection Threads
def start_server():
    global node_list
    bc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bc_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #it immediately frees the resources (eg port) when ever the program or thread goes down
    bc_sock.bind((self_ip_addr, udp_port))

    srvr_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srvr_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srvr_sock.bind((self_ip_addr, srvr_tcp_port))
    srvr_sock.listen()
    print(f"Server is Listening at {self_ip_addr} : {srvr_tcp_port}")
    while True:
        try:
          conn,addr = srvr_sock.accept()
          conn_thread = threading.Thread(target=start_conn_thread, args=(conn, bc_sock, addr,))
          conn_thread.daemon = True
          conn_thread.start()
          
        except socket.error as err:
          print(f"Socket accept Error : {err}")


# Client Node Thread - Connect to TCP Server
def start_conn():
    global srvr_con_sts
    while True:
        conn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        conn_sock.bind((self_ip_addr, self_tcp_port))
        try:
          conn_sock.connect((srvr_ip_addr, srvr_tcp_port))
          srvr_con_sts = "Server is Up" 
          while True:
            msg = conn_sock.recv(1024)
            try:
              if not msg:
                conn_sock.close()
                srvr_con_sts = "Server is Down"
                print(f"Server Down detected at Client - Reconnecting")
                break
            except socket.error as err:
              conn_sock.close()
              srvr_con_sts = "Server is Down"
              print(f"Server Down exception detected at Client - Reconnecting")
              break
        except socket.error as err:
#           print(f"Socket Connect Error : {err}")
            srvr_con_sts = "Server is Down"
            conn_sock.close()


# Client Node thread to recive IP-update-List from the Server and Chat Message 
# from others nodes in the group
def start_conn_upd():
    global node_list

    while True:
        conn_upd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conn_upd_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        conn_upd_sock.bind((self_ip_addr, udp_port))
        while True:
          msg, addr = conn_upd_sock.recvfrom(5020)
          try:
            if not msg:
              conn_upd_sock.close()
              print(f"Socket error detected at start_conn_upd - Reconnecting")
              break
            else:
              if addr[0] == srvr_ip_addr:
                node_list = pickle.loads(msg)
                #print(f"Updated IP List = {node_list}")
                print(f"Online Node List = {node_list}\n>>> ")
              else:
                dmsg = pickle.loads(msg)
                if dmsg != '' and dmsg != '\n': 
                #print(f"\nChat Message from {addr[0]} :: {pickle.loads(msg)}\n>>> ")
                  print(f"Chat Message from {addr[0]} :: {dmsg}\n>>> ")

          except socket.error as err:
            conn_upd_sock.close()
            print(f"Socket exception detected at start_conn_upd - Reconnecting")
            break


def main():
    global node_list
    global srvr_con_sts

    choice = input("Enter Node Type Server or Client : ")

    if choice.upper() == "SERVER" :
        print("Create Server Thread")
        srvr_thread = threading.Thread(target=start_server,)
        srvr_thread.daemon = True
        srvr_thread.start()
        while True:
          print(f"Total Client Thread : {threading.active_count()}")
          msg = input()
    else:
        print("Create Client Thread")
        conn_thread = threading.Thread(target=start_conn,)
        conn_thread.daemon = True
        conn_thread.start()

        print("Create Conn Update Thread at Client")
        conn_upd_thread = threading.Thread(target=start_conn_upd,)
        conn_upd_thread.daemon = True
        conn_upd_thread.start()

        while True:
            send_msg_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            send_msg_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            send_msg_sock.bind((self_ip_addr, snd_udp_port))
            print(f"Total Client Thread : {threading.active_count()}")
            print(f"{srvr_con_sts}\n>>> ")
#           print(f"Online Nodes :: {node_list}")
#           msg = input("Enter Message :")
            msg = input()
            if msg != '': 
              send_udp_msg(send_msg_sock,msg)
            print(f"Online Nodes :: {node_list}")

try:
  main()
except KeyboardInterrupt:
  print("\nKeyboardInterrupt : Program Exiting\n")
  sys.exit(0)
