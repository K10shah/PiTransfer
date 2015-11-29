import RPi.GPIO as GPIO
import time
import os
import subprocess
import glob
class HD44780 :

	"""initializing the lcd"""
    def __init__(self, pin_rs = 22,pin_e = 27, pins_db = [17,4,3,2]) :
		"""initialization"""
        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pins_db = pins_db
        
		
		"""setting the pins for lcd"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_e,GPIO.OUT) #enable pin
        GPIO.setup(self.pin_rs,GPIO.OUT) #rs pin
        for pin in self.pins_db:
            GPIO.setup(pin,GPIO.OUT) #data pins
	
		"""clearing the lcd"""
		self.clear()
	
	"""function for clearing the lcd"""
    def clear(self):
        """ lcd blank code """
        self.cmd(0x33)
        self.cmd(0x32)
        self.cmd(0x28)
        self.cmd(0x0C)
        self.cmd(0x06)
        self.cmd(0x01)
    
    def cmd(self, bits, char_mode = False) :
        """sending command to lcd"""

        time.sleep(0.01)
        bits = bin(bits)[2:].zfill(8)

        GPIO.output(self.pin_rs,char_mode)

        for pin in self.pins_db:
            GPIO.output(pin, False)

        for i in range(4):
            if bits[i] == "1" :
                GPIO.output(self.pins_db[::-1][i], True)

        GPIO.output(self.pin_e,True)
        GPIO.output(self.pin_e, False)

        for pin in self.pins_db:
            GPIO.output(pin,False)

        for i in range(4,8):
            if bits[i]=="1":
                GPIO.output(self.pins_db[::-1][i-4], True)

        GPIO.output(self.pin_e,True)
        GPIO.output(self.pin_e, False)        

    def message(self,text) :
        """send string to lcd. New line wraps to second line"""

        for char in text:
            if char == '\n':
                self.cmd(0xC0) #next line
            else:
                self.cmd(ord(char), True)
                
"""here the main program starts"""   
if __name__ == '__main__' :

    lcd = HD44780()
    lcd.message("HELLO") #printing hello
    time.sleep(3) #time delay is in seconds
    loopi=0 #this variable controls how many times our program will run 
	"""if you want it to run infinitely you just keep the while loop below as true"""
    while(loopi<10):
        loopi=loopi+1
        lcd.clear()
        lcd.message("Welcome")
        time.sleep(2)

		
		"""setting up pins for buttons"""
        GPIO.setmode(GPIO.BCM)
        one = 9
        two = 11
        three = 5
        four = 10
        GPIO.setup(one,GPIO.IN,pull_up_down=GPIO.PUD_UP) #PUD_UP will return false when button is pressed
        GPIO.setup(two,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(three,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(four,GPIO.IN,pull_up_down=GPIO.PUD_UP)

        cont = True
        pdList = os.listdir("/media/.") #variable pdList for listing all the folder names present in the media folder. 
		"""This command will only return folder names without any path"""
        lcd.clear()
        time.sleep(1.5) #adding delay after every print operation just to avoid any error 
       
        if len(pdList)>= 2 : #if two pen drives present then only proceed
            lcd.clear()
            lcd.message("select source \n Press 1 or 2")
            time.sleep(2)
            while cont :
                selectedDrive = ""
                if(GPIO.input(one) == False):
                    lcd.clear()
                    lcd.message("Pressed 1")
                    time.sleep(2)
                    selectedDrive = pdList[0]
                    fileList = glob.glob("/media/"+pdList[0]+"/*") #this function returns all the file names present in the folder along with their paths
					"""eg. /media/KETAN/abc.mp3"""
                    cont = False
                elif(GPIO.input(two)== False):
                    lcd.clear()
                    lcd.message("Pressed 2")
                    time.sleep(2)
                    selectedDrive = pdList[1]
                    fileList = glob.glob("/media/"+pdList[1]+"/*")
                    cont = False
                time.sleep(0.5)
            
            if len(fileList)>=1 :
                #there are files to copy - start with the procedure
                pointer = 0
                displayList = list(fileList)
                cutLength = 8 + (len(selectedDrive)) #this is just for cutting down only some part of the file name for displaying
                i = 0
                #while loop formatting diplay text
                while i< len(displayList):
                    endLength = 13 -(len(displayList[i])-cutLength) 
                    if endLength >= 0 :
                        endLength = len(displayList[i])
                    displayList[i] = displayList[i][cutLength : endLength]
                    while len(displayList[i]) < 13:
                        displayList[i] = displayList[i]+" "
                
                    i=i+1
                #selectedList
                cont = True
                lcd.clear()
                lcd.message(displayList[pointer]+"\n"+displayList[(pointer+1)%len(displayList)])
                time.sleep(2)
                while cont : 
                    
                    if(GPIO.input(one)==False):
                        if len(displayList[pointer])==13:
                            displayList[pointer] = displayList[pointer] + "-"
                            time.sleep(0.5)
                        elif len(displayList[pointer])==14:
                            displayList[pointer] = displayList[pointer][:12]
                            time.sleep(0.5)
                        lcd.clear()
                        lcd.message(displayList[pointer]+"\n"+displayList[(pointer+1)%len(displayList)])
                    elif(GPIO.input(two)==False):
                        pointer = (pointer - 1)% len(displayList)
                        lcd.clear()
                        lcd.message(displayList[pointer]+"\n"+displayList[(pointer+1)%len(displayList)])
                        time.sleep(0.5)
                    elif(GPIO.input(three)==False):
                        pointer = (pointer + 1)% len(displayList)
                        lcd.clear()
                        lcd.message(displayList[pointer]+"\n"+displayList[(pointer+1)%len(displayList)])
                        time.sleep(0.5)
                    elif(GPIO.input(four)==False):
                        #code for actually copying the files to destination now
                        #subprocess.call("cp -R '"+filelist[0]+"' /media/KETAN",shell=True)
                        lcd.clear()
                        lcd.message("select \nDestination")
                        time.sleep(2)
                        cont1 = True
                        destination = ""
                        while(cont1):
                            if(GPIO.input(one)==False):
                                destination = "/media/"+pdList[0]
                                lcd.clear()
                                lcd.message("Selected 1")
                                cont1=False
                                time.sleep(0.5)
                            elif(GPIO.input(two)==False):
                                destination = "/media/"+pdList[1]
                                lcd.clear()
                                lcd.message("Selected 2")
                                cont1=False
                                time.sleep(0.5)
                       
                        i=0
                        while i < len(displayList):
                            if len((displayList[i]))==14:
                                if(fileList[i] == "System Volume Information"):
                                    print ""
                                else :
                                    lcd.clear()
                                    lcd.message("..Copying..")
                                    subprocess.call("sudo cp -R '"+fileList[i]+"' '"+destination+"'",shell=True) #this is the linux command that will copy
                    
                            
                            i=i+1
                        
                        lcd.clear()
                        lcd.message("Everything copied.")
                        cont = False
                        time.sleep(0.3)

            else :
                #no file to copy
                print ""
        else:
            pass
               
    

