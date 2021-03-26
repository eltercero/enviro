# Enviro+ 

This is just my script to upload data from my [Enviro+](https://shop.pimoroni.com/products/enviro-plus) to several [IO Adafruit](https://io.adafruit.com/) feeds.

You may need to install Python3 and all the usual libraries from Enviro+. I'd do this easier for you but I honestly don't have much idea of Python yet. So... yeah, sorry about that.

## IO Adafruit config

It is expected that you have two ENV variables for your IO Adafruit settings. You can add them in your .bashrc or zshrc or whatever: 

```bash
export IO_USERNAME=""
export IO_KEY=""
```

## Run as a service

If you want to run this as a service in your Raspberry PI you can add a `enviro.service` file in `/lib/systemd/system/` with this:

```
[Unit]
Description=Enviro monitoring to adafruit io
After=multi-user.target

[Service]
WorkingDirectory=/home/pi/code/enviro
Type=simple
ExecStart=/usr/bin/python3 /home/pi/code/enviro/main.py
Restart=on-abort
User=pi
Environment="IO_USERNAME="
Environment="IO_KEY="

[Install]
WantedBy=multi-user.target
```

In the Enviroment parts you need to add your Adafruit IO username and key. Also, change `/home/pi/code/enviro/main.py` for wherever you clone this repo.

You will need to reload the daemons and enable the service with:

```bash
sudo systemctl daemon-reload
sudo systemctl enable enviro.service
```

And then stop or start the service with:

```bash
sudo systemctl start enviro.service
sudo systemctl stop enviro.service
```

## Default values

This will upload temperature, humidity, oxidising, reducing, and nh3 values. You may need to tweak the code if you want to add or remove one of those.
