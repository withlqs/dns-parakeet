#!/usr/bin/env python3

import argparse
import json
import os
import socket
import socketserver

dns_server_list = []
debug = False
latency = 0.029
max_message_length = 1024
max_waiting_time = 2


class DNSRequestHandler(socketserver.BaseRequestHandler):

    @staticmethod
    def rand_request(request):
        return os.urandom(2) + request[2:]

    @staticmethod
    def restore_request(request, trans_id):
        return trans_id + request[2:]

    def handle(self):
        trans_id = self.request[0][0:2]
        # if debug: print(type(self.request[0]))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(latency)

        for dns_server in dns_server_list:
            sock.sendto(self.request[0], (dns_server, 53))
        for dns_server in dns_server_list:
            sock.sendto(DNSRequestHandler.rand_request(self.request[0]), (dns_server, 53))

        timeout = latency
        while True:
            try:
                result, address = sock.recvfrom(max_message_length)
                if debug:
                    print(address)
                # if debug: print(result)
            except socket.timeout:
                for dns_server in dns_server_list:
                    sock.sendto(DNSRequestHandler.rand_request(self.request[0]), (dns_server, 53))
                if debug:
                    print('timeout+{}'.format(timeout))
                timeout += latency
                if timeout > max_waiting_time:
                    break
                continue
            break

        self.request[1].sendto(DNSRequestHandler.restore_request(result, trans_id), self.client_address)
        sock.close()


def main():
    global dns_server_list
    global debug
    parser = argparse.ArgumentParser(
        description='forward each dns request to multiple servers to accelerate dns resolving')
    parser.add_argument(
        'list_file',
        # required=True,
        type=argparse.FileType('r'),
        help='specify servers\' list'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='debug mode'
    )
    args = parser.parse_args()
    debug = args.debug
    read_server_list = json.load(args.list_file)

    for server in read_server_list:
        dns_server_list.append(server)

    server = socketserver.ThreadingUDPServer(('127.0.0.1', 53), DNSRequestHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
