# eBilal

This project turns a Raspberry Pi into an alternative to Radio Bilal. Once setup, it will play your selected live audio streams from livemasjid.com.

## Roll your own instructions

1. Install latest [Raspbian Lite](https://downloads.raspberrypi.org/raspbian_lite_latest)
2. Setup [Wifi and SSH](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md)
3. Boot and SSH
4. `sudo apt install git python3 python3-pip ffmpeg ssh-client`
5. `cd /opt/`
6. `sudo git clone https://bitbucket.org/mitpeople/ebilal.git`
7. `sudo chown -R pi:pi ebilal`
8. `cd ebilal`
9. `pip3 install -r requirements.txt`
10. `sudo cp other/*.service /lib/systemd/system/`
11. `sudo chmod 644 /lib/systemd/system/ebilal*`
12. `sudo systemctl daemon-reload`
13. `sudo systemctl enable ebilal.service`
14. `sudo systemctl enable ebilal_api.service`
15. Modify settings.json to set streams to listen to (pick from livemasjid.com using the last word in the stream URL)
16. `sudo reboot`

To check status:
`sudo systemctl status ebilal.service`

## API
Try the new API here:
http://ebilal.local:8000/docs


## Optional

If you're using the [pimoroni](https://shop.pimoroni.com/products/pirate-radio-pi-zero-w-project-kit):
`curl https://get.pimoroni.com/phatbeat | bash`

## Docker
Experimental: A docker image has been setup, usage:
docker run mitpeople/ebilal:latest <mountname> --device /dev/snd 
