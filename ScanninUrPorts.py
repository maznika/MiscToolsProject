#/usr/bin/env python

import threading
import argparse
import logging
import socket
import sys

conn_socket = None
target_hostname = None

def check_conn(tgt_host, tgt_port):
    try:
        conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_socket.settimeout(2)
        conn_socket.connect((tgt_host, tgt_port))
        conn_socket.send('test')
        results = conn_socket.recv(100)
        thread_lock.acquire()
        print '[+] %s TCP port is open' % tgt_port
        print '[+] %s' % results
        logging.info('[+] %s TCP Port open on %s' % tgt_port)
        logging.info('\t[+] %s' % results)
    except:
        thread_lock.acquire()
        logging.info('[-] %s/tcp closed' % tgt_port)
        print '[-] %d/tcp closed' % tgt_port
    finally:
        thread_lock.release()
        conn_socket.close()


def scan_ports(tgt, tgt_ports):
    target_hostname = tgt
    try:
        target_address = socket.gethostbyname(tgt)
    except:
        logging.INFO('[-] Cannot resolve %s: Unknown host' % tgt)
        return
    try:
        target_hostname = socket.gethostbyaddr(target_address)
        print '[+] Scan Results for: %s' % target_hostname[0]
    except:
        print '[-] Could not resolve address to retrieve hostname, using address'
        print '[+] Scan Results for: %s' % target_address

    socket.setdefaulttimeout(1)
    for port in tgt_ports:
        t = threading.Thread(target=check_conn,args=(target_hostname,int(port)))
        t.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''This is a simple Python port scanner.
        By default, the full range of ports from 1 to 65536 is scanned with localhost as the
        target.  It can also take a space delimited list of ports or a range of them,
        and checks their open/closed state.  Results are printed to stdout and also written
        to ./portscanner.log''')
    parser.add_argument('--target', type=str, help='Specify target IP or hostname')
    exclusive_grp = parser.add_mutually_exclusive_group()
    exclusive_grp.add_argument('--ports', type=str, nargs='+',
        help='Specify target port[s] separated by space. Default is the full range 1-65536')
    exclusive_grp.add_argument('--range', type=int, nargs=2,
        help='Range of ports to scan [E.G. --range 1 1024] will scan 1 to 1024')
    args = parser.parse_args()

    # Scans everything from 1 - 65535
    default_ports = range(1, 65536)

    thread_lock = threading.Semaphore(value=1)

    target = args.target if args.target else 'localhost'

    if args.ports:
        ports = args.ports
    elif args.range:
        ports = range(min(args.range), max(args.range) + 1)
    else:
        ports = default_ports

    logging.basicConfig(filename='portscanner.log',level=logging.DEBUG)

    try:
        scan_ports(target, ports)
    except Exception as e:
        print e
        sys.exit(1)
