const int photoResistorPin = A0;

float bias = 0.0;
float conta = 0.0;
float s = 0.0;
int LDR_B = 0; 

void setup() {
  Serial.begin(250000);
  pinMode(photoResistorPin, INPUT);
}

void loop() {
  conta = 0.0; 
  s = 0.0;     

  for (int i = 0; i < 100; i++) {
    int piedistallo = analogRead(photoResistorPin); 
    conta += piedistallo;  
    s += 1.0;             
  }
  bias = conta / s; 

  int LDRValue = analogRead(photoResistorPin);

  int newLDR_B = (1023 - LDRValue) - round(bias);

  if (abs(newLDR_B - LDR_B) >= 1.2) {
    LDR_B = newLDR_B; 
  }

  Serial.println(LDR_B);

  delay(80);
}
