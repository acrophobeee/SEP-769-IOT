# importing pubnub libraries
from pubnub.pubnub import PubNub, SubscribeListener, SubscribeCallback, PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.exceptions import PubNubException
import pubnub
# importing libraries
import RPi.GPIO as GPIO
import time
from pigpio_dht import DHT11, DHT22
import smbus

GPIO.cleanup()

GPIO.setmode(GPIO.BCM)

control_pins = [12,16,20,21]

for pin in control_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, False)


circle = [
        [1,0,0,0],
        [1,1,0,0],
        [0,1,0,0],
        [0,1,1,0],
        [0,0,1,0],
        [0,0,1,1],
        [0,0,0,1],
        [1,0,0,1]
]

def way(rou):
        Counter = 0
        sign = 1 if rou>0 else -1
        rou=sign*rou*2 #half-step
        print("Total number of rounds is", rou)
        for i in range(rou):
                for pin in range(4):
                    GPIO.output(control_pins[pin], circle[Counter][pin])
                Counter += sign
                # reach end sequence
                if (Counter==8 or Counter==-8):
                        Counter = 0
              
                time.sleep(0.005)
                
class MLX90614():
 
    MLX90614_TA    = 0x06
    MLX90614_TOBJ1 = 0x07
 
    def __init__(self, address = 0x5a, bus = 1):
        self.address = address
        self.bus = smbus.SMBus(bus)
 
    def readValue(self, registerAddress):
        error = None
        for i in range(3):
            try:
                return self.bus.read_word_data(self.address, registerAddress)
            except IOError as e:
                error = e
                sleep(0.1)
        raise error
 
    def valueToCelcius(self, value):
        return -273.15 + (value * 0.02)
 
    def readObjectTemperature(self):
        value = self.readValue(self.MLX90614_TOBJ1)
        return self.valueToCelcius(value)
    


# Define main program code
if __name__ == '__main__' :
 m = MLX90614()
 cur_temp = m.readObjectTemperature()
 pnconf = PNConfiguration() # create pubnub_configuration_object
 pnconf.publish_key = 'pub-c-068b4ef9-a0f2-4893-a721-4df5a511da5d' # set pubnub publish_key
 pnconf.subscribe_key = 'sub-c-15a4ed18-7a55-11ec-ae36-726521e9de9f' # set pubnub subscibe_key
 pnconf.uuid = '220099' 
 pubnub = PubNub(pnconf) # create pubnub_object using pubnub_configuration_object
 channel='Xinyu_Chen_769'      # provide pubnub channel_name
 pubnub.subscribe().channels(channel).execute() # subscribe the channel (Runs in background) 


 print('connected') # print confirmation msg


 while cur_temp < 35:
       cur_temp = m.readObjectTemperature()
       time.sleep(2)
       
       data = {         
                'message': "Temp={0:0.1f}C%".format(cur_temp)
               }
       pubnub.publish().channel(channel).message(data).sync()
       print('Current Temperature is %0.2f celusis degree' %cur_temp)
 try:
       print('Temperatue reach 35 degree, start fan power!')
       data = {         
                'message': 'Temperatue reach 35 degree, start fan power!'
               }
       pubnub.publish().channel(channel).message(data).sync()
       way(2048)
       time.sleep(1)
       way(-2048)
 except:
       time.sleep(1)
            
     
 GPIO.cleanup()

# End of main program code

