import socket
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import sys
import os
import time
from datetime import datetime

os.system("color 0A")

def caesar_encrypt(text, key=3):
    return ''.join(chr((ord(char) + key) % 65536) for char in text)

def caesar_decrypt(text, key=3):
    return ''.join(chr((ord(char) - key) % 65536) for char in text)

class DebugWindow:
    def __init__(self, start_time):
        self.start_time = start_time
        self.msg_sent = 0
        self.msg_received = 0
        self.root = tk.Tk()
        self.root.title("🟢 Chat Debug Console")
        self.root.geometry("800x500")
        self.root.configure(bg="#000000")

        title = tk.Label(self.root, text="🔒 Encrypted Chat Debug Window",
                         font=("Consolas", 16, "bold"), fg="#00FF00", bg="#000000")
        title.pack(pady=5)

        self.conn_label = tk.Label(self.root, text="Connection: Not established",
                                   font=("Consolas", 12), fg="#00FF00", bg="#000000")
        self.conn_label.pack()

        self.status_label = tk.Label(self.root, text="Status: Idle",
                                     font=("Consolas", 11), fg="#00FF00", bg="#000000")
        self.status_label.pack()

        self.stats_label = tk.Label(self.root, text="Messages Sent: 0 | Messages Received: 0 | Uptime: 0s",
                                    font=("Consolas", 10), fg="#00FF00", bg="#000000")
        self.stats_label.pack()

        self.text_area = ScrolledText(self.root, width=95, height=20, state='disabled',
                                      font=("Consolas", 10), bg="#000000", fg="#00FF00", insertbackground="white")
        self.text_area.pack(pady=10)

        self.command_entry = tk.Entry(self.root, font=("Consolas", 10), bg="#000000", fg="#00FF00", insertbackground="white")
        self.command_entry.pack(fill=tk.X, padx=5)
        self.command_entry.bind("<Return>", self.process_command)

        self.autoscroll = True
        self.root.protocol("WM_DELETE_WINDOW", self.exit_chat)
        self.update_uptime()

    def log(self, message, level="info"):
        self.root.after(0, self._log_safe, message, level)

    def _log_safe(self, message, level):
        self.text_area.config(state='normal')
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        color = "#00FF00" if level == "info" else "#FFFF00" if level == "warn" else "#FF0000"
        self.text_area.insert(tk.END, f"{timestamp} {message}\n", level)
        self.text_area.tag_config(level, foreground=color)
        if self.autoscroll:
            self.text_area.see(tk.END)
        self.text_area.config(state='disabled')

    def set_connection(self, ip):
        self.root.after(0, lambda: self.conn_label.config(text=f"Server <==> Client (6000: {ip})"))

    def update_status(self, status):
        self.root.after(0, lambda: self.status_label.config(text=f"Status: {status}"))

    def update_stats(self):
        uptime = int(time.time() - self.start_time)
        text = f"Messages Sent: {self.msg_sent} | Messages Received: {self.msg_received} | Uptime: {uptime}s"
        self.stats_label.config(text=text)

    def process_command(self, event=None):
        cmd = self.command_entry.get().strip()
        self.command_entry.delete(0, tk.END)
        if cmd == "/save":
            filename = f"chat_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.text_area.get("1.0", tk.END))
            self.log(f"[DEBUG] Log saved to {filename}", "warn")
        elif cmd == "/clear":
            self.text_area.config(state='normal')
            self.text_area.delete("1.0", tk.END)
            self.text_area.config(state='disabled')
            self.log("[DEBUG] Log cleared.", "warn")
        elif cmd == "/exit":
            self.exit_chat()
        elif cmd == "/help":
            self.log("[DEBUG] Available commands: /save, /clear, /exit, /help, /autoscroll", "warn")
        elif cmd == "/autoscroll":
            self.autoscroll = not self.autoscroll
            self.log(f"[DEBUG] Auto-scroll {'enabled' if self.autoscroll else 'disabled'}.", "warn")
        else:
            self.log(f"[DEBUG] Unknown command: {cmd}", "warn")

    def update_uptime(self):
        self.update_stats()
        self.root.after(1000, self.update_uptime)

    def exit_chat(self):
        self.log("[!] Exiting chat...", "error")
        sys.exit(0)

def handle_recv(sock, debug):
    try:
        while True:
            data = sock.recv(1024)
            if data:
                decrypted = caesar_decrypt(data.decode())
                debug.msg_received += 1
                debug.update_stats()
                print(f"\n[Received]: {decrypted}\n[You]: ", end="", flush=True)
                debug.log(f"[Received]: {decrypted}")
            else:
                debug.log("[!] Connection closed by peer.", "error")
                debug.update_status("Connection closed.")
                break
    except Exception as e:
        debug.log(f"[!] Error in receiver: {e}", "error")

def handle_send(sock, debug):
    try:
        while True:
            msg = input("[You]: ")
            encrypted = caesar_encrypt(msg)
            sock.send(encrypted.encode())
            debug.msg_sent += 1
            debug.update_stats()
            debug.log(f"[You]: {msg}")
    except Exception as e:
        debug.log(f"[!] Error in sender: {e}", "error")

def server(debug):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 6000))
    s.listen(1)
    debug.log("[Server] Waiting for connection on port 6000...")
    debug.update_status("Waiting for connection...")
    conn, addr = s.accept()
    debug.log(f"[Server] Connected by {addr}")
    debug.set_connection(addr[0])
    debug.update_status(f"Connected to {addr[0]}")

    threading.Thread(target=handle_recv, args=(conn, debug), daemon=True).start()
    handle_send(conn, debug)

def client(debug):
    target_ip = input("Enter peer IP to connect as client: ").strip()
    c = socket.socket()
    try:
        c.connect((target_ip, 6000))
        debug.log(f"[Client] Connected to {target_ip}")
        debug.set_connection(target_ip)
        debug.update_status(f"Connected to {target_ip}")
    except Exception as e:
        debug.log(f"[!] Could not connect: {e}", "error")
        debug.update_status("Connection failed.")
        sys.exit(1)

    threading.Thread(target=handle_recv, args=(c, debug), daemon=True).start()
    handle_send(c, debug)

if __name__ == '__main__':
    start_time = time.time()
    debug_window = DebugWindow(start_time)
    threading.Thread(target=server, args=(debug_window,), daemon=True).start()
    threading.Thread(target=client, args=(debug_window,), daemon=True).start()
    debug_window.root.mainloop()
