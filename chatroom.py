import socket
import threading
import pickle
import time
import sys

node_list = []  # global Variable to hold the IP addresses of the nodes in the group
udp_port_list = [] # global Variable to hold the port list of the nodes in the group
tcp_port_list = []

#self_ip_addr = socket.gethostbyname(socket.gethostname())
self_ip_addr = '0.0.0.0'    # Does NOT need changing
srvr_ip_addr = '0.0.0.0'    # Does need changing
srvr_tcp_port = 5090        # Static - does not change
self_tcp_port = 0        # This should change for each IP
udp_port = 0             # Port where data is received
snd_udp_port = 4000         # Port where data is sent
srvr_con_sts = "Server is Down"
your_prompt = "(You) >>> "

host_number = 0
client_number_list = []

UP = '\033[1A'
CLEAR = '\x1b[2K'
CLEAR_SCREEN = '\u001Bc'

sent_ips = 0
ACKED_ips = 0
wait_for_ACK = False

ACK_char = "ơ̴̧̧̨̧̮̩͖̮͙͉͇͖̳͓̣̰̥͔͈̙͚̥̭͖͍̭͖̙̼̰͖̗̗̮̳͎̤̘̱̠͔̄̅̎̊̉͐̓̚͜͜ͅͅ"

def set_ports():
    global srvr_tcp_port
    global self_tcp_port
    global udp_port
    global snd_udp_port

    if udp_port != 0:
        udp_port = random.rand_int(2000, 18000)
        while (udp_port == srvr_tcp_port) or (udp_port == snd_udp_port):
            udp_port = random.rand_int(2000, 18000)
    if self_tcp_port != 0:
        self_tcp_port = random.rand_int(2000, 18000)
        while (self_tcp_port == srvr_tcp_port) or (self_tcp_port == snd_udp_port) or (self_tcp_port == udp_port):
            self_tcp_port = random.rand_int(2000, 18000)

def set_unsigned_char(value):
    if 0 <= value <= 255:
        return value
    else:
        raise ValueError("Value must be in the range of an unsigned 8-bit number (0-255)")

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

# a. Send Broadcast UDP Message from Server to All Nodes to update the IP List
# b. Send CHAT Message in the group 
def send_udp_msg(udp_sock, msg):
    global node_list
    global port_list
    global sent_ips
    global ACKED_ips
    global wait_for_ACK
    wait_for_ACK = True
    serialised_data = pickle.dumps(msg)
    for index, port in enumerate(udp_port_list): 
      if(port != udp_port) and (node_list(index) != self_ip_addr):
        try:
          udp_sock.sendto(serialised_data,(ip_addr, udp_port))
        except socket.error as err:
          print(f"Could Not Send message to {ip_addr}: send_udp_msg  : {err}")
        else:
          sent_ips += 1
    start_time = time.clock_gettime_ns(1)
    #print(start_time)
    time_diff = 0
    max_time_diff = 12*(10**9)
    while (time_diff < max_time_diff):
        time_diff = time.clock_gettime_ns(1) - start_time
        if (ACKED_ips >= sent_ips):
            return
        time.sleep(1)
    max_time = max_time_diff /  (10**9)
    missing_users = sent_ips - ACKED_ips
    print(f"Over {max_time} seconds has passed. {missing_users} out of {sent_ips} users were not reached")
    wait_for_ACK = False
    ACKED_ips = 0
    sent_ips = 0

# Send a command to client
def send_command(send_msg_sock,msg):
    match msg.lower():
        case "/help":
            print(f"""\t/help - This Help Menu
\t/thread - Print Total Client Threads
\t/status - Print Server Status
\t/userlist - Show the list of users (nodes) connected""")
        case "/thread":
            print_client_threads()
        case "/threads":
            print_client_threads()
        case "/status":
            print_server_status()
        case "/userlist":
            print_userlist()
        case default:
            print(f"Invalid command. Type \"\help\" ")

#Repeated print functions
def print_client_threads():
    print(f"Total Client Thread : {threading.active_count()}")

def print_server_status():
    global srvr_con_sts
    global srvr_ip_addr
    print(f"{srvr_con_sts} At {srvr_ip_addr}")

def print_userlist():
    global node_list
    print(f"Nodes available to send the message : {node_list}")    

def exists_in_these_lists(item1, item2, list1, list2):   
    for index, list2item in enumerate(list2):
        if list2item == item2:
            if list1[index] == item1:
                return index
    return None

