# %%
import socket

# %%

local_port = 9999  # Puerto local para escuchar
dict={}
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', local_port))
'''
def decode_braille(force_array):
    number = None
    if force_array == "0111"[0,1,1,1]:
        number = 0
    elif force_array == [1,0,0,0]:
        number = 1
    elif force_array == [1,1,0,0]:
        number = 2
    elif force_array == [1,0,1,0]:
        number = 3
    elif force_array == [1,0,1,1]:
        number = 4
    elif force_array == [1,0,0,1]:
        number = 5
    elif force_array == [1,1,1,0]:
        number = 6
    elif force_array == [1,1,1,1]:
        number = 7
    elif force_array == [1,1,0,1]:
        number = 8
    elif force_array == [0,1,1,0]:
        number = 9
    else:
        print('Braille pattern not recognized:', force_array)

    return number
'''

def decode_braille(force_array):
    number = None
    if force_array == "0111":
        number = 0
    elif force_array == "1000":
        number = 1
    elif force_array == "1100":
        number = 2
    elif force_array == "1010":
        number = 3
    elif force_array == "1011":
        number = 4
    elif force_array == "1001":
        number = 5
    elif force_array == "1110":
        number = 6
    elif force_array == "1111":
        number = 7
    elif force_array == "1101":
        number = 8
    elif force_array == "0110":
        number = 9
    else:
        print('Braille pattern not recognized:', force_array)

    return number

while True:
    data, addr = sock.recvfrom(1024)
    print(decode_braille(data.decode()))
# %%
