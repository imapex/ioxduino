/*
 BasicButtonSerial Example 

 When a button is pressed, it writes a notice out the serial port.  
 
 This is created as part of a Demonstration/POC illustrating how 
 Cisco IOx could be integrated with external sensors to easily provide 
 Fog Computing and IOT uses cases.  

 */

// Constants
const int buttonPin = 6;     // the number of the pushbutton pin
const int ledPin =  8;      // the number of the LED pin

// Variables to hold details for serial alerts sent
String outputString = "";         // a string to hold incoming data
boolean alertComplete = false;  // whether the string is complete

// Variables related to Button State
int buttonState = 0;         // variable for reading the pushbutton status
int ledState = LOW;         // the current state of the output pin
int lastButtonState = LOW;   // the previous reading from the input pin
long lastDebounceTime = 0;  // the last time the output pin was toggled
long debounceDelay = 50;    // the debounce time; increase if the output flickers


void setup() {
  // initialize serial:
  Serial.begin(9600);
  // reserve 200 bytes for the outputString:
  outputString.reserve(200);
  // initialize the pushbutton pin as an input:
  pinMode(buttonPin, INPUT);
  // initialize the LED pin as an output:
  pinMode(ledPin, OUTPUT);

  // set initial LED state
  digitalWrite(ledPin, ledState);
}

void loop() {
  //  Check the button/sensor
  btn_check();
  
  // Write out alert if one exists.  
  if (alertComplete) {
    Serial.println(outputString);
    // clear the string:
    outputString = "";
    alertComplete = false;
  }
}

/* 
 *  This function checks for the button to be pressed
 *  and updates an alert message if done
 */
void btn_check() {
  // read the state of the switch into a local variable:
  int reading = digitalRead(buttonPin);

  // check to see if you just pressed the button
  // (i.e. the input went from LOW to HIGH),  and you've waited
  // long enough since the last press to ignore any noise:

  // If the switch changed, due to noise or pressing:
  if (reading != lastButtonState) {
    // reset the debouncing timer
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    // whatever the reading is at, it's been there for longer
    // than the debounce delay, so take it as the actual current state:

    // if the button state has changed:
    if (reading != buttonState) {
      buttonState = reading;

      // only toggle the LED if the new button state is HIGH
      if (buttonState == HIGH) {
        ledState = !ledState;
        outputString = String("Button ") + buttonPin + String(" pressed.");      
        alertComplete = true;
      }
    }
  }

  // set the LED:
  digitalWrite(ledPin, ledState);

  // save the reading.  Next time through the loop,
  // it'll be the lastButtonState:
  lastButtonState = reading;
  
}


// This currently not used, left for potential later when reading data in
/*
  SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */
//void serialEvent() {
//  while (Serial.available()) {
//    // get the new byte:
//    char inChar = (char)Serial.read();
//    // add it to the outputString:
//    outputString += inChar;
//    // if the incoming character is a newline, set a flag
//    // so the main loop can do something about it:
//    if (inChar == '\n') {
//      alertComplete = true;
//    }
//  }
//}


