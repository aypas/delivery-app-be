import json
from urllib.parse import unquote


#disgusting!
def OrderViewQString(meta):
	print('working?')
	print('this?',type(json.loads(unquote(meta))))
	print(meta)
	val = json.loads(meta)
	print(val)
	#return {i.split('=')[0]:i.split('=')[1] for i in meta.split('?') }

	



