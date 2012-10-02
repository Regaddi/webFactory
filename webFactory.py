#!/bin/python3

import json, os, sys
from variable import Variable
from relation import Relation
from _class import _Class
from complexhandler import ComplexHandler

version = 1.2
classes = []


def getVariable():
	print("variable name:")
	name = input()
	if name == "":
		return None
	print("variable datatype: (b)oolean, date(t)ime, (d)ecimal, (i)nt, (s)tring, te(x)t, (o)ther")
	datatype = input().lower()
	if len(datatype) > 0:
		datatype = datatype[0]
	else:
		return None
	if datatype == "b":
		return Variable(name, "BOOLEAN")
	elif datatype == "t":
		return Variable(name, "DATETIME")
	elif datatype == "d":
		try:
			print("length:")
			decLength = int(input())
			print("decimal places:")
			decPlaces = int(input())
		except:
			print("unexpected input. canceled.")
			return None
		return Variable(name, "DECIMAL("+str(decLength)+","+str(decPlaces)+")")
	elif datatype == "i":
		return Variable(name, "INT")
	elif datatype == "s":
		print("length:")
		try:
			strLength = int(input())
		except:
			print("unexpected input. canceled.")
			return None
		return Variable(name, "VARCHAR("+str(strLength)+")")
	elif datatype == "x":
		return Variable(name, "TEXT")
	return None

def createRelation():
	print("choose class")
	for c in classes:
		print(c.name+" ["+str(classes.index(c))+"]")
	try:
		i = int(input())
		class1 = classes[i]
		print("choose relation")
		print("has many\t[0]")
		print("belongs to\t[1]")

		r = int(input())

		print("choose related class")
		for c in classes:
			print(c.name+" ["+str(classes.index(c))+"]")
		j = int(input())

		rel_str = 'has_many'
		if r == 1:
			rel_str = 'belongs_to'

		rel = Relation(classes[j].name, rel_str)

		classes[i].setRelation(rel)
	except:
		print("bad input")

def deleteRelation():
	print("choose relation")
	i = 0
	for c in classes:
		for r in c.relations:
			print(str(r)+" ["+str(i)+"]")
			i+=1

	try:
		chosen = int(input())
		i = 0
		for c in classes:
			j = 0
			for r in c.relations:
				if i == chosen:
					c.removeRelation(r)
					print("relation deleted")
				i+=1
	except:
		print("bad input")


def createClass():
	print("class name:")
	name = input()
	new_class = _Class(name,[],[])
	while 1 == 1:
		var = getVariable()
		if var != None:
			new_class.setVariable(var)
		else:
			break

	classes.append(new_class)

def modifyClass():
	print("choose class:")
	for c in classes:
		print("[",c.name,"]","("+str(classes.index(c))+")")
	i = input()
	if len(i) > 0:
		i = int(i)
	else:
		print("no class chosen.")
		return
	mod = classes[i]
	print("class name: (", mod.name, ")")
	name = input()
	if name != mod.name:
		if name != "":
			mod.name = name
		vars = mod.variables
		while 1 == 1:
			var = getVariable()
			if var != None:
				mod.setVariable(var)
			else:
				break
		print("do you wish to delete variables? [y/N]")
		answer = input()
		if len(answer) > 0 and answer[0].lower() == "y":
			sel = "a"
			while sel[0].lower() != "q":
				print("select variable to delete")
				for v in mod.variables:
					print(str(v)+"\t["+str(mod.variables.index(v))+"]")
				print("press 'q' to end")
				sel = input()
				if len(sel) > 0:
					try:
						if int(sel) >= 0 and int(sel) < len(mod.variables):
							if mod.variables[int(sel)].name == 'id':
								print("you can't delete id, because this system needs it")
							else:
								del mod.variables[int(sel)]
						else:
							print(sel+" is not in range")
					except:
						if sel[0].lower() != "q":
							print("bad input")
		classes[i] = mod

def deleteClass():
	print("choose class:")
	for c in classes:
		print("[",c.name,"]","("+str(classes.index(c))+")")
	try:
		i = int(input())
		del classes[i]
	except:
		print("bad input")

def printClass(i):
	print(classes[i])

