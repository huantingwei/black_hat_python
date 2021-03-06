"""
to execute:

listener:
    > python scanner.py

some other client:
    > ping somedomain.come
"""

import socket
import os
import struct
from ctypes import *

import threading
import time
from netaddr import IPNetwork, IPAddress


# host to listen to
host = "10.0.2.15"

# subnet to scan
subnet = "192.168.0.0/16"

# the magic string we want to check in the ICMP responses
magic_message = "PYTHONRULES!"

# send out UDP datagrams
def udp_sender(subnet, magic_message):
    time.sleep(5)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for ip in IPNetwork(subnet):
        try:
            sender.sendto(magic_message, ("%s" % ip, 65212))
        except:
            pass

class IP(Structure):
    _fields_ = [
        ("ihl",             c_uint8, 4),
        ("version",         c_uint8, 4),
        ("tos",             c_uint8),
        ("len",             c_uint16),
        ("id",              c_uint16),
        ("offset",          c_uint16),
        ("ttl",             c_uint8),
        ("protocol_num",    c_uint8),
        ("sum",             c_uint16),
        ("src",             c_uint32),
        ("dst",             c_uint32),
    ]

    # __new__ is called before __init__
    # ref: www.geeksforgeeks.org/__new__-in-python/
    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):

        
        # map protocol constant to name
        self.protocol_map = { 1: "ICMP", 6: "TCP", 17: "UDP" }

        self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))

        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)

class ICMP(Structure):
    _fields_ = [
        ("type",             c_uint8),
        ("code",             c_uint8),
        ("checksum",         c_uint16),
        ("unused",           c_uint16),
        ("next_hop_mtu",     c_uint16),
    ]

    def __new__(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass



if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
sniffer.bind((host, 0))

# include IP headers in the packet
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)


# start to send out packet
t = threading.Thread(target=udp_sender, args=(subnet, magic_message))
t.start()


try:
    while True:
        # read one packet
        raw_buffer = sniffer.recvfrom(65565)[0]

        # instantiate an IP header from the first 20 bytes in raw_buffer
        ip_header = IP(raw_buffer[0:20])

        print("Protocol: %s %s -> %s" % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))

        if ip_header.protocol == "ICMP":

            # calculate the start address of ICMP packet
            offset = ip_header.ihl * 4
            buf = raw_buffer[offset:offset + sizeof(ICMP)]

            icmp_header = ICMP(buf)

            # print "ICMP -> Type: %d Code %d" % (icmp_header.type, icmp_header.code)
            
            if icmp_header.code == 3 and icmp_header.type == 3:
                if IPAddress(ip_header.src_address) in IPNetwork(subnet):

                    if raw_buffer[len(raw_buffer) - len(magic_message):] == magic_message: 
                        print("Host up: %s" % ip_header.src)

            
except KeyboardInterrupt:
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


