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
        elif command.startswith("add"):
            parts = command.split()
            if len(parts) < 2:
                print("Usage: add <username>")
                continue

            friend_username = parts[1]
            if state.add_friend(friend_username):
                print(f"Added {friend_username} to your friends list.")
            else:
                print(f"{friend_username} is already in your friends list.")
        elif command == "friends":
            print("--- Friends List ---")
            if not state.friends:
                print("Your friends list is empty.")
            else:
                for friend in state.friends:
                    print(f"- {friend}")
            print("--------------------")
        else:
            print("Unknown command. Available commands: users, send <user> <message>, add <user>, friends, exit")
