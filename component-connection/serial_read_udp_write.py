# %%
# imports
import serial
from shared_memory_dict import SharedMemoryDict
import time
import socket

#%% 
# UDP setup
UDP_ESP32 = "192.168.4.3"
UDP_PORT = 9999
MESSAGE = "000_000_000_000"  
print("UDP target IP: %s" % UDP_ESP32)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)

# uncomment for testing
# sock = socket.socket(socket.AF_INET, # Internet
#                        socket.SOCK_DGRAM) # UDP

#%% 
# Serial connection
port = serial.Serial('COM10', baudrate=512000) # set right port

#%% 
# parameters
# shared memory for MediaPipe and force sensors
smd = SharedMemoryDict(name='msg', size=1024)
# TODO decide which variables are necessary
smd['signed_number'] = None
smd['pressed_number'] = None

number_vibros = 4

#%% 
# functions
def encode_braille(number):
    intensity_array = [0,0,0,0]
    if number == 0:
        intensity_array = [0,1,1,1]
    elif number == 1:
        intensity_array = [1,0,0,0]
    elif number == 2:
        intensity_array = [1,1,0,0]
    elif number == 3:
        intensity_array = [1,0,1,0]
    elif number == 4:
        intensity_array = [1,0,1,1]
    elif number == 5:
        intensity_array = [1,0,0,1]
    elif number == 6:
        intensity_array = [1,1,1,0]
    elif number == 7:
        intensity_array = [1,1,1,1]
    elif number == 8:
        intensity_array = [1,1,0,1]
    elif number == 9:
        intensity_array = [0,1,1,0]
    else:
        print('Number not recognized:', number)

    return intensity_array


def decode_braille(force_array):
    number = None
    if force_array == [0,1,1,1]:
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


def send_array_udp(intensity):
        '''
        Send intensity array through UDP to ESP32 with vibromotors
        '''
        line = ''.join(str(x) for x in intensity)
        line = line + '\n'

        # send through UDP
        # sock.sendto(line.encode(), (UDP_IP, UDP_PORT))
        print('message:', line.encode(), 'UDP ip:', UDP_ESP32, 'UDP port:', UDP_PORT)
        j = 0
        #time.sleep(0.5)


def receive_array_serial(msg):
    try:
        force_array = [int(x) for x in msg]
        return force_array
    except ValueError as e:
        print(f"Error: {e}. The string contains non-integer characters.")
        return [0,0,0,0]

#%% 
# send and receive loop
while True:
    # Get the message from ESP32 with force sensors
    #msg = port.readline()
    msg = None

    # translate force sensor values into number
    if msg:
        force_array = receive_array_serial(msg)
        smd['pressed_number'] = decode_braille(force_array)
        print('Number received:', smd['pressed_number'])
    
    # send signed number via UDP to ESP32
    if smd['signed_number'] is not None:
        # send number
        intensity_array = encode_braille(smd['signed_number'])
        send_array_udp(intensity_array)
        # reset variables
        intensity_array = [0,0,0,0]
        smd['signed_number'] = None