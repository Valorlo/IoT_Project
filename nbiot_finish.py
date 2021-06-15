#這個版本是從https://makerpro.cc/2019/12/use-mtk-mt2625-nb-iot-usb-dongle-for-mqtt/ 修改而來
#因為原程式沒有適當的縮排，以至於需要修正。
#以迴圈每30秒做一次publish，並在之subscribe，由於可能MQTTlens的publish無法剛好在subcribe，
#因此做了10次的迴圈。
#如果要用在控制上，有兩種做法：(1)除了上傳之外，其他時間都在重復做subscribe，(2)後方程式一直處於
#subscribe，在收到模組的publish資料後，立刻做publish，而模組則在publish後立刻做subscribe
#需要安裝python的pyserial套件而不是serial套件

import random
import time
import serial
import sys
import serial.tools.list_ports

# global variables
TIMEOUT = 3 # seconds
DEVICE_KEY = "DKPK49AE9ZS9ZX5577"


# function for printing debug message
def debug_print(message):
	print(message)

# function for getting time as miliseconds
def millis():
	return int(time.time())

# function for delay as miliseconds
def delay(ms):
	time.sleep(float(ms/1000.0))


####################################
### NB IoT Shield Class ################
####################################
class NBIoT:
	board = "" # Shield name
	ip_address = "" # ip address
	domain_name = "" # domain name
	port_number = "" # port number
	timeout = TIMEOUT # default timeout for function and methods on this library.
	compose = ""
	response = ""
# Default Initializer
	#def __init__(self, serial_port="/dev/ttyUSB0", serial_baudrate=115200, board="BC-20"):
	def __init__(self, serial_port="COM5", serial_baudrate=9600, board="BC-20"):
		self.board = board
		ser.port = serial_port
		ser.baudrate = serial_baudrate
		ser.parity=serial.PARITY_NONE
		ser.stopbits=serial.STOPBITS_ONE
		ser.bytesize=serial.EIGHTBITS
		debug_print(self.board + " Class initialized!")

# Function for clearing compose variable
	def clear_compose(self):
		self.compose = ""

# Function for getting modem response
	def getResponse(self, desired_response):
		if (ser.isOpen() == False):
			ser.open()
		while 1:
			self.response =""
			while(ser.inWaiting()):
				self.response += ser.read(ser.inWaiting()).decode('utf-8', errors='ignore')
			if(self.response.find(desired_response) != -1):
				debug_print(self.response)
				break

# Function for sending at comamand to module
	def sendATCommOnce(self, command):
		if (ser.isOpen() == False):
			ser.open()
		self.compose = ""
		self.compose = str(command) + "\r\n"
		ser.reset_input_buffer()
		#print("send command")
		#print(command)
		ser.write(self.compose.encode())
		debug_print(self.compose)

# Function for sending at command to BC26_AT.
	def sendATComm(self, command, desired_response, timeout = None):
		if timeout is None:
			timeout = self.timeout
			self.sendATCommOnce(command)
			f_debug = False
		timer = millis()
		# print(command)
		#print(timeout)
		while 1:
			if( millis() - timer > timeout):
				self.sendATCommOnce(command)
			timer = millis()
			#print(timer)
			f_debug = False
			self.response =""
			
			while(ser.inWaiting()):
				#print("inWaiting")
				try:
					self.response += ser.read(ser.inWaiting()).decode('utf-8', errors='ignore')
					delay(100)
				except Exception as e:
					debug_print(e.Message)
			if(self.response.find(desired_response) != -1):
				debug_print(self.response)
				break

# Function for saving conf. and reset BC26_AT module
	def resetModule(self):
		self.saveConfigurations()
		time.sleep(0.2) #delay(200)
		self.sendATComm("AT+QRST=1","")

# Function for save configurations tShield be done in current session.
	def saveConfigurations(self):
		self.sendATComm("AT&W","OK\r\n")

# Function for getting response
	def sendAT(self):
		return self.sendATComm("AT","OK\r\n")

# Function for getting ATI
	def getATI(self):
		return self.sendATComm("ATI","OK\r\n")

# Function for disable sleep mode for bc20 
	def setDisableSleepMode(self):
		return self.sendATComm("AT+QSCLK=0","OK\r\n")

# Function for getting IMEI number
	def getIMEI(self):
		return self.sendATComm("AT+CGSN=1","OK\r\n")

# Function for getting firmware info
	def getFirmwareInfo(self):
		return self.sendATComm("AT+CGMR","OK\r\n")

# Function for enable NB-IoT module
	def enableNBIOT(self):
		return self.sendATComm("AT+CFUN=1","OK\r\n")
		
# Function for getting NB-IoT module info
	def getNBIOTInfo(self):
		return self.sendATComm("AT+CFUN?","+CFUN:")

# Function for getting band info
	def getBandInfo(self):
		return self.sendATComm("AT+QBAND?","+QBAND:")

# Function for getting network info
	def getNetworkInfo(self):
		return self.sendATComm("AT+CGATT?","+CGATT: 1")

# Function for getting SIM card info
	def getSIMInfo(self):
		return self.sendATComm("AT+CIMI","OK\r\n")

# Function for setting Echo
	def setEcho(self):
		return self.sendATComm("ATE0","OK\r\n")

# Function for getting hardware info
	def getHardwareInfo(self):
		return self.sendATComm("AT+CGMM","OK\r\n")

# Function for getting signal info
	def getSignalInfo(self):
		return self.sendATComm("AT+CSQ","CSQ:")

# Function for getting self.ip_address
	def getIPAddress(self):
		return self.sendATComm("AT+CGPADDR","+CGPADDR:")  #self.sendATComm("AT+CGPADDR","OK\r\n")
