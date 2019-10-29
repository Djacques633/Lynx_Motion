//
//  Notes:
//  Max height is 147, Lowest height is 22.
//  Any negative angles are ignored and the HPR is thrown away.
//  
//
//
#include <math.h> 
#include "Timer.h"

#define DEBUG
//#define SWEEP
#define ERRORNUM -1000
#define TIMEOUT 1000
#define POLLINT 1000
#define MIN_ANGLE -10
#define DEFAULT_POS 1350;
#define REFRESH_RATE 100
int move_time = REFRESH_RATE * 3;

unsigned long last_time = millis();
unsigned long last_update = millis();

int busy = 2;
int lastid = 0;
String message;
String first;
int numQueries = 10;

int p0 = DEFAULT_POS;
int p1 = DEFAULT_POS;
int p2 = DEFAULT_POS;
int p3 = 0;

//float calculate(float, float, float);

void setup() {
  
  Serial.begin(115200);
  Serial1.begin(115200);
  Serial1.println("#254CLED1");

  //Serial1.println("#254RESET");
  

  Serial1.println("#254CSR60");
  Serial1.println("#254AD100");
  Serial1.println("#254AA100");
  
  
  //Serial1.println("#254D2700");
  
  
  //Serial1.println("#4D0");
  //Serial1.println("#0D-700");
  //delay(2000);
  Serial1.println("#254CLED2");
 // Serial1.println("#254SR60");
  //Serial1.println("#4RS");
  //Serial1.println("#4WR20");
  //Serial1.println("#4RS");
  //Serial1.println("#254S4");
  //Serial1.println("#254EM0");


 // check_position();
 // check_position();
 // check_position();
  
}

bool sweep = true;
float angle = 0.0;
float stp = 20.0;
float mn = 0.0;
float mx = 90.0;

unsigned long last_step = millis();


void loop() {
  
  // We got a message
  if(Serial.available()){   
      //last_time = millis();
#ifdef SWEEP
      stp = Serial.parseFloat();
      Serial.read();
      sweep = true;
#else      
      // Read in first float (angle 1)
      p0 = 3.0 * Serial.parseFloat();
      // Consume ',' 
      Serial.read();
      

      // Read in next float (angle 2)
      p1 = 3.0 * Serial.parseFloat();
      // Consume ',' 
      Serial.read();

      
      // Read in next float (angle 3)
      p2 = 3.0 * Serial.parseFloat();
      // Consume ',' 
      Serial.read();

      
      //Read in the yaw
      p3 = Serial.parseFloat();
      // Consume '\n'
      Serial.read();
#endif
  }
  if(Serial1.available()){
    parsePos();
  }
#ifdef SWEEP
  unsigned long t = millis();
  float thisStep = ((t - last_step) * stp / 1000.0);
  last_step = t;
  
  if (sweep){
    angle += thisStep;
    if (angle > mx || angle < mn){
      stp = -stp;
      angle =  constrain(angle, mn, mx);
    }
    p0 = (int)(3 * angle * 10.0);
    p1 = p0;
    p2 = p0;
  }
#endif
    
  if(millis() - last_update > REFRESH_RATE){

   // Serial.println(p0);
    lssUpdate();

    last_update = millis();
  }

  
  if (millis() - last_time > POLLINT){
    check_position();
    last_time = millis();
  }
}



bool charReady(){
  long timeout = millis();
  while(!Serial1.available()){
      if (millis() - timeout > TIMEOUT){
        Serial.println("TIMEOUT");
        return false;
      }
    }
    return true;
}


// TODO: Async this!
void parsePos(){
  
  long timeout = millis();
  char c = (char)Serial1.read();
  if(c != '*'){
    return;
  }
  if(!charReady()){
    return;
  }
  
  int id = Serial1.parseInt();

  if(!charReady()){
    return;
  }
  
  c = (char)Serial1.read();
  if(c != 'Q'){
    return;
  }
  
  if(!charReady()){
    return;
  }
  
  c = (char)Serial1.read();
  if(c != 'D'){
    return;
  }
  
  if(!charReady()){
    return;
  }
  int pos = Serial1.parseInt();
  Serial.println("Motor Position: "+ (String)pos);
  Serial1.read();

  if(pos < MIN_ANGLE){
    message = "#" + (String)id + "O-3600";
    Serial1.println(message); //#254O-3600
    Serial.println((String)id + ": NEGATIVE");
  }
  numQueries = constrain(numQueries-2,0,10);
}



bool check_position(){
  lastid = (lastid) % 3 + 1;  

  message = "#" + (String)lastid + "QD";
  Serial1.println(message);
  Serial.println(message);
  numQueries = constrain(numQueries + 1,0,10);
  return true;
//  int result = parsePos(lastid);
//  if(result == ERRORNUM){
//    return false;
//  }
//  
//  #ifdef DEBUG
//    message = (String)result;
//    Serial.println((String)lastid + ":  " + message);
//  #endif  
  
  
  
  
}




// Function to update the serial outputs to the servos

char lssOutput[100];

void lssUpdate() {
  if(numQueries > 4){
    return;
  }
  sprintf(lssOutput, "#%u D%d T%u\r #%u D%d T%u\r #%u D%d T%u\r #%u D%d T%u\r",
    1,p0,move_time,
    2,p1,move_time,
    3,p2,move_time,
    4,p3,move_time
  );

  Serial1.println(lssOutput);
  Serial.println(lssOutput);

}
