#!/usr/bin/python
# (C) Kirils Solovjovs, 2017

import sys,os,re
from struct import unpack

if len(sys.argv) > 1:
	if len(sys.argv) > 2:
		dir = sys.argv[2]
	else:
		dir = sys.argv[1]+"_contents/"
else:
	raise Exception("Usage: "+sys.argv[0]+" <RouterOS.backup> [output_folder]")


if not os.access(sys.argv[1], os.R_OK):
	raise Exception("Can't read file "+sys.argv[1])

if not os.path.exists(dir):
    os.makedirs(dir)

if not os.access(dir, os.W_OK):
	raise Exception("Directory "+dir+" not writeable")
	
if os.listdir(dir)!=[]:
	raise Exception("Directory "+dir+" not empty")

realsize=os.path.getsize(sys.argv[1])

with open(sys.argv[1], 'rb') as backup:
	hdr = backup.read(4)
	
	if realsize>=8 and hdr == "\xEF\xA8\x91\x72":
		raise Exception("Encrypted RouterOS backup files are not supported.")
		
	if realsize<8 or hdr != "\x88\xAC\xA1\xB1":
		raise Exception("Not a RouterOS backup file.")
			
	matchsize, = unpack("<I",backup.read(4))
	if matchsize != realsize:
		raise Exception("File is damaged.")

	while backup.tell()+4 < matchsize:
		
		file_name = backup.read(unpack("<I",backup.read(4))[0])
		index_cont = backup.read(unpack("<I",backup.read(4))[0])
		data_cont = backup.read(unpack("<I",backup.read(4))[0])
		print '%3d entries, %8d bytes,  ./%s' % (len(index_cont)/4, len(data_cont),file_name)
		
		file_name=re.sub('\.{2,}','_',file_name); #would not wanna be writing all over the place

		try:
			os.makedirs(dir+"/"+os.path.dirname(file_name))
		except OSError as exc:
			if exc.errno == 17:
				pass

		fo = open(dir+"/"+file_name+".idx", "wb")
		fo.write(index_cont);
		fo.close()

		fo = open(dir+"/"+file_name+".dat", "wb")
		fo.write(data_cont);
		fo.close()

