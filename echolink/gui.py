from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from . import state
from . import network
import queue

# A queue to pass messages from the network threads to the GUI
message_queue = queue.Queue()

class UserList(RecycleView):
    def __init__(self, **kwargs):
        super(UserList, self).__init__(**kwargs)
        self.data = []

    def update_users(self, dt):
        self.data = [{'text': f"{username} ({ip})"} for ip, (username, last_seen) in state.online_users.items()]

class ChatLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(ChatLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.history = Label(text='Welcome to EchoLink!\n', size_hint_y=0.7)
        self.add_widget(self.history)

        self.user_list = UserList(size_hint_y=0.2)
        self.add_widget(self.user_list)
        Clock.schedule_interval(self.user_list.update_users, 1.0) # Update user list every second

        input_layout = BoxLayout(size_hint_y=0.1, orientation='horizontal')
        self.add_widget(input_layout)

        self.user_selector = Spinner(text='Select User')
        input_layout.add_widget(self.user_selector)
        Clock.schedule_interval(self.update_user_selector, 1.0)

        self.new_message = TextInput(multiline=False, readonly=False)
        input_layout.add_widget(self.new_message)

        self.send_button = Button(text='Send')
        self.send_button.bind(on_press=self.send_message)
        input_layout.add_widget(self.send_button)

        Clock.schedule_interval(self.check_queue, 0.1)

    def update_user_selector(self, dt):
        self.user_selector.values = [f"{username} ({ip})" for ip, (username, last_seen) in state.online_users.items()]

    def send_message(self, instance):
        message = self.new_message.text
        target = self.user_selector.text
        if message and target != 'Select User':
            self.history.text += f'[ME]: {message}\n'
            self.new_message.text = ''

            # Extract IP from "username (ip)"
            target_ip = target.split('(')[1].split(')')[0]
            network.send_message(target_ip, message)

    def check_queue(self, dt):
        while not message_queue.empty():
            message = message_queue.get()
            self.history.text += message + '\n'

class EchoLinkGUI(App):
    def build(self):
        return ChatLayout()

def gui_listen_for_messages():
    try:
        unicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        unicast_socket.bind(("", config.UNICAST_PORT))

        while True:
            data, addr = unicast_socket.recvfrom(config.BUFFER_SIZE)
            sender_ip = addr[0]
            sender_username = state.online_users.get(sender_ip, ("Unknown", None))[0]
            message = data.decode('utf-8')
            message_queue.put(f"[{sender_username}]: {message}")
    except (socket.error, OSError) as e:
        message_queue.put(f"[ERROR] Message listener failed: {e}")

def gui_listen_for_discovery():
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
                    message_queue.put(f"Discovered user: {username} ({ip})")
                state.online_users[ip] = (username, time.time())
    except (socket.error, OSError) as e:
        message_queue.put(f"[ERROR] Discovery listener failed: {e}")

# We need to replace the network listeners with versions that put messages in the queue
import socket
import time
from . import config

network.listen_for_messages = gui_listen_for_messages
network.listen_for_discovery = gui_listen_for_discovery
