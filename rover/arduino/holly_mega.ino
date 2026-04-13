#include <Wire.h>
#include <VL53L0X.h>

// Definizione Pin Motori (Driver L298N)
#define ENA 10 
#define IN1 9
#define IN2 8
#define IN3 7
#define IN4 6
#define ENB 5

// Pin XSHUT per il sensore Frontale (Inizio integrazione ToF)
#define X_F 14 

VL53L0X sF;
int vel = 100;
char comando_rpi = 'X';

void setup() {
  Serial1.begin(115200); // Comunicazione con Raspberry Pi 5
  Wire.begin();
  
  // Configurazione Output Motori
  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  
  // Inizializzazione Sensore Frontale
  pinMode(X_F, OUTPUT);
  digitalWrite(X_F, LOW); 
  delay(100);
  digitalWrite(X_F, HIGH);
  delay(50);
  
  if (sF.init()) {
    sF.setAddress(0x30);
    sF.setTimeout(200);
    sF.startContinuous();
  }
  
  stoppa();
}

void loop() {
  // Lettura distanza frontale
  int dF = sF.readRangeContinuousMillimeters();
  if (sF.timeoutOccurred()) dF = 0;

  // Ricezione comando dal Raspberry
  if (Serial1.available() > 0) {
    comando_rpi = Serial1.read();
  }

  char azione = comando_rpi;

  // LOGICA DI SICUREZZA (VETO)
  // Se il comando è AVANTI (W) ma c'è un ostacolo a meno di 20cm, forza lo STOP
  if (comando_rpi == 'W' && (dF < 200 && dF > 0)) {
    azione = 'X';
  }

  // Esecuzione movimento
  if (azione == 'W') muovi(vel, vel);
  else if (azione == 'S') muovi(-vel, -vel);
  else if (azione == 'A') muovi(-vel, vel);
  else if (azione == 'D') muovi(vel, -vel);
  else stoppa();

  // Invio Telemetria (Formato compatibile con lo script Python V12.4)
  Serial1.print("DATA:");
  Serial1.println(dF);

  delay(50);
}

void muovi(int l, int r) {
  digitalWrite(IN1, l > 0 ? LOW : HIGH); 
  digitalWrite(IN2, l > 0 ? HIGH : LOW);
  analogWrite(ENA, abs(l));
  
  digitalWrite(IN3, r > 0 ? LOW : HIGH); 
  digitalWrite(IN4, r > 0 ? HIGH : LOW);
  analogWrite(ENB, abs(r));
}

void stoppa() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  analogWrite(ENA, 0); analogWrite(ENB, 0);
}