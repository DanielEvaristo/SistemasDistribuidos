# gui.py

import threading
import time
from tkinter import Tk, Toplevel, Label, Entry, Button, scrolledtext, messagebox, END, DISABLED
from networking import peer_receive, register_with_discovery_server, broadcast, peers, server, running, message_history
from message_handler import display_message

ventana = Tk()
ventana.title("Mensajería UAQ")
ventana.geometry("400x400")
ventana.resizable(0, 0)
ventana.config(bg="gray")

chat_window = scrolledtext.ScrolledText(ventana, width=50, height=15, bg="white")
chat_window.config(state=DISABLED)
chat_window.tag_config('sent', background="lightgreen")
chat_window.tag_config('received', background="lightgrey")
chat_window.tag_config('disconnect', background="red")
chat_window.pack(pady=10)

mensaje_entry = Entry(ventana, width=40)
mensaje_entry.pack(pady=5)

def send_message():
    raw_message = mensaje_entry.get()
    if raw_message:
        timestamp = str(time.time())
        message = f"{alias}: {raw_message} (ID: {timestamp})"
        message_history.add(message)
        broadcast(message, None)
        display_message(message, 'sent', chat_window)  # Pasar chat_window
        mensaje_entry.delete(0, END)

send_button = Button(ventana, text="Enviar", command=send_message)
send_button.pack(pady=5)

def salir_chat():
    global running
    running = False
    disconnect_message = f"{alias} ha salido del chat."
    display_message(disconnect_message, 'disconnect', chat_window)
    broadcast(disconnect_message, None)
    for peer in peers:
        peer.close()
    server.close()
    ventana.destroy()

salir_button = Button(ventana, text="Salir", command=salir_chat, bg="red", fg="white")
salir_button.pack(pady=5)

alias_window = Toplevel(ventana)
alias_window.title("Ingresar Alias")
alias_window.geometry("300x150")
alias_window.resizable(0, 0)

alias_label = Label(alias_window, text="Ingresa tu alias:")
alias_label.pack(pady=10)
alias_entry = Entry(alias_window)
alias_entry.pack(pady=5)

def iniciar_chat():
    global alias
    alias = alias_entry.get().strip()
    if alias:
        alias_window.destroy()
        register_with_discovery_server()
        receive_thread = threading.Thread(target=peer_receive, args=(chat_window,))
        receive_thread.start()
    else:
        messagebox.showwarning("Alias requerido", "Por favor, ingresa un alias.")

alias_button = Button(alias_window, text="Iniciar", command=iniciar_chat)
alias_button.pack(pady=5)
alias_window.protocol("WM_DELETE_WINDOW", ventana.quit)
