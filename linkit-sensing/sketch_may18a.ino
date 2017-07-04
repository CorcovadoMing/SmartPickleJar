#include <Wire.h>
#include <SHT2x.h>
//#include <CO2Sensor.h>
#include <Adafruit_BMP085.h>
#include <Bridge.h>

//CO2Sensor co2Sensor(A5, 0.99, 100);
Adafruit_BMP085 bmp;

void setup()
{
  Wire.begin();
  Serial.begin(9600);
  Bridge.begin();
  //co2Sensor.calibrate();
  if (!bmp.begin()) {
    Serial.println("Could not find a valid BMP085 sensor, check wiring!");
    while (1) {}
  }
}

void loop()
{
  float Humidity = SHT2x.GetHumidity();
  float Temperature = SHT2x.GetTemperature();
  float Temperature_2 = bmp.readTemperature();
  float Pressure = bmp.readPressure();
  //float Co2 = co2Sensor.read();

  Bridge.put("Humidity", String(Humidity));
  Bridge.put("Temperature", String(Temperature));
  Bridge.put("Temperature_2", String(Temperature_2));
  Bridge.put("Pressure", String(Pressure));
  //Bridge.put("Co2", String(Co2));

  delay(5000);
}
