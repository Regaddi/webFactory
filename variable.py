class Variable:
	def __init__(self, name='', datatype=''):
		self.name = name
		self.datatype = datatype

	def __repr__(self):
		return "\t"+self.datatype+"\t"+self.name

	def jsonable(self):
		return self.__dict__