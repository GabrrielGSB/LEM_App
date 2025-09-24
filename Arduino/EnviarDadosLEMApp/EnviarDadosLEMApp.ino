#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include "WiFi.h"

#define sensorDeslocamento 33

float KalmanGain, kalmanAngleRoll, KalmanUncertaintyAngleRoll, 
      kalmanAnglePitch, KalmanUncertaintyAnglePitch, 
      RateCalibrationRoll, RateCalibrationPitch, RateCalibrationYaw,
      AceX, AceY, AceZ, Temp,
      GyrXc, GyrYc, GyrZc,
      AngleRoll, AnglePitch, 
      RateRoll, RatePitch, RateYaw;
      
bool calibration;

Adafruit_MPU6050 mpu;
WiFiServer server(80);

// Configurações da rede WiFi do servidor (AP)
const char *ssid     = "ESP32_Server";
const char *password = "123456789";

// IP e porta do servidor
const char *host   = "192.168.4.1"; // IP do servidor ESP32
const uint8_t port = 80;

struct sensorData 
{ 
//  float angleRoll,anglePitch, kalmanAngleRoll, kalmanAnglePitch, deslocamento; 
  float angleRoll, deslocamento; 
};

void setup() 
{
  Serial.begin(115200);
  pinMode(sensorDeslocamento, INPUT);

  pinMode(2, OUTPUT);
  MPUconfigSetup();
  iniciarServidor();
  CalibrarMPU();  
  setupKalman();
}

void loop() 
{
  MPUgetSignalsLoop();
  
  int analog = analogRead(sensorDeslocamento);

  // Aplica o filtro nos angulos Roll e Pitch
//  Kalman1D(kalmanAngleRoll,  KalmanUncertaintyAngleRoll,  RateRoll,  AngleRoll);  
//  Kalman1D(kalmanAnglePitch, KalmanUncertaintyAnglePitch, RatePitch, AnglePitch);

  WiFiClient client = server.available();
  if (client)                                       
  {
//      sensorData dados = {AngleRoll, AnglePitch, kalmanAngleRoll, kalmanAnglePitch, analog};
      sensorData dados = {AngleRoll, analog}; 
      digitalWrite(2, HIGH);       
      client.write((uint8_t*)&dados, sizeof(dados)); 
      // delay(100);                              
  }
  else delay(10);   
      
  delay(1);                             
}

void iniciarServidor()
{
  WiFi.softAP(ssid, password);
  Serial.print("Connecting to WiFi");

  server.begin();
  Serial.println("Server started");
  Serial.print("IP address: ");
  Serial.println(WiFi.softAPIP());
  
}

void MPUconfigSetup() 
{
  if (!mpu.begin()) 
  { 
    while (1) 
    {
      Serial.println("error");
      yield();
    }
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);//2G, 4G, 8G, 16G
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);     //250deg/s, 500deg/s, 1000deg/s, 2000deg/s
  mpu.setFilterBandwidth(MPU6050_BAND_10_HZ);  //5Hz, 10Hz, 21Hz, 44Hz, 94Hz, 184Hz, 260Hz
}

void MPUgetSignalsLoop() 
{  
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  AceX = a.acceleration.x / 9.81; // m/s^2...
  AceY = a.acceleration.y / 9.81; // ...
  AceZ = a.acceleration.z / 9.81; // ...
 
  RateRoll  = g.gyro.x * 57.3; // °/s...
  RatePitch = g.gyro.y * 57.3; // ...
  RateYaw   = g.gyro.z * 57.3; // ...
  
  Temp = temp.temperature; // °C
  
  AngleRoll  =  atan(AceY/sqrt(AceX*AceX + AceZ*AceZ))*1/(3.142/180);
  AnglePitch = -atan(AceX/sqrt(AceY*AceY + AceZ*AceZ))*1/(3.142/180);
  
  if (calibration == true){
  RateRoll  -= (RateCalibrationRoll/2000)  - 1.2;
  RatePitch -= (RateCalibrationPitch/2000) - 1.5;
  RateYaw   -= (RateCalibrationYaw/2000)   - 0;
  AceX -= 0.02;
  AceY -= 0.03;
  AceZ -= 0.13;
  }
}

void CalibrarMPU()
{
  Serial.printf("Calibrando...");
  for (int Passo = 0 ; Passo < 2000; Passo++) 
  {
    // Serial.printf("Calibrando: %d\n", Passo);

    MPUgetSignalsLoop();

    RateCalibrationRoll  += RateRoll;
    RateCalibrationPitch += RatePitch;
    RateCalibrationYaw   += RateYaw;
    delay(1);
  }
  Serial.printf("Calibrado!");
  calibration = true;
}

void setupKalman()
{
  KalmanGain = 0;
  kalmanAngleRoll  = 0, KalmanUncertaintyAngleRoll  = 2*2;
  kalmanAnglePitch = 0, KalmanUncertaintyAnglePitch = 2*2;
}

void Kalman1D(float &KalmanState, float &KalmanUncertainty, 
              const float &KalmanInput, const float &KalmanMeasurement)
{
  KalmanState       = KalmanState + 0.004*KalmanInput;
  KalmanUncertainty = KalmanUncertainty + 0.004*0.004*4*4;
  KalmanGain        = KalmanUncertainty*1/(1*KalmanUncertainty + 3*3);
  KalmanState       = KalmanState + KalmanGain*(KalmanMeasurement - KalmanState);
  KalmanUncertainty = (1 - KalmanGain)*KalmanUncertainty;
}