/* Con questo sketch possiamo identificare i transiti di
 *  pianeta (una pallina di stagnola) davanti ad una led. 
 *  Successivamente i dati vengono sia proiettati sul monitor
 *  seriale che scritti su una scheda microSD in modo da poterli
 *  analizzare anche in un secondo momento
 */
//inclusione delle librerie per la lettura della scheda SD
#include <SD.h>                    
#include <SPI.h>

//Dichiarazione delle variabili che useremo
int LDR = A0;                     
int potenziometro = A2;
int led = 5;
float conta = 0.0;
float piedistallo = 0.0;
float s = 0.0;
float bias = 0.0;
float LDR_B = 0.0;

int chipSelect = 4; 
File datalogger; 

void setup() 
{
    pinMode (led, OUTPUT);          //Dichiarazione del led come output
    Serial.begin(250000);          //Apertura e preparazione del monitor seriale
    pinMode(LDR, INPUT);           //Dichiarazione della fotoresistenza come input
    SD.begin(3);                   //Dichiarazione del pin di lettura della scheda SD

    datalogger = SD.open("data.txt", FILE_WRITE);  //apertura del file data.txt e inizio di scrittura
    datalogger.print("\n");
    datalogger.println("--------------- Nuova lettura ---------------");
    datalogger.println("\n");
    datalogger.print("\n");
    datalogger.close();
}

void loop() {
    /* Qui andiamo a calcolare e poi a eliminare la presenza di errori
     * dovuti a correnti esterni, fonte di luce esterne ecc... Nella fase
     * sucessiva definiamo una variabile bias che è la media di questi
     * errori e la sottraiamo al valore letto dalla fotoresistenza.
     * In questo modo vengono identificati solo i conteggi reali dovuti
     * al transito del pianeta.
     */
    for (int i = 0; i < 100; i++) {              
        float piedistallo = analogRead(LDR);
        conta = piedistallo + conta;
        s = s + 1.0;
    }

    bias = (conta / s);

    int intensita = analogRead(potenziometro);
    analogWrite(led, intensita / 4);

    int LDRValue = analogRead(LDR);
    float LDR_nb = analogRead(LDR);
    LDR_B = LDR_nb - bias;

    /* L'operatore datalogger apre la scheda SD e inizia a creare  
     * il file secondo una formattazione da noi voluta.
     */
    datalogger = SD.open("data.txt", FILE_WRITE); 
  
    if (datalogger) {
        float time = millis(); // Tempo in millisecondi
        int LDRValue = analogRead(LDR);

        datalogger.print("I= ");             // Scrive 'I = ' nel file data.txt  
        datalogger.print("\t");              // Da una tabulazione
        datalogger.print(LDR_B, 1);          // Scrive il valore letto dal sensore e sottratto per il bias
        datalogger.print("\t");              // Da una tabulazione
        datalogger.print("t= ");             // Scrive 't = ' nel file data.txt
        datalogger.print("\t");              // Da una tabulazione
        datalogger.print(time, 1);           // Scrive il valore di tempo in millisecondi
        datalogger.println("\n");            // Va a capo e si riparte con una nuova linea
        datalogger.close();
    }

    float timeInSeconds = millis() / 1000.0; // Converti il tempo in secondi
     Serial.print(timeInSeconds);
      Serial.print("   ");
    //Serial.print("LDR_B: ");
    Serial.println(LDR_B);
    //Serial.print(" | Tempo (s): ");
   
   

    delay(100); // Campionamento dell'acquisizione in ms
}
