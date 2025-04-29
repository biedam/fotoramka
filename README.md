## Installation

1. Install latest Raspberry pi OS (lite version) preferably using Raspberry Pi imager
2. Connect via SSH, run sudo raspi-config and setup following options:
   - System/autologin - as desktop user - usefull for debugging and connecting remotely
   - Advanced/expand filesystem
3. Install RPi Connect https://www.raspberrypi.com/documentation/services/connect.html
4. Setup RPi to use EPD screen https://www.waveshare.com/wiki/13.3inch_e-Paper_HAT+_(E)_Manual#Raspberry_Pi
5. Install needed packages:
   ```shell
   sudo apt install imagemagick
   ```
6. Optionally for better stability with remote VSCode server increase SWAP size:
   - Stop the swap service `sudo dphys-swapfile swapoff`
   - Edit the configuration filr `sudo nano /etc/dphys-swapfile`
   - Change the swap size `CONF_SWAPSIZE=1024`
   - Reinitialize the swap file `sudo dphys-swapfile setup`
   - Start the swap service `sudo dphys-swapfile swapon`
   - Reboot