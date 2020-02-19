# (C) Kirils Solovjovs, 2017

from warnings import warn
from struct import unpack
from collections import OrderedDict

class MTConfig(object):
	
	def __init__(self, datFileName, idxFileName=None):
		self.__db = open(datFileName, 'rb')
		if idxFileName is None:
			self.__index = None
		else:
			self.__index = open(idxFileName, 'rb')
		self.__ip = 0
		self.mapping = {0xfe0009 : 'comment',
						0xfe0001: 'record_id',
						0xfe000a: 'disabled',
						0xfe000d: 'default',
						0xffffff: 'index_id',
						0xfe0008: 'active',
						0xfe0010: 'name',
						}
		self.decode = False
		self.returnTypes = False
		self.preserveOrder = False
		self.parsers = {}
		self.filters = {}
		self.__idFormat = "_%c%x"
		self.__idFormatTypeLocation = 1
	
	@property
	def idFormat(self):
		return self.__idFormat
		
	@idFormat.setter
	def idFormat(self, idFormat):
		
		for i in map(chr, range(33, 48)):
			if i not in idFormat:
				break
		if i == "0":
			raise Exception("Unable to detect type position inside id format. Try using less characters.")
		
		self.__idFormat = idFormat
		
		test = idFormat %(i,0xAABBCC)
		if i in test:
			self.__idFormatTypeLocation = test.index(i)
		else:
			self.__idFormatTypeLocation = None

			
	def __iter__(self):
		return self


	def next(self):
		
		if self.__index is None:
			try:
				size, = unpack("<H",self.__db.read(2))
				parsed = self.parse_record(self.__db.read(size-2))
				if parsed is not None and self.returnTypes:
					parsed[iid_r] = (0x08,parsed[iid_r])
				return parsed
			except:
				raise StopIteration
			
		iid = 0xFFFFFFFF
		while iid == 0xFFFFFFFF:
			ientry=self.__index.read(12)
			if len(ientry)<12:
				raise StopIteration
			iid, = unpack("<I",ientry[0:4])
			ilen, = unpack("<I",ientry[4:8])
			isep, = unpack("<I",ientry[8:12])
			self.__ip += ilen
		
		if isep != 5:
			warn("Non-standart index separator %08X." % isep)
		
		self.__db.seek(self.__ip - ilen)
		size, = unpack("<H",self.__db.read(2))
		parsed = self.parse_record(self.__db.read(size-2))
		
		if parsed is None:
			return None
		
		iid_r = self.__idFormat % ("$",0xffffff)
		if self.decode:
			if (0xffffff) in self.mapping:
				iid_r = self.mapping[0xffffff]
			elif iid_r in self.mapping:
				iid_r = self.mapping[iid_r]
				
		parsed[iid_r] = self.parse_value(0xffffff,iid_r,0x08,iid)

		if self.returnTypes:
			parsed[iid_r] = (0x08,parsed[iid_r])
			
		return parsed
		
	def __mangle_data(self,what,which,how):
		if which in how:
			if isinstance(what,list):
				what_r=[ how[which](x) for x in what ] 
				go = sum([ x is not None for x in what_r ])
				if go == len(what):
					return what_r
				
			else:
				what_r=how[which](what)
				if what_r is not None:
					return what_r
					
		return None
		
	def parse_value(self,blockid_raw,blockid,blocktype,data):
		data_r = self.__mangle_data(data,blockid,self.parsers)
		if data_r is not None:
			return data_r
		data_r = self.__mangle_data(data,blockid_raw,self.parsers)
		if data_r is not None:
			return data_r
		data_r = self.__mangle_data(data,blocktype,self.filters)
		if data_r is not None:
			return data_r
		if self.__idFormatTypeLocation is not None:
			data_r = self.__mangle_data(data,blockid[self.__idFormatTypeLocation],self.filters)
			if data_r is not None:
				return data_r		
		data_r = self.__mangle_data(data,type(data),self.filters)
		if data_r is not None:
			return data_r
		return data
					
	
	def parse_record(self, record, topID=0):
		if self.preserveOrder:
			alldata = OrderedDict()
		else:
			alldata = {}

		if record[0:2] != "\x4D\x32":
			warn("Not MT DAT record.")
			return None
		
		bpointer = 2
		while bpointer+4 < len(record):
			bmarker, = unpack("<I",record[bpointer:bpointer+4])
			bpointer += 4
			bidraw = bmarker & 0xffffff
					
			btype = bmarker >> 24
			
			blen = None
			data = None
			

			'''
			btype ........
			      0000000, - boolean 
			      ,,1,1,,, - M2 block (len = short)
			      ,,11,,,, - binary data block (len = short)
			      ,,,,,,,1 - one byte
			      ,,,,,,1, - ???
			      ,,,,,1,, - ???
			      ,,,11,,, - 128bit int
			      ,,,,1,,, - int (four bytes)
			      ,,,1,,,, - long (8 bytes)
			      ,,1,,,,, - string
			      ,1,,,,,, - ??? unused? or long array of?
			      1,,,,,,, - short array of
			      			      
			types (MT notation)
				(CAPITAL X = list of x)

				a,A, (0x18) IPv6 address (or duid)
				b,B, bool
				  M, multi
				q,Q, (0x10) big number
				r,R, (0x31) mac address
				s,S, (0x21) string
				u,U, unsigned integer

			'''
			if btype == 0x21: #freelength short string	
				blen, = unpack("B",record[bpointer])
				bpointer += 1
				data = record[bpointer:bpointer+blen]
				mtype = "s"
			elif btype == 0x31: #freelength list of bytes (mac address)
				blen, = unpack("B",record[bpointer])
				bpointer += 1
				mtype = "r"
				data = map(ord,record[bpointer:bpointer+blen])
			elif btype == 0x08: #int
				blen = 4
				data, = unpack("<I",record[bpointer:bpointer+blen])
				mtype = "u"
			elif btype == 0x10: #long
				blen = 8
				data, = unpack("<Q",record[bpointer:bpointer+blen])
				mtype = "q"
				data = long(data)
			elif btype == 0x18: #128bit integer
				blen = 16
				data = map(ord,record[bpointer:bpointer+blen])
				mtype = "a"
			elif btype == 0x09: # byte
				blen = 1
				data, = unpack("B",record[bpointer:bpointer+blen])
				mtype = "u"
			elif btype == 0x29: # single short M2 block
				blen = 1
				sub_size, = unpack("B",record[bpointer:bpointer+blen])
				data = self.parse_record(record[bpointer+1:bpointer+1+sub_size],topID=(topID<<24)+bidraw)
				bpointer += sub_size
				mtype = "M"
			elif btype == 0xA8: # array of M2 blocks
				blen = 2
				arraysize, = unpack("<H",record[bpointer:bpointer+blen])
				parser = 0
				data = []
				while parser < arraysize:
					parser += 1
					bpointer += blen
					sub_size, = unpack("<H",record[bpointer:bpointer+2])
					bpointer += 2
					data.append(self.parse_record(record[bpointer:bpointer+sub_size],topID=(topID<<24)+bidraw))
					# MT has a bug here ^^, replicate it 
					
					bpointer += sub_size - 2
				mtype = "M"
			elif btype == 0x88: #array of int
				blen = 2
				arraysize, = unpack("<H",record[bpointer:bpointer+blen])
				parser = 0
				data = []
				while parser < arraysize:
					parser += 1
					data.append(unpack("<I",record[bpointer+blen:bpointer+blen+4])[0])
					bpointer += 4
				mtype = "U"
			elif btype == 0xA0: #array of strings
				blen = 2
				arraysize, = unpack("<H",record[bpointer:bpointer+blen])
				parser = 0
				data = []
				while parser < arraysize:
					parser += 1
					bpointer += blen
					sub_size, = unpack("<H",record[bpointer:bpointer+2])
					bpointer += 2
					data.append(record[bpointer:bpointer+sub_size])
					bpointer += sub_size - 2
				mtype = "S"
				
			elif btype == 0x00 or btype == 0x01:  # boolean
				blen = 0
				data = False if not btype else True
				mtype = "b"
			else:
				warn("Unknown datatype %02X." % btype)
				mtype = " "
				blen = 0
				data = None
			
			bid = self.__idFormat % (mtype,bidraw)
			if self.decode:
				if ((topID<<24) + bidraw) in self.mapping:
					bid = self.mapping[((topID<<24) + bidraw)]
				elif bid in self.mapping:
					bid = self.mapping[bid]


			data = self.parse_value	((topID<<24) + bidraw,bid,btype,data)
			
			
			if bid in alldata:
				warn("Record contains multiple blocks %06X that translate to the same ID (\"%s\"), ignoring extra blocks. Check your mapping and idFormat." % (bidraw, bid))
			else:
				if self.returnTypes:
					alldata[bid] = (btype,data)
				else:
					alldata[bid] = data
			
			bpointer += blen

		return alldata
		
		
		
	def mapBlockNames(self, mapping):
		self.mapping.update(mapping)
		self.decode = True

	def addParser(self, blockid, function):
		self.parsers[blockid] = function
		
	def addFilter(self, blocktype, function):
		self.filters[blocktype] = function


if __name__ == '__main__':
	
	store="."
	names = ["group"]
	for dbname in names:
		conf = MTConfig(store + "/" + dbname + ".dat", store + "/" + dbname + ".idx")
		conf.returnTypes = True
		conf.preserveOrder = True
		
		for record in conf:
			print "Start of record"
			
			for block in record:
				(btype,data) = record[block]
				print "(%02X) %s %s %s%s" % (btype, block, type(data), "{%i} "%len(data) if isinstance(data,(str,list,dict)) else "","" if (btype & 0x28 == 0x28) else data)
				if btype & 0x28 == 0x28:
					if btype & 0x80 != 0x80:
						data=[data]
					
					for item in data:
						if btype & 0x80 == 0x80:
							print "   -> (%02X) %s %s {%i}" % (btype & ~0x80, block, type(data), len(item))
						for block_s in item:
							(btype_s,data_s) = item[block_s]
							print "   "*(2 if (btype & 0x80 == 0x80) else 1)+"-> (%02X) %s %s %s%s" % (btype_s, block_s, type(data_s),"{%i} "%len(data_s) if isinstance(data_s,(str,list,dict)) else "", data_s)
						

			print "End of record"
			print


