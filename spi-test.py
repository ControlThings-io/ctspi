#!/usr/bin/env python
# encoding: utf-8
"""
Usage:
  pyi2c read ADDRESS [LENGTH] (-c | -m) [-Prtfv]
  pyi2c write ADDRESS (DATA | -f FILE | [-]) (-c | -mp) [-Prtv]
  pyi2c wipe ADDRESS [LENGTH] ( -c | -m) [-Prtfv]
  pyi2c sniff ( -c | -s) [-vf]

Arguments:
  ADDRESS                   Memory address to work with  [default: 0]
  LENGTH                    Number of bytes to read from chip or wipe
                              If LENGTH is not given, we'll figure it out
  DATA                      Data to write in ASCII, 0xABCD, or 0b0000
  [-]                       Write data from stdin if DATA nor FILE given

Options:
  --version                 Show program's version number and exit
  -f FILE, --file=FILE      File to write data to or read data from
  -v, --verbose             Increase verbosity level

  -c CHIP, --chip=CHIP      Specify chip to read/write.  Available:
                              AT25256     LENGTH=32768 -p 64
                              25AA128     LENGTH=16384 -p 64
                              25LC128     LENGTH=16384 -p 64
                              AT25080     LENGTH=1024 -p 32
                              email justin@meeas.com to contribute...
  -m MODE, --mode=MODE      SPI mode of operation  [default 0]
                              mode 0 : pol = 0, phase = 0
                              mode 3 : pol = 1, phase = 1
                              modes 1 and 2 are not supported
  -p NUM, --page=NUM        Max write page size  [default 64 bytes]

  -P PORT, --port=PORT      Serial port for Aardvark or BusPirate
                              If PORT not given, we'll figure it out
  -r RATE, --rate=RATE      Rate to read/write in mbps  [default: 1]
  -t NUM, --timeout=NUM     Timeout for read/write in millisec  [default: 250]

Copyright 2015 Justin Searle
Licensed under the GPL 3.0 or later, see <http://www.gnu.org/licenses/>
Partially adapted for BusPirate from Sean Nelson's spi_test.py
"""

from serial.serialutil import SerialException
import sys, optparse
from pyBusPirateLite.SPI import *

def read_list_data(size):
	data = []
	for i in range(size+1):
		data.append(0)
	return data

def parse_prog_args():
	parser = optparse.OptionParser(usage="%prog [options] filename",
									version="%prog 1.0")

	parser.set_defaults(command="read")

	parser.add_option("-v", "--verbose",
						action="store_true", dest="verbose", default=True,
						help="make lots of noise [default]")
	parser.add_option("-q", "--quiet",
						action="store_false", dest="verbose",
						help="be mute")
	parser.add_option("-r", "--read",
						action="store_const", dest="command", const="read",
						help="read from SPI to file [default]")
	parser.add_option("-w", "--write",
						action="store_const", dest="command", const="write",
						help="write from file to SPI")
	parser.add_option("-e", "--erase",
						action="store_const", dest="command", const="erase",
						help="erase SPI")
	parser.add_option("-i", "--id",
						action="store_const", dest="command", const="id",
						help="print Chip ID")
	parser.add_option("-s", "--size",
	 					dest="flash_size", default=128,
						help="Size of Flashchip in bytes", type="int")
	parser.add_option("-d", "--dev",
	 					dest="dev_name", default="/dev/tty.usbserial-A7004qlY",
						help="The device to connect to", type="string")

	(options, args) = parser.parse_args()

	if options.command == "id":
		return (options, args)
	elif len(args) != 1:
		parser.print_help()
		print options
		sys.exit(1)
	else:
		return (options, args)
	
""" enter binary mode """
if __name__ == '__main__':
	data = ""
	(opt, args)  = parse_prog_args()

	if opt.command == "read":
		f=open(args[0], 'wb')
	elif opt.command == "write":
		f=open(args[0], 'rb')

	try:
		spi = SPI(opt.dev_name, 115200)
	except SerialException as ex:
		print ex
		sys.exit();

	print "Entering binmode: ",
	if spi.BBmode():
		print "OK."
	else:
		print "failed."
		sys.exit()

	print "Entering raw SPI mode: ",
	if spi.enter_SPI():
		print "OK."
	else:
		print "failed."
		sys.exit()
		
	print "Configuring SPI peripherals: ",
	if spi.cfg_pins(PinCfg.POWER | PinCfg.CS | PinCfg.AUX):
		print "OK."
	else:
		print "failed."
		sys.exit()
	print "Configuring SPI speed: ",
	if spi.set_speed(SPISpeed._2_6MHZ):
		print "OK."
	else:
		print "failed."
		sys.exit()
	print "Configuring SPI configuration: ",
	if spi.cfg_spi(SPICfg.CLK_EDGE | SPICfg.OUT_TYPE):
		print "OK."
	else:
		print "failed."
		sys.exit()
	spi.timeout(0.2)

	if opt.command == "read":
		print "Reading EEPROM."
		spi.CS_Low()
		spi.bulk_trans(5, [0xB, 0, 0, 0, 0])
		for i in range((int(opt.flash_size)/16)):
			data = spi.bulk_trans(16, read_list_data(16))
			f.write(data)
		spi.CS_High()

	elif opt.command == "write":
		print "Writing EEPROM."
		spi.CS_Low()
		spi.bulk_trans(4, [0xA, 0, 0, 0])
		for i in range((int(opt.flash_size)/16)):
			spi.bulk_trans(16, None)
		spi.CS_High()

	elif opt.command == "id":
		print "Reading Chip ID: ",
		spi.CS_Low()
		d = spi.bulk_trans(4, [0x9F, 0, 0, 0])
		spi.CS_High()
		for each in d[1:]:
			print "%02X " % ord(each),
		print

	elif opt.command == "erase":
		pass

	print "Reset Bus Pirate to user terminal: ",
	if spi.resetBP():
		print "OK."
	else:
		print "failed."
		sys.exit()
		
