class Relation:
	def __init__(self, class_right=None, relation=None):
		self.class_right = class_right
		self.relation = relation

	def __repr__(self):
		other = self.class_right
		if self.relation == 'has_many':
			other += "s"
		return "\t->\t"+self.relation+"\t->\t"+other

	def jsonable(self):
		return self.__dict__