def printClasses():
	if len(classes) == 0:
		print("\tNo classes defined.")
	for c in classes:
		print(c)

def produceMySQLScheme():
	global classes
	print("set mysql scheme (database):")
	scheme = input()
	lines = []
	lines.append("USE `"+scheme+"`;\n")

	for c in classes:
		lines.append("\nCREATE TABLE IF NOT EXISTS `"+c.name.lower()+"s` (\n")
		constraints = []
		isPrimary = False
		primary = None
		for v in c.variables:
			if v.name == "id":
				isPrimary = True
				primary = v.name
			lines.append("\t`"+v.name.lower()+"` "+v.datatype)
			if isPrimary == True:
				lines.append(" AUTO_INCREMENT")
			lines.append(",\n")
			isPrimary = False
		for r in c.relations:
			if r.relation == 'belongs_to':
				lines.append("\t`"+r.class_right.lower()+"_id` INT,\n")
				constraints.append("CONSTRAINT `fk_"+c.name.lower()+"_"+r.class_right.lower()+"` FOREIGN KEY (`"+r.class_right.lower()+"_id`) REFERENCES `"+r.class_right.lower()+"s` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,\n")
		lines.append("\t`created_at` DATETIME NOT NULL,\n")
		lines.append("\t`updated_at` DATETIME,\n")
		if primary != None:
			lines.append("\tPRIMARY KEY (`"+primary+"`),\n")
		if len(constraints) > 0:
			lines.append(''.join(constraints))
		lines[-1] = lines[-1][:-2]+"\n"

		lines.append(") ENGINE=InnoDB ")
		if primary != None:
			lines.append("AUTO_INCREMENT=1 ")
		lines.append("DEFAULT CHARSET=utf8;\n")

	return ''.join(lines)


def producePHPCode(c):
	lines = []
	lines.append("<?php\n\n/** generated with webFactory "+str(version)+" */\n\n")
	# begin
	lines.append("class "+c.name+" extends ActiveRecordModel {\n")

	# vars
	for v in c.variables:
		if v.name == "id":
			lines.append("\tpublic $id = 0;\n")
		else:
			lines.append("\tpublic $"+v.name+";\n")
	for r in c.relations:
		if r.relation == 'belongs_to':
			lines.append("\t// belongs to\n\tpublic $"+r.class_right.lower()+";\n")
		elif r.relation == 'has_many':
			lines.append("\t// has many\n\tpublic $"+r.class_right.lower()+"s;\n")

	# getTableName
	lines.append("\n\tpublic static function getTableName() {\n")
	lines.append("\t\treturn '"+c.name.lower()+"s';\n")
	lines.append("\t}\n")

	for r in c.relations:
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
			lines.append("\t\t\treturn "+c.name+"::find('"+r.class_right.lower()+"_id='.$"+parent+");\n")
			lines.append("\t\t} elseif(get_class($"+parent+") == '"+r.class_right+"') {\n")
			lines.append("\t\t\treturn "+c.name+"::find('"+r.class_right.lower()+"_id='.$"+parent+"->id);\n")
			lines.append("\t\t}\n")
			lines.append("\t}\n")


	# static functions
	# all()
	lines.append("\n\tpublic static function all() {\n")
	lines.append("\t\t$result = array();\n")
	lines.append("\t\t$db = new DB();\n")
	lines.append("\t\t$rows = $db->preparedStatement(\"SELECT * FROM `\".self::getTableName().\"`\");\n")
	lines.append("\t\tforeach($rows as $r) {\n")
	lines.append("\t\t\tarray_push($result, new "+c.name+"($r));\n")
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
	lines.append("\t\t\t\treturn new "+c.name+"($r);\n")
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
	lines.append("\t\t\t\tarray_push($result, "+c.name+"::find($row['id']));\n")
	lines.append("\t\t\t}\n")
	lines.append("\t\t\treturn $result;\n")
	lines.append("\t\t}\n")
	lines.append("\t}\n")

	lines.append("}\n")
	lines.append("?>\n")
	return ''.join(lines)

