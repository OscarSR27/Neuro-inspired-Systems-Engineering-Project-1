# I can feel you sign: Bidirectional communication system between visually impaired and non-verbal individuals

## Run the fully integrated system

1. Open the script [uController_BidirectionalCommunication.ino](microcontroller/uController_BidirectionalCommunication). Compile and upload to the micontroller.

2. Connect the microcontrollers to a power source using the micro USB cable.

3. Connect your computer to the local network created by the microcontroller with the following credentials:
   - **Network Name:** " ESP32_for_IMU "
   - **Password:** " ICSESP32IMU "

4. One player will use the VTM-FSR system. The FSR panel will send messages, and the VTR will receive them.

5. Run the script named [mediaPipe_Bidirectional.py](mediapipe) on the player using the MediaPipe module to initialize it.

6. When the webcam appears, start the game by showing number signs in front of the camera. The program will automatically assign roles:
   - VTM-FSR player receives '1' as the sender or '2' as the receiver.
   - MediaPipe player is informed of their role in text format.

7. Roles are assigned only once per game, as they switch in each turn after the receiver confirms message receipt.

8. From now on, the sender can start sending numbers to indicate their desired position on the tic-tac-toe grid.

## Mediapipe Experiment
1. Open the [experiment_mediapipe.py](mediapipe) file
2. Adjust parameters for experiment:
    - Participants ID
    - duration of recoring time (default = 120 s)
3. Run the file in an interactive python environment   

## Vibrotactile Motor Experiment:

- Line 8 controls the duration of vibration in sequential mode.
- Line 9 controls the duration of vibration in simultaneous mode.
- Line 95 calls the function for sequential mode (Comment out line 96).
- Line 96 calls the function for simultaneous mode (Comment out line 95).

1. After configuring the parameters, compile and upload the program [Motors_experiments.ino](microcontroller/Experiments/Motors_experiments) to the microcontroller.

2. Open the serial monitor and press any key to start the experiment. The 2-minute countdown will begin at this point. Press 'n' to get the first number.

3. The participant should verbally communicate the perceived number in the VTM system, and the experimenter should record it in the serial terminal. Then press 'n' for to get the next number.

4. After 2 minutes, "End" will be displayed on the serial monitor, indicating the program has finished.

5. Press 'e' to display the results. Copy and paste these results into a text file with two columns: "ground_truth" and "response."

## Force Sensors Experiment:

- Line 8 controls the threshold in millivolt units that must be applied to the force sensor for the system to detect participant pressure.
- Line 9 controls the number of analog readings to be captured from each sensor before making a decision.

1. After configuring the parameters, compile and upload the program [FSR_experiments.ino](microcontroller/Experiments/FSR_experiments) to the microcontroller.

2. Open the serial monitor and press any key to start the experiment. The 2-minute countdown will begin at this point. Press 'n' to get the first number.

3. The Braille number to be entered will be displayed.

4. The experimenter should verbally instruct the participant on the number to input through the force sensors. After participant introduce the corresponding code press 'n' to get the next number.

5. After 2 minutes, "End" will be displayed on the serial monitor, indicating the program has finished.

6. Press 'e' to display the results. Copy and paste these results into a text file with two columns: "ground_truth" and "response."

## Data Analysis
1. Open the file [data_analysis.py](data-analysis) data-analysis
2. Indicate the experiment for which you want to run the experiment (line 33, all possible options are listed in 19-26).
3. (All paths are relative, if not using the directory structure of this repository, please provide the correct path in line 34. In case you renamed the folders for the experiments, update the new folder name in line 19-26).
4. Run the file in an interactive python environment

The data analysis file analyses one experiment at a time. Please repeat steps 1-4, especially step 2 is important.

## Authors
NISE Group 2 <br>
Members: Kunal Aggarwal, Katja Frey, Alexandra Samoylova, Oscar Soto Rivera, and Maria Zeller
