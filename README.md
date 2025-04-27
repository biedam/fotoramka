## Installation

1. Install latest Raspberry pi OS (full version) preferably using Raspberry Pi imager
2. Connect via SSH, run sudo raspi-config and setup following options:
   - System/autologin - as desktop user - usefull for debugging and connecting remotely
   - Advanced/expand filesystem
   - Advanced/wayland/labwc - usefull for connecting remotely
3. Install RPi Connect https://www.raspberrypi.com/documentation/services/connect.html
4. Install Pi-Apps: 
   ```shepp
   wget -qO- https://raw.githubusercontent.com/Botspot/pi-apps/master/install | bash
   ```
