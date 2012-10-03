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
	lines.append("USE `"+scheme+"`;")

	for c in classes:
		lines.append("CREATE TABLE IF NOT EXISTS `"+c.name.lower()+"s` (")
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
			lines.append(",")
			isPrimary = False
		for r in c.relations:
			if r.relation == 'belongs_to':
				lines.append("\t`"+r.class_right.lower()+"_id` INT,")
				constraints.append("CONSTRAINT `fk_"+c.name.lower()+"_"+r.class_right.lower()+"` FOREIGN KEY (`"+r.class_right.lower()+"_id`) REFERENCES `"+r.class_right.lower()+"s` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,")
		lines.append("\t`created_at` DATETIME NOT NULL,")
		lines.append("\t`updated_at` DATETIME,")
		if primary != None:
			lines.append("\tPRIMARY KEY (`"+primary+"`),")
		if len(constraints) > 0:
			lines.append(''.join(constraints))
		lines[-1] = lines[-1][:-2]+""

		lines.append(") ENGINE=InnoDB ")
		if primary != None:
			lines.append("AUTO_INCREMENT=1 ")
		lines.append("DEFAULT CHARSET=utf8;")

	return '\n'.join(lines)
	

def produceActiveRecordModelClass():
	lines = []
	lines.append("<?php")
	lines.append("/** generated with webFactory "+str(version)+" */")
	lines.append("class ActiveRecordModel {")

	# __construct
	lines.append("\tpublic function __construct($vars) {")
	lines.append("\t\tif(is_array($vars) && count($vars) > 0) {")
	lines.append("\t\t\tforeach($vars as $prop => $val) {")
	lines.append("\t\t\t\t$prop = substr($prop, -3) == \"_id\" ? substr($prop, 0, -3) : $prop;")
	lines.append("\t\t\t\tif(property_exists($this, $prop)) {")
	lines.append("\t\t\t\t\t$prop_class = $prop.'_class';")
	lines.append("\t\t\t\t\tif(property_exists($this, $prop_class)) {")
	lines.append("\t\t\t\t\t\t$classname = $this->$prop_class;")
	lines.append("\t\t\t\t\t\tif(property_exists($this, 'has_many_'.strtolower($this->$prop_class))) {")
	lines.append("\t\t\t\t\t\t\t$this->$prop = $classname::find_by_parent($this);")
	lines.append("\t\t\t\t\t\t} elseif(property_exists($this, 'belongs_to_'.strtolower($this->$prop_class))) {")
	lines.append("\t\t\t\t\t\t\t$this->$prop = (int)$val;")
	lines.append("\t\t\t\t\t\t}")
	lines.append("\t\t\t\t\t} else $this->$prop = $val;")
	lines.append("\t\t\t\t}")
	lines.append("\t\t\t}")
	lines.append("\t\t\tforeach(get_object_vars($this) as $prop => $val) {")
	lines.append("\t\t\t\tif(strstr($prop, 'has_many_') && is_bool($this->$prop)) {")
	lines.append("\t\t\t\t\t$class = $this->{substr($prop, 9).'_class'};")
	lines.append("\t\t\t\t\t$prop_var = static::${'has_many_'.strtolower($class).'_var'};")
	lines.append("\t\t\t\t\t$this->$prop_var = $class::find_by_parent($this);")
	lines.append("\t\t\t\t}")
	lines.append("\t\t\t}")
	lines.append("\t\t}")
	lines.append("\t\t$this->id = (int)$this->id;")
	lines.append("\t}\n")
	
	# find_by_parent
	lines.append("\tpublic static function find_by_parent($obj) {")
	lines.append("\t\t$var = 'belongs_to_'.strtolower(get_class($obj)).'_var';")
	lines.append("\t\tif(static::$$var) {")
	lines.append("\t\t\t$bvar = 'belongs_to_'.strtolower(get_class($obj)).'_var';")
	lines.append("\t\t\treturn static::find(static::$$bvar.'_id='.$obj->id);")
	lines.append("\t\t}")
	lines.append("\t\treturn NULL;")
	lines.append("\t}\n")

	# singleize
	lines.append("\tpublic function singleize() {")
	lines.append("\t\tforeach(get_object_vars($this) as $prop => $val) {")
	lines.append("\t\t\tif(substr($prop, 0, 9) == 'has_many_') {")
	lines.append("\t\t\t\t$this->$prop = array();")
	lines.append("\t\t\t}")
	lines.append("\t\t}");
	lines.append("\t}\n")

	# create
	lines.append("\tpublic static function create($vars) {")
	lines.append("\t\t$class = get_called_class();")
	lines.append("\t\t$obj = new $class($vars);")
	lines.append("\t\t$obj->save();")
	lines.append("\t\treturn $obj;")
	lines.append("\t}\n")

	# update_attributes

	lines.append("\tpublic function update_attributes($vars) {")
	lines.append("\t\tif(is_array($vars) && count($vars) > 0) {")
	lines.append("\t\t\tforeach($vars as $prop => $val) {")
	lines.append("\t\t\t\tif(property_exists($this, $prop)) {")
	lines.append("\t\t\t\t\t$this->$prop = $val;")
	lines.append("\t\t\t\t}")
	lines.append("\t\t\t}")
	lines.append("\t\t\t$this->save();")
	lines.append("\t\t}")
	lines.append("\t\treturn $this;")
	lines.append("\t}\n")

	# save
	lines.append("\tpublic function save() {")
	lines.append("\t\tif(property_exists($this, 'id')) {")
	lines.append("\t\t\t$db = new DB();")
	lines.append("\t\t\tif($this->id > 0) {")
	lines.append("\t\t\t\t$dbc = $db->custom();")
	lines.append("\t\t\t\t$fields = array();")
	lines.append("\t\t\t\tforeach(get_object_vars($this) as $prop => $val) {")
	lines.append("\t\t\t\t\tif($prop != \"id\") {")
	lines.append("\t\t\t\t\t\tif(property_exists($this, $prop.'_class')) {")
	lines.append("\t\t\t\t\t\t\t$prop_class = $prop.'_class';")
	lines.append("\t\t\t\t\t\t\t$check_has_many = 'has_many_'.strtolower($this->$prop_class).'s';")
	lines.append("\t\t\t\t\t\t\tif(property_exists($this, $check_has_many) && $this->$check_has_many) continue;")
	lines.append("\t\t\t\t\t\t}")
	lines.append("\t\t\t\t\t\tarray_push($fields, $prop.\" = :\".$prop);")
	lines.append("\t\t\t\t\t}")
	lines.append("\t\t\t\t}")
	lines.append("\t\t\t\t$stmt = \"UPDATE `\".static::getTableName().\"` SET \".implode(\", \", $fields).\", updated_at = NOW() WHERE id = :id\";")
	lines.append("\t\t\t\t$sth = $dbc->prepare($stmt);")
	lines.append("\t\t\t\tforeach(get_object_vars($this) as $prop => $val) {")
	lines.append("\t\t\t\t\tif($prop != \"id\") $sth->bindValue(\":\".$prop, $val, is_int($val) ? PDO::PARAM_INT : PDO::PARAM_STR);")
	lines.append("\t\t\t\t}")
	lines.append("\t\t\t\t$sth->bindValue(':id', $this->id);")
	lines.append("\t\t\t\t$sth->execute();")
	lines.append("\t\t\t} else {")
	lines.append("\t\t\t\t$dbc = $db->custom();")
	lines.append("\t\t\t\t$cols = array();")
	lines.append("\t\t\t\t$vals = array();")
	lines.append("\t\t\t\tforeach(get_object_vars($this) as $prop => $val) {")
	lines.append("\t\t\t\t\tif($prop != \"id\") {")
	lines.append("\t\t\t\t\t\tif(property_exists($this, $prop.'_class')) {")
	lines.append("\t\t\t\t\t\t\t$prop_class = $prop.'_class';")
	lines.append("\t\t\t\t\t\t\t$check_has_many = 'has_many_'.strtolower($this->$prop_class).'s';")
	lines.append("\t\t\t\t\t\t\tif(property_exists($this, $check_has_many) && $this->$check_has_many) continue;")
	lines.append("\t\t\t\t\t\t\t$check_belongs_to = 'belongs_to_'.strtolower($this->$prop_class);")
	lines.append("\t\t\t\t\t\t\tif(property_exists($this, $check_belongs_to) && $this->$check_belongs_to) {")
	lines.append("\t\t\t\t\t\t\t\tarray_push($cols, $prop.\"_id\");")
	lines.append("\t\t\t\t\t\t\t\tarray_push($vals, \":\".$prop);")
	lines.append("\t\t\t\t\t\t\t}")
	lines.append("\t\t\t\t\t\t} else {")
	lines.append("\t\t\t\t\t\t\tif(!strstr($prop, \"has_many_\") && !strstr($prop, \"_class\") && !strstr($prop, \"belongs_to_\")) {")
	lines.append("\t\t\t\t\t\t\t\tarray_push($cols, $prop);")
	lines.append("\t\t\t\t\t\t\t\tarray_push($vals, \":\".$prop);")
	lines.append("\t\t\t\t\t\t\t}")
	lines.append("\t\t\t\t\t\t}")
	lines.append("\t\t\t\t\t}")
	lines.append("\t\t\t\t}")
	lines.append("\t\t\t\t$stmt = \"INSERT INTO `\".static::getTableName().\"` (\".implode(\", \", $cols).\", created_at) VALUES (\".implode(\", \", $vals).\", NOW())\";")
	lines.append("\t\t\t\t$sth = $dbc->prepare($stmt);")
	lines.append("\t\t\t\tforeach(get_object_vars($this) as $prop => $val) {")
	lines.append("\t\t\t\t\tif($prop != 'id') {")
	lines.append("\t\t\t\t\t\tif(property_exists($this, $prop.'_class')) {")
	lines.append("\t\t\t\t\t\t\t$prop_class = $prop.'_class';")
	lines.append("\t\t\t\t\t\t\t$check_has_many = 'has_many_'.strtolower($this->$prop_class).'s';")
	lines.append("\t\t\t\t\t\t\tif(property_exists($this, $check_has_many) && $this->$check_has_many) continue;")
	lines.append("\t\t\t\t\t\t\t$check_belongs_to = 'belongs_to_'.strtolower($this->$prop_class);")
	lines.append("\t\t\t\t\t\t\tif(property_exists($this, $check_belongs_to) && $this->$check_belongs_to) {")
	lines.append("\t\t\t\t\t\t\t\t$sth->bindValue(':'.$prop, $val->id, is_int($val->id) ? PDO::PARAM_INT : PDO::PARAM_STR);")
	lines.append("\t\t\t\t\t\t\t}")
	lines.append("\t\t\t\t\t\t} else {")
	lines.append("\t\t\t\t\t\t\tif(!strstr($prop, \"has_many_\") && !strstr($prop, \"_class\") && !strstr($prop, \"belongs_to_\")) {")
	lines.append("\t\t\t\t\t\t\t\t$sth->bindValue(':'.$prop, $val, is_int($val) ? PDO::PARAM_INT : is_null($val) ? PDO::PARAM_NULL : PDO::PARAM_STR);")
	lines.append("\t\t\t\t\t\t\t}")
	lines.append("\t\t\t\t\t\t}")
	lines.append("\t\t\t\t\t}")
	lines.append("\t\t\t\t}")
	lines.append("\t\t\t\t$sth->execute();")
	lines.append("\t\t\t\t$this->id = $db->lastInsertId(static::getTableName());")
	lines.append("\t\t\t}")
	lines.append("\t\t}")
	lines.append("\t}\n")

	# delete
	lines.append("\tpublic function delete() {")
	lines.append("\t\tif(property_exists($this, 'id')) {")
	lines.append("\t\t\t$db = new DB();")
	lines.append("\t\t\t$db->preparedStatement(\"DELETE FROM `\".$this->getTableName().\"` WHERE id = ?\", $this->id);")
	lines.append("\t\t}")
	lines.append("\t}")

	lines.append("}")
	lines.append("?>")
	return '\n'.join(lines)

