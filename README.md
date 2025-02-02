# ArduExoPlanet

In questo lavoro è stato studiato un modello didattico sperimentale per simulare i transiti dei pianeti extrasolari e le relative curve di luce. Il modello proposto, denominato ArduExoPlanet, è stato realizzato con schede Arduino e altri materiali facilmente reperibili. L’utilizzo di una fotoresistenza, che simula il rivelatore di luce, permette l’acquisizione di dati e l’analisi quantitativa del fenomeno studiato. Questo sistema ha evidenziato un forte interesse didattico tra gli studenti sia per l’introduzione a temi astrofisici attraverso la metodologia sperimentale sia per la possibilità di utilizzare anche lo smartphone per l’acquisizione dei dati.

---

## Reference
Il firmware utilizzato per il prototipo è basato sul progetto realizzato da PLAY-INAF (link https://play.inaf.it/transiti-con-arduino/) 


## Project Overview

### Componenti

#### Lato Motore
- **Microcontroller**: Arduino Uno R3 (protitopo) - Arduino Nano (modello implementato)
- **Motore Stepper**: 28BYJ-48 con ULN2003 driver
- **Potenziometro**: 10KΩ (prototipo) 5kΩ (modello implementato)
- **Pulsante ON/OFF**
- **Alimentazione**: Batteria Lipo 3S + convertirore a 9V Mini360

**Connessioni:**
- Per il prototipo il driver ULN2003 è stato connesso a D8,D9,D10 e D11, mentre per il modello implementato è connesso a D1, D2, D3, e D4 su Arduino Nano

#### Lato LDR:
- **Light Dependent Resistor (LDR)**: 5mm per il prototipo e 12 mm per il modello implementato
- **Potenziometro**: 10kΩ per il prototipo e 20kΩ per il modello implementato
- **Microcontroller**: Arduino Uno R3 per il prototipo e Arduino Nano per il modello implementato

**Connessioni:**
- LDR e il potenziometro sono connessi in parallelo al pin A0 per entrmabi i modelli

---

## Stampa 3D modello implementato
I file per stampare in 3D il modello finale chiamato modello implementato possono essere reperiti qui:  
[Thingiverse - ArduExoplanet Model](https://www.thingiverse.com/thing:6888870)

![Interface Example](Arduexo2.png)
![Interface Example](Arduexo.png)

---

## Plottaggio e visualizzazione dei dati
Per visualizzare i dati raccolti e salvarli su un file txt è stato realizzato un piccolo software in Python chiamato ArduExoPlanet Analyzer che è possibile scaricare o come file sorgente o l'eseguibile.
E' tuttavia possibile utilizzare l'ide di Arduino o altri software come putty per poter leggere sul seriale i valori rilevati e poi plottarli con Excel.
[ArduExoplanet Plotter](https://github.com/abrosio/ArduExoplanet_Plotter)

---

## Caratteristiche Chiave

- **Stepper Motor Control**: Controllo regolare e preciso della rotazione planetaria con schermo OLED che mostra i giri al minuto
- **Light Sensing**: Misura in maniera precisa la luce che arriva dalla "stella"
- **Battery Powered**: Facilmente alimentabile tramite le porte usb e una piccola batteria LIPO
- **Customizable Components**: tutte le parti sono di facile reperimento e le parti in 3d sono stampabili anche con piccole stampanti

---

## Firmware
Il firmware di Arduino per il motore stepper e per la fotoresistenza sono scaricabili da questa repository. Si raccomanda di usare l'ide di arduino con le relative librerie e dipendenze.
Le librerie necessarie per il progetto sono: 
AccelStepper
Adafruit_GFX.h
Adafruit_SSD1306.h

---

## Istruzioni d'Uso

1. **Configurazione Hardware:**
   - Assembla le parti stampate in 3D seguendo il design disponibile su Thingiverse.
   - Collega i componenti elettronici come mostrato nella sezione schemi.
   - Assicurati che la batteria LiPo sia carica e collegata al convertitore di tensione nel modello implementato.

2. **Caricamento del Firmware**
   - Apri l’IDE di Arduino.
   - Carica i file del firmware per il motore passo-passo e per il sistema LDR.
   - Carica il codice sull’Arduino Uno/Nano.

3. **Esecuzione del Sistema:**
   - Accendi il sistema utilizzando l’interruttore On/Off.
   - Usa il potenziometro per controllare la rotazione del motore passo-passo.
   - Monitora le variazioni di luce tramite il sistema LDR.

---

## Contributi
I contributi al progetto sono benvenuti! Sentiti libero di aprire un’issue o una pull request su questo repository per suggerire miglioramenti o segnalare problemi.

---

© 2025 Antonino Brosio - [www.antoninobrosio.it](https://www.antoninobrosio.it) & Domenico Liguori [astrolabcariati.altervista.org](http://astrolabcariati.altervista.org)

Grazie per aver esplorato ArduExoplanet! Se hai domande o suggerimenti, non esitare a contattarci.
