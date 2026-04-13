#!/bin/bash

set -e  # Exit on any error

VIDEO_DEVICE="10"
DEVICE_PATH="/dev/video${VIDEO_DEVICE}"
CARD_LABEL="PhoneCam"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
echo "Checking permissions..."
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (use sudo)"
    exit 1
fi
echo "Running as root"
echo ""

# Unload v4l2loopback module if it's already loaded
echo "Cleaning up existing module..."
if lsmod | grep -q "v4l2loopback"; then
    echo "v4l2loopback is already loaded, unloading..."
    
    # Kill any processes using the device
    if [ -e "${DEVICE_PATH}" ]; then
        PIDS=$(fuser "${DEVICE_PATH}" 2>/dev/null || true)
        if [ -n "$PIDS" ]; then
            echo "Killing processes using ${DEVICE_PATH}: $PIDS"
            kill -9 $PIDS 2>/dev/null || true
            sleep 1
        fi
    fi
    
    # Unload the module
    rmmod v4l2loopback || true
    sleep 1
    echo "Module unloaded"
else
    echo "v4l2loopback not loaded (clean start)"
fi
echo ""

# Load v4l2loopback module
echo "Loading v4l2loopback module..."
if ! modprobe v4l2loopback devices=1 video_nr=${VIDEO_DEVICE} card_label="${CARD_LABEL}" exclusive_caps=1; then
    echo "Failed to load v4l2loopback module"
    echo "Troubleshooting tips:"
    echo "  - Make sure v4l2loopback is installed: sudo apt install v4l2loopback-dkms"
    echo "  - On Fedora: sudo dnf install v4l2loopback akmod-v4l2loopback && sudo akmods --force"
    exit 1
fi
sleep 1
echo "v4l2loopback module loaded"
echo ""

# Verify the device was created
echo "Verifying device creation..."
if [ ! -e "${DEVICE_PATH}" ]; then
    for i in {1..5}; do
        sleep 1
        if [ -e "${DEVICE_PATH}" ]; then
            break
        fi
        if [ $i -eq 5 ]; then
            echo "Device ${DEVICE_PATH} was not created!"
            echo "Available video devices:"
            ls -l /dev/video* 2>/dev/null || echo "  No video devices found"
            exit 1
        fi
        echo "Device not found yet, retrying... ($i/5)"
    done
fi
echo "Device created: ${DEVICE_PATH}"
echo ""

echo "Device information..."
ls -l "${DEVICE_PATH}"
v4l2-ctl --device="${DEVICE_PATH}" --info 2>/dev/null || echo "v4l2-ctl not available (optional)"
echo ""

echo -e "${GREEN}✓ Virtual camera setup complete!${NC}"