# Function for getting
	def getPDPInfo(self):
		return self.sendATComm("AT+CGPADDR=1","+CGPADDR:")

#******************************************************************************************
#*** Network Service Functions ************************************************************
#******************************************************************************************
# Function for getting signal quality
	def getSignalQuality(self):
		return self.sendATComm("AT+CSQ","+CSQ:")  #self.sendATComm("AT+CSQ","OK\r\n")

#Function for Query NBIoT Band
	def getBand(self):
		return self.sendATComm("AT+QBAND?","+QBAND:") #self.sendATComm("AT+QBAND?","OK\r\n")


#*************************************************************************************
#***MQTT Protocols Functions ****BC-26/BC-66******************************
# Function for create MQTT broker server connection
#AT+QMTOPEN=0,"broker.hivemq.com",1883 => +QMTOPEN: 0,0
# *************************************************************************************
	def openMQTT(self,mqttserver="203.75.129.103",port_number=1883):
		self.compose = "AT+QMTOPEN=0,\""
		self.compose += str(mqttserver)
		self.compose += "\","
		self.compose += str(port_number)
		self.sendATComm(self.compose,"+QMTOPEN: 0,0")
		self.clear_compose()

# Function fo connect MQTT broker server connection
#AT+QMTCONN=0,“LASSclient” => +QMTCONN: 0,0,0
# *************************************************************************************
	def connectMQTT(self,clientName):
		self.compose = "AT+QMTCONN=0,\""
		self.compose += str(clientName)
		self.compose += ",\""+DEVICE_KEY+"\",\""+DEVICE_KEY+"\""
		self.sendATComm(self.compose,"+QMTCONN: 0,0,0")
		self.clear_compose()

# Function fo Punlish MQTT Topics payload data
#AT+QMTPUB=0,0,0,0,"NB/BC26/USER99/TEMP","23.10" => +QMTPUB: 0,0,0
	def publishMQTT(self,topic,payload):
		self.compose = "AT+QMTPUB=0,0,0,0,\""
		self.compose += str(topic)
		self.compose += ",[{'id': 'flight','value': ['"
		self.compose += str(payload)
		self.compose += "']}]"
		self.sendATComm(self.compose,"+QMTPUB: 0,0,0")
		self.clear_compose()


# Function fo Subscribe MQTT Topics payload data
#AT+QMTSUB=0,1,"NB/BC26/USER99/TEMP",0 => +QMTSUB: 0,1,0,0
	def subscribeMQTT(self,topic):
		self.compose = "AT+QMTSUB=0,1,\""
		self.compose += str(topic)
		self.compose += "\",0"
		self.sendATComm(self.compose,"+QMTSUB: 0,1,0,0")
		self.clear_compose()

# Function for closing server connection
	def closeMQTT(self):
		self.sendATComm("AT+QMTCLOSE=0","+QMTCLOSE: 0,0")

	def closeallMQTT(self):
		self.sendATComm("AT+QMTCLOSE=0","")

####################################
# Main program
ser = serial.Serial()
port_list = list(serial.tools.list_ports.comports())
print(port_list)
if len(port_list) == 0:
	print("NB-IoT Dongle 未安裝!")
else:
	for i in range(0,len(port_list)):
		print(port_list[i])

nb= NBIoT() #define NBIoT Class
#Loop
while 1:
	try:
		nb.resetModule()
		print("Reset BC20....................Please wait\n")
		time.sleep(3)
		print("BC20 is working....................\n")
		nb.sendAT()			#AT
		nb.setEcho()		#ATE0
		nb.getSIMInfo()		#AT+CIMI
		time.sleep(0.5)
		nb.getATI()			#ATI 查看軟體版本
		time.sleep(0.5)
		nb.setDisableSleepMode()	#AT+QSCLK=0
		time.sleep(0.5)
		nb.getIMEI()		#AT+CGSN=1
		time.sleep(0.5)
		nb.getFirmwareInfo()	#AT+CGMR
		time.sleep(0.5)
		nb.getHardwareInfo()	#AT+CGMM
		time.sleep(0.5)
		nb.getIPAddress()		#AT+CGPADDR
		time.sleep(0.5)
		nb.getSignalQuality()	#AT+CSQ
		time.sleep(1)
		nb.getBandInfo()		#AT+QBAND
		time.sleep(0.5)
		nb.enableNBIOT()		#AT+CFUN=1
		time.sleep(5)
		nb.getNBIOTInfo()		#AT+CFUN?
		time.sleep(0.5)
		nb.getNetworkInfo()		#AT+CGATT
		time.sleep(0.5)
		nb.getPDPInfo()			#AT+CGPADDR=1
		time.sleep(2)
		nb.closeallMQTT()		#AT+QMTCLOSE=0
		nb.openMQTT("140.127.208.184",8880)	#AT+QMTOPEN
		time.sleep(0.5)
		nb.connectMQTT("test\"")		#AT+QMTCONN
		time.sleep(0.5)
		while 1:	
			nb.publishMQTT("/home/flight/drone/where\"",str(random.randint(0, 100)))
			# nb.publishMQTT("/v1/device/25923207903/rawdata\"",str(random.randint(0, 100)))
			#AT+QMTPUB=0,0,0,0,"NB/BC26/USER99/TEMP","23.10" => +QMTPUB: 0,0,0
			time.sleep(10)

			# nb.subscribeMQTT("/v1/device/25923207903/sensor/flight/rawdata")

	except KeyboardInterrupt:
		print('AT+QMTCLOSE=0')
		nb.closeallMQTT() # 關閉MQTT 連線
		time.sleep(30)
		ser.close() # 清除序列通訊物件
		print('結束 MQTT 測試！')
	
# function for printing debug message

	
	