def produceActiveRecordModelClass():
	lines = []
	lines.append("<?php\n\n/** generated with webFactory "+str(version)+" */\n\n")
	lines.append("class ActiveRecordModel {\n")

	# __construct
	lines.append("\tpublic function __construct($vars) {\n")
	lines.append("\t\tif(is_array($vars) && count($vars) > 0) {\n")
	lines.append("\t\t\tforeach($vars as $prop => $val) {\n")
	lines.append("\t\t\t\t$prop = substr($prop, -3) == \"_id\" ? substr($prop, 0, -3) : $prop;\n")
	lines.append("\t\t\t\tif(property_exists($this, $prop)) {\n")
	lines.append("\t\t\t\t\t$prop_class = $prop.'_class';\n")
	lines.append("\t\t\t\t\tif(property_exists($this, $prop_class)) {\n")
	lines.append("\t\t\t\t\t\t$classname = $this->$prop_class;\n")
	lines.append("\t\t\t\t\t\tif(property_exists($this, 'has_many_'.strtolower($this->$prop_class))) {\n")
	lines.append("\t\t\t\t\t\t\t$this->$prop = $classname::find_by_parent($this);\n")
	lines.append("\t\t\t\t\t\t} elseif(property_exists($this, 'belongs_to_'.strtolower($this->$prop_class))) {\n")
	lines.append("\t\t\t\t\t\t\t$this->$prop = (int)$val;\n")
	lines.append("\t\t\t\t\t\t}\n")
	lines.append("\t\t\t\t\t} else $this->$prop = $val;\n")
	lines.append("\t\t\t\t}\n")
	lines.append("\t\t\t}\n")
	lines.append("\t\t\tforeach(get_object_vars($this) as $prop => $val) {\n")
	lines.append("\t\t\t\tif(strstr($prop, 'has_many_') && is_bool($this->$prop)) {\n")
	lines.append("\t\t\t\t\t$class = $this->{substr($prop, 9).'_class'};\n")
	lines.append("\t\t\t\t\t$prop_var = static::${'has_many_'.strtolower($class).'_var'};\n")
	lines.append("\t\t\t\t\t$this->$prop_var = $class::find_by_parent($this);\n")
	lines.append("\t\t\t\t}\n")
	lines.append("\t\t\t}\n")
	lines.append("\t\t}\n")
	lines.append("\t\t$this->id = (int)$this->id;\n")
	lines.append("\t}\n\n")
	
	# find_by_parent
	lines.append("\tpublic static function find_by_parent($obj) {\n")
	lines.append("\t\t$var = 'belongs_to_'.strtolower(get_class($obj)).'_var';\n")
	lines.append("\t\tif(static::$$var) {\n")
	lines.append("\t\t\t$bvar = 'belongs_to_'.strtolower(get_class($obj)).'_var';\n")
	lines.append("\t\t\treturn static::find(static::$$bvar.'_id='.$obj->id);\n")
	lines.append("\t\t}\n")
	lines.append("\t\treturn NULL;\n")
	lines.append("\t}\n\n")

	# singleize
	lines.append("\tpublic function singleize() {\n")
	lines.append("\t\tforeach(get_object_vars($this) as $prop => $val) {\n")
	lines.append("\t\t\tif(substr($prop, 0, 9) == 'has_many_') {\n")
	lines.append("\t\t\t\t$this->$prop = array();\n")
	lines.append("\t\t\t}\n")
	lines.append("\t\t}\n");
	lines.append("\t}\n\n")

	# create
	lines.append("\tpublic static function create($vars) {\n")
	lines.append("\t\t$class = get_called_class();\n")
	lines.append("\t\t$obj = new $class($vars);\n")
	lines.append("\t\t$obj->save();\n")
	lines.append("\t\treturn $obj;\n")
	lines.append("\t}\n\n")

	# update_attributes

	lines.append("\tpublic function update_attributes($vars) {\n")
	lines.append("\t\tif(is_array($vars) && count($vars) > 0) {\n")
	lines.append("\t\t\tforeach($vars as $prop => $val) {\n")
	lines.append("\t\t\t\tif(property_exists($this, $prop)) {\n")
	lines.append("\t\t\t\t\t$this->$prop = $val;\n")
	lines.append("\t\t\t\t}\n")
	lines.append("\t\t\t}\n")
	lines.append("\t\t\t$this->save();\n")
	lines.append("\t\t}\n")
	lines.append("\t\treturn $this;\n")
	lines.append("\t}\n\n")

	# save
	lines.append("\tpublic function save() {\n")
	lines.append("\t\tif(property_exists($this, 'id')) {\n")
	lines.append("\t\t\t$db = new DB();\n")
	lines.append("\t\t\tif($this->id > 0) {\n")
	lines.append("\t\t\t\t$dbc = $db->custom();\n")
	lines.append("\t\t\t\t$fields = array();\n")
	lines.append("\t\t\t\tforeach(get_object_vars($this) as $prop => $val) {\n")
	lines.append("\t\t\t\t\tif($prop != \"id\") {\n")
	lines.append("\t\t\t\t\t\tif(property_exists($this, $prop.'_class')) {\n")
	lines.append("\t\t\t\t\t\t\t$prop_class = $prop.'_class';\n")
	lines.append("\t\t\t\t\t\t\t$check_has_many = 'has_many_'.strtolower($this->$prop_class).'s';\n")
	lines.append("\t\t\t\t\t\t\tif(property_exists($this, $check_has_many) && $this->$check_has_many) continue;\n")
	lines.append("\t\t\t\t\t\t}\n")
	lines.append("\t\t\t\t\t\tarray_push($fields, $prop.\" = :\".$prop);\n")
	lines.append("\t\t\t\t\t}\n")
	lines.append("\t\t\t\t}\n")
	lines.append("\t\t\t\t$stmt = \"UPDATE `\".static::getTableName().\"` SET \".implode(\", \", $fields).\", updated_at = NOW() WHERE id = :id\";\n")
	lines.append("\t\t\t\t$sth = $dbc->prepare($stmt);\n")
	lines.append("\t\t\t\tforeach(get_object_vars($this) as $prop => $val) {\n")
	lines.append("\t\t\t\t\tif($prop != \"id\") $sth->bindValue(\":\".$prop, $val, is_int($val) ? PDO::PARAM_INT : PDO::PARAM_STR);\n")
	lines.append("\t\t\t\t}\n")
	lines.append("\t\t\t\t$sth->bindValue(':id', $this->id);\n")
	lines.append("\t\t\t\t$sth->execute();\n")
	lines.append("\t\t\t} else {\n")
	lines.append("\t\t\t\t$dbc = $db->custom();\n")
	lines.append("\t\t\t\t$cols = array();\n")
	lines.append("\t\t\t\t$vals = array();\n")
	lines.append("\t\t\t\tforeach(get_object_vars($this) as $prop => $val) {\n")
	lines.append("\t\t\t\t\tif($prop != \"id\") {\n")
	lines.append("\t\t\t\t\t\tif(property_exists($this, $prop.'_class')) {\n")
	lines.append("\t\t\t\t\t\t\t$prop_class = $prop.'_class';\n")
	lines.append("\t\t\t\t\t\t\t$check_has_many = 'has_many_'.strtolower($this->$prop_class).'s';\n")
	lines.append("\t\t\t\t\t\t\tif(property_exists($this, $check_has_many) && $this->$check_has_many) continue;\n")
	lines.append("\t\t\t\t\t\t\t$check_belongs_to = 'belongs_to_'.strtolower($this->$prop_class);\n")
	lines.append("\t\t\t\t\t\t\tif(property_exists($this, $check_belongs_to) && $this->$check_belongs_to) {\n")
	lines.append("\t\t\t\t\t\t\t\tarray_push($cols, $prop.\"_id\");\n")
	lines.append("\t\t\t\t\t\t\t\tarray_push($vals, \":\".$prop);\n")
	lines.append("\t\t\t\t\t\t\t}\n")
	lines.append("\t\t\t\t\t\t} else {\n")
	lines.append("\t\t\t\t\t\t\tif(!strstr($prop, \"has_many_\") && !strstr($prop, \"_class\") && !strstr($prop, \"belongs_to_\")) {\n")
	lines.append("\t\t\t\t\t\t\t\tarray_push($cols, $prop);\n")
	lines.append("\t\t\t\t\t\t\t\tarray_push($vals, \":\".$prop);\n")
	lines.append("\t\t\t\t\t\t\t}\n")
	lines.append("\t\t\t\t\t\t}\n")
	lines.append("\t\t\t\t\t}\n")
	lines.append("\t\t\t\t}\n")
	lines.append("\t\t\t\t$stmt = \"INSERT INTO `\".static::getTableName().\"` (\".implode(\", \", $cols).\", created_at) VALUES (\".implode(\", \", $vals).\", NOW())\";\n")
	lines.append("\t\t\t\t$sth = $dbc->prepare($stmt);\n")
	lines.append("\t\t\t\tforeach(get_object_vars($this) as $prop => $val) {\n")
	lines.append("\t\t\t\t\tif($prop != 'id') {\n")
	lines.append("\t\t\t\t\t\tif(property_exists($this, $prop.'_class')) {\n")
	lines.append("\t\t\t\t\t\t\t$prop_class = $prop.'_class';\n")
	lines.append("\t\t\t\t\t\t\t$check_has_many = 'has_many_'.strtolower($this->$prop_class).'s';\n")
	lines.append("\t\t\t\t\t\t\tif(property_exists($this, $check_has_many) && $this->$check_has_many) continue;\n")
	lines.append("\t\t\t\t\t\t\t$check_belongs_to = 'belongs_to_'.strtolower($this->$prop_class);\n")
	lines.append("\t\t\t\t\t\t\tif(property_exists($this, $check_belongs_to) && $this->$check_belongs_to) {\n")
	lines.append("\t\t\t\t\t\t\t\t$sth->bindValue(':'.$prop, $val->id, is_int($val->id) ? PDO::PARAM_INT : PDO::PARAM_STR);\n")
	lines.append("\t\t\t\t\t\t\t}\n")
	lines.append("\t\t\t\t\t\t} else {\n")
	lines.append("\t\t\t\t\t\t\tif(!strstr($prop, \"has_many_\") && !strstr($prop, \"_class\") && !strstr($prop, \"belongs_to_\")) {\n")
	lines.append("\t\t\t\t\t\t\t\t$sth->bindValue(':'.$prop, $val, is_int($val) ? PDO::PARAM_INT : is_null($val) ? PDO::PARAM_NULL : PDO::PARAM_STR);\n")
	lines.append("\t\t\t\t\t\t\t}\n")
	lines.append("\t\t\t\t\t\t}\n")
	lines.append("\t\t\t\t\t}\n")
	lines.append("\t\t\t\t}\n")
	lines.append("\t\t\t\t$sth->execute();\n")
	lines.append("\t\t\t\t$this->id = $db->lastInsertId(static::getTableName());\n")
	lines.append("\t\t\t}\n")
	lines.append("\t\t}\n")
	lines.append("\t}\n\n")

	# delete
	lines.append("\tpublic function delete() {\n")
	lines.append("\t\tif(property_exists($this, 'id')) {\n")
	lines.append("\t\t\t$db = new DB();\n")
	lines.append("\t\t\t$db->preparedStatement(\"DELETE FROM `\".$this->getTableName().\"` WHERE id = ?\", $this->id);\n")
	lines.append("\t\t}\n")
	lines.append("\t}\n")

	lines.append("}\n")
	lines.append("?>\n")
	return ''.join(lines)

