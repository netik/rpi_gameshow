
/* D4-D7 is Player 1,2,3,4 LED with external pullups */

/* D9, D11, D12, D13 is Player 4,3,2,1 switches */

const unsigned int led_pins[] = { 4, 5, 6, 7 };
const unsigned int input_pins[] = { 12 , 11, 10, 9 };

void setup() {
  // put your setup code here, to run once:

  PCICR |= 0b00000001;   // turn on port b
/*  PCMSK0 |= 0b00100000;  // D13 / PCINT5 -- can't use due to LED
  PCMSK0 |= 0b00010000;  // D12 / PCINT4
  PCMSK0 |= 0b00001000;  // D11 / PCINT3
  PCMSK0 |= 0b00000000;  // D10 / PCINT2
  PCMSK0 |= 0b00000010;  // D9 / PCINT1
*/
  
  // easier way?
  //             12              11             19               9 
  PCMSK0 |=  (1 << PCINT4) | (1 << PCINT3) | (1 << PCINT2) | (1 << PCINT1);


  for (unsigned int x = 0; x < 4; x++) {
    pinMode(led_pins[x], OUTPUT);
    pinMode(input_pins[x], INPUT);
  }
  Serial.begin(9600);

    Serial.print("RESET ");
    dump_byte(PINB);
};

/*
  Interrupt pin handling

  PCMSK0 -> PB -> D8 to D13 pins
  PCMSK1 -> PC -> A0 to A5 pins
  PCMSK2 -> PD -> D0 to D7 pins
*/

void dump_byte(byte) {

  for (int i = 7; i >0; i--) {
    if (PINB & (1 << i)) {
      Serial.print("1");
    } else {
      Serial.print("0");
    }
  }

  Serial.println();
};

void showPinStates() {
  // put your main code here, to run repeatedly:
  for (int pin = 10; pin < 14; pin++) {
    int switchState = digitalRead(pin);

    Serial.print(pin);
    Serial.print(":");
    if (switchState) {
      Serial.print("1 ");
    } else {
      Serial.print("0 ");
    }
  }
  Serial.println(" ");
}

void loop() {
  // showPinStates();
  delay(1000);
};

/*

ISR(PCINT0_vect){}    // Port B, PCINT0 - PCINT7
ISR(PCINT1_vect){}    // Port C, PCINT8 - PCINT14
ISR(PCINT2_vect){}    // Port D, PCINT16 - PCINT23
*/

ISR(PCINT0_vect) {
  static unsigned long last_interrupt_time = 0;
  unsigned long interrupt_time = millis();

  // If interrupts come faster than 200ms, assume it's a bounce and ignore
  if (interrupt_time - last_interrupt_time > 100) {
    Serial.print("INT ");
    dump_byte(PINB);
    dump_byte(EIFR);
    dump_byte(EIFR);

  }
  last_interrupt_time = interrupt_time;
}
