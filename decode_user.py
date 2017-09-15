#!/usr/bin/python
# (C) Kirils Solovjovs, 2017

import sys,md5,datetime
from socket import inet_ntop,AF_INET,AF_INET6

from mt_dat_decoder import MTConfig

def xor(data, key): 
    return str(bytearray(a^b for a, b in zip(*map(bytearray, [data, key])))).split("\x00",2)[0]

def parseIPv4(data):
	return inet_ntop(AF_INET, chr(data & 0xFF) + chr(data >> 8 & 0xFF)+ chr(data >> 16 & 0xFF)+ chr(data >> 24 & 0xFF))

def parseIPv6(data):
	return inet_ntop(AF_INET6,''.join(map(chr,data)))
	
def parseAddressNet(data):
	ip = None
	netmask = None
	
	for blocktype in data:
		if blocktype == "_u1" or blocktype == "_u5" :
			ip = parseIPv4(data[blocktype])
		elif blocktype =="_a3":
				ip = parseIPv6(data[blocktype])
		elif blocktype =="_u4":
			netmask = str(data[blocktype])
		elif blocktype == "_u2" or blocktype == "_u6" :
			netmask = str(bin(data[blocktype]).count("1"))
			
	if ip and netmask:
		return ip+"/"+netmask


def parseMTdate(data):
	return datetime.datetime.fromtimestamp(data).strftime('%b/%d/%Y %H:%M:%S')

def parseMTusergroup(data):
	# this may be incorrect. depends on group.dat ;)
	groups = ["read","write","full"]
	if data>=0 and data<len(groups):
		return groups[data]

	
if len(sys.argv) > 1:
	dir = sys.argv[1]
else:
	dir = "."

database="user"

conf = MTConfig(dir+"/"+database+".dat",dir+"/"+database+".idx")

conf.mapBlockNames( {0xb:"permissions", 0x1f:"last_login", 0x1c:"password_set",
					0x1:"username",0x11:"password",0x2:"group",0x12:"groupname",
					0x10:"allowed_addresses",0x5:"allowed_ip4", 0x6:"allowed_net4" })

conf.addParser (0x1f, parseMTdate)
conf.addParser (0x12, parseMTusergroup)
conf.addParser (0xb, lambda x: "%x" % x)
conf.addParser (0x5, parseIPv4)
conf.addParser (0x6, parseIPv4)
conf.addParser (0x10, parseAddressNet)


for record in conf:
	if "username" in record and "password" in record: # http://hop.02.lv/2Wb
		record["#key"]=md5.new(record["username"]+"283i4jfkai3389").digest()	
		record["password"]=xor(record["password"],record["#key"]*16)
		record["#key"]=" ".join("{:02x}".format(ord(c)) for c in record["#key"])

	print(record)
	
