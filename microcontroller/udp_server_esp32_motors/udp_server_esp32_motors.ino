#include <WiFi.h>
#include <WiFiUdp.h>
#include <stdlib.h>
#include <analogWrite.h>
#include <Wire.h>

WiFiUDP Udp; // Creation of wifi Udp instance

char packetBuffer[255];

unsigned int localPort = 9999;
const char *ssid = "ESP32_Group2"; // X is your group number
const char *password = "ICSESP32IMU";

IPAddress ipServer(192, 168, 4, 3);   // IP for ESP32
IPAddress ipClient(192, 168, 4, 2);   // My computer, different IP than from ESP32
IPAddress Subnet(255, 255, 255, 0);

int number_vibros = 4;
int check_sum = 285; //"_" times (number_of_vibros-1) /475 /5 * 3

int array_ints[16]; //4 x 4

int motorPin1 = 32;    // GPIO 32 for vibration motor 1
int motorPin2 = 33;   // GPIO 33 for vibration motor 2
int motorPin3 = 14;   // GPIO 14 for vibration motor 3
int motorPin4 = 15;   // GPIO 15 for vibration motor 4

float motor_array1[4];

void setup() {
  Wire.begin();
  Serial.begin(512000);
  WiFi.mode(WIFI_AP); // ESP32 as AP
  WiFi.softAP(ssid, password);
  WiFi.softAPConfig(ipServer, ipClient, Subnet);
  Udp.begin(localPort);


  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  pinMode(motorPin3, OUTPUT);
  pinMode(motorPin4, OUTPUT);
}


void loop() {
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    Udp.read(packetBuffer, 255);
    String datReq(packetBuffer);

    int b = datReq[3] + datReq[7] + datReq[11]; //equals 475, if all are "_" (ascii). It included "ser_data[0] + " before, but that was replaced by number of ESP.
    //Serial.println(b);

    if (b != check_sum) {
      Serial.print("Discharged Data Package. It was: ");
      Serial.println(datReq);
    }
    else if (b == check_sum) {
      Serial.println("Used Data Package.");
      // Serial.print(". ");
      for (int i = 0; i < 4 * number_vibros; i++) { //make ints out of ASCII code. Look only at 24 chars (rest is there for fun)
        array_ints[i] = (int) datReq[i];
        array_ints[i] -= 48;
        //Serial.print(array_ints[i]);
        //Serial.println(array_ints[i]);
      }
    }
    for (int i = 0; i < 4; i++)
    {
      motor_array1[i] = (array_ints[i * 4] * 100 + array_ints[i * 4 + 1] * 10 + array_ints[i * 4 + 2]) ;
      Serial.println(motor_array1[i]);
    }
    analogWrite(motorPin1, motor_array1[0]); // 0 to 255
    analogWrite(motorPin2, motor_array1[1]); // 0 to 255
    analogWrite(motorPin3, motor_array1[2]); // 0 to 255
    analogWrite(motorPin4, motor_array1[3]); // 0 to 255
  }
}
