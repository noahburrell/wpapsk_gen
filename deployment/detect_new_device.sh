#!/bin/sh
# script to detect new dhcp lease
# this will be called by dnsmasq everytime a new device is connected
# with the following arguments
# $1 = add | old
# $2 = mac address
# $3 = ip address
# $4 = device name
if logread | tail -n50 | grep "$2 WPA: pairwise key handshake completed"; then
        if grep -q $2 /etc/hostapd.wpa_psk; then
                exit
        fi
        if grep -q "00:00:00:00:00:00" /etc/hostapd.wpa_psk; then
                psk=$(grep '00:00:00:00:00:00' /etc/hostapd.wpa_psk | sed 's/[^ ]* //');
                echo "$psk" >> /etc/test.log
                sed -i "s/00:00:00:00:00:00/$2/g" "/etc/hostapd.wpa_psk"
                pgrep hostapd | xargs kill -1
                python /etc/notifier/main.py "$psk" "$2"

        fi
fi