def produceDBClass():
	lines = []
	lines.append("<?php\n\n/** generated with webFactory "+str(version)+" */\n\n")
	lines.append("class DB {\n")
	lines.append("\tprivate $host = 'localhost';\n")
	lines.append("\tprivate $user = 'mysql_user';\n")
	lines.append("\tprivate $pass = 'mysql_pass';\n")
	lines.append("\tprivate $scheme = 'mysql_scheme';\n")
	lines.append("\tprivate $port = 3306;\n")
	lines.append("\tprivate $db = NULL;\n")

	# connect
	lines.append("\n\tpublic function __construct() {\n")
	lines.append("\t\ttry {\n")
	lines.append("\t\t\t$this->db = new PDO(\n")
	lines.append("\t\t\t\t'mysql:host='.$this->host.';dbname='.$this->scheme.';port='.$this->port.';charset=UTF-8',\n")
	lines.append("\t\t\t\t$this->user,\n")
	lines.append("\t\t\t\t$this->pass,\n")
	lines.append("\t\t\t\tarray(\n")
	lines.append("\t\t\t\t\tPDO::ATTR_PERSISTENT => true,\n")
	lines.append("\t\t\t\t\tPDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,\n")
	lines.append("\t\t\t\t\tPDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,\n")
	lines.append("\t\t\t\t\tPDO::MYSQL_ATTR_INIT_COMMAND => \"SET NAMES utf8\"\n")
	lines.append("\t\t\t\t)\n")
	lines.append("\t\t\t);\n")
	lines.append("\t\t} catch(PDOException $e) {\n")
	lines.append("\t\t\tdie($e->getMessage());\n")
	lines.append("\t\t}\n")
	lines.append("\t}\n")

	# close
	lines.append("\n\tpublic function close() {\n")
	lines.append("\t\t$this->db = NULL;\n")
	lines.append("\t}\n")

	# custom operations
	lines.append("\n\tpublic function custom() {\n")
	lines.append("\t\treturn $this->db;\n")
	lines.append("\t}\n")

	# preparedStatement
	lines.append("\n\tpublic function preparedStatement($stmt) {\n")
	lines.append("\t\ttry {\n")
	lines.append("\t\t\t$queryType = NULL;\n")
	lines.append("\t\t\tif(substr_compare($stmt, \"select\", 0, 6, TRUE) == 0) {\n")
	lines.append("\t\t\t\t$queryType = \"select\";\n")
	lines.append("\t\t\t}\n")
	lines.append("\t\t\tif(substr_compare($stmt, \"update\", 0, 6, TRUE) == 0) {\n")
	lines.append("\t\t\t\t$queryType = \"update\"; \n")
	lines.append("\t\t\t}\n")
	lines.append("\t\t\tif(substr_compare($stmt, \"delete\", 0, 6, TRUE) == 0) {\n")
	lines.append("\t\t\t\t$queryType = \"delete\";\n")
	lines.append("\t\t\t}\n")
	lines.append("\t\t\tif(substr_compare($stmt, \"insert\", 0, 6, TRUE) == 0) {\n")
	lines.append("\t\t\t\t$queryType = \"insert\";\n")
	lines.append("\t\t\t}\n")
	lines.append("\t\t\t// check number of parameters\n")
	lines.append("\t\t\tif(substr_count($stmt, \"?\") == func_num_args()-1) {\n")
	lines.append("\t\t\t\t$pstmt = $this->db->prepare($stmt);\n")
	lines.append("\t\t\t\t// bind all parameters\n")
	lines.append("\t\t\t\tfor($c = 1; $c < func_num_args(); $c++) {\n")
	lines.append("\t\t\t\t\t$p = func_get_arg($c);\n")
	lines.append("\t\t\t\t\tif(is_int($p)) {\n")
	lines.append("\t\t\t\t\t\t$pstmt->bindValue($c, $p, PDO::PARAM_INT);\n")
	lines.append("\t\t\t\t\t}\n")
	lines.append("\t\t\t\t\telseif(is_null($p)) {\n")
	lines.append("\t\t\t\t\t\t$pstmt->bindValue($c, $p, PDO::PARAM_NULL);\n")
	lines.append("\t\t\t\t\t}\n")
	lines.append("\t\t\t\t\telse {\n")
	lines.append("\t\t\t\t\t\t$pstmt->bindValue($c, $p, PDO::PARAM_STR);\n")
	lines.append("\t\t\t\t\t}\n")
	lines.append("\t\t\t\t}\n")
	lines.append("\t\t\t\t$pstmt->execute();\n")
	lines.append("\t\t\t\tif($pstmt->rowCount() > 0) {\n")
	lines.append("\t\t\t\t\tif($queryType == \"select\") {\n")
	lines.append("\t\t\t\t\t\treturn $pstmt->fetchAll();\n")
	lines.append("\t\t\t\t\t} else {\n")
	lines.append("\t\t\t\t\t\treturn $pstmt->rowCount();\n")
	lines.append("\t\t\t\t\t}\n")
	lines.append("\t\t\t\t} else {\n")
	lines.append("\t\t\t\t\treturn NULL;\n")
	lines.append("\t\t\t\t}\n")
	lines.append("\t\t\t}\n")
	lines.append("\t\t} catch(PDOException $e) {\n")
	lines.append("\t\t\tdie($e->getMessage());\n")
	lines.append("\t\t}\n")
	lines.append("\t}\n")

	# lastInsertId
	lines.append("\n\tpublic function lastInsertId($table) {\n")
	lines.append("\t\ttry {\n")
	lines.append("\t\t\t$stmt = $this->db->prepare(\"SELECT LAST_INSERT_ID() as id FROM `\".$table.\"`\");\n")
	lines.append("\t\t\t$stmt->execute();\n")
	lines.append("\t\t\t$id = $stmt->fetch();\n")
	lines.append("\t\t\treturn (int)$id['id'];\n")
	lines.append("\t\t} catch(PDOException $e) {\n")
	lines.append("\t\t\tdie($e->getMessage());\n")
	lines.append("\t\t}\n")
	lines.append("\t}\n")

	lines.append("}\n")
	lines.append("?>\n")
	return ''.join(lines)

