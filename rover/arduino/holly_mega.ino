/* * HOLLY - Milestone 1: Foundation (V10.0)
 * Solo movimento base tramite Driver L298N.
 * Ricezione comandi via Seriale dal Raspberry Pi.
 */

#define ENA 10 
#define IN1 9
#define IN2 8
#define IN3 7
#define IN4 6
#define ENB 5

int vel = 100; // Velocità fissa per i primi test

void setup() {
  Serial1.begin(115200); // Comunicazione con Raspberry Pi
  
  // Configurazione Pin Motori
  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  
  stoppa();
}

void loop() {
  if (Serial1.available() > 0) {
    char comando = Serial1.read();
    
    if (comando == 'W') muovi(vel, vel);        // Avanti
    else if (comando == 'S') muovi(-vel, -vel); // Indietro
    else if (comando == 'A') muovi(-vel, vel);  // Ruota SX
    else if (comando == 'D') muovi(vel, -vel);  // Ruota DX
    else if (comando == 'X') stoppa();          // Stop
  }
}

void muovi(int l, int r) {
  // Motore Sinistro
  digitalWrite(IN1, l > 0 ? LOW : HIGH); 
  digitalWrite(IN2, l > 0 ? HIGH : LOW);
  analogWrite(ENA, abs(l));
  
  // Motore Destro
  digitalWrite(IN3, r > 0 ? LOW : HIGH); 
  digitalWrite(IN4, r > 0 ? HIGH : LOW);
  analogWrite(ENB, abs(r));
}

void stoppa() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  analogWrite(ENA, 0); analogWrite(ENB, 0);
}