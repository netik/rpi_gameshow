
#define ONBOARD_LED 13
#undef DEBUG_TOKENS
#define DEBUG 1
#ifdef DEBUG
#define debugString(str) Serial.println(str)
#else
#define debugString(str) (void)0
#endif
#define MAX_TOKENS 4
#define MAX_TOKEN_LENGTH 10
#define MAX_PINS 4

#define INPUT_BYTE PINB
#define LED_BYTE PIND

/* PIN Configuration */
/* D4-D7 is Player 1,2,3,4 LED with external pullups */
/* D9, D11, D12, D13 is Player 4,3,2,1 switches */
const unsigned int led_pins[] = { 4, 5, 6, 7 }; // these are all PIND
const unsigned int input_pins[] = { 13, 12, 11, 10 }; // these are on PINB
const unsigned int input_masks[] = { PCINT2, PCINT3, PCINT4, PCINT5 };

/* Command Buffer */
const byte numChars = 32;
char receivedChars[numChars];  // an array to store the received data
boolean newSerialData = false;
boolean buttonsNeedHandling = false;

void lamp_test() {
  // DFM: On boot we'll light all of the LEDs
  for (unsigned int x = 0; x < 4; x++) {
    digitalWrite(led_pins[x],1);
    delay(100);
  }

  delay(500);
  for (unsigned int x = 0; x < 4; x++) {
    digitalWrite(led_pins[x],0);
  }
}
void setup() {
  // turn on interrupts on port B
 
  PCICR |= 0b00000001;

  // Setup pin interrupt mask register
  //             13              12             11              10
  PCMSK0 |= (1 << PCINT5) | (1 << PCINT4) | (1 << PCINT3) | (1 << PCINT2);

  // configure pins, using external pullups here.
  for (unsigned int x = 0; x < 4; x++) {
    pinMode(led_pins[x], OUTPUT);
    pinMode(input_pins[x], INPUT_PULLUP);
  }

  lamp_test();
  Serial.begin(115200);
  Serial.println("");
  Serial.println("RESET OK");
};

/*
  Interrupt pin handling

  PCMSK0 -> PB -> D8 to D13 pins
  PCMSK1 -> PC -> A0 to A5 pins
  PCMSK2 -> PD -> D0 to D7 pins
*/

void dump_byte(unsigned char theByte) {

  for (int i = 7; i > 0; i--) {
    if (theByte & (1 << i)) {
      Serial.print("1");
    } else {
      Serial.print("0");
    }
  }
};

void showPinStates() {
  // put your main code here, to run repeatedly:
  for (int pin = 0; pin < 4; pin++) {
    int switchState = digitalRead(input_pins[pin]);

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


void recvLine() {
  static byte ndx = 0;
  char endMarker = '\n';
  char rc;

  while (Serial.available() > 0 && newSerialData == false) {
    rc = Serial.read();

    if (rc != endMarker) {
      receivedChars[ndx] = rc;
      ndx++;
      if (ndx >= numChars) {
        ndx = numChars - 1;
      }
    } else {
      receivedChars[ndx] = '\0';  // terminate the string
      ndx = 0;
      newSerialData = true;
    }
  }
}

int parse_string(char* str, char** tokens) {
    int tokenIndex = -1;
    int charIndex = 0;

    for(int i = 0; str[i] != '\0'; i++) {
        if(str[i] != ' ') {
            if (tokenIndex < 0) { tokenIndex = 0; };
            tokens[tokenIndex][charIndex++] = str[i];
        } else {
            tokens[tokenIndex][charIndex] = '\0'; // end of string
            tokenIndex++;
            charIndex = 0;
            if (tokenIndex > MAX_TOKENS) {
              return(MAX_TOKENS);
            }
        }
    }
    tokens[tokenIndex][charIndex] = '\0'; // end of string

    return(tokenIndex+1);
}

void handleCommand(char **tokens) {
 
  /* LED Command
   *    Usage: LED [1-4, or ALL] [0 or 1] to change LED state.
   */
  if (strncmp(tokens[0], "LED", 5) == 0) {
    int state = atoi(tokens[2]);

    if (state != 0 && state != 1) {
      Serial.println("INVALID STATE");
      return;
    }

    // handle all pin change
    if (tokens[1][0] == 'A') {
      for (int p=0; p < MAX_PINS; p++) {
        digitalWrite(led_pins[p], state);
      }
      Serial.print("LED ");
      dump_byte(LED_BYTE);
      Serial.println(" OK");
      return;
    }

    // handle single pin change
    int pin = atoi(tokens[1]);
    if (pin < 1 || pin > MAX_PINS) {
      Serial.println("INVALID PIN");
      return;
    }

    digitalWrite(led_pins[pin-1], state);
    Serial.print("LED ");
    dump_byte(LED_BYTE);
    Serial.println(" OK");

    return;
  }

  Serial.println("ERROR");
}

void handleLine() {
  // Commands:
  //
  // LED 1 1   Turn on 1 LED  (does not change state of others)
  // LED 1 0   Turn off 1 LED (does not change state of others)
  // BLINK [A,1,2,3,4] ON Blink selected LED. Cleared via LED x OFF / LED x ON
  // SOLO [A,1,2,3,4] Turns off every light except the one requested (e.g. player keypress)
  //
  char* tokens[MAX_TOKENS];

  if (!newSerialData) return;

  // reset this regardless
  newSerialData = false;

  // Allocate memory for tokens
  for (int i = 0; i < MAX_TOKENS; i++) {
    tokens[i] = (char*)malloc(MAX_TOKEN_LENGTH * sizeof(char));
    *tokens[i] = 0x00;
  }

  int count = parse_string(receivedChars, tokens);
#ifdef DEBUG_TOKENS
  for(int i = 0; i < count; i++) {
      Serial.print(i);
      Serial.print(": ");
      Serial.println(tokens[i]);
   }
#endif
  handleCommand(tokens);
  // Free memory
  for (int i = 0; i < MAX_TOKENS; i++) {
    free(tokens[i]);
  }
}

void handleSwitches() {
  static unsigned long pinTime[MAX_PINS] = {0, 0, 0, 0};

  for (int i = 0; i < MAX_PINS; i++) {
      if ((digitalRead(input_pins[i]) == 0) && (pinTime[i] == 0)) {
        Serial.print("SWITCH ");
        Serial.print(i+1);
        Serial.println(" PRESSED");
        pinTime[i] = millis();
      } else if ((digitalRead(input_pins[i]) == 1) && (pinTime[i] > 0)) {
          Serial.print("SWITCH ");
          Serial.print(i+1);
          Serial.print(" RELEASED (down ");
          Serial.print(millis() - pinTime[i]);
          Serial.println(" mS)");
          pinTime[i]=0;
      }
    }
}

/** Port B Interrupt Handler**/
ISR(PCINT0_vect) {
  static unsigned long last_interrupt_time = 0;

  unsigned long interrupt_time = millis();
//  noInterrupts();

  // If interrupts come faster than 100ms, assume it's a bounce and ignore

  // there are some approaches here, e.g. if the button has been down for a long enough time it's a valid push.
  // if it's down for too long, it can be ignored (press and hold should not break the game)
  //if ((interrupt_time - last_interrupt_time > 100) || (last_interrupt_time = 0)) {
     buttonsNeedHandling = true;
  //}
  last_interrupt_time = interrupt_time;
//  interrupts();
}

void loop() {
  recvLine();
  handleLine();
  if (buttonsNeedHandling) {
    buttonsNeedHandling = false;
    handleSwitches();
  }
};
