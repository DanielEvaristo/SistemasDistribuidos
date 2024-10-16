# networking.py

import socket
import threading
from config import host, discovery_host, discovery_port
from message_handler import display_message

# Variables globales
peers = []
message_history = set()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, 0))
port = server.getsockname()[1]
server.listen()
running = True

def register_with_discovery_server():
    try:
        discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        discovery_socket.connect((discovery_host, discovery_port))
        peer_info = f"{host}:{port}"
        discovery_socket.send(peer_info.encode('utf-8'))
        
        data = discovery_socket.recv(4096).decode('utf-8')
        peer_list = data.split('\n')
        
        for peer in peer_list:
            if peer != peer_info:
                ip, peer_port = peer.split(':')
                connect_to_peer(ip, int(peer_port))
        
        discovery_socket.close()
    except Exception as e:
        print(f"Could not connect to discovery server: {e}")

def peer_receive(chat_window):
    while running:
        try:
            client, address = server.accept()
            peers.append(client)
            thread = threading.Thread(target=handle_peer, args=(client, address, chat_window))
            thread.start()
        except OSError:
            break

def handle_peer(peer, address, chat_window):
    while running:
        try:
            message = peer.recv(1024).decode('utf-8')
            if message and message not in message_history:
                message_history.add(message)
                display_message(message, 'received', chat_window)
                broadcast(message, peer)
        except:
            disconnection_message = f"{address} se ha desconectado."
            display_message(disconnection_message, 'disconnect', chat_window)
            peers.remove(peer)
            peer.close()
            break

def broadcast(message, sender):
    for peer in peers:
        if peer != sender:
            try:
                peer.send(message.encode('utf-8'))
            except:
                peer.close()
                peers.remove(peer)

def connect_to_peer(peer_ip, peer_port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((peer_ip, peer_port))
    peers.append(client)
    thread = threading.Thread(target=handle_peer, args=(client, (peer_ip, peer_port), None))
    thread.start()
