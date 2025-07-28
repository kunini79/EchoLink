import socket
import threading
import time

# --- Configuration ---
BROADCAST_PORT = 50000
UNICAST_PORT = 50001
BROADCAST_MESSAGE_PREFIX = "ECHOLINK_DISCOVERY"
BUFFER_SIZE = 1024
DISCOVERY_INTERVAL = 5

# --- State ---
online_users = {}  # {ip: username}

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

LOCAL_IP = get_local_ip()
USERNAME = ""

def broadcast_discovery(username):
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    while True:
        message = f"{BROADCAST_MESSAGE_PREFIX}:{username}"
        broadcast_socket.sendto(message.encode('utf-8'), ('<broadcast>', BROADCAST_PORT))
        time.sleep(DISCOVERY_INTERVAL)

def listen_for_discovery():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(("", BROADCAST_PORT))
    
    while True:
        data, addr = listen_socket.recvfrom(BUFFER_SIZE)
        message = data.decode('utf-8')
        
        if addr[0] == LOCAL_IP:
            continue

        if message.startswith(BROADCAST_MESSAGE_PREFIX):
            ip = addr[0]
            username = message.split(":")[1]
            if ip not in online_users:
                online_users[ip] = username
                print(f"\n[{time.strftime('%H:%M:%S')}] Discovered user: {username} ({ip})")
                print_prompt()

def listen_for_messages():
    unicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    unicast_socket.bind(("", UNICAST_PORT))
    
    while True:
        data, addr = unicast_socket.recvfrom(BUFFER_SIZE)
        sender_ip = addr[0]
        sender_username = online_users.get(sender_ip, "Unknown")
        message = data.decode('utf-8')
        print(f"\n[{time.strftime('%H:%M:%S')}] Message from {sender_username}: {message}")
        print_prompt()

def send_message(target_ip, message):
    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_socket.sendto(message.encode('utf-8'), (target_ip, UNICAST_PORT))
    send_socket.close()

def print_prompt():
    print(">>> ", end="", flush=True)

def main_ui():
    while True:
        command = input(">>> ").strip().lower()
        if command == "exit":
            break
        elif command == "users":
            print("--- Online Users ---")
            if not online_users:
                print("No other users found yet.")
            else:
                for ip, username in online_users.items():
                    print(f"- {username} ({ip})")
            print("--------------------")
        elif command.startswith("send"):
            parts = command.split()
            if len(parts) < 3:
                print("Usage: send <username> <message>")
                continue
            
            target_username = parts[1]
            message = " ".join(parts[2:])
            target_ip = None
            for ip, username in online_users.items():
                if username == target_username:
                    target_ip = ip
                    break
            
            if target_ip:
                send_message(target_ip, message)
                print(f"Message sent to {target_username}.")
            else:
                print(f"User '{target_username}' not found.")
        else:
            print("Unknown command. Available commands: users, send <user> <message>, exit")

if __name__ == "__main__":
    USERNAME = input("Enter your username: ").strip()
    if not USERNAME:
        USERNAME = f"User_{int(time.time()) % 1000}"

    print(f"--- Welcome to EchoLink, {USERNAME}! ---")
    print(f"Your IP is: {LOCAL_IP}")
    print("Type 'users' to see online users.")
    print("Type 'send <username> <message>' to send a message.")
    print("Type 'exit' to leave.")

    # Start background threads
    broadcast_thread = threading.Thread(target=broadcast_discovery, args=(USERNAME,), daemon=True)
    discovery_listen_thread = threading.Thread(target=listen_for_discovery, daemon=True)
    message_listen_thread = threading.Thread(target=listen_for_messages, daemon=True)
    
    broadcast_thread.start()
    discovery_listen_thread.start()
    message_listen_thread.start()

    main_ui()

    print("Exiting EchoLink. Goodbye.")