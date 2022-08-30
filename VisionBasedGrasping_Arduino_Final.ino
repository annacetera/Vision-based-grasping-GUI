#define dirPin 2
#define stepPin 3
#define stepsPerRevolution 1600/3 //120 degrees
//#define stepsPerRevolution 533 //120 degrees
#define stepsPerRevolutionCCW 533 - 30 //120 degrees
//#define stepsPerRevolutionCCW ( ( 1600/3 )  + 40 )
int motorCommand; 
# define buzzer 7
# define glasses 13
#define TBS 2000
#define off 3000
#define on 2000

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(buzzer,OUTPUT);
  pinMode(glasses,OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
while (Serial.available()==0){
  digitalWrite(stepPin, LOW);
 }
//motorCommand = Serial.parseInt();
motorCommand = Serial.read()-48;
//motorCommand = Serial.readStringUntil('\r');
//Serial.println(motorCommand);

if (motorCommand==1){ // SHOWS BOTTLE (CW)
  digitalWrite(dirPin, HIGH);

  // Spin the stepper motor 1 revolution slowly:
  for (int i = 0; i < stepsPerRevolution; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(on); //adjusts time between steps 
    digitalWrite(stepPin, LOW);
    delayMicroseconds(off);
  }
}

if (motorCommand == 3){ // SHOWS NO OBJECT FROM BOTTLE (CCW)
  digitalWrite(dirPin, LOW);
  // Spin the stepper motor 1 revolution quickly:
  for (int i = 0; i < stepsPerRevolution; i++) {
    // These four lines result in 1 step:
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(on);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(off);
  }
}

if (motorCommand==2){ // SHOWS PEN (CCW)
  digitalWrite(dirPin, LOW);

  // Spin the stepper motor 1 revolution quickly:
  for (int i = 0; i < stepsPerRevolution; i++) {
    // These four lines result in 1 step:
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(on);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(off);
  }
}

if(motorCommand == 4) { // SHOWS NO OBJECT FROM  PEN (CW)
  digitalWrite(dirPin, HIGH);

  // Spin the stepper motor 1 revolution slowly:
  for (int i = 0; i < stepsPerRevolution; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(on); //adjusts time between steps 
    digitalWrite(stepPin, LOW);
    delayMicroseconds(off);
  }
}

if (motorCommand == 5) { //BUZZER ON AND OFF
  digitalWrite(buzzer,HIGH);
  delay(500);
  digitalWrite(buzzer,LOW);
  delay(500);
}
if(motorCommand==6) { //GLASSES ON 
  digitalWrite(glasses,HIGH);
  delay(1000);
  //digitalWrite(glasses,LOW);
  //delay(200);
}
if (motorCommand == 7) { //BUZZER ON AND OFF
  digitalWrite(buzzer,HIGH);
  delay(2000);
  digitalWrite(buzzer,LOW);
  delay(500);
}

if(motorCommand==8) { //GLASSES OFF
  digitalWrite(glasses,LOW);
  delay(200);
}

}