def produceAppController():
	lines = []
	lines.append("<?php")
	lines.append("include_once(\"routes.php\");")
	lines.append("class AppController {")
	lines.append("\tpublic function __construct() {")
	lines.append("\t\tglobal $routes;")
	lines.append("\t\tglobal $id_regex;")
	lines.append("\t\tif(isset($_SERVER['PATH_INFO'])) {")
	lines.append("\t\t\t$pip = explode(\"/\", $_SERVER['PATH_INFO']);")
	lines.append("\t\t\tforeach($routes as $r => $rules) {")
	lines.append("\t\t\t\tif($r == $pip[1]) {")
	lines.append("\t\t\t\t\tforeach($rules as $reg => $action) {")
	lines.append("\t\t\t\t\t\t$rule = str_replace(\"{id}\", $id_regex, $reg);")
	lines.append("\t\t\t\t\t\tif(preg_match($rule, $_SERVER['REQUEST_METHOD'].\" \".$_SERVER['PATH_INFO']) == 1) {")
	lines.append("\t\t\t\t\t\t\t$class = ucwords($pip[1]).\"Controller\";")
	lines.append("\t\t\t\t\t\t\t$params;")
	lines.append("\t\t\t\t\t\t\tswitch($_SERVER['REQUEST_METHOD']) {")
	lines.append("\t\t\t\t\t\t\t\tcase \"GET\": $params = $_GET; break;")
	lines.append("\t\t\t\t\t\t\t\tcase \"POST\": $params = $_POST; break;")
	lines.append("\t\t\t\t\t\t\t\tcase \"PUT\": parse_str(file_get_contents(\"php://input\"),$params); break;")
	lines.append("\t\t\t\t\t\t\t\tcase \"DELETE\": $params = array(); break;")
	lines.append("\t\t\t\t\t\t\t}")
	lines.append("\t\t\t\t\t\t\t$oc = new $class($params);")
	lines.append("\t\t\t\t\t\t\t$oc->$action();")
	lines.append("\t\t\t\t\t\t}")
	lines.append("\t\t\t\t\t}")
	lines.append("\t\t\t\t} else continue;")
	lines.append("\t\t\t}")
	lines.append("\t\t}")
	lines.append("\t}")
	lines.append("}")
	lines.append("?>")
	return '\n'.join(lines)

