from variable import Variable
from relation import Relation

class _Class:
	def __init__(self, name, variables=[],relations=[]):
		self.name = name
		self.variables = variables
		foundId = False
		for v in self.variables:
			if v.name == 'id' and v.datatype == 'INT':
				foundId = True
				break
		if not foundId:
			self.variables.insert(0, Variable('id', 'INT'))
		self.relations = relations

	def setVariable(self, var):
		found = False
		for v in self.variables:
			if v.name == var.name:
				v.datatype = var.datatype
				found = True
				break

		if not found:
			self.variables.append(var)

	def removeVariable(self, var):
		for v in self.variables:
			if v.name == var.name:
				del self.variables[self.variables.index(v)]
				break

	def setRelation(self, relation):
		found = False
		for r in self.relations:
			if r.class_right == relation.class_right:
				self.relations[self.relations.index(r)] = relation
				found = True
				break
		if not found:
			self.relations.append(relation)

	def removeRelation(self, rel):
		for r in self.relations:
			if r.class_right == rel.class_right:
				del self.relations[self.relations.index(r)]
				break

	def __repr__(self):
		echo = ["\t[ "+self.name+" ]"]
		for r in self.relations:
			other = r.class_right
			if r.relation == 'has_many':
				other += "s"
			echo.append("\t"+r.relation+" "+other)
		for v in self.variables:
			echo.append(str(v))
		return '\n'.join(echo)

	def jsonable(self):
		return self.__dict__



