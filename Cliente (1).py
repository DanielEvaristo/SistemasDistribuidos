import threading
import socket
import time
from tkinter import *
from tkinter import scrolledtext
from tkinter import messagebox

# Crear la ventana de la interfaz gráfica
ventana = Tk()
ventana.title("Mensajería UAQ")
ventana.geometry("400x400")
ventana.resizable(0, 0)
ventana.iconbitmap("Logo.ico")
ventana.config(bg="gray")

# Variables de configuración inicial
discovery_host = '127.0.0.1'
discovery_port = 5000
host = '127.0.0.1'

# Asignar un puerto automáticamente
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, 0))
port = server.getsockname()[1]
server.listen()

# Lista de peers conectados y el historial de mensajes recientes
peers = []
message_history = set()
alias = ""
running = True  # Variable para controlar el estado de conexión del cliente

# Función para registrar el Peer en el servidor de descubrimiento
def register_with_discovery_server():
    try:
        discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        discovery_socket.connect((discovery_host, discovery_port))
        peer_info = f"{host}:{port}"
        discovery_socket.send(peer_info.encode('utf-8'))
        
        # Recibir lista de peers
        data = discovery_socket.recv(4096).decode('utf-8')
        peer_list = data.split('\n')
        
        print("Connected peers from discovery server:")
        for peer in peer_list:
            if peer != peer_info:
                ip, peer_port = peer.split(':')
                connect_to_peer(ip, int(peer_port))
        
        discovery_socket.close()
    except Exception as e:
        print(f"Could not connect to discovery server: {e}")

# Función para escuchar conexiones entrantes
def peer_receive():
    while running:
        try:
            client, address = server.accept()
            print(f"Connection established with {str(address)}")
            peers.append(client)
            thread = threading.Thread(target=handle_peer, args=(client, address))
            thread.start()
        except OSError:
            break

# Función para manejar mensajes de los peers conectados
def handle_peer(peer, address):
    while running:
        try:
            message = peer.recv(1024).decode('utf-8')
            if message and message not in message_history:
                message_history.add(message)
                display_message(message, 'received')
                broadcast(message, peer)
        except:
            # Manejo de desconexión del cliente
            disconnection_message = f"{address} se ha desconectado."
            print(disconnection_message)
            display_message(disconnection_message, 'disconnect')
            peers.remove(peer)
            peer.close()
            break

# Función para enviar mensajes a todos los peers
def broadcast(message, sender):
    for peer in peers:
        if peer != sender:
            try:
                peer.send(message.encode('utf-8'))
            except:
                peer.close()
                peers.remove(peer)

# Función para conectarse a otros peers
def connect_to_peer(peer_ip, peer_port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((peer_ip, peer_port))
    peers.append(client)
    print(f"Connected to peer at {peer_ip}:{peer_port}")
    thread = threading.Thread(target=handle_peer, args=(client, (peer_ip, peer_port)))
    thread.start()

# Función para enviar mensajes manualmente
def send_message():
    raw_message = mensaje_entry.get()
    if raw_message:
        timestamp = str(time.time())
        message = f"{alias}: {raw_message} (ID: {timestamp})"
        message_history.add(message)
        broadcast(message, None)
        display_message(message, 'sent')
        mensaje_entry.delete(0, END)

# Función para mostrar el mensaje en la ventana de chat con colores diferenciados
def display_message(message, message_type):
    chat_window.config(state=NORMAL)
    if message_type == 'sent':
        chat_window.insert(END, message + "\n", 'sent')
    elif message_type == 'received':
        chat_window.insert(END, message + "\n", 'received')
    elif message_type == 'disconnect':
        chat_window.insert(END, message + "\n", 'disconnect')
    chat_window.config(state=DISABLED)
    chat_window.yview(END)

# Función para iniciar la aplicación después de ingresar el alias
def iniciar_chat():
    global alias
    alias = alias_entry.get().strip()
    if alias:
        alias_window.destroy()
        register_with_discovery_server()
        receive_thread = threading.Thread(target=peer_receive)
        receive_thread.start()
    else:
        messagebox.showwarning("Alias requerido", "Por favor, ingresa un alias.")

# Función para salir del chat
def salir_chat():
    global running
    running = False
    disconnect_message = f"{alias} ha salido del chat."
    display_message(disconnect_message, 'disconnect')
    broadcast(disconnect_message, None)
    for peer in peers:
        peer.close()
    server.close()
    ventana.destroy()

# Ventana de entrada para el alias
alias_window = Toplevel(ventana)
alias_window.title("Ingresar Alias")
alias_window.geometry("300x150")
alias_window.resizable(0, 0)
alias_label = Label(alias_window, text="Ingresa tu alias:")
alias_label.pack(pady=10)
alias_entry = Entry(alias_window)
alias_entry.pack(pady=5)
alias_button = Button(alias_window, text="Iniciar", command=iniciar_chat)
alias_button.pack(pady=5)
alias_window.protocol("WM_DELETE_WINDOW", ventana.quit)

# Elementos de la interfaz gráfica principal
chat_window = scrolledtext.ScrolledText(ventana, width=50, height=15, bg="white")
chat_window.config(state=DISABLED)
chat_window.tag_config('sent', background="lightgreen")
chat_window.tag_config('received', background="lightgrey")
chat_window.tag_config('disconnect', background="red")
chat_window.pack(pady=10)

mensaje_entry = Entry(ventana, width=40)
mensaje_entry.pack(pady=5)
send_button = Button(ventana, text="Enviar", command=send_message)
send_button.pack(pady=5)
salir_button = Button(ventana, text="Salir", command=salir_chat, bg="red", fg="white")
salir_button.pack(pady=5)

# Correr la ventana principal de la interfaz gráfica
ventana.mainloop()
