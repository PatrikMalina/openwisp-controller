#!/bin/bash

SSID="DeauthTest"
PASSWORD="openwisp"
INTERFACE="wlan0"
PING_TARGET="8.8.8.8"
CHECK_INTERVAL=1

echo "Starting persistent Wi-Fi connection script for SSID: $SSID"

while true; do
    CURRENT_SSID=$(nmcli -t -f active,ssid dev wifi | grep '^yes' | cut -d: -f2)

    if [[ "$CURRENT_SSID" == "$SSID" ]]; then
        echo "$(date): Connected to $SSID — simulating traffic..."
        
        # Simulate traffic — replace or extend as needed
        ping -c 1 "$PING_TARGET" > /dev/null 2>&1
        curl -s https://google.com > /dev/null 2>&1
        
    else
        echo "$(date): Not connected to $SSID. Attempting to connect..."

        nmcli dev wifi connect "$SSID" password "$PASSWORD" ifname "$INTERFACE"

        if [[ $? -ne 0 ]]; then
            echo "$(date): Connection attempt failed. Retrying in $CHECK_INTERVAL seconds..."
        else
            echo "$(date): Successfully connected to $SSID."
        fi
    fi

    sleep "$CHECK_INTERVAL"
done
