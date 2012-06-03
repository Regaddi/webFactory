#!/bin/python3

import json, os, sys

version = 1.0
classes = []


def getVariable():
	print("variable name:")
	var = {}
	var['name'] = input()
	if var['name'] == "":
		return
	print("variable datatype: (b)oolean, date(t)ime, (d)ecimal, (i)nt, (s)tring, te(x)t, (o)ther")
	datatype = input().lower()
	if len(datatype) > 0:
		datatype = datatype[0]
	else:
		return var
	if datatype == "b":
		var['datatype'] = "BOOLEAN"
	elif datatype == "t":
		var['datatype'] = "DATETIME"
	elif datatype == "d":
		try:
			print("length:")
			decLength = int(input())
			print("decimal places:")
			decPlaces = int(input())
		except:
			print("unexpected input. canceled.")
			return var
		var['datatype'] = "DECIMAL("+str(decLength)+","+str(decPlaces)+")"
	elif datatype == "i":
		var['datatype'] = "INT(11)"
	elif datatype == "s":
		print("length:")
		try:
			strLength = int(input())
		except:
			print("unexpected input. canceled.")
			return var
		var['datatype'] = "VARCHAR("+str(strLength)+")"
	elif datatype == "x":
		var['datatype'] = "TEXT"
	elif datatype == "o":
		print("insert datatype manually:")
		oType = input()
		for c in classes:
			if c['name'].lower() == oType.lower():
				print("do you mean this class? (y/n)")
				printClass(classes.index(c))
				ret = input().lower()[0]
				if ret == "y":
					var['class'] = c['name']
					var['datatype'] = oType
				break
		print("has many? (y/n)")
		man = input().lower()[0]
		if man == "y":
			var['datatype'] = var['datatype']+"[]"
			var['hasmany'] = True
		else:
			print("belongs to? (y/n)")
			bel = input().lower()[0]
			if bel == "y":
				var['belongsto'] = True
	else:
		var = {}
	return var

def createClass():
	print("class name:")
	name = input()
	vars = []
	while 1 == 1:
		var = getVariable()
		if var != None and 'datatype' in var:
			vars.append(var)
		else:
			break

	var_id = { 'name': 'id', 'datatype': 'INT(11)'}
	if var_id not in vars:
		vars.insert(0, var_id)

	classes.append({ 'name': name, 'vars': vars })

def modifyClass():
	print("choose class:")
	for c in classes:
		print("[",c['name'],"]","("+str(classes.index(c))+")")
	i = input()
	if len(i) > 0:
		i = int(i)
	else:
		print("no class chosen.")
		return
	mod = classes[i]
	print("class name: (", mod['name'], ")")
	name = input()
	if name != mod['name']:
		if name != "":
			mod['name'] = name
		vars = mod['vars']
		while 1 == 1:
			var = getVariable()
			if var != None:
				isNew = True
				for v in vars:
					if v['name'] == var['name']:
						if 'datatype' not in var:
							print(var['name'],"deleted")
							del vars[vars.index(v)]
						else:
							vars[vars.index(v)] = var
						isNew = False
						break
				if isNew:
					if 'datatype' in var:
						vars.append(var)
			else:
				break
		var_id = { 'name': 'id', 'datatype': 'INT(11)'}
		if var_id not in vars:
			vars.insert(0, var_id)
		classes[i] = mod

def deleteClass():
	print("choose class:")
	for c in classes:
		print("[",c['name'],"]","("+str(classes.index(c))+")")
	i = int(input())
	del classes[i]

def printClass(i):
	c = classes[i]
	print("\t[",c['name'],"]")
	for v in c['vars']:
		print("\t",v['datatype'],"\t",v['name'])

def printClasses():
	if len(classes) == 0:
		print("\tNo classes defined.")
	for c in classes:
		print("\t[",c['name'],"]")
		for v in c['vars']:
			print("\t",v['datatype'],"\t",v['name'])

