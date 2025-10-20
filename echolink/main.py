import threading
import time
import sys
from . import state
from . import network
from . import ui
from . import gui

def main():
    state.USERNAME = input("Enter your username: ").strip()
    if not state.USERNAME:
        state.USERNAME = f"User_{int(time.time()) % 1000}"

    print(f"--- Welcome to EchoLink, {state.USERNAME}! ---")
    print(f"Your IP is: {state.LOCAL_IP}")

    # Start background threads
    broadcast_thread = threading.Thread(target=network.broadcast_discovery, daemon=True)
    discovery_listen_thread = threading.Thread(target=network.listen_for_discovery, daemon=True)
    message_listen_thread = threading.Thread(target=network.listen_for_messages, daemon=True)
    stale_user_thread = threading.Thread(target=network.check_stale_users, daemon=True)

    broadcast_thread.start()
    discovery_listen_thread.start()
    message_listen_thread.start()
    stale_user_thread.start()

    if '--cli' in sys.argv:
        print("Type 'users' to see online users.")
        print("Type 'send <username> <message>' to send a message.")
        print("Type 'exit' to leave.")
        ui.main_ui()
        print("Exiting EchoLink. Goodbye.")
    else:
        gui.EchoLinkGUI().run()

if __name__ == "__main__":
    main()
