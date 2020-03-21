import RPi.GPIO as GPIO
import time
from asterisk.ami import AMIClient
from asterisk.ami import SimpleAction

# Program variables
CallCount = 0
GPIO_PINS = [6, 5, 25, 24, 23, 22, 27, 18, 17, 4]

# Methods
def SequenceTest():
	for i in GPIO_PINS:
		GPIO.output(i,GPIO.HIGH)
		time.sleep(0.1)
		GPIO.output(i,GPIO.LOW)

def RangeTest():
	for i in range(0,len(GPIO_PINS)+1):
		OutputQueueCalls(i)
		time.sleep(0.1)
	for i in range(len(GPIO_PINS),-1,-1):
		OutputQueueCalls(i)
		time.sleep(0.1)

def AllOn():
	for i in GPIO_PINS:
		GPIO.output(i,GPIO.HIGH)

def AllOff():
	for i in GPIO_PINS:
		GPIO.output(i,GPIO.LOW)

def OutputQueueCalls(calls):
	if calls < 0: calls = 0
	if calls > len(GPIO_PINS) + 1: calls = len(GPIO_PINS) + 1
	AllOff()
	for i in range(calls):
		GPIO.output(GPIO_PINS[i],GPIO.HIGH)

def event_listener(event, **kwargs):
	print("Event: "+ event.name)

	global CallCount
	if event.name == "QueueStatusComplete":
		# Reset The Call Count
		OutputQueueCalls(CallCount)
		CallCount = 0
		return

	if event.name == "QueueEntry":
		# Increment the Call Count
		CallCount = CallCount+1
		return

# Setup
for i in GPIO_PINS:
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(i, GPIO.OUT)

# Test LED
SequenceTest()
time.sleep(0.1)
RangeTest()
time.sleep(0.1)
AllOn()
time.sleep(0.1)
AllOff()
time.sleep(0.1)
AllOn()
time.sleep(0.1)
AllOff()
time.sleep(1)

client = AMIClient(address='127.0.0.1',port=5038)
client.login('python','password')

action = SimpleAction('Events', EventMask='on')
client.send_action(action)

client.add_event_listener(event_listener, white_list=['QueueStatusComplete','QueueEntry'])

# Main Loop
while True:
	try:
		action = SimpleAction('QueueStatus', Queue='default')
		client.send_action(action)
	except Exception as e:
		print("Error setting queue calls")
		print(e)
	time.sleep(1)

# End
client.logoff()
GPIO.cleanup()