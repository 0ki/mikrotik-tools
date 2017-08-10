#!/usr/bin/python
# (C) Kirils Solovjovs, 2015

import sys,base64,zlib

#           111111 11112222
#01234567 89012345 67890123
#cdefgh56 78abGH12 34ABCDEF  (from)
#abcdefgh 12345678 ABCDEFGH  (to)
revtribitmap=[2,3,4,5,6,7,12,13,14,15,0,1,22,23,8,9,10,11,16,17,18,19,20,21]
#tribitmap=[10,11,0,1,2,3,4,5,14,15,16,17,6,7,8,9,18,19,20,21,22,23,12,13]

def revtribit(content):
	#origlen=len(content)
	
	while len(content)%3:
		content= content + "\x00"
		
	result=""
	for i in xrange(0, len(content) - 1,3):	
		goodtribit=0
		badtribit=ord(content[i])*0x10000+ord(content[i+1])*0x100+ord(content[i+2])
		for mangle in revtribitmap:
			goodtribit = (goodtribit<<1) + (1 if ((badtribit & (0x800000>>mangle))>0) else 0)
			
		for move in [16,8,0]:
			result=result+chr((goodtribit >> move)& 0xff)

	return result
	#return result[0:origlen]



if len(sys.argv) < 2:
	raise Exception("Usage: "+sys.argv[0]+" <section_name> [contentfile (or stdin)]")

if len(sys.argv) > 2:
	data=open(sys.argv[2],"rb")
else:
	data=sys.stdin
	
data=sys.argv[1]+"\x00"+zlib.compress(data.read())
reallen=len(base64.b64encode(data).replace("=",""))
data=base64.b64encode(revtribit(data))
data=data[:reallen]+"="*(len(data)-reallen)

sys.stdout.write("--BEGIN ROUTEROS SUPOUT SECTION\r\n");
sys.stdout.write("\r\n".join(data[i:i+76] for i in xrange(0, len(data), 76)))
sys.stdout.write("\r\n--END ROUTEROS SUPOUT SECTION\r\n");
