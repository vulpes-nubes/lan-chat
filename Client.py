import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import hashlib
import os

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")
        
        self.chat_area = scrolledtext.ScrolledText(root)
        self.chat_area.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        self.chat_area.config(state=tk.DISABLED)

        self.message_entry = tk.Entry(root)
        self.message_entry.pack(padx=20, pady=5, fill=tk.X)
        self.message_entry.bind("<Return>", self.send_message)
        
        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(padx=20, pady=10)

        self.key = self.load_key()

        self.SERVER, self.PORT = self.discover_server()
        if not self.SERVER:
            messagebox.showerror("Error", "No server found on the local network.")
            root.destroy()
            return
        
        self.ADDR = (self.SERVER, self.PORT)
        
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def load_key(self):
        """Load the SHA-256 key from the key file."""
        try:
            with open("client_key.txt", "r") as key_file:
                return key_file.read().strip()
        except FileNotFoundError:
            messagebox.showerror("Error", "Key file not found. Make sure 'client_key.txt' exists.")
            self.root.destroy()
            return None

    def hash_message(self, message):
        """Encrypts the message using SHA-256 and the shared key."""
        return hashlib.sha256((message + self.key).encode()).hexdigest()

    def verify_hash(self, hashed_message, original_message):
        """Verifies the hash of the received message."""
        return self.hash_message(original_message) == hashed_message

    def discover_server(self):
        """Sends a UDP broadcast to discover available servers on the local network."""
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        broadcast_message = "DISCOVER_SERVER".encode('utf-8')
        broadcast_socket.sendto(broadcast_message, ('<broadcast>', 5556))
        
        broadcast_socket.settimeout(3)
        
        try:
            response, server_addr = broadcast_socket.recvfrom(1024)
            server_ip, server_port = response.decode('utf-8').split(':')
            return server_ip, int(server_port)
        except socket.timeout:
            return None, None
        finally:
            broadcast_socket.close()

    def receive_messages(self):
        while True:
            try:
                data = self.client.recv(1024).decode('utf-8')
                if data:
                    try:
                        original_message, received_hash = data.split('||')
                        if self.verify_hash(received_hash, original_message):
                            self.chat_area.config(state=tk.NORMAL)
                            self.chat_area.insert(tk.END, original_message + '\n')
                            self.chat_area.yview(tk.END)
                            self.chat_area.config(state=tk.DISABLED)
                        else:
                            print("Received a message with an invalid hash!")
                    except ValueError:
                        print("Received an improperly formatted message.")
            except:
                self.client.close()
                break

    def send_message(self, event=None):
        message = self.message_entry.get()
        if message:
            hashed_message = self.hash_message(message)
            data = f"{message}||{hashed_message}"
            self.client.send(data.encode('utf-8'))
            self.message_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
