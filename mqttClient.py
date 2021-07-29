import paho.mqtt.client as mqtt #import the client1
import time
import datetime

replace_values = {"{": "", "}": "\n",",":"\n"}

def on_message(client, userdata, message):
    print(str(message.topic)+"\n"+ str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"\n"+multiple_replace(str(message.payload.decode("utf-8")), replace_values))
    text_file = open("/home/pi/webcam/telegramBot/alarmLogger.txt", "w")
    text_file.write(str(message.topic)+"\n"+ str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"\n"+multiple_replace(str(message.payload.decode("utf-8")), replace_values))
    text_file.close()

def multiple_replace(target_str, replace_values):

    for i, j in replace_values.items():
        target_str = target_str.replace(i, j)
    return target_str

broker_address="localhost"
#print("creating new instance")
client = mqtt.Client("PI") #create new instance
#print("connecting to broker")
client.connect(broker_address) #connect to broker
#print("Subscribing to topic","greenst/water_pump")
client.subscribe("greenst/water_pump")
client.subscribe("greenst/toilet")
client.subscribe("greenst/house")
while True:
 client.loop_start()
 client.on_message=on_message
