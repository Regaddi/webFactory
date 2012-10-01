class Relation:
	def __init__(self, class_left=None, class_right=None, relation=None):
		self.class_left = class_left
		self.class_right = class_right
		self.relation = relation

	def __repr__(self):
		other = self.class_right.name
		if self.relation == 'has_many':
			other += "s"
		return self.class_left.name+"\t->\t"+self.relation+"\t->\t"+other

	def jsonable(self):
		return self.__dict__