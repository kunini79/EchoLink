from . import state
from . import network

def print_prompt():
    print(">>> ", end="", flush=True)

def main_ui():
    while True:
        command = input(">>> ").strip().lower()
        if command == "exit":
            break
        elif command == "users":
            print("--- Online Users ---")
            if not state.online_users:
                print("No other users found yet.")
            else:
                for ip, (username, last_seen) in state.online_users.items():
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
            for ip, (username, last_seen) in state.online_users.items():
                if username == target_username:
                    target_ip = ip
                    break

            if target_ip:
                network.send_message(target_ip, message)
                print(f"Message sent to {target_username}.")
            else:
                print(f"User '{target_username}' not found.")
        else:
            print("Unknown command. Available commands: users, send <user> <message>, exit")
