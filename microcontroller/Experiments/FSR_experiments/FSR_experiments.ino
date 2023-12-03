#include <WiFi.h>
#include <WiFiUdp.h>
#include <iostream>
#include <random>


//Experimental parameter
int thr1=500;
const int frames = 15;

char braille_codes[][6] = {"0111","1000","1100","1010","1011","1001","1110","1111","1101","0110"};
int braille_codes_dec[] = {0,1,2,3,4,5,6,7,8,9};
int results[100][2];

std::mt19937 gen; // Declare the generator
std::uniform_int_distribution<> distrib(0, 9); // Distribution

//Pins for force sensors
int fsPin1 = 34; //A2
int fsPin2 = 39; //A3
int fsPin3 = 36; //A4
int fsPin4 = 32; //GPIO 32

unsigned long init_time;
unsigned long current_time;

WiFiUDP Udp; // creation of wifi Udp instance
char packetBuffer [255];
unsigned int localPort = 9999;
const char * ssid = " ESP32_for_IMU ";
const char * password = " ICSESP32IMU ";

void force_sensors(int threshold, int numReadings, char* result);
int findBrailleCodeIndex(char codes[][6], const char* output);

void setup ()
{
  Serial.begin(9600);
  WiFi.softAP(ssid , password ); // ESP32 as access point
  Udp . begin ( localPort );

  // Seed for random number
  float seed = 47;
  // Seed the random number generator
  gen.seed(seed);
}

int trials = 0;
bool first_iteration = true;
bool start_flag = false;
bool end_flag = false;

void loop ()
{
  int randomNumber = distrib(gen);// Seed for random number

  //Press any key to start sending numbers as well as the timer
  while(!start_flag)
  {
    if (Serial.available() > 0) 
    {
      Serial.println("Start");
      start_flag = true;
    } 
  }
    
  if(first_iteration)//Read timer once experiment starts
  {
    init_time = millis();
    first_iteration = false;
  }
  current_time = millis();

  if ((current_time - init_time) < 120000)//Verify if timer exceed 2 minutes
  {
    if (Serial.available() > 0) 
    {
      char inputChar = Serial.read(); // Read a character from the serial input
      Serial.println(inputChar);
      if (inputChar == 'n')
      {
        char output[5]={0};
        Serial.println("Sensors");
        results[trials][0] = braille_codes_dec[randomNumber]; // Record the expected result in result field 0
        Serial.println(braille_codes_dec[randomNumber]); //Shows the number 
        delay(500);//Delay of 500ms to give time to the experimenter to tell the number to the participant
 
        while (output[0] == '\0')//Wait until participant introduce the number in Braille code
        {
           //Call force sensor function
           force_sensors(thr1,frames,output);
           force_sensors(thr1,frames,output);
        }
        
        int index = findBrailleCodeIndex(braille_codes, output);//Decode the Braille code inserted by the participant and store the decimal value in results field 1
        if (index != -1)
        {
          results[trials][1] = braille_codes_dec[index];
        }
        else//In case of missmatch store -1
        {
          results[trials][1] = -1;
        }
        //Provide visual feedback to the experimenter about the recorded results for every iteration
        Serial.print(results[trials][0]);
        Serial.print(',');
        Serial.print(results[trials][1]);
        trials++;
      }
    } 
  }
  else
  {
    //Indicate end of experiment after 2 minutes
    if(!end_flag)
    {
      Serial.println();
      Serial.println("End");
      end_flag = true;
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

/*The debouncing functionality in this code helps filter out noise and stabilize sensor readings by taking multiple readings
over time and considering a sensor as active only if it consistently exceeds a threshold in a majority of those readings.*/
void force_sensors(int threshold, int numReadings, char* result)
{
  bool anySensorActive = false;// Flag to track if any sensor is active
  int activeCount[4] = {0, 0, 0, 0}; // Counter array for active readings for each sensor
  int sensorPins[4] = {fsPin1, fsPin2, fsPin3, fsPin4}; // Array of sensor pins

  memset(result, 0, 4);
  memset(result, '0', 4);
  
  for (int sensor = 0; sensor < 4; sensor++)
  {
      for (int i = 0; i < numReadings; i++)
      {
          int reading = analogRead(sensorPins[sensor]);// Read analog sensor value
          int voltage = map(reading, 0, 4095, 0, 3300);// Map the reading to voltage

          if (voltage > threshold)
          {
              activeCount[sensor]++;// Increment the active count for this sensor
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

  if (!anySensorActive) //If no sensor active then set output as null character
  {
    memset(result, 0, 4);
  }
}

int findBrailleCodeIndex(char codes[][6], const char* output)
{
    for (int i = 0; i < 10; ++i)
    {
        if (strcmp(codes[i], output) == 0) // Compare each code with the given output
        {
            return i; // Return the index if a match is found
        }
    }
    return -1; // Return -1 to indicate no match was found
}
