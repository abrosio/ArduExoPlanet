#include <Stepper.h>

#define STEPS_PER_REV 2048

#define IN1 2
#define IN2 3
#define IN3 4
#define IN4 5

#define POT_PIN A1

Stepper stepperMotor(STEPS_PER_REV, IN1, IN3, IN2, IN4);

int motorSpeed = 0; 
const int MAX_SPEED = 31; 

void setup() {
  stepperMotor.setSpeed(motorSpeed);
}

void loop() {
  int potValue = analogRead(POT_PIN);

  motorSpeed = map(potValue, 0, 1023, 0, MAX_SPEED);

  stepperMotor.setSpeed(motorSpeed);

  if (motorSpeed > 0) {
    stepperMotor.step(STEPS_PER_REV / 100); 
  }
}
