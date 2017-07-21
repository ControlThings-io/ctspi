#!/usr/bin/env python
# encoding: utf-8
"""
Adapted from i2c-dump.py
"""
import sys
from pyBusPirateLite.SPI import *
import argparse

def read_list_data(size):
	data = []
	for i in range(size+1):
		data.append(0)
	return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument("-o", "--output", dest="outfile", metavar="OUTFILE", type=argparse.FileType('wb'),
            required=True)
    parser.add_argument("-p", "--serial-port", dest="bp", default="/dev/ttyUSB0")
    parser.add_argument("-s", "--size", dest="size", type=int, required=True)
    parser.add_argument("-S", "--serial-speed", dest="speed", default=115200, type=int)

    args = parser.parse_args(sys.argv[1:])

    spi = SPI(args.bp, args.speed)
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
        
    print "Configuring SPI."
    if not spi.cfg_pins(PinCfg.POWER | PinCfg.CS | PinCfg.AUX):
        print "Failed to set SPI peripherals."
        sys.exit()

    print "Configuring SPI configuration: ",
    if spi.cfg_spi(SPICfg.CLK_EDGE | SPICfg.SAMPLE | SPICfg.OUT_TYPE):
        print "OK."
    else:
        print "failed."
        sys.exit()
    spi.timeout(0.2)
    
    print "Dumping %d bytes out of the EEPROM." % args.size
    spi.CS_Low()
    spi.bulk_trans(3, [0x3, 0, 0])
    for i in range(args.size/16):
        data = spi.bulk_trans(16, read_list_data(16))
        args.outfile.write(data)
    spi.CS_High()

    print "Reset Bus Pirate to user terminal: "
    if spi.resetBP():
        print "OK."
    else:
        print "failed."
        sys.exit()



