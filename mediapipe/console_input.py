#%%
# imports
from shared_memory_dict import SharedMemoryDict
import time

#%%
#%% 
# shared memory for MediaPipe and force sensors
smd = SharedMemoryDict(name='msg', size=1024)
# TODO decide which variables are necessary
smd['signed_number'] = None
smd['pressed_number'] = None

#%%
# test console input
while True:
    try:
        # Get user input for a number between 0-9
        user_input = int(input("Enter a number between 0 and 9: "))

        # Check if the entered number is within the valid range
        if 0 <= user_input <= 9:
            print(f"You entered: {user_input}")
            smd['signed_number'] = user_input
            print(smd['signed_number'])
            time.sleep(10) # Wait for 10 seconds
        else:
            print("Please enter a number between 0 and 9.")

    except ValueError:
        print("Invalid input. Please enter a valid number.")