# TCP Server - Sub function - Active Connection Thread - Sends the Updated Node(IP) List
# to all Nodes in the group in UDP message
def start_conn_thread(conn,bc_sock,addr):
    global node_list
    global tcp_port_list
    global client_number_list
    print(f"Client Node Connected at Server : {addr}")
    print(f"Connection is: {conn}")
    if not exists_in_these_lists(addr[0], addr[1], node_list, tcp_port_list):
      node_list.append(addr[0])
      tcp_port_list.append(addr[1])
      send_udp_msg(bc_sock,node_list)
      print(f"New Node {addr} Added in Node List \nNow Updated Node List at Server {node_list}")
    while True:
      try :
        msg = conn.recv(1024)
        if not msg:
          conn.close()
          print(f"Server Side No msf recv Error occurred")
          ind = exists_in_these_lists(addr[0], addr[1], node_list, tcp_port_list)
          if (ind):
                node_list.pop(ind)
                tcp_port_list.pop(ind)
                send_udp_msg(bc_sock,node_list)
                print(f"Node {addr} removed from Node List \nNow Updated Node List at Server {node_list}")
          break
      except socket.error as err:
        conn.close()
        print(f"Server Side conn.recv Error : {err}")
        ind = exists_in_these_lists(addr[0], addr[1], node_list, tcp_port_list)
        if (ind):
            node_list.pop(ind)
            tcp_port_list.pop(ind)
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
          srvr_con_sts = "Server is UP" 
          while True:
            msg = conn_sock.recv(1024)
            try:
              if not msg:
                conn_sock.close()
                srvr_con_sts = "Server is DOWN"
                print(f"Server Down detected at Client - Reconnecting")
                break
            except socket.error as err:
              conn_sock.close()
              srvr_con_sts = "Server is DOWN"
              print(f"Server Down exception detected at Client - Reconnecting")
              break
        except socket.error as err:
#           print(f"Socket Connect Error : {err}")
            srvr_con_sts = "Server is DOWN"
            conn_sock.close()


# Client Node thread to recive IP-update-List from the Server and Chat Message 
# from others nodes in the group
def start_conn_upd():
    global node_list
    global UP
    global CLEAR
    global ACKED_ips
    global ACK_char
    global wait_for_ACK

    while True:
        conn_upd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conn_upd_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        conn_upd_sock.bind((self_ip_addr, udp_port))
        while True:
          msg, addr = conn_upd_sock.recvfrom(5020)
          try:
            print(UP, end = CLEAR)
            if not msg:
              conn_upd_sock.close()
              print(f"Socket error detected at start_conn_upd - Reconnecting")
              break
            else:
              if addr[0] == srvr_ip_addr:
                node_list = pickle.loads(msg)
                #print_userlist()
              else:
                dmsg = pickle.loads(msg)
                if dmsg != '' and dmsg != '\n': 
                    if dmsg != ACK_char:
                        conn_upd_sock.sendto(pickle.dumps(ACK_char),(addr[0], udp_port))
                        print(f"{addr} | {dmsg}")
                        print(your_prompt, end = "")
                    else:
                        if (wait_for_ACK):
                            ACKED_ips += 1
          except socket.error as err:
            conn_upd_sock.close()
            print(f"Socket exception detected at start_conn_upd - Reconnecting")
            break

def main():
    global node_list
    global srvr_con_sts
    global your_prompt
    print("", end = CLEAR_SCREEN)
    self_ip_addr = get_ip()
    print(f"\n\t--- Your IP Address is: {self_ip_addr} ---\n")
    choice = input("Type \"1\" for SERVER. Or press any key for CLIENT\n>>> ")
    set_ports()
    if choice == "1" :
        print("Creating Server Thread...", end='')
        srvr_thread = threading.Thread(target=start_server,)
        srvr_thread.daemon = True
        srvr_thread.start()
        print(" DONE!")
        while True:
          print(f"Total Client Thread : {threading.active_count()}")
          msg = input()
    else:
        nickname = input("Enter you nickname >>> ")
        while(len(nickname) > 10):
            nickname = input("The nickname must be less than 10 characters >>> ")
        your_prompt = nickname + your_prompt

        print("Creating Client Thread...", end='')
        conn_thread = threading.Thread(target=start_conn,)
        conn_thread.daemon = True
        conn_thread.start()
        print(" DONE!")

        print("Creating Update Thread...", end='')
        conn_upd_thread = threading.Thread(target=start_conn_upd,)
        conn_upd_thread.daemon = True
        conn_upd_thread.start()
        print(" DONE!")

        print_client_threads()
        print_server_status()

        print("Type \"\help\" for a list of commands...\n\n")

        while True:
            send_msg_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            send_msg_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            send_msg_sock.bind((self_ip_addr, snd_udp_port))
            msg = input(your_prompt)
            while(len(msg) > 100):
                msg = input("The msg must be less than 100 characters >>> ")
            if msg != '':
              if msg[0] == '/':
                send_command(send_msg_sock,msg)
              else:
                if node_list == []:
                    print(UP, end = CLEAR)
                    print(f"{your_prompt}{msg} ....... No other users connected...")
                else:
                    msg = "{nickname} : {msg}"
                    send_udp_msg(send_msg_sock,msg)
try:
  main()
except KeyboardInterrupt:
  print("\nKeyboardInterrupt : Program Exiting\n")
  sys.exit(0)
