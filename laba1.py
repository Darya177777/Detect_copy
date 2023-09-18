import socket
import struct
from sys import argv
import keyboard


def simple_send(MCAST_GRP, MCAST_PORT, mes):
    ttl = struct.pack('B', 2)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # datagram
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)  # live time
    sock.sendto(bytes(str(socket.gethostbyname(socket.gethostname())) + mes, encoding='utf8'), (MCAST_GRP, MCAST_PORT))
    sock.close()


def simple_recv(MCAST_GRP, MCAST_PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.settimeout(0.1)
    size = 10240
    try:
        s = sock.recv(size).decode('utf-8')
        if s[-1] == 'o':
            print(s.split()[0] + " appear")
            ip_list[s.split()[0]] = 0
        elif s.split()[0] not in ip_list:
            print(s.split()[0] + " appear")
            ip_list[s.split()[0]] = 0
        elif ip_list[s.split()[0]] is not None:
            ip_list[s.split()[0]] += 1
    except Exception:
        pass
    sock.close()


def hard_send(MCAST_GRP, MCAST_PORT, mes):
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, True)
    sock.sendto(bytes(str(socket.gethostbyname(socket.gethostname())) + mes, encoding='utf8'), (MCAST_GRP, MCAST_PORT))


def hard_recv(MCAST_GRP, MCAST_PORT):
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MCAST_PORT))
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, True)
    mreq = struct.pack("16s15s".encode('utf-8'), socket.inet_pton(socket.AF_INET6, MCAST_GRP),
                       (chr(0) * 16).encode('utf-8'))
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)
    sock.settimeout(0.1)
    size = 10240
    try:
        s = sock.recv(size).decode('utf-8')
        if s[-1] == 'o':
            print(s.split()[0] + " appear")
            ip_list[s.split()[0]] = 0
        elif s.split()[0] not in ip_list:
            print(s.split()[0] + " appear")
            ip_list[s.split()[0]] = 0
        elif ip_list[s.split()[0]] is not None:
            ip_list[s.split()[0]] += 1
    except Exception:
        pass
    sock.close()


ip_list = {}
script, addr, port = argv
port = int(port)
is_simple = True
if ':' in addr:
    is_simple = False
mes = " hello"
if is_simple:
    simple_send(addr, port, mes)
else:
    hard_send(addr, port, mes)
check = 0
while not keyboard.is_pressed('q'):
    check += 1
    if is_simple:
        simple_send(addr, port, "")
        simple_recv(addr, port)
    else:
        hard_send(addr, port, "")
        hard_recv(addr, port)
    if check == 30:
        for i in ip_list.keys():
            if ip_list[i] == 0:
                print(i + " disappear")
                ip_list[i] = None
        for i in ip_list.keys():
            if ip_list[i] is not None:
                ip_list[i] = 0
        check = 0
