'''
TCP Proxy: 

Functions:
 - hexdump
 - request_from
 - response_handler
 - request_handler
 - proxy_handler
 - server_loop

'''

import sys
import socket
import threading

''' Filters out ASCII characters by identifying chars w/ length of 3. 
    Characters that don't match length are represented by dot.'''
HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)]) 

def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()

    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length])

        # Translates HEX_FILTER output to hexadecimal
        printable = word.translate(HEX_FILTER) 
        hexa = ' '.join([f'{ord(c):02X}' for c in word]) 
        hexwidth = length * 3
        results.append(f'{i:04x}  {hexa:<{hexwidth}}  {printable}')

    '''Prints hex value of:

    1. Index in first byte of word
    2. Hex value of word
    3. Printable representation'''
    if show:
        for line in results:
            print(line)
    else:
        return results

# Function allows real time monitoring of comms moving through proxy
def receive_from(connection):
    buffer = b""
    connection.settimeout(5) # Increase timeout as needed based on region + network quality
    try:
        while True:
            data = connection.recv(4096) # Loop to read response data into buffer until no more data or timeout
            if not data:
                break
            buffer += data
    except Exception as e:
        # [!!] Need to add actual exceptions. Currently passes.
        pass
    return buffer

''' Output modifier functions for request or response packets 
    Can add mofifiers within these functions for: fuzzing, 
    testing auth issues, privilege escalation '''
def request_handler(buffer):
    # Perform packet modifications
    return buffer

def response_handler(buffer):
    # Perform packet modifications
    return buffer

# Connect to remote host
def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect(remote_host, remote_port)

    # Check to see if need to initiate connection first
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print("[<--] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[-->] Received %d bytes from localhost." % len(local_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[-->] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<--] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<--] Sent to localhost.")
        # [!!] Currently program closes based on 5s timeout. Adjust per case based on connection quality.
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connection")
            break

# Server loop to manage the connection
def server_loop(local_host, local_port,
                remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    try:
        server.bind((local_host, local_port)) # Created socket binds to localhost and listens
    except Exception as e:
        print('Problem on bind: %r' % e)

        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # Print local connection info
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        # Start a thread to talk to remote host
        proxy_thread = threading.Thread( # Handoff connection request to proxy thread
            target = proxy_handler,
            args = (client_socket, remote_host,
                    remote_port, receive_first))
        proxy_thread.start()

# Main function
def main():
    # [!!] If user does not supply all 5 fields of information the usage guide is displayed
    if len(sys.argv[1:]) != 5: 
        print("Usage: ./proxy.py [localhost] [localport]", end='')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]
    
    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port,
                remote_host, remote_port, receive_first)
    
if __name__ == '__main__':
    main()


