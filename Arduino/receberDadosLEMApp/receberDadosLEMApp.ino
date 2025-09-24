#include "WiFi.h"

const char *ssid     = "ESP32_Server";
const char *password = "123456789";
const char *host     = "192.168.4.1"; 
const uint8_t port   =  80;

//struct sensorData { float AngleRoll,AnglePitch,kalmanAngleRoll,kalmanAnglePitch,deslocamento; };
struct sensorData { float AngleRoll, deslocamento; };

WiFiClient client;


void setup() 
{
  Serial.begin(115200);
  pinMode(2, OUTPUT);
  conectarServidor();
}

void loop() 
{
  receberDados();
}


void conectarServidor()
{
  WiFi.begin(ssid, password);
  Serial.println("Conectando ao Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) 
  {
      delay(1000);
      Serial.print(".");
  }
  Serial.println("Conectado ao Wi-Fi");
}

void receberDados()
{
  if (client.connect(host, port)) 
  { 
    while (client.available() < sizeof(sensorData)){}
    
    sensorData dadosRecebidos;
    client.read((uint8_t*)&dadosRecebidos, sizeof(dadosRecebidos));
 
//    Serial.printf("%f, %f, %f, %f, %f, %d \n",
//                   dadosRecebidos.AngleRoll,
//                   dadosRecebidos.AnglePitch,
//                   dadosRecebidos.kalmanAngleRoll,
//                   dadosRecebidos.kalmanAnglePitch,
//                   dadosRecebidos.deslocamento,
//                   millis());
    Serial.printf("%f, %f, %d \n",
                   dadosRecebidos.AngleRoll,
                   dadosRecebidos.deslocamento,
                   millis());
    digitalWrite(2, HIGH);
  }
  else
  { 
    digitalWrite(2, LOW);
    Serial.println("Falha na conexão com o servidor");
    delay(100);
  }  
}