def generateFiles():
	print("set output path:")
	path = input()

	if not os.path.exists(path):
		os.makedirs(path)

	armclass = produceActiveRecordModelClass()
	try:
		d = open(path+"/ActiveRecordModel.class.php","w")
	except:
		print("Could not open file! (ActiveRecordModel-Class)")
		return
	d.write(armclass)
	d.close()

	for c in classes:
		phpcode = producePHPCode(c)
		try:
			d = open(path+"/"+c.name.lower()+".class.php","w")
		except:
			print("Could not open file! (Class ",c.name,")")
			return
		d.write(phpcode)
		d.close();

	dbclass = produceDBClass()
	try:
		d = open(path+"/db.class.php","w")
	except:
		print("Could not open file! (DB-Class)")
		return
	d.write(dbclass)
	d.close()


	mysql = produceMySQLScheme()
	try:
		d = open(path+"/scheme.sql","w")
	except:
		print("Could not open file! (scheme.sql)")
		return
	d.write(mysql)
	d.close()


def importClasses():
	global classes
	print("path to file:")
	path = input()
	try:
		f = open(path, "r")
	except:
		print("Could not open file '"+path+"'")
		return
	cache = json.load(f)
	f.close()
	classes = []
	for c in cache:
		variables = []
		relations = []
		for v in c['variables']:
			variables.append(Variable(v['name'], v['datatype']))
		for r in c['relations']:
			relations.append(Relation(r['class_right'], r['relation']))
		classes.append(_Class(c['name'], variables, relations))
	print("Imported:")
	printClasses()

