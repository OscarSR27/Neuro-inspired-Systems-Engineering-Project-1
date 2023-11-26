#include <WiFi.h>
#include <WiFiUdp.h>

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

int thr1=1000;
int thr2=1.5;
const int numReadings = 10;

int reading1 ;
int voltage1 ;
unsigned long fsrResistance1 ;
//long fsrForce1 ;

int reading2 ;
int voltage2 ;
unsigned long fsrResistance2 ;
long fsrForce2 ;

int reading3 ;
int voltage3 ;
unsigned long fsrResistance3 ;
long fsrForce3 ;

int reading4 ;
int voltage4 ;
unsigned long fsrResistance4 ;
long fsrForce4 ;

unsigned long fsrConductance ;

WiFiUDP Udp; // creation of wifi Udp instance
char packetBuffer [255];
IPAddress clientIp(192, 168, 4, 2);
unsigned int localPort = 9999;
const char * ssid = " ESP32_for_IMU ";
const char * password = " ICSESP32IMU ";
int motor_selection = 0;
bool m1,m2,m3,m4 = false;

void force_sensors(int threshold, int numReadings, char* result);
bool processUdpPacket(WiFiUDP &Udp, char *packetBuffer, int delay_millis);
void vibration_control(int motor_1,int motor_2,int motor_3,int motor_4,int delay_millis);
void sendUdpData(WiFiUDP &udp, const char *data, IPAddress ip, unsigned int port);

enum STATE 
{
    READ_INPUT,
    ROLE,
    READ,
    CONFIRM,
    SEND,
    WAIT_CONFIRMATION
};

STATE currentState = READ_INPUT;

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

int packetSize = 0;
char result[5] = {0};//Initialize result with null character
bool start_communication = false;
bool sent_role = false;
bool read_role = false;
bool received = false;
bool resend = false;
bool confirmation = false;

