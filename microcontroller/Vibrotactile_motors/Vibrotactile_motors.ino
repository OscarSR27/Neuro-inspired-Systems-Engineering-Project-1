#include <WiFi.h>
#include <WiFiUdp.h>

int motorPin1 = 13; // GPIO 13 for vibration motor 1
int motorPin2 = 12; // GPIO 12 for vibration motor 2
int motorPin3 = 26; // GPIO 12 for vibration motor 2
int motorPin4 = 25; // GPIO 12 for vibration motor 2
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
  Serial.begin(512000);
  WiFi.softAP(ssid , password ); // ESP32 as access point
  Udp . begin ( localPort );
  pinMode ( motorPin1 , OUTPUT );
  pinMode ( motorPin2 , OUTPUT );
  pinMode ( motorPin3 , OUTPUT );
  pinMode ( motorPin4 , OUTPUT );
}

void loop ()
{
  int packetSize = Udp . parsePacket ();
  if ( packetSize ) 
  {
    int len = Udp. read ( packetBuffer , 255);
    if (len > 0) packetBuffer [len -1] = 0;
    m1 = packetBuffer[0] - '0'; // Convert 1 char to integer
    m2 = packetBuffer[1] - '0'; // Convert 2 char to integer
    m3 = packetBuffer[2] - '0'; // Convert 3 char to integer
    m4 = packetBuffer[3] - '0'; // Convert 4 char to integer

    vibration_control(m1,m2,m3,m4);
    Serial . print ("The  receiving   message  is: ");
    Serial . println ( packetBuffer );
    delay (1000);
  }
}

void vibration_control(int motor_1,int motor_2,int motor_3,int motor_4)
{
  
  digitalWrite ( motorPin1 , motor_1?HIGH:LOW );
  delay (100);
  digitalWrite ( motorPin1 , LOW );
  digitalWrite ( motorPin2 , motor_2?HIGH:LOW);
  delay (100);
  digitalWrite ( motorPin2 , LOW );
  digitalWrite ( motorPin3 , motor_3?HIGH:LOW);
  delay (100);
  digitalWrite ( motorPin3 , LOW );
  digitalWrite ( motorPin4 , motor_4?HIGH:LOW);
  delay (100);
  digitalWrite ( motorPin4 , LOW );
  
  
  
  
  
 /*
   analogWrite ( motorPin1 , motor_wave * dutyCycle );
   delay(1000);
   analogWrite ( motorPin1 , 0 * dutyCycle );
   
   analogWrite ( motorPin2 , motor_wave * dutyCycle );
   delay(1000);
   analogWrite ( motorPin2 , 0 * dutyCycle );
   
   analogWrite ( motorPin3 , motor_wave * dutyCycle );
   delay(1000);
   analogWrite ( motorPin3 , 0 * dutyCycle );
   
   analogWrite ( motorPin4 , motor_wave * dutyCycle );
   delay(1000);
   analogWrite ( motorPin4 , 0 * dutyCycle );
   */
}
