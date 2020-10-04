from scapy.all import *

def show(packet):
    print(packet.show())


def packet_callback(packet):
    if packet[TCP].payload:
        mail_packet = str(packet[TCP].payload)

        if "user" in mail_packet.lower() or "pass" in mail_packet.lower():
            print("[*] Server: %s" % packet[IP].dst)
            print("[*] %s" % packet[TCP].payload)



print("Start...")

# filter with syntax similar to wireshark
# only email protocol
# 110: POP3
# 143: IMAP
# 25 : SMTP

# without filter
# sniff(prn=show, count=1)

# with filter
# store = 0 : do not store any packet in memory
# !!! scapy seems to have bug for the filter !!!
# sniff(filter="TCP port 110 or TCP port 25 or TCP port 143", prn=packet_callback, store=0)

