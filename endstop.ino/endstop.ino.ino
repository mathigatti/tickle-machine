#include <AccelStepper.h>

#define Y_STEP_PIN A6
#define Y_DIR_PIN A7
#define Y_ENABLE_PIN A2

#define X_STEP_PIN A0
#define X_DIR_PIN A1
#define X_ENABLE_PIN 38

#define X_MIN 3
#define Y_MIN 14

// Global variables
double x_total_cm = 47;
double largo_motor_1 = x_total_cm / 2;
double largo_motor_2 = x_total_cm / 2;
double diametro_cm = 5;
double perimetro = PI * diametro_cm;
int steps_por_vuelta = 6400;
double cm_a_steps = steps_por_vuelta / perimetro;
int steps_m1, steps_m2;
struct Vector {
  double x;
  double y;
};
Vector posiciones[] = { { -10., 10. }, { 0., 20. }, { 10, 20 }, { 0, 10 } };
int lenVector = sizeof(posiciones) / sizeof(posiciones[0]);
int idx = 0;

void calibrar_motores(AccelStepper motorX, AccelStepper motorY, int *steps_motor_1, int *steps_motor_2) {
  /* ESTE CODIGO ASUME QUE EL MOTOR X TIENE HILO DE SOBRE SIEMPRE */
  int callibrate_steps = int(10 * cm_a_steps);
  // 1.
  // Mover motorY hasta que apriete el final de carrera
  while (digitalRead(X_MIN) == HIGH) {
    motorX.move(callibrate_steps);
    motorY.move(callibrate_steps);

    while (motorX.distanceToGo() > 0 && digitalRead(X_MIN) == HIGH) {
      motorY.run();
      motorX.run();
    }
  }

  *steps_motor_1 = 0;
  *steps_motor_2 = 0;
  // 2.
  // Mover motores hasta que se apriete el final de carrera del motorX
  while (digitalRead(Y_MIN) == HIGH) {
    motorY.move(-1*callibrate_steps);
    motorX.move(-1*callibrate_steps);
    while (abs(motorY.distanceToGo()) > 0 && digitalRead(Y_MIN) == HIGH) {
      motorY.run();
      motorX.run();
      *steps_motor_2+=1;
    }
  }

}

void update_steps(double x, double y, int *steps_motor_1, int *steps_motor_2) {
  double largo_motor_1_viejo = largo_motor_1;
  double largo_motor_2_viejo = largo_motor_2;

  largo_motor_1 = sqrt(pow(x, 2) + pow(y, 2));
  largo_motor_2 = sqrt(pow(x_total_cm - x, 2) + pow(y, 2));

  double diferencia_motor_1 = largo_motor_1 - largo_motor_1_viejo;
  double diferencia_motor_2 = largo_motor_2 - largo_motor_2_viejo;

  *steps_motor_1 = int(cm_a_steps * diferencia_motor_1);
  *steps_motor_2 = int(cm_a_steps * diferencia_motor_2);
}

int x_i;
int y_i;

int numberOfSteps = 400;
byte ledPin = 13;
int pulseWidthMicros = 20;    // microseconds
int millisbetweenSteps = 20;  // milliseconds - or try 1000 for slower steps

int vueltas = 4;
int steps = 200;
int microsteps = 32;

AccelStepper motorY(1, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper motorX(1, X_STEP_PIN, X_DIR_PIN);

void setup() {

  Serial.begin(9600);
  Serial.println("Starting StepperTest");
  digitalWrite(ledPin, LOW);

  pinMode(Y_STEP_PIN, OUTPUT);
  pinMode(Y_DIR_PIN, OUTPUT);
  pinMode(Y_ENABLE_PIN, OUTPUT);

  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(X_ENABLE_PIN, OUTPUT);

  pinMode(ledPin, OUTPUT);

  int speed = int(steps * microsteps);
  motorY.setMaxSpeed(speed * 2);
  motorY.setSpeed(speed);
  motorY.setAcceleration(speed * 4);

  motorX.setMaxSpeed(speed * 2);
  motorX.setSpeed(speed);
  motorX.setAcceleration(speed * 4);

  calibrar_motores(motorX, motorY, steps_m1, steps_m2);
}

void loop() {
  /*
  int max_position = steps * microsteps * vueltas;
 // motorY.run();
  motorX.run();

  if (motorY.distanceToGo() == 0 && motorX.distanceToGo() == 0) {
    idx++;
    if(idx == lenVector) {
      idx = 0;
    }
    x_i = posiciones[idx].x;
    //  y_i = posiciones[idx].y;

    update_steps(x_i, y_i, &steps_m1, &steps_m2);

    //motorY.moveTo(steps_m1);
    motorX.moveTo(steps_m2);

    delay(4000);

  }
  */
}
