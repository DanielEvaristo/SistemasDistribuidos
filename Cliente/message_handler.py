# message_handler.py

from tkinter import END, NORMAL, DISABLED

def display_message(message, message_type, chat_window):
    chat_window.config(state=NORMAL)
    if message_type == 'sent':
        chat_window.insert(END, message + "\n", 'sent')
    elif message_type == 'received':
        chat_window.insert(END, message + "\n", 'received')
    elif message_type == 'disconnect':
        chat_window.insert(END, message + "\n", 'disconnect')
    chat_window.config(state=DISABLED)
    chat_window.yview(END)