def produceDBClass():
	lines = []
	lines.append("<?php")
	lines.append("/** generated with webFactory "+str(version)+" */")
	lines.append("class DB {")
	lines.append("\tprivate $host = 'localhost';")
	lines.append("\tprivate $user = 'mysql_user';")
	lines.append("\tprivate $pass = 'mysql_pass';")
	lines.append("\tprivate $scheme = 'mysql_scheme';")
	lines.append("\tprivate $port = 3306;")
	lines.append("\tprivate $db = NULL;")

	# connect
	lines.append("\tpublic function __construct() {")
	lines.append("\t\ttry {")
	lines.append("\t\t\t$this->db = new PDO(")
	lines.append("\t\t\t\t'mysql:host='.$this->host.';dbname='.$this->scheme.';port='.$this->port.';charset=UTF-8',")
	lines.append("\t\t\t\t$this->user,")
	lines.append("\t\t\t\t$this->pass,")
	lines.append("\t\t\t\tarray(")
	lines.append("\t\t\t\t\tPDO::ATTR_PERSISTENT => true,")
	lines.append("\t\t\t\t\tPDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,")
	lines.append("\t\t\t\t\tPDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,")
	lines.append("\t\t\t\t\tPDO::MYSQL_ATTR_INIT_COMMAND => \"SET NAMES utf8\"")
	lines.append("\t\t\t\t)")
	lines.append("\t\t\t);")
	lines.append("\t\t} catch(PDOException $e) {")
	lines.append("\t\t\tdie($e->getMessage());")
	lines.append("\t\t}")
	lines.append("\t}")

	# close
	lines.append("\tpublic function close() {")
	lines.append("\t\t$this->db = NULL;")
	lines.append("\t}")

	# custom operations
	lines.append("\tpublic function custom() {")
	lines.append("\t\treturn $this->db;")
	lines.append("\t}")

	# preparedStatement
	lines.append("\tpublic function preparedStatement($stmt) {")
	lines.append("\t\ttry {")
	lines.append("\t\t\t$queryType = NULL;")
	lines.append("\t\t\tif(substr_compare($stmt, \"select\", 0, 6, TRUE) == 0) {")
	lines.append("\t\t\t\t$queryType = \"select\";")
	lines.append("\t\t\t}")
	lines.append("\t\t\tif(substr_compare($stmt, \"update\", 0, 6, TRUE) == 0) {")
	lines.append("\t\t\t\t$queryType = \"update\"; ")
	lines.append("\t\t\t}")
	lines.append("\t\t\tif(substr_compare($stmt, \"delete\", 0, 6, TRUE) == 0) {")
	lines.append("\t\t\t\t$queryType = \"delete\";")
	lines.append("\t\t\t}")
	lines.append("\t\t\tif(substr_compare($stmt, \"insert\", 0, 6, TRUE) == 0) {")
	lines.append("\t\t\t\t$queryType = \"insert\";")
	lines.append("\t\t\t}")
	lines.append("\t\t\t// check number of parameters")
	lines.append("\t\t\tif(substr_count($stmt, \"?\") == func_num_args()-1) {")
	lines.append("\t\t\t\t$pstmt = $this->db->prepare($stmt);")
	lines.append("\t\t\t\t// bind all parameters")
	lines.append("\t\t\t\tfor($c = 1; $c < func_num_args(); $c++) {")
	lines.append("\t\t\t\t\t$p = func_get_arg($c);")
	lines.append("\t\t\t\t\tif(is_int($p)) {")
	lines.append("\t\t\t\t\t\t$pstmt->bindValue($c, $p, PDO::PARAM_INT);")
	lines.append("\t\t\t\t\t}")
	lines.append("\t\t\t\t\telseif(is_null($p)) {")
	lines.append("\t\t\t\t\t\t$pstmt->bindValue($c, $p, PDO::PARAM_NULL);")
	lines.append("\t\t\t\t\t}")
	lines.append("\t\t\t\t\telse {")
	lines.append("\t\t\t\t\t\t$pstmt->bindValue($c, $p, PDO::PARAM_STR);")
	lines.append("\t\t\t\t\t}")
	lines.append("\t\t\t\t}")
	lines.append("\t\t\t\t$pstmt->execute();")
	lines.append("\t\t\t\tif($pstmt->rowCount() > 0) {")
	lines.append("\t\t\t\t\tif($queryType == \"select\") {")
	lines.append("\t\t\t\t\t\treturn $pstmt->fetchAll();")
	lines.append("\t\t\t\t\t} else {")
	lines.append("\t\t\t\t\t\treturn $pstmt->rowCount();")
	lines.append("\t\t\t\t\t}")
	lines.append("\t\t\t\t} else {")
	lines.append("\t\t\t\t\treturn NULL;")
	lines.append("\t\t\t\t}")
	lines.append("\t\t\t}")
	lines.append("\t\t} catch(PDOException $e) {")
	lines.append("\t\t\tdie($e->getMessage());")
	lines.append("\t\t}")
	lines.append("\t}")

	# lastInsertId
	lines.append("\tpublic function lastInsertId($table) {")
	lines.append("\t\ttry {")
	lines.append("\t\t\t$stmt = $this->db->prepare(\"SELECT LAST_INSERT_ID() as id FROM `\".$table.\"`\");")
	lines.append("\t\t\t$stmt->execute();")
	lines.append("\t\t\t$id = $stmt->fetch();")
	lines.append("\t\t\treturn (int)$id['id'];")
	lines.append("\t\t} catch(PDOException $e) {")
	lines.append("\t\t\tdie($e->getMessage());")
	lines.append("\t\t}")
	lines.append("\t}")

	lines.append("}")
	lines.append("?>")
	return '\n'.join(lines)

