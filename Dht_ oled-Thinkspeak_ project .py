from machine import Pin, I2C
import network
import wifi_credentials
import urequests 
import dht 
import time 
import ssd1306

ssid = "wifi name"
password = "wifi password"

# Create objects:
led = Pin(18, Pin.OUT) 
d = dht.DHT22(Pin(15))
i2c = I2C(scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Configure the ESP32 wifi as STAtion
sta = network.WLAN(network.STA_IF)
if not sta.isconnected(): 
  print('connecting to network...') 
  sta.active(True) 
  sta.connect(wifi_credentials.ssid, wifi_credentials.password) 
  while not sta.isconnected(): 
    pass 
print('network config:', sta.ifconfig()) 


# Constants and variables:
HTTP_HEADERS = {'Content-Type': 'application/json'} 
THINGSPEAK_WRITE_API_KEY = 'enter your api from thing speak' 
UPDATE_TIME_INTERVAL = 15000  # in ms 
last_update = time.ticks_ms() 

# Main loop:
while True: 
    if time.ticks_ms() - last_update >= UPDATE_TIME_INTERVAL: 
        d.measure() 
        t = d.temperature() 
        h = d.humidity() 
        
        # Show DHT data on OLED display:
        oled.fill(0)
        oled.text("Temp: {} C".format(t), 3, 10)
        oled.text("Hum: {} %".format(h), 3, 45)
        oled.show()
        oled.invert(1)
         
        dht_readings = {'field1':t, 'field2':h} 
        request = urequests.post( 
          'http://api.thingspeak.com/update?api_key=' +
          THINGSPEAK_WRITE_API_KEY, 
          json = dht_readings, 
          headers = HTTP_HEADERS )  
        request.close() 
        print(dht_readings) 
         
        led.value(not led.value()) 
        last_update = time.ticks_ms()

