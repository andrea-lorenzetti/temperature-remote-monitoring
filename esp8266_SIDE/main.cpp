#include <Arduino.h>
#include <ESP8266WiFi.h>        // Include the Wi-Fi library
#include <OneWire.h> 
#include <DallasTemperature.h>
#include "time.h"

#define ONE_WIRE_BUS 2
#define PERIOD 240000
#define TO_HOUR 17
#define FROM_HOUR 10

//WIFI AND SOCKET VARIABLES
const char* ssid     = "**hotspot_name**";         // The SSID (name) of the Wi-Fi network you want to connect to
const char* password = "**psw_hotspot**";     // The password of the Wi-Fi network
const char* server = "**server_name**"; 
int port = 0;/*load_data socket bind port*/
WiFiClient client;

//SENSOR VARIABLES
OneWire oneWire(ONE_WIRE_BUS); 
DallasTemperature sensors(&oneWire);


//ntp variables
const char* ntpServer = "it.pool.ntp.org";
const long  gmtOffset_sec = 3600;   //Replace with your GMT offset (seconds)
const int   daylightOffset_sec = 0;  //Replace with your daylight offset (seconds)

//other variables
String strTemp;
bool hotspot=0,sock=0;

//get current time
int getLocalTime(){
  time_t rawtime;
  struct tm * timeinfo;
  time (&rawtime);
  timeinfo = localtime (&rawtime);
  return timeinfo->tm_hour;
}

//connection manager
void connection(){
 WiFi.begin(ssid, password);             // Connect to the network
  Serial.print("Connecting to ");
  Serial.print(ssid);

  while (WiFi.status() != WL_CONNECTED) { // Wait for the Wi-Fi to connect
    delay(500);
    Serial.print('.');
  }
  Serial.println("Connection established!");  
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP());         // Send the IP address of the ESP8266 to the computer
  hotspot=1;
  Serial.println("connection to socket..");
  while(!client.connected()){
    if(client.connect(server,port)){
      Serial.println("connected to the socket !");
      sock=1;
    } 
    else{
        Serial.println(" NOT connected to the socket !");  
    }
    delay(1000);
  }
}
/////******************////////////
void setup() {
  Serial.begin(115200);         // Start the Serial communication to send messages to the computer
  delay(10);
  Serial.println('\n');
  while(getLocalTime()>FROM_HOUR && getLocalTime()<TO_HOUR ){ //DONT SEND ANY DATA FROM 9:00 TO 18:00
    delay(3000);
    Serial.println("waiting...");
  }
  connection();
  delay(2000);
  //clock(hour) setup
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  getLocalTime(); //first read to eliminate first useless date

  //SENAOR START
  sensors.begin();
  delay(20000);//SENSOR CALIBRATION

}


void loop() { 
  while(getLocalTime()>FROM_HOUR && getLocalTime()<TO_HOUR ){ //DONT SEND ANY DATA FROM 9:00 TO 18:00
    delay(3000);
    Serial.println("waiting...");
  }
  if(WiFi.status()==WL_CONNECTED){
    Serial.println("connected to hotspot");
    if(client.connected()){
      Serial.println("connection still alive, sending data");
      //TEMPERATURE ACQUISITION
      Serial.print(" Requesting temperatures..."); 
      sensors.requestTemperatures(); // Send the command to get temperature readings 
      Serial.println("DONE");
      strTemp=String(sensors.getTempCByIndex(0),2);
      Serial.print("temperature in string="); Serial.println(strTemp);
      if(client.print(strTemp)<=0){
        Serial.println("data not send-server problem");
        sock=0;
      }
    }
    else{
      Serial.println("connection to socket dead...exiting...");
      sock=0;      
    }
  }
  else{
    
    Serial.println("NOT connected to hotspot...EXITING");
    hotspot=0;
  }
  if(!sock || !hotspot){
    WiFi.disconnect();
    client.stop();
    Serial.println("reconnection: ");
    connection();
  }

  delay(PERIOD);//CHANGE FOR TESTS
}
