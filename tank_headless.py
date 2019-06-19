##!/usr/bin/env python2
#Libraries
import RPi.GPIO as GPIO
import time
import datetime 
import mysql.connector
import random
import os
import logging

os.system("sudo service mysql start")

time.sleep(1)

db = mysql.connector.connect(
  host="localhost",
  user="tank",
  passwd="password",
  database="Home"
)

cursor = db.cursor()

print("Started")

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
def distance():
    #print("calculating distance")
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
    
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    
    return distance
    #return random.randint(180,200)

tankDepthFull = 200

sensorHeightAboveMaxWL = 20

tankWidth = 2
tankHeight = 1.2

logging.basicConfig(filename='log.txt',filemode = 'w',format='%(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.info('Running')

def validation(depth, last_depth):
	if abs(depth - last_depth) < 0.2:
		return 1
	else:
		return 0


last_depth = sensorHeightAboveMaxWL+tankDepthFull-distance()

if __name__ == '__main__':
    try:
        while True:
            rawSensor = distance()
	    depth = sensorHeightAboveMaxWL+tankDepthFull-rawSensor
	    logging.debug("Calculated depth = %.1f cm" % depth)
	    #depth = rawSensor 

            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            #print ("Calculated Depth = %.1f cm" % depth)
	    percent = float(depth)/float(tankDepthFull)*100
	    #print(percent)
	    volumeremaining = float((float(depth)/100))*float((float(tankWidth)))*float((float(tankHeight)))*1000
	    #print(float(depth))    
            #print(float(tankWidth))        
            #print(float(tankHeight))
 	    #print(volumeremaining)
            #print((depth/100)*(tankWidth/100))
	    validated = validation(depth, last_depth)
            sql = "INSERT INTO TankDepths (Timestamp, Depth, Validated, PercentFull,VolumeRemaining) VALUES (%s, %s, %s, %s, %s)"
            val = (timestamp, depth, validated, percent, volumeremaining)
	    cursor.execute(sql, val)
	    last_depth = depth

	    db.commit()
            time.sleep(10)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        #print("Measurement stopped by User")
        GPIO.clear()
