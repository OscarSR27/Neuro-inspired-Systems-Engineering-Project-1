#include <WiFi.h>
#include <WiFiUdp.h>
#include <iostream>
#include <random>

char braille_codes[][6] = {"0111","1000","1100","1010","1011","1001","1110","1111","1101","0110"};
int braille_codes_dec[] = {0,1,2,3,4,5,6,7,8,9};
int results[100][2];

int thr1=1000;
const int frames = 10;

//Pins for vibrotactile motors
int motorPin1 = 13; // GPIO 13 for vibration motor 1
int motorPin2 = 12; // GPIO 12 for vibration motor 2
int motorPin3 = 27; // GPIO 27 for vibration motor 3
int motorPin4 = 33; // GPIO 33 for vibration motor 4

//Pins for force sensors
int fsPin1 = 34; //A2
int fsPin2 = 39; //A3
int fsPin3 = 36; //A4
int fsPin4 = 32; //GPIO 32

unsigned long init_time;
unsigned long current_time;

const int dutyCycle = 255;
float motor_wave = 0.9; // ranges from 0.05 to 1.0

WiFiUDP Udp; // creation of wifi Udp instance
char packetBuffer [255];
unsigned int localPort = 9999;
const char * ssid = " ESP32_for_IMU ";
const char * password = " ICSESP32IMU ";
//int motor_selection = 0;
//bool m1,m2,m3,m4 = false;

void force_sensors(int threshold, int numReadings, char* result);
void vibration_control(int motor_1,int motor_2,int motor_3,int motor_4);
int findBrailleCodeIndex(char codes[][6], const char* output);

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

int trials = 0;
bool first_iteration = true;
void loop ()
{
  if(first_iteration)
  {
    init_time = millis();
    first_iteration = false;
  }
  current_time = millis();
  // Define the distribution for integers between 0 and 9
  std::uniform_int_distribution<> distrib(0, 9);

  // Generate a random number
  int randomNumber = distrib(gen);

  if ((current_time - init_time) < 30000)
  {
    Serial.println(current_time - init_time);
    if (Serial.available() > 0) 
    {
      char inputChar = Serial.read(); // Read a character from the serial input
      Serial.println(inputChar);
      if (inputChar == 'n')
      {
        char output[5]={0};
        Serial.println("Sensors");
        results[trials][0] = braille_codes_dec[randomNumber]; // Convert 1 char to integer
        Serial.println(braille_codes_dec[randomNumber]);
        delay(500);
        vibration_control(1,0,0,0);
        while (output[0] == '\0')
        {
           force_sensors(thr1,frames,output);
        }
        
        int index = findBrailleCodeIndex(braille_codes, output);
        if (index != -1)
        {
          results[trials][1] = braille_codes_dec[index];
        }
        else
        {
          results[trials][1] = -1;
        }
        
        Serial.print(results[trials][0]);
        Serial.print(',');
        Serial.print(results[trials][1]);
        trials++;
      }
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
  else
  {
    Serial.println("End");
    for (int i = 0; i<trials; i++)
    {
      Serial.print(results[i][0]);
      Serial.print(',');
      Serial.println(results[i][1]);
    }
  }
}

void force_sensors(int threshold, int numReadings, char* result)
{
  bool anySensorActive = false;
  int activeCount[4] = {0, 0, 0, 0}; // Counter array for active readings for each sensor
  int sensorPins[4] = {fsPin1, fsPin2, fsPin3, fsPin4}; // Array of sensor pins

  memset(result, '0', 4);
  
  for (int sensor = 0; sensor < 4; sensor++)
  {
      for (int i = 0; i < numReadings; i++)
      {
          int reading = analogRead(sensorPins[sensor]);
          int voltage = map(reading, 0, 4095, 0, 3300);

          if (voltage > threshold)
          {
              activeCount[sensor]++;
          }

          delay(10); // Short pause between readings
      }

      // Determine if the sensor is mostly active or inactive
      if (activeCount[sensor] > numReadings / 2) 
      {
          result[sensor] = '1';
          anySensorActive = true;
      }
  }

  if (!anySensorActive) 
  {
    memset(result, 0, 4);
  }
}

int findBrailleCodeIndex(char codes[][6], const char* output)
{
    for (int i = 0; i < 10; ++i)
    {
        if (strcmp(codes[i], output) == 0)
        {
            return i;
        }
    }
    return -1;
}

void vibration_control(int motor_1,int motor_2,int motor_3,int motor_4)
{
  digitalWrite ( motorPin1 , motor_1?HIGH:LOW );
  delay (200);
  digitalWrite ( motorPin1 , LOW );
  /*digitalWrite ( motorPin2 , motor_2?HIGH:LOW);
  delay (1000);
  digitalWrite ( motorPin2 , LOW );
  digitalWrite ( motorPin3 , motor_3?HIGH:LOW);
  delay (1000);
  digitalWrite ( motorPin3 , LOW );
  digitalWrite ( motorPin4 , motor_4?HIGH:LOW);
  delay (1000);
  digitalWrite ( motorPin4 , LOW );
  */
}
