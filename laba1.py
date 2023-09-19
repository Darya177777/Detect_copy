import socket
import struct
from sys import argv
import keyboard
ip_list = {}


class Sender:
    def __init__(self, MCAST_GRP, MCAST_PORT):
        self.addr = MCAST_GRP
        self.port = int(MCAST_PORT)
        self.ipv4 = True
        if ':' in self.addr:
            self.ipv4 = False

    def send(self, mes):
        if self.ipv4:
            ttl = struct.pack('B', 2)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # datagram
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)  # live time
            sock.sendto(bytes(str(socket.gethostbyname(socket.gethostname())) + mes, encoding='utf8'),
                        (self.addr, self.port))
            sock.close()
        else:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, True)
            sock.sendto(bytes(str(socket.gethostbyname(socket.gethostname())) + mes, encoding='utf8'),
                        (self.addr, self.port))
            sock.close()


class Receiver:
    def __init__(self, MCAST_GRP, MCAST_PORT):
        self.addr = MCAST_GRP
        self.port = int(MCAST_PORT)
        self.ipv4 = True
        if ':' in self.addr:
            self.ipv4 = False

    def recv(self):
        if self.ipv4:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', self.port))
            mreq = struct.pack("4sl", socket.inet_aton(self.addr), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        else:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', self.port))
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, True)
            mreq = struct.pack("16s15s".encode('utf-8'), socket.inet_pton(socket.AF_INET6, self.addr),
                               (chr(0) * 16).encode('utf-8'))
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)
        sock.settimeout(0.1)
        size = 10240
        try:
            s = sock.recv(size).decode('utf-8').split()
            if len(s) > 1 and s[1][-1] == 'o':
                print(s[0] + " appear")
                ip_list[s[0]] = 0
            elif s[0] not in ip_list:
                print(s[0] + " appear")
                ip_list[s[0]] = 0
            elif ip_list[s[0]] is not None:
                ip_list[s[0]] += 1
        except Exception:
            pass
        sock.close()


def run():
    script, addr, port = argv
    my_sender = Sender(addr, port)
    my_receiver = Receiver(addr, port)
    mes = " hello"
    my_sender.send(mes)
    check = 0
    while not keyboard.is_pressed('q'):
        check += 1
        my_sender.send("")
        my_receiver.recv()
        if check == 30:
            for i in ip_list.keys():
                if ip_list[i] == 0:
                    print(i + " disappear")
                    ip_list[i] = None
            for i in ip_list.keys():
                if ip_list[i] is not None:
                    ip_list[i] = 0
            check = 0


if __name__ == "__main__":
    run()