def generateFiles():
	print("set output path:")
	path = input()

	if not os.path.exists(path):
		print("\tcreating",path)
		os.makedirs(path)

	print("\tgenerating",path+"/ActiveRecordModel.class.php")
	armclass = produceActiveRecordModelClass()
	try:
		d = open(path+"/ActiveRecordModel.class.php","w")
	except:
		print("Could not open file! (ActiveRecordModel-Class)")
		return
	d.write(armclass)
	d.close()

	print("Do you wish to generate a web-based REST service for your models? [Y/n]")
	answer = input()
		
	if len(answer) > 0 and answer[0].lower() == "y":
		print("\tgenerating AppController")
		try:
			d = open(path+"/appcontroller.class.php","w")
		except:
			print("Could not open file! (AppController)")
			return
		d.write(produceAppController())
		d.close();

	for c in classes:
		print("\tgenerating model",path+"/"+c.name.lower()+".class.php")
		phpcode = c.generatePHPModel()
		try:
			d = open(path+"/"+c.name.lower()+".class.php","w")
		except:
			print("Could not open file! (Class ",c.name,")")
			return
		d.write(phpcode)
		d.close();

		if len(answer) > 0 and answer[0].lower() == "y":
			print("\tgenerating controller",path+"/"+c.name.lower()+"scontroller.class.php")
			try:
				d = open(path+"/"+c.name.lower()+"scontroller.class.php","w")
			except:
				print("Could not open file! (Controller ",c.name,")")
				return
			d.write(c.generatePHPController())
			d.close();

	print("\tgenerating",path+"/db.class.php")
	dbclass = produceDBClass()
	try:
		d = open(path+"/db.class.php","w")
	except:
		print("Could not open file! (DB-Class)")
		return
	d.write(dbclass)
	d.close()

	mysql = produceMySQLScheme()
	print("\tgenerating",path+"/scheme.sql")
	try:
		d = open(path+"/scheme.sql","w")
	except:
		print("Could not open file! (scheme.sql)")
		return
	d.write(mysql)
	d.close()

	print("")
	print("****************")
	print("*** FINISHED ***")
	print("****************")
	print("")


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