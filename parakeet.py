#!/usr/bin/env python3

import socket
import socketserver

dns_server_list = [
    '114.114.114.114',
    '114.114.115.115',
    '119.29.29.29',
    '119.28.28.28',
    '223.5.5.5',
    '223.6.6.6',
]


class UDPMessageHandler(socketserver.BaseRequestHandler):

    def handle(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        for dns_server in dns_server_list:
            sock.sendto(self.request[0], (dns_server, 53))

        result = sock.recv(512)
        self.request[1].sendto(result, self.client_address)
        sock.close()


if __name__ == "__main__":
    server = socketserver.UDPServer(('127.0.0.1', 53), UDPMessageHandler)
    server.serve_forever()
