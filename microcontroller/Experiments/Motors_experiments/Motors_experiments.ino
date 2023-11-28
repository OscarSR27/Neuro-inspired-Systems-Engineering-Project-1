/*
#include <WiFi.h>
#include <WiFiUdp.h>
#include <iostream>
#include <random>

char braille_codes[][5] = {"0111","1000","1100","1010","1011","1001","1110","1111","1101","0110"};
char results[100][2][5];

//Pins for vibrotactile motors
int motorPin1 = 13; // GPIO 13 for vibration motor 1
int motorPin2 = 12; // GPIO 12 for vibration motor 2
int motorPin3 = 27; // GPIO 27 for vibration motor 3
int motorPin4 = 33; // GPIO 33 for vibration motor 4

const int dutyCycle = 255;
float motor_wave = 0.9; // ranges from 0.05 to 1.0

WiFiUDP Udp; // creation of wifi Udp instance
char packetBuffer [255];
unsigned int localPort = 9999;
const char * ssid = " ESP32_for_IMU ";
const char * password = " ICSESP32IMU ";
int motor_selection = 0;
bool m1,m2,m3,m4 = false;

void vibration_control (int motor_1,int motor_2,int motor_3,int motor_4);

void setup ()
{
  Serial.begin(9600);
  WiFi.softAP(ssid , password ); // ESP32 as access point
  Udp . begin ( localPort );
  pinMode ( motorPin1 , OUTPUT );
  pinMode ( motorPin2 , OUTPUT );
  pinMode ( motorPin3 , OUTPUT );
  pinMode ( motorPin4 , OUTPUT );
}
std::random_device rd;
std::mt19937 gen(rd());
// Define the distribution for integers between 0 and 9
std::uniform_int_distribution<> distrib(0, 9);
int trials = 0;
void loop ()
{
  // Define the distribution for integers between 0 and 9
  std::uniform_int_distribution<> distrib(0, 9);
  
  // Generate a random number
  int randomNumber = distrib(gen);
  
  if (Serial.available() > 0) 
  {
    char inputChar = Serial.read(); // Read a character from the serial input
    Serial.println(inputChar);
    if (inputChar == 'n')
    {
      Serial.println("Motors");
      Serial.flush();
      results[trials][0][0] = braille_codes[randomNumber][0]; // Convert 1 char to integer
      results[trials][0][1] = braille_codes[randomNumber][1]; // Convert 2 char to integer
      results[trials][0][2] = braille_codes[randomNumber][2]; // Convert 3 char to integer
      results[trials][0][3] = braille_codes[randomNumber][3]; // Convert 4 char to integer
      
      m1 = braille_codes[randomNumber][0] - '0'; // Convert 1 char to integer
      m2 = braille_codes[randomNumber][1] - '0'; // Convert 2 char to integer
      m3 = braille_codes[randomNumber][2] - '0'; // Convert 3 char to integer
      m4 = braille_codes[randomNumber][3] - '0'; // Convert 4 char to integer
  
      vibration_control(m1,m2,m3,m4);

      int count = 0;
      while(count < 4)
      {
        if (Serial.available() > 0) 
        {
          char inputChar = Serial.read(); // Read a character from the serial input
          results[trials][1][count] = inputChar;
          count++;
        }
      }
      Serial.print(results[trials][0][0]);
        Serial.print(results[trials][0][1]);
        Serial.print(results[trials][0][2]);
        Serial.print(results[trials][0][3]);
        Serial.print(',');
        Serial.print(results[trials][1][0]);
        Serial.print(results[trials][1][1]);
        Serial.print(results[trials][1][2]);
        Serial.print(results[trials][1][3]);
      trials++;
    }
    if (inputChar == 'e')
    {
      for (int i = 0; i<trials; i++)
      {
        Serial.flush();
        Serial.print(results[i][0][0]);
        Serial.print(results[i][0][1]);
        Serial.print(results[i][0][2]);
        Serial.print(results[i][0][3]);
        
        Serial.print(results[i][1][0]);
        Serial.print(results[i][1][1]);
        Serial.print(results[i][1][2]);
        Serial.print(results[i][1][3]);
      }
    }
  }
}

void vibration_control(int motor_1,int motor_2,int motor_3,int motor_4)
{
  digitalWrite ( motorPin1 , motor_1?HIGH:LOW );
  delay (1000);
  digitalWrite ( motorPin1 , LOW );
  digitalWrite ( motorPin2 , motor_2?HIGH:LOW);
  delay (1000);
  digitalWrite ( motorPin2 , LOW );
  digitalWrite ( motorPin3 , motor_3?HIGH:LOW);
  delay (1000);
  digitalWrite ( motorPin3 , LOW );
  digitalWrite ( motorPin4 , motor_4?HIGH:LOW);
  delay (1000);
  digitalWrite ( motorPin4 , LOW );
}*/

