import socket

target = "www.google.com"
port = 80

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target,port))
client.send(b'GET / HTTP/1.1\r\n/Host: google.com\r\n\r\n')

response = client.recv(4096)

print(response.decode())
client.close()