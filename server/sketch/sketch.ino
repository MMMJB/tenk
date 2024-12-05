const int buttonPins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11};
const unsigned long debounceDelay = 50;
 
int buttonStates[] = {HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};
unsigned long lastDebounceTimes[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

void setup() {
  Serial.begin(9600);
 
  for (const int &pin : buttonPins) {
    pinMode(pin, INPUT_PULLUP);
  }
}

void loop() {
  int index = 0;
 
  for (const int &pin : buttonPins ) {
    int newButtonState = digitalRead(pin);
    int currentButtonState = buttonStates[index];
   
    if ((millis() - lastDebounceTimes[index]) > debounceDelay) {                
      if (newButtonState != currentButtonState) {
        buttonStates[index] = newButtonState;

        if (newButtonState == HIGH) {
          Serial.println(String(index + 1) + "r");
        } else {
          Serial.println(String(index + 1) + "p");
        }
      }
    }
   
    if (newButtonState != currentButtonState) {
      lastDebounceTimes[index] = millis();
    }
   
    index++;
  }
}