#include <WiFi.h>
#include <WiFiUdp.h>
#include <iostream>
#include <random>

char braille_codes[][6] = {"0111","1000","1100","1010","1011","1001","1110","1111","1101","0110"};
int braille_codes_dec[] = {0,1,2,3,4,5,6,7,8,9};
int results[100][2];

const int analogPin = 34; 

std::mt19937 gen; // Declare the generator
std::uniform_int_distribution<> distrib(0, 9); // Distribution

//Pins for vibrotactile motors
int motorPin1 = 13; // GPIO 13 for vibration motor 1
int motorPin2 = 12; // GPIO 12 for vibration motor 2
int motorPin3 = 27; // GPIO 27 for vibration motor 3
int motorPin4 = 33; // GPIO 33 for vibration motor 4

const int dutyCycle = 255;
float motor_wave = 0.9; // ranges from 0.05 to 1.0

WiFiUDP Udp; // creation of wifi Udp instance
char packetBuffer [255];
unsigned int localPort = 9999;
const char * ssid = " ESP32_for_IMU ";
const char * password = " ICSESP32IMU ";
int motor_selection = 0;
bool m1,m2,m3,m4 = false;
unsigned long init_time;
unsigned long current_time;
bool first_iteration = true;
bool end_flag = true;

void vibration_control_seq (int motor_1,int motor_2,int motor_3,int motor_4);
void vibration_control_simul(int motor_1,int motor_2,int motor_3,int motor_4);
std::random_device rd;

void setup ()
{
  Serial.begin(9600);
  WiFi.softAP(ssid , password ); // ESP32 as access point
  Udp . begin ( localPort );
  pinMode ( motorPin1 , OUTPUT );
  pinMode ( motorPin2 , OUTPUT );
  pinMode ( motorPin3 , OUTPUT );
  pinMode ( motorPin4 , OUTPUT );

  // Read from the floating analog pin
  float seed = 766.876;

  // Seed the random number generator
  gen.seed(seed);
}
  
int trials = 0;
bool start_flag = false;


void loop ()
{
  int randomNumber = distrib(gen);
  char start = Serial.read();
  while(!start_flag)
  {
    if (Serial.available() > 0) 
    {
      start_flag = true;
    }
  }
  if(first_iteration)
  {
    init_time = millis();
    first_iteration = false;
  }
  current_time = millis();
 

  if ((current_time - init_time) < 120000)
  {
    Serial.println();
    Serial.println("Motors");
    Serial.flush();
    results[trials][0] = braille_codes_dec[randomNumber]; // Convert 1 char to integer
    Serial.println(braille_codes_dec[randomNumber]);
    
    m1 = braille_codes[randomNumber][0] - '0'; // Convert 1 char to integer
    m2 = braille_codes[randomNumber][1] - '0'; // Convert 2 char to integer
    m3 = braille_codes[randomNumber][2] - '0'; // Convert 3 char to integer
    m4 = braille_codes[randomNumber][3] - '0'; // Convert 4 char to integer
    //vibration_control_seq(m1,m2,m3,m4);
    vibration_control_simul(m1,m2,m3,m4);

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
    Serial.print(results[trials][0]);
    Serial.print(',');
    Serial.print(results[trials][1]);
    trials++; 
  }
  else
  {
    if (end_flag)
    {
      Serial.println();
      Serial.println("End");
      end_flag = false;
    }
    if (Serial.available() > 0)
    {
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

void vibration_control_seq(int motor_1,int motor_2,int motor_3,int motor_4)
{
  digitalWrite ( motorPin1 , motor_1?HIGH:LOW );
  delay (250);
  digitalWrite ( motorPin1 , LOW );
  digitalWrite ( motorPin2 , motor_2?HIGH:LOW);
  delay (250);
  digitalWrite ( motorPin2 , LOW );
  digitalWrite ( motorPin3 , motor_3?HIGH:LOW);
  delay (250);
  digitalWrite ( motorPin3 , LOW );
  digitalWrite ( motorPin4 , motor_4?HIGH:LOW);
  delay (250);
  digitalWrite ( motorPin4 , LOW );
}

void vibration_control_simul(int motor_1,int motor_2,int motor_3,int motor_4)
{
  digitalWrite ( motorPin1 , motor_1?HIGH:LOW);
  digitalWrite ( motorPin2 , motor_2?HIGH:LOW);
  digitalWrite ( motorPin3 , motor_3?HIGH:LOW);
  digitalWrite ( motorPin4 , motor_4?HIGH:LOW);
  delay (1000);
  digitalWrite ( motorPin1 , LOW );
  digitalWrite ( motorPin2 , LOW );
  digitalWrite ( motorPin3 , LOW );
  digitalWrite ( motorPin4 , LOW );
}
