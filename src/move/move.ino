#include <AccelStepper.h>

#define X_STEP_PIN A0
#define X_DIR_PIN A1
#define X_ENABLE_PIN 38

#define Y_STEP_PIN 46
#define Y_DIR_PIN 48
#define Y_ENABLE_PIN A8

#define Z_STEP_PIN A6
#define Z_DIR_PIN A7
#define Z_ENABLE_PIN A2

#define X_MIN 3
#define Y_MIN 18
#define Z_MIN 14

double diametro_cm = 5;
double perimetro = PI * diametro_cm;
int steps_por_vuelta = 6400;
double cm_a_steps = steps_por_vuelta / perimetro;


AccelStepper motorX(1, X_STEP_PIN, X_DIR_PIN);
AccelStepper motorY(1, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper motorZ(1, Z_STEP_PIN, Z_DIR_PIN);

int numberOfSteps = 400;
byte ledPin = 13;
int pulseWidthMicros = 20;    // microseconds
int millisbetweenSteps = 20;  // milliseconds - or try 1000 for slower steps

int vueltas = 4;
int steps = 200;
int microsteps = 32;

// Global variables
double x_total_cm = 100;
double z_total_cm = 200;
double y_total_cm = 220;

double current_x = x_total_cm/2;
double current_y = 0;
double current_z = z_total_cm/3;

// Valores de inicio
double largo_motor_1 = 83.33;
double largo_motor_2 = 83.33;
double largo_motor_3 = 133.33;

void update_steps(double x, double y, double z) {
  double largo_motor_1_viejo = largo_motor_1;
  double largo_motor_2_viejo = largo_motor_2;
  double largo_motor_3_viejo = largo_motor_3;

  Serial.println("Largo_motor");
  Serial.println(largo_motor_1);
  Serial.println(largo_motor_2);
  Serial.println(largo_motor_3);

  largo_motor_1 = sqrt(pow(x, 2) + pow(y, 2) + pow(z, 2));
  largo_motor_2 = sqrt(pow(x_total_cm - x, 2) + pow(y, 2) + pow(z, 2));
  largo_motor_3 = sqrt(pow(x_total_cm/2 - x, 2) + pow(y, 2) + pow(z_total_cm - z, 2));

  double diferencia_motor_1 = largo_motor_1 - largo_motor_1_viejo;
  double diferencia_motor_2 = largo_motor_2 - largo_motor_2_viejo;
  double diferencia_motor_3 = largo_motor_3 - largo_motor_3_viejo;

  int steps_motor_1 = int(cm_a_steps * diferencia_motor_1);
  int steps_motor_2 = int(cm_a_steps * diferencia_motor_2);
  int steps_motor_3 = int(cm_a_steps * diferencia_motor_3);

  motorZ.move(steps_motor_1);
  motorY.move(steps_motor_2);
  motorX.move(steps_motor_3);

  current_x = x;
  current_y = y;
  current_z = z;

}

double movement_length = 10.;

void handle_serial_command(char command) {
  switch (command) {
    case 'Y': // Motor X Up
      motorX.move(cm_a_steps*1);
      break;
    case 'H': // Motor X Down
      motorX.move(cm_a_steps*-1);
      break;
    case 'U': // Motor Y Up
      motorY.move(cm_a_steps*1);
      break;
    case 'J': // Motor Y Down
      motorY.move(cm_a_steps*-1);
      break;
    case 'I': // Motor Z Up
      motorZ.move(cm_a_steps*1);
      break;
    case 'K': // Motor Z Down
      motorZ.move(cm_a_steps*-1);
      break;

    case 'Q': // Up
      update_steps(current_x, current_y, current_z + movement_length);
      break;
    case 'A': // Down
      update_steps(current_x, current_y, current_z - movement_length);
      break;
    case 'W': // Front
      update_steps(current_x, current_y + movement_length, current_z);
      break;
    case 'S': // Back
      update_steps(current_x, current_y - movement_length, current_z);
      break;
    case 'E': // Right
      update_steps(current_x + movement_length, current_y, current_z);
      break;
    case 'D': // Left
      update_steps(current_x - movement_length, current_y, current_z);
      break;
    default:
      Serial.println("Invalid command");
  }
}

void setup() {

  Serial.begin(9600);
  Serial.println("Starting StepperTest");
  digitalWrite(ledPin, LOW);

  pinMode(X_MIN, INPUT);
  pinMode(Y_MIN, INPUT);
  pinMode(Z_MIN, INPUT);

  pinMode(Y_STEP_PIN, OUTPUT);
  pinMode(Y_DIR_PIN, OUTPUT);
  pinMode(Y_ENABLE_PIN, OUTPUT);

  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(X_ENABLE_PIN, OUTPUT);

  pinMode(Z_STEP_PIN, OUTPUT);
  pinMode(Z_DIR_PIN, OUTPUT);
  pinMode(Z_ENABLE_PIN, OUTPUT);

  pinMode(ledPin, OUTPUT);

  int speed = int(steps * microsteps * 2);
  motorY.setMaxSpeed(speed * 2);
  motorY.setSpeed(speed);
  motorY.setAcceleration(speed * 4);

  motorX.setMaxSpeed(speed * 2);
  motorX.setSpeed(speed);
  motorX.setAcceleration(speed * 4);

  motorZ.setMaxSpeed(speed * 2);
  motorZ.setSpeed(speed);
  motorZ.setAcceleration(speed * 4);

}

void loop() {
  motorX.run();
  motorY.run();
  motorZ.run();


  if (Serial.available()) {
    char command = Serial.read();
    handle_serial_command(command);
  }
}
