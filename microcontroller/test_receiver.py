# %%
import socket

# %%

local_port = 9999  # Puerto local para escuchar

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', local_port))

while True:
    data, addr = sock.recvfrom(1024)
    print(f"Received message: {data.decode()} from {addr}")