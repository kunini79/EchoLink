import socket
import threading
import time
from . import config
from . import state
from . import ui

def broadcast_discovery():
    try:
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        while True:
            message = f"{config.BROADCAST_MESSAGE_PREFIX}:{state.USERNAME}"
            broadcast_socket.sendto(message.encode('utf-8'), ('<broadcast>', config.BROADCAST_PORT))
            time.sleep(config.DISCOVERY_INTERVAL)
    except (socket.error, OSError) as e:
        print(f"\n[ERROR] Broadcast discovery failed: {e}")
        ui.print_prompt()


def listen_for_discovery():
    try:
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.bind(("", config.BROADCAST_PORT))
        
        while True:
            data, addr = listen_socket.recvfrom(config.BUFFER_SIZE)
            message = data.decode('utf-8')
            
            if addr[0] == state.LOCAL_IP:
                continue

            if message.startswith(config.BROADCAST_MESSAGE_PREFIX):
                ip = addr[0]
                username = message.split(":")[1]
                if ip not in state.online_users:
                    print(f"\n[{time.strftime('%H:%M:%S')}] Discovered user: {username} ({ip})")
                    ui.print_prompt()
                state.online_users[ip] = (username, time.time())
    except (socket.error, OSError) as e:
        print(f"\n[ERROR] Discovery listener failed: {e}")
        ui.print_prompt()


def listen_for_messages():
    try:
        unicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        unicast_socket.bind(("", config.UNICAST_PORT))
        
        while True:
            data, addr = unicast_socket.recvfrom(config.BUFFER_SIZE)
            sender_ip = addr[0]
            sender_username = state.online_users.get(sender_ip, ("Unknown", None))[0]
            message = data.decode('utf-8')
            print(f"\n[{time.strftime('%H:%M:%S')}] Message from {sender_username}: {message}")
            ui.print_prompt()
    except (socket.error, OSError) as e:
        print(f"\n[ERROR] Message listener failed: {e}")
        ui.print_prompt()


def send_message(target_ip, message):
    try:
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        send_socket.sendto(message.encode('utf-8'), (target_ip, config.UNICAST_PORT))
        send_socket.close()
    except (socket.error, OSError) as e:
        print(f"\n[ERROR] Failed to send message to {target_ip}: {e}")
        ui.print_prompt()

def check_stale_users():
    while True:
        stale_users = []
        for ip, (username, last_seen) in state.online_users.items():
            if time.time() - last_seen > config.DISCOVERY_INTERVAL * 2:
                stale_users.append(ip)

        for ip in stale_users:
            username = state.online_users[ip][0]
            del state.online_users[ip]
            print(f"\n[{time.strftime('%H:%M:%S')}] User has gone offline: {username} ({ip})")
            ui.print_prompt()

        time.sleep(config.DISCOVERY_INTERVAL)
