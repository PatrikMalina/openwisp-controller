#!/bin/bash

SSID="LabCapture"
PASSWORD="labcapture1"
INTERFACE="wlan0"
OUTPUT_DIR="./output"
FILENAME="capture_$(date +%Y%m%d_%H%M%S).pcap"

mkdir -p $OUTPUT_DIR

echo "Attempting to connect to Wi-Fi: $SSID"

# Retry until connected
until nmcli -t -f WIFI g | grep -q "enabled" && nmcli dev wifi connect "$SSID" password "$PASSWORD" ifname "$INTERFACE"; do
    echo "Connection failed. Retrying in 5 seconds..."
    sleep 5
done

echo "Connected to $SSID. Waiting for IP..."
sleep 10  # Allow time for DHCP, etc.

# Capture for 1 minute
echo "Starting capture on $INTERFACE for 60 seconds..."
timeout 60 tcpdump -i $INTERFACE -w "$OUTPUT_DIR/$FILENAME" -s 0 -U

echo "Capture saved to $OUTPUT_DIR/$FILENAME"