def produceMySQLScheme():
	global classes
	print("set mysql scheme (database):")
	scheme = input()
	lines = []
	lines.append("USE `"+scheme+"`;\n")

	for c in classes:
		lines.append("\nCREATE TABLE IF NOT EXISTS `"+c['name'].lower()+"` (\n")
		constraints = []
		isPrimary = False
		primary = None
		for v in c['vars']:
			if v['name'] == "id":
				isPrimary = True
				primary = v['name']
			if 'hasmany' not in v and 'belongsto' not in v:
				lines.append("\t`"+v['name'].lower()+"` "+v['datatype'])
			else:
				if 'belongsto' in v and v['belongsto'] == True:
					lines.append("\t`"+v['name'].lower()+"_id` INT(11)")
					constraints.append("CONSTRAINT `fk_"+c['name'].lower()+"_"+v['name'].lower()+"` FOREIGN KEY (`"+v['name'].lower()+"_id`) REFERENCES `"+v['datatype'].lower()+"` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,\n")
				if 'hasmany' in v and v['hasmany'] == True:
					continue
			if isPrimary == True:
				lines.append(" AUTO_INCREMENT")
			lines.append(",\n")
			isPrimary = False
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
	lines.append("class "+c['name']+" {\n")

	# vars
	for v in c['vars']:
		lines.append("\tpublic $"+v['name']+";\n")

	# __construct
	lines.append("\n\tpublic function __construct(")
	i = 0
	for v in c['vars']:
		lines.append("$"+v['name'])
		if i < len(c['vars'])-1:
			lines.append(",")
			
		i = i+1
	lines.append(") {\n")
	for v in c['vars']:
		if 'belongsto' in v and v['belongsto'] == True:
			lines.append("\t\t$this->"+v['name']+" = (int)$"+v['name']+";\n")
		else:
			lines.append("\t\t$this->"+v['name']+" = $"+v['name']+";\n")
	lines.append("\t}\n")

	for v in c['vars']:
		if 'hasmany' in v and v['hasmany'] == True:
			# get child by index
			funcName = "get"+v['name'][0].upper()+v['name'][1:-1]+"ByIndex"
			lines.append("\n\tpublic function "+funcName+"($index) {\n")
			lines.append("\t\treturn $this->"+v['name']+"[$index];\n")
			lines.append("\t}\n")
		if 'belongsto' in v and v['belongsto'] == True:
			# get parent
			funcName = "get"+v['name'][0].upper()+v['name'][1:]
			lines.append("\n\tpublic function "+funcName+"() {\n")
			lines.append("\t\treturn "+v['class']+"::find($this->"+v['name']+");\n")
			lines.append("\t}\n")

	# save()
	lines.append("\n\tpublic function save() {\n")
	lines.append("\t\t$db = new DB();\n")
	lines.append("\t\tif($this->id > 0) {\n")
	lines.append("\t\t\t$db->preparedStatement(\"UPDATE `"+c['name'].lower()+"` SET ")
	params = []
	for v in c['vars']:
		if 'hasmany' in v and v['hasmany'] == True:
				continue
		elif 'belongsto' in v and v['belongsto'] == True:
			lines.append(v['name'].lower()+"_id = ?")
			params.append("$this->"+v['name'])
		elif v['name'] != "id":
			lines.append(v['name'].lower()+" = ?")
			params.append("$this->"+v['name'])
		else:
			continue
		lines.append(", ")
	lines.append("updated_at = NOW() WHERE id = ?\"")
	params.append("$this->id")
	lines.append(", "+(', '.join(params))+");\n")
	lines.append("\t\t} else {\n")
	lines.append("\t\t\t$db->preparedStatement(\"INSERT INTO `"+c['name'].lower()+"` (")
	params = []
	vals = []
	for v in c['vars']:
		if 'hasmany' in v and v['hasmany'] == True:
				continue
		elif 'belongsto' in v and v['belongsto'] == True:
			lines.append(v['name'].lower()+"_id")
			vals.append("?")
			params.append("$this->"+v['name'])
		elif v['name'] != "id":
			lines.append(v['name'].lower())
			vals.append("?")
			params.append("$this->"+v['name'])
		else:
			continue
		lines.append(", ")
	lines.append("created_at")
	vals.append("NOW()")
	lines.append(") VALUES ("+(', '.join(vals))+");\", "+(', '.join(params))+");\n")
	lines.append("\t\t\t$this->id = $db->lastInsertId('"+c['name'].lower()+"');\n")
	lines.append("\t\t}\n")
	for v in c['vars']:
		if 'hasmany' in v and v['hasmany'] == True:
			lines.append("\t\tif(count($this->"+v['name']+") > 0) {\n")
			lines.append("\t\t\tforeach($this->"+v['name']+" as $"+v['name']+"_row) {\n")
			for c2 in classes:
				if c2['name'] == v['datatype'][:-2]:
					for v2 in c2['vars']:
						if v2['datatype'] == c['name']:
							lines.append("\t\t\t\t$"+v['name']+"_row->"+v2['name']+" = $this->id;\n")
							break;
			lines.append("\t\t\t\t$"+v['name']+"_row->save();\n")
			lines.append("\t\t\t}\n")
			lines.append("\t\t}\n")
	lines.append("\t}\n")

	# delete()
	lines.append("\n\tpublic function delete() {\n")
	lines.append("\t\t$db = new DB();\n")
	lines.append("\t\t$db->preparedStatement(\"DELETE FROM `"+c['name'].lower()+"` WHERE id = ?\", $this->id);\n")
	lines.append("\t}\n")

	# static functions
	# all()
	lines.append("\n\tpublic static function all() {\n")
	lines.append("\t\t$result = array();\n")
	lines.append("\t\t$db = new DB();\n")
	lines.append("\t\t$rows = $db->preparedStatement(\"SELECT * FROM `"+c['name'].lower()+"`\");\n")
	lines.append("\t\tforeach($rows as $r) {\n")
	lines.append("\t\t\tarray_push($result, new "+c['name']+"(\n")
	for v in c['vars']:
		if 'hasmany' in v:
			if v['hasmany']:
				foreignkey = ""
				for c2 in classes:
					if 'class' in v and c2['name'] == v['class']:
						for v2 in c2['vars']:
							if 'class' in v2 and v2['class'] == c['name']:
								foreignkey = v2['name']+"_id"
								break
				lines.append("\t\t\t\t\t"+v['class']+"::find('"+foreignkey+"='.$r['id'])")
			else:
				lines.append("\t\t\t\t\tnew "+v['class']+"("+v['class']+"::find($r['"+v['name'].lower()+"_id']))")
		else:
			lines.append("\t\t\t\t\t$r['"+v['name'].lower()+"']")
		if c['vars'].index(v) < len(c['vars'])-1:
			lines.append(",\n")
	lines.append("));\n")
	lines.append("\t\t}\n")
	lines.append("\t\t$db->close();\n")
	lines.append("\t\treturn $result;\n")
	lines.append("\t}\n")

	# find()
	lines.append("\n\tpublic static function find($searchTerm) {\n")
	lines.append("\t\t$db = new DB();\n")
	lines.append("\t\tif(is_numeric($searchTerm)) {\n")
	lines.append("\t\t\t$r = $db->preparedStatement(\"SELECT * FROM `"+c['name'].lower()+"` WHERE id = ?\", $searchTerm);\n")
	lines.append("\t\t\tif(count($r) == 1) {\n")
	lines.append("\t\t\t\t$r = $r[0];\n")
	lines.append("\t\t\t\treturn new "+c['name']+"(\n")
	for v in c['vars']:
		if 'hasmany' in v and v['hasmany'] == True:
			foreignkey = ""
			for c2 in classes:
				if 'class' in v and c2['name'] == v['class']:
					for v2 in c2['vars']:
						if 'class' in v2 and v2['class'] == c['name']:
							foreignkey = v2['name']+"_id"
							break
			lines.append("\t\t\t\t\t"+v['class']+"::find('"+foreignkey+"='.$r['id'])")
		elif 'belongsto' in v and v['belongsto'] == True:
			lines.append("\t\t\t\t\t$r['"+v['name'].lower()+"_id']")
		else:
			lines.append("\t\t\t\t\t$r['"+v['name'].lower()+"']")
		if c['vars'].index(v) < len(c['vars'])-1:
			lines.append(",\n")
	lines.append(");\n")
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
	lines.append("\t\t\t\tarray_push($where, $key.\" = ?\");\n")
	lines.append("\t\t\t}\n")
	lines.append("\t\t\t$customdb = $db->custom();\n")
	lines.append("\t\t\t$pstmt = $customdb->prepare(\"SELECT id FROM `"+c['name'].lower()+"` WHERE \".implode(\" AND \", $where));\n")
	lines.append("\t\t\t$i = 1;\n")
	lines.append("\t\t\tforeach($query as $key => $val) {\n")
	lines.append("\t\t\t\t$pstmt->bindValue($i, $val, is_int($val) ? PDO::PARAM_INT : is_null($val) ? PDO::PARAM_NULL : PDO::PARAM_STR);\n")
	lines.append("\t\t\t}\n")
	lines.append("\t\t\t$pstmt->execute();\n")
	lines.append("\t\t\t$result = array();\n")
	lines.append("\t\t\tforeach($pstmt->fetchAll() as $row) {\n")
	lines.append("\t\t\t\tarray_push($result, "+c['name']+"::find($row['id']));\n")
	lines.append("\t\t\t}\n")
	lines.append("\t\t\treturn $result;\n")
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
	lines.append("\t\t\treturn $id['id'];\n")
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

	for c in classes:
		phpcode = producePHPCode(c)
		try:
			d = open(path+"/"+c['name'].lower()+".class.php","w")
		except:
			print("Could not open file! (Class ",c['name'],")")
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
		print("Could not open file! (Class ",c['name'],")")
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
	classes = json.load(f)
	f.close()
	print("Imported:")
	printClasses()

def exportClasses():
	print("path to file:")
	path = input()

	with open(path, mode='w', encoding='utf-8') as f:
		json.dump(classes, f, indent=4)

def loopInput():
	print("action: (c)reate class, (m)odify class, (d)elete class, (p)rint, (i)mport, (e)xport, (g)enerate files, (q)uit")
	char = input().lower()[0]
	if char == "c":
		createClass()
	elif char == "m":
		modifyClass()
	elif char == "d":
		deleteClass()
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
	loopInput()

print("webFactory",str(version))

loopInput()