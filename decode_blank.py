#!/usr/bin/python

from mt_dat_decoder import MTConfig

def onlyPrintable (s):
	 return s if all(c in map(chr, range(32, 127)) for c in s) else "!{non-printable string of len %i}" % len(s)

dir="."
database="dhcp/client"

conf = MTConfig(dir+"/"+database+".dat",dir+"/"+database+".idx")

#conf.returnTypes = True
conf.mapBlockNames( {
	"_be" : "Use Peer NTP"
	} )

conf.addFilter (0, lambda x: "No" ) # addFilter() works on block types or data types
conf.addFilter (1, lambda x: "Yes" )
conf.addFilter (str, onlyPrintable)
conf.addParser (0x12, lambda x: "0x%x" % x ) # addParser() works on block ids
#conf.addParser ("_u2", lambda x: x )

for record in conf:
	print(record)

