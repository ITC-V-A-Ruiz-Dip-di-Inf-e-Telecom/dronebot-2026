#include <Wire.h>
#include <VL53L0X.h>

#define ENA 10 
#define IN1 9
#define IN2 8
#define IN3 7
#define IN4 6
#define ENB 5
#define X_F 14 
#define X_R 15 
#define X_L 16 
#define X_B 17 
#define B_SX 52 
#define B_DX 53 

int vel = 80; 
char comando_rpi = 'X'; 
VL53L0X sF, sR, sL, sB;

void setup() {
  Serial1.begin(115200); 
  Wire.begin();
  pinMode(B_SX, INPUT_PULLUP); pinMode(B_DX, INPUT_PULLUP);
  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);

  pinMode(X_F, OUTPUT); pinMode(X_R, OUTPUT); pinMode(X_L, OUTPUT); pinMode(X_B, OUTPUT);
  digitalWrite(X_F, LOW); digitalWrite(X_R, LOW); digitalWrite(X_L, LOW); digitalWrite(X_B, LOW);
  delay(100);
  initTof(sF, X_F, 0x30); initTof(sR, X_R, 0x31); initTof(sL, X_L, 0x32); initTof(sB, X_B, 0x33);
}

void initTof(VL53L0X &s, int p, uint8_t a) {
  digitalWrite(p, HIGH); delay(50);
  if(s.init()){ s.setAddress(a); s.setTimeout(200); s.startContinuous(); }
}

void loop() {
  int dF = sF.readRangeContinuousMillimeters();
  int dL = sL.readRangeContinuousMillimeters();
  int dR = sR.readRangeContinuousMillimeters();
  int dB = sB.readRangeContinuousMillimeters();
  bool bSX = (digitalRead(B_SX) == LOW);
  bool bDX = (digitalRead(B_DX) == LOW);

if (Serial1.available() > 0) { comando_rpi = Serial1.read(); }

  char azione = comando_rpi;

  // VETO DI SICUREZZA (Omnidirezionale)
  if (comando_rpi == 'W' && ((dF < 250 && dF > 0) || bSX || bDX)) azione = 'X';
  if (comando_rpi == 'S' && (dB < 200 && dB > 0)) azione = 'X';
  
  // Laterali meno sensibili per permettere manovre in spazi stretti
  if (comando_rpi == 'A' && (dL < 120 && dL > 0)) azione = 'X';
  if (comando_rpi == 'D' && (dR < 120 && dR > 0)) azione = 'X';

  esegui(azione);

  // Telemetria per Raspberry
  Serial1.print("DATA:"); Serial1.print(dF); Serial1.print(",");
  Serial1.print(dL); Serial1.print(","); Serial1.print(dR); Serial1.print(",");
  Serial1.print(dB); Serial1.print(","); Serial1.print(bSX); Serial1.print(",");
  Serial1.println(bDX);

  delay(40); 
}

void esegui(char c) {
  if (c == 'W') muovi(vel, vel);
  else if (c == 'S') muovi(-vel, -vel);
  else if (c == 'A') muovi(-vel, vel);
  else if (c == 'D') muovi(vel, -vel);
  // CORREZIONE STERZATA IN RETRO
  else if (c == 'Q') muovi(-vel/2, -vel); // Baffo SX colpito: Culo a SX, Muso a DX
  else if (c == 'E') muovi(-vel, -vel/2); // Baffo DX colpito: Culo a DX, Muso a SX
  else stoppa();
}

void muovi(int l, int r) {
  digitalWrite(IN1, l > 0 ? LOW : HIGH); digitalWrite(IN2, l > 0 ? HIGH : LOW);
  analogWrite(ENA, abs(l));
  digitalWrite(IN3, r > 0 ? LOW : HIGH); digitalWrite(IN4, r > 0 ? HIGH : LOW);
  analogWrite(ENB, abs(r));
}

void stoppa() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  analogWrite(ENA, 0); analogWrite(ENB, 0);
}
