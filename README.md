Teleram Bot with MQTT BROKER

Package install site:
1. Automiunt USB/HHD device - https://geekelectronics.org/raspberry-pi/raspberry-pi-podklyuchenie-usb-hdd.html
	Config /etc/fstab
HDD	#UUID=DEB8-D981 /home/pi/webcam/usb0 vfat defaults,rw 0 1
USB	#UUID=0251-17A8 /home/pi/webcam/usb0 vfat defaults, auto, users, rw, nofail, noatime 0 0

2. W3m browser - sudo apt-get install w3m

3. Install fswebcam - sudo apt install fswebcam

4. Install FFmpeg - sudo install ffmpeg 

5. Install python - sudo apt install python3-pip
Do for instruction https://linuxconfig.org/how-to-change-default-python-version-on-debian-9-stretch-linux
Change to python3.5
5.1 Install python library:
	pip3 install python-telegram-bot
	sudo pip3 install datetime
	sudo pip3 install path.py
	sudo pip3 install subprocess.run
	sudo pip3 install ffmpeg
	sudo pip3 install psutil
	sudo pip3 install glob2
	sudo pip3 install paho-mqtt

6. Install libssl - wget http://security.debian.org/debian-security/pool/updates/main/o/openssl/libssl1.0.0_1.0.1t-1+deb8u12_armhf.deb
	dpkg -i libssl1.0.0_1.0.1t-1+deb8u12_armhf.deb

7. Install mosquitto - https://robot-on.ru/articles/ystanovka-mqtt-brokera-mosquitto-raspberry-orange-pi
	Config - /etc/mosquitto/conf.d/default.conf
		allow_anonymous true
		password_file /etc/mosquitto/passwd
	Create user: mqttStoked - GreenSt1024
        To check signal - mosquitto_sub -d -t outTopic
8. Install Hostapd - https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md
	hostapd logs - sudo hostapd -dd /etc/hostapd/hostapd.conf

	Config: /etc/hostapd/hostapd.conf 

country_code=RU
interface=wlan0
#driver=rtl871xdrv
ssid=GreenSt
hw_mode=g
ieee80211d=1
ieee80211n=1
channel=7
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=Stoked1024
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP

9. Connect 3g modem:
	apt-get install usb-modeswitch minicom ppp
	reboot
	mkdir ~/3g
	cd 3g/
	wget http://sourceforge.net/projects/vim-n4n0/files/sakis3g.tar.gz
    tar -xzvf sakis3g.tar.gz
    sudo chmod +x sakis3g
    
10. rtl8188eus driver install
	sudo apt purge firmware-realtek
	wget http://downloads.fars-robotics.net/wifi-drivers/8188eu-drivers/$(uname -r).tar.gz
	tar -xzvf $(uname -r).tar.gz
	chmod a+x install.sh
	./install.sh

11.Zigbee2MQTT
https://www.zigbee2mqtt.io/getting_started/running_zigbee2mqtt.html