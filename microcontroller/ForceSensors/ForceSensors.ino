double thr1=1000;
double thr2=1.5;


//Pins for force sensors
int fsPin1 = 34; //A2
int fsPin2 = 39; //A3
int fsPin3 = 36; //A4
int fsPin4 = 32; //GPIO 32

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


void setup () 
{
Serial . begin (9600); // 9600 bits per second
}

void loop (void) {
  //vector<int> result={0,0,0,0};
  char result [5] = "0000";
 
  reading1 = analogRead ( pin1 );
  voltage1 = map( reading1 , 0, 4095 , 0, 3300);

  reading2 = analogRead ( pin2 );
  voltage2 = map( reading2 , 0, 4095 , 0, 3300);

  reading3 = analogRead ( pin3 );
  voltage3 = map( reading3 , 0, 4095 , 0, 3300);

  reading4 = analogRead ( pin4 );
  voltage4 = map( reading4 , 0, 4095 , 0, 3300);
  
  if ( voltage1 > thr1) {
    result[3] = '1';
    
  }
  if ( voltage2 > thr1) {
    result[2] = '1';
  }
  if ( voltage3 > thr1) {
    result[1] = '1';
  }
  if ( voltage4 > thr1) {
    result[0] = '1';
  }
  //Serial . print (" Voltage   reading  in mV = ");
  Serial . println ( result );
  Serial . println ( voltage1 );
  Serial . println ( voltage2 );
  Serial . println ( voltage3 );
  Serial . println ( voltage4 );
  delay (2000);
  //Serial . print (" Analog   reading  = ");
  //Serial . println ( fsrReading );
  //Serial . print (" Voltage   reading  in mV = ");
  //Serial . println ( fsrVoltage );
}
