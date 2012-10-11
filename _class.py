from variable import Variable
from relation import Relation
from _vars import version

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
		lines.append("<?php")
		lines.append("/** generated with webFactory "+str(version)+" */")
		# begin
		lines.append("class "+self.name+" extends ActiveRecordModel {")

		# vars
		for v in self.variables:
			if v.name == "id":
				lines.append("\tpublic $id = 0;")
			else:
				lines.append("\tpublic $"+v.name+";")
		for r in self.relations:
			if r.relation == 'belongs_to':
				lines.append("\t// belongs to\n\tpublic $"+r.class_right.lower()+";")
			elif r.relation == 'has_many':
				lines.append("\t// has many\n\tpublic $"+r.class_right.lower()+"s;")

		# getTableName
		lines.append("\n\tpublic static function getTableName() {")
		lines.append("\t\treturn '"+self.name.lower()+"s';")
		lines.append("\t}")

		for r in self.relations:
			if r.relation == 'has_many':
				# has_many_class
				lines.append("\tprotected $has_many_"+r.class_right.lower()+"s = TRUE;");
				# has_many_var
				lines.append("\tprotected static $has_many_"+r.class_right.lower()+"s_var = '"+r.class_right.lower()+"s';");
				# class_var
				lines.append("\tprotected $"+r.class_right.lower()+"s_class = '"+r.class_right+"';");

				# get child by index
				funcName = "get"+r.class_right+"ByIndex"
				lines.append("\tpublic function "+funcName+"($index) {")
				lines.append("\t\treturn $this->"+r.class_right.lower()+"s[$index];")
				lines.append("\t}")
			elif r.relation == 'belongs_to':
				# belongs_to_class
				lines.append("\tprotected $belongs_to_"+r.class_right.lower()+" = TRUE;");
				# belongs_to_var
				lines.append("\tprotected static $belongs_to_"+r.class_right.lower()+"_var = '"+r.class_right.lower()+"';");
				# class_var
				lines.append("\tprotected $"+r.class_right.lower()+"_class = '"+r.class_right+"';");

				# get parent
				funcName = "get"+r.class_right
				lines.append("\tpublic function "+funcName+"() {")
				lines.append("\t\treturn "+r.class_right+"::find($this->"+r.class_right.lower()+");")
				lines.append("\t}")

				# get by parent or parent id
				funcName = "find_by_"+r.class_right.lower()
				parent = r.class_right.lower()
				lines.append("\tpublic function "+funcName+"($"+parent+") {")
				lines.append("\t\tif(is_int($"+parent+") || is_numeric($"+parent+")) {")
				lines.append("\t\t\treturn "+self.name+"::find('"+r.class_right.lower()+"_id='.$"+parent+");")
				lines.append("\t\t} elseif(get_class($"+parent+") == '"+r.class_right+"') {")
				lines.append("\t\t\treturn "+self.name+"::find('"+r.class_right.lower()+"_id='.$"+parent+"->id);")
				lines.append("\t\t}")
				lines.append("\t}")


		# static functions
		# all()
		lines.append("\tpublic static function all() {")
		lines.append("\t\t$result = array();")
		lines.append("\t\t$db = new DB();")
		lines.append("\t\t$rows = $db->preparedStatement(\"SELECT * FROM `\".self::getTableName().\"`\");")
		lines.append("\t\tforeach($rows as $r) {")
		lines.append("\t\t\tarray_push($result, new "+self.name+"($r));")
		lines.append("\t\t}")
		lines.append("\t\t$db->close();")
		lines.append("\t\treturn $result;")
		lines.append("\t}")

		# find()
		lines.append("\tpublic static function find($searchTerm) {")
		lines.append("\t\t$db = new DB();")
		lines.append("\t\tif(is_numeric($searchTerm)) {")
		lines.append("\t\t\t$r = $db->preparedStatement(\"SELECT * FROM `\".self::getTableName().\"` WHERE id = ?\", $searchTerm);")
		lines.append("\t\t\tif(count($r) == 1) {")
		lines.append("\t\t\t\t$r = $r[0];")
		lines.append("\t\t\t\treturn new "+self.name+"($r);")
		lines.append("\t\t\t} else {")
		lines.append("\t\t\t\treturn NULL;")
		lines.append("\t\t\t}")
		lines.append("\t\t} else {")
		lines.append("\t\t\t$vars = explode(\"&\", $searchTerm);")
		lines.append("\t\t\t$query = array();")
		lines.append("\t\t\tforeach($vars as $var) {")
		lines.append("\t\t\t\t$parts = explode(\"=\", $var);")
		lines.append("\t\t\t\t$query[$parts[0]] = $parts[1];")
		lines.append("\t\t\t}")
		lines.append("\t\t\t$where = array();")
		lines.append("\t\t\tforeach($query as $key => $val) {")
		lines.append("\t\t\t\tif(is_null($val) || $val == \"NULL\") {")
		lines.append("\t\t\t\t\tarray_push($where, $key.\" IS NULL\");")
		lines.append("\t\t\t\t} else {")
		lines.append("\t\t\t\t\tarray_push($where, $key.\" = ?\");")
		lines.append("\t\t\t\t}")
		lines.append("\t\t\t}")
		lines.append("\t\t\t$customdb = $db->custom();")
		lines.append("\t\t\t$pstmt = $customdb->prepare(\"SELECT id FROM `\".self::getTableName().\"` WHERE \".implode(\" AND \", $where));")
		lines.append("\t\t\t$i = 1;")
		lines.append("\t\t\tforeach($query as $key => $val) {")
		lines.append("\t\t\t\t$pstmt->bindValue($i++, $val, ((is_int($val) || ctype_digit($val)) ? PDO::PARAM_INT : PDO::PARAM_STR));")
		lines.append("\t\t\t}")
		lines.append("\t\t\t$pstmt->execute();")
		lines.append("\t\t\t$result = array();")
		lines.append("\t\t\tforeach($pstmt->fetchAll() as $row) {")
		lines.append("\t\t\t\tarray_push($result, "+self.name+"::find($row['id']));")
		lines.append("\t\t\t}")
		lines.append("\t\t\treturn $result;")
		lines.append("\t\t}")
		lines.append("\t}")

		lines.append("}")
		lines.append("?>")
		return '\n'.join(lines)

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



