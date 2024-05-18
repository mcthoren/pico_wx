# -*- coding: utf-8 -*-
# once again thanks to Adafruit for all the boards, code, and examples. :)

import time, board, busio, adafruit_veml7700, adafruit_bme680, os, ipaddress, wifi, socketpool
from adafruit_httpserver import Server, Request, Response, POST

i2c0 = busio.I2C(board.GP15, board.GP14)
i2c1 = busio.I2C(board.GP17, board.GP16)

sens = adafruit_bme680.Adafruit_BME680_I2C(i2c0)
veml7700 = adafruit_veml7700.VEML7700(i2c1)

debug = 1
temp, hum, pres, lux, gas = (0, 0, 0, 0, 0)

if debug >= 1:
	print()
	print("Connecting to WiFi")

#  connect to your SSID
wifi.radio.connect(os.getenv('WIFI_SSID'), os.getenv('WIFI_PASSWORD'))

if debug >= 1:
	print("Connected to WiFi")

pool = socketpool.SocketPool(wifi.radio)

if debug >= 1:
	print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])
	print("My IP address is", wifi.radio.ipv4_address)
	print("starting server..")

server = Server(pool, "/static", debug = bool(debug))

try: # start web server
    server.start(host = str(wifi.radio.ipv4_address), port = 80)
except OSError: # reboot!
    time.sleep(5)
    print("restarting..")
    microcontroller.reset()

if debug >= 2:
	ipv4 = ipaddress.ip_address("9.9.9.9")

def sens_string(temp, hum, pres, lux, gas):
	sens_str = f"temp: {temp:.2f}°C, hum: {hum:.2f}%, pres: {pres:.3f} kPa, lux: {lux:.2f} lx, gas: {gas:.3f} kOhm\n"
	return sens_str

@server.route("/")
def base(request: Request):  # pylint: disable=unused-argument
    #  serve the HTML f string
    #  with content type text/html
    return Response(request, f"{sens_string(temp, hum, pres, lux, gas)}", content_type='text/html')

while True:
	temp = sens.temperature
	hum = sens.humidity
	pres = sens.pressure
	lux = veml7700.lux
	gas = sens.gas / 1000

	if debug >=1:
		print(f"temp: {temp:.2f}°C, hum: {hum:.2f}%, pres: {pres:.3f} kPa, lux: {lux:.2f} lx, gas: {gas:.3f} kOhm")

	if debug >=2:
		try:
			dt = wifi.radio.ping(ipv4)
			print(f"Ping q9: {dt * 1000} ms")
		except:
			print("ping error.")

	server.poll()
	time.sleep(1)
