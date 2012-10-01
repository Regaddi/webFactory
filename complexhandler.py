def ComplexHandler(Obj):
	if hasattr(Obj, 'jsonable'):
		return Obj.jsonable()
	else:
		print('Object of type %s with value of %s is not JSON serializable' % (type(Obj), repr(Obj)))