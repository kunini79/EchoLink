
import tkinter as tk
from tkinter import simpledialog
from echolink.gui import ChatGUI
from echolink.network import NetworkManager
import time

def main():
    # We need a root window to show the dialog, but we don't want it to be the main app window
    root = tk.Tk()
    root.withdraw() # Hide the root window

    username = simpledialog.askstring("Username", "Please enter your username:", parent=root)
    if not username:
        username = f"User_{int(time.time()) % 1000}"
    
    root.destroy() # We don't need this root window anymore

    # --- Callbacks ---
    def on_message_received(sender, message):
        app.receive_message(sender, message)

    def on_user_update(users):
        app.update_user_list(users)

    # --- Initialization ---
    network = NetworkManager(username, on_message_received, on_user_update)
    app = ChatGUI(network)

    # --- Start Application ---
    network.start()
    app.run() # This blocks until the GUI is closed
    network.stop()

if __name__ == "__main__":
    main()
