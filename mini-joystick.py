#!/usr/bin/env python3

import board, busio, digitalio, time
import adafruit_rfm9x 
from adc0832_joystick import * 

joy = Joystick()

spi = busio.SPI( board.SCK, MOSI=board.MOSI, MISO=board.MISO )
CS = digitalio.DigitalInOut( board.CE1 )
RESET = digitalio.DigitalInOut( board.D22 )
RADIO_FREQ_MHZ = 915.0

rfm9x = adafruit_rfm9x.RFM9x( spi, CS, RESET, RADIO_FREQ_MHZ, baudrate=1000000 )
rfm9x.tx_power = 13 #default is 13 can go up to 23dB

while True:    
    left_speed, right_speed = joy._retrieve_differential_speed() 
    message = "{:.2f}|{:.2f}".format(left_speed, right_speed)
    rfm9x.send(bytes(message, "utf-8"))
    
    packet = rfm9x.receive()