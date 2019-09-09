#!/usr/bin/env python3

import argparse
import datetime
import json
import os
import socket
import socketserver

dns_server_list = []
debug = False
latency = 0.013
max_message_length = 512
max_waiting_time = 2
first_send = 2


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def colored(content, color=None):
    content = str(content)
    if color is not None:
        buf = color + content + Colors.ENDC
    else:
        buf = content

    return buf


class DNSRequestHandler(socketserver.BaseRequestHandler):

    @staticmethod
    def rand_request(request):
        return os.urandom(2) + request[2:]

    @staticmethod
    def restore_request(request, trans_id):
        return trans_id + request[2:]

    def handle(self):
        trans_id = self.request[0][0:2]
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if debug:
            start = datetime.datetime.now()
        for i in range(first_send):
            for dns_server in dns_server_list:
                sock.sendto(DNSRequestHandler.rand_request(self.request[0]), (dns_server, 53))

        sock.settimeout(latency)
        buf = []

        def push_buf(content, buf_list=buf):
            buf_list.append(str(content) + '\n')

        def merge_buf(buf_list=buf):
            return ''.join(buf_list)

        if debug:
            domain = ''
            now = 12
            length = self.request[0][now]
            while length != 0:
                domain += bytes(self.request[0][now + 1:now + 1 + length]).decode('utf-8') + '.'
                now = now + 1 + length
                length = self.request[0][now]

            push_buf(
                colored('domain:\t{}'.format(domain), Colors.WARNING)
            )

        timeout = latency
        while True:
            try:
                result, address = sock.recvfrom(max_message_length)
                if debug:
                    push_buf('length:\t{} bytes'.format(len(result)))
                    push_buf('server:\t{0}:{1}'.format(address[0], address[1]))
                self.request[1].sendto(DNSRequestHandler.restore_request(result, trans_id), self.client_address)
                break
            except Exception as ex:
                for dns_server in dns_server_list:
                    sock.sendto(DNSRequestHandler.rand_request(self.request[0]), (dns_server, 53))
                timeout += latency
                if timeout > max_waiting_time:
                    if debug:
                        push_buf(colored('Warning:\ttimeout', Colors.FAIL))
                    break

        if debug:
            end = datetime.datetime.now()
            duration = int((end - start).total_seconds() * 1000)
            push_buf('time:\t' + colored('{}ms'.format(duration), Colors.UNDERLINE))
            print(merge_buf())
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
