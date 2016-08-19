# Qucik test file to open TSY01 connection and reads its temp
# 20160819 IMD
#
#


import TSYS01

sensor=TSYS01.TSYS01(0x76)
print 'Temperature = %3.3f C' % sensor.readTemp()
