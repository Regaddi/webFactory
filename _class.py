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

	def generatePHPModel(self):
		lines = []
		lines.append("<?php\n\n/** generated with webFactory "+str(version)+" */\n\n")
		# begin
		lines.append("class "+self.name+" extends ActiveRecordModel {\n")

		# vars
		for v in self.variables:
			if v.name == "id":
				lines.append("\tpublic $id = 0;\n")
			else:
				lines.append("\tpublic $"+v.name+";\n")
		for r in self.relations:
			if r.relation == 'belongs_to':
				lines.append("\t// belongs to\n\tpublic $"+r.class_right.lower()+";\n")
			elif r.relation == 'has_many':
				lines.append("\t// has many\n\tpublic $"+r.class_right.lower()+"s;\n")

		# getTableName
		lines.append("\n\tpublic static function getTableName() {\n")
		lines.append("\t\treturn '"+self.name.lower()+"s';\n")
		lines.append("\t}\n")

		for r in self.relations:
			if r.relation == 'has_many':
				# has_many_class
				lines.append("\n\tprotected $has_many_"+r.class_right.lower()+"s = TRUE;\n");
				# has_many_var
				lines.append("\n\tprotected static $has_many_"+r.class_right.lower()+"s_var = '"+r.class_right.lower()+"s';\n");
				# class_var
				lines.append("\n\tprotected $"+r.class_right.lower()+"s_class = '"+r.class_right+"';\n");

				# get child by index
				funcName = "get"+r.class_right+"ByIndex"
				lines.append("\n\tpublic function "+funcName+"($index) {\n")
				lines.append("\t\treturn $this->"+r.class_right.lower()+"s[$index];\n")
				lines.append("\t}\n")
			elif r.relation == 'belongs_to':
				# belongs_to_class
				lines.append("\n\tprotected $belongs_to_"+r.class_right.lower()+" = TRUE;\n");
				# belongs_to_var
				lines.append("\n\tprotected static $belongs_to_"+r.class_right.lower()+"_var = '"+r.class_right.lower()+"';\n");
				# class_var
				lines.append("\n\tprotected $"+r.class_right.lower()+"_class = '"+r.class_right+"';\n");

				# get parent
				funcName = "get"+r.class_right
				lines.append("\n\tpublic function "+funcName+"() {\n")
				lines.append("\t\treturn "+r.class_right+"::find($this->"+r.class_right.lower()+");\n")
				lines.append("\t}\n")

				# get by parent or parent id
				funcName = "find_by_"+r.class_right.lower()
				parent = r.class_right.lower()
				lines.append("\n\tpublic function "+funcName+"($"+parent+") {\n")
				lines.append("\t\tif(is_int($"+parent+") || is_numeric($"+parent+")) {\n")
				lines.append("\t\t\treturn "+self.name+"::find('"+r.class_right.lower()+"_id='.$"+parent+");\n")
				lines.append("\t\t} elseif(get_class($"+parent+") == '"+r.class_right+"') {\n")
				lines.append("\t\t\treturn "+self.name+"::find('"+r.class_right.lower()+"_id='.$"+parent+"->id);\n")
				lines.append("\t\t}\n")
				lines.append("\t}\n")


		# static functions
		# all()
		lines.append("\n\tpublic static function all() {\n")
		lines.append("\t\t$result = array();\n")
		lines.append("\t\t$db = new DB();\n")
		lines.append("\t\t$rows = $db->preparedStatement(\"SELECT * FROM `\".self::getTableName().\"`\");\n")
		lines.append("\t\tforeach($rows as $r) {\n")
		lines.append("\t\t\tarray_push($result, new "+self.name+"($r));\n")
		lines.append("\t\t}\n")
		lines.append("\t\t$db->close();\n")
		lines.append("\t\treturn $result;\n")
		lines.append("\t}\n")

		# find()
		lines.append("\n\tpublic static function find($searchTerm) {\n")
		lines.append("\t\t$db = new DB();\n")
		lines.append("\t\tif(is_numeric($searchTerm)) {\n")
		lines.append("\t\t\t$r = $db->preparedStatement(\"SELECT * FROM `\".self::getTableName().\"` WHERE id = ?\", $searchTerm);\n")
		lines.append("\t\t\tif(count($r) == 1) {\n")
		lines.append("\t\t\t\t$r = $r[0];\n")
		lines.append("\t\t\t\treturn new "+self.name+"($r);\n")
		lines.append("\t\t\t} else {\n")
		lines.append("\t\t\t\treturn NULL;\n")
		lines.append("\t\t\t}\n")
		lines.append("\t\t} else {\n")
		lines.append("\t\t\t$vars = explode(\"&\", $searchTerm);\n")
		lines.append("\t\t\t$query = array();\n")
		lines.append("\t\t\tforeach($vars as $var) {\n")
		lines.append("\t\t\t\t$parts = explode(\"=\", $var);\n")
		lines.append("\t\t\t\t$query[$parts[0]] = $parts[1];\n")
		lines.append("\t\t\t}\n")
		lines.append("\t\t\t$where = array();\n")
		lines.append("\t\t\tforeach($query as $key => $val) {\n")
		lines.append("\t\t\t\tif(is_null($val) || $val == \"NULL\") {\n")
		lines.append("\t\t\t\t\tarray_push($where, $key.\" IS NULL\");\n")
		lines.append("\t\t\t\t} else {\n")
		lines.append("\t\t\t\t\tarray_push($where, $key.\" = ?\");\n")
		lines.append("\t\t\t\t}\n")
		lines.append("\t\t\t}\n")
		lines.append("\t\t\t$customdb = $db->custom();\n")
		lines.append("\t\t\t$pstmt = $customdb->prepare(\"SELECT id FROM `\".self::getTableName().\"` WHERE \".implode(\" AND \", $where));\n")
		lines.append("\t\t\t$i = 1;\n")
		lines.append("\t\t\tforeach($query as $key => $val) {\n")
		lines.append("\t\t\t\t$pstmt->bindValue($i++, $val, ((is_int($val) || ctype_digit($val)) ? PDO::PARAM_INT : PDO::PARAM_STR));\n")
		lines.append("\t\t\t}\n")
		lines.append("\t\t\t$pstmt->execute();\n")
		lines.append("\t\t\t$result = array();\n")
		lines.append("\t\t\tforeach($pstmt->fetchAll() as $row) {\n")
		lines.append("\t\t\t\tarray_push($result, "+self.name+"::find($row['id']));\n")
		lines.append("\t\t\t}\n")
		lines.append("\t\t\treturn $result;\n")
		lines.append("\t\t}\n")
		lines.append("\t}\n")

		lines.append("}\n")
		lines.append("?>\n")
		return ''.join(lines)

	def generatePHPController(self):
		lines = []
		return ''.join(lines)

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



