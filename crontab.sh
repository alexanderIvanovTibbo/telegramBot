#!/bin/bash
for(( i=0; i <= 5; i++ ))
do
   if ping -c 1 ya.ru &> /dev/null
   then
      echo "Host found"
      break
   else
	if [[ $i == 2 ]]
	then
	    echo "Reconnect"
        sh /home/pi/webcam/usb0/scriptFolder/mainScript/telebotMqtt/modem3g.sh stop
	    sh /home/pi/webcam/usb0/scriptFolder/mainScript/telebotMqtt/modem3g.sh start
	    sleep 5
	fi

	if [[ $i == 5 ]]
	then
#	    echo "reboot"
	    reboot
	fi
   fi
done

if [ $(pgrep -c -f tinyHouseBot.py) == 0 ]
then
   sleep 1
   python /home/pi/webcam/usb0/scriptFolder/mainScript/telebotMqtt/tinyHouseBot.py
  exit 1
else
   echo "Exit! Python bot is already running!"
  exit 1
fi

