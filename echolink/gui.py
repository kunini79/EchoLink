

import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import threading

class ChatGUI(tk.Tk):
    def __init__(self, network_manager):
        super().__init__()
        self.network_manager = network_manager
        self.title(f"EchoLink - {network_manager.username}")
        self.geometry("400x500")

        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # --- Widgets ---
        self.user_list = tk.Listbox(self, width=15)
        self.chat_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, state='disabled')
        self.message_entry = tk.Entry(self, width=40)
        self.send_button = tk.Button(self, text="Send", command=self._send_message)

        # --- Layout ---
        self.user_list.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.chat_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.send_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.message_entry.bind("<Return>", self._send_message)

    def _on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.network_manager.stop()
            self.destroy()

    def _send_message(self, event=None):
        message = self.message_entry.get()
        if not message:
            return

        selected_user_index = self.user_list.curselection()
        if not selected_user_index:
            messagebox.showwarning("No User Selected", "Please select a user from the list to send a message.")
            return

        target_username = self.user_list.get(selected_user_index)
        target_ip = None
        for ip, username in self.network_manager.online_users.items():
            if username == target_username:
                target_ip = ip
                break

        if target_ip:
            if self.network_manager.send_message(target_ip, message):
                self._display_message(f"You: {message}")
                self.message_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Message Failed", f"Could not send message to {target_username}. They may have gone offline.")
        else:
            messagebox.showerror("User Not Found", f"User {target_username} could not be found.")

    def _display_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def update_user_list(self, users):
        self.user_list.delete(0, tk.END)
        for ip, username in users.items():
            self.user_list.insert(tk.END, username)

    def receive_message(self, username, message):
        self._display_message(f"{username}: {message}")

    def run(self):
        self.mainloop()

