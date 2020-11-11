"""
to execute:

listener:
  > python sniffer.py

some other client:
  > ping somedomain.com

the packet will be printed in listener's terminal
"""


import socket
import os

# the host we want to listen to
host = "10.0.2.15"

# if os = Windows
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0))

# include IP headers in the packet
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# if Windows, need to set some other flags using socket's IOCTL(io control)
# to turn on "promiscuous mode" 
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# read `one` packet
print(sniffer.recvfrom(65565))

# if Windows, turn of "promiscuous mode"
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

