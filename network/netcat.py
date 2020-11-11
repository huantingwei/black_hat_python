# This is a tool immitating Netcat

# Similar to SSH to a remote server

# server: 
# > python netcat.py -l -p LISTENING_PORT_NUM -c
# client: 
# > python netcat.py -t HOST_DOMAIN -p TARGET_PORT_NUM
# > <CTRL-D>
# <BHP:#> 


# send request to external sources
# echo -ne "GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n" | python netcat.py -t www.google.com -p 80

import sys
import socket
import getopt
import threading
import subprocess

listen      = False
command     = False
upload      = False
execute     = ""
target      = ""
upload_destination = ""
port        = 0


def client_sender(buffer):
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))
        if len(buffer):
            client.send(buffer)
        
        # wait for response data
        while True:
            recv_len = 1
            response = ""
            
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break
            print(response)

            # wait for more input
            buffer = raw_input("")
            buffer += "\n"

            client.send(buffer)

    except:
        print("[*] Exception! Exiting...")
        client.close()

def client_handler(client_socket):
    global upload
    global execute
    global command

    if len(upload_destination):
        print("upload files")
        file_buffer = ""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data
    
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)
    
    if len(execute):

        output = run_command(execute)
        client_socket.send(output)

    if command:
        while True:
            client_socket.send("<BHP:#> ")
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            response = run_command(cmd_buffer)

            client_socket.send(response)


def server_loop():
    global target
    
    # if no target defined, listen to all
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        print(addr)
        # print "Receives client from %s" % addr

        # start a thread to process a new client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def run_command(command):

    # strip newline
    command = command.rstrip()

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Command execution fail...\r\n"

    return output


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        # usage()
        print("usage()")

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help", "listen", "execute", "target", "port", "command", "upload"])
    
    except getopt.GetoptError as err:
        print(str(err))
        # usage()
    
    
    for o,a in opts:
        if o in ("-h", "--help"):
            # usage()
            print("usage()")
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "NO such option yet"
    
    # send data from stdin
    if not listen and len(target) and port > 0:

        buffer = sys.stdin.read()
        client_sender(buffer)
    
    # listen on a port
    if listen:
        server_loop()


main()