def exportClasses():
	print("path to file:")
	path = input()+".wfx"

	with open(path, mode='w', encoding='utf-8') as f:
		out = json.dumps(classes, default=ComplexHandler)
		f.write(out)

def loopInput():
	print("action: edit (c)lasses, edit (r)elations, (p)rint, (i)mport, (e)xport, (g)enerate files, (q)uit")
	char = " "
	try:
		char = input().lower()[0]
	except:
		print("bad input")
	if char == "c":
		print("(c)reate, (m)odify, (d)elete, (b)ack")
		try:
			char2 = input().lower()[0]
			if char2 == "c":
				createClass()
			elif char2 == "m":
				modifyClass()
			elif char2 == "d":
				deleteClass()
			else:
				print("")
		except:
			print("bad input")
	elif char == "r":
		print("(c)reate, (d)elete, (b)ack")
		try:
			char2 = input().lower()[0]
			if char2 == "c":
				createRelation()
			elif char2 == "d":
				deleteRelation()
			else:
				print("")
		except:
			print("bad input")
	elif char == "p":
		printClasses()
	elif char == "i":
		importClasses()
	elif char == "e":
		exportClasses()
	elif char == "g":
		generateFiles()
	elif char == "q":
		sys.exit(0)
	else:
		print("")
	loopInput()

print("webFactory",str(version))

loopInput()