#!/usr/bin/env python3

import argparse
import datetime
import json
import os
import socketserver
import sys

dns_server_list = []
debug = False
latency = 0.013
recommended_response_duration = 0.016
max_message_length = 512
max_waiting_time = 2
first_send_count = 2


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
        return trans_id + bytes([request[2] & 0b11111101]) + request[3:]
        # return trans_id + request[2:]

    def handle(self):
        import socket
        start = datetime.datetime.now()
        buf = []
        timeout_times = 0
        trans_id = self.request[0][0:2]
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(latency)

        def push_buf(content, buf_list=buf):
            buf_list.append(str(content) + '\n')

        def merge_buf(buf_list=buf):
            return ''.join(buf_list)

        def get_duration(start_date=start):
            return (datetime.datetime.now() - start_date).total_seconds()

        def final_print():
            duration = get_duration()
            duration_color = Colors.OKGREEN
            if duration > 2 * recommended_response_duration:
                duration_color = Colors.FAIL
            elif duration > recommended_response_duration:
                duration_color = Colors.OKBLUE
            push_buf(
                'time:\t' + colored('{}ms'.format(int(duration * 1000)), duration_color) + ', {}'.format(timeout_times))
            print(merge_buf())

        def one_send():
            for dns_server in dns_server_list:
                try:
                    sock.sendto(DNSRequestHandler.rand_request(self.request[0]), (dns_server, 53))
                except Exception as ex_one_send:
                    if isinstance(ex_one_send, socket.timeout):
                        if debug:
                            push_buf(colored('catch:\t{}'.format(type(ex_one_send)), Colors.FAIL))
                    else:
                        sock.close()
                        if debug:
                            push_buf(colored('catch:\t{}'.format(type(ex_one_send)), Colors.FAIL))
                            final_print()
                        os.execl(sys.executable, 'python', __file__, *sys.argv[1:])
                        return -1

            return 0

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
            push_buf('<sending>')

        for i in range(first_send_count):
            if one_send() != 0:
                return

        if debug:
            push_buf('<receiving>')

        while True:
            try:
                result, address = sock.recvfrom(max_message_length)
                self.request[1].sendto(DNSRequestHandler.restore_request(result, trans_id), self.client_address)
                if debug:
                    push_buf('length:\t{} bytes'.format(len(result)))
                    push_buf('server:\t{0}:{1}'.format(address[0], address[1]))
                break
            except Exception as ex:
                if isinstance(ex, socket.timeout):
                    if one_send() != 0:
                        return
                    if debug:
                        timeout_times += 1
                        if timeout_times == 1:
                            push_buf(colored('catch:\t{}'.format(type(ex)), Colors.FAIL))
                else:
                    sock.close()
                    if debug:
                        push_buf(colored('catch:\t{}'.format(type(ex)), Colors.FAIL))
                        final_print()
                    return

            if get_duration() > max_waiting_time:
                if debug:
                    push_buf(colored('Warning:\ttimeout', Colors.FAIL))
                break

        sock.close()

        if debug:
            final_print()


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
