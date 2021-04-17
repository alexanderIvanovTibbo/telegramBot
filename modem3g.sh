#!/bin/sh
case "$1" in
  start)
#    sleep 10
    echo "connecting via sakis3g"
    # run application you want to start
    /home/pi/sakis3g --console --pppd APN="internet.mc" USBINTERFACE="0" USBDRIVER="option" USBMODEM="12d1:1001" OTHER="USBMODEM" MODEM="OTHER" --sudo "connect"
#    echo $?
    ;;
  stop)
    echo "disconnecting via sakis3g"
    # kill application you want to stop
    /home/pi/sakis3g --console --pppd APN="internet.mc" USBINTERFACE="0" USBDRIVER="option" USBMODEM="12d1:1001" OTHER="USBMODEM" MODEM="OTHER" --sudo "disconnect"
    ;;
  *)
    echo "Usage: /var/opt/modem3g.sh {start|stop}"
    exit 1
    ;;
esac

exit 0
