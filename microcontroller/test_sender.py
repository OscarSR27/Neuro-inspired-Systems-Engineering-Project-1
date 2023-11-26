# %%

import socket

# %%

udp_ip = "192.168.4.1"  # IP del ESP32
udp_port = 9999         # Puerto del ESP32

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    data = input("Ingresa un valor de 4 caracteres (ejemplo '1111', '1010'): ")
    
    if len(data) == 4 and all(char in '01' for char in data):
        data += '\0'  # Agregar carácter nulo
        sock.sendto(data.encode(), (udp_ip, udp_port))
    else:
        print("Entrada inválida.")
# %%
