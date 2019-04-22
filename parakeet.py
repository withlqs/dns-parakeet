#!/usr/bin/env python3

import argparse
import json
import socket
import socketserver

dns_server_list = []


class UDPMessageHandler(socketserver.BaseRequestHandler):

    def handle(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        for dns_server in dns_server_list:
            sock.sendto(self.request[0], (dns_server, 53))
        for dns_server in dns_server_list:
            sock.sendto(self.request[0], (dns_server, 53))

        result = sock.recv(512)
        self.request[1].sendto(result, self.client_address)
        sock.close()


def main():
    global dns_server_list
    parser = argparse.ArgumentParser(
        description='forward each dns request to multiple servers to accelerate dns resolving')
    parser.add_argument(
        'list',
        # required=True,
        type=argparse.FileType('r'),
        help='specify servers\' list'
    )

    # server_list_file = open(parser.parse_args().list)
    read_server_list = json.load(parser.parse_args().list)
    for server in read_server_list:
        dns_server_list.append(server)

    server = socketserver.ThreadingUDPServer(('127.0.0.1', 53), UDPMessageHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