void loop ()
{
  Serial.println ("Init");
  Serial.println (currentState);
  switch (currentState)
  {
    case READ_INPUT:
         Serial.println ("READ_INPUT");
         //ToDo: Add delay before reading sensors? Vibrotactile feedback to indicate init of reading and end of reading? 1 motor starts, 2 motors end?
         memset(result, 0, sizeof(result));//Set result array to null character
         force_sensors(thr1,numReadings,result);
         if (result[0] != '\0')
         {
            currentState = ROLE;
            sendUdpData(Udp, result, clientIp, localPort);
            Serial.println (result);
            Serial.println ("ROLE");
         }
         break;
    case ROLE:
         packetSize = Udp.parsePacket();
         read_role = packetSize==0?false:processUdpPacket(Udp, packetBuffer, 1000);
         if (read_role)
         {
            Serial.println (packetBuffer);
            if (packetBuffer[0] == '1' && packetBuffer[1] == '0' && packetBuffer[2] == '0' && packetBuffer[3] == '0')//Receiver role code = 1000
            {
              currentState = READ;
              Serial.println ("READ");
            }
            else if (packetBuffer[0] == '0' && packetBuffer[1] == '1' && packetBuffer[2] == '0' && packetBuffer[3] == '0')//Sender role code = 0100
            {
              currentState = SEND;
              Serial.println ("SEND");
            }
         }
         delay(2000);
         break;
    case READ:
         packetSize = Udp.parsePacket();
         received = packetSize==0?false:processUdpPacket(Udp, packetBuffer, 1000);
         if (received)
         {
            currentState = CONFIRM;
            Serial.println ("CONFIRM");
         }
         delay(2000);
         break;
    case CONFIRM:
         //ToDo: Add delay before reading sensors? Vibrotactile feedback to indicate init of reading and end of reading? 1 motor starts, 2 motors end?
         memset(result, 0, sizeof(result));//Set result array to null character
         force_sensors(thr1,numReadings,result);
         if (result[0] == '1' && result[1] == '0' && result[2] == '0' && result[3] == '0') //Confirmation code = 1000
         {
            currentState = SEND;
            sendUdpData(Udp, result, clientIp, localPort);
            Serial.println ("SEND");
         }
         else if (result[0] == '0' && result[1] == '1' && result[2] == '0' && result[3] == '0') //Resend code = 0100
         {
            received = false;
            currentState = READ;
            sendUdpData(Udp, result, clientIp, localPort);
            Serial.println ("READ");
         }
         delay(2000);
         break;
    case SEND:
         //ToDo: Add delay before reading sensors? Vibrotactile feedback to indicate init of reading and end of reading? 1 motor starts, 2 motors end?
         memset(result, 0, sizeof(result));//Set result array to null character
         force_sensors(thr1,numReadings,result);
         if (result[0] != '\0')
         {
            currentState = WAIT_CONFIRMATION;
            sendUdpData(Udp, result, clientIp, localPort);
            Serial.println ("WAIT_CONFIRMATION");
         }
         delay(2000);
         break;
    case WAIT_CONFIRMATION:
         packetSize = Udp.parsePacket();
         confirmation = packetSize==0?false:processUdpPacket(Udp, packetBuffer, 1000);
         if (confirmation)
         {
            if (packetBuffer[0] == '1' && packetBuffer[1] == '0' && packetBuffer[2] == '0' && packetBuffer[3] == '0')//Confirmation code = 1000
            {
              currentState = READ;
              //Reset all control variables
              int packetSize = 0;
              char result[5] = {0};//Initialize result with null character
              bool start_communication = false;
              bool sent_role = false;
              bool read_role = false;
              bool received = false;
              bool resend = false;
              bool confirmation = false;
              Serial.println ("READ");
            }
            else if (packetBuffer[0] == '0' && packetBuffer[1] == '1' && packetBuffer[2] == '0' && packetBuffer[3] == '0')//Resend code = 0100
            {
              currentState = SEND;
              Serial.println ("SEND");
            }
         }
         delay(2000);
         break;
    default:
         int packetSize = 0;
         char result[5] = {0};//Initialize result with null character
         bool start_communication = false;
         bool sent_role = false;
         bool read_role = false;
         bool received = false;
         bool resend = false;
         bool confirmation = false;
         break;
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

  Serial.println(result);
}

bool processUdpPacket(WiFiUDP &Udp, char *packetBuffer, int delay_millis)
{
    int len = Udp.read(packetBuffer, 255);
    if (len > 0) packetBuffer[len - 1] = 0;

    int m1 = packetBuffer[0] - '0'; // Convert 1 char to integer
    int m2 = packetBuffer[1] - '0'; // Convert 1 char to integer
    int m3 = packetBuffer[2] - '0'; // Convert 1 char to integer
    int m4 = packetBuffer[3] - '0'; // Convert 1 char to integer
    
    vibration_control(m1, m2, m3, m4, delay_millis);
    Serial.print("The receiving message is: ");
    Serial.println(packetBuffer);

    return true; // Return true if a packet was received and processed
}

void vibration_control(int motor_1,int motor_2,int motor_3,int motor_4,int delay_millis)
{
  digitalWrite ( motorPin1 , motor_1?HIGH:LOW );
  delay (delay_millis);
  digitalWrite ( motorPin1 , LOW );
  
  digitalWrite ( motorPin2 , motor_2?HIGH:LOW);
  delay (delay_millis);
  digitalWrite ( motorPin2 , LOW );
  
  digitalWrite ( motorPin3 , motor_3?HIGH:LOW);
  delay (delay_millis);
  digitalWrite ( motorPin3 , LOW );
  
  digitalWrite ( motorPin4 , motor_4?HIGH:LOW);
  delay (delay_millis);
  digitalWrite ( motorPin4 , LOW );
}

void sendUdpData(WiFiUDP &udp, const char *data, IPAddress ip, unsigned int port)
{
    udp.beginPacket(ip, port);  // Start data transmission
    udp.print(data);            // Send data
    udp.endPacket();            // End transmission
}
