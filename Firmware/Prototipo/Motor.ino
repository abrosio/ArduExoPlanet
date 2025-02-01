/*Questo sketch permette di mettere in funzione il motore passo passo 
 * e di definire la velocità di rotazione mediante un potenziometro.
 * Il verso, orario o antiorario, e dato dalla pressione di un bottone
 */

//definizione delle librerie del motore passo passo
#include <Stepper.h>
#define STEPS 96
 
Stepper stepper(STEPS, 8, 10, 9, 11);
const int button =  13; //La direzione di rotazione è controllata da un bottone collegato al pin 13 --prima era sul 4
const int pot    = A0; //La velocità è controllata da un potenziometro connesso al pin analogico A0
 
void setup()
{
  pinMode(button, INPUT_PULLUP); //il bottone viene letto come input
}
 
int direction_ = 1, speed_ = 0;
 
void loop()
{

//in base al valore del bottone, 0 o 1, il motore girerà in senso orario o antiorario

  if ( digitalRead(button) == 0 )  
    if ( debounce() ) 
    {
      direction_ *= -1;
      while ( debounce() ) ; 
    }
 
  int val = analogRead(pot);

//Qui viene controllata la velocità di rotazione mediante il potenziometro
  if ( speed_ != map(val, 0, 1023, 2, 500) )
  { 
    speed_ = map(val, 0, 1023, 2, 500);
    stepper.setSpeed(speed_);
  }
 
  stepper.step(direction_);
 
}
 

bool debounce()
{
  byte count = 0;
  for(byte i = 0; i < 5; i++) {
    if (digitalRead(button) == 0)
      count++;
    delay(100);
  }
  if(count > 2)  return 1;
  else           return 0;

}
