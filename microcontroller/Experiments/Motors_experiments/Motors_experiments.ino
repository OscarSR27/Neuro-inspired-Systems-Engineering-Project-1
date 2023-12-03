#include <WiFi.h>
#include <WiFiUdp.h>
#include <iostream>
#include <random>


//Experimental parameter
const int delay_VTM_seq = 250;//Vibration duration for vibrotactile motors using sequential mode
const int delay_VTM_simul = 750;//Vibration duration for vibrotactile motors using simultaneous mode

char braille_codes[][6] = {"0111","1000","1100","1010","1011","1001","1110","1111","1101","0110"};
int braille_codes_dec[] = {0,1,2,3,4,5,6,7,8,9};
int results[100][2];

std::mt19937 gen; // Declare the generator
std::uniform_int_distribution<> distrib(0, 9); // Distribution

//Pins for vibrotactile motors
int motorPin1 = 13; // GPIO 13 for vibration motor 1
int motorPin2 = 12; // GPIO 12 for vibration motor 2
int motorPin3 = 27; // GPIO 27 for vibration motor 3
int motorPin4 = 33; // GPIO 33 for vibration motor 4

WiFiUDP Udp; // creation of wifi Udp instance
char packetBuffer [255];
unsigned int localPort = 9999;
const char * ssid = " ESP32_for_IMU ";
const char * password = " ICSESP32IMU ";
bool m1,m2,m3,m4 = false;
unsigned long init_time;
unsigned long current_time;
bool first_iteration = true;
bool end_flag = true;
std::random_device rd;

void vibration_control_seq (int motor_1,int motor_2,int motor_3,int motor_4,int delay_VTM_seq);
void vibration_control_simul(int motor_1,int motor_2,int motor_3,int motor_4,int delay_VTM_simul);


void setup ()
{
  Serial.begin(9600);
  WiFi.softAP(ssid , password ); // ESP32 as access point
  Udp . begin ( localPort );
  pinMode ( motorPin1 , OUTPUT );
  pinMode ( motorPin2 , OUTPUT );
  pinMode ( motorPin3 , OUTPUT );
  pinMode ( motorPin4 , OUTPUT );

  // Seed for random number
  float seed = 48;

  // Seed the random number generator
  gen.seed(seed);
}
  
int trials = 0;
bool start_flag = false;


void loop ()
{
  int randomNumber = distrib(gen);//Generate random number to pick Braille codes
  
  //Press any key to start sending numbers as well as the timer
  while(!start_flag)
  {
    if (Serial.available() > 0) 
    {
      start_flag = true;
    }
  }
  if(first_iteration)//Read timer once experiment starts
  {
    init_time = millis();
    first_iteration = false;
  }
  current_time = millis();//Record timer evey iteration
 

  if ((current_time - init_time) < 120000)//Verify if timer exceed 2 minutes
  {
    Serial.println();
    Serial.println("Motors");
    Serial.flush();
    results[trials][0] = braille_codes_dec[randomNumber]; // Record the expected result in result field 0
    Serial.println(braille_codes_dec[randomNumber]); //Shows the number 

    //Extract the numerical value from char, this should be 0 or 1 so it can be used as bool parameters
    m1 = braille_codes[randomNumber][0] - '0'; // Convert 1 char to integer
    m2 = braille_codes[randomNumber][1] - '0'; // Convert 2 char to integer
    m3 = braille_codes[randomNumber][2] - '0'; // Convert 3 char to integer
    m4 = braille_codes[randomNumber][3] - '0'; // Convert 4 char to integer

    //Call vibrotactile functions to transmit sensory feedback to the user
    vibration_control_seq(m1,m2,m3,m4,delay_VTM_seq);
    //vibration_control_simul(m1,m2,m3,m4,delay_VTM_simul);

    //Next block of code is waiting for the experimenter to register the number decode by the participant into the results field 1
    int count = 0;
    Serial.flush();
    char inputChar = Serial.read();
    while(count < 1)
    {
      if (Serial.available() > 0) 
      {
        char inputChar = Serial.read(); // Read a character from the serial input
        results[trials][1] = atoi(&inputChar);
        count++;
      }
    }
    //Provide visual feedback to the experimenter about the recorded results for every iteration
    Serial.print(results[trials][0]);
    Serial.print(',');
    Serial.print(results[trials][1]);
    trials++; 
  }
  else
  {
    //Indicate end of experiment after 2 minutes
    if (end_flag)
    {
      Serial.println();
      Serial.println("End");
      end_flag = false;
    }
    if (Serial.available() > 0)
    {//Wait until experimenter press letter e on the keyboard to display results
      char inputChar = Serial.read(); // Read a character from the serial input
      if (inputChar == 'e')
      {
        for (int i = 0; i<trials; i++)
        {
          Serial.print(results[i][0]);
          Serial.print(',');
          Serial.println(results[i][1]);
        }
      }    
    }
  }
}

//This function implemet the sequential mode
void vibration_control_seq(int motor_1,int motor_2,int motor_3,int motor_4,int delay_VTM_seq)
{
  digitalWrite ( motorPin1 , motor_1?HIGH:LOW );
  delay (delay_VTM_seq);
  digitalWrite ( motorPin1 , LOW );
  digitalWrite ( motorPin2 , motor_2?HIGH:LOW);
  delay (delay_VTM_seq);
  digitalWrite ( motorPin2 , LOW );
  digitalWrite ( motorPin3 , motor_3?HIGH:LOW);
  delay (delay_VTM_seq);
  digitalWrite ( motorPin3 , LOW );
  digitalWrite ( motorPin4 , motor_4?HIGH:LOW);
  delay (delay_VTM_seq);
  digitalWrite ( motorPin4 , LOW );
}

//This function implemet the simultaneous mode
void vibration_control_simul(int motor_1,int motor_2,int motor_3,int motor_4, int delay_VTM_simul)
{
  digitalWrite ( motorPin1 , motor_1?HIGH:LOW);
  digitalWrite ( motorPin2 , motor_2?HIGH:LOW);
  digitalWrite ( motorPin3 , motor_3?HIGH:LOW);
  digitalWrite ( motorPin4 , motor_4?HIGH:LOW);
  delay (delay_VTM_simul);
  digitalWrite ( motorPin1 , LOW );
  digitalWrite ( motorPin2 , LOW );
  digitalWrite ( motorPin3 , LOW );
  digitalWrite ( motorPin4 , LOW );
}
