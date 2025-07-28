
import socket
import threading
import time

# --- Configuration ---
BROADCAST_PORT = 50000
TCP_PORT = 50001
BROADCAST_MESSAGE_PREFIX = "ECHOLINK_DISCOVERY"
BUFFER_SIZE = 1024
DISCOVERY_INTERVAL = 5

class NetworkManager:
    def __init__(self, username, message_callback, user_update_callback):
        self.username = username
        self.message_callback = message_callback
        self.user_update_callback = user_update_callback
        self.online_users = {}
        self.local_ip = self._get_local_ip()
        self.running = True

        self.broadcast_thread = threading.Thread(target=self._broadcast_discovery, daemon=True)
        self.discovery_listen_thread = threading.Thread(target=self._listen_for_discovery, daemon=True)
        self.tcp_listen_thread = threading.Thread(target=self._listen_for_tcp, daemon=True)

    def start(self):
        self.broadcast_thread.start()
        self.discovery_listen_thread.start()
        self.tcp_listen_thread.start()

    def stop(self):
        self.running = False

    def _get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def _broadcast_discovery(self):
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        while self.running:
            message = f"{BROADCAST_MESSAGE_PREFIX}:{self.username}"
            broadcast_socket.sendto(message.encode('utf-8'), ('<broadcast>', BROADCAST_PORT))
            time.sleep(DISCOVERY_INTERVAL)

    def _listen_for_discovery(self):
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.bind(("", BROADCAST_PORT))
        
        while self.running:
            data, addr = listen_socket.recvfrom(BUFFER_SIZE)
            message = data.decode('utf-8')
            
            if addr[0] == self.local_ip:
                continue

            if message.startswith(BROADCAST_MESSAGE_PREFIX):
                ip = addr[0]
                username = message.split(":", 1)[1]
                if ip not in self.online_users:
                    self.online_users[ip] = username
                    self.user_update_callback(self.online_users)

    def _listen_for_tcp(self):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.bind(("", TCP_PORT))
        tcp_socket.listen(5)
        
        while self.running:
            conn, addr = tcp_socket.accept()
            with conn:
                data = conn.recv(BUFFER_SIZE)
                if data:
                    sender_ip = addr[0]
                    sender_username = self.online_users.get(sender_ip, "Unknown")
                    message = data.decode('utf-8')
                    self.message_callback(sender_username, message)

    def send_message(self, target_ip, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((target_ip, TCP_PORT))
                s.sendall(message.encode('utf-8'))
        except ConnectionRefusedError:
            # User might have gone offline
            if target_ip in self.online_users:
                del self.online_users[target_ip]
                self.user_update_callback(self.online_users)
            return False
        return True
