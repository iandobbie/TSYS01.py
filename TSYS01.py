#Copyright (c) 2016 Ian Dobbie (ian.doibbie@bioch.ox.ac.uk)
# V 1.0 20160815 IMD
#
# This is a simple library to access the TSY01 i2c sensor board on a
# rapsberrypi (tested on a 3)

#Default i2c address is 0x76 i2c bus is 1 on a RPi 3. Only alternative
#is 0x77 as we have a single address pin on this chip.


import smbus
import time
import struct

#i2c commands
# 0x1E     Reset
# 0x48     start ADC temp conversion
# 0x00     Read ADC temp result
# 0xA0,0xA2,...0xAE   read prom addresses 0-7

ADDR_DEFAULT = 0x76

#addresses of the calibration coefficents.
#TSY01_COEFF0 = 0xAA
#TSY01_COEFF1 = 0xA8
#TSY01_COEFF2 = 0xA6
#TSY01_COEFF3 = 0xA4
#TSY01_COEFF4 = 0xA2

#The following are taken from the Ardruino libabry at:
#https://github.com/Ell-i/ELL-i-KiCAD-Boards/blob/master/TSYS01/Arduino/Tsys01.h
#Made by Apocalyt, precalculated constants of powers of 10
#This resolves loss of accuracy in calculation of the temperature values resulting from
#10^(-21/4) / 256.0
TSYS_POW_A = 0.0000056234132519034908039495103977648123146825104309869166408/ 256.0
#10^(-16/3) / 256.0
TSYS_POW_B = 0.0000046415888336127788924100763509194465765513491250112436376/ 256.0
#10^(-11/2) / 256.0
TSYS_POW_C = 0.0000031622776601683793319988935444327185337195551393252168268/ 256.0
# 10^(-6/1) / 256.0
TSYS_POW_D = 0.000001/ 256.0
#10^(-2/1)
TSYS_POW_E = 0.01


#main class.
class TSYS01(object):
    """Class to read the TSY01 i2c temperature sensing board"""
    def __init__(self, address=ADDR_DEFAULT, i2c=1, **kwargs):
        """Initialise TSY01 device, resets and reads calibration data as well"""
        self.address=address
        if (self.address != 0x76 and self.address != 0x77):
            print "Error: TSY01 only supports address 0x76 or 0x77"
            return
        self.bus = smbus.SMBus(1)
        #reset board to get it into a know state.
        self.reset()
        #read a store calibration data for laetr calculation
        self.readCalibration()
        
    def reset(self):
        """Reset the device"""
        self.bus.write_byte_data(self.address,0,0x1E)

    def readCalibration(self):
        """Reads calibartion from the sensor and stores it on self.cal"""
        self.cal=[0]*5
        for i in range(5):
            caldata=self.bus.read_word_data(self.address,(0xAA-i*2))
            self.cal[i]=struct.unpack("<H",struct.pack(">H",caldata))[0]

    #define to allow compatibility with adafruit MCP9808 library
    def readTempC(self):
        """Reads the adc values and returns the temp in C"""
        return(readTemp())

            
    def readTemp(self):
        """Reads the adc values and returns the temp in C"""
        #first start  tempurature conversion
        self.bus.write_byte(self.address,0x48)
        #let ADC converstion happen, max time is 10ms
        time.sleep(0.01)
        #then read output data
        output= self.bus.read_i2c_block_data(self.address,0x00,3)
        self.lastADC=output[2]+256*output[1]+(256**2)*output[0]
        #return temp but adc value is stored in self.lastADC
        return(self.calculateTemp(self.lastADC))
        
    def calculateTemp(self, adc):
        """Takes 24bit ADC values are returns temperature in C"""
        #see TSY01 data sheet for spec of this calulation
        term1=(-2.0)*self.cal[4]*((TSYS_POW_A*adc)**4)
        term2=(4.0)*self.cal[3]*((TSYS_POW_B*adc)**3)
        term3=(-2.0)*self.cal[2]*((TSYS_POW_C*adc)**2)
        term4=(1)*self.cal[1]*(TSYS_POW_D*adc)
        term5=(-1.5)*self.cal[0]*(TSYS_POW_E)
        
        self.lastTemp=term1+term2+term3+term4+term5
        #return temperatiure but also store it in self.lastTemp
        return(self.lastTemp)
    
