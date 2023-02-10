# Disable USB ports to save energy
echo '1-1' | sudo tee /sys/bus/usb/drivers/usb/unbind
cd /home/pi/FasiBoi
python3 main.py &>/dev/null &
