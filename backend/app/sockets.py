# app/sockets.py
from flask_socketio import emit
from . import socketio

@socketio.on('message')
def handle_message(message):
    print('Received message: ' + message)
    emit('response', {'data': 'Message received!'}, broadcast=True)

@socketio.on('custom_event')
def handle_custom_event(json):
    print('Received custom event: ' + str(json))
    emit('response', {'data': 'Custom event received!'}, broadcast=True)
