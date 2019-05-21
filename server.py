#!/usr/bin/env python3

import socket, select
import sys, signal


def signal_handler(sig, frame):
    print("\nShutting down!")
    serversocket.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

PORT = 5055
INTERFACE = ""
SELECT_TIMEOUT = 60
RECVBUFFER = 3000

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((INTERFACE, PORT))
serversocket.listen(5)

potential_readers = [serversocket]
potential_writers = []
potential_errs = []
while True:
    ready_to_read, ready_to_write, in_error = select.select(
        potential_readers, potential_writers, potential_errs, SELECT_TIMEOUT
    )
    if serversocket in ready_to_read:
        ready_to_read.remove(serversocket)
        (clientsocket, address) = serversocket.accept()
        potential_readers.append(clientsocket)
        # potential_writers.append(clientsocket)
    for socket in ready_to_read:
        socket.recv(RECVBUFFER)
