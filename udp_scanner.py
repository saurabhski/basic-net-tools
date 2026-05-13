import socket

target = "www.google.com"
port = 80

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto(b"AAABBBCCC",(target,port))

data, addr = client.recvfrom(4096)

print(data.decode())
client.close()