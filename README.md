# TSYS01.py
Basic library to read the TSYS01 temperature sensor over i2c on a Raspberry Pi.

This is a python module to provide basic fucntions to access the TSY01
temperature sensor board over i2c from as Raspberry Pi.  I bought a
complete board from
http://www.elecrow.com/tsys01-temperature-sensor-board-p-1608.html but
you can also get the bare chips if you are more of a hardware hacker
than me.

The whole library is in TSYS01.py and requires smbus time and struct
to run.

Very simple to use, simply create a connection by calling
 sensor=TSYS01.TSYS01()
This opens the connection, resets the board
and reads the calibration params. The temperature can then be read by
calling
 sensor.readTemp()

