const int fsrPin1 = 26; // Analog Pin A0;
const int fsrPin2 = 26;
const int fsrPin3 = 26;
const int fsrPin4 = 26;

const int number_fsr = 4;
const int bufferSize = 150; // 150
float sensorValues[number_fsr];

void setup() {
  Serial.begin(512000);
  delay(1000);
}

void loop() {
  // TODO: read sensor values
  // sensorValues = read_fsr_sensors()
  // TODO: send sensor values
  // msg = encode_message(sensorValues) //expected format: msg = "XXX_XXX_XXX_XXX"
  // Serial.println(msg)

}
